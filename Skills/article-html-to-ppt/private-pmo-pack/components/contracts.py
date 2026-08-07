"""Implementation and interface contracts for PMO component families.

Phase 2 P0 entries are implemented; later Phase 2 and Phase 3 entries remain
planning contracts only.
"""

from __future__ import annotations

from typing import Any


def _phase2(
    component: str,
    priority: str,
    fields: list[str],
    qa_gates: list[str],
    dependencies: list[str],
) -> dict[str, Any]:
    implemented = priority == "P0"
    return {
        "component": component,
        "phase": 2,
        "status": "implemented" if implemented else "planned",
        "priority": priority,
        "renderer_implemented": implemented,
        "layout_solver_implemented": implemented,
        "ir_required_fields": fields,
        "qa_gates": qa_gates,
        "dependencies": dependencies,
    }


PHASE2_CONTRACTS: dict[str, dict[str, Any]] = {
    "kpi_status": _phase2(
        "kpi_status",
        "P0",
        ["id", "label", "value", "unit", "target", "direction", "status", "period", "note"],
        ["target_direction_valid", "status_semantics_complete", "metric_text_fits"],
        ["token_resolver", "text_overflow_qa"],
    ),
    "milestone": _phase2(
        "milestone",
        "P0",
        ["id", "label", "date", "owner", "evidence", "status"],
        ["date_in_range", "evidence_present", "labels_do_not_collide"],
        ["date_mapping", "status_semantics"],
    ),
    "risk_heat_map": _phase2(
        "risk_heat_map",
        "P0",
        ["id", "label", "likelihood", "impact", "owner", "status", "mitigation"],
        ["scale_bounds_valid", "risk_id_unique", "cell_labels_fit", "legend_complete"],
        ["token_resolver", "text_overflow_qa"],
    ),
    "raci": _phase2(
        "raci",
        "P0",
        ["activities", "roles", "assignments"],
        ["one_accountable_per_activity", "assignment_codes_valid", "table_density_within_limit"],
        ["table_layout_contract", "text_overflow_qa"],
    ),
    "raid": _phase2(
        "raid",
        "P1",
        ["item_id", "type", "description", "owner", "due_date", "mitigation", "status"],
        ["taxonomy_valid", "owner_present", "date_valid", "status_semantics_complete"],
        ["status_semantics", "table_layout_contract"],
    ),
    "action_tracker": _phase2(
        "action_tracker",
        "P1",
        ["action_id", "action", "owner", "due_date", "status"],
        ["owner_present", "date_valid", "status_semantics_complete", "row_overflow_checked"],
        ["status_semantics", "table_layout_contract"],
    ),
    "decision_matrix": _phase2(
        "decision_matrix",
        "P1",
        ["options", "criteria", "weights", "scores", "recommendation"],
        ["weights_sum_valid", "score_range_valid", "recommendation_traceable", "legend_complete"],
        ["table_layout_contract", "numeric_format_contract"],
    ),
    "swimlane_dependency": _phase2(
        "swimlane_dependency",
        "P2",
        ["lanes", "activities", "dependencies"],
        ["lane_ownership_complete", "dependency_endpoints_valid", "connector_crossing_budget", "text_bounds"],
        ["connector_routing", "reserved_channel_layout"],
    ),
}


def _phase3(
    component: str,
    dependencies: list[str],
    uncertainties: list[str],
) -> dict[str, Any]:
    return {
        "component": component,
        "phase": 3,
        "status": "planned",
        "renderer_implemented": False,
        "layout_solver_implemented": False,
        "dependencies": dependencies,
        "uncertainties": uncertainties,
    }


PHASE3_CONTRACTS: dict[str, dict[str, Any]] = {
    "budget_vs_actual": _phase3(
        "budget_vs_actual",
        ["numeric_format_contract", "native_chart_theme", "variance_semantics"],
        ["currency_and_locale_policy", "forecast_encoding"],
    ),
    "waterfall": _phase3(
        "waterfall",
        ["numeric_format_contract", "native_chart_workbook_qa"],
        ["negative_bridge_label_routing", "subtotal_authoring_parity"],
    ),
    "resource_capacity": _phase3(
        "resource_capacity",
        ["date_mapping", "capacity_unit_contract", "heat_scale_tokens"],
        ["mixed_FTE_and_hours", "overbooking_policy"],
    ),
    "portfolio_bubble": _phase3(
        "portfolio_bubble",
        ["axis_scale_contract", "collision_aware_labels", "native_scatter_chart"],
        ["bubble_size_normalization", "outlier_label_fallback"],
    ),
    "release_train": _phase3(
        "release_train",
        ["roadmap_boundaries", "dependency_channels", "milestone_contract"],
        ["cross_team_dependency_density", "calendar_exception_policy"],
    ),
    "trend_burndown": _phase3(
        "trend_burndown",
        ["native_line_chart", "date_mapping", "forecast_semantics"],
        ["missing_period_interpolation", "target_rebaseline_disclosure"],
    ),
    "complex_governance": _phase3(
        "complex_governance",
        ["graph_ir", "connector_routing", "hierarchy_layout", "page_split_policy"],
        ["arbitrary_graph_complexity", "native_connector_endpoint_binding"],
    ),
    "liquid_glass_skin": _phase3(
        "liquid_glass_skin",
        ["skin_independent_geometry", "solid_fallback_tokens", "renderer_parity_tests"],
        ["LibreOffice_transparency_parity", "print_contrast", "shadow_rendering_parity"],
    ),
}


def get_component_contract(component: str) -> dict[str, Any]:
    if component in PHASE2_CONTRACTS:
        return dict(PHASE2_CONTRACTS[component])
    if component in PHASE3_CONTRACTS:
        return dict(PHASE3_CONTRACTS[component])
    raise KeyError(component)
