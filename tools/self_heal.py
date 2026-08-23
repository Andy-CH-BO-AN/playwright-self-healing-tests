import argparse
import subprocess
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
_tools_dir = str(Path(__file__).resolve().parent)
if sys.path and sys.path[0] == _tools_dir:
    sys.path.pop(0)

from self_heal import SelfHealError  # noqa: E402
from self_heal.agent import RepairCandidate, request_repair_plan  # noqa: E402
from self_heal.evidence import clear_test_evidence, load_failure_contexts  # noqa: E402
from self_heal.safety import (  # noqa: E402
    apply_patch,
    has_valid_page_object_diff,
    run_static_checks,
    validate_candidate,
)

MAX_ROUNDS = 3


def main() -> None:
    initial_evidence_root = _parse_evidence_dir()
    current_evidence_root = initial_evidence_root

    try:
        for round_number in range(1, MAX_ROUNDS + 1):
            print(f"\n=== Repair Round {round_number}/{MAX_ROUNDS} ===")
            contexts = load_failure_contexts(current_evidence_root)
            if not contexts:
                print(f"No failure evidence found in {current_evidence_root}.")
                break

            print(f"Loaded {len(contexts)} failure(s) from {current_evidence_root}.")
            plan = request_repair_plan(contexts)

            print(f"Received repair plan with {len(plan.repairs)} candidate(s).")
            applied_count = _apply_safe_candidates(plan.repairs)
            if applied_count == 0:
                print("No valid repairs could be applied in this round; stopping loop.")
                break

            run_static_checks()
            clear_test_evidence()

            print("Rebuilding Docker image...")
            if not _run_command(["docker", "compose", "build", "tests"]):
                fail("Docker build failed after applying repair")

            print("Running full serial E2E test suite...")
            if _run_full_regression():
                print("All E2E tests passed!")
                print("FINAL: REPAIRED")
                sys.exit(0)

            latest_evidence_root = Path("test-results/self-heal")
            if not load_failure_contexts(latest_evidence_root):
                fail("E2E failed but produced no failure evidence")

            print(
                "E2E tests still have failures; proceeding to next round if available."
            )
            current_evidence_root = latest_evidence_root

        if has_valid_page_object_diff():
            print("FINAL: PARTIAL_REPAIR")
        else:
            print("FINAL: CANNOT_REPAIR")
        sys.exit(0)

    except SelfHealError as e:
        fail(str(e))


def _apply_safe_candidates(repairs: list[RepairCandidate]) -> int:
    applied_count = 0
    for i, repair in enumerate(repairs, 1):
        print(f"  Candidate {i}: {repair.file} (confidence: {repair.confidence})")
        print(f"  Reason: {repair.reason}")
        safety_error = validate_candidate(repair.file, repair.old)
        if safety_error:
            print(f"  Skipping invalid candidate: {safety_error}")
            continue

        apply_patch(repair.file, repair.old, repair.new)
        applied_count += 1
        print(f"  Applied repair to {repair.file}")
    return applied_count


def _run_full_regression() -> bool:
    return _run_command(
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


def _run_command(cmd: list[str]) -> bool:
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


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


def fail(message: str) -> None:
    print(message)
    print("FINAL: REPAIR_FAILED")
    sys.exit(1)


if __name__ == "__main__":
    main()
