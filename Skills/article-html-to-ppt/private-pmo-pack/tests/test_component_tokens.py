from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.tokens import TokenResolutionError, get_token, resolve_tokens


class ComponentTokenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.legacy = json.loads((ROOT / "contracts" / "mckinsey-pmo.style.json").read_text(encoding="utf-8"))

    def test_boardroom_tokens_preserve_legacy_contract_keys(self) -> None:
        resolved = resolve_tokens(self.legacy)
        self.assertEqual("boardroom-ink", resolved["meta"]["system_id"])
        self.assertTrue(set(self.legacy["colors"]).issubset(resolved["colors"]))
        self.assertTrue(set(self.legacy["typography"]).issubset(resolved["typography"]))
        self.assertEqual("182230", get_token(resolved, "semantic.text.title"))
        self.assertEqual(0.08, get_token(resolved, "spacing.unit_in"))

    def test_role_resolution_uses_declared_fallback_only(self) -> None:
        resolved = resolve_tokens(self.legacy)
        self.assertEqual(
            get_token(resolved, "semantic.text.body"),
            get_token(resolved, "semantic.text.unknown", fallback_role="semantic.text.body"),
        )
        with self.assertRaises(TokenResolutionError):
            get_token(resolved, "semantic.text.unknown")

    def test_density_override_changes_component_limits_without_losing_defaults(self) -> None:
        resolved = resolve_tokens(self.legacy, {"density": {"roadmap": {"max_phases": 4}}})
        self.assertEqual(4, resolved["density"]["roadmap"]["max_phases"])
        self.assertEqual(12, resolved["density"]["gantt"]["max_rows"])


if __name__ == "__main__":
    unittest.main()
