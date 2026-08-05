from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


from visual_narrative.audience_router import route_audience


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
