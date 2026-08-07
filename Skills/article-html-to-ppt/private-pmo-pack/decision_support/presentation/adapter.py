from __future__ import annotations

from typing import Any, Mapping

from decision_support.model import RouteAction
from decision_support.pipeline import DecisionPackage, FrameworkRecommendation


_TITLES = {
    "decision_brief": "The decision is bounded by declared evidence, route, and readiness",
    "benefits_dashboard": "Benefits are ahead of plan, but future economics remain the decision basis",
    "business_case_gate": "Sequential gates favor the strongest future incremental option",
    "weighted_decision_matrix": "Fixed anchors preserve comparability across portfolio options",
    "capacity_scenario_allocation": "Allocation changes are exposed by bounded capacity scenarios",
    "critical_path_gantt": "Driving dependencies, not task count, determine the finish",
    "constraint_board": "Binding and near-critical constraints define the recovery boundary",
    "risk_exposure": "Mitigation economics must be read with residual exposure and tolerance",
    "mitigation_roi": "Treatment value is conditional on calibrated probability and consequence",
    "recommendation_trace": "Recommendation, counterargument, sensitivity, and evidence boundary stay together",
    "decision_record": "Approval must preserve conditions, triggers, owner, and review date",
    "evidence_gap_diagnostic": "Evidence gaps block prescriptive output without blocking diagnosis",
}


def _metadata(package: DecisionPackage, framework_id: str | None = None) -> dict[str, str]:
    item = next((entry for entry in package.framework_recommendations if entry.framework_id == framework_id), None)
    result = next((entry for entry in package.analysis_results if entry.framework_id == framework_id), None)
    recommendation = item.recommendation if item else package.recommendation
    framework_version = result.framework_version if result else recommendation.model_version or "decision-pipeline-1.0.0"
    cutoff = package.audit.get("evidence_cutoff")
    if cutoff is None:
        cutoff = next(
            (entry.updated_at or entry.created_at for entry in package.analysis_results if entry.updated_at or entry.created_at),
            None,
        )
    return {
        "analysis_run_id": recommendation.analysis_run_id or str(package.audit.get("analysis_run_id", "not supplied")),
        "input_hash_short": package.input_hash[:12],
        "evidence_cutoff": cutoff.isoformat() if hasattr(cutoff, "isoformat") else str(cutoff or "not supplied in DecisionPackage"),
        "framework_version": f"{framework_id or 'decision_pipeline'} / {framework_version}",
        "recommendation_status": recommendation.status.value,
    }


def _page(package: DecisionPackage, page_type: str, framework_id: str | None = None, **content: Any) -> dict[str, Any]:
    return {
        "page_type": page_type,
        "title": _TITLES[page_type],
        "framework_id": framework_id,
        "metadata": _metadata(package, framework_id),
        **content,
    }


def _calculations(result: Any) -> dict[str, str]:
    return {item.id: "not supplied" if item.value is None else str(item.value) for item in result.calculations}


def _readiness(package: DecisionPackage, framework_id: str) -> FrameworkRecommendation | None:
    return next((item for item in package.framework_recommendations if item.framework_id == framework_id), None)


