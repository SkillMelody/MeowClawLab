from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "scripts" / "run_pipeline.py"
FIXTURES = ROOT / "tests" / "fixtures" / "v2-acceptance"


def _write_json(path: Path, document: dict) -> None:
    path.write_text(json.dumps(document), encoding="utf-8")


def _run_visual_pipeline(tmp_path: Path, brief: dict | None) -> subprocess.CompletedProcess[str]:
    analysis = tmp_path / "content-analysis.json"
    storyline = tmp_path / "storyline.json"
    _write_json(analysis, {"evidence_types": ["statistics", "comparison", "trend"], "relationship_types": []})
    _write_json(
        storyline,
        {
            "title": "路由门禁测试",
            "slides": [
                {
                    "id": "S01",
                    "role": "cover",
                    "message": "测试",
                    "evidence_refs": [{"source_id": "src-001", "locator": "1"}],
                    "relationships": [],
                    "priority": "supporting",
                }
            ],
        },
    )
    command = [
        sys.executable,
        str(PIPELINE),
        "--requirements", str(FIXTURES / "requirements-fast.json"),
        "--ppt-ir", str(FIXTURES / "ppt-ir.json"),
        "--style", str(FIXTURES / "style-contract-editorial.json"),
        "--content-analysis", str(analysis),
        "--storyline", str(storyline),
        "--builder", "python_pptx",
        "--profile", "fast",
        "--work-dir", str(tmp_path / ".ppt-work"),
        "--output-dir", str(tmp_path / "delivery"),
    ]
    if brief is not None:
        brief_path = tmp_path / "source-context-brief.json"
        _write_json(brief_path, brief)
        command.extend(["--source-context-brief", str(brief_path)])
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def test_visual_pipeline_requires_a_source_context_brief(tmp_path: Path) -> None:
    completed = _run_visual_pipeline(tmp_path, brief=None)

    assert completed.returncode != 0
    assert "--source-context-brief is required when visual narrative inputs are provided" in completed.stderr


def test_ambiguous_source_context_blocks_before_delivery_build(tmp_path: Path) -> None:
    completed = _run_visual_pipeline(
        tmp_path,
        {
            "schema_version": "1.0",
            "source_id": "undetermined-document",
            "primary_audience": ["analyst"],
            "delivery_objective": "communicate_findings",
            "source_material_type": "document",
            "evidence_profile": ["notes"],
            "industry_compliance_context": [],
            "delivery_scenario": "unknown",
        },
    )

    assert completed.returncode != 0
    state = json.loads((tmp_path / ".ppt-work" / "state.json").read_text(encoding="utf-8"))
    assert state["failed_stage"] == "route_audience"
    assert "AUDIENCE_ROUTE_AMBIGUOUS" in state["error"]
    assert not (tmp_path / ".ppt-work" / "builds").exists()
