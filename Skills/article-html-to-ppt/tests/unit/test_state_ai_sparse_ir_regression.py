from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ir_enrichment import enrich_ppt_ir
from ir_quality_floor import assess_ir_quality_floor

FIXTURE = ROOT / "tests" / "fixtures" / "path-b-quality-floor" / "state-of-ai-sparse-ppt-ir.json"


def test_state_of_ai_sparse_path_b_ir_is_fail_closed_before_delivery() -> None:
    ppt_ir = json.loads(FIXTURE.read_text(encoding="utf-8"))

    report = assess_ir_quality_floor(enrich_ppt_ir(ppt_ir))

    assert report["status"] == "blocked"
    assert {issue["slide_id"] for issue in report["issues"]} == {"S04", "S05", "S06", "S08"}
    assert {issue["code"] for issue in report["issues"]} == {"IR_SUPPORTING_EVIDENCE_REQUIRED"}
