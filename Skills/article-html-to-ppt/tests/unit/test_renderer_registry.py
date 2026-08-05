from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
RENDERER_CAPABILITIES = ROOT / "references" / "renderer-capabilities.json"
COMPONENT_REGISTRY = ROOT / "references" / "component-registry.json"

from visual_narrative.renderer_registry import (
    effective_component_support,
    load_renderer_capabilities,
    smoke_test_renderer,
)


def test_load_renderer_capabilities_accepts_schema_1_0(tmp_path: Path) -> None:
    path = tmp_path / "renderer-capabilities.json"
    document = {"schema_version": "1.0", "renderers": {}}
    path.write_text(json.dumps(document), encoding="utf-8")

    assert load_renderer_capabilities(path) == document


def test_load_renderer_capabilities_rejects_unsupported_schema(tmp_path: Path) -> None:
    path = tmp_path / "renderer-capabilities.json"
    path.write_text(json.dumps({"schema_version": "2.0"}), encoding="utf-8")

    with pytest.raises(ValueError, match="^RENDERER_CAPABILITY_SCHEMA_UNSUPPORTED$"):
        load_renderer_capabilities(path)


def test_registry_full_does_not_override_missing_renderer_handler() -> None:
    registry = {
        "schema_version": "1.0",
        "components": [
            {
                "component_type": "native_table",
                "builder_support": {"python_pptx": {"level": "full"}},
            }
        ]
    }
    capabilities = {
        "schema_version": "1.0",
        "renderers": {
            "python_pptx": {
                "native_table": {
                    "level": "full",
                    "schema_versions": ["1.0"],
                    "smoke_test": "passed",
                }
            }
        },
    }

    support = effective_component_support(registry, capabilities, "python_pptx")

    assert support["native_table"] == "unsupported"


def test_registry_full_requires_compatible_component_schema() -> None:
    registry = {
        "schema_version": "1.0",
        "components": [
            {
                "component_type": "native_table",
                "builder_support": {"python_pptx": {"level": "full"}},
            }
        ],
    }
    capabilities = {
        "schema_version": "1.0",
        "renderers": {
            "python_pptx": {
                "native_table": {
                    "level": "full",
                    "handler": "builders.python_pptx_adapter._add_table",
                    "schema_versions": ["2.0"],
                    "smoke_test": "passed",
                }
            }
        },
    }

    support = effective_component_support(registry, capabilities, "python_pptx")

    assert support["native_table"] == "unsupported"


def test_registry_full_fails_closed_when_real_smoke_test_fails(monkeypatch) -> None:
    from builders import python_pptx_adapter

    def fail_to_render(*args, **kwargs) -> None:
        raise RuntimeError("renderer unavailable")

    monkeypatch.setattr(python_pptx_adapter, "_add_table", fail_to_render)
    registry = {
        "schema_version": "1.0",
        "components": [
            {
                "component_type": "native_table",
                "builder_support": {"python_pptx": {"level": "full"}},
            }
        ],
    }
    capabilities = {
        "schema_version": "1.0",
        "renderers": {
            "python_pptx": {
                "native_table": {
                    "level": "full",
                    "handler": "builders.python_pptx_adapter._add_table",
                    "schema_versions": ["1.0"],
                    "smoke_test": "passed",
                }
            }
        },
    }

    support = effective_component_support(registry, capabilities, "python_pptx")

    assert support["native_table"] == "unsupported"


def test_registry_full_requires_full_renderer_capability_level() -> None:
    registry = {
        "schema_version": "1.0",
        "components": [
            {
                "component_type": "native_table",
                "builder_support": {"python_pptx": {"level": "full"}},
            }
        ],
    }
    capabilities = {
        "schema_version": "1.0",
        "renderers": {
            "python_pptx": {
                "native_table": {
                    "level": "partial",
                    "handler": "builders.python_pptx_adapter._add_table",
                    "schema_versions": ["1.0"],
                    "smoke_test": "passed",
                }
            }
        },
    }

    support = effective_component_support(registry, capabilities, "python_pptx")

    assert support["native_table"] == "unsupported"


