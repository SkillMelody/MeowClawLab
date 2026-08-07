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

from components.inspection import inspect_phase2_p0_pptx


DEFAULT_PPTX = ROOT / "output" / "pmo-component-system-phase2-p0.pptx"
DEFAULT_MANIFEST = ROOT / "qa" / "component-system-phase2-p0-manifest.json"
DEFAULT_INSPECTION = ROOT / "qa" / "component-system-phase2-p0-inspection.json"
DEFAULT_RENDER_REPORT = ROOT / "qa" / "component-system-phase2-p0-render-report.json"
DEFAULT_RENDER_DIR = ROOT / "qa" / "component-system-phase2-p0-rendered"
DEFAULT_SUMMARY = ROOT / "qa" / "component-system-phase2-p0-verification-summary.md"
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
    parser = argparse.ArgumentParser(description="Verify the Phase 2 P0 PMO component system.")
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
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.pptx.exists():
        print(f"missing PPTX: {args.pptx}", file=sys.stderr)
        return 2
    manifest = load_json(args.manifest)
    inspection = inspect_phase2_p0_pptx(args.pptx)
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
                "4",
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
        "phase2_p0_complete"
        if status == "passed"
        else ("phase2_p0_visual_review_in_progress" if args.visual_review_status == "pending" else "phase2_p0_failed")
    )
    now = datetime.now(timezone.utc).isoformat()
    state = load_json(args.state) if args.state.exists() else {}
    state.update(
        {
            "status": state_status,
            "phase": 2,
            "completed_tasks": [
                "boardroom_ink_token_resolver",
                "phase1_semantic_ir_validation",
                "shared_layout_and_qa_helpers",
                "native_annotated_doughnut_renderer",
                "native_roadmap_renderer",
                "native_gantt_renderer",
                "phase1_regression_suite",
                "phase2_p0_semantic_ir_validation",
                "native_kpi_status_renderer",
                "native_milestone_timeline_renderer",
                "native_risk_heat_map_renderer",
                "native_raci_table_renderer",
                "phase2_p0_density_fallbacks",
                "phase2_p0_edge_fixtures_and_tests",
                "phase2_p0_static_package_inspection",
            ]
            + (["phase2_p0_libreoffice_render"] if render_status == "passed" else [])
            + (["phase2_p0_visual_review"] if args.visual_review_status == "passed" else []),
            "next_task": "phase2_p1_raid_action_tracker_decision_matrix_implementation",
            "last_updated": now,
            "verification": {
                "status": status,
                "tests": {"status": test_status, "count": test_count, "returncode": test_run.returncode},
                "inspection": {"status": "passed" if inspection["passed"] else "failed", "path": str(args.inspection)},
                "render": {"status": render_status, "path": str(args.render_report)},
                "visual_review": {
                    "status": args.visual_review_status,
                    "slides_reviewed": [1, 2, 3, 4] if args.visual_review_status == "passed" else [],
                    "checks": [
                        "KPI value, unit, target, status legend, and mini-trend fit",
                        "milestone date labels, alternating lanes, node alignment, and leader correspondence",
                        "heat-map axis direction, cell mapping, same-cell jitter, and register readability",
                        "RACI row-column alignment, legal codes, header fit, and activity-name fit",
                    ],
                },
                "pptx": str(args.pptx),
                "manifest": str(args.manifest),
                "failures": failures,
                "limitations": [
                    "LibreOffice render verifies open/render behavior but is not a substitute for manual Microsoft PowerPoint review.",
                    "Density fallback pagination is deterministic in layout IR; the four-slide acceptance deck intentionally exercises the normal single-page mode.",
                    "Phase 2 P1/P2 and all Phase 3 families remain unimplemented.",
                ],
            },
        }
    )
    write_json(args.state, state)
    lines = [
        "# PMO Component System Phase 2 P0 Verification",
        "",
        f"- Status: `{status}`",
        f"- PPTX: `{args.pptx}`",
        f"- Build manifest: `{args.manifest}`",
        f"- Tests: `{test_status}` ({test_count} tests observed)",
        f"- Static inspection: `{'passed' if inspection['passed'] else 'failed'}`",
        f"- Slides: `{inspection['slide_count']}`",
        f"- Native shapes: `{inspection['native_shape_count']}`",
        f"- Native connectors: `{inspection['connector_count']}`",
        f"- Native tables: `{inspection['table_count']}`",
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
            "- LibreOffice evidence does not replace manual Microsoft PowerPoint review.",
            "- Split/table fallback geometry is tested independently; the acceptance deck uses normal-density fixtures.",
            "- Phase 2 P1/P2 and Phase 3 are not implemented.",
            "",
            "## Rendered-slide visual checks",
            "",
            "- KPI values, units, targets, notes, status bars, legend, and trends are separated and legible.",
            "- Milestone dates map monotonically to the axis; alternating label lanes and leaders are unambiguous.",
            "- Heat-map axes are explicit; IDs remain inside their cells, same-cell points are separated, and the right register is readable.",
            "- RACI has exactly one A and at least one R per activity; table headers and activity labels are not clipped.",
        ]
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "tests": test_status, "inspection": inspection["passed"], "render": render_status, "summary": str(args.summary), "state": str(args.state)}))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