def _framework_pages(package: DecisionPackage, result: Any) -> list[dict[str, Any]]:
    framework_id = result.framework_id
    calculations = _calculations(result)
    extensions: Mapping[str, Any] = result.extensions
    output: list[dict[str, Any]] = []
    readiness = _readiness(package, framework_id)
    diagnostic = not readiness or not readiness.readiness.ready
    if framework_id == "value_gate":
        output.append(_page(package, "benefits_dashboard", framework_id, metrics=[
            {"label": "Benefit realization", "value": calculations.get("benefit_realization", "not supplied")},
            {"label": "Forecast gap", "value": calculations.get("forecast_gap", "not supplied")},
        ], benefit_series=dict(extensions.get("benefit_series", {})),
                            findings=[item.statement for item in result.findings], limitations=list(result.limitations)))
        option_metrics = [
            {"option": key.removeprefix("npv-"), "npv": value}
            for key, value in calculations.items()
            if key.startswith("npv-") and not key.startswith("npv-incremental-")
        ]
        output.append(_page(package, "business_case_gate", framework_id, options=option_metrics,
                            gates=list(result.diagnostics), calculations=calculations,
                            mode="diagnostic" if diagnostic else "prescriptive"))
    elif framework_id == "resource_allocation":
        scores = [{"option": key.removeprefix("weighted-score:"), "score": value}
                  for key, value in calculations.items() if key.startswith("weighted-score:")]
        output.append(_page(package, "weighted_decision_matrix", framework_id, scores=scores,
                            selected=list(extensions.get("selected_option_ids", ())),
                            method=extensions.get("method", "not supplied")))
        output.append(_page(package, "capacity_scenario_allocation", framework_id,
                            scenarios=extensions.get("scenarios", {}),
                            constraints=list(extensions.get("binding_constraints", ())),
                            option_resource_demand=extensions.get("option_resource_demand", {}),
                            option_cost=extensions.get("option_cost", {}),
                            resource_limits=extensions.get("resource_limits", {}),
                            budget_limits=extensions.get("budget_limits", {}),
                            note="Bounded scenarios; no global optimizer claim.",
                            mode="diagnostic" if diagnostic else "prescriptive"))
    elif framework_id == "schedule_analysis":
        schedule = extensions.get("schedule", {})
        output.append(_page(package, "critical_path_gantt", framework_id,
                            tasks=schedule.get("tasks", {}), critical_paths=schedule.get("critical_paths", ()),
                            driving_dependencies=schedule.get("driving_dependencies", ()),
                            dependency_edges=schedule.get("dependency_edges", ()),
                            critical_tasks=schedule.get("critical_subgraph", {}).get("task_ids", ()),
                            near_critical=schedule.get("near_critical_task_ids", ()),
                            required_finish=schedule.get("required_finish", "not supplied"),
                            project_finish=schedule.get("project_finish", "not supplied")))
        output.append(_page(package, "constraint_board", framework_id,
                            overloads=schedule.get("overload_intervals", ()),
                            near_critical=schedule.get("near_critical_task_ids", ()),
                            binding_tasks=schedule.get("critical_subgraph", {}).get("task_ids", ()),
                            tasks=schedule.get("tasks", {}),
                            dependency_edges=schedule.get("dependency_edges", ()),
                            required_finish=schedule.get("required_finish", "not supplied"),
                            scenarios=schedule.get("capacity_scenarios", ()), limitations=list(result.limitations),
                            mode="diagnostic"))
    elif framework_id == "risk_treatment":
        output.append(_page(package, "risk_exposure", framework_id, metrics=[
            {"label": "Baseline exposure", "value": calculations.get("baseline_exposure_central", "not supplied")},
            {"label": "Residual exposure", "value": calculations.get("adjusted_residual_exposure_central", "not supplied")},
            {"label": "Exposure reduction", "value": calculations.get("exposure_reduction_central", "not supplied")},
            {"label": "Tolerance gap", "value": calculations.get("tolerance_gap", "not supplied")},
        ], limitations=list(result.limitations)))
        output.append(_page(package, "mitigation_roi", framework_id, metrics=[
            {"label": "Full-life cost", "value": calculations.get("full_life_mitigation_cost", "not supplied")},
            {"label": "Net benefit", "value": calculations.get("net_benefit", "not supplied")},
            {"label": "ROI", "value": calculations.get("roi", "not supplied")},
            {"label": "Benefit / cost", "value": calculations.get("benefit_cost_ratio", "not supplied")},
        ], calculations=calculations, mode="diagnostic" if diagnostic else "prescriptive"))
    return output


def _trace_rows(package: DecisionPackage) -> list[dict[str, Any]]:
    rows = []
    for item in package.framework_recommendations:
        recommendation = item.recommendation
        rows.append({
            "framework": item.framework_id,
            "readiness": "passed" if item.readiness.ready else "diagnostic only",
            "status": recommendation.status.value,
            "recommendation": recommendation.statement if item.readiness.ready else "Prescriptive output suppressed; diagnostic result only.",
            "counterargument": recommendation.counterarguments[0].statement if recommendation.counterarguments else "not supplied",
            "sensitivity": recommendation.sensitivity_summary[0] if recommendation.sensitivity_summary else "not supplied",
            "evidence_boundary": ", ".join(item.readiness.reason_codes) or "shared readiness passed",
        })
    return rows


def build_decision_presentation_ir(package: DecisionPackage) -> tuple[dict, ...]:
    """Adapt an audited package to semantic pages without recalculating analysis."""
    brief = _page(
        package,
        "decision_brief",
        route_action=package.route.route_action.value,
        framework_order=list(package.audit.get("framework_order", ())),
        sufficiency={
            "sufficient": package.route.sufficiency_report.sufficient,
            "missing_fields": list(package.route.sufficiency_report.missing_fields),
            "reason_codes": list(package.route.reason_codes),
        },
        recommendation_status=package.recommendation.status.value,
    )
    if package.route.route_action is not RouteAction.ROUTE or not package.analysis_results:
        diagnostic = _page(
            package,
            "evidence_gap_diagnostic",
            missing_fields=list(package.route.requested_evidence_fields),
            reason_codes=list(package.route.reason_codes),
            validation_issues=[issue.message for report in package.validations for issue in report.issues],
        )
        return (brief, diagnostic)

    pages = [brief]
    for result in package.analysis_results:
        pages.extend(_framework_pages(package, result))

    ready_items = [item for item in package.framework_recommendations if item.readiness.ready]
    if ready_items:
        pages.append(_page(package, "recommendation_trace", rows=_trace_rows(package),
                           aggregate_statement=package.recommendation.statement,
                           aggregate_status=package.recommendation.status.value,
                           note="Framework outputs remain separate; no opaque total score is computed."))
        pages.append(_page(package, "decision_record", records=[{
            "framework": item.framework_id,
            "owner": item.recommendation.owner or "not supplied",
            "review_date": item.recommendation.review_date.isoformat() if item.recommendation.review_date else "not supplied",
            "conditions": list(item.recommendation.conditions),
            "triggers": [{"condition": trigger.condition, "action": trigger.action} for trigger in item.recommendation.triggers],
        } for item in package.framework_recommendations], decision_status="review_ready"))
    else:
        pages.append(_page(package, "evidence_gap_diagnostic",
                           missing_fields=[], reason_codes=[code for item in package.framework_recommendations for code in item.readiness.reason_codes],
                           validation_issues=["All framework outputs are descriptive or diagnostic; recommendation page suppressed."]))
    return tuple(pages)
