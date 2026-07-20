from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "scripts" / "run_pipeline.py"
FIXTURES = ROOT / "tests" / "fixtures" / "v2-acceptance"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def run_pipeline(
    tmp_path: Path,
    requirements: Path,
    *,
    ppt_ir: Path | None = None,
    assets: Path | None = None,
    builder: str = "python_pptx",
    profile: str = "standard",
    env: dict[str, str] | None = None,
    rubric_case: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    work_dir = tmp_path / ".ppt-work"
    output_dir = tmp_path / "delivery"
    return subprocess.run(
        [
            sys.executable,
            str(PIPELINE),
            "--requirements", str(requirements),
            "--ppt-ir", str(ppt_ir or FIXTURES / "ppt-ir.json"),
            "--style", str(FIXTURES / "style-contract-editorial.json"),
            *(["--assets", str(assets)] if assets else []),
            "--builder", builder,
            "--profile", profile,
            *(["--rubric-case", str(rubric_case), "--use-reference-rubric"] if rubric_case else []),
            "--work-dir", str(work_dir),
            "--output-dir", str(output_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_standard_pipeline_produces_unique_delivery_and_preserves_audit_artifacts(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements.json"
    write_json(requirements, {"production_profile": "standard", "user_request": "Standard delivery"})

    completed = run_pipeline(tmp_path, requirements)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    output = tmp_path / "delivery"
    expected = [
        work / "contracts" / "requirements.json",
        work / "contracts" / "ppt-ir.json",
        work / "contracts" / "style-contract.json",
        work / "contracts" / "production-profile.json",
        work / "contracts" / "capability-report.json",
        work / "contracts" / "delivery-plan.json",
        work / "contracts" / "build-manifest.json",
        work / "qa" / "pptx-inspection.json",
        work / "qa" / "qa-report.json",
        work / "state.json",
        output / "delivery-manifest.json",
    ]
    assert all(path.is_file() for path in expected)
    assert len(list(output.glob("*.pptx"))) == 1
    assert not list(output.glob("*copy*.pptx"))

    build = load_json(work / "contracts" / "build-manifest.json")
    qa = load_json(work / "qa" / "qa-report.json")
    inspection = load_json(work / "qa" / "pptx-inspection.json")
    delivery = load_json(output / "delivery-manifest.json")
    state = load_json(work / "state.json")
    Draft202012Validator(load_json(ROOT / "schemas" / "build-manifest.schema.json")).validate(build)
    Draft202012Validator(load_json(ROOT / "schemas" / "qa-report.schema.json")).validate(qa)
    Draft202012Validator(load_json(ROOT / "schemas" / "pptx-inspection.schema.json")).validate(inspection)
    Draft202012Validator(load_json(ROOT / "schemas" / "delivery-manifest.schema.json")).validate(delivery)
    assert inspection["status"] == "passed"
    assert qa["status"] == "pass"
    assert delivery["status"] == "verified"
    assert state["status"] == "completed"
    assert state["last_successful_stage"] == "package_delivery"
    assert state["failed_stage"] is None
    assert state["command_inputs"]["profile"] == "standard"
    assert state["command_inputs"]["builder"] == "python_pptx"


def test_success_failure_resume_removes_stale_artifacts_and_preserves_attempt_audit(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements.json"
    write_json(requirements, {"production_profile": "standard"})
    mutable_ir = tmp_path / "ppt-ir.json"
    write_json(mutable_ir, load_json(FIXTURES / "ppt-ir.json"))

    first = run_pipeline(tmp_path, requirements, ppt_ir=mutable_ir)
    assert first.returncode == 0, first.stderr or first.stdout
    work = tmp_path / ".ppt-work"
    output = tmp_path / "delivery"
    old_deck_hash = load_json(work / "state.json")["input_fingerprints"]["ppt_ir"]
    assert (work / "builds" / "final" / "deck.pptx").is_file()
    assert (work / "qa" / "qa-report.json").is_file()
    assert len(list(output.glob("*.pptx"))) == 1

    invalid = load_json(mutable_ir)
    del invalid["deck"]["id"]
    write_json(mutable_ir, invalid)
    failed = run_pipeline(tmp_path, requirements, ppt_ir=mutable_ir)

    assert failed.returncode != 0
    state_path = work / "state.json"
    failed_state = load_json(state_path)
    assert failed_state["status"] == "failed"
    assert failed_state["last_successful_stage"] == "prepare_inputs"
    assert failed_state["failed_stage"] == "validate_inputs"
    assert not output.exists()
    assert not (work / "builds").exists()
    assert not (work / "qa").exists()
    assert len(failed_state["attempts"]) == 2
    assert failed_state["attempts"][0]["status"] == "completed"
    assert failed_state["attempts"][0]["input_fingerprints"]["ppt_ir"] == old_deck_hash
    assert failed_state["attempts"][1]["status"] == "failed"

    write_json(mutable_ir, load_json(FIXTURES / "ppt-ir.json"))
    resumed = run_pipeline(tmp_path, requirements, ppt_ir=mutable_ir)

    assert resumed.returncode == 0, resumed.stderr or resumed.stdout
    resumed_state = load_json(state_path)
    assert resumed_state["attempt"] == 3
    assert len(resumed_state["attempts"]) == 3
    assert [attempt["status"] for attempt in resumed_state["attempts"]] == ["completed", "failed", "completed"]
    assert resumed_state["attempts"][2]["input_fingerprints"]["ppt_ir"] == old_deck_hash
    assert len(list(output.glob("*.pptx"))) == 1


def test_assets_present_then_omitted_recreates_current_contract_set(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements.json"
    write_json(requirements, {"production_profile": "standard"})
    assets = tmp_path / "asset-manifest.json"
    asset_doc = load_json(ROOT / "examples" / "contracts" / "valid" / "asset-manifest.json")
    for asset in asset_doc["assets"]:
        asset["source_refs"] = ["acceptance-source"]
    write_json(assets, asset_doc)

    first = run_pipeline(tmp_path, requirements, assets=assets)
    assert first.returncode == 0, first.stderr or first.stdout
    copied = tmp_path / ".ppt-work" / "contracts" / "asset-manifest.json"
    assert copied.is_file()

    second = run_pipeline(tmp_path, requirements)
    assert second.returncode == 0, second.stderr or second.stdout
    state = load_json(tmp_path / ".ppt-work" / "state.json")
    assert not copied.exists()
    assert state["command_inputs"]["asset_manifest"] is None
    assert "asset_manifest" not in state["input_fingerprints"]


def test_auto_with_no_available_builder_fails_before_build(tmp_path: Path, monkeypatch) -> None:
    requirements = tmp_path / "requirements.json"
    write_json(requirements, {"production_profile": "standard"})
    monkeypatch.setenv("PPTSMITH_TEST_CAPABILITIES", "none")

    completed = run_pipeline(tmp_path, requirements, builder="auto", env=dict(__import__("os").environ))

    assert completed.returncode != 0
    assert "BUILDER_SELECTION_NO_VALID_CANDIDATE" in completed.stderr
    state = load_json(tmp_path / ".ppt-work" / "state.json")
    assert state["failed_stage"] == "resolve_delivery"
    assert not (tmp_path / ".ppt-work" / "builds").exists()


def test_forced_unavailable_builder_fails_named_before_build(tmp_path: Path, monkeypatch) -> None:
    requirements = tmp_path / "requirements.json"
    write_json(requirements, {"production_profile": "standard"})
    monkeypatch.setenv("PPTSMITH_TEST_CAPABILITIES", "python_pptx_unavailable")

    completed = run_pipeline(tmp_path, requirements, builder="python_pptx", env=dict(__import__("os").environ))

    assert completed.returncode != 0
    assert "CAPABILITY_BUILDER_NOT_FOUND" in completed.stderr
    state = load_json(tmp_path / ".ppt-work" / "state.json")
    assert state["failed_stage"] == "resolve_delivery"
    assert not (tmp_path / ".ppt-work" / "builds").exists()


@pytest.mark.parametrize("profile", ["fast", "standard"])
@pytest.mark.parametrize("builder", ["python_pptx", "pptxgenjs"])
def test_profile_builder_matrix_runs_real_success_pipeline(tmp_path: Path, profile: str, builder: str) -> None:
    requirements = FIXTURES / f"requirements-{profile}.json"

    completed = run_pipeline(tmp_path, requirements, builder=builder, profile=profile)

    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    output = tmp_path / "delivery"
    state = load_json(work / "state.json")
    copied_requirements = load_json(work / "contracts" / "requirements.json")
    production = load_json(work / "contracts" / "production-profile.json")
    plan = load_json(work / "contracts" / "delivery-plan.json")
    build = load_json(work / "contracts" / "build-manifest.json")
    qa = load_json(work / "qa" / "qa-report.json")
    delivery = load_json(output / "delivery-manifest.json")
    decks = list(output.glob("*.pptx"))
    expected_qa_status = "pass"
    assert state["status"] == "completed"
    assert copied_requirements["production_profile"] == profile
    assert production["selected_profile"] == profile
    assert production["override_applied"] is True
    assert f"USER_REQUESTED_{profile.upper()}" in production["reason_codes"]
    assert plan["profile"] == profile
    assert plan["builder"]["requested"] == builder
    assert plan["builder"]["selected"] == builder
    assert build["builder"]["requested"] == builder
    assert build["builder"]["selected"] == builder
    assert qa["status"] == expected_qa_status
    assert qa["metrics"]["qa_error_count"] == 0
    assert qa["trusted_delivery_status"] == "verified"
    assert build["status"] == "verified"
    assert delivery["status"] == "verified"
    assert len(decks) == 1
    assert decks[0].stat().st_size > 0


def test_premium_without_renderer_is_truthfully_blocked_and_never_delivered(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PPTSMITH_TEST_RENDERERS"] = "none"
    completed = run_pipeline(
        tmp_path,
        FIXTURES / "requirements-premium.json",
        builder="pptxgenjs",
        profile="premium",
        env=env,
    )

    assert completed.returncode != 0
    work = tmp_path / ".ppt-work"
    output = tmp_path / "delivery"
    state = load_json(work / "state.json")
    qa = load_json(work / "qa" / "qa-report.json")
    assert state["status"] in {"provisional", "blocked"}
    assert state["status"] != "completed"
    assert state["failed_stage"] == "verify"
    assert state["provisional_reason"] == "RENDER_ENGINE_UNAVAILABLE"
    assert qa["trusted_delivery_status"] != "final"
    assert not output.exists()
    assert not list(tmp_path.rglob("delivery-manifest.json"))
    assert not list(tmp_path.glob("delivery/*.pptx"))


def test_premium_with_renderer_still_requires_explicit_rubric(tmp_path: Path) -> None:
    completed = run_pipeline(
        tmp_path,
        FIXTURES / "requirements-premium.json",
        builder="pptxgenjs",
        profile="premium",
        env=dict(os.environ),
    )

    assert completed.returncode != 0
    assert "PREMIUM_RUBRIC_REQUIRED" in completed.stderr
    state = load_json(tmp_path / ".ppt-work" / "state.json")
    assert state["failed_stage"] in {"verify", "score"}
    assert not (tmp_path / "delivery").exists()


@pytest.mark.skipif(not Path("/Applications/LibreOffice.app").exists() and not shutil.which("soffice"), reason="real renderer required")
def test_premium_rejects_rubric_bound_to_another_build_even_with_real_renderer(tmp_path: Path) -> None:
    completed = run_pipeline(
        tmp_path,
        FIXTURES / "requirements-premium.json",
        builder="pptxgenjs",
        profile="premium",
        env=dict(os.environ),
        rubric_case=FIXTURES / "premium-rubric" / "case.json",
    )

    assert completed.returncode != 0
    assert "reference rubric build_id does not match current evidence" in completed.stderr
    assert not (tmp_path / "delivery").exists()


def test_actual_pipeline_build_route_deviation_fails_strict_validation(tmp_path: Path) -> None:
    completed = run_pipeline(
        tmp_path,
        FIXTURES / "requirements-standard.json",
        builder="python_pptx",
        profile="standard",
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    work = tmp_path / ".ppt-work"
    build_path = work / "contracts" / "build-manifest.json"
    build = load_json(build_path)
    planned = next(
        obj
        for slide in load_json(work / "contracts" / "delivery-plan.json")["slides"]
        for obj in slide["objects"]
    )
    authoritative_route = planned["selected_route"]
    deviating_route = "unsupported" if authoritative_route != "unsupported" else "native_ppt"
    build["fallbacks"] = [{
        "slide_id": planned["slide_id"],
        "object_id": planned["object_id"],
        "component_type": planned["component_type"],
        "planned_route": authoritative_route,
        "actual_route": deviating_route,
        "reason_codes": ["TEST_ROUTE_DEVIATION"],
        "editable_core_preserved": True,
    }]
    build["metrics"]["fallback_count"] = 1
    write_json(build_path, build)

    checked = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "validate_contracts.py"),
            "--ppt-ir", str(work / "contracts" / "ppt-ir.json"),
            "--style", str(work / "contracts" / "style-contract.json"),
            "--delivery", str(work / "contracts" / "delivery-plan.json"),
            "--build", str(build_path),
            "--strict", "--json-output",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert checked.returncode != 0
    validation = json.loads(checked.stdout)
    codes = [item["code"] for item in validation["issues"]]
    assert "BUILD_ROUTE_DEVIATION" in codes
    schema_error_codes = {
        "ADDITIONAL_PROPERTY", "ANY_OF_INVALID", "CONST_INVALID", "ENUM_INVALID",
        "MAXIMUM_INVALID", "MAX_ITEMS_INVALID", "MINIMUM_INVALID", "MIN_ITEMS_INVALID",
        "MIN_LENGTH_INVALID", "ONE_OF_INVALID", "PATTERN_INVALID", "REQUIRED_FIELD_MISSING",
        "TYPE_INVALID", "UNIQUE_ITEMS_INVALID",
    }
    assert not schema_error_codes.intersection(codes), validation


def test_native_required_visual_downgrade_fails_pipeline_strictly(tmp_path: Path) -> None:
    downgraded_ir = load_json(FIXTURES / "ppt-ir.json")
    native_required = downgraded_ir["slides"][1]["objects"][0]
    assert native_required["editability"] == "native_required"
    native_required["component_type"] = "conceptual_scene"
    native_required["delivery_preferences"] = {
        "preferred_route": "generated_image",
        "allowed_fallbacks": ["raster_component"],
    }
    ir_path = tmp_path / "native-required-downgrade.json"
    write_json(ir_path, downgraded_ir)

    completed = run_pipeline(
        tmp_path,
        FIXTURES / "requirements-standard.json",
        ppt_ir=ir_path,
        builder="pptxgenjs",
        profile="standard",
        env=dict(os.environ),
    )

    assert completed.returncode != 0
    assert "BUILDER_NATIVE_REQUIRED_UNSUPPORTED" in completed.stderr
    assert "BUILDER_VISUAL_ONLY_FOR_NATIVE_REQUIRED" in completed.stderr
    state = load_json(tmp_path / ".ppt-work" / "state.json")
    assert state["failed_stage"] == "resolve_delivery"
    assert not (tmp_path / ".ppt-work" / "builds").exists()
    assert not (tmp_path / "delivery").exists()
