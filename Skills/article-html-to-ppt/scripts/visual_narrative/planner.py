from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .intent import validate_page_design_intent


SCHEMA_VERSION = "1.0.0"
DEFAULT_STYLE_ID = "azure-insight-architecture"
ROOT = Path(__file__).resolve().parents[2]
STYLE_DIR = ROOT / "references" / "template-packs"

COMPONENT_RULES = (
    ({"heatmap", "matrix"}, "heat_matrix"),
    ({"layer", "system_boundary", "data_flow"}, "layered_architecture"),
    ({"hierarchy", "drill_down"}, "drill_down_stair"),
    ({"phase", "milestone", "roadmap"}, "phase_roadmap"),
)

EXPRESSION_BY_COMPONENT = {
    "heat_matrix": "table_matrix",
    "layered_architecture": "relationship_visual",
    "drill_down_stair": "relationship_visual",
    "phase_roadmap": "sequence_visual",
    "unsupported": "relationship_visual",
}

ARCHETYPE_BY_COMPONENT = {
    "heat_matrix": "heat_matrix",
    "layered_architecture": "layered_architecture",
    "drill_down_stair": "drill_down",
    "phase_roadmap": "phase_roadmap",
    "unsupported": "relationship_canvas",
}


class VisualPlanningError(ValueError):
    def __init__(self, code: str, slide_id: str = "deck") -> None:
        super().__init__(f"{code}:{slide_id}")
        self.code = code
        self.slide_id = slide_id


def choose_component(relationships: set[str]) -> str:
    for signals, component in COMPONENT_RULES:
        if signals & relationships:
            return component
    return "unsupported"


def plan_visual_narrative(
    task_route: dict[str, Any],
    storyline: dict[str, Any],
    style_id: str = DEFAULT_STYLE_ID,
) -> dict[str, Any]:
    route = _require_string(task_route.get("selected_route"), "PLANNER_ROUTE_REQUIRED")
    slides = storyline.get("slides")
    if not isinstance(slides, list) or not slides:
        raise VisualPlanningError("PLANNER_SLIDES_REQUIRED")

    style = _load_style(style_id)
    intents = [
        _plan_slide(slide, style=style)
        for slide in slides
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "selected_route": route,
        "style_id": style["style_id"],
        "display_name_zh": style["display_name_zh"],
        "display_name_en": style["display_name_en"],
        "slides": intents,
    }


def _plan_slide(
    slide: Any,
    *,
    style: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(slide, dict):
        raise VisualPlanningError("PLANNER_SLIDE_INVALID")

    slide_id = _require_string(slide.get("id"), "PLANNER_SLIDE_ID_REQUIRED")
    role = _require_string(slide.get("role"), "PLANNER_SLIDE_ROLE_REQUIRED", slide_id)
    message = _require_string(slide.get("message"), "PLANNER_MESSAGE_REQUIRED", slide_id)
    evidence_refs = _evidence_refs(slide.get("evidence_refs"))
    if not evidence_refs:
        raise VisualPlanningError("PLANNER_EVIDENCE_REQUIRED", slide_id)

    relationships = set(_string_list(slide.get("relationships")))
    component = choose_component(relationships)
    if component == "unsupported" and role not in {"relationship", "architecture", "diagram"}:
        component = _component_for_non_relationship(role)

    expression = EXPRESSION_BY_COMPONENT.get(component, _expression_for_role(role))
    archetype = ARCHETYPE_BY_COMPONENT.get(component, _archetype_for_role(role))
    priority = "key" if slide.get("priority") in {"key", "high"} else "supporting"

    intent = {
        "schema_version": SCHEMA_VERSION,
        "slide_id": slide_id,
        "slide_role": role,
        "audience_question": (
            slide.get("audience_question")
            if isinstance(slide.get("audience_question"), str) and slide["audience_question"].strip()
            else f"这页需要帮助受众理解什么？"
        ),
        "message": message,
        "evidence_refs": evidence_refs,
        "priority": priority,
        "primary_expression": expression,
        "page_archetype": archetype,
        "semantic_component": component,
        "visual_anchor": component,
        "layout": {
            "family": "single_semantic_canvas",
            "zones": ["title", "primary", "evidence", "source"],
            "primary_zone_ratio": 0.64 if priority == "key" else 0.56,
            "reading_order": ["title", "primary", "evidence", "source"],
        },
        "density": {
            "level": _density_for_slide(slide, priority),
            "max_primary_labels": 6,
            "max_supporting_blocks": 2,
        },
        "editability": {
            "message_bearing": "native_required",
            "whole_slide_raster_forbidden": True,
        },
        "delivery": {
            "preferred_route": "native_diagram",
            "allowed_fallbacks": [],
            "minimum_renderer_support": "full",
        },
        "style_system": {
            "style_id": style["style_id"],
            "display_name_zh": style["display_name_zh"],
        },
        "forbidden_patterns": [
            "generic_equal_cards",
            "multiple_primary_anchors",
            "decorative_isometric_scene_without_semantic_role",
        ],
        "qa_focus": [
            "primary_anchor_strength",
            "evidence_lineage",
            "label_legibility",
            "native_editability",
        ],
    }
    issues = validate_page_design_intent(intent)
    if issues:
        codes = ",".join(issue["code"] for issue in issues)
        raise VisualPlanningError(f"PLANNER_INTENT_INVALID[{codes}]", slide_id)
    return intent


def _load_style(style_id: str) -> dict[str, Any]:
    if not isinstance(style_id, str) or not style_id.strip():
        raise VisualPlanningError("PLANNER_STYLE_REQUIRED")
    path = STYLE_DIR / f"{style_id}.json"
    if not path.is_file():
        raise VisualPlanningError("PLANNER_STYLE_UNKNOWN")
    with path.open("r", encoding="utf-8") as handle:
        style = json.load(handle)
    if not isinstance(style, dict) or style.get("style_id") != style_id:
        raise VisualPlanningError("PLANNER_STYLE_INVALID")
    return style


def _require_string(value: Any, code: str, slide_id: str = "deck") -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualPlanningError(code, slide_id)
    return value.strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _evidence_refs(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    refs: list[Any] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            refs.append(item.strip())
        elif isinstance(item, dict) and item:
            refs.append(item)
    return refs


def _component_for_non_relationship(role: str) -> str:
    return {
        "data": "data_comparison_bridge",
        "roadmap": "phase_roadmap",
        "timeline": "phase_roadmap",
        "kpi": "kpi_dashboard",
    }.get(role, "narrative_statement")


def _expression_for_role(role: str) -> str:
    return {
        "data": "data_visual",
        "roadmap": "sequence_visual",
        "timeline": "sequence_visual",
        "kpi": "data_visual",
    }.get(role, "statement")


def _archetype_for_role(role: str) -> str:
    return {
        "data": "comparison_bridge",
        "roadmap": "phase_roadmap",
        "timeline": "phase_roadmap",
        "kpi": "dashboard",
    }.get(role, "statement")


def _density_for_slide(slide: dict[str, Any], priority: str) -> str:
    density = slide.get("density")
    if isinstance(density, str) and density in {"low", "medium", "high"}:
        return density
    return "medium" if priority == "key" else "low"
