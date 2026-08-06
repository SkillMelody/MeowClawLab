from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from .model import (
    AnalysisMode,
    AnalysisResult,
    DecisionCase,
    ExplanationTrace,
    FrameworkSelection,
    ReadinessReport,
    Recommendation,
    RecommendationStatus,
    RouteAction,
    SensitivityResult,
    SufficiencyReport,
    ValidationReport,
)
from .recommendation import prescriptive_readiness
from .registry import FrameworkRegistry, default_registry
from .router import route_decision
from .serialization import input_snapshot_sha256
from .validation import validate_decision_case


@dataclass(frozen=True)
class FrameworkRecommendation:
    framework_id: str
    recommendation: Recommendation
    readiness: ReadinessReport


@dataclass(frozen=True)
class DecisionPackage:
    route: FrameworkSelection
    validations: Tuple[ValidationReport, ...]
    analysis_results: Tuple[AnalysisResult, ...]
    sensitivity: Tuple[Tuple[SensitivityResult, ...], ...]
    framework_recommendations: Tuple[FrameworkRecommendation, ...]
    recommendation: Recommendation
    explanation_trace: Tuple[ExplanationTrace, ...]
    input_hash: str
    audit: Mapping[str, Any]


def _no_recommendation(case: DecisionCase, input_hash: str, statement: str) -> Recommendation:
    return Recommendation(
        id=f"pipeline-no-recommendation-{case.id}-{input_hash[:12]}",
        status=RecommendationStatus.NO_RECOMMENDATION,
        statement=statement,
        owner=case.question.owner,
        model_version="decision-pipeline-1.0.0",
        analysis_run_id=f"decision-pipeline-{input_hash[:16]}",
    )


def enforce_prescriptive_readiness(
    case: DecisionCase,
    result: AnalysisResult,
    sensitivity: Tuple[SensitivityResult, ...],
    recommendation: Recommendation,
) -> Tuple[Recommendation, ReadinessReport]:
    readiness = prescriptive_readiness(case, result, sensitivity, recommendation)
    protected = recommendation.status in (
        RecommendationStatus.NO_RECOMMENDATION,
        RecommendationStatus.INFEASIBLE,
    )
    if case.question.requested_analysis_mode is not AnalysisMode.PRESCRIPTIVE or protected or readiness.ready:
        return recommendation, readiness
    blocked = replace(
        recommendation,
        status=RecommendationStatus.NO_RECOMMENDATION,
        statement="No recommendation: shared prescriptive readiness failed (" + ", ".join(readiness.reason_codes) + ").",
        selected_option_ids=(),
    )
    return blocked, readiness


def _framework_route(
    case: DecisionCase,
    route: FrameworkSelection,
    registry: FrameworkRegistry,
) -> Tuple[FrameworkSelection, Tuple[ValidationReport, ...]]:
    if route.route_action is not RouteAction.ROUTE:
        return route, ()
    missing = []
    reason_codes = []
    reports = []
    for framework_id in route.candidate_framework_ids:
        framework = registry.framework(framework_id)
        if framework is None:
            missing.append(f"framework.{framework_id}")
            reason_codes.append("framework_not_registered")
            continue
        sufficiency = framework.assess_sufficiency(case)
        missing.extend(sufficiency.missing_fields)
        reason_codes.extend(sufficiency.reason_codes)
        report = framework.validate_evidence(case)
        reports.append(report)
        reason_codes.extend(report.reason_codes)
    missing_fields = tuple(dict.fromkeys(missing))
    codes = tuple(dict.fromkeys(reason_codes))
    if any(not report.valid for report in reports):
        sufficiency = SufficiencyReport(False, missing_fields, codes)
        return FrameworkSelection(
            route.candidate_framework_ids, (), RouteAction.BLOCK, sufficiency,
            codes, missing_fields,
        ), tuple(reports)
    if missing_fields or codes:
        action = RouteAction.ASK if case.question.requested_analysis_mode is AnalysisMode.PRESCRIPTIVE else RouteAction.DESCRIBE_ONLY
        sufficiency = SufficiencyReport(False, missing_fields, codes)
        return FrameworkSelection(
            route.candidate_framework_ids, (), action, sufficiency, codes,
            missing_fields,
        ), tuple(reports)
    return route, tuple(reports)


def analyze_decision(
    case: DecisionCase,
    registry: Optional[FrameworkRegistry] = None,
) -> DecisionPackage:
    registry = registry or default_registry()
    input_hash = input_snapshot_sha256(case)
    shared_validation = validate_decision_case(case)
    route = route_decision(case, registry)
    route, framework_validations = _framework_route(case, route, registry)
    validations = (shared_validation,) + framework_validations

    results = []
    sensitivities = []
    recommendations = []
    explanations = []
    if route.route_action is RouteAction.ROUTE:
        for framework_id in route.selected_framework_ids:
            framework = registry.framework(framework_id)
            if framework is None:
                continue
            result = replace(framework.analyze(case), input_snapshot_hash=input_hash)
            sensitivity = tuple(framework.run_sensitivity(case, result))
            recommendation = framework.build_recommendation(case, result, sensitivity)
            recommendation, readiness = enforce_prescriptive_readiness(
                case, result, sensitivity, recommendation,
            )
            results.append(result)
            sensitivities.append(sensitivity)
            recommendations.append(FrameworkRecommendation(framework_id, recommendation, readiness))
            explanations.append(framework.explain(result))

    if len(recommendations) == 1:
        recommendation = recommendations[0].recommendation
    elif len(recommendations) > 1:
        recommendation = _no_recommendation(
            case, input_hash,
            "No aggregate recommendation: review the ordered framework recommendations without combining them into an opaque score.",
        )
    else:
        recommendation = _no_recommendation(
            case, input_hash,
            f"No recommendation: decision route action is {route.route_action.value}.",
        )

    audit = MappingProxyType({
        "input_hash": input_hash,
        "analysis_run_id": f"decision-pipeline-{input_hash[:16]}",
        "framework_order": tuple(item.framework_id for item in results),
        "route_action": route.route_action.value,
    })
    return DecisionPackage(
        route=route,
        validations=validations,
        analysis_results=tuple(results),
        sensitivity=tuple(sensitivities),
        framework_recommendations=tuple(recommendations),
        recommendation=recommendation,
        explanation_trace=tuple(explanations),
        input_hash=input_hash,
        audit=audit,
    )
