from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_contracts.py"
SCHEMA_DIR = ROOT / "schemas"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from visual_narrative.intent import validate_page_design_intent


@pytest.fixture
def valid_intent() -> dict:
    return {
        "schema_version": "1.0.0",
        "slide_id": "S01",
        "slide_role": "insight",
        "audience_question": "为什么现在要做这件事？",
        "message": "AI agent adoption 正在从试点转向系统化落地。",
        "evidence_refs": [{"source_id": "src-01", "locator": "p.12"}],
        "priority": "high",
        "primary_expression": "relationship_visual",
        "page_archetype": "architecture",
        "semantic_component": "layered_architecture",
        "visual_anchor": "three-layer system diagram",
        "layout": {"family": "single_canvas", "zones": ["title", "body", "footer"]},
        "density": {"level": "medium"},
        "editability": {"message_bearing": "native_preferred"},
        "delivery": {"allowed_fallbacks": ["native_diagram", "svg_component"]},
        "style_system": {"style_id": "azure-insight-architecture"},
        "forbidden_patterns": ["prompt_only"],
        "qa_focus": ["message_clarity", "editability"],
    }


def test_prompt_only_document_is_invalid() -> None:
    issues = validate_page_design_intent({"prompt": "做一页专业科技风架构图"})

    assert {issue["code"] for issue in issues} >= {
        "INTENT_SCHEMA_VERSION_REQUIRED",
        "INTENT_PRIMARY_EXPRESSION_REQUIRED",
        "INTENT_SEMANTIC_COMPONENT_REQUIRED",
    }


def test_native_required_rejects_generic_card_fallback(valid_intent: dict) -> None:
    valid_intent["editability"]["message_bearing"] = "native_required"
    valid_intent["delivery"]["allowed_fallbacks"] = ["generic_card"]

    issues = validate_page_design_intent(valid_intent)

    assert "INTENT_NATIVE_GENERIC_CARD_FORBIDDEN" in {issue["code"] for issue in issues}


def test_validate_contracts_accepts_repeated_page_design_intent(valid_intent: dict, tmp_path: Path) -> None:
    first = tmp_path / "intent-1.json"
    second = tmp_path / "intent-2.json"
    first.write_text(json.dumps(valid_intent), encoding="utf-8")
    second.write_text(json.dumps(valid_intent | {"slide_id": "S02"}), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--page-design-intent",
            str(first),
            "--page-design-intent",
            str(second),
            "--schema-dir",
            str(SCHEMA_DIR),
            "--strict",
            "--json-output",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert json.loads(result.stdout)["ok"] is True
