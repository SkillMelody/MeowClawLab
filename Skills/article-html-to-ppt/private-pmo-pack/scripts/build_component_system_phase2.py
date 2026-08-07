#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.renderer import build_phase2_p0_sample_deck
from components.tokens import resolve_tokens


DEFAULT_INPUT = ROOT / "examples" / "pmo-component-system-phase2-p0.json"
DEFAULT_SCHEMA = ROOT / "schemas" / "pmo-component-ir.schema.json"
DEFAULT_STYLE = ROOT / "contracts" / "mckinsey-pmo.style.json"
DEFAULT_OUTPUT = ROOT / "output" / "pmo-component-system-phase2-p0.pptx"
DEFAULT_MANIFEST = ROOT / "qa" / "component-system-phase2-p0-manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Phase 2 P0 PMO component-system sample deck.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--style", type=Path, default=DEFAULT_STYLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = load_json(args.input)
    schema = load_json(args.schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    legacy_style = load_json(args.style)
    tokens = resolve_tokens(legacy_style)
    build = build_phase2_p0_sample_deck(args.output, tokens=tokens, components=payload["components"])
    gates = {
        "four_components": [item["component"] for item in build["components"]]
        == ["kpi_status", "milestone", "risk_heat_map", "raci"],
        "four_slides": build["slide_count"] == 4,
        "zero_pictures": build["picture_count"] == 0,
        "native_table_present": build["table_count"] >= 1,
        "native_shapes_present": build["native_shape_count"] >= 90,
        "component_qa_passed": build["component_qa"]["passed"],
        "text_bounds_passed": build["text_bounds"]["passed"],
        "text_overflow_passed": build["text_overflow"]["passed"],
    }
    token_json = json.dumps(tokens, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest = {
        "status": "passed" if all(gates.values()) else "failed",
        "phase": 2,
        "priority": "P0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "schema": str(args.schema),
        "legacy_style": str(args.style),
        "token_system": tokens["meta"],
        "token_sha256": hashlib.sha256(token_json).hexdigest(),
        "output": str(args.output),
        "gates": gates,
        "build": build,
    }
    write_json(args.manifest, manifest)
    print(json.dumps({"status": manifest["status"], "output": str(args.output), "manifest": str(args.manifest)}))
    return 0 if manifest["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
