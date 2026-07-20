from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def load_score_module() -> Any:
    spec = importlib.util.spec_from_file_location("score_deck", str(ROOT / "scripts" / "score_deck.py"))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def minimal_case(tmp_path: Path) -> tuple[dict[str, Any], Path]:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    case = {
        "schema_version": "1.0",
        "case_id": "unit-case",
        "title": "Unit Case",
        "category": "technical_agent",
        "source_files": ["source.md"],
        "requirements_file": "requirements.json",
        "reference_rubric": "reference-rubric.json",
        "profile": "premium",
    }
    (case_dir / "case.json").write_text(json.dumps(case), encoding="utf-8")
    return case, case_dir / "case.json"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def qa(status: str, severities: list[str], *, render_report: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "2.1",
        "deck_id": "unit-case",
        "ppt_ir_ref": "ppt-ir.json",
        "profile": "premium",
        "status": status,
        "issues": [
            {
                "issue_code": f"ISSUE_{idx}",
                "severity": severity,
                "category": "unit",
                "evidence": {},
                "message": "unit",
                "repair_action": None,
                "repair_status": "pending",
            }
            for idx, severity in enumerate(severities)
        ],
        "metrics": {"qa_error_count": severities.count("error"), "qa_fatal_count": severities.count("fatal")},
        "evidence": {"render_report": render_report} if render_report else {},
    }


def write_reference(
    case_path: Path,
    scores: list[int],
    *,
    build_id: str = "build-unit",
    deck_id: str = "unit-case",
    case_id: str = "unit-case",
    pptx_sha256: str | None = None,
    render_report_sha256: str | None = None,
    render_evidence_sha256: str | None = None,
    evidence: list[str] | None = None,
    scorer: dict[str, Any] | None = None,
) -> None:
    dimensions = load_score_module().DIMENSIONS
    data = {
        "schema_version": "1.0",
        "case_id": case_id,
        "build_id": build_id,
        "deck_id": deck_id,
        "bindings": {
            "case_id": case_id,
            "build_id": build_id,
            "deck_id": deck_id,
            "pptx_sha256": pptx_sha256,
            "render_report_sha256": render_report_sha256,
            "render_evidence_sha256": render_evidence_sha256,
        },
        "scorer": scorer or {
            "type": "human_reference",
            "name": "Unit Reviewer",
            "version": "1.0",
            "provenance": {
                "review_id": "review-unit-001",
                "reviewed_at": "2026-07-20T16:00:00+08:00",
                "method": "human_visual_review",
            },
        },
        "dimensions": [
            {"dimension": dimension, "score": score, "evidence": evidence if evidence is not None else ["Visible rendered evidence supports this score."], "confidence": 1.0}
            for dimension, score in zip(dimensions, scores)
        ],
    }
    (case_path.parent / "reference-rubric.json").write_text(json.dumps(data), encoding="utf-8")


