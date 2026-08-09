from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ir_enrichment import enrich_ppt_ir
from ir_quality_floor import assess_ir_quality_floor


def test_enrichment_does_not_treat_repeated_slide_message_as_evidence() -> None:
    ppt_ir = {
        "slides": [{
            "id": "S03", "slide_role": "data", "primary_expression": "data_visual",
            "title": "采用率提高", "message": "规律使用 AI 的组织占比达到 88%。",
            "source_refs": [{"source_id": "report", "locator": "Exhibit 1", "claim_type": "direct"}],
            "objects": [{"id": "chart", "type": "chart", "component_type": "bar_chart", "priority": "primary", "content": {"categories": ["2025"], "series": [{"name": "采用率", "values": [88]}]}}],
        }]
    }

    enriched = enrich_ppt_ir(ppt_ir)

    objects = enriched["slides"][0]["objects"]
    assert len(objects) == 1
    assert objects[0]["source_refs"] == ppt_ir["slides"][0]["source_refs"]
    assert assess_ir_quality_floor(enriched)["status"] == "blocked"


def test_enrichment_builds_same_slide_support_from_two_source_bound_primary_objects() -> None:
    ppt_ir = {
        "slides": [{
            "id": "S03", "slide_role": "data", "primary_expression": "data_visual",
            "title": "使用扩张明显，但规模化阶段只占约三分之一",
            "message": "从“会用”到“规模化”之间仍存在显著价值落地缺口。",
            "source_refs": [{"source_id": "report", "locator": "slide-level", "claim_type": "direct"}],
            "objects": [
                {
                    "id": "adoption", "type": "chart", "component_type": "bar_chart", "priority": "primary",
                    "content": {"categories": ["2023", "2024", "2025"], "series": [{"name": "规律使用 AI", "values": [55, 78, 88]}]},
                    "source_refs": [{"source_id": "report", "locator": "Exhibit adoption", "claim_type": "direct"}],
                },
                {
                    "id": "stage", "type": "table", "component_type": "native_table", "priority": "primary",
                    "content": {"headers": ["阶段", "组织占比"], "body": [["试验", "32%"], ["试点", "30%"], ["规模化", "31%"], ["全面规模化", "7%"]]},
                    "source_refs": [{"source_id": "report", "locator": "Exhibit stage", "claim_type": "direct"}],
                },
            ],
        }]
    }

    enriched = enrich_ppt_ir(ppt_ir)

    support = enriched["slides"][0]["objects"][-1]
    assert support["id"] == "S03-same-slide-evidence-comparison"
    assert support["component_type"] == "comparison_card"
    assert support["content"]["title"] == "同页来源证据对照"
    assert [item["object_id"] for item in support["content"]["items"]] == ["adoption", "stage"]
    assert {ref["locator"] for ref in support["source_refs"]} == {"Exhibit adoption", "Exhibit stage"}
    assert "slide-level" not in {ref["locator"] for ref in support["source_refs"]}
    assert support["provenance"]["derived_from_object_ids"] == ["adoption", "stage"]
    assert assess_ir_quality_floor(enriched)["status"] == "passed"


def test_enrichment_compiles_explicit_independent_source_bound_evidence() -> None:
    ppt_ir = {
        "slides": [{
            "id": "S03", "slide_role": "data", "primary_expression": "data_visual",
            "title": "采用率提高", "message": "规律使用 AI 的组织占比达到 88%。",
            "source_refs": [{"source_id": "report", "locator": "Exhibit 1", "claim_type": "direct"}],
            "supporting_evidence": [{
                "content": "只有约三分之一组织完成企业级扩展，采用与规模化之间存在缺口。",
                "source_refs": [{"source_id": "report", "locator": "Exhibit 2", "claim_type": "direct"}],
            }],
            "objects": [{"id": "chart", "type": "chart", "component_type": "bar_chart", "priority": "primary", "content": {"categories": ["2025"], "series": [{"name": "采用率", "values": [88]}]}}],
        }]
    }

    enriched = enrich_ppt_ir(ppt_ir)

    support = enriched["slides"][0]["objects"][-1]
    assert support["component_type"] == "evidence_block"
    assert support["content"].startswith("只有约三分之一")
    assert support["source_refs"][0]["locator"] == "Exhibit 2"
    assert assess_ir_quality_floor(enriched)["status"] == "passed"


