"""Semantic component IR validation.

The IR stores PMO meaning. It intentionally excludes coordinates, PowerPoint
shape types, and drawing commands.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any, Iterable, Mapping


class ComponentValidationError(ValueError):
    def __init__(self, reason_codes: Iterable[str]):
        self.reason_codes = sorted(set(reason_codes))
        super().__init__(", ".join(self.reason_codes))


SUPPORTED_PHASE1_TYPES = {"annotated_doughnut", "roadmap", "gantt"}
SUPPORTED_PHASE2_P0_TYPES = {"kpi_status", "milestone", "risk_heat_map", "raci"}
SUPPORTED_COMPONENT_TYPES = SUPPORTED_PHASE1_TYPES | SUPPORTED_PHASE2_P0_TYPES
STATUS_VALUES = {"healthy", "watch", "risk", "neutral"}
KPI_DIRECTIONS = {"higher_is_better", "lower_is_better"}
RACI_CODES = {"R", "A", "C", "I"}


def _parse_date(value: Any, reason_codes: list[str]) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        reason_codes.append("date_invalid")
        return None


def _validate_interval(
    interval: Mapping[str, Any],
    timeline_start: date,
    timeline_end: date,
    reason_codes: list[str],
) -> tuple[date | None, date | None]:
    start = _parse_date(interval.get("start"), reason_codes)
    end = _parse_date(interval.get("end"), reason_codes)
    if start and end:
        if start > end:
            reason_codes.append("date_order_invalid")
        if start < timeline_start or end > timeline_end:
            reason_codes.append("interval_outside_timeline")
    return start, end


def _interval_covered(
    actual: tuple[date | None, date | None],
    planned: list[tuple[date | None, date | None]],
) -> bool:
    actual_start, actual_end = actual
    if not actual_start or not actual_end:
        return False
    return any(
        planned_start is not None
        and planned_end is not None
        and planned_start <= actual_start
        and actual_end <= planned_end
        for planned_start, planned_end in planned
    )


def validate_component_ir(ir: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a detached semantic IR mapping."""

    reasons: list[str] = []
    if not isinstance(ir, Mapping):
        raise ComponentValidationError(["ir_not_object"])
    component_type = ir.get("type")
    if component_type not in SUPPORTED_COMPONENT_TYPES:
        raise ComponentValidationError(["component_type_unsupported"])
    if not str(ir.get("title", "")).strip():
        reasons.append("title_missing")

    if component_type == "annotated_doughnut":
        categories = ir.get("categories")
        if not isinstance(categories, list) or len(categories) < 2:
            reasons.append("category_count_invalid")
        else:
            total = 0.0
            amount_total = 0.0
            amounts_present = 0
            for category in categories:
                if not isinstance(category, Mapping):
                    reasons.append("category_invalid")
                    continue
                if not str(category.get("label", "")).strip():
                    reasons.append("category_label_missing")
                try:
                    value = float(category.get("value"))
                except (TypeError, ValueError):
                    reasons.append("category_value_invalid")
                    continue
                if value <= 0:
                    reasons.append("category_value_non_positive")
                total += value
                if not str(category.get("color_role", "")).strip():
                    reasons.append("category_color_role_missing")
                if category.get("label_mode", "callout") not in {"callout", "legend"}:
                    reasons.append("category_label_mode_invalid")
                if "amount" in category:
                    amounts_present += 1
                    try:
                        amount = float(category.get("amount"))
                    except (TypeError, ValueError):
                        reasons.append("category_amount_invalid")
                    else:
                        if amount <= 0:
                            reasons.append("category_amount_non_positive")
                        amount_total += amount
                if "status_role" in category and category.get("status_role") not in STATUS_VALUES:
                    reasons.append("category_status_invalid")
                if ("status_role" in category) != bool(str(category.get("status_text", "")).strip()):
                    reasons.append("category_status_incomplete")
            tolerance = float(ir.get("sum_tolerance", 0.5))
            if abs(total - 100.0) > tolerance:
                reasons.append("category_sum_invalid")
            if amounts_present not in {0, len(categories)}:
                reasons.append("category_amounts_incomplete")
            if amounts_present:
                try:
                    budget_total = float(ir.get("budget_total"))
                except (TypeError, ValueError):
                    reasons.append("budget_total_invalid")
                else:
                    if budget_total <= 0:
                        reasons.append("budget_total_non_positive")
                    amount_tolerance = float(ir.get("amount_tolerance", 0.02))
                    if abs(amount_total - budget_total) > amount_tolerance:
                        reasons.append("category_amount_sum_invalid")
                    for category in categories:
                        if isinstance(category, Mapping) and "amount" in category:
                            expected = budget_total * float(category["value"]) / 100.0
                            if abs(float(category["amount"]) - expected) > amount_tolerance:
                                reasons.append("category_amount_share_mismatch")
            try:
                max_leaders = int(ir.get("max_leaders", len(categories)))
            except (TypeError, ValueError):
                reasons.append("max_leaders_invalid")
            else:
                if max_leaders < 0 or max_leaders > len(categories):
                    reasons.append("max_leaders_invalid")
            readouts = ir.get("readouts", [])
            if not isinstance(readouts, list) or len(readouts) > 3:
                reasons.append("readout_count_invalid")
            else:
                for readout in readouts:
                    if not isinstance(readout, Mapping):
                        reasons.append("readout_invalid")
                        continue
                    if not str(readout.get("headline", "")).strip() or not str(readout.get("detail", "")).strip():
                        reasons.append("readout_text_missing")
                    if readout.get("status_role", "neutral") not in STATUS_VALUES:
                        reasons.append("readout_status_invalid")

    elif component_type == "roadmap":
        phases = ir.get("phases")
        if not isinstance(phases, list) or len(phases) < 2:
            reasons.append("phase_count_invalid")
        else:
            identifiers: set[str] = set()
            for phase in phases:
                if not isinstance(phase, Mapping):
                    reasons.append("phase_invalid")
                    continue
                identifier = str(phase.get("id", "")).strip()
                if not identifier:
                    reasons.append("phase_id_missing")
                elif identifier in identifiers:
                    reasons.append("phase_id_duplicate")
                identifiers.add(identifier)
                for field in ("name", "period", "objective", "exit_condition", "gate"):
                    if not str(phase.get(field, "")).strip():
                        reasons.append("phase_field_missing")
                outputs = phase.get("outputs")
                if not isinstance(outputs, list) or not outputs or not all(str(item).strip() for item in outputs):
                    reasons.append("phase_outputs_invalid")

    elif component_type == "gantt":
        timeline_start = _parse_date(ir.get("start_date"), reasons)
        timeline_end = _parse_date(ir.get("end_date"), reasons)
        if timeline_start and timeline_end and timeline_start >= timeline_end:
            reasons.append("date_order_invalid")
        tasks = ir.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            reasons.append("task_count_invalid")
        elif timeline_start and timeline_end and timeline_start < timeline_end:
            task_ids: set[str] = set()
            for task in tasks:
                if not isinstance(task, Mapping):
                    reasons.append("task_invalid")
                    continue
                task_id = str(task.get("id", "")).strip()
                if not task_id:
                    reasons.append("task_id_missing")
                elif task_id in task_ids:
                    reasons.append("task_id_duplicate")
                task_ids.add(task_id)
                for field in ("label", "owner", "health"):
                    if not str(task.get(field, "")).strip():
                        reasons.append("task_field_missing")
                planned_raw = task.get("planned_intervals")
                if not isinstance(planned_raw, list) or not planned_raw:
                    reasons.append("planned_interval_missing")
                    planned_raw = []
                if len(planned_raw) > 1 and not task.get("allow_disjoint", False):
                    reasons.append("disjoint_interval_undeclared")
                planned = [
                    _validate_interval(interval, timeline_start, timeline_end, reasons)
                    for interval in planned_raw
                    if isinstance(interval, Mapping)
                ]
                actual_raw = task.get("actual_intervals", [])
                if not isinstance(actual_raw, list):
                    reasons.append("actual_intervals_invalid")
                    actual_raw = []
                for interval in actual_raw:
                    if not isinstance(interval, Mapping):
                        reasons.append("actual_interval_invalid")
                        continue
                    actual = _validate_interval(interval, timeline_start, timeline_end, reasons)
                    if not _interval_covered(actual, planned) and not task.get("exception_state"):
                        reasons.append("actual_exceeds_baseline")
                for milestone in task.get("milestones", []):
                    milestone_date = _parse_date(milestone.get("date"), reasons) if isinstance(milestone, Mapping) else None
                    if milestone_date and not timeline_start <= milestone_date <= timeline_end:
                        reasons.append("milestone_outside_timeline")
        reference = ir.get("reference_date")
        if reference and timeline_start and timeline_end and timeline_start < timeline_end:
            reference_date = _parse_date(reference, reasons)
            if reference_date and not timeline_start <= reference_date <= timeline_end:
                reasons.append("reference_outside_timeline")

    elif component_type == "kpi_status":
        metrics = ir.get("metrics")
        if not isinstance(metrics, list) or len(metrics) < 3:
            reasons.append("metric_count_invalid")
        if isinstance(metrics, list):
            metric_ids: set[str] = set()
            for metric in metrics:
                if not isinstance(metric, Mapping):
                    reasons.append("metric_invalid")
                    continue
                metric_id = str(metric.get("id", "")).strip()
                if not metric_id:
                    reasons.append("metric_id_missing")
                elif metric_id in metric_ids:
                    reasons.append("metric_id_duplicate")
                metric_ids.add(metric_id)
                for field in ("label", "unit", "period", "note"):
                    if not str(metric.get(field, "")).strip():
                        reasons.append(f"metric_{field}_missing")
                if metric.get("direction") not in KPI_DIRECTIONS:
                    reasons.append("metric_direction_invalid")
                if metric.get("status") not in STATUS_VALUES:
                    reasons.append("status_semantics_invalid")
                numeric: dict[str, float] = {}
                for field in ("value", "target"):
                    try:
                        numeric[field] = float(metric.get(field))
                    except (TypeError, ValueError):
                        reasons.append(f"metric_{field}_invalid")
                if len(numeric) != 2:
                    reasons.append("metric_target_value_not_comparable")
                trend_values = metric.get("trend_values")
                if trend_values is not None:
                    if not isinstance(trend_values, list) or len(trend_values) < 2:
                        reasons.append("metric_trend_invalid")
                    else:
                        for value in trend_values:
                            try:
                                float(value)
                            except (TypeError, ValueError):
                                reasons.append("metric_trend_invalid")
                                break

    elif component_type == "milestone":
        timeline_start = _parse_date(ir.get("start_date"), reasons)
        timeline_end = _parse_date(ir.get("end_date"), reasons)
        if timeline_start and timeline_end and timeline_start >= timeline_end:
            reasons.append("date_order_invalid")
        milestones = ir.get("milestones")
        if not isinstance(milestones, list) or not milestones:
            reasons.append("milestone_count_invalid")
        elif timeline_start and timeline_end and timeline_start < timeline_end:
            milestone_ids: set[str] = set()
            for milestone in milestones:
                if not isinstance(milestone, Mapping):
                    reasons.append("milestone_invalid")
                    continue
                milestone_id = str(milestone.get("id", "")).strip()
                if not milestone_id:
                    reasons.append("milestone_id_missing")
                elif milestone_id in milestone_ids:
                    reasons.append("milestone_id_duplicate")
                milestone_ids.add(milestone_id)
                if not str(milestone.get("label", "")).strip():
                    reasons.append("milestone_label_missing")
                if not str(milestone.get("owner", "")).strip():
                    reasons.append("milestone_owner_missing")
                if not str(milestone.get("evidence", "")).strip():
                    reasons.append("milestone_evidence_missing")
                if milestone.get("status") not in STATUS_VALUES:
                    reasons.append("status_semantics_invalid")
                milestone_date = _parse_date(milestone.get("date"), reasons)
                if milestone_date and not timeline_start <= milestone_date <= timeline_end:
                    reasons.append("milestone_outside_timeline")

    elif component_type == "risk_heat_map":
        risks = ir.get("risks")
        if not isinstance(risks, list) or not risks:
            reasons.append("risk_count_invalid")
        else:
            risk_ids: set[str] = set()
            for risk in risks:
                if not isinstance(risk, Mapping):
                    reasons.append("risk_invalid")
                    continue
                risk_id = str(risk.get("id", "")).strip()
                if not risk_id:
                    reasons.append("risk_id_missing")
                elif risk_id in risk_ids:
                    reasons.append("risk_id_duplicate")
                risk_ids.add(risk_id)
                for field in ("label", "owner", "mitigation"):
                    if not str(risk.get(field, "")).strip():
                        reasons.append(f"risk_{field}_missing")
                for field in ("likelihood", "impact"):
                    value = risk.get(field)
                    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
                        reasons.append("risk_scale_invalid")
                if risk.get("status") not in STATUS_VALUES:
                    reasons.append("status_semantics_invalid")

    elif component_type == "raci":
        roles = ir.get("roles")
        activities = ir.get("activities")
        assignments = ir.get("assignments")
        if not isinstance(roles, list) or not roles or not all(str(role).strip() for role in roles):
            reasons.append("raci_roles_invalid")
            roles = []
        elif len(set(roles)) != len(roles):
            reasons.append("raci_role_duplicate")
        if not isinstance(activities, list) or not activities or not all(str(item).strip() for item in activities):
            reasons.append("raci_activities_invalid")
            activities = []
        elif len(set(activities)) != len(activities):
            reasons.append("raci_activity_duplicate")
        if not isinstance(assignments, list):
            reasons.append("raci_assignments_invalid")
            assignments = []
        matrix: dict[str, list[str]] = {str(activity): [] for activity in activities}
        seen_pairs: set[tuple[str, str]] = set()
        for assignment in assignments:
            if not isinstance(assignment, Mapping):
                reasons.append("raci_assignment_invalid")
                continue
            activity = str(assignment.get("activity", ""))
            role = str(assignment.get("role", ""))
            code = str(assignment.get("code", ""))
            if activity not in matrix:
                reasons.append("raci_activity_reference_invalid")
            if role not in roles:
                reasons.append("raci_role_reference_invalid")
            if code not in RACI_CODES:
                reasons.append("raci_code_invalid")
            pair = (activity, role)
            if pair in seen_pairs:
                reasons.append("raci_assignment_duplicate")
            seen_pairs.add(pair)
            if activity in matrix and code in RACI_CODES:
                matrix[activity].append(code)
        for codes in matrix.values():
            if codes.count("A") != 1:
                reasons.append("raci_accountable_count_invalid")
            if "R" not in codes:
                reasons.append("raci_responsible_missing")

    if reasons:
        raise ComponentValidationError(reasons)
    return deepcopy(dict(ir))
