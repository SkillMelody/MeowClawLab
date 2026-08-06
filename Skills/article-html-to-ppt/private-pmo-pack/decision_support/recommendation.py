from datetime import date
from typing import Optional, Tuple

from .model import (
    AnalysisResult,
    ConfidenceLevel,
    Counterargument,
    DecisionCase,
    ReadinessReport,
    Recommendation,
    RecommendationStatus,
    ReviewTrigger,
    SensitivityResult,
)


def prescriptive_readiness(
    case: DecisionCase,
    result: AnalysisResult,
    sensitivity: Tuple[SensitivityResult, ...],
    recommendation: Optional[Recommendation] = None,
) -> ReadinessReport:
    codes = []
    if not result.evidence_ids:
        codes.append("recommendation_evidence_trace_missing")
    if not result.assumption_ids:
        codes.append("recommendation_assumption_trace_missing")
    if not result.calculations:
        codes.append("recommendation_calculation_trace_missing")
    if not sensitivity:
        codes.append("sensitivity_missing")
    if recommendation is None or not recommendation.counterarguments:
        codes.append("counterargument_missing")
    if recommendation is None or not recommendation.owner:
        codes.append("recommendation_owner_missing")
    if recommendation is None or recommendation.review_date is None:
        codes.append("review_date_missing")
    if recommendation is None or not recommendation.triggers:
        codes.append("review_trigger_missing")
    if recommendation is None or not recommendation.conditions:
        codes.append("recommendation_conditions_missing")
    return ReadinessReport(not codes, tuple(codes))


def build_recommendation_trace(
    case: DecisionCase,
    result: AnalysisResult,
    sensitivity: Tuple[SensitivityResult, ...],
    *,
    status: RecommendationStatus,
    statement: str,
    counterarguments: Tuple[Counterargument, ...],
    owner: str,
    review_date: date,
    triggers: Tuple[ReviewTrigger, ...],
    conditions: Tuple[str, ...] = ("Evidence remains current",),
    selected_option_ids: Tuple[str, ...] = (),
    rejected_option_ids: Tuple[str, ...] = (),
    deferred_option_ids: Tuple[str, ...] = (),
) -> Recommendation:
    evidence_by_id = {item.id: item for item in case.evidence}
    referenced = [evidence_by_id[item_id] for item_id in result.evidence_ids if item_id in evidence_by_id]
    confidence = min((item.confidence for item in referenced), key=lambda item: (ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH).index(item), default=ConfidenceLevel.LOW)
    return Recommendation(
        id=f"recommendation-{result.id}", status=status, statement=statement,
        selected_option_ids=selected_option_ids, rejected_option_ids=rejected_option_ids,
        deferred_option_ids=deferred_option_ids, evidence_ids=result.evidence_ids,
        assumption_ids=result.assumption_ids, calculation_ids=tuple(item.id for item in result.calculations),
        counterarguments=counterarguments, sensitivity_summary=tuple(item.conclusion for item in sensitivity),
        confidence=confidence, confidence_basis="Minimum evidence quality across referenced evidence; confidence is not an outcome likelihood.",
        owner=owner, conditions=conditions, review_date=review_date, triggers=triggers,
        model_version=result.framework_version, analysis_run_id=result.id,
    )
