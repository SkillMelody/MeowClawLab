from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from routing.page_router import route_page


class PageRouterTests(unittest.TestCase):
    def test_routes_single_project_health_to_executive_dashboard(self) -> None:
        result = route_page(
            {
                "intent": "summarize_single_project_health",
                "project_count": 1,
                "metrics": ["schedule", "budget", "risk", "quality"],
                "has_timeline": True,
                "decision_required": False,
            }
        )
        self.assertEqual(result["page_family"], "single_project_health_dashboard")
        self.assertEqual(result["primary_visual"], "executive_dashboard")

    def test_routes_cross_project_comparison_to_portfolio_dashboard(self) -> None:
        result = route_page(
            {
                "intent": "compare_project_portfolio",
                "project_count": 6,
                "metrics": ["health", "budget", "progress", "priority"],
                "has_timeline": False,
                "decision_required": True,
            }
        )
        self.assertEqual(result["page_family"], "portfolio_dashboard")
        self.assertIn("project_comparison_table", result["supporting_visuals"])

    def test_routes_resource_data_to_time_resource_dashboard(self) -> None:
        result = route_page(
            {
                "intent": "explain_resource_capacity",
                "project_count": 1,
                "metrics": ["fte", "utilization", "hours", "budget"],
                "has_timeline": True,
                "decision_required": True,
            }
        )
        self.assertEqual(result["page_family"], "time_resource_dashboard")
        self.assertEqual(result["primary_visual"], "resource_allocation_bars")

    def test_routes_enterprise_pmo_health_to_control_tower(self) -> None:
        result = route_page(
            {
                "intent": "monitor_pmo_control_tower",
                "project_count": 12,
                "metrics": ["milestones", "risk", "compliance", "budget", "stakeholders"],
                "has_timeline": True,
                "decision_required": True,
            }
        )
        self.assertEqual(result["page_family"], "pmo_control_tower")
        self.assertIn("risk_compliance_panel", result["supporting_visuals"])

    def test_routes_weekly_status_material_to_executive_one_pager(self) -> None:
        result = route_page(
            {
                "intent": "weekly_executive_status",
                "project_count": 1,
                "metrics": ["summary", "accomplishments", "next_steps", "risks", "milestones"],
                "has_timeline": True,
                "decision_required": False,
            }
        )
        self.assertEqual(result["page_family"], "executive_status_one_pager")
        self.assertEqual(result["primary_visual"], "status_narrative_grid")

    def test_rejects_data_visual_when_evidence_is_too_thin(self) -> None:
        result = route_page(
            {
                "intent": "show_trend",
                "project_count": 1,
                "metrics": ["adoption"],
                "observations": 1,
                "has_timeline": False,
                "decision_required": False,
            }
        )
        self.assertEqual(result["page_family"], "claim_evidence")
        self.assertEqual(result["primary_visual"], "native_text_callout")
        self.assertIn("insufficient_observations", result["reason_codes"])

    def test_routes_core_pmo_management_questions(self) -> None:
        cases = [
            ("explain_program_phases", "implementation_roadmap", "phase_roadmap"),
            ("show_key_milestones", "milestone_timeline", "milestone_axis"),
            ("manage_raid", "raid_register", "native_raid_table"),
            ("show_workstream_health", "workstream_board", "workstream_status_lanes"),
            ("clarify_accountability", "raci_matrix", "native_raci_table"),
            ("prioritize_risks", "risk_heat_map", "risk_matrix_5x5"),
            ("compare_decision_options", "decision_page", "weighted_decision_matrix"),
            ("show_trend", "kpi_dashboard", "kpi_trend_chart"),
            ("track_actions", "action_tracker", "native_action_table"),
        ]
        for intent, family, visual in cases:
            with self.subTest(intent=intent):
                result = route_page(
                    {
                        "intent": intent,
                        "project_count": 1,
                        "metrics": ["status", "owner", "date"],
                        "observations": 4 if intent == "show_trend" else 0,
                    }
                )
                self.assertEqual(result["page_family"], family)
                self.assertEqual(result["primary_visual"], visual)


if __name__ == "__main__":
    unittest.main()
