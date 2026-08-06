"""Boardroom Ink token resolution with legacy PMO style compatibility."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


class TokenResolutionError(KeyError):
    """Raised when a semantic token cannot be resolved."""


BOARDROOM_INK_DEFAULTS: dict[str, Any] = {
    "meta": {
        "schema_version": "1.0",
        "system_id": "boardroom-ink",
        "display_name": "Boardroom Ink",
        "skin": "default",
    },
    "slide": {
        "width_in": 13.333,
        "height_in": 7.5,
        "margin_left_in": 0.55,
        "margin_right_in": 0.55,
        "margin_top_in": 0.34,
        "margin_bottom_in": 0.34,
    },
    "colors": {
        "background": "FFFFFF",
        "paper": "F7F8FA",
        "ink": "182230",
        "text": "344054",
        "muted": "667085",
        "line": "D0D5DD",
        "soft": "E4E7EC",
        "navy": "17365D",
        "blue": "2F6BFF",
        "green": "2E7D32",
        "yellow": "F2C94C",
        "orange": "F2994A",
        "red": "D92D20",
        "white": "FFFFFF",
        "gray": "98A2B3",
        "navy_700": "285489",
    },
    "typography": {
        "font": "Aptos",
        "font_cjk": "Microsoft YaHei",
        "fallback_latin": "Arial",
        "fallback_cjk": "PingFang SC",
        "title_pt": 21,
        "subtitle_pt": 12,
        "body_pt": 11,
        "small_pt": 8.5,
        "metric_pt": 26,
        "roles": {
            "display": {"size_pt": 30, "bold": True},
            "slide_title": {"size_pt": 22, "bold": True},
            "section_title": {"size_pt": 14, "bold": True},
            "body": {"size_pt": 11, "bold": False},
            "label": {"size_pt": 9, "bold": True},
            "metric": {"size_pt": 26, "bold": True},
            "footnote": {"size_pt": 8, "bold": False},
        },
    },
    "spacing": {
        "unit_in": 0.08,
        "scale": {"1": 0.08, "2": 0.16, "3": 0.24, "4": 0.32, "6": 0.48, "8": 0.64, "12": 0.96},
        "minimum_gap_in": 0.12,
        "connector_text_clearance_in": 0.10,
        "chart_label_safe_gap_in": 0.16,
    },
    "line_widths": {
        "hairline_pt": 0.65,
        "grid_pt": 0.5,
        "annotation_pt": 1.5,
        "primary_path_pt": 2.5,
        "reference_pt": 1.5,
    },
    "semantic": {
        "surface": {"canvas": "FFFFFF", "paper": "F7F8FA", "panel": "FFFFFF"},
        "text": {"title": "182230", "body": "344054", "muted": "667085", "inverse": "FFFFFF"},
        "line": {"divider": "D0D5DD", "soft": "E4E7EC", "annotation": "667085"},
        "sequence": {
            "phase_1": "17365D",
            "phase_2": "285489",
            "phase_3": "2F6BFF",
            "phase_4": "2E7D32",
            "phase_5": "667085",
        },
        "state": {
            "healthy": "2E7D32",
            "watch": "F2C94C",
            "risk": "D92D20",
            "neutral": "98A2B3",
        },
        "schedule": {
            "planned": "D0D5DD",
            "actual": "2F6BFF",
            "actual_complete": "17365D",
            "milestone": "F2994A",
            "reference": "D92D20",
        },
    },
    "status_semantics": {
        "healthy": {"label": "On track", "color": "2E7D32", "shape": "circle"},
        "watch": {"label": "Watch", "color": "F2C94C", "shape": "circle"},
        "risk": {"label": "At risk", "color": "D92D20", "shape": "circle"},
        "neutral": {"label": "Not assessed", "color": "98A2B3", "shape": "circle"},
    },
    "density": {
        "doughnut": {"max_categories": 6, "min_label_gap_in": 0.55, "max_label_chars": 31},
        "roadmap": {"max_phases": 5, "max_outputs_per_phase": 4, "min_phase_width_in": 1.85},
        "gantt": {"max_rows": 12, "min_row_height_in": 0.32, "weekly_range_days": 120},
        "kpi_status": {"min_per_page": 3, "max_per_page": 6, "max_label_chars": 34},
        "milestone": {"max_per_page": 8, "table_fallback_above": 16, "min_label_width_in": 1.25},
        "risk_heat_map": {"max_points": 12, "max_points_per_cell": 9, "list_rows": 8},
        "raci": {"max_roles_per_page": 8, "max_activities_per_page": 10, "min_font_pt": 8.0},
    },
    "fallbacks": {
        "doughnut": "right_legend",
        "roadmap": "split_into_waves",
        "gantt": "paginate_or_monthly",
        "kpi_status": "split_into_metric_pages",
        "milestone": "split_then_table",
        "risk_heat_map": "risk_register_table",
        "raci": "split_role_and_activity_blocks",
        "font_latin": "Arial",
        "font_cjk": "PingFang SC",
    },
}


def _deep_merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = deepcopy(value)
    return base


def resolve_tokens(
    legacy_style: Mapping[str, Any] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve Boardroom Ink defaults, legacy aliases, then explicit overrides."""

    resolved = deepcopy(BOARDROOM_INK_DEFAULTS)
    if legacy_style:
        for section in ("slide", "colors", "typography", "rules", "status_colors"):
            value = legacy_style.get(section)
            if isinstance(value, Mapping):
                _deep_merge(resolved.setdefault(section, {}), value)
        resolved["meta"]["legacy_style_id"] = legacy_style.get("style_id")
        resolved["meta"]["legacy_schema_version"] = legacy_style.get("schema_version")
    if overrides:
        _deep_merge(resolved, overrides)
    return resolved


def get_token(tokens: Mapping[str, Any], role: str, *, fallback_role: str | None = None) -> Any:
    """Read a dotted token role; a fallback must be explicitly declared."""

    def lookup(path: str) -> Any:
        node: Any = tokens
        for part in path.split("."):
            if not isinstance(node, Mapping) or part not in node:
                raise TokenResolutionError(path)
            node = node[part]
        return node

    try:
        return lookup(role)
    except TokenResolutionError:
        if fallback_role is None:
            raise
        return lookup(fallback_role)
