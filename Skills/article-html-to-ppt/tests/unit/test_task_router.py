from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from visual_narrative.task_router import route_task


def test_research_evidence_routes_to_research_report() -> None:
    analysis = {
        "evidence_types": ["statistics", "comparison", "trend"],
        "relationship_types": ["adoption_gap"],
        "project_governance_terms": [],
    }

    result = route_task(analysis)

    assert result["selected_route"] == "research_report"
    assert "domain_adapter" in result["rejected_routes"]


def test_low_confidence_uses_general_visual_narrative_route() -> None:
    result = route_task({"evidence_types": [], "relationship_types": []})

    assert result["selected_route"] == "general_visual_narrative"
    assert result["confidence"] < 0.6
    assert "TASK_ROUTE_LOW_CONFIDENCE" in result["warnings"]


@pytest.mark.parametrize("malformed_analysis", [None, "oops", [], ("a", "b")])
def test_malformed_analysis_is_parameterized(malformed_analysis: object) -> None:
    result = route_task(malformed_analysis)  # type: ignore[arg-type]

    assert result["selected_route"] == "general_visual_narrative"
    assert result["confidence"] < 0.6
    assert "TASK_ROUTE_INVALID_ANALYSIS" in result["warnings"]
