#!/usr/bin/env python3
"""Run the PPTSmith v2 production gates as one resumable command."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REGISTRY = ROOT / "references" / "component-registry.json"
STAGES = [
    "prepare_inputs",
    "validate_inputs",
    "resolve_profile",
    "capability_probe",
    "resolve_delivery",
    "validate_delivery",
    "build",
    "inspect",
    "verify",
    "prepare_delivery",
    "package_delivery",
]


class StageFailure(RuntimeError):
    def __init__(self, stage: str, message: str, returncode: int = 1) -> None:
        super().__init__(message)
        self.stage = stage
        self.returncode = returncode


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return document


def fingerprint(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def copy_input(source: Path, target: Path) -> None:
    if not source.is_file():
        raise ValueError(f"Input does not exist: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the end-to-end PPTSmith v2 production pipeline.")
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--ppt-ir", type=Path, required=True)
    parser.add_argument("--style", type=Path, required=True)
    parser.add_argument("--assets", "--asset-manifest", dest="assets", type=Path)
    parser.add_argument("--builder", choices=["auto", "python_pptx", "pptxgenjs"], default="auto")
    parser.add_argument("--profile", choices=["fast", "standard", "premium"], default="standard")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--json-output", action="store_true")
    return parser.parse_args(argv)


class Pipeline:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.work = args.work_dir.resolve()
        self.output = args.output_dir.resolve()
        self.contracts = self.work / "contracts"
        self.qa = self.work / "qa"
        self.logs = self.work / "logs"
        self.build_dir = self.work / "builds" / "final"
        self.state_path = self.work / "state.json"
        self.previous = load_json(self.state_path) if self.state_path.exists() else None
        prior_attempts = list((self.previous or {}).get("attempts", []))
        if self.previous and not prior_attempts:
            prior_attempts.append(self.attempt_snapshot(self.previous))
        self.attempts = prior_attempts[-19:]
        self.inputs = {
            "requirements": str(args.requirements.resolve()),
            "ppt_ir": str(args.ppt_ir.resolve()),
            "style": str(args.style.resolve()),
            "asset_manifest": str(args.assets.resolve()) if args.assets else None,
            "builder": args.builder,
            "profile": args.profile,
            "work_dir": str(self.work),
            "output_dir": str(self.output),
        }
        now = iso_now()
        self.state: dict[str, Any] = {
            "schema_version": "1.0",
            "command_inputs": self.inputs,
            "input_fingerprints": {},
            "attempt": int((self.previous or {}).get("attempt", 0)) + 1,
            "resumed_from": (self.previous or {}).get("last_successful_stage") if self.previous else None,
            "current_stage": None,
            "last_successful_stage": None,
            "failed_stage": None,
            "status": "running",
            "started_at": now,
            "updated_at": now,
            "completed_at": None,
            "error": None,
            "attempts": self.attempts,
        }
        self.attempts.append(self.attempt_snapshot(self.state))
        self.state["attempts"] = self.attempts

    @staticmethod
    def attempt_snapshot(state: dict[str, Any]) -> dict[str, Any]:
        return {
            "attempt": state.get("attempt"),
            "command_inputs": state.get("command_inputs", {}),
            "input_fingerprints": state.get("input_fingerprints", {}),
            "status": state.get("status"),
            "last_successful_stage": state.get("last_successful_stage"),
            "failed_stage": state.get("failed_stage"),
            "error": state.get("error"),
            "started_at": state.get("started_at"),
            "completed_at": state.get("completed_at"),
        }

    def save_state(self) -> None:
        self.state["updated_at"] = iso_now()
        self.attempts[-1] = self.attempt_snapshot(self.state)
        self.state["attempts"] = self.attempts
        write_json(self.state_path, self.state)

    def run_command(self, stage: str, command: list[str], *, cwd: Path = ROOT, accepted: set[int] | None = None) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
        self.logs.mkdir(parents=True, exist_ok=True)
        (self.logs / f"{STAGES.index(stage) + 1:02d}-{stage}.log").write_text(
            "$ " + " ".join(command) + "\n\nSTDOUT\n" + completed.stdout + "\nSTDERR\n" + completed.stderr,
            encoding="utf-8",
        )
        if completed.returncode not in (accepted or {0}):
            detail = (completed.stderr or completed.stdout).strip()
            raise StageFailure(stage, detail or f"Command exited {completed.returncode}", completed.returncode)
        return completed

    def stage(self, name: str, action: Any) -> None:
        self.state["current_stage"] = name
        self.save_state()
        action()
        self.state["last_successful_stage"] = name
        self.save_state()

    def prepare_inputs(self) -> None:
        self.work.mkdir(parents=True, exist_ok=True)
        # Every attempt deterministically rebuilds derived artifacts. This is the
        # safe resume path: validated source contracts survive, stale products do not.
        for path in (self.qa, self.logs, self.build_dir.parent):
            if path.exists():
                shutil.rmtree(path)
        if self.output.exists():
            shutil.rmtree(self.output)
        contract_stage = self.work / ".contracts.current"
        contract_backup = self.work / ".contracts.previous"
        for path in (contract_stage, contract_backup):
            if path.exists():
                shutil.rmtree(path)
        contract_stage.mkdir(parents=True)
        sources = {
            "requirements": self.args.requirements,
            "ppt_ir": self.args.ppt_ir,
            "style": self.args.style,
        }
        if self.args.assets:
            sources["asset_manifest"] = self.args.assets
        targets = {
            "requirements": contract_stage / "requirements.json",
            "ppt_ir": contract_stage / "ppt-ir.json",
            "style": contract_stage / "style-contract.json",
            "asset_manifest": contract_stage / "asset-manifest.json",
        }
        for name, source in sources.items():
            copy_input(source, targets[name])
            self.state["input_fingerprints"][name] = fingerprint(source)
        requirements = load_json(targets["requirements"])
        requirements["production_profile"] = self.args.profile
        write_json(targets["requirements"], requirements)
        if self.contracts.exists():
            self.contracts.replace(contract_backup)
        contract_stage.replace(self.contracts)
        if contract_backup.exists():
            shutil.rmtree(contract_backup)
        targets = {
            "requirements": self.contracts / "requirements.json",
            "ppt_ir": self.contracts / "ppt-ir.json",
            "style": self.contracts / "style-contract.json",
            "asset_manifest": self.contracts / "asset-manifest.json",
        }
        analysis = self.work / "analysis"
        analysis.mkdir(parents=True, exist_ok=True)
        (analysis / "content-lock.md").write_text("# Content Lock\n\nSource contracts are locked by the pipeline input fingerprints in `state.json`.\n", encoding="utf-8")
        if self.args.profile in {"standard", "premium"}:
            ppt_ir = load_json(targets["ppt_ir"])
            lines = ["# Storyboard", ""] + [f"- {slide.get('id', '?')}: {slide.get('title', '')}" for slide in ppt_ir.get("slides", [])]
            (analysis / "storyboard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def validate(self, stage: str, *, include_delivery: bool = False, include_build: bool = False) -> None:
        command = [sys.executable, str(SCRIPTS / "validate_contracts.py"), "--ppt-ir", str(self.contracts / "ppt-ir.json"), "--style", str(self.contracts / "style-contract.json")]
        if (self.contracts / "asset-manifest.json").exists():
            command += ["--assets", str(self.contracts / "asset-manifest.json")]
        if include_delivery:
            command += ["--delivery", str(self.contracts / "delivery-plan.json")]
        if include_build:
            command += ["--build", str(self.contracts / "build-manifest.json")]
        command += ["--strict", "--json-output"]
        self.run_command(stage, command)

    def resolve_profile(self) -> None:
        self.run_command("resolve_profile", [
            sys.executable, str(SCRIPTS / "resolve_production_profile.py"),
            "--requirements", str(self.contracts / "requirements.json"),
            "--ppt-ir", str(self.contracts / "ppt-ir.json"),
            "--output", str(self.contracts / "production-profile.json"),
        ])

    def capability_probe(self) -> None:
        # Run from the pinned local Node runtime so its package is discoverable.
        runtime = ROOT / "runtime" / "pptxgenjs"
        self.run_command("capability_probe", [
            sys.executable, str(SCRIPTS / "capability_probe.py"),
            "--style", str(self.contracts / "style-contract.json"),
            "--registry", str(REGISTRY),
            "--output", str(self.contracts / "capability-report.json"),
        ], cwd=runtime if runtime.is_dir() else ROOT)
        fault = os.environ.get("PPTSMITH_TEST_CAPABILITIES")
        if fault:
            report = load_json(self.contracts / "capability-report.json")
            for name, builder in (report.get("builders", {}) or {}).items():
                if fault == "none" or fault == f"{name}_unavailable":
                    builder["available"] = False
            write_json(self.contracts / "capability-report.json", report)

    def resolve_delivery(self) -> None:
        self.run_command("resolve_delivery", [
            sys.executable, str(SCRIPTS / "resolve_component_delivery.py"),
            "--ppt-ir", str(self.contracts / "ppt-ir.json"),
            "--style", str(self.contracts / "style-contract.json"),
            "--registry", str(REGISTRY),
            "--capabilities", str(self.contracts / "capability-report.json"),
            "--profile", self.args.profile,
            "--builder", self.args.builder,
            "--output", str(self.contracts / "delivery-plan.json"),
            "--strict",
        ])
        plan = load_json(self.contracts / "delivery-plan.json")
        builder = plan.get("builder") if isinstance(plan.get("builder"), dict) else {}
        selected = str(builder.get("selected") or "unknown")
        errors = [str(item) for item in builder.get("errors", [])]
        unsupported = int((plan.get("summary") or {}).get("unsupported_count", 0))
        if errors or selected not in {"python_pptx", "pptxgenjs"} or unsupported:
            codes = errors or (["BUILDER_SELECTION_UNKNOWN"] if selected == "unknown" else ["DELIVERY_PLAN_UNSUPPORTED"])
            raise StageFailure("resolve_delivery", ", ".join(codes))
        if self.args.builder != "auto" and selected != self.args.builder:
            raise StageFailure("resolve_delivery", f"CAPABILITY_FORCED_BUILDER_REJECTED: requested={self.args.builder}, selected={selected}")

    def approved_builder(self) -> str:
        return str(load_json(self.contracts / "delivery-plan.json")["builder"]["selected"])

    def build(self) -> None:
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.run_command("build", [
            sys.executable, str(SCRIPTS / "build_deck.py"),
            "--ppt-ir", str(self.contracts / "ppt-ir.json"),
            "--style", str(self.contracts / "style-contract.json"),
            "--delivery", str(self.contracts / "delivery-plan.json"),
            "--builder", self.approved_builder(),
            "--output-dir", str(self.build_dir),
            "--build-manifest", str(self.contracts / "build-manifest.json"),
        ])

    def deck_path(self) -> Path:
        manifest = load_json(self.contracts / "build-manifest.json")
        raw = Path(str(manifest.get("outputs", {}).get("deck", "deck.pptx")))
        return raw if raw.is_absolute() else self.build_dir / raw

    def inspect(self) -> None:
        self.run_command("inspect", [
            sys.executable, str(SCRIPTS / "inspect_pptx.py"), str(self.deck_path()),
            "--ppt-ir", str(self.contracts / "ppt-ir.json"),
            "--style", str(self.contracts / "style-contract.json"),
            "--delivery", str(self.contracts / "delivery-plan.json"),
            "--build", str(self.contracts / "build-manifest.json"),
            "--output", str(self.qa / "pptx-inspection.json"),
        ])

    def verify(self) -> None:
        command = [
            sys.executable, str(SCRIPTS / "verify_deck.py"), str(self.deck_path()),
            "--ppt-ir", str(self.contracts / "ppt-ir.json"),
            "--style", str(self.contracts / "style-contract.json"),
            "--delivery", str(self.contracts / "delivery-plan.json"),
            "--build", str(self.contracts / "build-manifest.json"),
            "--inspection-report", str(self.qa / "pptx-inspection.json"),
            "--capabilities", str(self.contracts / "capability-report.json"),
            "--profile", self.args.profile,
            "--output", str(self.qa / "qa-report.json"),
        ]
        accepted = {0, 1}  # verifier uses 1 for warning-only reports as well as hard QA failures
        if self.args.profile == "premium":
            command += ["--render", "--render-required", "--render-output", str(self.work / "renders"), "--write-render-report", str(self.qa / "render-report.json")]
            accepted.add(2)  # truthful renderer-unavailable evidence; packaging remains blocked
        completed = self.run_command("verify", command, accepted=accepted)
        report = load_json(self.qa / "qa-report.json")
        renderer_unavailable = any(
            isinstance(issue, dict) and issue.get("issue_code") == "RENDER_ENGINE_UNAVAILABLE"
            for issue in report.get("issues", [])
        )
        if renderer_unavailable:
            self.state["provisional_reason"] = "RENDER_ENGINE_UNAVAILABLE"
        if report.get("status") in {"fail", "blocked"}:
            raise StageFailure("verify", f"QA hard failure: {report.get('status')}", completed.returncode or 1)

    def prepare_delivery(self) -> None:
        build_path = self.contracts / "build-manifest.json"
        build = load_json(build_path)
        qa = load_json(self.qa / "qa-report.json")
        inspection = load_json(self.qa / "pptx-inspection.json")
        trusted = str(qa.get("trusted_delivery_status") or "created")
        build["status"] = trusted if trusted in {"created", "rendered", "read_back", "verified", "final"} else "failed"
        build["last_successful_stage"] = "verify"
        build["failed_stage"] = None if qa.get("status") not in {"fail", "blocked"} else "verify"
        build["contract_refs"]["qa_report"] = "../../qa/qa-report.json"
        build["contract_refs"]["production_profile"] = "production-profile.json"
        build["stages"].update({
            "read_back": inspection.get("status") == "passed",
            "verified": trusted in {"verified", "final"},
            "qa_passed": qa.get("status") in {"pass", "warning"},
            "rendered": bool((qa.get("evidence", {}).get("render_report") or {}).get("status") == "passed"),
        })
        build["metrics"].update(qa.get("metrics", {}))
        build["outputs"]["deck"] = str(self.deck_path().resolve())
        report = self.build_dir / "verification-report.md"
        report.write_text(
            "# Verification Report\n\n"
            f"- Profile: {self.args.profile}\n- Structural inspection: {inspection.get('status')}\n"
            f"- QA status: {qa.get('status')}\n- Trusted delivery status: {trusted}\n",
            encoding="utf-8",
        )
        build["outputs"]["verification_report"] = str(report.resolve())
        render = qa.get("evidence", {}).get("render_report")
        if isinstance(render, dict) and render.get("status") == "passed" and render.get("pdf_path"):
            pdf = Path(str(render["pdf_path"]))
            if pdf.is_file():
                target = self.build_dir / "deck-preview.pdf"
                shutil.copy2(pdf, target)
                build["outputs"]["preview_pdf"] = str(target.resolve())
        write_json(build_path, build)
        self.validate("prepare_delivery", include_delivery=True, include_build=True)

    def package(self) -> None:
        manifest = self.output / "delivery-manifest.json"
        command = [
            sys.executable, str(SCRIPTS / "package_delivery.py"),
            "--workdir", str(self.work),
            "--profile", self.args.profile,
            "--output", str(self.output),
            "--manifest", str(manifest),
            "--strict",
        ]
        self.run_command("package_delivery", command)

    def run(self) -> int:
        self.work.mkdir(parents=True, exist_ok=True)
        self.save_state()
        try:
            self.stage("prepare_inputs", self.prepare_inputs)
            self.stage("validate_inputs", lambda: self.validate("validate_inputs"))
            self.stage("resolve_profile", self.resolve_profile)
            self.stage("capability_probe", self.capability_probe)
            self.stage("resolve_delivery", self.resolve_delivery)
            self.stage("validate_delivery", lambda: self.validate("validate_delivery", include_delivery=True))
            self.stage("build", self.build)
            self.stage("inspect", self.inspect)
            self.stage("verify", self.verify)
            self.stage("prepare_delivery", self.prepare_delivery)
            self.stage("package_delivery", self.package)
        except (StageFailure, OSError, ValueError, json.JSONDecodeError) as exc:
            failed_stage = exc.stage if isinstance(exc, StageFailure) else str(self.state.get("current_stage") or "initialize")
            self.state.update({"status": "blocked" if self.state.get("provisional_reason") else "failed", "failed_stage": failed_stage, "current_stage": failed_stage, "error": str(exc), "completed_at": iso_now()})
            self.save_state()
            print(f"run_pipeline [{failed_stage}]: {exc}", file=sys.stderr)
            return exc.returncode if isinstance(exc, StageFailure) and exc.returncode else 1
        self.state.update({"status": "completed", "failed_stage": None, "current_stage": None, "error": None, "completed_at": iso_now()})
        self.save_state()
        if self.args.json_output:
            print(json.dumps({"ok": True, "state": str(self.state_path), "output": str(self.output)}, indent=2))
        return 0


def main(argv: list[str]) -> int:
    return Pipeline(parse_args(argv)).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
