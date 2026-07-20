from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "template-pack.schema.json"
PACKS = ROOT / "references" / "template-packs"
STYLES = ROOT / "tests" / "fixtures" / "styles"
REGISTRY_PATH = ROOT / "references" / "component-registry.json"
ARCHETYPES_PATH = ROOT / "references" / "premium-page-archetypes.md"
REQUIRED_ROLES = {
    "cover",
    "judgment",
    "evidence_data",
    "process_relationship",
    "comparison_implementation",
    "closing",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validator() -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(load_json(SCHEMA_PATH))


def pack_paths() -> list[Path]:
    return [PACKS / "editorial-knowledge.json", PACKS / "technical-blueprint.json"]


def canonical_page_archetypes() -> set[str]:
    reference = ARCHETYPES_PATH.read_text(encoding="utf-8")
    section = re.search(
        r"^## Core Archetypes\s*$\n(?P<body>.*?)(?=^##\s|\Z)",
        reference,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert section is not None, f"{ARCHETYPES_PATH}: missing '## Core Archetypes' section"

    entry_pattern = re.compile(r"^-\s+`([a-z0-9]+(?:-[a-z0-9]+)*)`\s*:")
    entries = [line for line in section.group("body").splitlines() if line.startswith("-")]
    malformed = [line for line in entries if entry_pattern.match(line) is None]
    assert not malformed, f"{ARCHETYPES_PATH}: malformed Core Archetypes entries: {malformed}"

    names = [entry_pattern.match(line).group(1) for line in entries]
    assert names, f"{ARCHETYPES_PATH}: Core Archetypes section yielded no identifiers"
    duplicates = sorted({name for name in names if names.count(name) > 1})
    assert not duplicates, f"{ARCHETYPES_PATH}: duplicate archetype identifiers: {duplicates}"
    return set(names)


def assert_invalid(data: dict) -> None:
    assert list(validator().iter_errors(data))


def test_production_template_packs_pass_schema() -> None:
    for path in pack_paths():
        errors = sorted(validator().iter_errors(load_json(path)), key=lambda error: list(error.path))
        assert not errors, f"{path}: {[error.message for error in errors]}"


def test_schema_requires_pack_contract_sections() -> None:
    pack = load_json(pack_paths()[0])
    for field in [
        "pack_id",
        "display_name",
        "style_contract",
        "compatible_expression_modes",
        "archetypes",
        "editable_core_policy",
        "forbidden_patterns",
        "truthful_constraints",
    ]:
        broken = copy.deepcopy(pack)
        broken.pop(field)
        assert_invalid(broken)


def test_exactly_six_required_archetype_roles() -> None:
    for path in pack_paths():
        pack = load_json(path)
        assert len(pack["archetypes"]) == 6
        assert {item["role"] for item in pack["archetypes"]} == REQUIRED_ROLES

    broken = load_json(pack_paths()[0])
    broken["archetypes"] = broken["archetypes"][:-1]
    assert_invalid(broken)


def test_style_references_resolve_to_matching_v2_contracts() -> None:
    for path in pack_paths():
        pack = load_json(path)
        style_ref = pack["style_contract"]
        style_path = (path.parent / style_ref["ref"]).resolve()
        assert style_path.is_file(), style_path
        style = load_json(style_path)
        assert style["schema_version"] == "2.0"
        assert style["style_id"] == style_ref["style_id"] == pack["pack_id"]
        assert style_path == (STYLES / f"{pack['pack_id']}.json").resolve()


def test_template_pack_archetypes_and_schema_enum_match_canonical_reference() -> None:
    canonical = canonical_page_archetypes()

    for path in pack_paths():
        used = {item["page_archetype"] for item in load_json(path)["archetypes"]}
        assert used <= canonical, f"{path}: unknown page archetypes: {sorted(used - canonical)}"

    schema_values = load_json(SCHEMA_PATH)["$defs"]["archetype"]["properties"]["page_archetype"]["enum"]
    assert len(schema_values) == len(set(schema_values)), f"{SCHEMA_PATH}: duplicate page_archetype enum values"
    schema_enum = set(schema_values)
    assert schema_enum == canonical, (
        f"{SCHEMA_PATH}: page_archetype enum drift; "
        f"missing={sorted(canonical - schema_enum)}, extra={sorted(schema_enum - canonical)}"
    )


def test_every_archetype_uses_pack_modes_and_named_registry_routes() -> None:
    registry = {item["component_type"]: item for item in load_json(REGISTRY_PATH)["components"]}
    for path in pack_paths():
        pack = load_json(path)
        pack_modes = set(pack["compatible_expression_modes"])
        for archetype in pack["archetypes"]:
            modes = set(archetype["allowed_expression_modes"])
            assert modes <= pack_modes
            for policy in archetype["component_routes"]:
                component = registry.get(policy["component_type"])
                assert component is not None, policy
                assert policy["expression_mode"] in modes
                assert policy["expression_mode"] in component["supported_primary_expressions"]
                assert policy["preferred_route"] in component["allowed_delivery_routes"]
                assert set(policy["allowed_routes"]) <= set(component["allowed_delivery_routes"])
                assert policy["preferred_route"] in policy["allowed_routes"]


def test_editable_core_policy_is_nonempty_and_truthful() -> None:
    for path in pack_paths():
        pack = load_json(path)
        policy = pack["editable_core_policy"]
        assert policy["required_native_objects"]
        assert policy["required_editable_elements"]
        assert policy["whole_slide_raster_forbidden"] is True
        assert policy["bounded_visual_requires_native_overlay"] is True
        assert pack["forbidden_patterns"]
        constraints = pack["truthful_constraints"]
        assert constraints["renderer_evidence_required_for_final"] is True
        assert constraints["disclose_route_deviations"] is True
        assert constraints["disclose_raster_or_generated_components"] is True


def test_unknown_expression_and_route_fail_schema() -> None:
    pack = load_json(pack_paths()[0])
    pack["compatible_expression_modes"].append("hybrid_panel")
    assert_invalid(pack)

    pack = load_json(pack_paths()[0])
    pack["archetypes"][0]["component_routes"][0]["preferred_route"] = "screenshot_master"
    assert_invalid(pack)


def test_unknown_fields_fail_strict_schema() -> None:
    pack = load_json(pack_paths()[0])
    pack["screenshot_master"] = True
    assert_invalid(pack)
