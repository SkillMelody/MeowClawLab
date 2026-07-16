from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIAGRAMS = ROOT / "tests" / "fixtures" / "diagrams"
VALIDATOR = ROOT / "scripts" / "validate_diagram_ir.py"
ANALYZER = ROOT / "scripts" / "analyze_diagram_complexity.py"
NORMALIZER = ROOT / "scripts" / "normalize_diagram_ir.py"
RECOMMENDER = ROOT / "scripts" / "recommend_diagram_layout.py"


def validate(path: Path) -> set[str]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--diagram", str(path), "--strict", "--json-output"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {issue["code"] for issue in json.loads(result.stdout)["issues"]}


def test_swimlane_requires_lane_groups() -> None:
    assert "DIAGRAM_REQUIRED_LANES_MISSING" in validate(DIAGRAMS / "invalid" / "invalid-swimlane.json")


def test_flywheel_requires_cycle() -> None:
    data = json.loads((DIAGRAMS / "flywheel.json").read_text(encoding="utf-8"))
    data["edges"] = data["edges"][:2]
    path = DIAGRAMS / "invalid" / "_tmp-flywheel-no-cycle.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    try:
        assert "DIAGRAM_CYCLE_REQUIRED" in validate(path)
    finally:
        path.unlink(missing_ok=True)


def test_decision_tree_requires_decision_node() -> None:
    data = json.loads((DIAGRAMS / "decision-tree.json").read_text(encoding="utf-8"))
    data["nodes"][0]["node_type"] = "stage"
    data["nodes"][0]["shape"] = "rounded_rect"
    path = DIAGRAMS / "invalid" / "_tmp-decision-no-node.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    try:
        assert "DIAGRAM_DECISION_NODE_MISSING" in validate(path)
    finally:
        path.unlink(missing_ok=True)


def test_empty_boundary_fails() -> None:
    assert "DIAGRAM_EMPTY_BOUNDARY" in validate(DIAGRAMS / "invalid" / "empty-boundary.json")


def test_connector_web_risk_is_detected() -> None:
    assert "DIAGRAM_CONNECTOR_WEB_RISK" in validate(DIAGRAMS / "invalid" / "connector-web-risk.json")


def test_native_delivery_contract_rejects_raster() -> None:
    data = json.loads((DIAGRAMS / "process-simple.json").read_text(encoding="utf-8"))
    data["delivery_contract"]["preferred_route"] = "raster_component"
    data["delivery_contract"]["raster_policy"]["allowed"] = True
    path = DIAGRAMS / "invalid" / "_tmp-raster-route.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    try:
        assert "DIAGRAM_NATIVE_ROUTE_RASTER_FORBIDDEN" in validate(path)
    finally:
        path.unlink(missing_ok=True)


def test_analyzer_reports_hybrid_for_complex_ecosystem() -> None:
    result = subprocess.run(
        [sys.executable, str(ANALYZER), "--diagram", str(DIAGRAMS / "ecosystem-complex.json"), "--json-output"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["recommended_layout"] == "zoned_ecosystem"
    assert payload["node_count"] >= 8


def test_layout_recommender_prefers_layered() -> None:
    result = subprocess.run(
        [sys.executable, str(RECOMMENDER), "--diagram", str(DIAGRAMS / "layered-agent-architecture.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout)["recommended_type"] == "layered_architecture"


def test_normalizer_writes_output(tmp_path: Path) -> None:
    output = tmp_path / "normalized.json"
    subprocess.run(
        [sys.executable, str(NORMALIZER), "--input", str(DIAGRAMS / "process-simple.json"), "--output", str(output)],
        cwd=ROOT,
        check=True,
    )
    assert json.loads(output.read_text(encoding="utf-8"))["reading_order"]
