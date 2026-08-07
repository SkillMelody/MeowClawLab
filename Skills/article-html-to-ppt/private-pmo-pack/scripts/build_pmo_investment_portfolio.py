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
WORKSPACE = ROOT.parents[1]
DEFAULT_INPUT = ROOT / "examples" / "pmo-investment-portfolio.poster.json"
DEFAULT_SCHEMA = ROOT / "schemas" / "pmo-component-ir.schema.json"
DEFAULT_STYLE = ROOT / "contracts" / "mckinsey-pmo.style.json"
DEFAULT_DELIVERY = WORKSPACE / "deliverables" / "pptsmith-pmo-poster-doughnut"
DEFAULT_OUTPUT = DEFAULT_DELIVERY / "pptsmith-pmo-investment-portfolio.pptx"
DEFAULT_MANIFEST = DEFAULT_DELIVERY / "build-manifest.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.renderer import build_portfolio_doughnut_deck
from components.tokens import resolve_tokens


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the native PMO investment-portfolio poster slide.")
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
    tokens = resolve_tokens(
        legacy_style,
        overrides={
            "semantic": {
                "surface": {"canvas": "F4F2EE", "paper": "FBFAF8", "panel": "FFFFFF"},
                "text": {"title": "17212B", "body": "344054", "muted": "667085", "inverse": "FFFFFF"},
                "line": {"divider": "C9CED6", "soft": "DFE3E8", "annotation": "7B8491"},
                "sequence": {
                    "phase_1": "183B56",
                    "phase_2": "3F6D8A",
                    "phase_3": "5B83B5",
                    "phase_4": "7C8F78",
                    "phase_5": "A1A8B0"
                },
                "state": {
                    "healthy": "2F7A5C",
                    "watch": "D49A33",
                    "risk": "C64B4B",
                    "neutral": "77818D"
                }
            },
            "density": {"doughnut": {"max_categories": 6, "min_label_gap_in": 0.88, "max_label_chars": 31}},
            "typography": {
                "font": "Aptos",
                "roles": {
                    "slide_title": {"size_pt": 21, "bold": True},
                    "label": {"size_pt": 9, "bold": True},
                    "metric": {"size_pt": 25, "bold": True},
                    "footnote": {"size_pt": 8, "bold": False}
                }
            }
        },
    )
    component = payload["components"][0]
    build = build_portfolio_doughnut_deck(args.output, tokens=tokens, component=component)
    gates = {
        "single_slide": build["slide_count"] == 1,
        "five_categories": len(component["categories"]) == 5,
        "percentage_sum_100": abs(sum(item["value"] for item in component["categories"]) - 100.0) <= 0.001,
        "amount_sum_matches_budget": abs(
            sum(item["amount"] for item in component["categories"]) - component["budget_total"]
        ) <= component["amount_tolerance"],
        "four_leaders": build["components"][0]["leader_count"] == 4,
        "fifth_category_legend_fallback": build["components"][0]["legend_fallback_count"] == 1,
        "native_chart_present": build["chart_count"] == 1,
        "zero_pictures": build["picture_count"] == 0,
        "object_bounds_passed": build["object_bounds"]["passed"],
        "text_bounds_passed": build["text_bounds"]["passed"],
        "text_overflow_passed": build["text_overflow"]["passed"],
    }
    token_json = json.dumps(tokens, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest = {
        "status": "passed" if all(gates.values()) else "failed",
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
