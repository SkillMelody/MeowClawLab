from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builders.base import BuildPlan
from builders.pptxgenjs_adapter import PptxGenJsAdapter
from ppt_qa.package_inspector import inspect_package


def two_slide_plan() -> BuildPlan:
    return BuildPlan(
        builder="pptxgenjs",
        slides=[
            {
                "id": "S01",
                "title": "PptxGenJS Runtime",
                "message": "Editable title and body",
                "objects": [
                    {
                        "id": "card-1",
                        "type": "shape",
                        "component_type": "metric_card",
                        "content": {"title": "Coverage", "value": "100%"},
                        "editability": "native_required",
                        "delivery_plan": {"selected_route": "native_ppt"},
                    }
                ],
            },
            {
                "id": "S02",
                "title": "Native data and process",
                "objects": [
                    {
                        "id": "table-1",
                        "type": "table",
                        "component_type": "native_table",
                        "content": {"headers": ["Item", "Status"], "body": [["Table", "Native"]]},
                        "editability": "native_required",
                        "delivery_plan": {"selected_route": "native_table"},
                    },
                    {
                        "id": "chart-1",
                        "type": "chart",
                        "component_type": "bar_chart",
                        "content": {"categories": ["A", "B"], "series": [{"name": "Score", "values": [2, 5]}]},
                        "editability": "native_required",
                        "delivery_plan": {"selected_route": "native_chart"},
                    },
                    {
                        "id": "process-1",
                        "type": "diagram",
                        "component_type": "process",
                        "content": {"nodes": [{"label": "Plan"}, {"label": "Build"}, {"label": "Verify"}]},
                        "editability": "native_required",
                        "delivery_plan": {"selected_route": "native_diagram"},
                    },
                ],
            },
        ],
    )


def test_probe_availability_follows_node_and_local_module() -> None:
    adapter = PptxGenJsAdapter()
    capability = adapter.probe()
    runtime = ROOT / "runtime" / "pptxgenjs"
    expected = (
        shutil.which("node") is not None
        and (runtime / "node_modules" / "pptxgenjs" / "package.json").is_file()
        and (runtime / "node_modules" / "jszip" / "package.json").is_file()
    )
    assert capability.available is expected
    assert capability.command == shutil.which("node") if expected else capability.command is None
    if expected:
        assert capability.version


def test_probe_names_incomplete_direct_module_install(tmp_path: Path) -> None:
    if shutil.which("node") is None:
        return
    runtime = tmp_path / "runtime"
    (runtime / "node_modules" / "pptxgenjs").mkdir(parents=True)
    (runtime / "node_modules" / "jszip").mkdir(parents=True)
    (runtime / "build-deck.mjs").write_text("// present\n", encoding="utf-8")
    (runtime / "node_modules" / "pptxgenjs" / "package.json").write_text(
        json.dumps({"name": "pptxgenjs", "version": "4.0.1", "type": "module", "main": "missing.mjs"}),
        encoding="utf-8",
    )
    (runtime / "node_modules" / "jszip" / "package.json").write_text(
        json.dumps({"name": "jszip", "version": "3.10.1", "main": "missing.js"}),
        encoding="utf-8",
    )

    capability = PptxGenJsAdapter(runtime_dir=runtime, timeout_seconds=1).probe()

    assert capability.available is False
    assert "PPTXGENJS_RUNTIME_MODULE_LOAD_FAILED" in capability.errors


def test_forced_missing_runtime_failure_is_named(tmp_path: Path) -> None:
    adapter = PptxGenJsAdapter(runtime_dir=tmp_path / "missing-runtime")
    result = adapter.build(two_slide_plan(), tmp_path / "out")
    assert result.status == "failed"
    assert result.errors[0]["code"] == "PPTXGENJS_RUNTIME_UNAVAILABLE"


def test_builds_nonempty_two_slide_pptx_and_runtime_result(tmp_path: Path) -> None:
    adapter = PptxGenJsAdapter()
    assert adapter.probe().available, adapter.probe().errors
    result = adapter.build(two_slide_plan(), tmp_path)
    assert result.status == "created", result.errors
    deck = Path(result.pptx or "")
    assert deck.is_file() and deck.stat().st_size > 0
    runtime_result = json.loads((tmp_path / "runtime-result.json").read_text(encoding="utf-8"))
    assert runtime_result["status"] == "created"
    assert len(runtime_result["object_results"]) == 4
    inspection = inspect_package(deck)
    assert inspection.status == "passed"
    assert inspection.slide_count == 2
    with zipfile.ZipFile(deck) as package:
        slide_xml = package.read("ppt/slides/slide2.xml").decode("utf-8")
    assert 'prst="chevron"' not in slide_xml
    assert '<a:tailEnd type="triangle"' in slide_xml
    assert "Material:process-node:" in slide_xml


