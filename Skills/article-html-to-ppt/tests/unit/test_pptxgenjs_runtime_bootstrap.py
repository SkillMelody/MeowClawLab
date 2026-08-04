from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts" / "bootstrap_pptxgenjs_runtime.py"


def test_preflight_missing_modules_explains_the_pinned_bootstrap_command(tmp_path: Path) -> None:
    runtime = tmp_path / "pptxgenjs"
    runtime.mkdir()
    (runtime / "package.json").write_text(
        json.dumps({"dependencies": {"pptxgenjs": "4.0.1", "jszip": "3.10.1"}}),
        encoding="utf-8",
    )
    (runtime / "package-lock.json").write_text(
        json.dumps({"lockfileVersion": 3}),
        encoding="utf-8",
    )
    (runtime / "build-deck.mjs").write_text("// runtime fixture\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(BOOTSTRAP), "--check", "--runtime", str(runtime)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    report = json.loads(completed.stdout)
    assert report["status"] == "blocked"
    assert report["code"] == "PPTXGENJS_RUNTIME_UNAVAILABLE"
    assert report["action"] == "npm ci"
    assert "package-lock.json" in report["message"]
