from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "tests" / "fixtures" / "qa" / "generate_fixtures.py"
sys.path.insert(0, str(ROOT / "scripts"))

from fixture_safety import validated_fixture_root


def test_fixture_generator_rejects_root_outside_its_own_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="fixture root"):
        validated_fixture_root(tmp_path, GENERATOR_PATH)


def test_fixture_generator_accepts_only_its_real_non_symlink_directory() -> None:
    expected = GENERATOR_PATH.resolve().parent
    assert validated_fixture_root(expected, GENERATOR_PATH) == expected
