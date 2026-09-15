from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest

MODULE_PATH = Path(__file__).with_name("finite_scaling_v1.py")
spec = importlib.util.spec_from_file_location("finite_scaling_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class FiniteScalingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = mod.build_receipt()

    def test_exact_crossover(self):
        row = self.receipt["work_crossover"]
        self.assertEqual(row["D_10"], -2)
        self.assertEqual(row["D_11"], 10)
        self.assertEqual(row["integer_transition_count"], 1)
        self.assertEqual(row["integer_transitions"], [{"from_n":10,"to_n":11,"from":"Q","to":"L"}])
        self.assertTrue(row["Q_wins_n_1_through_10"])
        self.assertTrue(row["L_wins_n_11_through_128"])

    def test_no_hidden_extra_crossings(self):
        winners = [mod.work_winner(n) for n in range(1,129)]
        self.assertEqual(winners[:10], ["Q"] * 10)
        self.assertEqual(winners[10:], ["L"] * 118)
        self.assertNotIn("TIE", winners)

    def test_finite_size_correction_and_failed_extrapolation(self):
        row = self.receipt["finite_size_correction"]
        self.assertEqual(row["relative_correction"], "4/(3n)")
        self.assertEqual(row["first_n_within_tolerance"], 27)
        self.assertEqual(row["n10_relative_correction"], "2/15")
        self.assertEqual(row["asymptotic_n10_winner"], "L")
        self.assertEqual(row["exact_n10_winner"], "Q")
        self.assertGreater(mod.finite_relative_correction(26), F(1,20))
        self.assertLessEqual(mod.finite_relative_correction(27), F(1,20))

    def test_smooth_control_has_no_selection_transition(self):
        row = self.receipt["smooth_vs_crossover"]
        self.assertTrue(row["both_smooth_for_x_gt_0"])
        self.assertFalse(row["thermodynamic_phase_transition_proved"])
        self.assertEqual(row["smooth_control"]["transition_count_n1_128"], 0)
        self.assertTrue(all(mod.smooth_control_winner(n)=="A" for n in range(1,129)))

    def test_bottleneck_equivalence_exhaustive(self):
        row = self.receipt["bottleneck"]["exact_exhaustive_control"]
        self.assertEqual(row["cases"], 3375)
        self.assertEqual(row["failures"], 0)
        self.assertTrue(row["all_green"])

    def test_n11_capability_threshold_and_twin(self):
        row = self.receipt["bottleneck"]["threshold_n11"]
        self.assertEqual(row["requirements_L_n11"], [111,15,22])
        self.assertFalse(row["below"]["feasible"])
        self.assertTrue(row["at"]["feasible"])
        self.assertFalse(row["memory_negative_twin"]["feasible"])

    def test_binary_saturation(self):
        row = self.receipt["bottleneck"]["saturation_control"]
        self.assertEqual(row["before_extra_work"]["sigma"], "1")
        self.assertEqual(row["after_extra_work"]["sigma"], "1")
        self.assertEqual(row["before_extra_work"]["bottlenecks"], ["memory","verify"])
        self.assertEqual(row["after_extra_work"]["bottlenecks"], ["memory","verify"])
        self.assertTrue(row["binary_feasibility_unchanged"])

    def test_resource_coordinate_winner_reversal_and_pareto(self):
        row = self.receipt["nonuniversality"]
        self.assertEqual(row["work_winner_n11"], "L")
        self.assertEqual(row["verify_winner_n11"], "Q")
        self.assertFalse(row["pareto"]["Q_dominates_L"])
        self.assertFalse(row["pareto"]["L_dominates_Q"])
        self.assertTrue(row["full_vector_nondominance"])

    def test_generic_bottleneck_edges(self):
        self.assertTrue(mod.feasible((1,1,1),(1,1,1)))
        self.assertFalse(mod.feasible((100,0,100),(1,1,1)))
        sigma,bottlenecks,ratios = mod.slack((2,4,6),(1,2,3))
        self.assertEqual(sigma, 2)
        self.assertEqual(set(bottlenecks), {"work","memory","verify"})
        self.assertEqual(ratios, (F(2),F(2),F(2)))

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError): mod.req("Q",0)
        with self.assertRaises(ValueError): mod.req("X",1)
        with self.assertRaises(ValueError): mod.slack((1,2),(1,2,3))
        with self.assertRaises(ValueError): mod.slack((-1,2,3),(1,2,3))
        with self.assertRaises(ValueError): mod.slack((1,2,3),(0,2,3))
        with self.assertRaises(ValueError): mod.dominates((1,2),(1,2,3))

    def test_claim_boundary(self):
        self.assertEqual(self.receipt["claim_ceiling"], mod.CLAIM)
        self.assertIn("THERMODYNAMIC_PHASE_TRANSITION_PROVED", self.receipt["forbidden_claims"])
        self.assertIn("UNIVERSAL_SCALING_EXPONENT", self.receipt["forbidden_claims"])
        self.assertIn("COMPLETE_GMI", self.receipt["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
