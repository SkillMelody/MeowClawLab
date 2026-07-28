from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from visual_narrative.revision import (
    ALLOWED_ACTIONS,
    VisualRevisionError,
    build_revision_request,
)


def test_revision_requests_replace_repeated_cards_and_enlarge_anchor() -> None:
    request = build_revision_request(
        visual_plan={
            "slides": [
                {
                    "slide_id": "S04",
                    "priority": "key",
                    "semantic_component": "generic_cards",
                }
            ]
        },
        observations=[
            {
                "slide_id": "S04",
                "codes": [
                    "VISUAL_REPEATED_CARDS",
                    "VISUAL_WEAK_PRIMARY_ANCHOR",
                ],
            }
        ],
    )

    actions = request["slides"][0]["actions"]
    assert {"action": "replace_component", "target": "primary"} in actions
    assert {
        "action": "enlarge_primary_anchor",
        "minimum_area_ratio": 0.50,
    } in actions


def test_revision_only_emits_whitelisted_actions_and_protects_content() -> None:
    request = build_revision_request(
        visual_plan={
            "slides": [
                {
                    "slide_id": "S08",
                    "priority": "supporting",
                    "semantic_component": "generic_cards",
                    "message": "不得被精修请求改写的结论。",
                    "evidence_refs": ["E08"],
                    "editability": {"message_bearing": "native_required"},
                }
            ]
        },
        observations=[
            {
                "slide_id": "S08",
                "codes": [
                    "VISUAL_DUPLICATE_COPY",
                    "VISUAL_FRAGMENTED_SUPPORT",
                    "VISUAL_DENSITY_IMBALANCE",
                    "VISUAL_STYLE_TOKEN_DRIFT",
                    "VISUAL_UNKNOWN_REQUEST",
                ],
            }
        ],
    )

    action_names = {
        action["action"]
        for slide in request["slides"]
        for action in slide["actions"]
    }
    assert action_names == {
        "delete_duplicate_copy",
        "merge_supporting_blocks",
        "rebalance_density",
        "correct_style_tokens",
    }
    assert action_names <= ALLOWED_ACTIONS
    serialized = json.dumps(request, ensure_ascii=False)
    assert "不得被精修请求改写的结论" not in serialized
    assert "E08" not in serialized
    assert request["protected_fields"] == [
        "evidence_values",
        "source_refs",
        "message",
        "editability_requirement",
    ]


def test_metrics_and_rubric_can_request_safe_visual_actions() -> None:
    request = build_revision_request(
        visual_plan={
            "slides": [
                {
                    "slide_id": "S03",
                    "priority": "key",
                    "semantic_component": "data_comparison_bridge",
                },
                {
                    "slide_id": "S08",
                    "priority": "supporting",
                    "semantic_component": "generic_cards",
                },
            ]
        },
        observations=[],
        rubric_score={"page_composition": 2.2, "component_craft": 2.3},
        contact_sheet_metrics={
            "slides": [
                {
                    "slide_id": "S08",
                    "primary_anchor_area_ratio": 0.28,
                    "repeated_card_count": 6,
                    "supporting_block_count": 4,
                    "duplicate_copy_count": 1,
                    "style_token_drift_count": 2,
                }
            ]
        },
    )

    by_slide = {slide["slide_id"]: slide["actions"] for slide in request["slides"]}
    assert {
        "action": "enlarge_primary_anchor",
        "minimum_area_ratio": 0.50,
    } in by_slide["S03"]
    assert {action["action"] for action in by_slide["S08"]} == ALLOWED_ACTIONS


def test_missing_contact_metric_does_not_create_false_anchor_revision() -> None:
    request = build_revision_request(
        visual_plan={
            "slides": [
                {
                    "slide_id": "S04",
                    "priority": "supporting",
                    "semantic_component": "narrative_statement",
                }
            ]
        },
        observations=[],
        contact_sheet_metrics={
            "slides": [
                {
                    "slide_id": "S04",
                    "duplicate_copy_count": 1,
                }
            ]
        },
    )

    assert {
        action["action"]
        for action in request["slides"][0]["actions"]
    } == {"delete_duplicate_copy"}


def test_revision_request_is_schema_valid() -> None:
    request = build_revision_request(
        visual_plan={
            "slides": [
                {
                    "slide_id": "S04",
                    "priority": "supporting",
                    "semantic_component": "generic_cards",
                }
            ]
        },
        observations=[
            {
                "slide_id": "S04",
                "codes": ["VISUAL_REPEATED_CARDS"],
            }
        ],
    )
    schema = json.loads(
        (ROOT / "schemas" / "visual-revision-request.schema.json").read_text(
            encoding="utf-8"
        )
    )

    Draft202012Validator(schema).validate(request)


@pytest.mark.parametrize(
    "visual_plan",
    [
        None,
        "oops",
        [],
        {},
        {"slides": "oops"},
        {"slides": [{"priority": "key"}]},
    ],
)
def test_malformed_visual_plan_fails_closed(visual_plan: object) -> None:
    with pytest.raises(VisualRevisionError, match="REVISION_PLAN_INVALID"):
        build_revision_request(visual_plan=visual_plan, observations=[])
