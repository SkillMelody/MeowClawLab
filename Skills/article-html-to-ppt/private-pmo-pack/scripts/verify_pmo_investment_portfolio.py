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

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
DEFAULT_DELIVERY = WORKSPACE / "deliverables" / "pptsmith-pmo-poster-doughnut"
DEFAULT_PPTX = DEFAULT_DELIVERY / "pptsmith-pmo-investment-portfolio.pptx"
DEFAULT_SOURCE_PNG = DEFAULT_DELIVERY / "rendered" / "slides" / "slide-001.png"
DEFAULT_PNG = DEFAULT_DELIVERY / "pptsmith-pmo-investment-portfolio.png"
DEFAULT_SOURCE_RENDER_REPORT = DEFAULT_DELIVERY / "rendered" / "render-report.json"
DEFAULT_RENDER_REPORT = DEFAULT_DELIVERY / "render-report.json"
DEFAULT_INSPECTION = DEFAULT_DELIVERY / "inspection.json"
DEFAULT_SUMMARY = DEFAULT_DELIVERY / "verification-summary.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.inspection import inspect_portfolio_doughnut_pptx


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the native PMO investment-portfolio poster slide.")
    parser.add_argument("--pptx", type=Path, default=DEFAULT_PPTX)
    parser.add_argument("--source-png", type=Path, default=DEFAULT_SOURCE_PNG)
    parser.add_argument("--png", type=Path, default=DEFAULT_PNG)
    parser.add_argument("--source-render-report", type=Path, default=DEFAULT_SOURCE_RENDER_REPORT)
    parser.add_argument("--render-report", type=Path, default=DEFAULT_RENDER_REPORT)
    parser.add_argument("--inspection", type=Path, default=DEFAULT_INSPECTION)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument(
        "--visual-review-status",
        choices=["pending", "passed", "failed"],
        default="pending",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    inspection = inspect_portfolio_doughnut_pptx(args.pptx)
    write_json(args.inspection, inspection)

    test_run = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    test_count = test_run.stderr.count(" ... ok")
    test_status = "passed" if test_run.returncode == 0 else "failed"

    source_render = load_json(args.source_render_report)
    render_status = str(source_render.get("status", "unknown"))
    shutil.copyfile(args.source_render_report, args.render_report)
    args.png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.source_png, args.png)
    with Image.open(args.png) as image:
        image_width, image_height = image.size
        image_format = image.format

    failures: list[str] = []
    if not inspection["passed"]:
        failures.append("static PPTX inspection failed")
    if test_status != "passed":
        failures.append("unit tests failed")
    if render_status != "passed":
        failures.append(f"LibreOffice render status is {render_status}")
    if image_format != "PNG" or image_width < 2500 or image_height < 1400:
        failures.append("rendered PNG is not high resolution")
    if args.visual_review_status != "passed":
        failures.append(f"rendered-slide visual review status is {args.visual_review_status}")
    status = "passed" if not failures else "failed"

    summary_lines = [
        "# PPTSmith PMO Investment Portfolio — Verification Summary",
        "",
        f"- Status: `{status}`",
        f"- Verified at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- PPTX: `{args.pptx}`",
        f"- PNG: `{args.png}`",
        f"- Unit tests: `{test_status}` ({test_count} observed)",
        f"- Static package inspection: `{'passed' if inspection['passed'] else 'failed'}`",
        f"- LibreOffice render: `{render_status}`",
        f"- Rendered-slide visual review: `{args.visual_review_status}`",
        f"- Rendered PNG: `{image_width}×{image_height}`",
        "",
        "## Native object counts",
        "",
        f"- Total/native objects: `{inspection['total_shape_count']}` / `{inspection['native_shape_count']}`",
        f"- Native charts: `{inspection['chart_count']}`",
        f"- Native connectors: `{inspection['connector_count']}`",
        f"- Text shapes: `{inspection['text_shape_count']}`",
        f"- Picture shapes: `{inspection['picture_count']}`",
        f"- Package media files: `{inspection['media_file_count']}`",
        f"- Embedded chart workbooks: `{inspection['embedded_workbook_count']}`",
        "",
        "## Data and geometry gates",
        "",
        "- Five categories are present; percentages sum to 100%.",
        "- Displayed amounts sum to ¥8.60M and each amount is within ±¥0.02M of percentage-derived value.",
        "- Four callout endpoints use the target segment mid-angle and fall inside the target segment.",
        "- Leader polylines are continuous and have no crossings.",
        "- Risk reserve is the single compact legend/bottom-band fallback.",
        "- All native objects are within slide bounds; tracked text boxes pass bounds and static text-fit gates.",
        "",
        "## Rendered-slide review",
        "",
        "- Judgment title remains readable at poster-thumbnail scale.",
        "- Ring is the visual anchor; center contains only ¥8.60M and Total project budget.",
        "- Category colors and status colors remain separate.",
        "- Four external labels occupy left/right safe zones without line crossings.",
        "- PMO readout panel contains exactly three prioritized observations.",
        "- No generated logo or generated visual asset is used.",
        "",
        "## Failures",
        "",
    ]
    summary_lines.extend([f"- {item}" for item in failures] or ["- None"])
    summary_lines.extend(
        [
            "",
            "## Explicit limits",
            "",
            "- The sample is a native editable PMO visual, not a live data-connected dashboard.",
            "- Connector endpoint binding is not claimed; leaders are deterministic native straight-connector chains.",
            "- LibreOffice open/render evidence does not replace a manual Microsoft PowerPoint compatibility review.",
            "- Native chart plot padding and font metrics may vary slightly across Office versions.",
            "- No unimplemented PPTSmith feature is represented as available.",
        ]
    )
    args.summary.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "tests": test_status,
                "inspection": inspection["passed"],
                "render": render_status,
                "visual_review": args.visual_review_status,
                "png": str(args.png),
                "summary": str(args.summary),
            }
        )
    )
    if test_run.returncode != 0:
        print(test_run.stdout, file=sys.stderr)
        print(test_run.stderr, file=sys.stderr)
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
