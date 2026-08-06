from collections import defaultdict
from typing import Dict, List, Set

from .model import DecisionCase, EvidenceKind, FreshnessStatus, ValidationIssue, ValidationReport


def validate_decision_case(case: DecisionCase) -> ValidationReport:
    issues: List[ValidationIssue] = []
    question = case.question
    if not question.question.strip():
        issues.append(ValidationIssue("decision_question_missing", "decision question is required"))
    if not question.owner:
        issues.append(ValidationIssue("decision_owner_missing", "decision owner is required"))
    if question.decision_date is None:
        issues.append(ValidationIssue("decision_date_missing", "decision date is required"))
    if not question.horizon:
        issues.append(ValidationIssue("decision_horizon_missing", "decision horizon is required"))
    if not question.option_ids:
        issues.append(ValidationIssue("option_boundary_missing", "decision options are required"))
    if question.baseline_id is None:
        issues.append(ValidationIssue("baseline_missing", "decision baseline is required"))
    for option_id in question.option_ids:
        if option_id not in case.option_ids:
            issues.append(ValidationIssue("broken_reference", f"unknown option: {option_id}"))
    if question.baseline_id and question.baseline_id not in case.option_ids:
        issues.append(ValidationIssue("broken_reference", f"unknown baseline: {question.baseline_id}"))

    seen = set()
    records = (case.question,) + case.sources + case.evidence + case.assumptions + case.recommendations + case.decision_records
    for record in records:
        if record.id in seen:
            issues.append(ValidationIssue("duplicate_id", f"duplicate id: {record.id}"))
        seen.add(record.id)
    source_ids = {source.id for source in case.sources}
    evidence_ids = {item.id for item in case.evidence}
    for source in case.sources:
        if not source.location or not source.location.kind.strip() or not source.location.value.strip():
            issues.append(ValidationIssue("source_location_missing", f"source {source.id} has no specific location"))
    for item in case.evidence:
        for source_id in item.source_ids:
            if source_id not in source_ids:
                issues.append(ValidationIssue("broken_reference", f"unknown source: {source_id}"))
        if item.derivation_id and item.derivation_id not in evidence_ids:
            issues.append(ValidationIssue("broken_reference", f"unknown derivation: {item.derivation_id}"))
        if item.decisive and item.freshness is FreshnessStatus.STALE:
            issues.append(ValidationIssue("stale_decisive_evidence", f"decisive evidence is stale: {item.id}"))
        if item.decisive and item.conflict_status not in ("none", "resolved"):
            issues.append(ValidationIssue("unresolved_evidence_conflict", f"decisive evidence is disputed: {item.id}"))
        if item.decisive and item.kind is EvidenceKind.ESTIMATE and (
            item.estimate is None or not item.estimate.method.strip()
        ):
            issues.append(ValidationIssue("decisive_estimate_range_or_method_missing", f"estimate trace is incomplete: {item.id}"))

    metric_groups: Dict[str, list] = defaultdict(list)
    for item in case.evidence:
        if item.metric and item.unit:
            metric_groups[item.metric].append(item)
    for items in metric_groups.values():
        for left, right in zip(items, items[1:]):
            if left.unit.dimension != right.unit.dimension:
                issues.append(ValidationIssue("incompatible_unit", "evidence dimensions are incompatible"))
            if left.unit.currency != right.unit.currency:
                issues.append(ValidationIssue("incompatible_currency", "evidence currencies are incompatible"))
            if left.unit.time_denominator != right.unit.time_denominator or (
                left.time_basis and right.time_basis and left.time_basis.period != right.time_basis.period
            ):
                issues.append(ValidationIssue("incompatible_time_basis", "evidence time bases are incompatible"))
            if left.unit.scope != right.unit.scope:
                issues.append(ValidationIssue("incompatible_scope", "evidence scopes are incompatible"))

    for assumption in case.assumptions:
        if not assumption.owner:
            issues.append(ValidationIssue("assumption_owner_missing", f"assumption owner missing: {assumption.id}"))
        if assumption.expiry_date is None and assumption.review_date is None:
            issues.append(ValidationIssue("assumption_expiry_missing", f"assumption expiry/review missing: {assumption.id}"))
        if not assumption.trigger:
            issues.append(ValidationIssue("assumption_trigger_missing", f"assumption trigger missing: {assumption.id}"))

    graph = {item.id: item.derivation_id for item in case.evidence if item.derivation_id}
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        target = graph.get(node)
        cyclic = bool(target and target in graph and visit(target))
        visiting.remove(node)
        visited.add(node)
        return cyclic

    if any(visit(node) for node in graph):
        issues.append(ValidationIssue("reference_cycle", "evidence derivation graph contains a cycle"))
    return ValidationReport(not any(issue.blocking for issue in issues), tuple(issues))

