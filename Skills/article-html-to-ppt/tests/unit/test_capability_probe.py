from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import capability_probe

STYLE = ROOT / "tests" / "fixtures" / "styles" / "technical-blueprint.json"
REGISTRY = ROOT / "references" / "component-registry.json"
PROBE = ROOT / "scripts" / "capability_probe.py"


def test_probe_writes_capability_report(tmp_path: Path) -> None:
    output = tmp_path / "capability-report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(PROBE),
            "--style",
            str(STYLE),
            "--registry",
            str(REGISTRY),
            "--output",
            str(output),
            "--timeout",
            "3",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["schema_version"] == "1.0"
    assert {"officecli", "pptxgenjs", "python_pptx", "html_svg"} <= set(report["builders"])
    assert {"microsoft_powerpoint", "libreoffice"} <= set(report["renderers"])
    assert "pptx_write" in report["formats"]
    assert "required_missing" in report["fonts"]
    assert report["environment"]["working_directory"] == ROOT.name


def test_probe_detects_pptxgenjs(monkeypatch) -> None:
    class Completed:
        returncode = 0
        stdout = "4.0.1\n"
        stderr = ""

    monkeypatch.setattr(capability_probe.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(capability_probe, "run_command", lambda command, timeout: Completed())
    report = capability_probe.probe_pptxgenjs({"components": []}, timeout=1)
    assert report["available"] is True
    assert report["version"] == "4.0.1"
    assert report["features"]["native_chart"] is True


def test_probe_does_not_import_unexported_pptxgenjs_package_json(monkeypatch) -> None:
    class Completed:
        returncode = 0
        stdout = "4.0.1\n"
        stderr = ""

    captured: list[str] = []

    def fake_run(command, timeout):
        captured.append(command[2])
        return Completed()

    monkeypatch.setattr(capability_probe.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(capability_probe, "run_command", fake_run)

    report = capability_probe.probe_pptxgenjs({"components": []}, timeout=1)

    assert report["available"] is True
    assert len(captured) == 1
    assert "require('pptxgenjs/package.json')" not in captured[0]
    assert "require.resolve('pptxgenjs')" in captured[0]


def test_probe_rejects_wrong_ancestor_package_identity(monkeypatch) -> None:
    class Completed:
        returncode = 1
        stdout = ""
        stderr = "PPTXGENJS_PACKAGE_IDENTITY_MISMATCH"

    captured: list[str] = []

    def fake_run(command, timeout):
        captured.append(command[2])
        return Completed()

    monkeypatch.setattr(capability_probe.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(capability_probe, "run_command", fake_run)

    report = capability_probe.probe_pptxgenjs({"components": []}, timeout=1)

    assert report["available"] is False
    assert report["version"] is None
    assert "pkg.name !== 'pptxgenjs'" in captured[0]
    assert "CAPABILITY_PPTXGENJS_PACKAGE_IDENTITY_INVALID" in report["errors"]


def test_missing_builder_is_reported(monkeypatch) -> None:
    monkeypatch.setattr(capability_probe.shutil, "which", lambda name: None)
    report = capability_probe.probe_officecli({"components": []}, timeout=1)
    assert report["available"] is False
    assert "officecli command not found." in report["warnings"]


def test_core_builder_not_available_on_failed_smoke(monkeypatch) -> None:
    class Completed:
        returncode = 1
        stdout = ""
        stderr = "Cannot find module"

    monkeypatch.setattr(capability_probe.shutil, "which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(capability_probe, "run_command", lambda command, timeout: Completed())
    report = capability_probe.probe_pptxgenjs({"components": []}, timeout=1)
    assert report["available"] is False
    assert "CAPABILITY_SMOKE_TEST_FAILED" in report["errors"]
