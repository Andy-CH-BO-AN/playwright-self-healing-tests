import argparse
import subprocess
import sys
from pathlib import Path

from self_heal import SelfHealError
from self_heal.agent import RepairCandidate, request_repair_plan
from self_heal.evidence import clear_test_evidence, load_failure_contexts
from self_heal.safety import (
    apply_patch,
    has_valid_page_object_diff,
    run_static_checks,
    validate_candidate,
)

MAX_ROUNDS = 3


def main() -> None:
    try:
        status = run_repair_loop(_parse_evidence_dir())
        print(f"FINAL: {status}")
    except SelfHealError as e:
        fail(str(e))


def run_repair_loop(initial_evidence_root: Path) -> str:
    current_evidence_root = initial_evidence_root

    for round_number in range(1, MAX_ROUNDS + 1):
        print(f"\n=== Repair Round {round_number}/{MAX_ROUNDS} ===")
        contexts = load_failure_contexts(current_evidence_root)
        if not contexts:
            print(f"No failure evidence found in {current_evidence_root}.")
            break

        print(f"Loaded {len(contexts)} failure(s) from {current_evidence_root}.")
        plan = request_repair_plan(contexts)
        print(f"Received repair plan with {len(plan.repairs)} candidate(s).")

        if not _apply_safe_candidates(plan.repairs):
            print("No valid repairs could be applied in this round; stopping loop.")
            break

        run_static_checks()
        clear_test_evidence()
        _rebuild_test_image()

        if _run_full_regression():
            print("All E2E tests passed!")
            return "REPAIRED"

        current_evidence_root = _latest_failure_evidence()
        print("E2E tests still have failures; proceeding to next round if available.")

    return "PARTIAL_REPAIR" if has_valid_page_object_diff() else "CANNOT_REPAIR"


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


def _rebuild_test_image() -> None:
    print("Rebuilding Docker image...")
    if not _run_command(["docker", "compose", "build", "tests"]):
        raise SelfHealError("Docker build failed after applying repair")


def _run_full_regression() -> bool:
    print("Running full parallel E2E test suite...")
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
            "-n",
            "2",
        ]
    )


def _latest_failure_evidence() -> Path:
    evidence_root = Path("test-results/self-heal")
    if not load_failure_contexts(evidence_root):
        raise SelfHealError("E2E failed but produced no failure evidence")
    return evidence_root


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
        raise SelfHealError(f"Evidence path '{path}' does not exist")
    return path


def fail(message: str) -> None:
    print(message)
    print("FINAL: REPAIR_FAILED")
    sys.exit(1)


if __name__ == "__main__":
    main()
