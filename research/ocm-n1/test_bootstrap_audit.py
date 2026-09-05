from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bootstrap_audit  # noqa: E402


class BootstrapAuditTests(unittest.TestCase):
    def test_audit_binds_current_sources_and_inventory(self):
        r = bootstrap_audit.verify()
        self.assertEqual(r["source_bindings"], "PASS")
        self.assertTrue(r["strong_authored_language_prior_present"])
        self.assertEqual(r["inventory"]["microworld_seed_lexemes"], 26)
        self.assertEqual(r["inventory"]["microworld_seed_morph_rules"], 10)
        self.assertEqual(len(r["inventory"]["seed_constructions"]), 7)

    def test_current_runtime_is_not_mislabeled_minimal(self):
        r = bootstrap_audit.verify()
        self.assertEqual(r["terminal"], "CURRENT_RUNTIME_BOOTSTRAP_NOT_MINIMAL__N1_MINIMAL_TARGET_REGISTERED")
        self.assertGreater(r["minimal_target_excluded_classes"], 0)

    def test_language_prior_counts_include_communication_policy(self):
        r = bootstrap_audit.verify()
        inv = r["inventory"]
        self.assertEqual(inv["fixed_dialogue_acts"], 11)
        self.assertEqual(inv["fixed_reference_pronouns"], 9)
        self.assertEqual(inv["fixed_reference_ordinals"], 5)
        self.assertEqual(inv["fixed_world_surface_phrase_templates"], 16)
        self.assertTrue(inv["clarification_question_forms_executable"])


if __name__ == "__main__":
    unittest.main()