def bound_inputs(tmp_path: Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    pptx = tmp_path / "deck.pptx"
    pptx.write_bytes(b"current deck bytes")
    slide_a = tmp_path / "slide-1.png"
    slide_b = tmp_path / "slide-2.png"
    slide_a.write_bytes(b"slide one")
    slide_b.write_bytes(b"slide two")
    render = {
        "schema_version": "1.0",
        "status": "passed",
        "slides": [
            {"slide_index": 1, "image": str(slide_a), "status": "passed"},
            {"slide_index": 2, "image": str(slide_b), "status": "passed"},
        ],
    }
    build = {"build_id": "build-unit", "deck_id": "unit-case", "outputs": {"deck": str(pptx)}}
    return pptx, render, build, qa("pass", [], render_report=render)


def bind_reference(score_deck: Any, case_path: Path, pptx: Path, render: dict[str, Any], **overrides: Any) -> None:
    binding = score_deck.build_evidence_binding(pptx, render)
    binding.update(overrides)
    write_reference(case_path, [3, 3, 3, 3, 3, 3], **binding)


def test_manual_review_required_without_reference_or_model(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=qa("pass", []), build_manifest=None)
    assert result["manual_review_required"] is True
    assert result["total_score"] is None
    assert result["rubric_quality_status"] == "manual_review_required"
    assert all(item["score"] is None for item in result["dimensions"])


def test_hard_gate_failure_overrides_high_reference_score(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    bind_reference(score_deck, case_path, pptx, render)
    report["status"] = "fail"
    report["issues"] = qa("fail", ["error"])["issues"]
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    assert result["total_score"] == 18
    assert result["hard_gate_status"] == "failed"
    assert result["rubric_quality_status"] == "passed"
    assert result["overall_status"] == "failed"


def test_low_score_fails_even_when_qa_passes(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    binding = score_deck.build_evidence_binding(pptx, render)
    write_reference(case_path, [2, 2, 2, 2, 2, 3], **binding)
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    assert result["total_score"] == 13
    assert result["hard_gate_status"] == "passed"
    assert result["rubric_quality_status"] == "failed"
    assert result["overall_status"] == "failed"


def test_zero_dimension_fails_quality(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    binding = score_deck.build_evidence_binding(pptx, render)
    write_reference(case_path, [3, 3, 3, 3, 3, 0], **binding)
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    assert result["total_score"] == 15
    assert result["rubric_quality_status"] == "failed"
    assert result["decoupling"]["zero_dimension_fails_quality"] is True


def test_fixture_score_validates_against_schema() -> None:
    score_deck = load_score_module()
    case_path = ROOT / "tests" / "fixtures" / "benchmark" / "technical-agent-architecture" / "case.json"
    case = load_json(case_path)
    result = score_deck.build_rubric_score(
        case=case,
        case_path=case_path,
        ppt_ir=load_json(case_path.parent / "expected-ppt-ir.json"),
        qa_report=load_json(case_path.parent / "baseline" / "qa-report.json"),
        build_manifest=load_json(case_path.parent / "baseline" / "build-manifest.json"),
        use_reference_rubric=False,
    )
    schema = load_json(ROOT / "schemas" / "rubric-score.schema.json")
    Draft202012Validator(schema).validate(result)
    assert result["case_id"] == "technical-agent-architecture"


def test_fabricated_reference_without_bindings_is_rejected(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    write_reference(case_path, [3] * 6)
    rubric = load_json(case_path.parent / "reference-rubric.json")
    rubric.pop("bindings")
    (case_path.parent / "reference-rubric.json").write_text(json.dumps(rubric), encoding="utf-8")
    pptx, _render, build, report = bound_inputs(tmp_path)
    with __import__("pytest").raises(score_deck.ScoreInputError, match="bindings"):
        score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)


def test_reference_rejects_mismatched_case_deck_or_build(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    for field, bad in (("case_id", "other-case"), ("deck_id", "other-deck"), ("build_id", "other-build")):
        bind_reference(score_deck, case_path, pptx, render, **{field: bad})
        with __import__("pytest").raises(score_deck.ScoreInputError, match=field):
            score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)


def test_reference_rejects_stale_render_digest_and_deck_replay(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    bind_reference(score_deck, case_path, pptx, render, render_report_sha256=sha256_bytes(b"stale"))
    with __import__("pytest").raises(score_deck.ScoreInputError, match="render_report_sha256"):
        score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    bind_reference(score_deck, case_path, pptx, render)
    replayed = tmp_path / "another-deck.pptx"
    replayed.write_bytes(b"another deck")
    with __import__("pytest").raises(score_deck.ScoreInputError, match="pptx_sha256"):
        score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=replayed, use_reference_rubric=True)


def test_reference_rejects_empty_evidence_untrusted_scorer_and_private_path(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    binding = score_deck.build_evidence_binding(pptx, render)
    write_reference(case_path, [3] * 6, evidence=[], **binding)
    with __import__("pytest").raises(score_deck.ScoreInputError, match="evidence"):
        score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    write_reference(case_path, [3] * 6, scorer={"type": "automatic_metrics", "name": "fake", "version": "1"}, **binding)
    with __import__("pytest").raises(score_deck.ScoreInputError, match="scorer"):
        score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    write_reference(case_path, [3] * 6, evidence=["See /Users/reviewer/private/slide.png"], **binding)
    with __import__("pytest").raises(score_deck.ScoreInputError, match="absolute local path"):
        score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)


def test_legally_bound_reference_passes_without_leaking_paths(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    pptx, render, build, report = bound_inputs(tmp_path)
    bind_reference(score_deck, case_path, pptx, render)
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=report, build_manifest=build, pptx_path=pptx, use_reference_rubric=True)
    assert result["overall_status"] == "passed"
    assert result["manual_review_required"] is False
    assert "/Users/" not in json.dumps(result)
