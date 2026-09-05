import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "machine-epistemics-lifetime-v1"))

from ocm.evaluation.lifetime_metrics import CheckStatus, ResourceVector, StateMeasure, TouchMeasure  # noqa: E402
import calibration  # noqa: E402


class LifetimeMetricTests(unittest.TestCase):
    def test_k_is_union_of_unique_actual_touches(self):
        state = StateMeasure({"objects": 10}, object_grammar="test")
        touch = TouchMeasure(("a", "b", "c"))
        self.assertEqual(touch.k, 3)
        self.assertEqual(touch.k_over_n(state), 0.3)
        with self.assertRaises(ValueError):
            TouchMeasure(("a", "a"))

    def test_k_cannot_exceed_n(self):
        state = StateMeasure({"objects": 1}, object_grammar="test")
        with self.assertRaises(ValueError):
            TouchMeasure(("a", "b")).k_over_n(state)

    def test_resource_vector_does_not_hide_coordinates(self):
        a = ResourceVector(work_units=2, index_read_entries=3)
        b = ResourceVector(work_units=5, persistent_write_bytes=7)
        c = a.plus(b)
        self.assertEqual(c.work_units, 7)
        self.assertEqual(c.index_read_entries, 3)
        self.assertEqual(c.persistent_write_bytes, 7)

    def test_amortized_acquisition_is_parent_sufficient_in_toy(self):
        r = calibration.acquisition_calibration()
        self.assertTrue(r["signature_present"])
        self.assertEqual([x["acquisition_work_units"] for x in r["ocm"]], [4, 2, 2, 2])
        self.assertEqual(r["ocm"], r["skill_library_parent"])
        self.assertEqual(r["isolated_terminal"], "PARENT_SUFFICIENT")

    def test_sparse_meter_catches_global_scan(self):
        r = calibration.sparse_scaling_calibration()
        for row in r["rows"]:
            self.assertEqual(row["oracle_sparse_k"], 5)
            self.assertEqual(row["global_scan_k"], row["N"])
            self.assertLess(row["oracle_sparse_k_over_N"], row["global_scan_k_over_N"])
        ratios = [row["oracle_sparse_k_over_N"] for row in r["rows"]]
        self.assertTrue(all(a > b for a, b in zip(ratios, ratios[1:])))

    def test_revision_exact_and_hostile_mutants(self):
        r = calibration.revision_calibration()
        self.assertTrue(r["alternate_support_survives"])
        self.assertTrue(r["exact"]["exact_revocation"])
        self.assertTrue(r["exact"]["exact_restoration"])
        self.assertEqual(r["exact"]["precision"], 1.0)
        self.assertEqual(r["exact"]["recall"], 1.0)
        self.assertTrue(r["under_revoke_hostile"]["caught"])
        self.assertLess(r["under_revoke_hostile"]["recall"], 1.0)
        self.assertTrue(r["over_revoke_hostile"]["caught"])
        self.assertLess(r["over_revoke_hostile"]["precision"], 1.0)

    def test_cannot_check_path(self):
        r = calibration.cannot_check_calibration()
        self.assertEqual(r["status"], CheckStatus.CANNOT_CHECK.value)
        self.assertIn("do not report k/N", r["required_behavior"])

    def test_current_simple_parent_is_not_strong_enough_for_all_hypotheses(self):
        r = calibration.comparator_calibration()
        self.assertEqual(r["H1_amortized_acquisition"]["current_simple"]["status"], "CANNOT_CHECK")
        self.assertEqual(r["H3_H4_local_exact_revision"]["current_simple"]["status"], "CANNOT_CHECK")
        self.assertEqual(r["H3_H4_local_exact_revision"]["composite"]["status"], "MATCHED")

    def test_run_is_deterministic_and_conservative(self):
        a = calibration.run()
        b = calibration.run()
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertFalse(a["protected_claim_authority"])
        self.assertTrue(a["confirmatory_terminal"].startswith("CANNOT_CHECK"))


if __name__ == "__main__":
    unittest.main()
