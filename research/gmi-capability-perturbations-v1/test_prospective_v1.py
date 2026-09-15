from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("prospective_score_v1.py")
spec = importlib.util.spec_from_file_location("prospective_score_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class ProspectiveCapabilityPerturbationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = mod.load_freeze()
        cls.receipt = mod.score_freeze(cls.freeze)

    def test_registered_result_counts(self):
        self.assertEqual(self.receipt["cases_scored"], 12)
        self.assertEqual(self.receipt["point_target_cells"], 48)
        self.assertEqual(self.receipt["determinate_cells"], 40)
        self.assertEqual(self.receipt["determinate_correct"], 40)
        self.assertEqual(self.receipt["abstentions"], 8)
        self.assertFalse(self.receipt["abstentions_count_as_success"])
        self.assertEqual(self.receipt["verdict"], "PASS")

    def test_main_deficit_sets(self):
        rows = self.receipt["transformations"]
        self.assertEqual(rows["ablation_main"]["direct_deficit_set"], ["memory_exact", "planning_exact"])
        self.assertEqual(rows["repricing_main"]["direct_deficit_set"], ["verified_tool_exact"])
        self.assertEqual(rows["drift_main"]["direct_deficit_set"], ["coordination_exact"])

    def test_safe_controls_do_not_change(self):
        rows = self.receipt["transformations"]
        for name in ("ablation_safe", "repricing_safe", "drift_safe"):
            self.assertEqual(rows[name]["direct_deficit_set"], [])
            for case_id in (rows[name]["pre"], rows[name]["post"]):
                self.assertEqual(self.receipt["cases"][case_id]["oracle"], [1, 1, 1, 1])
                self.assertEqual(self.receipt["cases"][case_id]["predictor"], [1, 1, 1, 1])

    def test_frozen_abstention_locations(self):
        C = mod.CANNOT_IDENTIFY
        self.assertEqual(self.receipt["cases"]["A_post"]["predictor"], [0, 0, C, C])
        self.assertEqual(self.receipt["cases"]["R_post"]["predictor"], [C, C, C, 0])
        self.assertEqual(self.receipt["cases"]["D_post"]["predictor"], [C, C, 0, C])

    def test_independent_oracle_is_separate_from_predictor_helper(self):
        point = mod._point_dict([0, 0, 0, -2, 0])
        expected = {
            "memory_exact": 1,
            "planning_exact": 1,
            "coordination_exact": 1,
            "verified_tool_exact": 0,
        }
        self.assertEqual(mod.independent_oracle(point), expected)

    def test_predictor_blob_drift_fails_closed(self):
        mutated = copy.deepcopy(self.freeze)
        mutated["pinned_predictor"]["git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(RuntimeError, "PINNED_PREDICTOR_BLOB_DRIFT"):
            mod.score_freeze(mutated)

    def test_transformation_tampering_fails_closed(self):
        mutated = copy.deepcopy(self.freeze)
        mutated["transformations"]["repricing_main"]["price_to"] = 6
        with self.assertRaisesRegex(ValueError, "repricing arithmetic"):
            mod.validate_freeze(mutated)

    def test_hidden_development_grid_substitution_fails_closed(self):
        mutated = copy.deepcopy(self.freeze)
        for row in mutated["cases"]:
            if row["id"] == "A_post":
                row["point"] = [-1, 0, 0, 0, 0]
        with self.assertRaisesRegex(ValueError, "substituted back inside development grid"):
            mod.validate_freeze(mutated)

    def test_outcome_aware_expected_vector_mutation_fails(self):
        mutated = copy.deepcopy(self.freeze)
        for row in mutated["cases"]:
            if row["id"] == "A_post":
                row["predictor"][0] = 1
        with self.assertRaisesRegex(RuntimeError, "FROZEN_PREDICTOR_VECTOR_MISMATCH"):
            mod.score_freeze(mutated)

    def test_abstention_cannot_be_relabelled_success(self):
        self.assertGreater(self.receipt["abstentions"], 0)
        self.assertEqual(
            self.receipt["determinate_correct"],
            self.receipt["determinate_cells"],
        )
        self.assertNotEqual(
            self.receipt["determinate_correct"],
            self.receipt["point_target_cells"],
        )

    def test_claim_ceiling(self):
        self.assertEqual(self.receipt["claim_ceiling"], mod.CLAIM)
        self.assertIn("COMPLETE_GMI", self.receipt["forbidden_claims"])
        self.assertIn("REAL_WORLD_PERTURBATION_CALIBRATION", self.receipt["forbidden_claims"])
        self.assertIn("UNIVERSAL_CAPABILITY_PREDICTOR", self.receipt["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
