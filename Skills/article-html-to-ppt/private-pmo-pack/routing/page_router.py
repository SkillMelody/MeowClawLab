from __future__ import annotations

from typing import Any


def route_page(features: dict[str, Any]) -> dict[str, Any]:
    intent = str(features.get("intent") or "").strip()
    metrics = {str(item).lower() for item in features.get("metrics", [])}
    project_count = int(features.get("project_count") or 1)
    observations = int(features.get("observations") or 0)

    if intent == "show_trend" and observations < 2:
        return _route(
            "claim_evidence",
            "native_text_callout",
            ["evidence_note"],
            ["insufficient_observations"],
        )

    core_routes = {
        "explain_program_phases": ("implementation_roadmap", "phase_roadmap", ["gate_markers", "milestone_axis"], "phase_progression"),
        "show_key_milestones": ("milestone_timeline", "milestone_axis", ["evidence_labels", "status_markers"], "milestone_tracking"),
        "manage_raid": ("raid_register", "native_raid_table", ["severity_chips", "close_plan"], "risk_issue_dependency_control"),
        "show_workstream_health": ("workstream_board", "workstream_status_lanes", ["owner_labels", "delivery_bars"], "workstream_accountability"),
        "clarify_accountability": ("raci_matrix", "native_raci_table", ["accountability_gap_callout"], "responsibility_lookup"),
        "prioritize_risks": ("risk_heat_map", "risk_matrix_5x5", ["top_risk_table", "response_callouts"], "risk_prioritization"),
        "compare_decision_options": ("decision_page", "weighted_decision_matrix", ["recommendation_callout", "stop_condition"], "decision_tradeoff"),
        "track_actions": ("action_tracker", "native_action_table", ["priority_grouping", "dependency_labels"], "action_closure"),
    }
    if intent == "show_trend" and observations >= 2:
        return _route("kpi_dashboard", "kpi_trend_chart", ["target_line", "variance_callout"], ["trend_evidence"])
    if intent in core_routes:
        family, primary, supporting, reason = core_routes[intent]
        return _route(family, primary, supporting, [reason])

    if intent == "compare_project_portfolio" or project_count > 1 and {"health", "priority"} <= metrics:
        return _route(
            "portfolio_dashboard",
            "portfolio_health_matrix",
            ["project_comparison_table", "portfolio_mix_chart", "priority_callout"],
            ["cross_project_comparison"],
        )

    if intent == "monitor_pmo_control_tower" or {"compliance", "stakeholders", "milestones"} <= metrics:
        return _route(
            "pmo_control_tower",
            "pmo_health_overview",
            ["milestone_trend", "risk_compliance_panel", "budget_variance", "decision_queue"],
            ["enterprise_pmo_monitoring"],
        )

    if intent == "explain_resource_capacity" or len({"fte", "utilization", "hours"} & metrics) >= 2:
        return _route(
            "time_resource_dashboard",
            "resource_allocation_bars",
            ["capacity_heatmap", "task_timeline", "budget_consumption"],
            ["resource_capacity_question"],
        )

    if intent == "weekly_executive_status" or {"summary", "accomplishments", "next_steps"} <= metrics:
        return _route(
            "executive_status_one_pager",
            "status_narrative_grid",
            ["project_health_table", "milestone_timeline", "top_risks"],
            ["weekly_status_material"],
        )

    if intent == "summarize_single_project_health" or {"schedule", "budget", "risk"} <= metrics:
        return _route(
            "single_project_health_dashboard",
            "executive_dashboard",
            ["status_kpis", "risk_issue_panel", "delivery_timeline"],
            ["single_project_health"],
        )

    return _route(
        "claim_evidence",
        "native_text_callout",
        ["evidence_note"],
        ["no_specialized_page_match"],
    )


def _route(
    page_family: str,
    primary_visual: str,
    supporting_visuals: list[str],
    reason_codes: list[str],
) -> dict[str, Any]:
    return {
        "page_family": page_family,
        "primary_visual": primary_visual,
        "supporting_visuals": supporting_visuals,
        "reason_codes": reason_codes,
    }
