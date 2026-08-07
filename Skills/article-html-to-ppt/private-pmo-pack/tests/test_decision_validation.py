import unittest
from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

from decision_support.model import (
    AnalysisMode,
    AnalysisResult,
    Assumption,
    CalculationTrace,
    ConfidenceLevel,
    Counterargument,
    DecisionCase,
    DecisionQuestion,
    DecisionType,
    EvidenceItem,
    FreshnessStatus,
    RecommendationStatus,
    ReviewTrigger,
    SensitivityResult,
    SourceLocation,
    SourceReference,
    TimeBasis,
    UnitSpec,
)
from decision_support.recommendation import build_recommendation_trace, prescriptive_readiness
from decision_support.validation import validate_decision_case


NOW = datetime(2026, 7, 25, tzinfo=timezone.utc)


def base_case(**changes):
    source = SourceReference(id="src", title="Ledger", source_type="system", location=SourceLocation("field", "forecast", "amount"))
    evidence = EvidenceItem(
        id="ev",
        claim="Approved baseline",
        metric="cost",
        value=Decimal("100"),
        unit=UnitSpec("currency", "USD", currency="USD", time_denominator="year", scope="programme"),
        time_basis=TimeBasis("year", date(2026, 1, 1), date(2026, 12, 31)),
        source_ids=("src",),
        confidence=ConfidenceLevel.HIGH,
        freshness=FreshnessStatus.CURRENT,
        decisive=True,
    )
    question = DecisionQuestion(
        id="q", decision_type=DecisionType.VALUE, question="Continue or stop?", owner="Sponsor",
        decision_date=date(2026, 8, 1), horizon="FY2026", requested_analysis_mode=AnalysisMode.PRESCRIPTIVE,
        option_ids=("continue", "stop"), baseline_id="baseline",
    )
    case = DecisionCase(
        id="case", question=question, sources=(source,), evidence=(evidence,),
        assumptions=(Assumption(id="a", statement="Adoption holds", owner="Product", expiry_date=date(2026, 10, 1), trigger="Adoption below 70%"),),
        option_ids=("baseline", "continue", "stop"), created_at=NOW, updated_at=NOW,
    )
    return replace(case, **changes)


class DecisionValidationTests(unittest.TestCase):
    def test_incompatible_unit_currency_time_and_scope_have_stable_codes(self):
        case = base_case()
        other = replace(
            case.evidence[0], id="ev-2", value=Decimal("90"),
            unit=UnitSpec("currency", "EUR", currency="EUR", time_denominator="month", scope="workstream"),
            time_basis=TimeBasis("month", date(2026, 1, 1), date(2026, 1, 31)),
        )
        codes = validate_decision_case(replace(case, evidence=case.evidence + (other,))).reason_codes
        self.assertTrue({"incompatible_currency", "incompatible_time_basis", "incompatible_scope"}.issubset(codes))

    def test_stale_and_conflicting_decisive_evidence_are_blocking(self):
        item = replace(base_case().evidence[0], freshness=FreshnessStatus.STALE, conflict_status="unresolved")
        report = validate_decision_case(replace(base_case(), evidence=(item,)))
        self.assertFalse(report.valid)
        self.assertIn("stale_decisive_evidence", report.reason_codes)
        self.assertIn("unresolved_evidence_conflict", report.reason_codes)

    def test_assumption_owner_expiry_and_trigger_are_required(self):
        assumption = Assumption(id="a-bad", statement="Demand holds")
        codes = validate_decision_case(replace(base_case(), assumptions=(assumption,))).reason_codes
        self.assertTrue({"assumption_owner_missing", "assumption_expiry_missing", "assumption_trigger_missing"}.issubset(codes))

    def test_empty_source_location_and_reference_cycle_are_rejected(self):
        source = SourceReference(id="src-empty", title="System", source_type="system", location=SourceLocation("field", ""))
        first = EvidenceItem(id="one", claim="one", derivation_id="two")
        second = EvidenceItem(id="two", claim="two", derivation_id="one")
        report = validate_decision_case(replace(base_case(), sources=(source,), evidence=(first, second)))
        self.assertIn("source_location_missing", report.reason_codes)
        self.assertIn("reference_cycle", report.reason_codes)

    def test_prescriptive_readiness_requires_complete_recommendation_trace(self):
        case = base_case()
        result = AnalysisResult(
            id="run", framework_id="value_gate", framework_version="1", input_snapshot_hash="abc",
            analysis_mode=AnalysisMode.PRESCRIPTIVE,
            calculations=(CalculationTrace("calc", "100 - 80", Decimal("20"), ("ev",), ("a",)),),
            evidence_ids=("ev",), assumption_ids=("a",),
        )
        empty = prescriptive_readiness(case, result, ())
        self.assertTrue({"sensitivity_missing", "counterargument_missing", "recommendation_owner_missing", "review_date_missing", "review_trigger_missing"}.issubset(empty.reason_codes))

        sensitivity = (SensitivityResult("s1", "adoption", "60%", "90%", "stable"),)
        recommendation = build_recommendation_trace(
            case, result, sensitivity, status=RecommendationStatus.CONDITIONAL, statement="Continue with adoption gate",
            counterarguments=(Counterargument("c1", "Adoption may lag", "Review monthly", ("ev",)),),
            owner="Sponsor", review_date=date(2026, 9, 1), triggers=(ReviewTrigger("t1", "Adoption below 70%", "Pivot"),),
        )
        ready = prescriptive_readiness(case, result, sensitivity, recommendation)
        self.assertTrue(ready.ready)
        self.assertEqual(recommendation.confidence, ConfidenceLevel.HIGH)
        self.assertIn("evidence quality", recommendation.confidence_basis.lower())
        self.assertNotIn("probability", recommendation.confidence_basis.lower())


if __name__ == "__main__":
    unittest.main()
