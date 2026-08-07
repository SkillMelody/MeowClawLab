from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from compile_visual_plan import compile_visual_plan


def _source_ref() -> list[dict[str, str]]:
    return [{"source_id": "report", "locator": "Exhibit 1", "claim_type": "direct"}]


def test_compiler_preserves_source_backed_supporting_objects_when_adding_primary_component() -> None:
    ppt_ir = {
        "slides": [
            {
                "id": "S03",
                "message": "采用率提高，但规模化价值仍有缺口。",
                "source_refs": _source_ref(),
                "objects": [
                    {
                        "id": "adoption-chart",
                        "type": "chart",
                        "component_type": "bar_chart",
                        "content": {"categories": ["2023", "2024", "2025"], "series": [{"name": "采用率", "values": [55, 78, 88]}]},
                        "source_refs": _source_ref(),
                        "editability": "native_required",
                        "priority": "primary",
                    },
                    {
                        "id": "management-implication",
                        "type": "shape",
                        "component_type": "evidence_block",
                        "content": "规模化仍是价值实现的瓶颈。",
                        "source_refs": _source_ref(),
                        "editability": "native_required",
                        "priority": "supporting",
                    },
                ],
            }
        ]
    }
    visual_plan = {
        "slides": [
            {
                "slide_id": "S03",
                "semantic_component": "phase_roadmap",
                "primary_expression": "sequence_visual",
                "message": "采用率提高，但规模化价值仍有缺口。",
                "evidence_refs": _source_ref(),
            }
        ]
    }

    compiled = compile_visual_plan(ppt_ir, visual_plan)
    objects = compiled["slides"][0]["objects"]

    assert {item["id"] for item in objects} == {"adoption-chart", "management-implication", "S03-phase_roadmap"}
    assert next(item for item in objects if item["id"] == "management-implication")["priority"] == "supporting"
