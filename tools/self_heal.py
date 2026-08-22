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


class RepairDecision(BaseModel):
    decision: Literal["repair", "cannot_repair"]
    file: str = Field(default="")
    old: str = Field(default="")
    new: str = Field(default="")
    reason: str = Field(default="")
    confidence: int = Field(ge=1, le=100)


def main() -> None:
    evidence_dir = _parse_evidence_dir()
    failure_data = _load_failure_data(evidence_dir)
    user_prompt = _build_repair_prompt(evidence_dir, failure_data)
    decision = _request_repair_decision(user_prompt)

    print(f"Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence}")
    print(f"Reason: {decision.reason}")

    if decision.decision == "cannot_repair":
        print("FINAL: CANNOT_REPAIR")
        sys.exit(0)

    _apply_and_validate_repair(decision, failure_data.get("nodeid", ""))

    print("FINAL: REPAIRED")
    sys.exit(0)


def _parse_evidence_dir() -> Path:
    parser = argparse.ArgumentParser(description="AI-assisted locator repair")
    parser.add_argument(
        "--evidence",
        required=True,
        help="Path to failure evidence directory (containing failure.json)",
    )
    args = parser.parse_args()
    return Path(args.evidence)


def _load_failure_data(evidence_dir: Path) -> dict:
    failure_file = evidence_dir / "failure.json"
    if not failure_file.exists():
        fail(f"Error: failure.json not found in {evidence_dir}")

    return json.loads(failure_file.read_text(encoding="utf-8"))


def _build_repair_prompt(evidence_dir: Path, failure_data: dict) -> str:
    nodeid = failure_data.get("nodeid", "")
    traceback_text = failure_data.get("traceback", "")

    page_html_file = evidence_dir / "page.html"
    page_html = (
        page_html_file.read_text(encoding="utf-8") if page_html_file.exists() else ""
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

    prompt_path = Path("ai/prompts/locator-repair.md")
    if not prompt_path.is_file():
        fail(f"Error: Prompt file '{prompt_path}' does not exist")

    prompt_template = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt_template:
        fail(f"Error: Prompt file '{prompt_path}' is empty")

    return f"""{prompt_template}

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

### 4. Failing Test Source (`{test_file or "Unknown"}`)
```python
{test_source}
```
"""


def _request_repair_decision(user_prompt: str) -> RepairDecision:
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
                response_schema=RepairDecision,
                temperature=0.1,
            ),
        )
        return RepairDecision.model_validate_json(response.text)
    except Exception as e:
        fail(f"LLM call failed: {e}")


def _apply_and_validate_repair(decision: RepairDecision, nodeid: str) -> None:
    print(f"Target file: {decision.file}")
    print(f"Old snippet:\n{decision.old}")
    print(f"New snippet:\n{decision.new}")

    safety_error = validate_candidate(decision.file, decision.old)
    if safety_error:
        fail(f"Safety guard violation: {safety_error}")

    target_path = Path(decision.file)
    original_content = target_path.read_text(encoding="utf-8")
    new_content = original_content.replace(decision.old, decision.new, 1)

    print(f"Applying patch to {target_path}...")
    target_path.write_text(new_content, encoding="utf-8")

    commands = [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "ruff", "format", "--check", "."],
        ["docker", "compose", "build", "tests"],
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
        ],
        ["docker", "compose", "run", "--rm", "tests"],
    ]

    for command in commands:
        if not run_cmd(command):
            rollback(target_path, original_content)
            fail("Validation failed, state restored")


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


if __name__ == "__main__":
    main()
