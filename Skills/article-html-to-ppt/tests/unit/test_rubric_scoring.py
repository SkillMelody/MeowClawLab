from __future__ import annotations

import importlib.util
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


def qa(status: str, severities: list[str]) -> dict[str, Any]:
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
    }


def write_reference(case_path: Path, scores: list[int]) -> None:
    dimensions = load_score_module().DIMENSIONS
    data = {
        "schema_version": "1.0",
        "case_id": "unit-case",
        "scorer": {"type": "human_reference", "name": "unit", "version": "1.0"},
        "dimensions": [
            {"dimension": dimension, "score": score, "evidence": ["unit"], "confidence": 1.0}
            for dimension, score in zip(dimensions, scores)
        ],
    }
    (case_path.parent / "reference-rubric.json").write_text(json.dumps(data), encoding="utf-8")


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
    write_reference(case_path, [3, 3, 3, 3, 3, 3])
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=qa("fail", ["error"]), build_manifest=None, use_reference_rubric=True)
    assert result["total_score"] == 18
    assert result["hard_gate_status"] == "failed"
    assert result["rubric_quality_status"] == "passed"
    assert result["overall_status"] == "failed"


def test_low_score_fails_even_when_qa_passes(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    write_reference(case_path, [2, 2, 2, 2, 2, 3])
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=qa("pass", []), build_manifest=None, use_reference_rubric=True)
    assert result["total_score"] == 13
    assert result["hard_gate_status"] == "passed"
    assert result["rubric_quality_status"] == "failed"
    assert result["overall_status"] == "failed"


def test_zero_dimension_fails_quality(tmp_path: Path) -> None:
    score_deck = load_score_module()
    case, case_path = minimal_case(tmp_path)
    write_reference(case_path, [3, 3, 3, 3, 3, 0])
    result = score_deck.build_rubric_score(case=case, case_path=case_path, ppt_ir=None, qa_report=qa("pass", []), build_manifest=None, use_reference_rubric=True)
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
        use_reference_rubric=True,
    )
    schema = load_json(ROOT / "schemas" / "rubric-score.schema.json")
    Draft202012Validator(schema).validate(result)
    assert result["case_id"] == "technical-agent-architecture"
