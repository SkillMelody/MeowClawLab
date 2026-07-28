from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import run_pipeline


def test_pipeline_rejects_broad_or_overlapping_work_and_output_paths(tmp_path: Path) -> None:
    validator = getattr(run_pipeline, "_validate_pipeline_paths", None)
    assert callable(validator), "pipeline must validate destructive path boundaries"

    with pytest.raises(ValueError, match="work directory"):
        validator(ROOT, tmp_path / "delivery")
    with pytest.raises(ValueError, match="must be distinct"):
        validator(tmp_path / ".ppt-work", tmp_path / ".ppt-work")


def test_pipeline_refuses_to_reset_nonempty_unowned_output(tmp_path: Path) -> None:
    validator = getattr(run_pipeline, "_validate_output_reset", None)
    assert callable(validator), "pipeline must require output ownership before reset"

    output = tmp_path / "delivery"
    output.mkdir()
    (output / "user-file.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="not owned"):
        validator(output)


def test_pipeline_accepts_empty_or_marked_output(tmp_path: Path) -> None:
    validator = getattr(run_pipeline, "_validate_output_reset", None)
    assert callable(validator), "pipeline must require output ownership before reset"

    empty = tmp_path / "empty-delivery"
    empty.mkdir()
    validator(empty)

    owned = tmp_path / "owned-delivery"
    owned.mkdir()
    (owned / run_pipeline.OUTPUT_OWNERSHIP_MARKER).write_text("owned", encoding="utf-8")
    (owned / "deck.pptx").write_text("fixture", encoding="utf-8")
    validator(owned)
