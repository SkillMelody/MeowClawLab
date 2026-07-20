from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "qa"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ppt_qa.verifier import build_verification_report, run_structural_inspection


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_deck.py"), *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )


def test_verification_report_passes_without_render_when_not_required() -> None:
    fixture = FIXTURES / "valid-native-deck"
    ppt_ir = load_json(fixture / "ppt-ir.json")
    report = build_verification_report(
        fixture / "deck.pptx",
        ppt_ir=ppt_ir,
        style=load_json(fixture / "style-contract.json"),
        delivery=load_json(fixture / "delivery-plan.json"),
        ppt_ir_ref=str(fixture / "ppt-ir.json"),
    )
    assert report["status"] == "pass"
    assert report["build_status_cap"] == "read_back"
    schema = load_json(ROOT / "schemas" / "qa-report.schema.json")
    Draft202012Validator(schema).validate(report)


def test_verification_report_normalizes_structural_errors() -> None:
    fixture = FIXTURES / "whole-slide-image"
    report = build_verification_report(
        fixture / "deck.pptx",
        ppt_ir=load_json(fixture / "ppt-ir.json"),
        style=load_json(fixture / "style-contract.json"),
        delivery=load_json(fixture / "delivery-plan.json"),
    )
    issue = next(item for item in report["issues"] if item["issue_code"] == "PPTX_WHOLE_SLIDE_RASTER")
    assert report["status"] == "fail"
    assert issue["severity"] == "error"
    assert issue["compatibility_severity"] == "fail"


def test_verify_cli_returns_unavailable_when_render_requested(tmp_path: Path) -> None:
    fixture = FIXTURES / "valid-native-deck"
    output = tmp_path / "qa-report.json"
    result = run_cli(
        str(fixture / "deck.pptx"),
        "--ppt-ir",
        str(fixture / "ppt-ir.json"),
        "--style",
        str(fixture / "style-contract.json"),
        "--delivery",
        str(fixture / "delivery-plan.json"),
        "--render",
        "--output",
        str(output),
        env={**os.environ, "PPTSMITH_TEST_RENDERERS": "none"},
    )
    assert result.returncode == 2, result.stderr
    report = load_json(output)
    assert report["status"] == "warning"
    assert report["build_status_cap"] == "created"
    assert any(issue["issue_code"] == "RENDER_ENGINE_UNAVAILABLE" for issue in report["issues"])


def test_verify_cli_returns_failure_for_structural_qa_error(tmp_path: Path) -> None:
    fixture = FIXTURES / "whole-slide-image"
    output = tmp_path / "qa-report.json"
    result = run_cli(
        str(fixture / "deck.pptx"),
        "--ppt-ir",
        str(fixture / "ppt-ir.json"),
        "--style",
        str(fixture / "style-contract.json"),
        "--delivery",
        str(fixture / "delivery-plan.json"),
        "--output",
        str(output),
    )
    assert result.returncode == 1, result.stderr
    assert load_json(output)["status"] == "fail"


def test_repair_cli_writes_conservative_report(tmp_path: Path) -> None:
    fixture = FIXTURES / "whole-slide-image"
    qa_report = tmp_path / "qa-report.json"
    initial = build_verification_report(
        fixture / "deck.pptx",
        inspection_report=run_structural_inspection(
            fixture / "deck.pptx",
            ppt_ir=load_json(fixture / "ppt-ir.json"),
            style=load_json(fixture / "style-contract.json"),
            delivery=load_json(fixture / "delivery-plan.json"),
        ),
    )
    qa_report.write_text(json.dumps(initial, indent=2), encoding="utf-8")
    repaired = tmp_path / "repaired.pptx"
    repair_report = tmp_path / "repair-report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "repair_deck.py"),
            str(fixture / "deck.pptx"),
            "--qa-report",
            str(qa_report),
            "--output-pptx",
            str(repaired),
            "--output-report",
            str(repair_report),
        ],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 1
    report = load_json(repair_report)
    assert repaired.exists()
    assert report["status"] == "no_safe_repairs_available"
    assert report["remaining_issues"]
    assert report["iterations"][0]["attempted_repairs"][0]["status"] == "skipped_unregistered"
