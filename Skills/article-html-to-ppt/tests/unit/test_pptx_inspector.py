from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "qa"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ppt_qa.package_inspector import inspect_package
from ppt_qa.report import inspection_to_dict
from ppt_qa.slide_inspector import inspect_slides
GENERATOR = FIXTURES / "generate_fixtures.py"
spec = importlib.util.spec_from_file_location("qa_fixture_generator", GENERATOR)
assert spec is not None and spec.loader is not None
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
save_whole_slide_image = generator.save_whole_slide_image


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def inspect_fixture(name: str) -> dict[str, Any]:
    fixture = FIXTURES / name
    package = inspect_package(fixture / "deck.pptx", ppt_ir=load_json(fixture / "ppt-ir.json"))
    if not any(issue.severity == "fatal" for issue in package.issues):
        package = inspect_slides(
            fixture / "deck.pptx",
            package,
            ppt_ir=load_json(fixture / "ppt-ir.json"),
            style=load_json(fixture / "style-contract.json"),
            delivery=load_json(fixture / "delivery-plan.json"),
        )
    return inspection_to_dict(package)


def issue_codes(report: dict[str, Any]) -> set[str]:
    return {issue["issue_code"] for issue in report["issues"]}


def test_valid_pptx_package_passes_and_matches_schema() -> None:
    report = inspect_fixture("valid-native-deck")
    assert report["status"] == "passed"
    assert report["issues"] == []
    schema = load_json(ROOT / "schemas" / "pptx-inspection.schema.json")
    Draft202012Validator(schema).validate(report)


def test_missing_media_fails() -> None:
    report = inspect_fixture("missing-media")
    assert "PPTX_MISSING_MEDIA" in issue_codes(report)
    assert report["status"] == "failed"


def test_broken_relationship_fails() -> None:
    report = inspect_fixture("broken-relationship")
    assert "PPTX_MISSING_MEDIA" in issue_codes(report)
    assert report["status"] == "failed"


def test_whole_slide_image_is_detected() -> None:
    report = inspect_fixture("whole-slide-image")
    assert "PPTX_WHOLE_SLIDE_RASTER" in issue_codes(report)


def test_background_image_with_native_overlay_is_allowed(tmp_path: Path) -> None:
    save_whole_slide_image(tmp_path, name="background", delivery_route="background_image", overlay=True)
    package = inspect_package(tmp_path / "deck.pptx", ppt_ir=load_json(tmp_path / "ppt-ir.json"))
    report = inspection_to_dict(
        inspect_slides(
            tmp_path / "deck.pptx",
            package,
            ppt_ir=load_json(tmp_path / "ppt-ir.json"),
            style=load_json(tmp_path / "style-contract.json"),
            delivery=load_json(tmp_path / "delivery-plan.json"),
        )
    )
    assert "PPTX_WHOLE_SLIDE_RASTER" not in issue_codes(report)


def test_font_below_minimum_fails() -> None:
    report = inspect_fixture("font-too-small")
    assert "PPTX_FONT_SIZE_BELOW_MINIMUM" in issue_codes(report)


def test_color_drift_detected() -> None:
    report = inspect_fixture("color-drift")
    assert "STYLE_COLOR_DRIFT" in issue_codes(report)


def test_fragmentation_thresholds_fire() -> None:
    report = inspect_fixture("fragmented-svg-conversion")
    codes = issue_codes(report)
    assert "PPTX_TINY_OBJECT_OVERLOAD" in codes
    assert "PPTX_TEXT_FRAGMENTATION" in codes


def test_out_of_bounds_detected() -> None:
    report = inspect_fixture("object-out-of-bounds")
    assert {"PPTX_TEXT_OUT_OF_BOUNDS", "GEOMETRY_OBJECT_OUT_OF_BOUNDS"} & issue_codes(report)


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("rasterized-table", "PPTX_TABLE_NOT_NATIVE"),
        ("rasterized-chart", "PPTX_CHART_NOT_NATIVE"),
        ("route-deviation", "PPTX_RASTER_ROUTE_UNDECLARED"),
    ],
)
def test_rasterized_route_fixtures_produce_expected_issues(fixture: str, expected: str) -> None:
    report = inspect_fixture(fixture)
    assert expected in issue_codes(report)
    assert "PPTX_RASTER_ROUTE_UNDECLARED" in issue_codes(report)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "inspect_pptx.py"), *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_cli_exit_codes_0_1_2(tmp_path: Path) -> None:
    valid = FIXTURES / "valid-native-deck"
    whole = FIXTURES / "whole-slide-image"
    result_ok = run_cli(
        str(valid / "deck.pptx"),
        "--ppt-ir",
        str(valid / "ppt-ir.json"),
        "--style",
        str(valid / "style-contract.json"),
        "--delivery",
        str(valid / "delivery-plan.json"),
        "--output",
        str(tmp_path / "valid.json"),
    )
    assert result_ok.returncode == 0, result_ok.stderr
    result_error = run_cli(
        str(whole / "deck.pptx"),
        "--ppt-ir",
        str(whole / "ppt-ir.json"),
        "--style",
        str(whole / "style-contract.json"),
        "--delivery",
        str(whole / "delivery-plan.json"),
        "--output",
        str(tmp_path / "whole.json"),
    )
    assert result_error.returncode == 1, result_error.stderr
    result_unreadable = run_cli(str(tmp_path / "missing.pptx"))
    assert result_unreadable.returncode == 2
