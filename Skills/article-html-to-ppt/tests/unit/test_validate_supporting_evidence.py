from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_contracts import validate_ppt_ir_semantics


def test_supporting_evidence_must_reference_a_declared_deck_source(tmp_path: Path) -> None:
    ppt_ir = {
        "sources": [{"source_id": "declared", "type": "report", "title": "来源"}],
        "slides": [{
            "id": "S02", "slide_role": "judgment", "title_role": "judgment", "judgment": "判断",
            "source_refs": [], "delivery_contract": {}, "objects": [],
            "supporting_evidence": [{
                "content": "独立证据", "source_refs": [{"source_id": "invented", "locator": "p.2", "claim_type": "direct"}],
            }],
        }],
    }

    errors = validate_ppt_ir_semantics(tmp_path / "ppt-ir.json", ppt_ir, assets=None, style=None)

    assert {error["code"] for error in errors} == {"SOURCE_REF_NOT_FOUND"}
    assert errors[0]["pointer"] == "/slides/0/supporting_evidence/0/source_refs/0/source_id"
