#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.content_to_pages import select_pages


def main() -> int:
    evidence_path = ROOT / "examples" / "dashboard-evidence-units.json"
    output_path = ROOT / "qa" / "selection-manifest.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    manifest = select_pages(evidence)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0 if manifest["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
