from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_diagram_ir.py"
CONTRACT_VALIDATOR = ROOT / "scripts" / "validate_contracts.py"
DIAGRAMS = ROOT / "tests" / "fixtures" / "diagrams"
STYLE = ROOT / "tests" / "fixtures" / "styles" / "technical-blueprint.json"
PPT_IR = ROOT / "tests" / "fixtures" / "technical-agent" / "ppt-ir.json"


def run_validator(path: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--diagram", str(path), "--strict", "--json-output"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return json.loads(result.stdout)


def test_valid_diagram_fixtures_pass() -> None:
    for path in sorted(DIAGRAMS.glob("*.json")):
        payload = run_validator(path)
        assert payload["ok"], f"{path}: {payload}"


def test_unknown_edge_node_fails() -> None:
    payload = run_validator(DIAGRAMS / "invalid" / "unknown-node.json")
    assert "DIAGRAM_UNKNOWN_TARGET_NODE" in {issue["code"] for issue in payload["issues"]}


def test_broken_main_path_fails() -> None:
    payload = run_validator(DIAGRAMS / "invalid" / "broken-main-path.json")
    assert "DIAGRAM_MAIN_PATH_BROKEN" in {issue["code"] for issue in payload["issues"]}


def test_all_primary_edges_warns() -> None:
    payload = run_validator(DIAGRAMS / "invalid" / "all-primary-edges.json")
    assert "DIAGRAM_ALL_EDGES_PRIMARY" in {issue["code"] for issue in payload["issues"]}


def test_ppt_ir_diagram_reference_exists() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CONTRACT_VALIDATOR),
            "--ppt-ir",
            str(PPT_IR),
            "--style",
            str(STYLE),
            "--diagram",
            str(DIAGRAMS / "layered-agent-architecture.json"),
            "--strict",
            "--json-output",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"], payload
