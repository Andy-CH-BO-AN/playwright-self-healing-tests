import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

MAX_ROUNDS = 3


class RepairDecision(BaseModel):
    file: str
    old: str
    new: str
    reason: str
    confidence: int = Field(ge=1, le=100)


class RepairPlan(BaseModel):
    repairs: list[RepairDecision]


def main() -> None:
    initial_evidence_root = _parse_evidence_dir()
    current_evidence_root = initial_evidence_root

    for round_number in range(1, MAX_ROUNDS + 1):
        print(f"\n=== Repair Round {round_number}/{MAX_ROUNDS} ===")
        failure_dirs = _find_failure_dirs(current_evidence_root)
        if not failure_dirs:
            print(f"No failure evidence found in {current_evidence_root}.")
            break

        print(f"Loaded {len(failure_dirs)} failure(s) from {current_evidence_root}.")
        user_prompt = _build_repair_prompt(failure_dirs)
        plan = _request_repair_plan(user_prompt)

        print(f"Received repair plan with {len(plan.repairs)} candidate(s).")
        applied_count = 0
        for i, repair in enumerate(plan.repairs, 1):
            print(f"  Candidate {i}: {repair.file} (confidence: {repair.confidence})")
            print(f"  Reason: {repair.reason}")
            safety_error = validate_candidate(repair.file, repair.old)
            if safety_error:
                print(f"  Skipping invalid candidate: {safety_error}")
                continue

            _apply_single_patch(repair.file, repair.old, repair.new)
            applied_count += 1
            print(f"  Applied repair to {repair.file}")

        if applied_count == 0:
            print("No valid repairs could be applied in this round; stopping loop.")
            break

        _run_static_checks()
        _clear_test_evidence()

        print("Rebuilding Docker image...")
        if not run_cmd(["docker", "compose", "build", "tests"]):
            fail("Docker build failed after applying repair")

        print("Running full serial E2E test suite...")
        tests_passed = run_cmd(
            [
                "docker",
                "compose",
                "run",
                "--rm",
                "tests",
                "pytest",
                "--browser",
                "chromium",
            ]
        )

        if tests_passed:
            print("All E2E tests passed!")
            print("FINAL: REPAIRED")
            sys.exit(0)

        latest_evidence_root = Path("test-results/self-heal")
        if not _find_failure_dirs(latest_evidence_root):
            fail("E2E failed but produced no failure evidence")

        print("E2E tests still have failures; proceeding to next round if available.")
        current_evidence_root = latest_evidence_root

    if _has_valid_page_object_diff():
        print("FINAL: PARTIAL_REPAIR")
        sys.exit(0)
    else:
        print("FINAL: CANNOT_REPAIR")
        sys.exit(0)


def _parse_evidence_dir() -> Path:
    parser = argparse.ArgumentParser(
        description="Iterative multi-failure locator repair"
    )
    parser.add_argument(
        "--evidence",
        required=True,
        help="Path to failure evidence directory or root containing failures",
    )
    args = parser.parse_args()
    path = Path(args.evidence)
    if not path.exists():
        fail(f"Evidence path '{path}' does not exist")
    return path


def _find_failure_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if (root / "failure.json").is_file():
        return [root]
    return sorted({p.parent for p in root.rglob("failure.json")})


