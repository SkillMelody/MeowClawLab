#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from score_deck import build_rubric_score, load_json, write_json

BENCHMARK_SCHEMA_VERSION = "1.0"


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def discover_cases(cases_dir: Path, categories: Optional[set[str]] = None, case_ids: Optional[set[str]] = None) -> list[Path]:
    paths = sorted(cases_dir.glob("*/case.json"))
    selected = []
    for path in paths:
        case = load_json(path)
        assert case is not None
        if categories and case.get("category") not in categories:
            continue
        if case_ids and case.get("case_id") not in case_ids:
            continue
        selected.append(path)
    return selected


def validate_json(schema_path: Path, data: dict[str, Any]) -> list[str]:
    schema = load_json(schema_path)
    assert schema is not None
    validator = Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(data), key=str)]


def run_case(case_path: Path, output_dir: Path, iteration: int, *, render: bool, use_reference_rubric: bool) -> dict[str, Any]:
    case = load_json(case_path)
    assert case is not None
    case_id = str(case["case_id"])
    case_dir = case_path.parent
    run_dir = output_dir / case_id / f"repeat-{iteration:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    case_validation_errors = validate_json(ROOT / "schemas" / "benchmark-case.schema.json", case)
    baseline_dir = case_dir / "baseline"
    pptx = baseline_dir / "deck.pptx"
    expected_ppt_ir = _case_file(case_dir, case.get("expected_ppt_ir"))
    expected_style = _case_file(case_dir, case.get("expected_style_contract"))
    build_manifest = baseline_dir / "build-manifest.json"
    qa_report = baseline_dir / "qa-report.json"
    verification_status = "unavailable"
    verification_exit_code: Optional[int] = None
    verification_output = run_dir / "qa-report.json"
    if pptx.exists() and expected_ppt_ir and expected_ppt_ir.exists():
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "verify_deck.py"),
            str(pptx),
            "--ppt-ir",
            str(expected_ppt_ir),
            "--output",
            str(verification_output),
            "--benchmark-case-id",
            case_id,
        ]
        if expected_style and expected_style.exists():
            cmd.extend(["--style", str(expected_style)])
        if build_manifest.exists():
            cmd.extend(["--build", str(build_manifest)])
        if render:
            cmd.append("--render")
        completed = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        verification_exit_code = completed.returncode
        verification_status = "completed" if verification_output.exists() else "failed"
        if verification_output.exists():
            qa_report = verification_output
        (run_dir / "verify_deck.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    score_output = run_dir / "rubric-score.json"
    score = build_rubric_score(
        case=case,
        case_path=case_path,
        ppt_ir=load_json(expected_ppt_ir) if expected_ppt_ir and expected_ppt_ir.exists() else None,
        qa_report=load_json(qa_report) if qa_report.exists() else None,
        build_manifest=load_json(build_manifest) if build_manifest.exists() else None,
        use_reference_rubric=use_reference_rubric,
    )
    write_json(score, score_output)
    score_validation_errors = validate_json(ROOT / "schemas" / "rubric-score.schema.json", score)
    return {
        "case_id": case_id,
        "category": case["category"],
        "iteration": iteration,
        "case_path": str(case_path),
        "baseline_available": pptx.exists(),
        "verification_status": verification_status,
        "verification_exit_code": verification_exit_code,
        "qa_report": str(qa_report) if qa_report.exists() else None,
        "rubric_score": str(score_output),
        "hard_gate_status": score["hard_gate_status"],
        "rubric_quality_status": score["rubric_quality_status"],
        "overall_status": score["overall_status"],
        "manual_review_required": score["manual_review_required"],
        "total_score": score["total_score"],
        "validation_errors": case_validation_errors + score_validation_errors,
    }


def build_report(results: list[dict[str, Any]], output_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    case_ids = sorted({str(result["case_id"]) for result in results})
    categories = sorted({str(result["category"]) for result in results})
    status_counts: dict[str, int] = {}
    for result in results:
        status = str(result["overall_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "generated_at": iso_now(),
        "run_id": args.run_id,
        "cases_dir": str(args.cases_dir),
        "output_dir": str(output_dir),
        "repeat": args.repeat,
        "renderer": "requested" if args.render else "not_requested",
        "summary": {
            "case_count": len(case_ids),
            "result_count": len(results),
            "categories": categories,
            "status_counts": status_counts,
            "manual_review_required_count": len([item for item in results if item.get("manual_review_required")]),
            "regression_count": 0,
        },
        "results": results,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Benchmark Report",
        "",
        f"- Run ID: `{report['run_id']}`",
        f"- Cases: {report['summary']['case_count']}",
        f"- Results: {report['summary']['result_count']}",
        f"- Categories: {', '.join(report['summary']['categories'])}",
        f"- Manual review required: {report['summary']['manual_review_required_count']}",
        "",
        "| Case | Category | Iteration | Status | Hard Gate | Rubric | Score |",
        "| --- | --- | ---: | --- | --- | --- | ---: |",
    ]
    for result in report["results"]:
        score = result["total_score"] if result["total_score"] is not None else "n/a"
        lines.append(
            "| {case_id} | {category} | {iteration} | {overall_status} | {hard_gate_status} | {rubric_quality_status} | {score} |".format(
                **result,
                score=score,
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _case_file(case_dir: Path, value: Any) -> Optional[Path]:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else case_dir / path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run article-html-to-ppt benchmark cases against available baseline artifacts.")
    parser.add_argument("--cases-dir", type=Path, default=ROOT / "tests" / "fixtures" / "benchmark")
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".ppt-work" / "benchmark")
    parser.add_argument("--run-id", default=f"benchmark-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    parser.add_argument("--category", action="append", default=[])
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--use-reference-rubric", action="store_true")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.repeat <= 0:
        print("--repeat must be positive", file=sys.stderr)
        return 3
    categories = set(args.category) if args.category else None
    case_ids = set(args.case_id) if args.case_id else None
    output_dir = args.output_dir / args.run_id
    case_paths = discover_cases(args.cases_dir, categories, case_ids)
    results = []
    for iteration in range(1, args.repeat + 1):
        for case_path in case_paths:
            results.append(run_case(case_path, output_dir, iteration, render=args.render, use_reference_rubric=args.use_reference_rubric))
    report = build_report(results, output_dir, args)
    json_output = args.json or output_dir / "benchmark-report.json"
    md_output = args.markdown or output_dir / "benchmark-report.md"
    write_json(report, json_output)
    write_markdown(report, md_output)
    validation_errors = validate_json(ROOT / "schemas" / "benchmark-report.schema.json", report)
    if validation_errors:
        for error in validation_errors:
            print(error, file=sys.stderr)
        return 3
    return 1 if any(result["overall_status"] == "failed" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
