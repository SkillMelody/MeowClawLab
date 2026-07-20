from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "qa"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ppt_qa.render_report import build_render_report
from ppt_qa.renderers.analysis import blank_score
from ppt_qa.renderers.base import RenderResult, select_renderer


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def issue_codes(report: dict[str, Any], section: str = "errors") -> set[str]:
    return {issue["code"] for issue in report[section]}


def make_busy_png(path: Path, *, width: int = 320, height: int = 180) -> Path:
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    colors = ["#1f2937", "#2563eb", "#ef4444", "#16a34a", "#f59e0b"]
    for index in range(18):
        x0 = (index % 6) * 52
        y0 = (index // 6) * 52
        draw.rectangle([x0 + 6, y0 + 8, x0 + 44, y0 + 42], fill=colors[index % len(colors)])
    draw.line([0, height - 1, width, 0], fill="#111827", width=4)
    image.save(path)
    return path


def test_auto_renderer_selection_is_unavailable_cleanly_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv("PPTSMITH_TEST_RENDERERS", "none")
    assert select_renderer("auto") is None


def test_explicit_unavailable_renderer_returns_none(monkeypatch) -> None:
    monkeypatch.setenv("PPTSMITH_TEST_RENDERERS", "none")
    assert select_renderer("libreoffice") is None


def test_blank_score_flags_white_and_allows_busy_png(tmp_path: Path) -> None:
    white = tmp_path / "white.png"
    Image.new("RGB", (320, 180), "white").save(white)
    busy = make_busy_png(tmp_path / "busy.png")
    assert blank_score(white) >= 0.995
    assert blank_score(busy) < 0.98


def test_synthetic_render_report_validates_against_schema(tmp_path: Path) -> None:
    image = make_busy_png(tmp_path / "slide-001.png")
    pdf = tmp_path / "deck.pdf"
    pdf.write_bytes(b"%PDF-1.7\n% synthetic test input\n")
    result = RenderResult(
        status="passed",
        engine="synthetic-test",
        engine_version="1.0",
        pdf_path=pdf,
        slide_images=[image],
        duration_seconds=0.1,
        slide_count_rendered=1,
    )
    report = build_render_report(tmp_path / "deck.pptx", result, started_at="2026-07-15T10:00:00+08:00", expected_slides=1)
    assert report["status"] == "passed"
    schema = load_json(ROOT / "schemas" / "render-report.schema.json")
    Draft202012Validator(schema).validate(report)


def test_slide_count_mismatch_fires_on_synthetic_report(tmp_path: Path) -> None:
    image = make_busy_png(tmp_path / "slide-001.png")
    pdf = tmp_path / "deck.pdf"
    pdf.write_bytes(b"%PDF-1.7\n% synthetic test input\n")
    result = RenderResult(
        status="passed",
        engine="synthetic-test",
        engine_version=None,
        pdf_path=pdf,
        slide_images=[image],
        duration_seconds=0.1,
        slide_count_rendered=1,
    )
    report = build_render_report(tmp_path / "deck.pptx", result, started_at="2026-07-15T10:00:00+08:00", expected_slides=2)
    assert "RENDER_SLIDE_COUNT_MISMATCH" in issue_codes(report)
    assert report["status"] == "partial"


def test_missing_image_check_fires_on_synthetic_report(tmp_path: Path) -> None:
    pdf = tmp_path / "deck.pdf"
    pdf.write_bytes(b"%PDF-1.7\n% synthetic test input\n")
    missing = tmp_path / "slide-001.png"
    result = RenderResult(
        status="passed",
        engine="synthetic-test",
        engine_version=None,
        pdf_path=pdf,
        slide_images=[missing],
        duration_seconds=0.1,
        slide_count_rendered=1,
    )
    report = build_render_report(tmp_path / "deck.pptx", result, started_at="2026-07-15T10:00:00+08:00", expected_slides=1)
    assert "RENDER_IMAGE_MISSING" in issue_codes(report)
    assert report["status"] == "partial"


def test_render_cli_writes_unavailable_report_for_valid_fixture(tmp_path: Path) -> None:
    output = tmp_path / "rendered"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "render_pptx.py"),
            str(FIXTURES / "valid-native-deck" / "deck.pptx"),
            "--engine",
            "auto",
            "--output",
            str(output),
            "--expected-slides",
            "1",
        ],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "PPTSMITH_TEST_RENDERERS": "none"},
    )
    assert result.returncode == 2, result.stderr
    report = load_json(output / "render-report.json")
    assert report["status"] == "unavailable"
    assert "RENDER_ENGINE_UNAVAILABLE" in issue_codes(report)
    schema = load_json(ROOT / "schemas" / "render-report.schema.json")
    Draft202012Validator(schema).validate(report)