def test_enrichment_does_not_build_same_slide_support_from_only_one_primary_object() -> None:
    ppt_ir = {
        "slides": [{
            "id": "S05", "slide_role": "data", "primary_expression": "data_visual",
            "title": "创新是最常被感知的收益，EBIT 仍是更高门槛",
            "message": "64% 认为 AI 促进创新；企业级 EBIT 影响仅为 39%。",
            "source_refs": [{"source_id": "report", "locator": "slide-level", "claim_type": "direct"}],
            "objects": [{
                "id": "benefits", "type": "chart", "component_type": "bar_chart", "priority": "primary",
                "content": {"categories": ["创新", "盈利能力"], "series": [{"name": "改善", "values": [64, 36]}]},
                "source_refs": [{"source_id": "report", "locator": "Exhibit 5", "claim_type": "direct"}],
            }],
        }]
    }

    enriched = enrich_ppt_ir(ppt_ir)

    assert [obj["id"] for obj in enriched["slides"][0]["objects"]] == ["benefits"]
    assert assess_ir_quality_floor(enriched)["status"] == "blocked"


def test_enrichment_is_idempotent_for_generated_same_slide_support() -> None:
    ppt_ir = {
        "slides": [{
            "id": "S02", "slide_role": "judgment", "primary_expression": "structured_cards",
            "title": "核心判断：采用率已走高，但企业级价值仍未普遍兑现",
            "message": "88% 已规律使用 AI；约三分之二仍在试验或试点，只有 39% 报告企业级 EBIT 影响。",
            "objects": [
                {
                    "id": "m1", "type": "shape", "component_type": "metric_card", "priority": "primary",
                    "content": "88%\n至少一个职能规律使用 AI",
                    "source_refs": [{"source_id": "report", "locator": "PDF, m1", "claim_type": "direct"}],
                },
                {
                    "id": "m2", "type": "shape", "component_type": "metric_card", "priority": "primary",
                    "content": "约 2/3\n仍在试验或试点",
                    "source_refs": [{"source_id": "report", "locator": "PDF, m2", "claim_type": "direct"}],
                },
                {
                    "id": "m3", "type": "shape", "component_type": "metric_card", "priority": "primary",
                    "content": "39%\n报告企业级 EBIT 影响",
                    "source_refs": [{"source_id": "report", "locator": "PDF, m3", "claim_type": "direct"}],
                },
            ],
        }]
    }

    first = enrich_ppt_ir(ppt_ir)
    second = enrich_ppt_ir(first)

    generated_ids = [obj["id"] for obj in second["slides"][0]["objects"] if obj["id"] == "S02-same-slide-evidence-comparison"]
    assert generated_ids == ["S02-same-slide-evidence-comparison"]


def test_enrichment_preserves_authored_supporting_evidence_without_generated_duplicate() -> None:
    ppt_ir = {
        "slides": [{
            "id": "S04", "slide_role": "judgment", "primary_expression": "structured_cards",
            "title": "Agentic AI：热度已起，单一职能内的规模化仍稀缺",
            "message": "23% 正在某处规模化 Agentic AI，39% 正在试验；任一职能的规模化比例均不超过 10%。",
            "supporting_evidence": [{
                "content": "热度扩散快于单一职能的组织级落地。",
                "source_refs": [{"source_id": "report", "locator": "Exhibit 4 note", "claim_type": "direct"}],
            }],
            "objects": [
                {
                    "id": "a1", "type": "shape", "component_type": "metric_card", "priority": "primary",
                    "content": "23%\n正在规模化 Agentic AI",
                    "source_refs": [{"source_id": "report", "locator": "PDF, a1", "claim_type": "direct"}],
                },
                {
                    "id": "a2", "type": "shape", "component_type": "metric_card", "priority": "primary",
                    "content": "39%\n正在试验 Agentic AI",
                    "source_refs": [{"source_id": "report", "locator": "PDF, a2", "claim_type": "direct"}],
                },
            ],
        }]
    }

    enriched = enrich_ppt_ir(ppt_ir)

    object_ids = [obj["id"] for obj in enriched["slides"][0]["objects"]]
    assert "S04-source-bound-interpretation" in object_ids
    assert "S04-same-slide-evidence-comparison" not in object_ids
    assert assess_ir_quality_floor(enriched)["status"] == "passed"


def test_enrichment_does_not_fabricate_a_chart_when_data_page_has_no_data_object() -> None:
    ppt_ir = {"slides": [{"id": "S03", "slide_role": "data", "primary_expression": "data_visual", "title": "采用率", "message": "采用率提高。", "source_refs": [], "objects": []}]}

    enriched = enrich_ppt_ir(ppt_ir)

    assert enriched["slides"][0]["objects"] == []
    assert assess_ir_quality_floor(enriched)["status"] == "blocked"
