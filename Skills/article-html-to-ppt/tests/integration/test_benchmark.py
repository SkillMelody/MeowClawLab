from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "benchmark"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_benchmark_fixture_catalog_has_required_categories_and_cases() -> None:
    cases = [load_json(path) for path in sorted(FIXTURES.glob("*/case.json"))]
    categories = {case["category"] for case in cases}
    assert len(cases) >= 10
    assert {"editorial_article", "product_report", "technical_agent", "design_spec", "anti_regression"} <= categories
    baseline_categories = {
        case["category"]
        for case in cases
        if (FIXTURES / case["case_id"] / "baseline" / "deck.pptx").exists()
    }
    assert len(baseline_categories) >= 3


def test_benchmark_case_fixtures_validate_against_schema() -> None:
    schema = load_json(ROOT / "schemas" / "benchmark-case.schema.json")
    validator = Draft202012Validator(schema)
    for path in sorted(FIXTURES.glob("*/case.json")):
        validator.validate(load_json(path))


def test_benchmark_smoke_run_writes_valid_json_and_markdown(tmp_path: Path) -> None:
    output = tmp_path / "benchmark-report.json"
    markdown = tmp_path / "benchmark-report.md"
    result = run_cli(
        str(ROOT / "scripts" / "benchmark.py"),
        "--cases-dir",
        str(FIXTURES),
        "--output-dir",
        str(tmp_path),
        "--run-id",
        "integration",
        "--category",
        "technical_agent",
        "--repeat",
        "1",
        "--use-reference-rubric",
        "--json",
        str(output),
        "--markdown",
        str(markdown),
    )
    assert result.returncode == 0, result.stderr
    report = load_json(output)
    schema = load_json(ROOT / "schemas" / "benchmark-report.schema.json")
    Draft202012Validator(schema).validate(report)
    assert report["summary"]["case_count"] == 2
    assert markdown.exists()
    assert all(item["rubric_score"] for item in report["results"])


def test_compare_benchmark_runs_detects_score_regression(tmp_path: Path) -> None:
    baseline = {
        "schema_version": "1.0",
        "run_id": "baseline",
        "summary": {},
        "results": [{"case_id": "case-a", "iteration": 1, "overall_status": "passed", "total_score": 16}],
    }
    candidate = {
        "schema_version": "1.0",
        "run_id": "candidate",
        "summary": {},
        "results": [{"case_id": "case-a", "iteration": 1, "overall_status": "passed", "total_score": 14}],
    }
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    output = tmp_path / "comparison.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
    result = run_cli(
        str(ROOT / "scripts" / "compare_benchmark_runs.py"),
        "--baseline",
        str(baseline_path),
        "--candidate",
        str(candidate_path),
        "--output",
        str(output),
    )
    assert result.returncode == 1
    report = load_json(output)
    assert report["summary"]["regression_count"] == 1
    assert report["regressions"][0]["score_delta"] == -2
