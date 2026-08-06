from typing import Dict, Tuple

from .evidence import assess_evidence
from .model import AnalysisMode, DecisionCase, DecisionType, FrameworkSelection, RouteAction, SufficiencyReport
from .registry import FrameworkRegistry
from .validation import validate_decision_case


FRAMEWORK_ORDER = ("value_gate", "resource_allocation", "schedule_analysis", "risk_treatment")
TYPE_FRAMEWORK: Dict[DecisionType, str] = {
    DecisionType.VALUE: "value_gate",
    DecisionType.RESOURCE: "resource_allocation",
    DecisionType.SCHEDULE: "schedule_analysis",
    DecisionType.RISK: "risk_treatment",
}
SIGNALS = (
    ("value_gate", ("continue", "pivot", "stop", "benefit", "business case")),
    ("resource_allocation", ("prioritize", "prioritization", "budget", "capacity", "allocation")),
    ("schedule_analysis", ("delay", "critical path", "bottleneck", "crash", "gate date")),
    ("risk_treatment", ("accept", "mitigate", "transfer", "escalate", "mitigation")),
)


def _candidates(case: DecisionCase) -> Tuple[str, ...]:
    decision_type = case.question.decision_type
    if decision_type is DecisionType.MULTI_DOMAIN:
        return FRAMEWORK_ORDER
    if decision_type in TYPE_FRAMEWORK:
        return (TYPE_FRAMEWORK[decision_type],)
    text = case.question.question.lower()
    matched = tuple(framework_id for framework_id, words in SIGNALS if any(word in text for word in words))
    return matched[:1]


def route_decision(case: DecisionCase, registry: FrameworkRegistry) -> FrameworkSelection:
    validation = validate_decision_case(case)
    if not validation.valid:
        report = SufficiencyReport(False, (), validation.reason_codes)
        return FrameworkSelection((), (), RouteAction.BLOCK, report, validation.reason_codes)

    candidates = _candidates(case)
    if not candidates:
        report = SufficiencyReport(False, ("decision_type",), ("decision_type_unknown",))
        return FrameworkSelection((), (), RouteAction.ASK, report, report.reason_codes, report.missing_fields)

    selected = []
    missing = []
    for framework_id in candidates:
        metadata = registry.metadata(framework_id)
        report = assess_evidence(case, metadata.required_evidence)
        if report.sufficient:
            selected.append(framework_id)
        else:
            missing.extend(report.missing_fields)
    missing_fields = tuple(dict.fromkeys(missing))
    if missing_fields:
        report = SufficiencyReport(False, missing_fields, ("required_evidence_missing",))
        action = RouteAction.ASK if case.question.requested_analysis_mode is AnalysisMode.PRESCRIPTIVE else RouteAction.DESCRIBE_ONLY
        return FrameworkSelection(candidates, tuple(selected), action, report, report.reason_codes, missing_fields)
    report = SufficiencyReport(True)
    return FrameworkSelection(candidates, tuple(selected), RouteAction.ROUTE, report)

