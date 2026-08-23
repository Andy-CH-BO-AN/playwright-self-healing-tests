import ast
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FailureContext:
    nodeid: str
    failure_data: dict[str, Any]
    dom_snapshot: str
    test_file: str
    test_source: str
    relevant_page_objects: dict[Path, str]


def load_failure_contexts(evidence_root: Path) -> list[FailureContext]:
    failure_dirs = _find_failure_dirs(evidence_root)
    contexts: list[FailureContext] = []

    for f_dir in failure_dirs:
        failure_file = f_dir / "failure.json"
        if not failure_file.exists():
            continue

        try:
            failure_data = json.loads(failure_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        nodeid = failure_data.get("nodeid", "")
        traceback_text = failure_data.get("traceback", "")

        page_html_file = f_dir / "page.html"
        dom_snapshot = (
            page_html_file.read_text(encoding="utf-8")
            if page_html_file.exists()
            else ""
        )

        test_file = nodeid.split("::")[0] if "::" in nodeid else nodeid
        test_path = Path(test_file) if test_file else None
        test_source = (
            test_path.read_text(encoding="utf-8")
            if test_path and test_path.is_file()
            else ""
        )

        page_object_paths: set[Path] = set()
        if test_file:
            page_object_paths.update(_find_page_object_imports(test_file))

        traceback_page = _extract_page_object_path(traceback_text)
        if traceback_page:
            page_object_paths.add(Path(traceback_page))

        relevant_page_objects: dict[Path, str] = {}
        for po_path in sorted(page_object_paths):
            if po_path.is_file():
                relevant_page_objects[po_path] = po_path.read_text(encoding="utf-8")

        contexts.append(
            FailureContext(
                nodeid=nodeid,
                failure_data=failure_data,
                dom_snapshot=dom_snapshot,
                test_file=test_file,
                test_source=test_source,
                relevant_page_objects=relevant_page_objects,
            )
        )

    return contexts


def _find_failure_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if (root / "failure.json").is_file():
        return [root]
    return sorted({p.parent for p in root.rglob("failure.json")})


def _find_page_object_imports(test_file: str) -> list[Path]:
    test_path = Path(test_file)
    if not test_file or not test_path.is_file():
        return []

    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    paths: set[Path] = set()

    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)

        for module in modules:
            if not module.startswith("pages."):
                continue
            path = Path(module.replace(".", "/") + ".py")
            if path.is_file():
                paths.add(path)

    return sorted(paths)


def _extract_page_object_path(traceback_text: str) -> str | None:
    matches = re.findall(r"(?:/app/)?(pages/[a-zA-Z0-9_/]+\.py)", traceback_text)
    for match in reversed(matches):
        if Path(match).exists():
            return match
    return None


def clear_test_evidence(
    target_dir: Path = Path("test-results/self-heal"),
) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
