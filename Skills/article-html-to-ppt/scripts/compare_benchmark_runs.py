#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_RANK = {
    "passed": 0,
    "warning": 1,
    "manual_review_required": 2,
    "failed": 3,
}


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def index_results(report: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    indexed = {}
    for result in report.get("results", []):
        if not isinstance(result, dict):
            continue
        indexed[(str(result.get("case_id")), int(result.get("iteration") or 1))] = result
    return indexed


def compare_reports(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base = index_results(baseline)
    cand = index_results(candidate)
    regressions = []
    improvements = []
    unchanged = []
    for key in sorted(set(base) | set(cand)):
        base_item = base.get(key)
        cand_item = cand.get(key)
        if base_item is None:
            improvements.append({"case_id": key[0], "iteration": key[1], "change": "new_candidate_result"})
            continue
        if cand_item is None:
            regressions.append({"case_id": key[0], "iteration": key[1], "change": "missing_candidate_result"})
            continue
        base_score = base_item.get("total_score")
        cand_score = cand_item.get("total_score")
        base_status = str(base_item.get("overall_status"))
        cand_status = str(cand_item.get("overall_status"))
        status_delta = STATUS_RANK.get(cand_status, 2) - STATUS_RANK.get(base_status, 2)
        score_delta = None
        if isinstance(base_score, int) and isinstance(cand_score, int):
            score_delta = cand_score - base_score
        change = {
            "case_id": key[0],
            "iteration": key[1],
            "baseline_status": base_status,
            "candidate_status": cand_status,
            "baseline_score": base_score,
            "candidate_score": cand_score,
            "score_delta": score_delta,
            "status_delta": status_delta,
        }
        if status_delta > 0 or (score_delta is not None and score_delta < 0):
            regressions.append(change)
        elif status_delta < 0 or (score_delta is not None and score_delta > 0):
            improvements.append(change)
        else:
            unchanged.append(change)
    return {
        "schema_version": "1.0",
        "generated_at": iso_now(),
        "baseline_run_id": baseline.get("run_id"),
        "candidate_run_id": candidate.get("run_id"),
        "summary": {
            "baseline_result_count": len(base),
            "candidate_result_count": len(cand),
            "regression_count": len(regressions),
            "improvement_count": len(improvements),
            "unchanged_count": len(unchanged),
        },
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Benchmark Comparison",
        "",
        f"- Baseline: `{report.get('baseline_run_id')}`",
        f"- Candidate: `{report.get('candidate_run_id')}`",
        f"- Regressions: {report['summary']['regression_count']}",
        f"- Improvements: {report['summary']['improvement_count']}",
        "",
    ]
    if report["regressions"]:
        lines.extend(["## Regressions", ""])
        for item in report["regressions"]:
            lines.append(f"- `{item['case_id']}` repeat {item['iteration']}: {item.get('baseline_status')} -> {item.get('candidate_status')}, score delta {item.get('score_delta')}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two benchmark report JSON files and flag regressions.")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = compare_reports(load_json(args.baseline), load_json(args.candidate))
    write_json(report, args.output)
    if args.markdown:
        write_markdown(report, args.markdown)
    return 1 if report["summary"]["regression_count"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
