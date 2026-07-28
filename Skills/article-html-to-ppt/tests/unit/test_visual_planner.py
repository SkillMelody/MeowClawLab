from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from visual_narrative.intent import validate_page_design_intent
from visual_narrative.planner import plan_visual_narrative


def relationship_storyline() -> dict:
    return {
        "title": "企业指标穿透方案",
        "slides": [
            {
                "id": "S03",
                "role": "relationship",
                "audience_question": "指标如何从集团穿透到业务单据？",
                "message": "统一指标从集团逐层穿透至业务单据。",
                "evidence_refs": ["E03"],
                "relationships": ["hierarchy", "drill_down"],
                "priority": "key",
            }
        ],
    }


def test_relationship_slide_selects_semantic_component() -> None:
    plan = plan_visual_narrative(
        {"selected_route": "enterprise_proposal"},
        relationship_storyline(),
        "azure-insight-architecture",
    )

    slide = plan["slides"][0]
    assert slide["semantic_component"] == "drill_down_stair"
    assert slide["primary_expression"] == "relationship_visual"
    assert slide["page_archetype"] != "equal_cards"
    assert "generic_equal_cards" in slide["forbidden_patterns"]


def test_every_slide_is_a_valid_page_design_intent() -> None:
    storyline = relationship_storyline()
    storyline["slides"].append(
        {
            "id": "S04",
            "role": "architecture",
            "audience_question": "系统如何分层并保持边界清晰？",
            "message": "五层能力架构通过统一数据流连接。",
            "evidence_refs": ["E04"],
            "relationships": ["layer", "system_boundary", "data_flow"],
        }
    )

    plan = plan_visual_narrative(
        {"selected_route": "technical_architecture"},
        storyline,
        "azure-insight-architecture",
    )

    assert len(plan["slides"]) == 2
    assert plan["slides"][1]["semantic_component"] == "layered_architecture"
    intent_schema = json.loads(
        (ROOT / "schemas" / "page-design-intent.schema.json").read_text(encoding="utf-8")
    )
    for slide in plan["slides"]:
        assert validate_page_design_intent(slide) == []
        Draft202012Validator(intent_schema).validate(slide)

    schema = json.loads((ROOT / "schemas" / "visual-plan.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(plan)


def test_planner_preserves_structured_evidence_refs() -> None:
    storyline = relationship_storyline()
    storyline["slides"][0]["evidence_refs"] = [
        {"source_id": "E03", "locator": "第 3 章"}
    ]

    plan = plan_visual_narrative(
        {"selected_route": "enterprise_proposal"},
        storyline,
        "azure-insight-architecture",
    )

    assert plan["slides"][0]["evidence_refs"] == [
        {"source_id": "E03", "locator": "第 3 章"}
    ]


def test_cli_writes_schema_valid_chinese_visual_plan(tmp_path: Path) -> None:
    task_route_path = tmp_path / "task-route.json"
    storyline_path = tmp_path / "storyline.json"
    output_path = tmp_path / "visual-plan.json"
    task_route_path.write_text(
        json.dumps({"selected_route": "enterprise_proposal"}, ensure_ascii=False),
        encoding="utf-8",
    )
    storyline_path.write_text(
        json.dumps(relationship_storyline(), ensure_ascii=False),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "plan_visual_narrative.py"),
            "--task-route",
            str(task_route_path),
            "--storyline",
            str(storyline_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    plan = json.loads(output_path.read_text(encoding="utf-8"))
    assert plan["display_name_zh"] == "澄蓝智构"
    assert plan["slides"][0]["message"] == "统一指标从集团逐层穿透至业务单据。"
