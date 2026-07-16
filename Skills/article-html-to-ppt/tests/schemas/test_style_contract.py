from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_contracts.py"
MIGRATOR = ROOT / "scripts" / "migrate_style_contract_v1_to_v2.py"
FIXTURES = ROOT / "tests" / "fixtures" / "styles"


def run_validator(path: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--style", str(path), "--strict", "--json-output"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def write_style(tmp_path: Path, mutate) -> Path:
    data = json.loads((FIXTURES / "consulting-light.json").read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "style.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def codes(result: dict) -> set[str]:
    return {issue["code"] for issue in result["issues"]}


def test_five_style_contracts_pass() -> None:
    for name in [
        "consulting-light.json",
        "product-report.json",
        "technical-blueprint.json",
        "consulting-blueprint-hybrid.json",
        "editorial-knowledge.json",
    ]:
        result = run_validator(FIXTURES / name)
        assert result["ok"], result


def test_invalid_hex_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["colors"].__setitem__("primary", "blue"))
    assert "STYLE_INVALID_HEX" in codes(run_validator(path))


def test_missing_primary_color_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["colors"].pop("primary"))
    result_codes = codes(run_validator(path))
    assert "REQUIRED_FIELD_MISSING" in result_codes or "STYLE_REQUIRED_COLOR_MISSING" in result_codes


def test_empty_font_stack_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["typography"].__setitem__("font_primary", []))
    assert "STYLE_FONT_STACK_EMPTY" in codes(run_validator(path))


def test_font_stack_needs_generic_family(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["typography"].__setitem__("font_primary", ["Aptos"]))
    assert "STYLE_FONT_GENERIC_FAMILY_MISSING" in codes(run_validator(path))


def test_body_size_below_minimum_fails(tmp_path: Path) -> None:
    def mutate(data: dict) -> None:
        data["typography"]["minimum_body_size_pt"] = 12
        data["typography"]["body_sizes_pt"]["normal"] = 10

    assert "STYLE_BODY_SIZE_BELOW_MINIMUM" in codes(run_validator(write_style(tmp_path, mutate)))


def test_negative_grid_margin_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["grid"].__setitem__("margin_left_in", -0.1))
    assert "MINIMUM_INVALID" in codes(run_validator(path))


def test_card_unknown_color_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["card_tokens"]["default"].__setitem__("fill", "missing_surface"))
    assert "STYLE_UNKNOWN_TOKEN_REFERENCE" in codes(run_validator(path))


def test_chart_unknown_series_color_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["chart_tokens"]["series_colors"].append("missing_color"))
    assert "STYLE_UNKNOWN_TOKEN_REFERENCE" in codes(run_validator(path))


def test_diagram_unknown_relation_style_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["diagram_tokens"]["relation_styles"].__setitem__("request", "spiral"))
    assert "STYLE_DIAGRAM_RELATION_UNKNOWN" in codes(run_validator(path))


def test_spacing_rule_unknown_scale_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["spacing"]["rules"].__setitem__("card_gap", "mega"))
    assert "STYLE_SPACING_REFERENCE_MISSING" in codes(run_validator(path))


def test_undeclared_field_fails_in_strict_mode(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data.__setitem__("surprise", True))
    assert "ADDITIONAL_PROPERTY" in codes(run_validator(path))


def test_negative_density_limit_fails(tmp_path: Path) -> None:
    path = write_style(tmp_path, lambda data: data["density_limits"]["low"].__setitem__("max_primary_objects", -1))
    assert "STYLE_DENSITY_LIMIT_INVALID" in codes(run_validator(path))


def test_alias_conflict_fails(tmp_path: Path) -> None:
    def mutate(data: dict) -> None:
        data["compatibility_aliases"] = [
            {"alias": "legacy", "maps_to": "consulting-light"},
            {"alias": "legacy", "maps_to": "product-report"},
        ]

    assert "STYLE_ALIAS_CONFLICT" in codes(run_validator(write_style(tmp_path, mutate)))


def test_legacy_style_contract_migrates_to_v2(tmp_path: Path) -> None:
    legacy = {
        "schema_version": "1.1",
        "style_system": "consulting-light",
        "palette_name": "mckinsey",
        "colors": {
            "primary": "#0A2233",
            "accent": "#2C4A6E",
            "background": "#FBFBF8",
            "text": "#2A2E35",
            "secondary": "#7C7669",
            "border": "#E4E0D7",
            "surface": "#F1EFEA",
        },
        "typography": {"minimum_body_size_pt": 10},
        "spacing_scale_in": [0.06, 0.1, 0.16, 0.24, 0.36, 0.52],
        "component_variants": {},
        "footer": {"enabled": True, "height_in": 0.24, "text_color": "text_secondary", "font_size_ref": "typography.body_sizes_pt.footnote", "divider_color": "border"},
        "density_limits": {"low": {"max_primary_objects": 2}, "medium": {"max_primary_objects": 4}, "high": {"max_primary_objects": 6}},
        "forbidden_drift": ["invented colors"],
    }
    legacy_path = tmp_path / "legacy.json"
    migrated_path = tmp_path / "migrated.json"
    legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
    subprocess.run([sys.executable, str(MIGRATOR), str(legacy_path), "-o", str(migrated_path)], cwd=ROOT, check=True)
    result = run_validator(migrated_path)
    assert result["ok"], result
