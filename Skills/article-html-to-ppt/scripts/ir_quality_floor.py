"""Minimum semantic completeness checks for Path B PPT IR."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DATA_COMPONENTS = {"bar_chart", "line_chart", "pie_chart", "native_table", "heat_matrix", "kpi_dashboard", "metric_card"}
SUPPORT_COMPONENTS = {"evidence_block", "metric_card", "comparison_card", "summary_action_card", "source_note"}
NAVIGATION_ROLES = {"cover", "agenda", "section", "reference"}


def _content_tokens(value: str) -> set[str]:
    return {char for char in value.replace(" ", "") if char.strip()}


def _is_near_duplicate(value: str, baseline: str) -> bool:
    candidate, existing = _content_tokens(value), _content_tokens(baseline)
    if not candidate or not existing:
        return False
    return len(candidate & existing) / len(candidate | existing) >= 0.75


def assess_ir_quality_floor(ppt_ir: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    for slide in ppt_ir.get("slides", []) or []:
        if not isinstance(slide, dict):
            continue
        slide_id = str(slide.get("id") or "unknown-slide")
        role = str(slide.get("slide_role") or "")
        expression = str(slide.get("primary_expression") or "")
        objects = [obj for obj in slide.get("objects", []) or [] if isinstance(obj, dict)]
        kinds = {str(obj.get("component_type") or obj.get("type") or "") for obj in objects}
        support_objects = [obj for obj in objects if str(obj.get("component_type") or obj.get("type") or "") in SUPPORT_COMPONENTS and obj.get("priority") != "primary"]
        support_count = len(support_objects)

        if role in NAVIGATION_ROLES:
            continue
        if role in {"data", "judgment"}:
            slide_claims = [str(slide.get(key) or "") for key in ("title", "judgment", "message")]
            for obj in support_objects:
                content = obj.get("content")
                if isinstance(content, str) and any(_is_near_duplicate(content, claim) for claim in slide_claims):
                    issues.append(_issue(slide_id, "IR_SUPPORTING_EVIDENCE_DUPLICATES_SLIDE_CLAIM", "Supporting evidence must add independently sourced information, not repeat the slide claim."))
        if role == "closing":

            actions = sum(1 for obj in objects if str(obj.get("component_type") or obj.get("type") or "") == "summary_action_card")
            if actions < 2:
                issues.append(_issue(slide_id, "IR_CLOSING_ACTIONS_INSUFFICIENT", "Closing slides require 2–4 actionable native objects."))
            continue
        if role == "data" or expression == "data_visual":
            data_objects = [obj for obj in objects if str(obj.get("component_type") or obj.get("type") or "") in DATA_COMPONENTS]
            if not data_objects:
                issues.append(_issue(slide_id, "IR_PRIMARY_DATA_OBJECT_REQUIRED", "Data slides require a source-backed native chart, table, matrix, or KPI dashboard."))
            for obj in data_objects:
                if not obj.get("source_refs"):
                    issues.append(_issue(slide_id, "IR_DATA_OBJECT_SOURCE_REQUIRED", "Each primary data object must carry its own source reference."))
                content = obj.get("content") if isinstance(obj.get("content"), dict) else {}
                categories = content.get("categories") if isinstance(content.get("categories"), list) else []
                series = content.get("series") if isinstance(content.get("series"), list) else []
                if categories and any(not isinstance(item, dict) or not isinstance(item.get("values"), list) or len(item["values"]) != len(categories) for item in series):
                    issues.append(_issue(slide_id, "IR_CHART_SERIES_LENGTH_INVALID", "Each chart series must have exactly one value per category."))
            if support_count < 1:
                issues.append(_issue(slide_id, "IR_SUPPORTING_EVIDENCE_REQUIRED", "Data slides require at least one supporting interpretation or evidence object."))
            elif not any(obj.get("source_refs") for obj in support_objects):
                issues.append(_issue(slide_id, "IR_SUPPORTING_OBJECT_SOURCE_REQUIRED", "Supporting evidence must carry an independent source reference."))
        elif role == "judgment":
            if support_count < 1:
                issues.append(_issue(slide_id, "IR_SUPPORTING_EVIDENCE_REQUIRED", "Judgment slides require at least one supporting evidence or interpretation object."))
            elif not any(obj.get("source_refs") for obj in support_objects):
                issues.append(_issue(slide_id, "IR_SUPPORTING_OBJECT_SOURCE_REQUIRED", "Supporting evidence must carry an independent source reference."))
    return {"status": "blocked" if issues else "passed", "issues": issues}


def _issue(slide_id: str, code: str, message: str) -> dict[str, str]:
    return {"slide_id": slide_id, "code": code, "severity": "blocked", "message": message}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Assess Path B PPT IR semantic completeness.")
    parser.add_argument("--ppt-ir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.ppt_ir.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("ppt-ir must be a JSON object")
        report = assess_ir_quality_floor(document)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 2 if args.strict and report["status"] != "passed" else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ir_quality_floor: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