def test_plan_preserves_style_contract_and_runtime_applies_supported_style(tmp_path: Path) -> None:
    style = {
        "schema_version": "2.0",
        "style_id": "review-style",
        "aspect_ratios": ["4:3"],
        "colors": {
            "primary": "#123456", "accent": "#CC5500", "background": "#FEFDF0",
            "surface_1": "#EEEEDD", "surface_2": "#DDDDAA", "text_primary": "#102030",
            "text_secondary": "#405060", "border": "#ABCDEF", "positive": "#008800",
            "warning": "#AA7700", "negative": "#AA0000", "data_series": ["#123456", "#CC5500", "#008800"],
        },
        "typography": {
            "font_primary": ["Courier New", "sans-serif"], "font_editorial": ["Georgia"],
            "title_sizes_pt": {"cover": 38, "section": 34, "slide": 31},
            "body_sizes_pt": {"large": 20, "normal": 17, "small": 12, "footnote": 9},
        },
        "grid": {"margin_left_in": 0.8, "margin_right_in": 0.7, "margin_top_in": 0.4, "title_zone_height_in": 0.8, "gutter_horizontal_in": 0.25},
        "spacing": {
            "unit": "in",
            "scale": {"xs": 0.06, "sm": 0.1, "md": 0.22, "lg": 0.33, "xl": 0.4, "xxl": 0.5},
            "rules": {
                "card_gap": "md", "title_to_body": "lg", "section_gap": "xl",
                "icon_to_label": "sm", "label_to_value": "xs", "paragraph_gap": "sm",
            },
        },
        "shape_tokens": {"card_radius_pt": 12},
    }
    adapter = PptxGenJsAdapter()
    planned = adapter.plan({"slides": two_slide_plan().slides}, style, {"slides": []})
    assert planned.style_contract == style

    result = adapter.build(planned, tmp_path)

    assert result.status == "created", result.errors
    serialized = json.loads((tmp_path / "build-plan.json").read_text(encoding="utf-8"))
    assert serialized["style_contract"] == style
    warned_paths = {
        warning.rsplit(": ", 1)[-1]
        for warning in result.warnings
        if warning.startswith("Unsupported style field ignored by PptxGenJS runtime:")
    }
    assert {
        "shape_tokens",
        "typography.title_sizes_pt.cover", "typography.title_sizes_pt.section",
        "typography.body_sizes_pt.large", "typography.body_sizes_pt.footnote",
        "spacing.rules.section_gap", "spacing.rules.icon_to_label",
        "spacing.rules.label_to_value", "spacing.rules.paragraph_gap",
        "spacing.scale.xs", "spacing.scale.sm", "spacing.scale.xl", "spacing.scale.xxl",
    } <= warned_paths
    assert "typography.title_sizes_pt.slide" not in warned_paths
    assert "typography.body_sizes_pt.normal" not in warned_paths
    assert "typography.body_sizes_pt.small" not in warned_paths
    assert "spacing.rules.card_gap" not in warned_paths
    assert "spacing.rules.title_to_body" not in warned_paths
    assert "spacing.scale.md" not in warned_paths
    assert "spacing.scale.lg" not in warned_paths
    with zipfile.ZipFile(result.pptx or "") as package:
        xml = "\n".join(package.read(name).decode("utf-8", errors="ignore") for name in package.namelist() if name.endswith(".xml"))
    assert "Courier New" in xml
    assert "FEFDF0" in xml
    assert 'cx="9144000"' in xml  # 4:3 slide width


def test_nonzero_runtime_cannot_reuse_stale_success(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "deck.pptx").write_bytes(b"old deck")
    (tmp_path / "runtime-result.json").write_text(
        json.dumps({"status": "created", "pptx": str(tmp_path / "deck.pptx"), "errors": []}),
        encoding="utf-8",
    )
    adapter = PptxGenJsAdapter()
    monkeypatch.setattr(adapter, "probe", lambda: type("Capability", (), {"available": True, "command": shutil.which("node"), "errors": []})())
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 9, stdout="", stderr="current run failed"),
    )

    result = adapter.build(two_slide_plan(), tmp_path)

    assert result.status == "failed"
    assert result.pptx is None
    assert result.errors[0]["code"] in {"PPTXGENJS_RUNTIME_RESULT_MISSING", "PPTXGENJS_RUNTIME_FAILED"}
    assert not (tmp_path / "deck.pptx").exists()


def test_rejects_unsupported_native_required_object(tmp_path: Path) -> None:
    plan = BuildPlan(
        builder="pptxgenjs",
        slides=[
            {
                "id": "S01",
                "title": "Unsupported",
                "objects": [
                    {
                        "id": "media-1",
                        "type": "video",
                        "component_type": "native_video",
                        "editability": "native_required",
                        "delivery_plan": {"selected_route": "native_ppt"},
                    }
                ],
            }
        ],
    )
    result = PptxGenJsAdapter().build(plan, tmp_path)
    assert result.status == "failed"
    assert result.errors[0]["code"] == "UNSUPPORTED_NATIVE_REQUIRED_OBJECT"
    assert not (tmp_path / "deck.pptx").exists()


def test_unknown_non_required_object_discloses_semantic_card_fallback(tmp_path: Path) -> None:
    plan = BuildPlan(builder="pptxgenjs", slides=[{
        "id": "S01", "title": "Fallback", "objects": [{
            "id": "mystery-1", "component_type": "mystery_widget", "content": {"text": "Kept as text"},
            "delivery_plan": {"selected_route": "native_ppt"},
        }],
    }])

    result = PptxGenJsAdapter().build(plan, tmp_path)

    assert result.status == "created", result.errors
    assert result.fallbacks[0]["reason_codes"] == ["PPTXGENJS_SEMANTIC_CARD_FALLBACK"]
    assert any("mystery_widget" in warning for warning in result.warnings)
