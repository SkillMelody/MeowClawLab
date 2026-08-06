#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.tokens import resolve_tokens
from decision_support.pipeline import analyze_decision
from decision_support.presentation import render_decision_deck
from decision_support.serialization import load_decision_case


def _primitive(value: Any) -> Any:
    if is_dataclass(value):
        return {item.name: _primitive(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _primitive(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_primitive(item) for item in value]
    if isinstance(value, (Decimal, date, datetime, Enum)):
        return value.value if isinstance(value, Enum) else str(value)
    return value


def main() -> int:
    output_dir = ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    case_path = ROOT / "examples" / "pmo-decision-support-gold.json"
    case = load_decision_case(case_path)
    package = analyze_decision(case)
    analysis_path = output_dir / "pmo-decision-support-gold-analysis.json"
    deck_path = output_dir / "pmo-decision-support-gold.pptx"
    manifest_path = output_dir / "pmo-decision-support-gold-manifest.json"
    analysis_path.write_text(json.dumps(_primitive(package), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = render_decision_deck(package, deck_path, resolve_tokens())
    manifest = {
        "case": str(case_path),
        "analysis": str(analysis_path),
        "deck": str(deck_path),
        "input_hash": package.input_hash,
        "route_action": package.route.route_action.value,
        "recommendation_status": package.recommendation.status.value,
        "page_types": list(result.page_types),
        "slide_count": result.slide_count,
        "native_shape_count": result.native_shape_count,
        "text_shape_count": result.text_shape_count,
        "table_count": result.table_count,
        "chart_count": result.chart_count,
        "connector_count": result.connector_count,
        "picture_count": result.picture_count,
        "media_count": result.media_count,
        "out_of_bounds_text": list(result.out_of_bounds_text),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
