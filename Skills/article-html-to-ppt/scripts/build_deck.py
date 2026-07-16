#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builders.registry import get_builder


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def selected_builder(delivery_plan: dict[str, Any], requested: str) -> str:
    if requested != "auto":
        return requested
    builder = delivery_plan.get("builder") if isinstance(delivery_plan.get("builder"), dict) else {}
    selected = builder.get("selected")
    return selected if isinstance(selected, str) and selected != "unknown" else "python_pptx"


def build_manifest(
    *,
    ppt_ir: dict[str, Any],
    delivery_plan: dict[str, Any],
    builder_name: str,
    result: Any,
    output_dir: Path,
    ppt_ir_ref: str,
    style_ref: str,
    delivery_ref: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    deck_id = ppt_ir.get("deck", {}).get("id", "deck")
    profile = delivery_plan.get("profile") or ppt_ir.get("deck", {}).get("production_profile", "standard")
    status = "created" if result.status == "created" else "failed"
    return {
        "schema_version": "2.0",
        "build_id": f"build-{deck_id}-{now}",
        "deck_id": deck_id,
        "profile": profile,
        "builder": delivery_plan.get("builder", {"requested": builder_name, "selected": builder_name, "version": None, "selection_score": 0, "selection_reasons": []}),
        "builder_profile": builder_name,
        "status": status,
        "production_profile_ref": None,
        "resume_from": None,
        "last_successful_stage": "built" if status == "created" else None,
        "failed_stage": None if status == "created" else "build",
        "contract_refs": {
            "ppt_ir": ppt_ir_ref,
            "style_contract": style_ref,
            "asset_manifest": ppt_ir.get("asset_manifest_ref", "asset-manifest.json"),
            "delivery_plan": delivery_ref,
            "production_profile": None,
            "capability_report": delivery_plan.get("capability_report_ref"),
            "qa_report": None,
        },
        "environment": {"capability_report": delivery_plan.get("capability_report_ref")},
        "stages": {"planned": True, "built": status == "created", "rendered": False, "read_back": False, "verified": False},
        "outputs": {"deck": str(Path(result.pptx).relative_to(output_dir)) if result.pptx else ""},
        "metrics": {
            "slide_count": len(ppt_ir.get("slides", []) or []),
            "object_count": len(result.object_results),
            "fallback_count": len(result.fallbacks),
        },
        "fallbacks": result.fallbacks,
        "warnings": result.warnings,
        "errors": [{"message": error} if isinstance(error, str) else error for error in result.errors],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a PPTX deck from PPT IR and Delivery Plan.")
    parser.add_argument("--ppt-ir", type=Path, required=True)
    parser.add_argument("--style", type=Path, required=True)
    parser.add_argument("--delivery", type=Path, required=True)
    parser.add_argument("--builder", default="auto")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--build-manifest", type=Path, required=True)
    parser.add_argument("--json-output", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        ppt_ir = load_json(args.ppt_ir)
        style = load_json(args.style)
        delivery = load_json(args.delivery)
        builder_name = selected_builder(delivery, args.builder)
        adapter = get_builder(builder_name)
        if adapter is None:
            raise ValueError(f"Unknown builder: {builder_name}")
        plan = adapter.plan(ppt_ir, style, delivery)
        result = adapter.build(plan, args.output_dir)
        manifest = build_manifest(
            ppt_ir=ppt_ir,
            delivery_plan=delivery,
            builder_name=builder_name,
            result=result,
            output_dir=args.output_dir,
            ppt_ir_ref=str(args.ppt_ir),
            style_ref=str(args.style),
            delivery_ref=str(args.delivery),
        )
        write_json(args.build_manifest, manifest)
        if args.json_output:
            print(json.dumps({"result": result.__dict__, "build_manifest": manifest}, ensure_ascii=False, indent=2))
        return 0 if result.status == "created" else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"build_deck: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
