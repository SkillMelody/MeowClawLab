import json
import unittest
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType

from decision_support.model import (
    AnalysisMode,
    AnalysisResult,
    Assumption,
    ConfidenceLevel,
    Counterargument,
    DecisionCase,
    DecisionQuestion,
    DecisionType,
    EvidenceItem,
    EvidenceKind,
    FreshnessStatus,
    Recommendation,
    RecommendationStatus,
    ReviewTrigger,
    RouteAction,
    SourceLocation,
    SourceReference,
    UnitSpec,
)
from decision_support.pipeline import analyze_decision
from decision_support.registry import FrameworkRegistry, default_registry
from decision_support.frameworks.value_gate import ValueGateFramework


FIXTURES = Path(__file__).parent / "fixtures" / "decision"


def _payload(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _case(decision_type, extension_key, fixture, *, mode=AnalysisMode.PRESCRIPTIVE):
    data = _payload(fixture)
    if extension_key == "risk_treatment":
        data = data["risk_treatment"]
    options = {
        "value_gate": ("baseline", "continue", "pivot", "stop"),
        "resource_allocation": ("baseline", "alpha", "beta", "gamma"),
        "schedule": ("baseline", "recover", "hold"),
        "risk_treatment": ("baseline", "mitigate", "accept"),
    }[extension_key]
    source = SourceReference(
        id="src", title="Approved system extract", source_type="system",
        location=SourceLocation("field", "decision.input"),
    )
    evidence = EvidenceItem(
        id="ev", claim="Approved decision input", metric="decision_input",
        value=Decimal("1"), unit=UnitSpec("count", "item"), source_ids=("src",),
        kind=EvidenceKind.FACT, confidence=ConfidenceLevel.HIGH,
        confidence_rationale="Approved source", freshness=FreshnessStatus.CURRENT,
        decisive=True,
    )
    assumption = Assumption(
        id="assumption", statement="Inputs remain valid", owner="Sponsor",
        validation_method="Review source", review_date=date(2026, 8, 15),
        trigger="Source changes",
    )
    return DecisionCase(
        id=f"case-{decision_type.value}",
        question=DecisionQuestion(
            id=f"q-{decision_type.value}", decision_type=decision_type,
            question="Make the declared decision", owner="Sponsor",
            decision_date=date(2026, 8, 1), horizon="FY2027",
            requested_analysis_mode=mode, option_ids=options[1:],
            baseline_id="baseline",
        ),
        sources=(source,), evidence=(evidence,), assumptions=(assumption,),
        option_ids=options, extensions=MappingProxyType({extension_key: data}),
    )


class DecisionPipelineTests(unittest.TestCase):
    def test_registry_contains_four_real_plugins_in_router_order(self):
        registry = default_registry()
        self.assertEqual(
            tuple(item.framework_id for item in registry.all_metadata()),
            ("value_gate", "resource_allocation", "schedule_analysis", "risk_treatment"),
        )
        self.assertTrue(all(registry.framework(item.framework_id) for item in registry.all_metadata()))

    def test_four_minimal_cases_execute_the_expected_framework(self):
        cases = (
            (_case(DecisionType.VALUE, "value_gate", "value-continue.json"), "value_gate"),
            (_case(DecisionType.RESOURCE, "resource_allocation", "resource-ranking.json"), "resource_allocation"),
            (_case(DecisionType.SCHEDULE, "schedule", "schedule-cpm.json", mode=AnalysisMode.DIAGNOSTIC), "schedule_analysis"),
            (_case(DecisionType.RISK, "risk_treatment", "risk-mitigation.json"), "risk_treatment"),
        )
        for case, framework_id in cases:
            with self.subTest(framework_id=framework_id):
                package = analyze_decision(case)
                self.assertEqual(package.route.route_action, RouteAction.ROUTE)
                self.assertEqual(tuple(item.framework_id for item in package.analysis_results), (framework_id,))
                self.assertEqual(package.input_hash, package.audit["input_hash"])

    def test_multi_domain_execution_is_ordered_and_not_opaque(self):
        value = _case(DecisionType.VALUE, "value_gate", "value-continue.json")
        extensions = {
            "value_gate": _payload("value-continue.json"),
            "resource_allocation": _payload("resource-ranking.json"),
            "schedule": _payload("schedule-cpm.json"),
            "risk_treatment": _payload("risk-mitigation.json")["risk_treatment"],
        }
        case = replace(
            value,
            id="case-multi",
            question=replace(value.question, decision_type=DecisionType.MULTI_DOMAIN),
            extensions=MappingProxyType(extensions),
        )
        package = analyze_decision(case)
        expected = ("value_gate", "resource_allocation", "schedule_analysis", "risk_treatment")
        self.assertEqual(tuple(item.framework_id for item in package.analysis_results), expected)
        self.assertEqual(tuple(item.framework_id for item in package.framework_recommendations), expected)
        self.assertNotIn("score", package.audit)

    def test_framework_sufficiency_preserves_ask_and_describe_only(self):
        case = _case(DecisionType.VALUE, "value_gate", "value-insufficient.json")
        prescriptive = analyze_decision(case)
        self.assertEqual(prescriptive.route.route_action, RouteAction.ASK)
        self.assertEqual(prescriptive.analysis_results, ())
        self.assertIn("value_gate.options.stop", prescriptive.route.requested_evidence_fields)

        diagnostic = analyze_decision(replace(case, question=replace(case.question, requested_analysis_mode=AnalysisMode.DIAGNOSTIC)))
        self.assertEqual(diagnostic.route.route_action, RouteAction.DESCRIBE_ONLY)
        self.assertEqual(diagnostic.recommendation.status, RecommendationStatus.NO_RECOMMENDATION)

    def test_shared_validation_blocks_incompatible_units_and_conflicts(self):
        case = _case(DecisionType.VALUE, "value_gate", "value-continue.json")
        conflicting = replace(
            case.evidence[0], id="ev-conflict", value=Decimal("2"),
            unit=UnitSpec("count", "item", time_denominator="month"),
            conflict_status="disputed",
        )
        original = replace(case.evidence[0], unit=UnitSpec("money", "USD", currency="USD", time_denominator="year"))
        package = analyze_decision(replace(case, evidence=(original, conflicting)))
        self.assertEqual(package.route.route_action, RouteAction.BLOCK)
        self.assertIn("incompatible_unit", package.route.reason_codes)
        self.assertIn("unresolved_evidence_conflict", package.route.reason_codes)
        self.assertEqual(package.recommendation.status, RecommendationStatus.NO_RECOMMENDATION)

    def test_input_is_not_mutated_and_canonical_hash_is_reproducible(self):
        case = _case(DecisionType.VALUE, "value_gate", "value-continue.json")
        before = repr(case)
        first = analyze_decision(case)
        second = analyze_decision(replace(case))
        self.assertEqual(repr(case), before)
        self.assertEqual(first.input_hash, second.input_hash)
        self.assertEqual(tuple(item.input_snapshot_hash for item in first.analysis_results), (first.input_hash,))

    def test_prescriptive_readiness_downgrades_every_missing_governance_field(self):
        case = _case(DecisionType.VALUE, "value_gate", "value-continue.json")
        class IncompleteValueFramework(ValueGateFramework):
            def run_sensitivity(self, case, result):
                return ()

            def build_recommendation(self, case, result, sensitivity):
                recommendation = super().build_recommendation(case, result, sensitivity)
                return replace(
                    recommendation, status=RecommendationStatus.RECOMMEND,
                    counterarguments=(), sensitivity_summary=(), owner=None,
                    review_date=None, conditions=(), triggers=(),
                )

        registry = FrameworkRegistry()
        registry.register(IncompleteValueFramework())
        package = analyze_decision(case, registry)
        framework_output = package.framework_recommendations[0]
        readiness = framework_output.readiness
        self.assertEqual(framework_output.recommendation.status, RecommendationStatus.NO_RECOMMENDATION)
        self.assertEqual(package.recommendation.status, RecommendationStatus.NO_RECOMMENDATION)
        self.assertFalse(readiness.ready)
        self.assertTrue({
            "counterargument_missing", "sensitivity_missing", "recommendation_owner_missing",
            "review_date_missing", "recommendation_conditions_missing", "review_trigger_missing",
        }.issubset(readiness.reason_codes))

    def test_existing_no_recommendation_and_infeasible_statuses_are_preserved(self):
        schedule = analyze_decision(_case(
            DecisionType.SCHEDULE, "schedule", "schedule-cpm.json", mode=AnalysisMode.DIAGNOSTIC,
        ))
        self.assertEqual(schedule.recommendation.status, RecommendationStatus.NO_RECOMMENDATION)

        resource = analyze_decision(_case(
            DecisionType.RESOURCE, "resource_allocation", "resource-infeasible.json",
        ))
        self.assertEqual(resource.recommendation.status, RecommendationStatus.INFEASIBLE)


if __name__ == "__main__":
    unittest.main()
