from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

from minimal_morphology_recovery import run  # noqa: E402


class MinimalMorphologyRecoveryTests(unittest.TestCase):
    def test_zero_rule_start_and_hybrid_recovery(self):
        result = run()
        self.assertEqual(result["time_zero_morph_rules"], 0)
        self.assertGreaterEqual(result["productive_rule_objects"], 1)
        self.assertEqual(result["exception_rule_objects"], 1)
        self.assertEqual(result["exceptions"], 1)

    def test_productive_rule_generalizes_to_held_out_verb(self):
        result = run()
        self.assertTrue(result["held_out_jump_generalizes"])
        self.assertTrue(result["regular_seen_open_recognized"])
        self.assertTrue(result["irregular_see_recognized"])

    def test_productive_and_exception_support_are_revocable(self):
        result = run()
        self.assertTrue(result["productive_support_revocation_removes_held_out_form"])
        self.assertTrue(result["exception_support_revocation_removes_irregular_form"])
        self.assertTrue(result["exception_live_before_revocation"])
        self.assertTrue(result["exception_dead_after_revocation"])

    def test_receipt_stays_calibration_only(self):
        result = run()
        self.assertFalse(result["protected_claim_authority"])
        self.assertEqual(result["terminal"], "ZERO_MORPHOLOGY_RULES_RECOVER_PRODUCTIVE_PLUS_EXCEPTION_CALIBRATION")


if __name__ == "__main__":
    unittest.main()
