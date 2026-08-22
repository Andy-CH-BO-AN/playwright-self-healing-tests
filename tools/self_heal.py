import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

BANNED_PATTERNS = [
    r"\btime\.sleep\b",
    r"\bsleep\(",
    r"\bwait_for_timeout\b",
    r"\bforce\s*=\s*True\b",
    r"\bevaluate\(",
    r"\$\$?eval\b",
    r"\bretry\b",
    r"\bassert\b",
    r"\bexpect\(",
]


class RepairDecision(BaseModel):
    decision: Literal["repair", "cannot_repair"]
    file: str = Field(default="")
    old: str = Field(default="")
    new: str = Field(default="")
    reason: str = Field(default="")
    confidence: int = Field(ge=1, le=100)


def check_banned_patterns(text: str) -> str | None:
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, text):
            return f"Contains banned pattern matching '{pattern}'"
    return None


def extract_page_object_path(traceback_text: str) -> str | None:
    matches = re.findall(r"(?:/app/)?(pages/[a-zA-Z0-9_/]+\.py)", traceback_text)
    if matches:
        for match in reversed(matches):
            if Path(match).exists():
                return match
        for match in matches:
            if Path(match).exists():
                return match
    return None


def extract_test_path(nodeid: str, traceback_text: str) -> str | None:
    test_file = nodeid.split("::")[0]
    if Path(test_file).exists():
        return test_file
    matches = re.findall(r"(?:/app/)?(tests/[a-zA-Z0-9_/]+\.py)", traceback_text)
    for match in matches:
        if Path(match).exists():
            return match
    return None


def validate_candidate(
    decision_file: str,
    old_snippet: str,
    new_snippet: str,
) -> str | None:
    pages_dir = Path("pages").resolve()
    candidate_path = Path(decision_file)
    try:
        resolved_path = candidate_path.resolve()
        resolved_path.relative_to(pages_dir)
    except ValueError, RuntimeError:
        return f"Candidate file '{decision_file}' escapes pages directory"

    if not resolved_path.is_file() or resolved_path.suffix != ".py":
        return (
            f"Candidate file '{decision_file}' is not an existing Python file in pages"
        )

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

    banned_reason = check_banned_patterns(new_snippet)
    if banned_reason:
        return f"Safety violation in replacement: {banned_reason}"

    return None


def run_cmd(cmd: list[str]) -> bool:
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def rollback(target_path: Path, original_content: str) -> None:
    print(f"Rolling back changes to {target_path}...")
    target_path.write_text(original_content, encoding="utf-8")
    print("Rebuilding Docker image after rollback...")
    subprocess.run(["docker", "compose", "build", "tests"])


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-assisted locator repair")
    parser.add_argument(
        "--evidence",
        required=True,
        help="Path to failure evidence directory (containing failure.json)",
    )
    args = parser.parse_args()

    evidence_dir = Path(args.evidence)
    failure_file = evidence_dir / "failure.json"
    if not failure_file.exists():
        print(f"Error: failure.json not found in {evidence_dir}")
        print("FINAL: REPAIR_FAILED")
        sys.exit(1)

    failure_data = json.loads(failure_file.read_text(encoding="utf-8"))
    nodeid = failure_data.get("nodeid", "")
    traceback_text = failure_data.get("traceback", "")

    page_html_file = evidence_dir / "page.html"
    page_html = (
        page_html_file.read_text(encoding="utf-8") if page_html_file.exists() else ""
    )

    page_obj_path = extract_page_object_path(traceback_text)
    page_obj_source = ""
    if page_obj_path and Path(page_obj_path).exists():
        page_obj_source = Path(page_obj_path).read_text(encoding="utf-8")

    test_path = extract_test_path(nodeid, traceback_text)
    test_source = ""
    if test_path and Path(test_path).exists():
        test_source = Path(test_path).read_text(encoding="utf-8")

    prompt_path = Path("ai/prompts/locator-repair.md")
    if not prompt_path.is_file():
        print(f"Error: Prompt file '{prompt_path}' does not exist")
        print("FINAL: REPAIR_FAILED")
        sys.exit(1)

    prompt_template = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt_template:
        print(f"Error: Prompt file '{prompt_path}' is empty")
        print("FINAL: REPAIR_FAILED")
        sys.exit(1)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in the environment or .env file")
        print("FINAL: REPAIR_FAILED")
        sys.exit(1)

    model_name = os.getenv("SELF_HEAL_MODEL", "gemini-3.5-flash-lite")

    user_prompt = f"""{prompt_template}

## Actual Failure Context

### 1. Failure Evidence (`failure.json`)
```json
{json.dumps(failure_data, indent=2, ensure_ascii=False)}
```

### 2. DOM Snapshot (`page.html`)
```html
{page_html}
```

### 3. Target Page Object Source (`{page_obj_path or "Unknown"}`)
```python
{page_obj_source}
```

### 4. Failing Test Source (`{test_path or "Unknown"}`)
```python
{test_source}
```
"""

    print(f"Calling Gemini model '{model_name}' for failure diagnosis...")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RepairDecision,
                temperature=0.1,
            ),
        )
        decision = RepairDecision.model_validate_json(response.text)
    except Exception as e:
        print(f"LLM call failed: {e}")
        print("FINAL: REPAIR_FAILED")
        sys.exit(1)

    print(f"Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence}")
    print(f"Reason: {decision.reason}")

    if decision.decision == "cannot_repair":
        print("FINAL: CANNOT_REPAIR")
        sys.exit(0)

    # decision == "repair"
    print(f"Target file: {decision.file}")
    print(f"Old snippet:\n{decision.old}")
    print(f"New snippet:\n{decision.new}")

    safety_error = validate_candidate(decision.file, decision.old, decision.new)
    if safety_error:
        print(f"Safety guard violation: {safety_error}")
        print("FINAL: REPAIR_FAILED")
        sys.exit(1)

    target_path = Path(decision.file)
    original_content = target_path.read_text(encoding="utf-8")
    new_content = original_content.replace(decision.old, decision.new, 1)

    print(f"Applying patch to {target_path}...")
    target_path.write_text(new_content, encoding="utf-8")

    # Run validation pipeline
    validation_passed = False
    try:
        # 1. ruff check
        if not run_cmd([sys.executable, "-m", "ruff", "check", "."]):
            raise RuntimeError("ruff check failed")

        # 2. ruff format check
        if not run_cmd([sys.executable, "-m", "ruff", "format", "--check", "."]):
            raise RuntimeError("ruff format check failed")

        # 3. docker compose build tests
        if not run_cmd(["docker", "compose", "build", "tests"]):
            raise RuntimeError("docker compose build tests failed")

        # 4. targeted failing test
        if not run_cmd(
            [
                "docker",
                "compose",
                "run",
                "--rm",
                "tests",
                "pytest",
                nodeid,
                "--browser",
                "chromium",
            ]
        ):
            raise RuntimeError("Targeted test failed")

        # 5. full Docker test suite
        if not run_cmd(["docker", "compose", "run", "--rm", "tests"]):
            raise RuntimeError("Full test suite failed")

        validation_passed = True
    except Exception as e:
        print(f"Validation error: {e}")
    finally:
        if not validation_passed:
            rollback(target_path, original_content)
            print("FINAL: REPAIR_FAILED")
            sys.exit(1)

    print("FINAL: REPAIRED")
    sys.exit(0)


if __name__ == "__main__":
    main()
