from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


GENERATOR_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "qa"
    / "generate_fixtures.py"
)
SPEC = importlib.util.spec_from_file_location("qa_fixture_generator_safety", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
GENERATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GENERATOR)


def test_fixture_generator_rejects_root_outside_its_own_directory(tmp_path: Path) -> None:
    validator = getattr(GENERATOR, "_validated_fixture_root", None)
    assert callable(validator), "fixture generator must validate its cleanup root"

    with pytest.raises(ValueError, match="fixture root"):
        validator(tmp_path, GENERATOR_PATH)


def test_fixture_generator_accepts_only_its_real_non_symlink_directory() -> None:
    validator = getattr(GENERATOR, "_validated_fixture_root", None)
    assert callable(validator), "fixture generator must validate its cleanup root"

    expected = GENERATOR_PATH.resolve().parent
    assert validator(expected, GENERATOR_PATH) == expected
