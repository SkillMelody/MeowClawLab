from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builders.python_pptx_adapter import PythonPptxAdapter
from ppt_qa.package_inspector import inspect_package

STYLE = ROOT / "tests" / "fixtures" / "styles" / "consulting-light.json"
BUILD = ROOT / "scripts" / "build_deck.py"


def sample_ppt_ir() -> dict:
    return {
        "schema_version": "2.0",
        "deck": {
            "id": "builder-smoke",
            "title": "Builder Smoke",
            "source_type": "article",
            "audience": "builders",
            "purpose": "smoke test",
            "language": "en",
            "presentation_context": "internal",
            "aspect_ratio": "16:9",
            "production_profile": "fast",
            "target_builder": "python_pptx",
            "logical_slide_count": 2,
        },
        "sources": [{"source_id": "src-001", "type": "article", "title": "Fixture"}],
        "style_contract_ref": "style-contract.json",
        "asset_manifest_ref": "asset-manifest.json",
        "slides": [
            {
                "id": "S01",
                "index": 1,
                "slide_role": "cover",
                "title_role": "navigation",
                "title": "Builder Smoke",
                "judgment": None,
                "message": "Native PPTX smoke test.",
                "audience_question": "Can the adapter create a deck?",
                "source_refs": [],
                "primary_expression": "textual_argument",
                "supporting_expressions": [],
                "primary_anchor": "title",
                "objects": [],
                "delivery_contract": {"preferred_route": "native_ppt", "editable_core": ["title"], "raster_allowance": [], "forbidden_raster": ["title"]},
            },
            {
                "id": "S02",
                "index": 2,
                "slide_role": "judgment",
                "title_role": "judgment",
                "title": "Text and tables are native",
                "judgment": "The minimal builder creates editable text and table objects.",
                "message": "Use it as the first v2 runtime gate.",
                "audience_question": "What does the minimal builder cover?",
                "source_refs": [{"source_id": "src-001", "locator": "s1", "claim_type": "direct"}],
                "primary_expression": "table_matrix",
                "supporting_expressions": [],
                "primary_anchor": "table",
                "objects": [
                    {
                        "id": "tbl-1",
                        "type": "table",
                        "component_type": "native_table",
                        "semantic_role": "evidence",
                        "content": {"headers": ["Capability", "Status"], "body": [["Text", "Native"], ["Table", "Native"]]},
                        "source_refs": [],
                        "editability": "native_required",
                    }
                ],
                "delivery_contract": {"preferred_route": "native_table", "editable_core": ["headers", "cells"], "raster_allowance": [], "forbidden_raster": ["tbl-1"]},
            },
        ],
    }


def sample_delivery_plan() -> dict:
    return {
        "schema_version": "1.0",
        "ppt_ir_ref": "ppt-ir.json",
        "style_contract_ref": "style-contract.json",
        "component_registry_ref": "references/component-registry.json",
        "capability_report_ref": None,
        "profile": "fast",
        "builder": {"requested": "python_pptx", "selected": "python_pptx", "version": None, "selection_score": 1, "selection_reasons": ["TEST"]},
        "slides": [
            {
                "slide_id": "S02",
                "objects": [
                    {
                        "slide_id": "S02",
                        "object_id": "tbl-1",
                        "component_type": "native_table",
                        "preferred_route": "native_table",
                        "selected_route": "native_table",
                        "decision": "selected",
                        "reason_codes": [],
                        "editable_core": ["headers", "cells"],
                        "rasterized_parts": [],
                        "svg_parts": [],
                        "native_overlay_parts": [],
                        "qa_checks": ["TABLE_NATIVE"],
                        "fallback_chain": [],
                    }
                ],
            }
        ],
        "summary": {"total_objects": 1, "fallback_count": 0, "unsupported_count": 0, "risk_codes": []},
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_python_pptx_adapter_builds_inspectable_deck(tmp_path: Path) -> None:
    adapter = PythonPptxAdapter()
    plan = adapter.plan(sample_ppt_ir(), json.loads(STYLE.read_text(encoding="utf-8")), sample_delivery_plan())
    result = adapter.build(plan, tmp_path)
    assert result.status == "created"
    assert result.pptx is not None
    inspection = inspect_package(Path(result.pptx), ppt_ir=sample_ppt_ir())
    assert inspection.status == "passed"
    assert inspection.slide_count == 2


def test_build_deck_cli_writes_manifest(tmp_path: Path) -> None:
    ppt_ir = tmp_path / "ppt-ir.json"
    style = tmp_path / "style-contract.json"
    delivery = tmp_path / "delivery-plan.json"
    manifest = tmp_path / "build-manifest.json"
    output = tmp_path / "out"
    write_json(ppt_ir, sample_ppt_ir())
    style.write_text(STYLE.read_text(encoding="utf-8"), encoding="utf-8")
    write_json(delivery, sample_delivery_plan())

    result = subprocess.run(
        [
            sys.executable,
            str(BUILD),
            "--ppt-ir",
            str(ppt_ir),
            "--style",
            str(style),
            "--delivery",
            str(delivery),
            "--builder",
            "python_pptx",
            "--output-dir",
            str(output),
            "--build-manifest",
            str(manifest),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (output / "deck.pptx").exists()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads((ROOT / "schemas" / "build-manifest.schema.json").read_text(encoding="utf-8"))).validate(data)
    assert data["status"] == "created"
    assert data["outputs"]["deck"] == "deck.pptx"
