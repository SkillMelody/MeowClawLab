import json
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path
from types import MappingProxyType

from decision_support.frameworks.schedule_analysis import ScheduleAnalysisFramework, analyze_schedule
from decision_support.model import AnalysisMode, DecisionCase, DecisionQuestion, DecisionType


FIXTURES = Path(__file__).parent / "fixtures" / "decision"


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


class ScheduleAnalysisTests(unittest.TestCase):
    def test_calendar_and_all_dependency_types_drive_forward_pass(self):
        result = analyze_schedule(fixture("schedule-cpm.json"))

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["tasks"]["A"]["es"], 0)
        self.assertEqual(result["tasks"]["B"]["es"], 3)  # FS + 1
        self.assertEqual(result["tasks"]["C"]["es"], 1)  # SS + 1
        self.assertEqual(result["tasks"]["D"]["es"], 6)  # FF + 1
        self.assertEqual(result["tasks"]["E"]["es"], 2)  # SF + 3
        self.assertEqual(result["tasks"]["B"]["es_date"], "2026-07-30")
        self.assertEqual(result["tasks"]["B"]["ef_date"], "2026-08-05")

    def test_backward_pass_required_finish_and_driving_dependencies(self):
        payload = fixture("schedule-cpm.json")
        payload["required_finish"] = "2026-08-04"
        result = analyze_schedule(payload)

        self.assertEqual(result["finish_variance"], -3)
        self.assertEqual(result["tasks"]["F"], {
            "es": 7, "ef": 8, "ls": 4, "lf": 5, "total_float": -3,
            "es_date": "2026-08-06", "ef_date": "2026-08-07",
            "ls_date": "2026-08-03", "lf_date": "2026-08-04",
        })
        self.assertEqual(result["driving_dependencies"], ["ab", "ac", "bd", "ce", "df", "eg"])

    def test_multiple_critical_paths_are_preserved_and_near_critical_is_configurable(self):
        result = analyze_schedule(fixture("schedule-multiple-critical.json"))

        self.assertEqual(result["critical_subgraph"]["task_ids"], ["A", "B", "C", "D", "E"])
        self.assertEqual(result["critical_subgraph"]["dependency_ids"], ["ab", "cd", "be", "de"])
        self.assertEqual(result["near_critical_task_ids"], ["N"])

    def test_cycle_and_dangling_endpoint_block_analysis(self):
        cycle = analyze_schedule(fixture("schedule-cycle.json"))
        dangling_payload = fixture("schedule-cycle.json")
        dangling_payload["dependencies"] = [
            {"id": "ax", "predecessor": "A", "successor": "X", "type": "FS", "lag": 0}
        ]
        dangling = analyze_schedule(dangling_payload)

        self.assertEqual(cycle["reason_codes"], ["schedule_dependency_cycle"])
        self.assertEqual(dangling["reason_codes"], ["schedule_dependency_endpoint_missing"])

    def test_actual_dates_must_be_consistent_with_data_date(self):
        payload = fixture("schedule-cpm.json")
        payload["tasks"][0]["actual_finish"] = "2026-07-28"
        without_start = analyze_schedule(payload)
        payload["tasks"][0]["actual_start"] = "2026-07-27"
        payload["tasks"][0]["actual_finish"] = "2026-07-29"
        after_data_date = analyze_schedule(payload)

        self.assertIn("schedule_actual_finish_without_start", without_start["reason_codes"])
        self.assertIn("schedule_actual_after_data_date", after_data_date["reason_codes"])

        payload["tasks"][0]["remaining_duration"] = 1
        del payload["data_date"]
        missing_data_date = analyze_schedule(payload)
        self.assertIn("schedule_data_date_missing", missing_data_date["reason_codes"])

    def test_data_date_is_required_even_without_actuals(self):
        payload = fixture("schedule-cpm.json")
        del payload["data_date"]

        result = analyze_schedule(payload)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("schedule_data_date_missing", result["reason_codes"])

    def test_resource_overload_and_finite_capacity_scenario_are_bounded(self):
        result = analyze_schedule(fixture("schedule-resource-conflict.json"))

        self.assertEqual(result["overload_intervals"][0], {
            "resource": "engineer", "start": 0, "finish": 1, "demand": 2,
            "capacity": 1, "task_ids": ["A", "B"],
        })
        scenario = result["capacity_scenarios"][0]
        self.assertEqual(scenario["method"], "bounded_serial_capacity_scenario")
        self.assertEqual(scenario["task_starts"], {"A": 0, "B": 3, "C": 5})
        self.assertIn("not global resource leveling", scenario["limitations"][0])

    def test_pert_is_analytic_and_disclaims_project_probability(self):
        payload = fixture("schedule-cpm.json")
        payload["tasks"][0].update(optimistic=1, most_likely=2, pessimistic=7)
        result = analyze_schedule(payload)

        self.assertEqual(result["pert"]["A"]["expected_duration"], "2.666666666666666666666666667")
        self.assertEqual(result["pert"]["A"]["method"], "analytic_pert_approximation")
        self.assertTrue(any("no Monte Carlo or project P80" in item for item in result["limitations"]))

    def test_framework_adapts_shared_protocol_without_shared_model_changes(self):
        payload = fixture("schedule-cpm.json")
        case = DecisionCase(
            id="case-schedule",
            question=DecisionQuestion(
                id="q", decision_type=DecisionType.SCHEDULE, question="What drives the finish?",
                owner="PMO", decision_date=date(2026, 7, 30), horizon="Release",
                requested_analysis_mode=AnalysisMode.DIAGNOSTIC,
            ),
            extensions=MappingProxyType({"schedule": payload}),
        )
        framework = ScheduleAnalysisFramework()
        result = framework.analyze(case)

        self.assertTrue(framework.assess_sufficiency(case).sufficient)
        self.assertTrue(framework.validate_evidence(case).valid)
        self.assertEqual(result.framework_id, "schedule_analysis")
        self.assertEqual(result.extensions["schedule"]["status"], "ok")
        self.assertIn("working-time calendar", framework.explain(result).summary)


if __name__ == "__main__":
    unittest.main()
