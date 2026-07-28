from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "scripts" / "run_pipeline.py"
FIXTURES = ROOT / "tests" / "fixtures" / "v2-acceptance"


def write_json(path: Path, document: dict) -> None:
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def storyline(*, request_revision: bool = False) -> dict:
    slides = [
        ("S01", "cover", [], "supporting"),
        ("S02", "relationship", ["hierarchy", "drill_down"], "supporting"),
        ("S03", "data", [], "key"),
        ("S04", "architecture", ["layer", "system_boundary"], "supporting"),
        ("S05", "data", [], "supporting"),
        ("S06", "diagram", ["phase", "milestone"], "key"),
        ("S07", "comparison", [], "supporting"),
        ("S08", "roadmap", ["phase", "roadmap"], "supporting"),
        ("S09", "closing", [], "supporting"),
    ]
    document = {
        "title": "PPTSmith 视觉叙事验收",
        "slides": [
            {
                "id": slide_id,
                "role": role,
                "message": f"{slide_id} 的判断信息保持不变。",
                "evidence_refs": [{"source_id": "src-001", "locator": slide_id}],
                "relationships": relationships,
                "priority": priority,
            }
            for slide_id, role, relationships, priority in slides
        ],
    }
    if request_revision:
        document["revision_observations"] = [
            {"slide_id": "S03", "codes": ["VISUAL_WEAK_PRIMARY_ANCHOR"]}
        ]
    return document


def run_phase1_pipeline(tmp_path: Path, *, request_revision: bool = False) -> subprocess.CompletedProcess[str]:
    content_analysis = tmp_path / "content-analysis.json"
    storyline_path = tmp_path / "storyline.json"
    write_json(
        content_analysis,
        {
            "evidence_types": ["statistics", "comparison", "trend"],
            "relationship_types": ["hierarchy"],
        },
    )
    write_json(storyline_path, storyline(request_revision=request_revision))
    return subprocess.run(
        [
            sys.executable,
            str(PIPELINE),
            "--requirements",
            str(FIXTURES / "requirements-fast.json"),
            "--ppt-ir",
            str(FIXTURES / "ppt-ir.json"),
            "--style",
            str(FIXTURES / "style-contract-editorial.json"),
            "--content-analysis",
            str(content_analysis),
            "--storyline",
            str(storyline_path),
            "--builder",
            "pptxgenjs",
            "--profile",
            "fast",
            "--work-dir",
            str(tmp_path / ".ppt-work"),
            "--output-dir",
            str(tmp_path / "delivery"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_visual_narrative_stages_run_before_delivery_resolution(tmp_path: Path) -> None:
    completed = run_phase1_pipeline(tmp_path)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    state = load_json(work / "state.json")
    assert state["stage_order"].index("route_task") < state["stage_order"].index(
        "resolve_delivery"
    )
    assert state["stage_order"].index("plan_visual_narrative") < state[
        "stage_order"
    ].index("build")
    assert state["stage_order"].index("deck_rhythm") < state["stage_order"].index(
        "build"
    )
    assert state["visual_revision_count"] == 0
    for name in (
        "task-route.json",
        "visual-plan.json",
        "deck-rhythm-report.json",
        "visual-revision-request.json",
    ):
        assert (work / "contracts" / name).is_file()


def test_visual_revision_is_applied_at_most_once_and_keeps_first_pass_evidence(
    tmp_path: Path,
) -> None:
    completed = run_phase1_pipeline(tmp_path, request_revision=True)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    state = load_json(work / "state.json")
    request = load_json(work / "contracts" / "visual-revision-request.json")
    plan = load_json(work / "contracts" / "visual-plan.json")
    assert request["status"] == "revision_required"
    assert state["visual_revision_count"] == 1
    assert state["stage_order"].count("visual_revision") == 1
    assert (work / "revisions" / "initial" / "deck.pptx").is_file()
    revised_slide = next(slide for slide in plan["slides"] if slide["slide_id"] == "S03")
    assert revised_slide["revision"]["iteration"] == 1
    assert revised_slide["message"] == "S03 的判断信息保持不变。"
    assert revised_slide["evidence_refs"] == [
        {"source_id": "src-001", "locator": "S03"}
    ]
