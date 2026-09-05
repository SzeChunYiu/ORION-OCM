from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from multilingual_scoping import run  # noqa: E402


class MultilingualScopingTests(unittest.TestCase):
    def test_same_machine_adds_incompatible_languages_after_initialization(self):
        result = run()
        self.assertEqual(result["language_registrations_at_initialization"], 0)
        self.assertEqual(result["languages_learned_after_initialization"], ["lang-sov", "lang-svo"])
        self.assertTrue(result["same_machine_class_reused"])
        self.assertTrue(result["state_growth"]["second_language_added_persistently"])

    def test_surface_orders_are_scope_local_but_semantics_match(self):
        result = run()
        self.assertTrue(result["semantic_equivalence_across_surface_orders"])
        self.assertTrue(result["conflicting_surface_order_is_scope_local"])
        self.assertTrue(result["construction_scope_check_refuses_cross_language_use"])

    def test_revocation_is_local_to_language_inventory(self):
        result = run()
        self.assertTrue(result["revision_locality"]["revoked_language_loses_competence"])
        self.assertTrue(result["revision_locality"]["other_language_retains_competence"])

    def test_unknown_language_and_parent_terminal_are_explicit(self):
        result = run()
        self.assertTrue(result["unknown_language_terminal"].startswith("UNKNOWN_LANGUAGE:"))
        self.assertTrue(result["explicit_language_context_required"])
        self.assertEqual(result["isolated_terminal"], "PARENT_SUFFICIENT_SCOPED_MULTILINGUAL_REGISTRY")
        self.assertFalse(result["protected_claim_authority"])


if __name__ == "__main__":
    unittest.main()
