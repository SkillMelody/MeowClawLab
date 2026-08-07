from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.content_to_pages import select_pages


class ContentAdapterTests(unittest.TestCase):
    def test_selects_distinct_dashboard_families_from_evidence_units(self) -> None:
        manifest = select_pages(
            [
                {"id": "E1", "intent": "summarize_single_project_health", "project_count": 1, "metrics": ["schedule", "budget", "risk", "quality"], "has_timeline": True},
                {"id": "E2", "intent": "compare_project_portfolio", "project_count": 6, "metrics": ["health", "budget", "progress", "priority"]},
                {"id": "E3", "intent": "explain_resource_capacity", "project_count": 1, "metrics": ["fte", "utilization", "hours", "budget"], "has_timeline": True},
                {"id": "E4", "intent": "monitor_pmo_control_tower", "project_count": 12, "metrics": ["milestones", "risk", "compliance", "budget", "stakeholders"], "has_timeline": True},
                {"id": "E5", "intent": "weekly_executive_status", "project_count": 1, "metrics": ["summary", "accomplishments", "next_steps", "risks", "milestones"], "has_timeline": True},
            ]
        )
        self.assertEqual(
            [page["page_family"] for page in manifest["pages"]],
            [
                "single_project_health_dashboard",
                "portfolio_dashboard",
                "time_resource_dashboard",
                "pmo_control_tower",
                "executive_status_one_pager",
            ],
        )
        self.assertTrue(manifest["passed"])

    def test_records_layout_failure_in_selection_manifest(self) -> None:
        manifest = select_pages(
            [
                {
                    "id": "E1",
                    "intent": "summarize_single_project_health",
                    "project_count": 1,
                    "metrics": ["schedule", "budget", "risk"],
                    "supporting_visuals_override": ["a", "b", "c", "d", "e"],
                    "body_character_count": 220,
                }
            ]
        )
        self.assertFalse(manifest["passed"])
        self.assertIn("primary_visual_budget_exceeded", manifest["pages"][0]["layout_qa"]["reason_codes"])
        self.assertIn("text_density_exceeded", manifest["pages"][0]["layout_qa"]["reason_codes"])


if __name__ == "__main__":
    unittest.main()
