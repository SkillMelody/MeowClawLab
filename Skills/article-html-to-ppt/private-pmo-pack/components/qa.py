"""Reusable semantic and geometry QA checks for PMO components."""

from __future__ import annotations

import math
from typing import Any, Iterable, Mapping

from components.ir import validate_component_ir


def legend_completeness(used_roles: Iterable[str], legend_roles: Iterable[str]) -> dict[str, Any]:
    used = set(used_roles)
    declared = set(legend_roles)
    missing = sorted(used - declared)
    return {"passed": not missing, "missing": missing, "extra": sorted(declared - used)}


def check_text_bounds(
    boxes: Iterable[Mapping[str, Any]],
    region: Mapping[str, float],
    *,
    tolerance: float = 1e-6,
) -> dict[str, Any]:
    region_x2 = region["x"] + region["w"]
    region_y2 = region["y"] + region["h"]
    outside: list[str] = []
    for box in boxes:
        if (
            box["x"] < region["x"] - tolerance
            or box["y"] < region["y"] - tolerance
            or box["x"] + box["w"] > region_x2 + tolerance
            or box["y"] + box["h"] > region_y2 + tolerance
        ):
            outside.append(str(box.get("name", "unnamed")))
    return {"passed": not outside, "outside": outside}


def check_text_overflow(
    boxes: Iterable[Mapping[str, Any]],
    *,
    min_font_pt: float,
) -> dict[str, Any]:
    overflow: list[str] = []
    details: list[dict[str, Any]] = []
    for box in boxes:
        font_pt = max(float(box.get("font_pt", min_font_pt)), min_font_pt)
        width_pt = float(box["w"]) * 72.0
        height_pt = float(box["h"]) * 72.0
        average_glyph_width = font_pt * 0.52
        chars_per_line = max(1, int(width_pt / average_glyph_width))
        text = str(box.get("text", ""))
        paragraphs = text.splitlines() or [""]
        line_count = sum(max(1, math.ceil(len(paragraph) / chars_per_line)) for paragraph in paragraphs)
        required_height_pt = line_count * font_pt * 1.22
        if required_height_pt > height_pt:
            name = str(box.get("name", "unnamed"))
            overflow.append(name)
            details.append(
                {
                    "name": name,
                    "required_height_pt": round(required_height_pt, 2),
                    "available_height_pt": round(height_pt, 2),
                }
            )
    return {"passed": not overflow, "overflow": overflow, "details": details}


def _boxes_overlap(first: Mapping[str, float], second: Mapping[str, float], *, gap: float = 0.0) -> bool:
    return not (
        first["x"] + first["w"] + gap <= second["x"]
        or second["x"] + second["w"] + gap <= first["x"]
        or first["y"] + first["h"] + gap <= second["y"]
        or second["y"] + second["h"] + gap <= first["y"]
    )


