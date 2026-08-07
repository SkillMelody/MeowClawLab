from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ir_enrichment import enrich_ppt_ir
from ir_quality_floor import assess_ir_quality_floor

TEMPLATE = ROOT / "templates" / "ppt-ir-source-bound-evidence-template.json"
SCHEMA = ROOT / "schemas" / "ppt-ir.schema.json"


def test_path_b_authoring_template_is_schema_valid_and_meets_quality_floor() -> None:
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate(template)
    report = assess_ir_quality_floor(enrich_ppt_ir(template))

    assert report == {"status": "passed", "issues": []}
