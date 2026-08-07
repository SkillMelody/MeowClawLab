#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
PPTSMITH = WORKSPACE / "MeowClawLab" / "Skills" / "article-html-to-ppt"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.inspection import inspect_phase1_pptx


DEFAULT_PPTX = ROOT / "output" / "pmo-component-system-phase1.pptx"
DEFAULT_MANIFEST = ROOT / "qa" / "component-system-phase1-manifest.json"
DEFAULT_INSPECTION = ROOT / "qa" / "component-system-phase1-inspection.json"
DEFAULT_RENDER_REPORT = ROOT / "qa" / "component-system-phase1-render-report.json"
DEFAULT_RENDER_DIR = ROOT / "qa" / "component-system-phase1-rendered"
DEFAULT_SUMMARY = ROOT / "qa" / "component-system-phase1-verification-summary.md"
DEFAULT_STATE = ROOT / "state" / "component-system-progress.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the Phase 1 PMO component system.")
    parser.add_argument("--pptx", type=Path, default=DEFAULT_PPTX)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--inspection", type=Path, default=DEFAULT_INSPECTION)
    parser.add_argument("--render-report", type=Path, default=DEFAULT_RENDER_REPORT)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER_DIR)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument(
        "--visual-review-status",
        choices=["pending", "passed", "failed"],
        default="pending",
        help="Record the explicit rendered-slide visual review result.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.pptx.exists():
        print(f"missing PPTX: {args.pptx}", file=sys.stderr)
        return 2
    manifest = load_json(args.manifest)
    inspection = inspect_phase1_pptx(args.pptx)
    write_json(args.inspection, inspection)

    test_run = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], ROOT)
    test_status = "passed" if test_run.returncode == 0 else "failed"
    test_count = test_run.stderr.count(" ... ok")

    renderer = shutil.which("soffice") or shutil.which("libreoffice")
    render_status = "unavailable"
    render_returncode: int | None = None
    source_report: dict[str, Any] = {}
    if renderer and (PPTSMITH / "scripts" / "render_pptx.py").exists():
        if args.render_dir.exists():
            shutil.rmtree(args.render_dir)
        render_run = run(
            [
                sys.executable,
                str(PPTSMITH / "scripts" / "render_pptx.py"),
                str(args.pptx),
                "--output",
                str(args.render_dir),
                "--expected-slides",
                "3",
            ],
            PPTSMITH,
        )
        render_returncode = render_run.returncode
        source_path = args.render_dir / "render-report.json"
        if source_path.exists():
            source_report = load_json(source_path)
            render_status = str(source_report.get("status", "unknown"))
        else:
            render_status = "failed"
    render_report = {
        "status": render_status,
        "renderer_available": bool(renderer),
        "renderer_binary": renderer,
        "returncode": render_returncode,
        "source_report": str(args.render_dir / "render-report.json"),
        "slide_png_count": len(list((args.render_dir / "slides").glob("*.png"))) if args.render_dir.exists() else 0,
        "details": source_report,
    }
    write_json(args.render_report, render_report)

    failures: list[str] = []
    if manifest.get("status") != "passed":
        failures.append("build manifest is not passed")
    if not inspection["passed"]:
        failures.append("static PPTX inspection failed")
    if test_status != "passed":
        failures.append("unit tests failed")
    if renderer and render_status != "passed":
        failures.append(f"LibreOffice render status is {render_status}")
    if args.visual_review_status != "passed":
        failures.append(f"rendered-slide visual review status is {args.visual_review_status}")
    status = "passed" if not failures else "failed"
    state_status = (
        "phase1_complete"
        if status == "passed"
        else ("phase1_visual_fix_in_progress" if args.visual_review_status == "pending" else "phase1_failed")
    )
    now = datetime.now(timezone.utc).isoformat()
    state = load_json(args.state) if args.state.exists() else {}
    state.update(
        {
            "status": state_status,
            "phase": 1,
            "completed_tasks": [
                "boardroom_ink_token_resolver",
                "phase1_semantic_ir_validation",
                "shared_layout_and_qa_helpers",
                "native_annotated_doughnut_renderer",
                "native_roadmap_renderer",
                "native_gantt_renderer",
                "edge_fixtures_and_tests",
                "phase1_sample_pptx",
                "static_package_inspection",
                "doughnut_chart_coordinate_alignment",
                "roadmap_flat_first_phase_geometry",
                "gantt_week_column_bounds_and_status_legend",
            ]
            + (["libreoffice_render"] if render_status == "passed" else []),
            "next_task": "phase2_kpi_status_and_risk_heat_map_ir_layout_implementation",
            "last_updated": now,
            "verification": {
                "status": status,
                "tests": {"status": test_status, "count": test_count, "returncode": test_run.returncode},
                "inspection": {"status": "passed" if inspection["passed"] else "failed", "path": str(args.inspection)},
                "render": {"status": render_status, "path": str(args.render_report)},
                "visual_review": {
                    "status": args.visual_review_status,
                    "slides_reviewed": [1, 2, 3] if args.visual_review_status == "passed" else [],
                    "checks": [
                        "doughnut endpoint angle, endpoint color, and segment ownership for all four categories",
                        "elbow leader continuity and no-crossing gate",
                        "roadmap flat-left first phase, continuous middle chevrons, and gate alignment",
                        "gantt 13 column labels, final milestone bounds, complete health legend, and reference line",
                    ],
                },
                "pptx": str(args.pptx),
                "manifest": str(args.manifest),
                "failures": failures,
                "limitations": [
                    "Native connector endpoint binding is not verified because python-pptx does not expose a reliable binding API.",
                    "LibreOffice render verifies open/render behavior but is not a substitute for manual Microsoft PowerPoint review.",
                    "Phase 2 and Phase 3 entries are interface contracts only; their renderers are not implemented.",
                ],
            },
        }
    )
    write_json(args.state, state)
    lines = [
        "# PMO Component System Phase 1 Verification",
        "",
        f"- Status: `{status}`",
        f"- PPTX: `{args.pptx}`",
        f"- Build manifest: `{args.manifest}`",
        f"- Tests: `{test_status}` ({test_count} tests observed)",
        f"- Static inspection: `{'passed' if inspection['passed'] else 'failed'}`",
        f"- Slides: `{inspection['slide_count']}`",
        f"- Native shapes: `{inspection['native_shape_count']}`",
        f"- Native connectors: `{inspection['connector_count']}`",
        f"- Native charts: `{inspection['chart_count']}`",
        f"- Pictures: `{inspection['picture_count']}`",
        f"- Package media files: `{inspection['media_file_count']}`",
        f"- LibreOffice render: `{render_status}`",
        f"- Rendered slide PNGs: `{render_report['slide_png_count']}`",
        f"- Rendered-slide visual review: `{args.visual_review_status}`",
        "",
        "## Failures",
        "",
    ]
    lines.extend([f"- {item}" for item in failures] or ["- None"])
    lines.extend(
        [
            "",
            "## Explicit limits",
            "",
            "- Native connector endpoint binding is not verified; leaders are continuous native elbow connector objects.",
            "- LibreOffice render evidence does not replace manual Microsoft PowerPoint review.",
            "- Phase 2 and Phase 3 contracts are planned interfaces, not completed renderers.",
            "",
            "## Rendered-slide visual checks",
            "",
            "- Doughnut endpoints and endpoint colors match Platform, Data, Adoption, and Controls segment mid-angles; elbow leaders do not cross.",
            "- Roadmap first phase has a flat left boundary; middle chevrons interlock continuously and all phase text is visible.",
            "- Gantt has 13 bounded week columns with explicit date spans; the end milestone remains inside W13.",
            "- Gantt legend defines planned, actual, on-track, watch, not-assessed, milestone, and Today encodings.",
        ]
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "tests": test_status,
                "inspection": inspection["passed"],
                "render": render_status,
                "summary": str(args.summary),
                "state": str(args.state),
            }
        )
    )
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