@pytest.mark.parametrize(
    "smoke_test_fields",
    [
        {"smoke_test": "failed"},
        {},
        {"smoke_test": "unknown"},
    ],
    ids=("failed", "missing", "unknown"),
)
def test_registry_full_requires_static_smoke_test_passed(
    smoke_test_fields: dict[str, str],
) -> None:
    registry = {
        "schema_version": "1.0",
        "components": [
            {
                "component_type": "native_table",
                "builder_support": {"python_pptx": {"level": "full"}},
            }
        ],
    }
    handler = {
        "level": "full",
        "handler": "builders.python_pptx_adapter._add_table",
        "schema_versions": ["1.0"],
        **smoke_test_fields,
    }
    capabilities = {
        "schema_version": "1.0",
        "renderers": {"python_pptx": {"native_table": handler}},
    }

    support = effective_component_support(registry, capabilities, "python_pptx")

    assert support["native_table"] == "unsupported"


def test_smoke_test_renderer_exercises_existing_native_table_handler() -> None:
    assert smoke_test_renderer("python_pptx", "native_table", "1.0") is True


def test_smoke_test_renderer_rejects_unbound_component() -> None:
    assert smoke_test_renderer("python_pptx", "flywheel", "1.0") is False


@pytest.mark.parametrize(
    ("builder", "component_type"),
    [
        ("python_pptx", "comparison_card"),
        ("python_pptx", "metric_card"),
        ("python_pptx", "summary_action_card"),
        ("python_pptx", "bar_chart"),
        ("python_pptx", "process_flow"),
        ("pptxgenjs", "comparison_card"),
        ("pptxgenjs", "metric_card"),
        ("pptxgenjs", "summary_action_card"),
        ("pptxgenjs", "bar_chart"),
        ("pptxgenjs", "process_flow"),
        ("pptxgenjs", "native_table"),
    ],
)
def test_merged_v2_runtime_handlers_pass_real_smoke(
    builder: str,
    component_type: str,
) -> None:
    assert smoke_test_renderer(builder, component_type, "1.0") is True


@pytest.mark.parametrize(
    "component_type",
    [
        "heat_matrix",
        "layered_architecture",
        "drill_down_stair",
        "phase_roadmap",
        "causal_chain",
    ],
)
def test_priority_renderer_bindings_pass_real_smoke(component_type: str) -> None:
    assert smoke_test_renderer("python_pptx", component_type, "1.0") is True


def test_renderer_capability_baseline_only_declares_truth_bound_handlers() -> None:
    document = load_renderer_capabilities(RENDERER_CAPABILITIES)

    assert set(document["renderers"]) == {"python_pptx", "pptxgenjs"}
    assert set(document["renderers"]["python_pptx"]) == {
        "comparison_card",
        "metric_card",
        "summary_action_card",
        "bar_chart",
        "process_flow",
        "native_table",
        "heat_matrix",
        "layered_architecture",
        "drill_down_stair",
        "phase_roadmap",
        "product_ui_overview",
        "interaction_storyboard",
        "causal_chain",
    }
    assert set(document["renderers"]["pptxgenjs"]) == {
        "comparison_card",
        "metric_card",
        "summary_action_card",
        "bar_chart",
        "process_flow",
        "native_table",
    }
    for builder, components in document["renderers"].items():
        for component_type, capability in components.items():
            assert capability["handler"]
            assert capability["schema_versions"] == ["1.0"]
            assert capability["smoke_test"] == "passed"
            assert smoke_test_renderer(builder, component_type, "1.0") is True
    assert "flywheel" not in document["renderers"]["python_pptx"]
    assert "flywheel" not in document["renderers"]["pptxgenjs"]


def test_priority_renderers_are_full_in_effective_component_registry() -> None:
    registry = json.loads(COMPONENT_REGISTRY.read_text(encoding="utf-8"))
    capabilities = load_renderer_capabilities(RENDERER_CAPABILITIES)

    support = effective_component_support(registry, capabilities, "python_pptx")

    assert {
        component_type: support.get(component_type)
        for component_type in (
            "heat_matrix",
            "layered_architecture",
            "drill_down_stair",
            "phase_roadmap",
        )
    } == {
        "heat_matrix": "full",
        "layered_architecture": "full",
        "drill_down_stair": "full",
        "phase_roadmap": "full",
    }
