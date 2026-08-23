import subprocess
import sys
from pathlib import Path

from self_heal import SelfHealError


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


def apply_patch(file_path: str, old_snippet: str, new_snippet: str) -> None:
    target_path = Path(file_path)
    original_content = target_path.read_text(encoding="utf-8")
    new_content = original_content.replace(old_snippet, new_snippet, 1)
    target_path.write_text(new_content, encoding="utf-8")


def run_static_checks() -> None:
    print("Running static quality checks...")
    commands = [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "ruff", "format", "--check", "."],
        ["git", "diff", "--check"],
    ]
    for cmd in commands:
        if not _run_subprocess(cmd):
            raise SelfHealError(f"Static check failed: {' '.join(cmd)}")

    if not has_valid_page_object_diff():
        raise SelfHealError(
            "Safety check failed: unexpected changes outside pages/**/*.py"
        )

    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
    )
    if untracked.stdout.strip():
        raise SelfHealError(
            "Safety check failed: untracked files detected:\n"
            f"{untracked.stdout.strip()}"
        )


def has_valid_page_object_diff() -> bool:
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


def _run_subprocess(cmd: list[str]) -> bool:
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0
