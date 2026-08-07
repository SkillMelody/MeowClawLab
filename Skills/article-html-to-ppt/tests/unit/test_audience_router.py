from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


from visual_narrative.audience_router import route_audience


@pytest.mark.parametrize(
    ("brief", "expected_route"),
    [
        ({"primary_audience": ["executive"], "delivery_objective": "decide", "source_material_type": "strategy_memo", "delivery_scenario": "strategy_review"}, "strategic_decision"),
        ({"primary_audience": ["investor"], "delivery_objective": "raise_funding", "source_material_type": "pitch_deck", "delivery_scenario": "fundraising"}, "investor_commercial"),
        ({"primary_audience": ["product_manager", "engineer", "designer", "tester"], "delivery_objective": "review_and_align", "source_material_type": "prd", "delivery_scenario": "prd_review"}, "product_prd"),
        ({"primary_audience": ["architect"], "delivery_objective": "approve_architecture", "source_material_type": "architecture_document", "delivery_scenario": "architecture_review"}, "technical_architecture"),
        ({"primary_audience": ["project_sponsor"], "delivery_objective": "govern_delivery", "source_material_type": "project_plan", "delivery_scenario": "steering_committee"}, "project_governance"),
        ({"primary_audience": ["analyst"], "delivery_objective": "communicate_findings", "source_material_type": "research_report", "delivery_scenario": "insight_briefing"}, "research_insight"),
        ({"primary_audience": ["learner"], "delivery_objective": "teach", "source_material_type": "training_material", "delivery_scenario": "training_session"}, "education_explanation"),
        ({"primary_audience": ["consumer"], "delivery_objective": "build_awareness", "source_material_type": "campaign_brief", "delivery_scenario": "campaign_launch"}, "brand_content_communication"),
    ],
)
def test_each_professional_context_selects_exactly_one_matching_route(brief: dict, expected_route: str) -> None:
    result = route_audience({"schema_version": "1.0", "evidence_profile": ["evidence"], "industry_compliance_context": [], **brief})

    assert result["status"] == "ready"
    assert result["selected_route"] == expected_route
    assert len(result["rejected_routes"]) == 7


def test_prd_review_selects_one_product_route_with_a_professional_narrative_contract() -> None:
    brief = {
        "schema_version": "1.0",
        "primary_audience": ["product_manager", "engineer", "designer", "tester"],
        "delivery_objective": "review_and_align",
        "source_material_type": "prd",
        "evidence_profile": ["scope_boundary", "user_flow", "acceptance_criteria"],
        "industry_compliance_context": ["consumer_software"],
        "delivery_scenario": "prd_review",
    }

    result = route_audience(brief)

    assert result["status"] == "ready"
    assert result["selected_route"] == "product_prd"
    assert result["confidence"] >= 0.8
    assert len(result["rejected_routes"]) == 7
    assert result["narrative_contract"]["sequence"] == [
        "problem_and_scope",
        "user_flow_and_rules",
        "acceptance_and_open_questions",
    ]


def test_ambiguous_brief_is_blocked_instead_of_falling_back_to_a_generic_deck() -> None:
    brief = {
        "schema_version": "1.0",
        "primary_audience": [],
        "delivery_objective": "",
        "source_material_type": "document",
        "evidence_profile": [],
        "industry_compliance_context": [],
        "delivery_scenario": "unknown",
    }

    result = route_audience(brief)

    assert result["status"] == "blocked"
    assert result["selected_route"] is None
    assert result["confidence"] == 0.0
    assert "AUDIENCE_ROUTE_INSUFFICIENT_CONTEXT" in result["blocking_codes"]