def qa_component(
    ir: Mapping[str, Any],
    layout: Mapping[str, Any],
    tokens: Mapping[str, Any],
) -> dict[str, Any]:
    """Run blocking semantic and deterministic geometry gates."""

    validated = validate_component_ir(ir)
    component_type = validated["type"]
    reasons: list[str] = []
    checks: dict[str, Any] = {"semantic_ir": {"passed": True}}
    frame = layout.get("frame", {})

    if layout.get("component") != component_type:
        reasons.append("layout_component_mismatch")

    if component_type == "kpi_status":
        card_boxes = [
            {
                "name": card["metric"]["id"],
                "x": card["x"],
                "y": card["y"],
                "w": card["w"],
                "h": card["h"],
            }
            for page in layout["pages"]
            for card in page["cards"]
        ]
        bounds = check_text_bounds(card_boxes, frame)
        checks["card_bounds"] = bounds
        if not bounds["passed"]:
            reasons.append("kpi_card_outside_frame")
        max_per_page = int(tokens["density"]["kpi_status"]["max_per_page"])
        if any(len(page["cards"]) > max_per_page for page in layout["pages"]):
            reasons.append("kpi_page_density_exceeded")
        for page in layout["pages"]:
            for card in page["cards"]:
                trend = card["trend_box"]
                for point in card["trend_points"]:
                    if not (
                        trend["x"] <= point["x"] <= trend["x"] + trend["w"]
                        and trend["y"] <= point["y"] <= trend["y"] + trend["h"]
                    ):
                        reasons.append("kpi_trend_outside_card")
        used_statuses = {metric["status"] for metric in validated["metrics"]}
        legend = legend_completeness(used_statuses, tokens["status_semantics"].keys())
        checks["status_legend"] = legend
        if not legend["passed"]:
            reasons.append("status_legend_incomplete")

    elif component_type == "milestone":
        if layout["mode"] != "table":
            max_per_page = int(tokens["density"]["milestone"]["max_per_page"])
            for page in layout["pages"]:
                if len(page["nodes"]) > max_per_page:
                    reasons.append("milestone_page_density_exceeded")
                label_boxes = [node["label_box"] for node in page["nodes"]]
                bounds = check_text_bounds(label_boxes, frame)
                if not bounds["passed"]:
                    reasons.append("milestone_label_outside_frame")
                for index, first in enumerate(label_boxes):
                    for second in label_boxes[index + 1 :]:
                        if first["lane"] == second["lane"] and _boxes_overlap(first, second, gap=0.02):
                            reasons.append("milestone_label_collision")
                for node in page["nodes"]:
                    if not frame["x"] <= node["x"] <= frame["x"] + frame["w"]:
                        reasons.append("milestone_node_outside_axis")
            checks["label_collision"] = {"passed": "milestone_label_collision" not in reasons}

    elif component_type == "risk_heat_map":
        used_statuses = {risk["status"] for risk in validated["risks"]}
        legend = legend_completeness(used_statuses, tokens["status_semantics"].keys())
        checks["status_legend"] = legend
        if not legend["passed"]:
            reasons.append("status_legend_incomplete")
        if layout["mode"] != "table":
            for page in layout["pages"]:
                grid = page["grid"]
                seen: dict[tuple[int, int], set[tuple[float, float]]] = {}
                cell_points: dict[tuple[int, int], list[tuple[float, float]]] = {}
                for point in page["points"]:
                    if not (
                        grid["x"] < point["x"] < grid["x"] + grid["w"]
                        and grid["y"] < point["y"] < grid["y"] + grid["h"]
                    ):
                        reasons.append("risk_point_outside_grid")
                    cell = (point["likelihood"], point["impact"])
                    position = (round(point["x"], 6), round(point["y"], 6))
                    if position in seen.setdefault(cell, set()):
                        reasons.append("risk_point_overlap")
                    seen[cell].add(position)
                    for prior_x, prior_y in cell_points.setdefault(cell, []):
                        if math.hypot(point["x"] - prior_x, point["y"] - prior_y) < float(layout["point_diameter"]):
                            reasons.append("risk_point_overlap")
                    cell_points[cell].append((point["x"], point["y"]))
                if any(
                    len(positions) > int(tokens["density"]["risk_heat_map"]["max_points_per_cell"])
                    for positions in seen.values()
                ):
                    reasons.append("risk_cell_density_exceeded")
            checks["point_geometry"] = {
                "passed": not {"risk_point_outside_grid", "risk_point_overlap", "risk_cell_density_exceeded"}.intersection(
                    reasons
                )
            }

    elif component_type == "raci":
        max_roles = int(tokens["density"]["raci"]["max_roles_per_page"])
        max_activities = int(tokens["density"]["raci"]["max_activities_per_page"])
        for page in layout["pages"]:
            if len(page["roles"]) > max_roles:
                reasons.append("raci_role_density_exceeded")
            if len(page["rows"]) > max_activities:
                reasons.append("raci_activity_density_exceeded")
            if page["role_w"] < 0.72 or page["row_h"] < 0.34:
                reasons.append("raci_cell_too_small")
            if any(code not in {"", "R", "A", "C", "I"} for row in page["rows"] for code in row["codes"]):
                reasons.append("raci_code_invalid")
        checks["table_density"] = {
            "passed": not {
                "raci_role_density_exceeded",
                "raci_activity_density_exceeded",
                "raci_cell_too_small",
            }.intersection(reasons)
        }

    unique_reasons = sorted(set(reasons))
    return {
        "component": component_type,
        "passed": not unique_reasons,
        "reason_codes": unique_reasons,
        "checks": checks,
    }
