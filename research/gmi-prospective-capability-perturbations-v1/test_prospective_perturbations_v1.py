from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("prospective_perturbations_v1.py")
spec = importlib.util.spec_from_file_location("prospective_perturbations_v1", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load prospective perturbation module")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class ProspectivePerturbationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred_mod = mod.load_predictor_module()
        cls.predictor = cls.pred_mod.fit_registered_development_predictor()

    def test_pinned_blob(self):
        self.assertEqual(mod.verify_predictor_blob(), mod.PINNED_PREDICTOR_BLOB)

    def test_all_frozen_cases(self):
        rows = {
            case_id: mod.evaluate_case(case_id, mod.CASES[case_id], self.predictor)
            for case_id in ("A0", "A1", "R0", "R1", "D0", "D1")
        }
        self.assertEqual(rows["A0"]["direct_deficit_set"], ["memory_exact", "planning_exact"])
        self.assertEqual(rows["R0"]["direct_deficit_set"], ["verified_tool_exact"])
        self.assertEqual(rows["D0"]["direct_deficit_set"], ["coordination_exact"])
        self.assertEqual(rows["A0"]["post_abstention_set"], ["coordination_exact", "verified_tool_exact"])
        self.assertEqual(rows["R0"]["post_abstention_set"], ["memory_exact", "planning_exact", "coordination_exact"])
        self.assertEqual(rows["D0"]["post_abstention_set"], ["memory_exact", "planning_exact", "verified_tool_exact"])
        for case_id in ("A1", "R1", "D1"):
            self.assertEqual(rows[case_id]["direct_deficit_set"], [])
            self.assertEqual(rows[case_id]["post_abstention_set"], [])
            self.assertTrue(rows[case_id]["safe_control"])

    def test_aggregate_accounting(self):
        receipt = mod.build_receipt()
        agg = receipt["aggregate"]
        self.assertEqual(agg["total_cells"], 48)
        self.assertEqual(agg["determinate_cells"], 40)
        self.assertEqual(agg["determinate_correct"], 40)
        self.assertEqual(agg["determinate_accuracy"], "40/40")
        self.assertEqual(agg["abstention_cells"], 8)
        self.assertTrue(agg["abstentions_excluded_from_accuracy"])
        self.assertTrue(agg["safe_controls_all_ones"])

    def test_repricer_reconstructs_not_trusts_post(self):
        case = copy.deepcopy(mod.CASES["R0"])
        case["frozen_post"] = (0, 0, 0, -1, 0)
        with self.assertRaises(ValueError):
            mod.evaluate_case("R0", case, self.predictor)

    def test_drift_reconstructs_not_trusts_post(self):
        case = copy.deepcopy(mod.CASES["D0"])
        case["transform"]["shock"] = 2
        with self.assertRaises(ValueError):
            mod.evaluate_case("D0", case, self.predictor)

    def test_abstention_cannot_be_laundered_as_correct(self):
        case = copy.deepcopy(mod.CASES["A0"])
        case["expected_post_predictor"] = (0, 0, 1, 1)
        with self.assertRaises(ValueError):
            mod.evaluate_case("A0", case, self.predictor)

    def test_development_grid_substitution_fails(self):
        case = copy.deepcopy(mod.CASES["A0"])
        case["transform"]["after"] = -1
        case["frozen_post"] = (-1, 0, 0, 0, 0)
        with self.assertRaises(ValueError):
            mod.evaluate_case("A0", case, self.predictor)

    def test_expected_oracle_mutation_fails(self):
        case = copy.deepcopy(mod.CASES["D0"])
        case["expected_post_oracle"] = (1, 1, 1, 1)
        with self.assertRaises(ValueError):
            mod.evaluate_case("D0", case, self.predictor)

    def test_hostiles_all_fail_closed(self):
        hostiles = mod.hostile_results(self.predictor)
        self.assertTrue(hostiles)
        self.assertTrue(all(value == "PASS_FAIL_CLOSED" for value in hostiles.values()))


if __name__ == "__main__":
    unittest.main()
