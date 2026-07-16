from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from package_delivery import calculate_delivery_status, sha256_file
from resolve_production_profile import recommend_profile


def test_user_requested_profile_wins() -> None:
    result = recommend_profile(
        {"profile": "fast", "public_or_internal": "public", "brand_requirement": "high"},
        {"slides": [{"objects": [{"component_type": "ecosystem_map", "complexity": {"node_count": 20, "edge_count": 20}}]}]},
    )
    assert result["selected_profile"] == "fast"
    assert result["override_applied"] is True
    assert result["reason_codes"] == ["USER_REQUESTED_FAST"]


def test_public_delivery_selects_premium() -> None:
    result = recommend_profile(
        {
            "user_request": "Create a polished public launch deck",
            "public_or_internal": "public",
            "delivery_value": "high",
            "brand_requirement": "high",
        },
        {"slides": []},
    )
    assert result["selected_profile"] == "premium"
    assert "PUBLIC_DELIVERY" in result["reason_codes"]
    assert "BRAND_ASSETS_REQUIRED" in result["reason_codes"]


def test_ordinary_internal_report_selects_standard_not_premium() -> None:
    result = recommend_profile(
        {
            "user_request": "Create a formal internal quarterly business review deck",
            "public_or_internal": "internal",
            "delivery_value": "medium",
            "brand_requirement": "medium",
            "editability_requirement": "high",
        },
        {"slides": [{"objects": [{"type": "table", "component_type": "table"}]}]},
    )
    assert result["selected_profile"] == "standard"
    assert "USER_REQUESTED_PREMIUM" not in result["reason_codes"]


def test_premium_word_in_style_description_does_not_force_profile() -> None:
    result = recommend_profile(
        {
            "user_request": "Create a polished knowledge deck with a premium-looking editorial style",
            "public_or_internal": "internal",
            "delivery_value": "medium",
            "brand_requirement": "medium",
        },
        {"slides": []},
    )
    assert result["selected_profile"] == "standard"


def test_fast_artifact_contract() -> None:
    result = recommend_profile({"public_or_internal": "internal", "deadline_mode": "urgent"}, {"slides": []})
    assert result["selected_profile"] == "fast"
    assert ".ppt-work/contracts/ppt-ir.json" in result["required_artifacts"]
    assert "benchmark" in result["allowed_skips"]
    assert "full_render" not in result["required_gates"]


def test_premium_cannot_be_final_without_render() -> None:
    build_manifest = {
        "status": "read_back",
        "outputs": {"deck": "deck.pptx"},
        "stages": {"built": True, "read_back": True, "rendered": False},
        "metrics": {
            "editable_core_ratio": 0.98,
            "whole_slide_raster_count": 0,
            "qa_error_count": 0,
            "qa_fatal_count": 0,
        },
        "fallbacks": [],
        "errors": [],
    }
    qa_report = {
        "metrics": {"editable_core_ratio": 0.98, "whole_slide_raster_count": 0, "qa_error_count": 0},
        "issues": [],
        "evidence": {"render_report": {"status": "not_run"}},
    }
    status = calculate_delivery_status(
        profile="premium",
        build_manifest=build_manifest,
        qa_report=qa_report,
        benchmark_score={"rubric_score": 15},
    )
    assert status != "final"
    assert status == "read_back"


def test_delivery_manifest_hashes_files(tmp_path: Path) -> None:
    artifact = tmp_path / "deck.pptx"
    artifact.write_bytes(b"stable bytes")
    expected = "sha256:" + hashlib.sha256(b"stable bytes").hexdigest()
    assert sha256_file(artifact) == expected
