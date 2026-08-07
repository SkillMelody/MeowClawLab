from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "route_audience.py"
SCHEMA = ROOT / "schemas" / "audience-route.schema.json"


def test_route_audience_cli_writes_a_schema_valid_decision(tmp_path: Path) -> None:
    brief = tmp_path / "brief.json"
    output = tmp_path / "audience-route.json"
    brief.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "source_id": "prd-checkout-v3",
                "primary_audience": ["product_manager", "engineer", "designer", "tester"],
                "delivery_objective": "review_and_align",
                "source_material_type": "prd",
                "evidence_profile": ["scope_boundary", "user_flow", "acceptance_criteria"],
                "industry_compliance_context": ["consumer_software"],
                "delivery_scenario": "prd_review",
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--brief", str(brief), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(output.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(result)
    assert result["selected_route"] == "product_prd"


def test_route_audience_cli_fails_closed_for_a_valid_but_ambiguous_brief(tmp_path: Path) -> None:
    brief = tmp_path / "brief.json"
    output = tmp_path / "audience-route.json"
    brief.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "source_id": "undetermined-document",
                "primary_audience": ["analyst"],
                "delivery_objective": "communicate_findings",
                "source_material_type": "document",
                "evidence_profile": ["notes"],
                "industry_compliance_context": [],
                "delivery_scenario": "unknown",
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--brief", str(brief), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["status"] == "blocked"
    assert "AUDIENCE_ROUTE_AMBIGUOUS" in result["blocking_codes"]
