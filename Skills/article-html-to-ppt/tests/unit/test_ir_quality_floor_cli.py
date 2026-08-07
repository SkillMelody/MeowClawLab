from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ir_quality_floor.py"


def test_cli_writes_named_blocker_for_sparse_data_ir(tmp_path: Path) -> None:
    ppt_ir = {
        "slides": [
            {
                "id": "S03", "slide_role": "data", "primary_expression": "data_visual",
                "title": "采用率", "message": "采用率提高。", "source_refs": [], "objects": [],
            }
        ]
    }
    input_path = tmp_path / "ppt-ir.json"
    output_path = tmp_path / "quality-floor.json"
    input_path.write_text(json.dumps(ppt_ir), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--ppt-ir", str(input_path), "--output", str(output_path), "--strict"],
        text=True, capture_output=True, check=False,
    )

    assert completed.returncode == 2
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["status"] == "blocked"
    assert {issue["code"] for issue in report["issues"]} == {"IR_PRIMARY_DATA_OBJECT_REQUIRED", "IR_SUPPORTING_EVIDENCE_REQUIRED"}
