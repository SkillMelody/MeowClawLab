from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESOLVER = ROOT / "scripts" / "resolve_component_delivery.py"
VALIDATOR = ROOT / "scripts" / "validate_contracts.py"
FIXTURE = ROOT / "tests" / "fixtures" / "components" / "sample-ppt-ir.json"
TECHNICAL_DIAGRAM_FIXTURE = ROOT / "tests" / "fixtures" / "technical-agent" / "ppt-ir.json"
STYLE = ROOT / "tests" / "fixtures" / "styles" / "technical-blueprint.json"
REGISTRY = ROOT / "references" / "component-registry.json"
CAPABILITIES = ROOT / "tests" / "fixtures" / "components" / "capabilities.json"


def resolve(tmp_path: Path, ppt_ir: Path = FIXTURE, profile: str = "premium", builder: str = "auto", strict: bool = True) -> dict:
    output = tmp_path / "delivery-plan.json"
    command = [
        sys.executable,
        str(RESOLVER),
        "--ppt-ir",
        str(ppt_ir),
        "--style",
        str(STYLE),
        "--registry",
        str(REGISTRY),
        "--capabilities",
        str(CAPABILITIES),
        "--profile",
        profile,
        "--builder",
        builder,
        "--output",
        str(output),
    ]
    if strict:
        command.append("--strict")
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
    )
    return json.loads(output.read_text(encoding="utf-8"))


def plans_by_object(plan: dict) -> dict[str, dict]:
    return {obj["object_id"]: obj for slide in plan["slides"] for obj in slide["objects"]}


def test_metric_card_uses_native_route(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path))["metric-01"]
    assert obj["selected_route"] == "native_ppt"


def test_simple_chart_uses_native_chart(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path))["chart-01"]
    assert obj["selected_route"] == "native_chart"


def test_simple_diagram_uses_native_diagram(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path))["diagram-01"]
    assert obj["selected_route"] == "native_diagram"


def test_diagram_ir_reference_adds_analysis(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path, ppt_ir=TECHNICAL_DIAGRAM_FIXTURE))["diagram-01"]
    assert obj["diagram_analysis"]["node_count"] == 6
    assert obj["diagram_analysis"]["layout_recommendation"] == "layered_architecture"
    assert obj["selected_route"] in {"native_diagram", "hybrid_overlay", "svg_component"}


def test_complex_ecosystem_uses_hybrid_overlay(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path))["ecosystem-01"]
    assert obj["selected_route"] == "hybrid_overlay"
    assert "DELIVERY_COMPLEXITY_EXCEEDS_NATIVE_LIMIT" in obj["reason_codes"]


def test_conceptual_scene_uses_generated_image_with_overlay(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path))["scene-01"]
    assert obj["selected_route"] == "generated_image"
    assert "title" in obj["native_overlay_parts"]


def test_native_required_never_rasterizes(tmp_path: Path) -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["slides"][0]["objects"][0]["component_type"] = "conceptual_scene"
    data["slides"][0]["objects"][0]["editability"] = "native_required"
    path = tmp_path / "native-required.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    obj = plans_by_object(resolve(tmp_path, path, strict=False))["metric-01"]
    assert obj["selected_route"] == "unsupported"
    assert "DELIVERY_NATIVE_REQUIRED_UNAVAILABLE" in obj["reason_codes"]


def test_ordinary_table_rasterization_fails_validation(tmp_path: Path) -> None:
    plan = resolve(tmp_path)
    obj = plans_by_object(plan)["metric-01"]
    obj["selected_route"] = "raster_component"
    plan_path = tmp_path / "bad-delivery-plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--ppt-ir",
            str(FIXTURE),
            "--style",
            str(STYLE),
            "--delivery",
            str(plan_path),
            "--strict",
            "--json-output",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    codes = {issue["code"] for issue in json.loads(result.stdout)["issues"]}
    assert "DELIVERY_ORDINARY_COMPONENT_RASTERIZED" in codes


def test_unknown_component_fails(tmp_path: Path) -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["slides"][0]["objects"][0]["component_type"] = "not_registered"
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    obj = plans_by_object(resolve(tmp_path, path, strict=False))["metric-01"]
    assert obj["selected_route"] == "unsupported"
    assert "DELIVERY_COMPONENT_NOT_REGISTERED" in obj["reason_codes"]


def test_premium_whole_slide_raster_fails(tmp_path: Path) -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["slides"][4]["objects"][0]["whole_slide_raster"] = True
    path = tmp_path / "whole-slide.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    obj = plans_by_object(resolve(tmp_path, path, strict=False))["scene-01"]
    assert obj["selected_route"] == "unsupported"
    assert "DELIVERY_WHOLE_SLIDE_RASTER_FORBIDDEN" in obj["reason_codes"]


def test_fast_complex_diagram_can_use_svg(tmp_path: Path) -> None:
    obj = plans_by_object(resolve(tmp_path, profile="fast"))["ecosystem-01"]
    assert obj["selected_route"] in {"hybrid_overlay", "svg_component"}
    assert "title" in obj["native_overlay_parts"]


def test_delivery_plan_matches_schema(tmp_path: Path) -> None:
    output = tmp_path / "delivery-plan.json"
    plan = resolve(tmp_path)
    output.write_text(json.dumps(plan), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--ppt-ir",
            str(FIXTURE),
            "--style",
            str(STYLE),
            "--component-registry",
            str(REGISTRY),
            "--delivery",
            str(output),
            "--strict",
            "--json-output",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert json.loads(result.stdout)["ok"], result.stdout


def test_build_manifest_route_deviation_fails(tmp_path: Path) -> None:
    plan = resolve(tmp_path)
    output = tmp_path / "delivery-plan.json"
    output.write_text(json.dumps(plan), encoding="utf-8")
    build = {
        "schema_version": "2.0",
        "build_id": "build-test",
        "deck_id": "deck-test",
        "profile": "premium",
        "builder": "pptxgenjs",
        "builder_profile": "test",
        "status": "planned",
        "contract_refs": {
            "ppt_ir": str(FIXTURE),
            "style_contract": str(STYLE),
            "asset_manifest": "asset-manifest.json",
            "delivery_plan": str(output),
        },
        "stages": {},
        "outputs": {},
        "metrics": {},
        "fallbacks": [
            {
                "slide_id": "S04",
                "object_id": "ecosystem-01",
                "component_type": "ecosystem_map",
                "planned_route": "native_diagram",
                "actual_route": "hybrid_overlay",
                "reason_codes": ["DELIVERY_COMPLEXITY_EXCEEDS_NATIVE_LIMIT"],
                "editable_core_preserved": True,
            }
        ],
        "warnings": [],
        "errors": [],
    }
    build_path = tmp_path / "build-manifest.json"
    build_path.write_text(json.dumps(build), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--ppt-ir",
            str(FIXTURE),
            "--style",
            str(STYLE),
            "--delivery",
            str(output),
            "--build",
            str(build_path),
            "--strict",
            "--json-output",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    codes = {issue["code"] for issue in json.loads(result.stdout)["issues"]}
    assert "BUILD_ROUTE_DEVIATION" in codes
