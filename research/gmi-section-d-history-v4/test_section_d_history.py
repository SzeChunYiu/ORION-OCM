import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("hist", ROOT / "section_d_history_witness.py")
hist = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = hist
SPEC.loader.exec_module(hist)


class DevelopmentalHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = hist.build_results()

    def test_all_frozen_predictions(self):
        self.assertTrue(self.r["all_frozen_predictions_pass"])
        self.assertTrue(all(self.r["assertions"].values()))

    def test_history_is_only_heldout_difference(self):
        held = self.r["heldout_m1"]
        self.assertEqual(held["same_present_scalar_occupancy"], 4)
        self.assertEqual(held["only_registered_difference"], "semantic installed orientation")
        self.assertEqual(held["H_key_pareto"], ["key_index"])
        self.assertEqual(held["H_value_pareto"], ["value_index"])
        self.assertEqual(held["H_key_vectors"]["key_index"]["lifecycle_ops"], 31)
        self.assertEqual(held["H_key_vectors"]["value_index"]["lifecycle_ops"], 33)
        self.assertEqual(held["H_value_vectors"]["value_index"]["lifecycle_ops"], 25)
        self.assertEqual(held["H_value_vectors"]["key_index"]["lifecycle_ops"], 39)

    def test_crossover_and_controls(self):
        main = self.r["phase_main"]
        self.assertEqual(main["H_key"]["1"]["all_pairs"], ["key_index"])
        for m in range(2, 9):
            self.assertEqual(main["H_key"][str(m)]["all_pairs"], ["value_index"])
        for m in range(1, 9):
            self.assertEqual(main["H_value"][str(m)]["all_pairs"], ["value_index"])
            self.assertEqual(self.r["controls"]["zero_K"]["H_key"][str(m)]["all_pairs"], ["value_index"])
            self.assertEqual(self.r["controls"]["zero_K"]["H_value"][str(m)]["all_pairs"], ["value_index"])
            self.assertEqual(self.r["controls"]["cold_start"][str(m)]["all_pairs"], ["value_index"])
        mirror = self.r["controls"]["mirrored_ecology"]
        self.assertEqual(mirror["H_value"]["1"]["all_pairs"], ["value_index"])
        for m in range(2, 9):
            self.assertEqual(mirror["H_value"][str(m)]["all_pairs"], ["key_index"])
        for m in range(1, 9):
            self.assertEqual(mirror["H_key"][str(m)]["all_pairs"], ["key_index"])

    def test_exhaustive_exactness_and_migration(self):
        ex = self.r["relation_family_exactness"]
        self.assertEqual(ex["bijections"], 24)
        self.assertEqual(ex["obligations_per_bijection"], 8)
        self.assertTrue(all(ex["all_exact"].values()))
        self.assertEqual(set(ex["checks_per_candidate"].values()), {192})
        mig = self.r["migration"]
        self.assertTrue(mig["all_exact"])
        self.assertEqual(mig["bijections_checked"], 24)
        self.assertEqual(mig["future_ops_seen"], [8])

    def test_general_theorem_grid(self):
        grid = self.r["general_theorem_grid"]
        self.assertEqual(grid["tuples_checked"], 4160)
        self.assertEqual(grid["from_H_A_outcomes"], {"A": 720, "tie": 135, "B": 3305})
        self.assertTrue(grid["all_pass"])

    def test_remint_and_selector_independence(self):
        rem = self.r["remint"]
        self.assertTrue(rem["all_exact"])
        self.assertTrue(rem["costs_preserved"])
        self.assertTrue(rem["heldout_history_collision_preserved"])
        self.assertEqual(rem["key_block_ops"], 23)
        self.assertEqual(rem["value_block_ops"], 17)
        for group in (
            self.r["phase_main"]["H_key"], self.r["phase_main"]["H_value"],
            self.r["controls"]["zero_K"]["H_key"], self.r["controls"]["zero_K"]["H_value"],
            self.r["controls"]["cold_start"],
            self.r["controls"]["mirrored_ecology"]["H_key"], self.r["controls"]["mirrored_ecology"]["H_value"],
        ):
            for m in range(1, 9):
                self.assertTrue(group[str(m)]["agree"])

    def test_committed_receipt_reproduces(self):
        committed = json.loads((ROOT / "RESULT_V4.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, self.r)


if __name__ == "__main__":
    unittest.main()
