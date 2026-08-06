import json
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from decision_support.frameworks.risk_treatment import RiskTreatmentFramework
from decision_support.model import (
    AnalysisMode,
    DecisionCase,
    DecisionQuestion,
    DecisionType,
    RecommendationStatus,
)


FIXTURES = Path(__file__).parent / "fixtures" / "decision"


def load_case(name):
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"), parse_float=Decimal)
    return DecisionCase(
        id=payload["id"],
        question=DecisionQuestion(
            id=f"q-{payload['id']}",
            decision_type=DecisionType.RISK,
            question=payload["question"],
            owner=payload.get("owner", "Risk owner"),
            decision_date=date(2026, 8, 1),
            horizon=payload.get("horizon", "FY2027"),
            requested_analysis_mode=AnalysisMode.PRESCRIPTIVE,
            option_ids=tuple(payload.get("option_ids", ("accept", "mitigate", "transfer", "avoid"))),
            baseline_id="untreated",
        ),
        option_ids=("untreated",) + tuple(payload.get("option_ids", ("accept", "mitigate", "transfer", "avoid"))),
        extensions={"risk_treatment": payload["risk_treatment"]},
    )


def calculations(result):
    return {item.id: item.value for item in result.calculations}


class RiskTreatmentFrameworkTests(unittest.TestCase):
    def setUp(self):
        self.framework = RiskTreatmentFramework()

    def test_probability_horizon_range_and_multiple_consequences_drive_emv(self):
        result = self.framework.analyze(load_case("risk-mitigation.json"))
        values = calculations(result)
        self.assertEqual(values["probability_low"], Decimal("0.20"))
        self.assertEqual(values["probability_central"], Decimal("0.30"))
        self.assertEqual(values["probability_high"], Decimal("0.40"))
        self.assertEqual(values["consequence_central"], Decimal("1500000"))
        self.assertEqual(values["baseline_exposure_central"], Decimal("450000"))
        self.assertIn("probability horizon: FY2027", result.diagnostics)

    def test_failure_adjusted_residual_and_full_life_economics(self):
        result = self.framework.analyze(load_case("risk-mitigation.json"))
        values = calculations(result)
        self.assertEqual(values["adjusted_residual_probability_central"], Decimal("0.12"))
        self.assertEqual(values["adjusted_residual_exposure_central"], Decimal("135000.000"))
        self.assertEqual(values["exposure_reduction_central"], Decimal("315000.000"))
        self.assertEqual(values["full_life_mitigation_cost"], Decimal("150000"))
        self.assertEqual(values["net_benefit"], Decimal("165000.000"))
        self.assertEqual(values["roi"], Decimal("1.100"))
        self.assertEqual(values["benefit_cost_ratio"], Decimal("2.100"))

    def test_tolerance_and_mitigation_recommendation(self):
        case = load_case("risk-mitigation.json")
        result = self.framework.analyze(case)
        sensitivity = self.framework.run_sensitivity(case, result)
        recommendation = self.framework.build_recommendation(case, result, sensitivity)
        self.assertEqual(calculations(result)["tolerance_gap"], Decimal("35000.000"))
        self.assertEqual(recommendation.status, RecommendationStatus.CONDITIONAL)
        self.assertEqual(recommendation.selected_option_ids, ("mitigate",))
        self.assertTrue(any("tolerance" in condition.lower() for condition in recommendation.conditions))

    def test_transfer_uses_full_life_premium_and_is_selected(self):
        case = load_case("risk-transfer.json")
        result = self.framework.analyze(case)
        recommendation = self.framework.build_recommendation(case, result, self.framework.run_sensitivity(case, result))
        self.assertEqual(calculations(result)["full_life_mitigation_cost"], Decimal("120000"))
        self.assertEqual(calculations(result)["adjusted_residual_exposure_central"], Decimal("50000.00"))
        self.assertEqual(recommendation.selected_option_ids, ("transfer",))

    def test_risk_below_tolerance_is_accepted(self):
        case = load_case("risk-mitigation.json")
        data = dict(case.extensions["risk_treatment"])
        data["risk_tolerance"] = Decimal("500000")
        case = DecisionCase(**{**case.__dict__, "extensions": {"risk_treatment": data}})
        result = self.framework.analyze(case)
        recommendation = self.framework.build_recommendation(case, result, self.framework.run_sensitivity(case, result))
        self.assertEqual(recommendation.selected_option_ids, ("accept",))

    def test_legal_or_safety_constraint_mandates_escalation_over_economics(self):
        case = load_case("risk-mitigation.json")
        data = dict(case.extensions["risk_treatment"])
        data["mandatory_escalation"] = True
        data["constraint_types"] = ["legal", "safety"]
        case = DecisionCase(**{**case.__dict__, "extensions": {"risk_treatment": data}})
        result = self.framework.analyze(case)
        recommendation = self.framework.build_recommendation(case, result, self.framework.run_sensitivity(case, result))
        self.assertEqual(recommendation.selected_option_ids, ("escalate",))
        self.assertIn("mandatory_escalation", result.diagnostics)
        self.assertTrue(any("legal" in item.lower() for item in recommendation.binding_constraints))

    def test_ordinal_scores_are_descriptive_and_never_monetized(self):
        case = load_case("risk-ordinal-only.json")
        report = self.framework.assess_sufficiency(case)
        result = self.framework.analyze(case)
        recommendation = self.framework.build_recommendation(case, result, ())
        self.assertFalse(report.sufficient)
        self.assertIn("ordinal_risk_not_monetizable", report.reason_codes)
        self.assertEqual(result.analysis_mode, AnalysisMode.DESCRIPTIVE)
        self.assertEqual(result.calculations, ())
        self.assertEqual(recommendation.status, RecommendationStatus.NO_RECOMMENDATION)

    def test_tail_or_correlated_risk_blocks_roi_and_escalates(self):
        case = load_case("risk-tail.json")
        report = self.framework.validate_evidence(case)
        result = self.framework.analyze(case)
        recommendation = self.framework.build_recommendation(case, result, ())
        self.assertFalse(report.valid)
        self.assertTrue({"tail_risk_requires_escalation", "correlated_risk_requires_model"}.issubset(report.reason_codes))
        self.assertNotIn("roi", calculations(result))
        self.assertEqual(recommendation.selected_option_ids, ("escalate",))

    def test_named_sensitivity_includes_switching_points(self):
        case = load_case("risk-mitigation.json")
        result = self.framework.analyze(case)
        sensitivity = self.framework.run_sensitivity(case, result)
        variables = {item.variable for item in sensitivity}
        self.assertTrue({"event_probability", "mitigation_failure_probability", "mitigation_cost", "risk_tolerance"}.issubset(variables))
        self.assertTrue(all(item.id and "switch" in item.conclusion.lower() for item in sensitivity))

    def test_avoid_when_residual_is_intolerable_and_treatment_has_no_value(self):
        case = load_case("risk-mitigation.json")
        data = dict(case.extensions["risk_treatment"])
        data["mitigation"] = {**data["mitigation"], "one_time_cost": Decimal("900000")}
        case = DecisionCase(**{**case.__dict__, "extensions": {"risk_treatment": data}})
        result = self.framework.analyze(case)
        recommendation = self.framework.build_recommendation(case, result, self.framework.run_sensitivity(case, result))
        self.assertEqual(recommendation.selected_option_ids, ("avoid",))


if __name__ == "__main__":
    unittest.main()
