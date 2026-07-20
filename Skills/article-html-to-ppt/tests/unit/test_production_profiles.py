from __future__ import annotations

import hashlib
import json
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


def premium_gate_inputs(tmp_path: Path) -> tuple[dict, dict, dict, Path]:
    deck = tmp_path / "deck.pptx"
    deck.write_bytes(b"bound deck")
    digest = sha256_file(deck)
    build = {
        "status": "verified",
        "build_id": "build-unit",
        "deck_id": "unit-case",
        "outputs": {"deck": "deck.pptx"},
        "stages": {"built": True, "read_back": True, "rendered": True},
        "metrics": {
            "editable_core_ratio": 1.0,
            "whole_slide_raster_count": 0,
            "qa_error_count": 0,
            "qa_fatal_count": 0,
        },
        "fallbacks": [],
        "errors": [],
    }
    inspection = {"schema_version": "1.0", "status": "passed", "pptx_sha256": digest, "issues": [], "slides": [], "metrics": {}}
    slide = tmp_path / "slide-1.png"
    slide.write_bytes(b"rendered slide")
    render_report = {"status": "passed", "slides": [{"slide_index": 1, "image": str(slide), "status": "passed"}]}
    render_report_digest = "sha256:" + hashlib.sha256(json.dumps({"slides": [{"image": "<image>", "slide_index": 1, "status": "passed"}], "status": "passed"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    render_evidence_digest = hashlib.sha256()
    render_evidence_digest.update(b"1")
    render_evidence_digest.update(bytes.fromhex(sha256_file(slide).split(":", 1)[1]))
    qa_report = {
        "status": "pass",
        "metrics": {"editable_core_ratio": 1.0, "whole_slide_raster_count": 0, "qa_error_count": 0},
        "issues": [],
        "evidence": {"render_report": render_report, "structural_inspection": inspection},
    }
    rubric = {
        "case_id": "unit-case",
        "build_id": "build-unit",
        "deck_id": "unit-case",
        "rubric_score": 18,
        "overall_status": "passed",
        "manual_review_required": False,
        "scorer": {"type": "human_reference", "name": "reviewer", "version": "1"},
        "evidence_binding": {
            "case_id": "unit-case",
            "build_id": "build-unit",
            "deck_id": "unit-case",
            "pptx_sha256": digest,
            "render_report_sha256": render_report_digest,
            "render_evidence_sha256": "sha256:" + render_evidence_digest.hexdigest(),
        },
    }
    return build, qa_report, rubric, deck


def test_premium_automatic_score_cannot_grant_final(tmp_path: Path) -> None:
    build, qa_report, _rubric, deck = premium_gate_inputs(tmp_path)

    status = calculate_delivery_status(
        profile="premium",
        build_manifest=build,
        qa_report=qa_report,
        benchmark_score={
            "rubric_score": 18,
            "overall_status": "passed",
            "manual_review_required": True,
            "scorer": {"type": "automatic_metrics", "name": "test", "version": "1"},
        },
        pptx_path=deck,
    )

    assert status == "verified"


def test_qa_json_without_explicit_inspection_cannot_claim_read_back_or_final(tmp_path: Path) -> None:
    build, qa_report, rubric, deck = premium_gate_inputs(tmp_path)
    qa_report["evidence"].pop("structural_inspection")
    build["stages"]["read_back"] = False
    status = calculate_delivery_status(profile="premium", build_manifest=build, qa_report=qa_report, benchmark_score=rubric, pptx_path=deck)
    assert status in {"created", "rendered"}


def test_failed_or_hash_mismatched_inspection_cannot_grant_final(tmp_path: Path) -> None:
    build, qa_report, rubric, deck = premium_gate_inputs(tmp_path)
    qa_report["evidence"]["structural_inspection"]["status"] = "failed"
    assert calculate_delivery_status(profile="premium", build_manifest=build, qa_report=qa_report, benchmark_score=rubric, pptx_path=deck) != "final"
    qa_report["evidence"]["structural_inspection"]["status"] = "passed"
    qa_report["evidence"]["structural_inspection"]["pptx_sha256"] = "sha256:" + "0" * 64
    assert calculate_delivery_status(profile="premium", build_manifest=build, qa_report=qa_report, benchmark_score=rubric, pptx_path=deck) != "final"


def test_bound_successful_inspection_allows_premium_final(tmp_path: Path) -> None:
    build, qa_report, rubric, deck = premium_gate_inputs(tmp_path)
    status = calculate_delivery_status(profile="premium", build_manifest=build, qa_report=qa_report, benchmark_score=rubric, pptx_path=deck)
    assert status == "final"


def test_delivery_manifest_hashes_files(tmp_path: Path) -> None:
    artifact = tmp_path / "deck.pptx"
    artifact.write_bytes(b"stable bytes")
    expected = "sha256:" + hashlib.sha256(b"stable bytes").hexdigest()
    assert sha256_file(artifact) == expected
