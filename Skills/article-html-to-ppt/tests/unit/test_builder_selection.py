from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from builders.selector import select_builder

RESOLVER = ROOT / "scripts" / "resolve_component_delivery.py"
STYLE = ROOT / "tests" / "fixtures" / "styles" / "technical-blueprint.json"
REGISTRY_PATH = ROOT / "references" / "component-registry.json"
PPT_IR_PATH = ROOT / "tests" / "fixtures" / "components" / "sample-ppt-ir.json"
CAP_DIR = ROOT / "tests" / "fixtures" / "capabilities"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_selector_prefers_higher_editable_coverage() -> None:
    selection = select_builder(
        load(PPT_IR_PATH),
        None,
        load(REGISTRY_PATH),
        load(CAP_DIR / "macos-full.json"),
        "premium",
        "auto",
    )
    assert selection.selected == "officecli"
    assert "BUILDER_SELECTED_BY_SCORE" in selection.selection_reasons


def test_user_requested_builder_wins_when_valid() -> None:
    selection = select_builder(
        load(PPT_IR_PATH),
        None,
        load(REGISTRY_PATH),
        load(CAP_DIR / "macos-full.json"),
        "premium",
        "pptxgenjs",
    )
    assert selection.selected == "pptxgenjs"
    assert selection.errors == []
    assert "BUILDER_USER_REQUEST_VALID" in selection.selection_reasons


def test_premium_rejects_unknown_support() -> None:
    selection = select_builder(
        load(PPT_IR_PATH),
        None,
        load(REGISTRY_PATH),
        load(CAP_DIR / "unknown-builder.json"),
        "premium",
        "auto",
    )
    assert selection.selected == "unknown"
    assert "BUILDER_SELECTION_NO_VALID_CANDIDATE" in selection.errors


def test_native_required_rejects_visual_only_builder() -> None:
    selection = select_builder(
        load(PPT_IR_PATH),
        None,
        load(REGISTRY_PATH),
        load(CAP_DIR / "broken-builder.json"),
        "premium",
        "html_svg",
    )
    assert selection.selected == "unknown"
    assert "BUILDER_SELECTION_NO_VALID_CANDIDATE" in selection.errors
    assert any("BUILDER_NATIVE_REQUIRED_UNSUPPORTED" in candidate["errors"] for candidate in selection.candidates)


def test_fast_warns_and_uses_static_defaults_without_capabilities() -> None:
    selection = select_builder(load(PPT_IR_PATH), None, load(REGISTRY_PATH), None, "fast", "auto")
    assert selection.selected != "unknown"
    assert "CAPABILITY_REPORT_MISSING_STATIC_DEFAULTS_USED" in selection.warnings


def test_standard_requires_capability_report() -> None:
    selection = select_builder(load(PPT_IR_PATH), None, load(REGISTRY_PATH), None, "standard", "auto")
    assert selection.selected == "unknown"
    assert "CAPABILITY_REPORT_REQUIRED" in selection.errors


def test_resolver_records_builder_selection(tmp_path: Path) -> None:
    output = tmp_path / "delivery-plan.json"
    subprocess.run(
        [
            sys.executable,
            str(RESOLVER),
            "--ppt-ir",
            str(PPT_IR_PATH),
            "--style",
            str(STYLE),
            "--registry",
            str(REGISTRY_PATH),
            "--capabilities",
            str(CAP_DIR / "macos-full.json"),
            "--profile",
            "premium",
            "--builder",
            "pptxgenjs",
            "--output",
            str(output),
            "--strict",
        ],
        cwd=ROOT,
        check=True,
    )
    plan = load(output)
    assert plan["builder"]["requested"] == "pptxgenjs"
    assert plan["builder"]["selected"] == "pptxgenjs"
    assert plan["builder"]["selection_score"] > 0
