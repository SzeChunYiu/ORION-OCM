import importlib.util
import pathlib
import unittest
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = _load("grand_gmi_family_phase_soundness_checks_v1")
SECTOR = _load("grand_gmi_family_phase_checks_v1")


class FamilyPhaseSoundnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_terminal(self):
        self.assertEqual(
            self.aggregate["terminal"],
            "GRAND_GMI_FAMILY_PHASE_SOUNDNESS_CORRECTION_GREEN_AT_FINITE_SCOPE",
        )
        self.assertFalse(self.aggregate["empirical_hardware_cost_claimed"])

    def test_withdrawn_crossover_condition_is_vacuous(self):
        r = self.aggregate["stated_crossover_condition_is_vacuous"]
        self.assertEqual(r["ordered_pairs_enumerated"], 225)
        self.assertEqual(r["robust_b_configurations"], 35)
        self.assertTrue(r["stated_condition_holds_at_every_robust_b_point"])
        self.assertFalse(r["stated_condition_identifies_a_boundary"])

    def test_connected_crossover_abstains_pairwise(self):
        r = self.aggregate["connected_pairwise_crossover"]
        self.assertEqual(r["crossover_parameter"], "3/10")
        self.assertEqual(r["touching_bounds_upper_a_equals_lower_b"], "19/5")
        self.assertTrue(r["neither_family_robust_at_crossover"])

    def test_discrete_register_has_no_boundary(self):
        r = self.aggregate["discrete_register_counterexample"]
        self.assertEqual(r["verdicts"], {"1": "A", "2": "B"})
        self.assertFalse(r["abstention_parameter_exists"])

    def test_pairwise_abstention_is_not_global(self):
        r = self.aggregate["third_family_defeats_pairwise_abstention"]
        self.assertEqual(r["pairwise_verdict_at_crossover"], "UNDECIDED_FROM_CURRENT_EVIDENCE")
        self.assertEqual(r["three_family_verdict_at_crossover"], "C")

    def test_malformed_intervals_are_rejected_not_compared(self):
        r = self.aggregate["malformed_intervals_require_abstention"]
        self.assertEqual(r["unvalidated_two_winner_witness"], ["A", "B"])
        self.assertEqual(r["grid_configurations_enumerated"], 625)
        self.assertEqual(r["malformed_multi_winner_configurations"], 100)
        self.assertEqual(r["well_formed_multi_winner_configurations"], 0)
        with self.assertRaises(MOD.PhaseInputError):
            MOD.robust_winner({"A": (Fraction(5), Fraction(0))})
        with self.assertRaises(MOD.PhaseInputError):
            MOD.robust_winner({})

    def test_sector_checker_validates_intervals(self):
        with self.assertRaises(SECTOR.PhaseInputError):
            SECTOR.robust_scalar_winner({"A": (5, 0), "B": (5, 0)})
        with self.assertRaises(SECTOR.PhaseInputError):
            SECTOR.robust_scalar_winner({})
        self.assertEqual(SECTOR.robust_scalar_winner({"A": (1, 2), "B": (5, 6)}), "A")

    def test_upper_bound_is_not_a_lower_bound_term(self):
        r = self.aggregate["pure_family_lower_bound_misuse"]
        self.assertEqual(r["predecessor_pure_neural_lower_bound"], 12)
        self.assertEqual(r["sound_pure_neural_lower_bound"], 8)
        self.assertEqual(r["sound_pure_non_neural_lower_bound"], 9)
        self.assertEqual(r["hybrid_upper_bound"], 8)
        self.assertTrue(r["sound_neural_exclusion_fails"])
        self.assertTrue(r["sound_non_neural_exclusion_survives"])
        self.assertEqual(r["corrected_verdict"], "UNDECIDED_FROM_CURRENT_EVIDENCE")

    def test_repaired_registration_recovers_the_verdict(self):
        r = self.aggregate["repaired_registration_recovers_hybrid"]
        self.assertEqual(r["sound_pure_neural_lower_bound"], 12)
        self.assertEqual(r["sound_pure_non_neural_lower_bound"], 12)
        self.assertTrue(r["hybrid_robustly_selected_after_repair"])

    def test_decomposition_closure_is_required(self):
        r = self.aggregate["decomposition_closure_is_required"]
        self.assertEqual(r["verdict_under_decomposition_closed_class"], "HYBRID")
        self.assertEqual(
            r["verdict_without_decomposition_closure"], "UNDECIDED_FROM_CURRENT_EVIDENCE"
        )
        self.assertEqual(r["monolithic_pure_neural_cost"], 6)


if __name__ == "__main__":
    unittest.main()
