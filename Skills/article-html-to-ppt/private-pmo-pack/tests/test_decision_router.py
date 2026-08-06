import unittest
from dataclasses import replace
from datetime import date

from decision_support.evidence import EvidenceRequirement
from decision_support.model import (
    AnalysisMode,
    DecisionCase,
    DecisionQuestion,
    DecisionType,
    EvidenceItem,
    RouteAction,
    SourceLocation,
    SourceReference,
)
from decision_support.protocols import DecisionFramework
from decision_support.registry import FrameworkMetadata, FrameworkRegistry
from decision_support.router import route_decision


FRAMEWORKS = (
    ("value_gate", DecisionType.VALUE, (EvidenceRequirement("baseline", "Baseline"), EvidenceRequirement("options", "Continue/stop options"))),
    ("resource_allocation", DecisionType.RESOURCE, (EvidenceRequirement("budget", "Budget"), EvidenceRequirement("capacity", "Capacity"))),
    ("schedule_analysis", DecisionType.SCHEDULE, (EvidenceRequirement("dependencies", "Dependencies"), EvidenceRequirement("durations", "Durations"))),
    ("risk_treatment", DecisionType.RISK, (EvidenceRequirement("probability", "Probability"), EvidenceRequirement("impact", "Impact"))),
)


def registry():
    result = FrameworkRegistry()
    for framework_id, decision_type, requirements in FRAMEWORKS:
        result.register_metadata(FrameworkMetadata(framework_id, "1.0", frozenset({decision_type}), requirements))
    return result


def case(decision_type, question, tags=(), mode=AnalysisMode.PRESCRIPTIVE, owner="Sponsor"):
    source = SourceReference(id="src", title="System", source_type="system", location=SourceLocation("field", "record.amount"))
    evidence = tuple(EvidenceItem(id=f"ev-{tag}", claim=tag, tags=(tag,), source_ids=("src",)) for tag in tags)
    return DecisionCase(
        id="case", question=DecisionQuestion(
            id="q", decision_type=decision_type, question=question, owner=owner,
            decision_date=date(2026, 8, 1), horizon="FY2026", requested_analysis_mode=mode,
            option_ids=("continue", "stop"), baseline_id="baseline",
        ), sources=(source,), evidence=evidence, option_ids=("baseline", "continue", "stop"),
    )


class RouterTests(unittest.TestCase):
    def test_protocol_exposes_frozen_metadata_and_six_methods(self):
        annotations = DecisionFramework.__annotations__
        self.assertTrue({"framework_id", "version", "decision_types"}.issubset(annotations))
        methods = {name for name in DecisionFramework.__dict__ if not name.startswith("_")}
        self.assertTrue({"assess_sufficiency", "validate_evidence", "analyze", "run_sensitivity", "build_recommendation", "explain"}.issubset(methods))

    def test_routes_each_explicit_decision_type_deterministically(self):
        for framework_id, decision_type, requirements in FRAMEWORKS:
            with self.subTest(decision_type=decision_type):
                routed = route_decision(case(decision_type, "Decision", tuple(item.key for item in requirements)), registry())
                self.assertEqual(routed.route_action, RouteAction.ROUTE)
                self.assertEqual(routed.selected_framework_ids, (framework_id,))

    def test_multi_domain_order_is_fixed(self):
        tags = ("baseline", "options", "budget", "capacity", "dependencies", "durations", "probability", "impact")
        routed = route_decision(case(DecisionType.MULTI_DOMAIN, "Portfolio delay and risk", tags), registry())
        self.assertEqual(routed.selected_framework_ids, ("value_gate", "resource_allocation", "schedule_analysis", "risk_treatment"))

    def test_unknown_type_uses_explicit_question_signals(self):
        routed = route_decision(case(DecisionType.UNKNOWN, "Should we mitigate or transfer this risk?", ("probability", "impact")), registry())
        self.assertEqual(routed.selected_framework_ids, ("risk_treatment",))

    def test_missing_evidence_returns_exact_fields(self):
        routed = route_decision(case(DecisionType.RESOURCE, "Prioritize budget", ("budget",)), registry())
        self.assertEqual(routed.route_action, RouteAction.ASK)
        self.assertEqual(routed.requested_evidence_fields, ("capacity",))
        self.assertEqual(routed.reason_codes, ("required_evidence_missing",))

    def test_non_prescriptive_insufficient_case_is_describe_only(self):
        routed = route_decision(case(DecisionType.SCHEDULE, "Explain delay", (), AnalysisMode.DIAGNOSTIC), registry())
        self.assertEqual(routed.route_action, RouteAction.DESCRIBE_ONLY)

    def test_invalid_case_blocks_before_routing(self):
        routed = route_decision(case(DecisionType.VALUE, "Continue?", ("baseline", "options"), owner=None), registry())
        self.assertEqual(routed.route_action, RouteAction.BLOCK)
        self.assertIn("decision_owner_missing", routed.reason_codes)


if __name__ == "__main__":
    unittest.main()
