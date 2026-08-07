from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "ppt-ir.schema.json"


def _slide() -> dict:
    return {
        "id": "S03", "index": 3, "slide_role": "data", "title_role": "judgment",
        "title": "采用率提高", "message": "核心结论", "audience_question": "说明什么？",
        "source_refs": [], "primary_expression": "data_visual", "supporting_expressions": ["interpretation"],
        "primary_anchor": "chart", "delivery_contract": {"preferred_route": "native_ppt", "editable_core": [], "raster_allowance": [], "forbidden_raster": []},
        "supporting_evidence": [{
            "content": "仅三分之一组织实现规模化。",
            "source_refs": [{"source_id": "report", "locator": "Exhibit 2", "claim_type": "direct"}],
        }],
    }


def test_supporting_evidence_is_a_formal_source_bound_ir_field() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate({
        "schema_version": "2.0", "deck": {"id": "deck", "title": "deck", "source_type": "report", "audience": "管理层", "purpose": "决策", "language": "zh-CN", "aspect_ratio": "16:9", "production_profile": "standard", "logical_slide_count": 1},
        "sources": [{"source_id": "report", "type": "report", "title": "报告"}],
        "style_contract_ref": "style.json", "asset_manifest_ref": "assets.json", "slides": [_slide()],
    })


def test_supporting_evidence_rejects_missing_source_reference() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    slide = _slide()
    slide["supporting_evidence"] = [{"content": "无来源的补充判断"}]
    document = {
        "schema_version": "2.0", "deck": {"id": "deck", "title": "deck", "source_type": "report", "audience": "管理层", "purpose": "决策", "language": "zh-CN", "aspect_ratio": "16:9", "production_profile": "standard", "logical_slide_count": 1},
        "sources": [{"source_id": "report", "type": "report", "title": "报告"}],
        "style_contract_ref": "style.json", "asset_manifest_ref": "assets.json", "slides": [slide],
    }

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(document)
