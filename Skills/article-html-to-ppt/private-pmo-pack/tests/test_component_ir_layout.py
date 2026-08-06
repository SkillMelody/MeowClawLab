from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ir import ComponentValidationError, validate_component_ir
from components.layout import (
    angle_anchor,
    angle_in_interval,
    date_to_position,
    layout_doughnut,
    layout_gantt,
    layout_roadmap,
    leaders_have_no_crossings,
)
from components.tokens import resolve_tokens


def load_fixture(name: str) -> dict:
    return json.loads((ROOT / "tests" / "fixtures" / name).read_text(encoding="utf-8"))


class ComponentIRLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        legacy = json.loads((ROOT / "contracts" / "mckinsey-pmo.style.json").read_text(encoding="utf-8"))
        self.tokens = resolve_tokens(legacy)

    def test_doughnut_ir_is_semantic_and_anchor_follows_mid_angle(self) -> None:
        ir = {
            "type": "annotated_doughnut",
            "title": "Portfolio mix",
            "center_metric": "100%",
            "center_caption": "investment",
            "categories": [
                {"label": "Platform", "value": 50, "color_role": "sequence.phase_1"},
                {"label": "Data", "value": 30, "color_role": "sequence.phase_2"},
                {"label": "Change", "value": 20, "color_role": "sequence.phase_3"},
            ],
        }
        validate_component_ir(ir)
        anchor = angle_anchor(2.0, 2.0, 1.0, 0.0)
        self.assertAlmostEqual(3.0, anchor["x"])
        self.assertAlmostEqual(2.0, anchor["y"])
        layout = layout_doughnut(ir, {"x": 0.0, "y": 0.0, "w": 8.0, "h": 4.5}, self.tokens)
        self.assertEqual("annotated", layout["mode"])
        self.assertEqual(3, len(layout["leaders"]))
        self.assertTrue(leaders_have_no_crossings(layout["leaders"]))
        self.assertTrue(
            all(abs(leader["points"][0]["y"] - leader["points"][-1]["y"]) >= 0.15 for leader in layout["leaders"])
        )
        for segment in layout["segments"]:
            anchor = segment["anchor"]
            endpoint_angle = math.atan2(
                anchor["y"] - layout["center"]["y"],
                anchor["x"] - layout["center"]["x"],
            )
            self.assertTrue(
                angle_in_interval(endpoint_angle, segment["start_angle"], segment["end_angle"]),
                msg=segment["label"],
            )
            self.assertAlmostEqual(segment["mid_angle"], segment["endpoint_angle"], places=6)
        self.assertAlmostEqual(-math.pi / 2, layout["segments"][0]["start_angle"], places=6)
        self.assertAlmostEqual(3 * math.pi / 2, layout["segments"][-1]["end_angle"], places=6)
        self.assertEqual(0, layout["chart_first_slice_angle_deg"])

    def test_angle_interval_handles_zero_degree_wrap(self) -> None:
        self.assertTrue(angle_in_interval(math.radians(355), math.radians(330), math.radians(390)))
        self.assertTrue(angle_in_interval(math.radians(5), math.radians(330), math.radians(390)))
        self.assertFalse(angle_in_interval(math.radians(180), math.radians(330), math.radians(390)))

    def test_crowded_doughnut_uses_legend_fallback(self) -> None:
        ir = load_fixture("doughnut-crowded.json")
        validate_component_ir(ir)
        layout = layout_doughnut(ir, {"x": 0.0, "y": 0.0, "w": 6.0, "h": 2.3}, self.tokens)
        self.assertEqual("legend", layout["mode"])
        self.assertIn("label_lane_capacity_exceeded", layout["reason_codes"])

    def test_roadmap_boundaries_align_gates_and_overflow_requests_split(self) -> None:
        normal = {
            "type": "roadmap",
            "title": "Delivery path",
            "phases": [
                {"id": "P1", "name": "Discover", "period": "Jul", "objective": "Align", "outputs": ["Charter"], "exit_condition": "Scope signed", "gate": "G1"},
                {"id": "P2", "name": "Design", "period": "Aug", "objective": "Design", "outputs": ["Blueprint"], "exit_condition": "Design signed", "gate": "G2"},
                {"id": "P3", "name": "Build", "period": "Sep", "objective": "Build", "outputs": ["Release"], "exit_condition": "Release ready", "gate": "G3"},
                {"id": "P4", "name": "Scale", "period": "Oct", "objective": "Scale", "outputs": ["Runbook"], "exit_condition": "Runbook accepted", "gate": "G4"},
            ],
        }
        validate_component_ir(normal)
        layout = layout_roadmap(normal, {"x": 0.5, "y": 1.5, "w": 12.0, "h": 4.8}, self.tokens)
        self.assertEqual("single", layout["mode"])
        self.assertEqual(layout["boundaries"], [gate["x"] for gate in layout["gates"]])
        self.assertTrue(all(layout["phase_boxes"][idx]["x2"] == layout["boundaries"][idx] for idx in range(4)))

        overflow = load_fixture("roadmap-overflow.json")
        validate_component_ir(overflow)
        overflow_layout = layout_roadmap(overflow, {"x": 0.5, "y": 1.5, "w": 12.0, "h": 4.8}, self.tokens)
        self.assertEqual("split", overflow_layout["mode"])
        self.assertIn("phase_count_exceeded", overflow_layout["reason_codes"])

    def test_gantt_maps_dates_and_preserves_declared_disjoint_intervals(self) -> None:
        ir = load_fixture("gantt-disjoint.json")
        validate_component_ir(ir)
        self.assertAlmostEqual(0.5, date_to_position("2026-07-06", "2026-07-01", "2026-07-11"))
        layout = layout_gantt(ir, {"x": 3.2, "y": 1.6, "w": 9.4, "h": 4.8}, self.tokens)
        self.assertEqual(2, len(layout["rows"][0]["planned_bars"]))
        self.assertTrue(layout["rows"][0]["planned_bars"][0]["x2"] < layout["rows"][0]["planned_bars"][1]["x1"])
        self.assertGreater(layout["reference_x"], 3.2)
        self.assertEqual(13, len(layout["time_columns"]))
        self.assertEqual(layout["time_columns"][0]["x1"], layout["month_spans"][0]["x1"])
        self.assertEqual(layout["time_columns"][-1]["x2"], layout["month_spans"][-1]["x2"])
        for first, second in zip(layout["month_spans"], layout["month_spans"][1:]):
            self.assertAlmostEqual(first["x2"], second["x1"])
        timeline_right = 3.2 + 9.4
        for row in layout["rows"]:
            for milestone in row["milestones"]:
                self.assertGreaterEqual(milestone["x"], 3.2 + layout["milestone_half_width"])
                self.assertLessEqual(milestone["x"], timeline_right - layout["milestone_half_width"])

    def test_gantt_rejects_invalid_date_ranges(self) -> None:
        with self.assertRaises(ComponentValidationError) as error:
            validate_component_ir(load_fixture("gantt-invalid-date.json"))
        self.assertIn("date_order_invalid", error.exception.reason_codes)


if __name__ == "__main__":
    unittest.main()
