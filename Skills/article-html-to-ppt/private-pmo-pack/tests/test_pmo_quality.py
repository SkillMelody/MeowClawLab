from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quality.layout_budget import validate_layout_budget
from quality.semantic_qa import validate_pmo_semantics


class PMOQualityTests(unittest.TestCase):
    def test_rejects_dashboard_with_too_many_primary_visuals(self) -> None:
        result = validate_layout_budget(
            {
                "page_family": "single_project_health_dashboard",
                "primary_visual": "executive_dashboard",
                "supporting_visuals": ["status_kpis", "risk_issue_panel", "delivery_timeline", "budget_chart", "resource_heatmap"],
                "body_character_count": 180,
            }
        )
        self.assertFalse(result["passed"])
        self.assertIn("primary_visual_budget_exceeded", result["reason_codes"])

    def test_accepts_one_primary_visual_with_bounded_supporting_content(self) -> None:
        result = validate_layout_budget(
            {
                "page_family": "portfolio_dashboard",
                "primary_visual": "portfolio_health_matrix",
                "supporting_visuals": ["project_comparison_table", "priority_callout"],
                "body_character_count": 110,
            }
        )
        self.assertTrue(result["passed"])

    def test_semantic_qa_requires_owner_due_date_and_status_for_actions(self) -> None:
        result = validate_pmo_semantics(
            {
                "actions": [
                    {"owner": "PM", "action": "Confirm pilot", "deadline": "2026-08-01", "status": "amber"},
                    {"owner": "", "action": "Fix data", "deadline": "", "status": ""},
                ],
                "raci": {"roles": ["PM", "CTO"], "tasks": [{"task": "Go live", "assignments": ["R", "A"]}]},
                "risk_heat_map": [{"id": "R1", "label": "Data", "impact": 5, "likelihood": 4, "owner": "CDO"}],
                "decision": {"recommendation": "Proceed conditionally", "next_step": "Review in two weeks"},
            }
        )
        self.assertFalse(result["passed"])
        self.assertIn("action_missing_owner", result["reason_codes"])
        self.assertIn("action_missing_deadline", result["reason_codes"])
        self.assertIn("action_missing_status", result["reason_codes"])

    def test_semantic_qa_accepts_complete_pmo_data(self) -> None:
        result = validate_pmo_semantics(
            {
                "actions": [{"owner": "PM", "action": "Confirm pilot", "deadline": "2026-08-01", "status": "amber"}],
                "raci": {"roles": ["PM", "CTO"], "tasks": [{"task": "Go live", "assignments": ["R", "A"]}]},
                "risk_heat_map": [{"id": "R1", "label": "Data", "impact": 5, "likelihood": 4, "owner": "CDO"}],
                "decision": {"recommendation": "Proceed conditionally", "next_step": "Review in two weeks"},
            }
        )
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
