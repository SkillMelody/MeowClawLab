from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.contracts import PHASE2_CONTRACTS, PHASE3_CONTRACTS, get_component_contract
from components.inspection import inspect_phase1_pptx
from components.renderer import build_phase1_sample_deck
from components.tokens import resolve_tokens


class FutureContractsAndInspectionTests(unittest.TestCase):
    def test_phase2_contracts_mark_only_p0_as_implemented(self) -> None:
        expected = {
            "kpi_status",
            "milestone",
            "risk_heat_map",
            "raci",
            "raid",
            "action_tracker",
            "decision_matrix",
            "swimlane_dependency",
        }
        self.assertEqual(expected, set(PHASE2_CONTRACTS))
        for name, contract in PHASE2_CONTRACTS.items():
            if contract["priority"] == "P0":
                self.assertEqual("implemented", contract["status"], name)
                self.assertTrue(contract["renderer_implemented"], name)
                self.assertTrue(contract["layout_solver_implemented"], name)
            else:
                self.assertEqual("planned", contract["status"], name)
                self.assertFalse(contract["renderer_implemented"], name)
                self.assertFalse(contract["layout_solver_implemented"], name)
            self.assertTrue(contract["ir_required_fields"])
            self.assertTrue(contract["qa_gates"])
            self.assertIn(contract["priority"], {"P0", "P1", "P2"})
        self.assertEqual("risk_heat_map", get_component_contract("risk_heat_map")["component"])

    def test_phase3_contracts_record_dependencies_and_uncertainty(self) -> None:
        expected = {
            "budget_vs_actual",
            "waterfall",
            "resource_capacity",
            "portfolio_bubble",
            "release_train",
            "trend_burndown",
            "complex_governance",
            "liquid_glass_skin",
        }
        self.assertEqual(expected, set(PHASE3_CONTRACTS))
        for contract in PHASE3_CONTRACTS.values():
            self.assertEqual("planned", contract["status"])
            self.assertFalse(contract["renderer_implemented"])
            self.assertTrue(contract["dependencies"])
            self.assertTrue(contract["uncertainties"])

    def test_inspection_reads_native_object_evidence_from_pptx(self) -> None:
        legacy = json.loads((ROOT / "contracts" / "mckinsey-pmo.style.json").read_text(encoding="utf-8"))
        tokens = resolve_tokens(legacy)
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "phase1.pptx"
            build_phase1_sample_deck(output, tokens=tokens)
            report = inspect_phase1_pptx(output)
        self.assertTrue(report["passed"])
        self.assertEqual(3, report["slide_count"])
        self.assertEqual(0, report["picture_count"])
        self.assertGreaterEqual(report["chart_count"], 1)
        self.assertEqual([], report["missing_component_prefixes"])
        self.assertEqual(0, report["media_file_count"])


if __name__ == "__main__":
    unittest.main()
