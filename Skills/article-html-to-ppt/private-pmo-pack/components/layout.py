"""Deterministic geometry for native PMO components."""

from __future__ import annotations

import math
from datetime import date
from typing import Any, Mapping

from components.ir import validate_component_ir


def angle_anchor(center_x: float, center_y: float, radius: float, angle_radians: float) -> dict[str, float]:
    return {
        "x": center_x + radius * math.cos(angle_radians),
        "y": center_y + radius * math.sin(angle_radians),
    }


def angle_in_interval(angle: float, start: float, end: float, *, tolerance: float = 1e-9) -> bool:
    full_turn = 2 * math.pi
    sweep = end - start
    if sweep < -tolerance or sweep > full_turn + tolerance:
        return False
    relative = (angle - start) % full_turn
    return relative <= sweep + tolerance or abs(relative - full_turn) <= tolerance


def date_to_position(value: str, start: str, end: str) -> float:
    value_date = date.fromisoformat(value)
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if start_date >= end_date:
        raise ValueError("date range must increase")
    return (value_date - start_date).days / (end_date - start_date).days


def _line_segments(leader: Mapping[str, Any]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    points = leader["points"]
    return [
        ((points[index]["x"], points[index]["y"]), (points[index + 1]["x"], points[index + 1]["y"]))
        for index in range(len(points) - 1)
    ]


def _orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> int:
    value = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
    if abs(value) < 1e-9:
        return 0
    return 1 if value > 0 else 2


def _segments_cross(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    a, b = first
    c, d = second
    return _orientation(a, b, c) != _orientation(a, b, d) and _orientation(c, d, a) != _orientation(c, d, b)


def leaders_have_no_crossings(leaders: list[Mapping[str, Any]]) -> bool:
    for first_index, first in enumerate(leaders):
        for second in leaders[first_index + 1 :]:
            for first_segment in _line_segments(first):
                for second_segment in _line_segments(second):
                    if _segments_cross(first_segment, second_segment):
                        return False
    return True


def _resolve_lane(items: list[dict[str, Any]], top: float, bottom: float, gap: float) -> list[dict[str, Any]]:
    ordered = sorted(items, key=lambda item: item["anchor"]["y"])
    elbow_offset = 0.22 if not ordered or max(item["anchor"]["y"] for item in ordered) + 0.22 <= bottom else -0.22
    next_y = top
    for item in ordered:
        item["label_y"] = max(item["anchor"]["y"] + elbow_offset, next_y)
        next_y = item["label_y"] + gap
    if ordered and ordered[-1]["label_y"] > bottom:
        shift = ordered[-1]["label_y"] - bottom
        for item in reversed(ordered):
            item["label_y"] -= shift
            shift = max(0.0, top - item["label_y"])
    return ordered


def layout_doughnut(ir: Mapping[str, Any], frame: Mapping[str, float], tokens: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    categories = validated["categories"]
    center_x = frame["x"] + frame["w"] * 0.43
    center_y = frame["y"] + frame["h"] * 0.53
    radius = min(frame["w"] * 0.19, frame["h"] * 0.34)
    total = sum(float(category["value"]) for category in categories)
    segments: list[dict[str, Any]] = []
    cursor = -math.pi / 2
    for index, category in enumerate(categories):
        sweep = 2 * math.pi * float(category["value"]) / total
        mid = cursor + sweep / 2
        anchor = angle_anchor(center_x, center_y, radius, mid)
        segments.append(
            {
                "index": index,
                "label": category["label"],
                "value": float(category["value"]),
                "color_role": category["color_role"],
                "start_angle": cursor,
                "end_angle": cursor + sweep,
                "mid_angle": mid,
                "endpoint_angle": mid,
                "anchor": anchor,
                "side": "right" if math.cos(mid) >= 0 else "left",
            }
        )
        cursor += sweep

    explicit_modes = any("label_mode" in category for category in categories)
    max_leaders = int(validated.get("max_leaders", len(categories)))
    callout_indexes = {
        index
        for index, category in enumerate(categories)
        if (
            category.get("label_mode", "callout") == "callout"
            if explicit_modes
            else index < max_leaders
        )
    }
    if len(callout_indexes) > max_leaders:
        callout_indexes = set(sorted(callout_indexes)[:max_leaders])
    callout_segments = [segment for segment in segments if segment["index"] in callout_indexes]
    legend_fallback = [
        {
            "index": segment["index"],
            "label": segment["label"],
            "value": segment["value"],
            "color_role": segment["color_role"],
        }
        for segment in segments
        if segment["index"] not in callout_indexes
    ]

    min_gap = float(tokens["density"]["doughnut"]["min_label_gap_in"])
    capacity = max(1, int((frame["h"] - 0.55) // min_gap))
    left = [dict(segment) for segment in callout_segments if segment["side"] == "left"]
    right = [dict(segment) for segment in callout_segments if segment["side"] == "right"]
    reasons: list[str] = []
    if len(left) > capacity or len(right) > capacity:
        reasons.append("label_lane_capacity_exceeded")
    if len(categories) > int(tokens["density"]["doughnut"]["max_categories"]):
        reasons.append("category_count_exceeded")
    if reasons:
        return {
            "component": "annotated_doughnut",
            "mode": "legend",
            "reason_codes": reasons,
            "chart_first_slice_angle_deg": 0,
            "chart_direction": "clockwise",
            "center": {"x": center_x, "y": center_y},
            "radius": radius,
            "segments": segments,
            "legend": [{"label": item["label"], "value": item["value"], "color_role": item["color_role"]} for item in segments],
            "legend_fallback": [],
            "leaders": [],
        }

    lane_top = frame["y"] + 0.25
    lane_bottom = frame["y"] + frame["h"] - 0.35
    left = _resolve_lane(left, lane_top, lane_bottom, min_gap)
    right = _resolve_lane(right, lane_top, lane_bottom, min_gap)
    label_width = frame["w"] * 0.25
    leaders: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    for item in left + right:
        side = item["side"]
        radial = angle_anchor(center_x, center_y, radius + 0.16, item["mid_angle"])
        elbow_x = center_x - radius - 0.35 if side == "left" else center_x + radius + 0.35
        label_x = frame["x"] + 0.05 if side == "left" else frame["x"] + frame["w"] - label_width - 0.05
        edge_x = label_x + label_width if side == "left" else label_x
        leader = {
            "label": item["label"],
            "side": side,
            "points": [
                item["anchor"],
                radial,
                {"x": elbow_x, "y": item["label_y"]},
                {"x": edge_x, "y": item["label_y"]},
            ],
        }
        leaders.append(leader)
        labels.append(
            {
                "label": item["label"],
                "value": item["value"],
                "color_role": item["color_role"],
                "x": label_x,
                "y": item["label_y"] - 0.34,
                "w": label_width,
                "h": 0.72,
                "side": side,
                "category_index": item["index"],
            }
        )
    if not leaders_have_no_crossings(leaders):
        return {
            "component": "annotated_doughnut",
            "mode": "legend",
            "reason_codes": ["leader_crossing_unresolved"],
            "chart_first_slice_angle_deg": 0,
            "chart_direction": "clockwise",
            "center": {"x": center_x, "y": center_y},
            "radius": radius,
            "segments": segments,
            "legend": [{"label": item["label"], "value": item["value"], "color_role": item["color_role"]} for item in segments],
            "legend_fallback": [],
            "leaders": [],
        }
    return {
        "component": "annotated_doughnut",
        "mode": "annotated",
        "reason_codes": [],
        "chart_first_slice_angle_deg": 0,
        "chart_direction": "clockwise",
        "center": {"x": center_x, "y": center_y},
        "radius": radius,
        "segments": segments,
        "labels": labels,
        "leaders": leaders,
        "legend_fallback": legend_fallback,
        "callout_category_count": len(callout_segments),
    }


def layout_roadmap(ir: Mapping[str, Any], frame: Mapping[str, float], tokens: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    phases = validated["phases"]
    reasons: list[str] = []
    max_phases = int(tokens["density"]["roadmap"]["max_phases"])
    max_outputs = int(tokens["density"]["roadmap"]["max_outputs_per_phase"])
    min_width = float(tokens["density"]["roadmap"]["min_phase_width_in"])
    if len(phases) > max_phases or frame["w"] / len(phases) < min_width:
        reasons.append("phase_count_exceeded")
    if any(len(phase["outputs"]) > max_outputs for phase in phases):
        reasons.append("phase_output_count_exceeded")
    mode = "split" if reasons else "single"
    phase_width = frame["w"] / len(phases)
    phase_boxes: list[dict[str, Any]] = []
    boundaries: list[float] = []
    gates: list[dict[str, Any]] = []
    for index, phase in enumerate(phases):
        x1 = frame["x"] + index * phase_width
        x2 = frame["x"] + (index + 1) * phase_width
        phase_boxes.append(
            {
                "index": index,
                "x": x1,
                "x2": x2,
                "w": phase_width,
                "chevron_y": frame["y"],
                "chevron_h": 1.05,
                "gate_y": frame["y"] + 1.25,
                "output_y": frame["y"] + 1.72,
                "output_h": max(0.8, frame["h"] - 2.48),
                "summary_y": frame["y"] + frame["h"] - 0.48,
            }
        )
        boundaries.append(x2)
        gates.append({"label": phase["gate"], "phase_id": phase["id"], "x": x2, "y": frame["y"] + 1.34})
    return {
        "component": "roadmap",
        "mode": mode,
        "reason_codes": reasons,
        "phase_boxes": phase_boxes,
        "boundaries": boundaries,
        "gates": gates,
    }


def layout_gantt(ir: Mapping[str, Any], frame: Mapping[str, float], tokens: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    tasks = validated["tasks"]
    reasons: list[str] = []
    if len(tasks) > int(tokens["density"]["gantt"]["max_rows"]):
        reasons.append("row_count_exceeded")
    row_height = max(
        float(tokens["density"]["gantt"]["min_row_height_in"]),
        (frame["h"] - 0.75) / max(len(tasks), 1),
    )

    def x_for(value: str) -> float:
        return frame["x"] + frame["w"] * date_to_position(value, validated["start_date"], validated["end_date"])

    timeline_start = date.fromisoformat(validated["start_date"])
    timeline_end = date.fromisoformat(validated["end_date"])
    time_columns: list[dict[str, Any]] = []
    column_start = timeline_start
    column_index = 0
    while column_start < timeline_end:
        column_end = min(column_start.fromordinal(column_start.toordinal() + 7), timeline_end)
        time_columns.append(
            {
                "index": column_index + 1,
                "start": column_start.isoformat(),
                "end": column_end.isoformat(),
                "x1": x_for(column_start.isoformat()),
                "x2": x_for(column_end.isoformat()),
            }
        )
        column_start = column_end
        column_index += 1

    month_spans: list[dict[str, Any]] = []
    month_start = timeline_start
    while month_start < timeline_end:
        if month_start.month == 12:
            next_month = date(month_start.year + 1, 1, 1)
        else:
            next_month = date(month_start.year, month_start.month + 1, 1)
        month_end = min(next_month, timeline_end)
        month_spans.append(
            {
                "label": month_start.strftime("%b %Y"),
                "start": month_start.isoformat(),
                "end": month_end.isoformat(),
                "x1": x_for(month_start.isoformat()),
                "x2": x_for(month_end.isoformat()),
            }
        )
        month_start = month_end

    milestone_half_width = 0.09
    timeline_left = frame["x"]
    timeline_right = frame["x"] + frame["w"]

    def milestone_x(value: str) -> float:
        return min(
            max(x_for(value), timeline_left + milestone_half_width),
            timeline_right - milestone_half_width,
        )

    rows: list[dict[str, Any]] = []
    for index, task in enumerate(tasks):
        y = frame["y"] + 0.72 + index * row_height
        planned = [{"x1": x_for(item["start"]), "x2": x_for(item["end"]), "y": y} for item in task["planned_intervals"]]
        actual = [{"x1": x_for(item["start"]), "x2": x_for(item["end"]), "y": y} for item in task.get("actual_intervals", [])]
        milestones = [
            {"x": milestone_x(item["date"]), "y": y, "label": item["label"], "date": item["date"]}
            for item in task.get("milestones", [])
        ]
        rows.append(
            {
                "task_id": task["id"],
                "label": task["label"],
                "owner": task["owner"],
                "health": task["health"],
                "y": y,
                "h": row_height,
                "planned_bars": planned,
                "actual_bars": actual,
                "milestones": milestones,
            }
        )
    reference_x = x_for(validated["reference_date"]) if validated.get("reference_date") else None
    return {
        "component": "gantt",
        "mode": "paginate" if reasons else "single",
        "reason_codes": reasons,
        "rows": rows,
        "reference_x": reference_x,
        "timeline": dict(frame),
        "time_columns": time_columns,
        "month_spans": month_spans,
        "milestone_half_width": milestone_half_width,
    }


def _chunks(items: list[Any], size: int) -> list[list[Any]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def layout_kpi_status(
    ir: Mapping[str, Any],
    frame: Mapping[str, float],
    tokens: Mapping[str, Any],
) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    metrics = validated["metrics"]
    max_per_page = int(tokens["density"]["kpi_status"]["max_per_page"])
    metric_pages = _chunks(metrics, max_per_page)
    pages: list[dict[str, Any]] = []
    for page_index, page_metrics in enumerate(metric_pages):
        columns = 2 if len(page_metrics) == 4 else 3
        rows = 1 if len(page_metrics) <= 3 else 2
        gap_x = 0.18
        gap_y = 0.20
        card_w = (frame["w"] - gap_x * (columns - 1)) / columns
        card_h = (frame["h"] - gap_y * (rows - 1)) / rows
        cards: list[dict[str, Any]] = []
        for index, metric in enumerate(page_metrics):
            column = index % columns
            row = index // columns
            x = frame["x"] + column * (card_w + gap_x)
            y = frame["y"] + row * (card_h + gap_y)
            trend_box = {
                "x": x + card_w * 0.56,
                "y": y + card_h * 0.50,
                "w": card_w * 0.35,
                "h": card_h * 0.25,
            }
            trend = [float(value) for value in metric.get("trend_values", [])]
            trend_points: list[dict[str, float]] = []
            if trend:
                low = min(trend)
                high = max(trend)
                spread = high - low
                for trend_index, value in enumerate(trend):
                    fraction_x = trend_index / max(1, len(trend) - 1)
                    fraction_y = 0.5 if spread == 0 else (value - low) / spread
                    trend_points.append(
                        {
                            "x": trend_box["x"] + trend_box["w"] * fraction_x,
                            "y": trend_box["y"] + trend_box["h"] * (1.0 - fraction_y),
                        }
                    )
            variance = float(metric["value"]) - float(metric["target"])
            favorable = variance >= 0 if metric["direction"] == "higher_is_better" else variance <= 0
            cards.append(
                {
                    "metric": metric,
                    "x": x,
                    "y": y,
                    "w": card_w,
                    "h": card_h,
                    "variance": variance,
                    "favorable": favorable,
                    "trend_box": trend_box,
                    "trend_points": trend_points,
                }
            )
        pages.append({"index": page_index + 1, "cards": cards})
    reasons = ["metric_count_exceeded"] if len(metric_pages) > 1 else []
    return {
        "component": "kpi_status",
        "mode": "split" if reasons else "single",
        "reason_codes": reasons,
        "frame": dict(frame),
        "pages": pages,
    }


def _resolve_horizontal_labels(
    nodes: list[dict[str, Any]],
    frame: Mapping[str, float],
    label_width: float,
    gap: float,
) -> None:
    for lane in ("above", "below"):
        lane_nodes = [node for node in nodes if node["label_box"]["lane"] == lane]
        cursor = frame["x"]
        for node in lane_nodes:
            box = node["label_box"]
            box["x"] = max(box["x"], cursor)
            cursor = box["x"] + label_width + gap
        if lane_nodes:
            overflow = lane_nodes[-1]["label_box"]["x"] + label_width - (frame["x"] + frame["w"])
            if overflow > 0:
                for node in reversed(lane_nodes):
                    node["label_box"]["x"] -= overflow
                    overflow = max(0.0, frame["x"] - node["label_box"]["x"])


def layout_milestone(
    ir: Mapping[str, Any],
    frame: Mapping[str, float],
    tokens: Mapping[str, Any],
) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    milestones = sorted(validated["milestones"], key=lambda item: (item["date"], item["id"]))
    max_per_page = int(tokens["density"]["milestone"]["max_per_page"])
    table_above = int(tokens["density"]["milestone"]["table_fallback_above"])
    if len(milestones) > table_above:
        return {
            "component": "milestone",
            "mode": "table",
            "reason_codes": ["milestone_density_exceeded"],
            "frame": dict(frame),
            "pages": [{"index": 1, "rows": milestones}],
        }
    milestone_pages = _chunks(milestones, max_per_page)
    pages: list[dict[str, Any]] = []
    axis_y = frame["y"] + frame["h"] * 0.52
    label_width = max(float(tokens["density"]["milestone"]["min_label_width_in"]), 1.42)
    for page_index, page_milestones in enumerate(milestone_pages):
        nodes: list[dict[str, Any]] = []
        for index, milestone in enumerate(page_milestones):
            x = frame["x"] + frame["w"] * date_to_position(
                milestone["date"],
                validated["start_date"],
                validated["end_date"],
            )
            lane = "above" if index % 2 == 0 else "below"
            label_y = axis_y - 1.50 if lane == "above" else axis_y + 0.42
            nodes.append(
                {
                    "milestone": milestone,
                    "x": x,
                    "y": axis_y,
                    "lane": lane,
                    "leader_end_y": axis_y - 0.42 if lane == "above" else axis_y + 0.42,
                    "label_box": {
                        "x": min(max(x - label_width / 2, frame["x"]), frame["x"] + frame["w"] - label_width),
                        "y": label_y,
                        "w": label_width,
                        "h": 0.94,
                        "lane": lane,
                    },
                }
            )
        _resolve_horizontal_labels(nodes, frame, label_width, 0.10)
        pages.append({"index": page_index + 1, "axis_y": axis_y, "nodes": nodes})
    reasons = ["milestone_count_exceeded"] if len(milestone_pages) > 1 else []
    return {
        "component": "milestone",
        "mode": "split" if reasons else "single",
        "reason_codes": reasons,
        "frame": dict(frame),
        "pages": pages,
    }


def layout_risk_heat_map(
    ir: Mapping[str, Any],
    frame: Mapping[str, float],
    tokens: Mapping[str, Any],
) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    risks = validated["risks"]
    max_points = int(tokens["density"]["risk_heat_map"]["max_points"])
    if len(risks) > max_points:
        return {
            "component": "risk_heat_map",
            "mode": "table",
            "reason_codes": ["risk_density_exceeded"],
            "frame": dict(frame),
            "pages": [{"index": 1, "rows": risks}],
        }
    grid_size = min(frame["h"] - 0.42, frame["w"] * 0.43)
    grid = {
        "x": frame["x"] + 0.42,
        "y": frame["y"] + 0.10,
        "w": grid_size,
        "h": grid_size,
    }
    cell_w = grid["w"] / 5
    cell_h = grid["h"] / 5
    cell_groups: dict[tuple[int, int], list[Mapping[str, Any]]] = {}
    for risk in risks:
        cell_groups.setdefault((risk["likelihood"], risk["impact"]), []).append(risk)
    offsets = [
        (-0.30, -0.30),
        (0.30, -0.30),
        (-0.30, 0.30),
        (0.30, 0.30),
        (0.0, -0.30),
        (0.0, 0.30),
        (-0.30, 0.0),
        (0.30, 0.0),
        (0.0, 0.0),
    ]
    points: list[dict[str, Any]] = []
    for (likelihood, impact), cell_risks in sorted(cell_groups.items()):
        cell_x = grid["x"] + (likelihood - 1) * cell_w
        cell_y = grid["y"] + (5 - impact) * cell_h
        for index, risk in enumerate(sorted(cell_risks, key=lambda item: item["id"])):
            offset_x, offset_y = offsets[index % len(offsets)]
            points.append(
                {
                    "risk": risk,
                    "id": risk["id"],
                    "likelihood": likelihood,
                    "impact": impact,
                    "x": cell_x + cell_w * (0.5 + offset_x),
                    "y": cell_y + cell_h * (0.5 + offset_y),
                    "cell_bounds": {
                        "x": cell_x,
                        "y": cell_y,
                        "x2": cell_x + cell_w,
                        "y2": cell_y + cell_h,
                    },
                }
            )
    list_panel = {
        "x": grid["x"] + grid["w"] + 0.45,
        "y": frame["y"] + 0.06,
        "w": frame["x"] + frame["w"] - (grid["x"] + grid["w"] + 0.45),
        "h": frame["h"] - 0.12,
    }
    return {
        "component": "risk_heat_map",
        "mode": "single",
        "reason_codes": [],
        "frame": dict(frame),
        "point_diameter": 0.26,
        "pages": [
            {
                "index": 1,
                "grid": grid,
                "cell_w": cell_w,
                "cell_h": cell_h,
                "points": points,
                "list_panel": list_panel,
                "risks": risks,
            }
        ],
    }


def layout_raci(
    ir: Mapping[str, Any],
    frame: Mapping[str, float],
    tokens: Mapping[str, Any],
) -> dict[str, Any]:
    validated = validate_component_ir(ir)
    roles = validated["roles"]
    activities = validated["activities"]
    max_roles = int(tokens["density"]["raci"]["max_roles_per_page"])
    max_activities = int(tokens["density"]["raci"]["max_activities_per_page"])
    role_pages = _chunks(roles, max_roles)
    activity_pages = _chunks(activities, max_activities)
    assignment_map = {
        (assignment["activity"], assignment["role"]): assignment["code"]
        for assignment in validated["assignments"]
    }
    pages: list[dict[str, Any]] = []
    page_index = 0
    for activity_page in activity_pages:
        for role_page in role_pages:
            page_index += 1
            activity_w = min(3.15, frame["w"] * 0.28)
            role_w = (frame["w"] - activity_w) / len(role_page)
            row_h = frame["h"] / (len(activity_page) + 1)
            rows = []
            for row_index, activity in enumerate(activity_page):
                rows.append(
                    {
                        "activity": activity,
                        "y": frame["y"] + (row_index + 1) * row_h,
                        "h": row_h,
                        "codes": [assignment_map.get((activity, role), "") for role in role_page],
                    }
                )
            pages.append(
                {
                    "index": page_index,
                    "roles": role_page,
                    "activities": activity_page,
                    "rows": rows,
                    "activity_w": activity_w,
                    "role_w": role_w,
                    "row_h": row_h,
                    "frame": dict(frame),
                }
            )
    reasons: list[str] = []
    if len(role_pages) > 1:
        reasons.append("role_count_exceeded")
    if len(activity_pages) > 1:
        reasons.append("activity_count_exceeded")
    return {
        "component": "raci",
        "mode": "split" if reasons else "single",
        "reason_codes": reasons,
        "frame": dict(frame),
        "pages": pages,
    }
