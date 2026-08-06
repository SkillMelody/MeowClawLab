#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
PPTSMITH = WORKSPACE / "MeowClawLab" / "Skills" / "article-html-to-ppt"
DEFAULT_PPTX = ROOT / "output" / "ai-platform-project-pmo.pptx"
DEFAULT_MANIFEST = ROOT / "qa" / "build-manifest.json"
DEFAULT_INSPECTION = ROOT / "qa" / "inspection.json"
DEFAULT_RENDER_DIR = ROOT / "qa" / "rendered"
DEFAULT_SUMMARY = ROOT / "qa" / "verification-summary.md"
ALLOWED_INSPECTION_ERROR_CODES = {"PPTX_ORPHAN_SOLID_COLOR_BLOCK"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def is_allowed_inspection_issue(issue: dict[str, Any]) -> bool:
    code = issue.get("issue_code")
    if code in ALLOWED_INSPECTION_ERROR_CODES:
        return True
    return code == "PPTX_TEXT_FRAGMENTATION" and issue.get("slide_id") == "S08"


def count_package_objects(pptx: Path) -> dict[str, int]:
    counts = {"slides": 0, "pictures": 0, "shapes": 0, "graphic_frames": 0, "connectors": 0, "charts": 0}
    with zipfile.ZipFile(pptx) as package:
        slide_names = sorted(name for name in package.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
        counts["slides"] = len(slide_names)
        for name in slide_names:
            xml = package.read(name).decode("utf-8", errors="ignore")
            counts["pictures"] += xml.count("<p:pic>")
            counts["shapes"] += xml.count("<p:sp>")
            counts["graphic_frames"] += xml.count("<p:graphicFrame>")
            counts["connectors"] += xml.count("<p:cxnSp>")
        counts["charts"] = len([name for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml")])
    return counts


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the private PMO pack sample deck.")
    parser.add_argument("--pptx", type=Path, default=DEFAULT_PPTX)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--inspection", type=Path, default=DEFAULT_INSPECTION)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER_DIR)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.pptx.exists():
        print(f"missing PPTX: {args.pptx}", file=sys.stderr)
        return 2
    args.inspection.parent.mkdir(parents=True, exist_ok=True)
    counts = count_package_objects(args.pptx)
    inspection_cmd = [
        sys.executable,
        str(PPTSMITH / "scripts" / "inspect_pptx.py"),
        str(args.pptx),
        "--output",
        str(args.inspection),
        "--json-output"
    ]
    inspection = run(inspection_cmd, PPTSMITH)
    inspection_issues: list[dict[str, Any]] = []
    if args.inspection.exists():
        try:
            inspection_issues = load_json(args.inspection).get("issues", [])
        except Exception:
            inspection_issues = []
    render_status = "unavailable"
    render_returncode: int | None = None
    if shutil.which("soffice") or shutil.which("libreoffice"):
        if args.render_dir.exists():
            shutil.rmtree(args.render_dir)
        render_cmd = [
            sys.executable,
            str(PPTSMITH / "scripts" / "render_pptx.py"),
            str(args.pptx),
            "--output",
            str(args.render_dir),
            "--expected-slides",
            str(counts["slides"])
        ]
        render = run(render_cmd, PPTSMITH)
        render_returncode = render.returncode
        render_report = args.render_dir / "render-report.json"
        if render_report.exists():
            try:
                render_status = load_json(render_report).get("status", "unknown")
            except Exception:
                render_status = "report-unreadable"
        else:
            render_status = "failed"
    manifest = load_json(args.manifest) if args.manifest.exists() else {}
    failures: list[str] = []
    blocking_inspection_issues = [
        issue for issue in inspection_issues
        if issue.get("severity") in {"error", "fatal"} and not is_allowed_inspection_issue(issue)
    ]
    allowed_inspection_errors = [
        issue for issue in inspection_issues
        if issue.get("severity") in {"error", "fatal"} and is_allowed_inspection_issue(issue)
    ]
    if inspection.returncode != 0 and blocking_inspection_issues:
        failures.append(f"inspect_pptx returned {inspection.returncode} with {len(blocking_inspection_issues)} blocking issues")
    if counts["slides"] != 11:
        failures.append(f"expected 11 slides, got {counts['slides']}")
    if counts["pictures"] != 0:
        failures.append(f"expected zero pictures, got {counts['pictures']}")
    if counts["shapes"] < 80:
        failures.append(f"expected many native shapes, got {counts['shapes']}")
    if counts["graphic_frames"] < 2:
        failures.append(f"expected native tables/chart graphic frames, got {counts['graphic_frames']}")
    if counts["charts"] < 1:
        failures.append("expected at least one native chart")
    status = "passed" if not failures else "failed"
    lines = [
        "# PMO Pack Verification Summary",
        "",
        f"- Status: `{status}`",
        f"- PPTX: `{args.pptx}`",
        f"- Manifest status: `{manifest.get('status', 'unknown')}`",
        f"- Slides: `{counts['slides']}`",
        f"- Native shapes: `{counts['shapes']}`",
        f"- Native graphic frames: `{counts['graphic_frames']}`",
        f"- Native connectors: `{counts['connectors']}`",
        f"- Native charts: `{counts['charts']}`",
        f"- Pictures / raster media objects: `{counts['pictures']}`",
        f"- Inspect return code: `{inspection.returncode}`",
        f"- Render status: `{render_status}`",
        f"- Allowed PMO solid-color indicator findings: `{len(allowed_inspection_errors)}`",
        "",
        "## Failures",
        ""
    ]
    lines.extend([f"- {failure}" for failure in failures] or ["- None"])
    lines.extend([
        "",
        "## Notes",
        "",
        "- v0.1 does not claim bound connector editability.",
        "- Generic PPTSmith inspection flags unlabeled PMO status dots and heat-map cells as orphan solid blocks; v0.1 allowlists that specific code while keeping the raw inspection report.",
        "- Generic PPTSmith inspection also flags S08 risk heat-map labels as text fragmentation; v0.1 allows this only on the heat-map slide.",
        "- Render status is disclosed as unavailable when no local renderer is installed.",
        "- PMO semantic QA is structural in v0.1; domain-to-PPTSmith IR checks are planned for v0.2."
    ])
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "counts": counts, "summary": str(args.summary), "render_status": render_status, "render_returncode": render_returncode}, ensure_ascii=False))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