def _build_repair_prompt(failure_dirs: list[Path]) -> str:
    prompt_path = Path("ai/prompts/locator-repair.md")
    if not prompt_path.is_file():
        fail(f"Error: Prompt file '{prompt_path}' does not exist")

    prompt_template = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt_template:
        fail(f"Error: Prompt file '{prompt_path}' is empty")

    sections = [prompt_template, "\n## Actual Failure Context\n"]

    for i, f_dir in enumerate(failure_dirs, 1):
        failure_file = f_dir / "failure.json"
        if not failure_file.exists():
            continue

        failure_data = json.loads(failure_file.read_text(encoding="utf-8"))
        nodeid = failure_data.get("nodeid", "")
        traceback_text = failure_data.get("traceback", "")

        page_html_file = f_dir / "page.html"
        page_html = (
            page_html_file.read_text(encoding="utf-8")
            if page_html_file.exists()
            else ""
        )

        page_obj_path = extract_page_object_path(traceback_text)
        page_obj_source = (
            Path(page_obj_path).read_text(encoding="utf-8")
            if page_obj_path and Path(page_obj_path).exists()
            else ""
        )

        test_file = nodeid.split("::")[0]
        test_source = (
            Path(test_file).read_text(encoding="utf-8")
            if test_file and Path(test_file).exists()
            else ""
        )

        section = f"""### Failure {i} (`{nodeid or "Unknown"}`)

#### 1. Failure Evidence (`failure.json`)
```json
{json.dumps(failure_data, indent=2, ensure_ascii=False)}
```

#### 2. DOM Snapshot (`page.html`)
```html
{page_html}
```

#### 3. Target Page Object Source (`{page_obj_path or "Unknown"}`)
```python
{page_obj_source}
```

#### 4. Failing Test Source (`{test_file or "Unknown"}`)
```python
{test_source}
```
"""
        sections.append(section)

    return "\n".join(sections)


def _request_repair_plan(user_prompt: str) -> RepairPlan:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        fail("Error: GEMINI_API_KEY is not set in the environment or .env file")

    model_name = os.getenv("SELF_HEAL_MODEL", "gemini-3.5-flash-lite")

    print(f"Calling Gemini model '{model_name}' for failure diagnosis...")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RepairPlan,
                temperature=0.1,
            ),
        )
        return RepairPlan.model_validate_json(response.text)
    except Exception as e:
        fail(f"LLM call failed: {e}")


def _apply_single_patch(file_path: str, old_snippet: str, new_snippet: str) -> None:
    target_path = Path(file_path)
    original_content = target_path.read_text(encoding="utf-8")
    new_content = original_content.replace(old_snippet, new_snippet, 1)
    target_path.write_text(new_content, encoding="utf-8")


def _run_static_checks() -> None:
    print("Running static quality checks...")
    commands = [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "ruff", "format", "--check", "."],
        ["git", "diff", "--check"],
    ]
    for cmd in commands:
        if not run_cmd(cmd):
            fail(f"Static check failed: {' '.join(cmd)}")

    if not _has_valid_page_object_diff():
        fail("Safety check failed: unexpected changes outside pages/**/*.py")

    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
    )
    if untracked.stdout.strip():
        fail(
            "Safety check failed: untracked files detected:\n"
            f"{untracked.stdout.strip()}"
        )


def _clear_test_evidence() -> None:
    evidence_dir = Path("test-results/self-heal")
    if evidence_dir.exists():
        shutil.rmtree(evidence_dir, ignore_errors=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)


def _has_valid_page_object_diff() -> bool:
    res = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
    )
    changed = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    if not changed:
        return False

    pages_dir = Path("pages").resolve()
    for file in changed:
        try:
            resolved = Path(file).resolve()
            resolved.relative_to(pages_dir)
            if resolved.suffix != ".py":
                return False
        except ValueError:
            return False
    return True


def fail(message: str) -> None:
    print(message)
    print("FINAL: REPAIR_FAILED")
    sys.exit(1)


def extract_page_object_path(traceback_text: str) -> str | None:
    matches = re.findall(r"(?:/app/)?(pages/[a-zA-Z0-9_/]+\.py)", traceback_text)
    for match in reversed(matches):
        if Path(match).exists():
            return match
    return None


def validate_candidate(decision_file: str, old_snippet: str) -> str | None:
    pages_dir = Path("pages").resolve()
    try:
        resolved_path = Path(decision_file).resolve()
        resolved_path.relative_to(pages_dir)
    except ValueError:
        return f"Candidate file '{decision_file}' escapes pages directory"

    if not resolved_path.is_file() or resolved_path.suffix != ".py":
        return f"Candidate '{decision_file}' is not an existing Python file in pages"

    if not old_snippet:
        return "Old snippet is empty"

    content = resolved_path.read_text(encoding="utf-8")
    count = content.count(old_snippet)
    if count == 0:
        return f"Old snippet not found in '{decision_file}'"
    if count > 1:
        return (
            f"Old snippet occurs {count} times in '{decision_file}', expected exactly 1"
        )

    return None


def run_cmd(cmd: list[str]) -> bool:
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


if __name__ == "__main__":
    main()
