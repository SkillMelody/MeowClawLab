from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
PACKAGER = ROOT / "scripts" / "package_delivery.py"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def create_minimal_pptx(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("ppt/presentation.xml", "<p:presentation/>")


def create_standard_workdir(tmp_path: Path, *, failed: bool = False) -> Path:
    workdir = tmp_path / ".ppt-work"
    (workdir / "analysis").mkdir(parents=True)
    (workdir / "analysis" / "content-lock.md").write_text("# Content Lock\n", encoding="utf-8")
    (workdir / "analysis" / "storyboard.md").write_text("# Storyboard\n", encoding="utf-8")
    (workdir / "contracts").mkdir()
    for name in ("ppt-ir.json", "style-contract.json", "delivery-plan.json"):
        write_json(workdir / "contracts" / name, {"schema_version": "test"})
    deck = workdir / "builds" / "final" / "deck.pptx"
    create_minimal_pptx(deck)
    (workdir / "builds" / "final" / "deck-preview.pdf").write_bytes(b"%PDF-1.4\n")
    (workdir / "builds" / "final" / "verification-report.md").write_text("verified\n", encoding="utf-8")
    build = {
        "schema_version": "2.0",
        "build_id": "build-test",
        "deck_id": "deck-test",
        "profile": "standard",
        "builder": "pptxgenjs",
        "builder_profile": "test",
        "status": "failed" if failed else "verified",
        "contract_refs": {
            "ppt_ir": "contracts/ppt-ir.json",
            "style_contract": "contracts/style-contract.json",
            "asset_manifest": "contracts/asset-manifest.json",
            "delivery_plan": "contracts/delivery-plan.json",
            "production_profile": "contracts/production-profile.json",
            "qa_report": "qa/qa-report.json",
        },
        "stages": {"built": True, "rendered": True, "read_back": True, "qa_passed": not failed},
        "outputs": {
            "deck": "deck.pptx",
            "preview_pdf": "deck-preview.pdf",
            "verification_report": "verification-report.md",
        },
        "metrics": {
            "editable_core_ratio": 0.96,
            "whole_slide_raster_count": 0,
            "qa_error_count": 0 if not failed else 1,
            "qa_fatal_count": 0,
        },
        "fallbacks": [],
        "warnings": [],
        "errors": [{"code": "RENDER_FAILED"}] if failed else [],
        "resume_from": "06-render" if failed else None,
        "last_successful_stage": "build" if failed else "qa",
        "failed_stage": "render" if failed else None,
    }
    write_json(workdir / "contracts" / "build-manifest.json", build)
    qa = {
        "schema_version": "2.1",
        "deck_id": "deck-test",
        "ppt_ir_ref": "contracts/ppt-ir.json",
        "profile": "standard",
        "status": "fail" if failed else "pass",
        "issues": [{"severity": "error", "issue_code": "RENDER_FAILED"}] if failed else [],
        "metrics": {
            "editable_core_ratio": 0.96,
            "whole_slide_raster_count": 0,
            "qa_error_count": 0 if not failed else 1,
            "qa_fatal_count": 0,
        },
        "evidence": {
            "render_report": {
                "status": "passed",
                "engine": "test-renderer",
                "engine_version": "1.0",
                "slide_count_rendered": 1,
            }
        },
    }
    write_json(workdir / "qa" / "qa-report.json", qa)
    return workdir


def run_packager(workdir: Path, output: Path, manifest: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PACKAGER),
            "--workdir",
            str(workdir),
            "--profile",
            "standard",
            "--output",
            str(output),
            "--manifest",
            str(manifest),
            "--strict",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_package_standard_delivery(tmp_path: Path) -> None:
    workdir = create_standard_workdir(tmp_path)
    output = tmp_path / "delivery"
    manifest_path = output / "delivery-manifest.json"
    result = run_packager(workdir, output, manifest_path)
    assert result.returncode == 0, result.stderr
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads((ROOT / "schemas" / "delivery-manifest.schema.json").read_text(encoding="utf-8"))).validate(manifest)
    assert manifest["status"] == "verified"
    assert {item["role"] for item in manifest["files"]} >= {"pptx", "preview_pdf", "verification_report", "delivery_manifest"}
    assert not (output / ".ppt-work").exists()
    deck_entry = next(item for item in manifest["files"] if item["role"] == "pptx")
    expected_hash = "sha256:" + hashlib.sha256((output / "deck.pptx").read_bytes()).hexdigest()
    assert deck_entry["hash"] == expected_hash


def test_failed_build_preserves_workdir_without_user_facing_output(tmp_path: Path) -> None:
    workdir = create_standard_workdir(tmp_path, failed=True)
    output = tmp_path / "delivery"
    manifest_path = output / "delivery-manifest.json"
    result = run_packager(workdir, output, manifest_path)
    assert result.returncode == 1
    assert workdir.exists()
    assert (workdir / "contracts" / "build-manifest.json").exists()
    assert not output.exists()


def test_late_privacy_failure_never_promotes_pptx_or_manifest(tmp_path: Path) -> None:
    workdir = create_standard_workdir(tmp_path)
    report = workdir / "builds" / "final" / "verification-report.md"
    report.write_text("api_key=abcdefghijklmnop\n", encoding="utf-8")
    output = tmp_path / "delivery"
    output.mkdir()
    (output / "old.pptx").write_bytes(b"stale")
    manifest_path = output / "delivery-manifest.json"

    result = run_packager(workdir, output, manifest_path)

    assert result.returncode == 1
    assert "DELIVERY_SECRET_LEAK" in result.stderr
    assert not output.exists()
    assert not list(tmp_path.glob(".delivery.staging-*"))


def test_strict_packaging_rejects_invalid_trust_ratio_without_clamping(tmp_path: Path) -> None:
    workdir = create_standard_workdir(tmp_path)
    build_path = workdir / "contracts" / "build-manifest.json"
    build = json.loads(build_path.read_text(encoding="utf-8"))
    build["metrics"]["editable_core_ratio"] = 1.01
    write_json(build_path, build)
    qa_path = workdir / "qa" / "qa-report.json"
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    qa["metrics"]["editable_core_ratio"] = 1.01
    write_json(qa_path, qa)
    output = tmp_path / "delivery"

    result = run_packager(workdir, output, output / "delivery-manifest.json")

    assert result.returncode == 1
    assert "DELIVERY_INVALID_TRUST_RATIO: editable_core_ratio" in result.stderr
    assert not output.exists()
