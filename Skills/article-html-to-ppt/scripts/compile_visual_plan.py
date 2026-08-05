#!/usr/bin/env python3
"""Bind validated visual-plan intents to the PPT IR used by delivery and builders.

This is deliberately fail-closed: a relationship page without a real renderer must
not silently retain an unrelated chart/table from an earlier PPT IR draft.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


COMPILABLE = {"phase_roadmap"}
RELATIONSHIP_EXPRESSIONS = {"relationship_visual", "sequence_visual"}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _roadmap_object(slide: dict[str, Any], intent: dict[str, Any]) -> dict[str, Any]:
    message = str(slide.get("message") or intent.get("message") or "关键阶段").strip()
    return {
        "id": f"{slide['id']}-phase-roadmap",
        "type": "diagram",
        "component_type": "phase_roadmap",
        "semantic_role": "phase_roadmap",
        "content": {
            "phases": [
                {"label": "当前判断", "detail": message},
                {"label": "关键行动", "detail": "以证据验证并形成决策门禁"},
                {"label": "下一阶段", "detail": "复盘结果并决定是否扩大应用"},
            ],
            "milestones": [
                {"label": "决策门禁", "phase": 1},
            ],
        },
        "diagram_ir": {
            "diagram_id": f"{slide['id']}-phase-roadmap",
            "diagram_type": "timeline",
            "nodes": [
                {
                    "id": "current",
                    "label": "当前判断",
                    "priority": "primary",
                },
                {
                    "id": "action",
                    "label": "关键行动",
                    "priority": "secondary",
                },
                {
                    "id": "next",
                    "label": "下一阶段",
                    "priority": "secondary",
                },
            ],
            "edges": [
                {"id": "current-to-action", "source": "current", "target": "action", "relation": "sequence", "priority": "primary"},
                {"id": "action-to-next", "source": "action", "target": "next", "relation": "sequence", "priority": "secondary"},
            ],
            "main_paths": [
                {"id": "main", "node_ids": ["current", "action", "next"], "priority": "primary"},
            ],
        },
        "complexity": {"node_count": 3, "edge_count": 2},
        "source_refs": list(slide.get("source_refs") or []),
        "editability": "native_required",
        "priority": "primary",
        "delivery_preferences": {
            "preferred_route": "native_diagram",
            "allowed_fallbacks": [],
        },
    }


def compile_visual_plan(ppt_ir: dict[str, Any], visual_plan: dict[str, Any]) -> dict[str, Any]:
    intents = visual_plan.get("slides")
    slides = ppt_ir.get("slides")
    if not isinstance(intents, list) or not isinstance(slides, list):
        raise ValueError("VISUAL_PLAN_IR_COMPONENT_MISMATCH: document structure")
    by_id = {slide.get("id"): slide for slide in slides if isinstance(slide, dict) and isinstance(slide.get("id"), str)}
    bind_records: list[dict[str, str]] = []

    for intent in intents:
        if not isinstance(intent, dict):
            raise ValueError("VISUAL_PLAN_IR_COMPONENT_MISMATCH: invalid intent")
        slide_id = intent.get("slide_id")
        if not isinstance(slide_id, str) or slide_id not in by_id:
            raise ValueError("VISUAL_PLAN_IR_COMPONENT_MISMATCH: slide id")
        slide = by_id[slide_id]
        component = intent.get("semantic_component")
        expression = intent.get("primary_expression")
        if not isinstance(component, str) or not isinstance(expression, str):
            raise ValueError(f"VISUAL_PLAN_IR_COMPONENT_MISMATCH:{slide_id}")

        slide["page_design_intent"] = intent
        if component in COMPILABLE:
            slide["primary_expression"] = "relationship_visual"
            slide["objects"] = [_roadmap_object(slide, intent)]
            bind_records.append({"slide_id": slide_id, "planned_component": component, "actual_component": component})
            continue
        if expression in RELATIONSHIP_EXPRESSIONS and component == "unsupported":
            raise ValueError(f"VISUAL_PLAN_IR_COMPONENT_MISMATCH:{slide_id}:{component}")
        bind_records.append({"slide_id": slide_id, "planned_component": component, "actual_component": "preserved"})

    ppt_ir["visual_plan_bindings"] = bind_records
    return ppt_ir


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compile visual-plan intents into PPT IR.")
    parser.add_argument("--ppt-ir", type=Path, required=True)
    parser.add_argument("--visual-plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        compiled = compile_visual_plan(load_json(args.ppt_ir), load_json(args.visual_plan))
        write_json(args.output, compiled)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"compile_visual_plan: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
