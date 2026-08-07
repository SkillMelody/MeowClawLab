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


def test_enrichment_does_not_fabricate_a_chart_when_data_page_has_no_data_object() -> None:
    ppt_ir = {"slides": [{"id": "S03", "slide_role": "data", "primary_expression": "data_visual", "title": "采用率", "message": "采用率提高。", "source_refs": [], "objects": []}]}

    enriched = enrich_ppt_ir(ppt_ir)

    assert enriched["slides"][0]["objects"] == []
    assert assess_ir_quality_floor(enriched)["status"] == "blocked"
