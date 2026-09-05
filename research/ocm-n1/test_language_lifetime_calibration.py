from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from language_lifetime_calibration import run, run_arm  # noqa: E402


class LanguageLifetimeCalibrationTests(unittest.TestCase):
    def test_related_nested_families_get_cheaper_than_reset(self):
        result = run()
        self.assertEqual(result["related_observation_curve_ocm"], [2, 1, 1])
        self.assertEqual(result["related_observation_curve_reset"], [2, 3, 4])
        self.assertTrue(result["amortization_present_vs_reset"])

    def test_unrelated_language_receives_no_cross_scope_reuse(self):
        result = run()
        self.assertEqual(result["unrelated_scope_reuse_count"], 0)

    def test_harmful_transfer_is_detected_and_does_not_increase_information_cost(self):
        result = run()
        self.assertTrue(result["harmful_transfer_rejected"])
        self.assertTrue(result["harmful_task_cost_equals_reset"])

    def test_strong_persistent_skill_parent_matches_exactly(self):
        result = run()
        self.assertTrue(result["strong_parent_matches_exactly"])
        self.assertEqual(result["isolated_terminal"], "PARENT_SUFFICIENT")
        self.assertEqual(result["meta_learning_terminal"], "NO_META_LEARNING_CLAIM_FROM_CONSTRAINT_REUSE")

    def test_every_arm_learns_registered_unique_orders(self):
        for persistent in (False, True):
            for receipt in run_arm(persistent=persistent):
                self.assertGreaterEqual(receipt.observations_consumed, 1)
                self.assertEqual(len(receipt.surviving_order), len(set(receipt.surviving_order)))


if __name__ == "__main__":
    unittest.main()
