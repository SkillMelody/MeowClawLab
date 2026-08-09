from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ir_quality_floor import assess_ir_quality_floor


def _slide(role: str, expression: str, objects: list[dict]) -> dict:
    return {
        "id": "S02",
        "slide_role": role,
        "primary_expression": expression,
        "title": "测试页",
        "judgment": "核心判断" if role == "judgment" else None,
        "message": "来源支持的结论",
        "source_refs": [{"source_id": "report", "locator": "p.4", "claim_type": "direct"}],
        "objects": objects,
    }


def test_sparse_data_slide_is_blocked_before_delivery() -> None:
    report = assess_ir_quality_floor({"slides": [_slide("data", "data_visual", [])]})

    assert report["status"] == "blocked"
    assert {issue["code"] for issue in report["issues"]} == {
        "IR_PRIMARY_DATA_OBJECT_REQUIRED",
        "IR_SUPPORTING_EVIDENCE_REQUIRED",
    }


def test_data_slide_with_chart_and_evidence_block_passes_floor() -> None:
    objects = [
        {"id": "chart", "component_type": "bar_chart", "priority": "primary", "source_refs": [{"source_id": "report", "locator": "p.4"}], "content": {"categories": ["2025"], "series": [{"name": "采用率", "values": [88]}]}},

        {"id": "insight", "component_type": "evidence_block", "priority": "supporting", "content": "采用率高于规模化成熟度。", "source_refs": [{"source_id": "report", "locator": "p.5"}]},

    ]
    report = assess_ir_quality_floor({"slides": [_slide("data", "data_visual", objects)]})

    assert report["status"] == "passed"
    assert report["issues"] == []


def test_data_slide_with_untraceable_or_malformed_chart_is_blocked() -> None:
    objects = [
        {"id": "chart", "component_type": "bar_chart", "priority": "primary", "content": {"categories": ["2024", "2025"], "series": [{"name": "采用率", "values": [88]}]}},
        {"id": "insight", "component_type": "evidence_block", "priority": "supporting", "content": "独立解读", "source_refs": [{"source_id": "report", "locator": "p.4"}]},
    ]

    report = assess_ir_quality_floor({"slides": [_slide("data", "data_visual", objects)]})

    assert report["status"] == "blocked"
    assert {issue["code"] for issue in report["issues"]} == {"IR_DATA_OBJECT_SOURCE_REQUIRED", "IR_CHART_SERIES_LENGTH_INVALID"}


def test_supporting_object_must_be_independently_source_bound() -> None:
    objects = [
        {"id": "chart", "component_type": "bar_chart", "priority": "primary", "source_refs": [{"source_id": "report", "locator": "p.4"}], "content": {"categories": ["2025"], "series": [{"name": "采用率", "values": [88]}]}},
        {"id": "insight", "component_type": "evidence_block", "priority": "supporting", "content": "独立解读", "source_refs": []},
    ]

    report = assess_ir_quality_floor({"slides": [_slide("data", "data_visual", objects)]})

    assert report["status"] == "blocked"
    assert {issue["code"] for issue in report["issues"]} == {"IR_SUPPORTING_OBJECT_SOURCE_REQUIRED"}


def test_generated_support_must_point_back_to_multiple_same_slide_primary_objects() -> None:
    objects = [
        {"id": "m1", "component_type": "metric_card", "priority": "primary", "content": "88%\n已规律使用 AI", "source_refs": [{"source_id": "report", "locator": "p.4"}]},
        {
            "id": "derived",
            "component_type": "comparison_card",
            "priority": "supporting",
            "content": {"title": "同页来源证据对照", "items": [{"object_id": "m1", "summary": "88% 已规律使用 AI"}]},
            "source_refs": [{"source_id": "report", "locator": "p.4"}],
            "provenance": {"derivation": "same_slide_evidence_augmenter", "derived_from_object_ids": ["m1"]},
        },
    ]

    report = assess_ir_quality_floor({"slides": [_slide("judgment", "structured_cards", objects)]})

    assert report["status"] == "blocked"
    assert {issue["code"] for issue in report["issues"]} == {"IR_SUPPORTING_OBJECT_SOURCE_REQUIRED"}


def test_supporting_evidence_must_not_repeat_slide_judgment() -> None:
    objects = [
        {"id": "chart", "component_type": "bar_chart", "priority": "primary", "source_refs": [{"source_id": "report", "locator": "p.4"}], "content": {"categories": ["2025"], "series": [{"name": "采用率", "values": [88]}]}},
        {"id": "repeat", "component_type": "evidence_block", "priority": "supporting", "content": "来源支持的结论", "source_refs": [{"source_id": "report", "locator": "p.4"}]},
    ]

    report = assess_ir_quality_floor({"slides": [_slide("data", "data_visual", objects)]})

    assert report["status"] == "blocked"
    assert {issue["code"] for issue in report["issues"]} == {"IR_SUPPORTING_EVIDENCE_DUPLICATES_SLIDE_CLAIM"}


def test_closing_requires_multiple_actionable_objects() -> None:
    one_action = [{"id": "action-1", "component_type": "summary_action_card", "priority": "primary", "content": "锁定价值场景"}]
    report = assess_ir_quality_floor({"slides": [_slide("closing", "structured_cards", one_action)]})

    assert report["status"] == "blocked"
    assert report["issues"][0]["code"] == "IR_CLOSING_ACTIONS_INSUFFICIENT"
