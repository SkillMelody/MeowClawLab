import json
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path

from decision_support.model import AnalysisMode, DecisionCase, DecisionQuestion, DecisionType, RecommendationStatus
from decision_support.frameworks.resource_allocation import ResourceAllocationFramework


FIXTURES = Path(__file__).parent / "fixtures" / "decision"


def resource_case(name):
    data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    question = DecisionQuestion(
        id="q-resource", decision_type=DecisionType.RESOURCE,
        question="Which portfolio should receive resources?", owner="Portfolio Board",
        decision_date=date(2026, 8, 1), horizon="FY2027",
        requested_analysis_mode=AnalysisMode.PRESCRIPTIVE,
        option_ids=tuple(item["id"] for item in data["options"]),
    )
    return DecisionCase(id="resource-case", question=question, option_ids=question.option_ids,
                        extensions={"resource_allocation": data})


class ResourceAllocationTests(unittest.TestCase):
    def setUp(self):
        self.framework = ResourceAllocationFramework()

    def test_fixed_anchor_scores_and_dominance(self):
        result = self.framework.analyze(resource_case("resource-ranking.json"))
        scores = result.extensions["option_scores"]
        self.assertAlmostEqual(scores["alpha"]["weighted_score"], 0.8)
        self.assertAlmostEqual(scores["beta"]["weighted_score"], 0.66)
        self.assertIn("gamma", result.extensions["dominance"]["alpha"])
        self.assertEqual(result.extensions["normalization"], "fixed_anchors")

    def test_missing_weight_source_and_sample_minmax_are_rejected(self):
        case = resource_case("resource-ranking.json")
        data = dict(case.extensions["resource_allocation"])
        data["criteria"] = [dict(data["criteria"][0], weight_source=""),
                            dict(data["criteria"][1], normalization="sample_minmax")]
        report = self.framework.assess_sufficiency(replace(case, extensions={"resource_allocation": data}))
        self.assertIn("weight_source_missing", report.reason_codes)
        self.assertIn("sample_relative_normalization_forbidden", report.reason_codes)

    def test_missing_option_score_is_reported(self):
        case = resource_case("resource-ranking.json")
        data = dict(case.extensions["resource_allocation"])
        options = [dict(item) for item in data["options"]]
        options[0]["scores"] = {"value": "80"}
        data["options"] = options
        report = self.framework.assess_sufficiency(replace(case, extensions={"resource_allocation": data}))
        self.assertIn("option_score_missing", report.reason_codes)

    def test_must_do_dependency_closure_and_complete_enumeration(self):
        result = self.framework.analyze(resource_case("resource-portfolio.json"))
        self.assertEqual(set(result.extensions["selected_option_ids"]), {"platform", "security", "growth"})
        self.assertEqual(result.extensions["method"], "complete_enumeration")
        self.assertTrue(result.extensions["optimal_within_declared_model"])
        self.assertIn("budget", result.extensions["binding_constraints"])
        self.assertGreater(result.extensions["opportunity_costs"]["migration"], 0)
        self.assertEqual(set(result.extensions["scenarios"]), {"base", "downside", "relief"})

    def test_infeasible_must_do_returns_infeasible_recommendation(self):
        case = resource_case("resource-infeasible.json")
        result = self.framework.analyze(case)
        self.assertFalse(result.extensions["feasible"])
        recommendation = self.framework.build_recommendation(case, result, ())
        self.assertEqual(recommendation.status, RecommendationStatus.INFEASIBLE)

    def test_fixed_anchors_prevent_rank_reversal_when_irrelevant_option_added(self):
        case = resource_case("resource-rank-reversal.json")
        first = self.framework.analyze(case).extensions["ranking"]
        data = dict(case.extensions["resource_allocation"])
        data["options"] = data["options"] + [{"id": "irrelevant", "scores": {"value": "5", "ease": "1"}, "cost": "2"}]
        second_case = replace(case, option_ids=case.option_ids + ("irrelevant",),
                              extensions={"resource_allocation": data})
        second = self.framework.analyze(second_case).extensions["ranking"]
        self.assertEqual(first, [item for item in second if item != "irrelevant"])

    def test_weight_sensitivity_finds_rank_flip(self):
        case = resource_case("resource-rank-reversal.json")
        result = self.framework.analyze(case)
        sensitivity = self.framework.run_sensitivity(case, result)
        self.assertTrue(any(item.variable.startswith("weight:") and "ranking changes" in item.conclusion for item in sensitivity))

    def test_cross_period_model_is_explicitly_heuristic(self):
        case = resource_case("resource-ranking.json")
        data = dict(case.extensions["resource_allocation"], periods=["Q1", "Q2"])
        result = self.framework.analyze(replace(case, extensions={"resource_allocation": data}))
        self.assertEqual(result.extensions["method"], "heuristic")
        self.assertFalse(result.extensions["optimal_within_declared_model"])
        self.assertIn("global optimality is not claimed", " ".join(result.limitations))

    def test_policy_and_date_constraints_apply_before_scoring(self):
        case = resource_case("resource-ranking.json")
        data = dict(case.extensions["resource_allocation"], required_by="2026-09-01",
                    policy_thresholds={"value": {"minimum": "60"}})
        options = [dict(item) for item in data["options"]]
        options[0]["available_by"] = "2026-10-01"
        data["options"] = options
        result = self.framework.analyze(replace(case, extensions={"resource_allocation": data}))
        self.assertNotIn("alpha", result.extensions["selected_option_ids"])
        self.assertNotIn("gamma", result.extensions["selected_option_ids"])

    def test_recommendation_contains_governance_and_counterargument(self):
        case = resource_case("resource-ranking.json")
        result = self.framework.analyze(case)
        sensitivity = self.framework.run_sensitivity(case, result)
        recommendation = self.framework.build_recommendation(case, result, sensitivity)
        self.assertTrue(recommendation.counterarguments)
        self.assertTrue(recommendation.conditions)
        self.assertTrue(recommendation.triggers)


if __name__ == "__main__":
    unittest.main()
