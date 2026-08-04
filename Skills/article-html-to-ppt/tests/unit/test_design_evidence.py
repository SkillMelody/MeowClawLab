from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from visual_narrative.design_evidence import build_design_evidence


def test_product_prd_evidence_preserves_sources_and_requires_both_prototypes() -> None:
    result = build_design_evidence(
        {
            "source_id": "meowclaw-workbench-prd",
            "design_tokens": [
                {"value": "meowclaw / paper / night", "kind": "theme", "locator": "6.1 Workspace"},
                {"value": "screen-bottom persistent dock", "kind": "layout", "locator": "3.1"},
            ],
            "ui_spaces": [
                {"name": "Canvas", "locator": "5"},
                {"name": "Inspector", "locator": "5"},
                {"name": "Dock", "locator": "3.1"},
            ],
            "interactions": [
                {"trigger": "select article", "state": "inline chat bubble", "locator": "8.2"},
                {"trigger": "publish", "state": "failed on 40164", "locator": "11"},
            ],
        }
    )

    assert result["schema_version"] == "1.0"
    assert {item["category"] for item in result["items"]} == {"token", "ui_space", "interaction"}
    assert all(item["source"]["source_id"] == "meowclaw-workbench-prd" for item in result["items"])
    assert all(item["source"]["directness"] == "direct" for item in result["items"])
    assert result["coverage_matrix"]["product_ui_overview"]["required"] is True
    assert result["coverage_matrix"]["interaction_storyboard"]["required"] is True
    assert result["status"] == "blocked"
    assert "PRODUCT_PRD_REQUIRED_PROTOTYPES_UNCONSUMED" in result["blocking_codes"]


def test_product_prd_without_spaces_or_interactions_does_not_require_prototypes() -> None:
    result = build_design_evidence({"source_id": "minimal-prd", "design_tokens": []})

    assert result["coverage_matrix"]["product_ui_overview"]["required"] is False
    assert result["coverage_matrix"]["interaction_storyboard"]["required"] is False
    assert result["status"] == "ready"


def test_cli_writes_machine_readable_design_evidence(tmp_path: Path) -> None:
    analysis = tmp_path / "product-prd.json"
    output = tmp_path / "design-evidence.json"
    analysis.write_text(json.dumps({"source_id": "prd", "ui_spaces": [{"name": "Canvas", "locator": "5"}]}), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "extract_design_evidence.py"), "--analysis", str(analysis), "--output", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(output.read_text(encoding="utf-8"))
    assert evidence["coverage_matrix"]["product_ui_overview"]["required"] is True
