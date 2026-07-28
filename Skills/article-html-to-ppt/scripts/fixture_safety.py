from __future__ import annotations

from pathlib import Path


def validated_fixture_root(root: Path, script_path: Path) -> Path:
    declared = Path(root)
    if declared.is_symlink():
        raise ValueError("fixture root must not be a symlink")
    resolved = declared.resolve()
    expected = Path(script_path).resolve().parent
    if (
        resolved != expected
        or expected.name != "qa"
        or expected.parent.name != "fixtures"
        or expected.parent.parent.name != "tests"
    ):
        raise ValueError("fixture root must be tests/fixtures/qa beside this script")
    return resolved
