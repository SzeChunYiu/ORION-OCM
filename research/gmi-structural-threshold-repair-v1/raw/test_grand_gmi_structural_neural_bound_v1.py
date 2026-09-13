import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_structural_neural_bound_checks_v1",
    HERE / "grand_gmi_structural_neural_bound_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class StructuralNeuralBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_terminal_and_no_timing(self):
        self.assertEqual(
            self.aggregate["terminal"],
            "GRAND_GMI_STRUCTURAL_NEURAL_BOUND_GREEN_AT_FINITE_SCOPE",
        )
        self.assertFalse(self.aggregate["timing_measurement_used"])
        self.assertFalse(self.aggregate["structural_exclusion"]["timing_used"])

    def test_sn2_behaviour_set_is_saturated(self):
        r = self.aggregate["behaviour_saturation"]
        self.assertEqual(r["behaviours_registered_range"], 104)
        self.assertEqual(r["behaviours_wider_range"], 104)
        self.assertTrue(r["behaviour_sets_identical"])
        self.assertTrue(r["wider_range_never_cheaper"])

    def test_sn3_few_unit_networks_are_infeasible(self):
        r = self.aggregate["grammar_minimum"]
        self.assertIsNone(r["per_unit_count"]["1"])
        self.assertIsNone(r["per_unit_count"]["2"])
        self.assertIsNotNone(r["per_unit_count"]["3"])
        self.assertTrue(r["one_and_two_unit_networks_infeasible"])

    def test_sn3_minimum_is_attained_and_additive(self):
        r = self.aggregate["grammar_minimum"]
        self.assertTrue(r["minimizer_predicted_equals_compiled"])
        self.assertTrue(r["minimizer_computes_parity"])
        self.assertEqual(r["derived_minimum_per_full_domain_sweep"],
                         r["derived_minimum_per_call"] * 8)
        # The minimizer must be a real member of the registered grammar.
        self.assertIn("int(", r["minimizer_source"])
        self.assertIn("a, b, c = x", r["minimizer_source"])

    def test_sn4_large_unit_counts_are_excluded_by_a_cost_floor(self):
        r = self.aggregate["unbounded_unit_count_excluded"]
        self.assertGreater(r["minimum_hidden_unit_line_cost"], 0)
        self.assertGreaterEqual(r["floor_at_five_units"], r["enumerated_minimum_per_call"])
        self.assertTrue(r["enumeration_complete_over_unit_count"])

    def test_sn5_class_exclusion_holds_with_a_margin(self):
        r = self.aggregate["structural_exclusion"]
        self.assertLess(r["non_neural_witness_per_sweep"],
                        r["derived_class_lower_bound_per_sweep"])
        self.assertGreater(r["margin_per_sweep"], 0)
        self.assertTrue(r["structural_exclusion_holds"])
        self.assertTrue(r["covers_unwritten_members_of_the_class"])
        self.assertEqual(r["coordinate"], "python_opcode_count_per_full_domain_sweep")

    def test_sn6_registered_candidate_attains_the_bound(self):
        r = self.aggregate["registered_candidates_are_grammar_optimal"]
        self.assertEqual(r["registered_shared_sum_net_per_call"], r["derived_minimum_per_call"])
        self.assertTrue(r["registered_candidate_attains_the_bound"])
        self.assertTrue(r["bound_is_tight_in_the_pl3b_sense"])
        self.assertGreater(r["registered_dnf_net_per_call"], r["derived_minimum_per_call"])

    def test_sn6a_optimum_is_not_unique(self):
        r = self.aggregate["registered_candidates_are_grammar_optimal"]
        self.assertTrue(r["minimizer_differs_from_registered_candidate"])

    def test_sn7_delegation_is_outside_the_coordinate(self):
        r = self.aggregate["delegation_outside_the_coordinate"]
        counts = r["per_sweep_counts"]
        self.assertLess(counts["threshold_net_delegating_the_sum"],
                        counts["class_member_written_arithmetic"])
        self.assertLess(counts["non_neural_written_xor"],
                        counts["class_member_written_arithmetic"])
        self.assertLess(counts["non_neural_delegating"],
                        counts["threshold_net_delegating_the_sum"])
        self.assertEqual(r["candidate_frame_calls"]["non_neural_written_xor"], 0)
        self.assertTrue(r["callees_have_no_python_code_object"])
        self.assertTrue(r["derived_bound_is_relative_to_the_non_delegating_rendering"])
        self.assertTrue(r["exclusion_is_conservative_under_delegation"])
        self.assertFalse(r["timing_used"])

    def test_residue_names_delegation(self):
        r = self.aggregate["residue"]
        self.assertTrue(any("delegate" in x for x in r["open_residue"]))

    def test_residue_is_stated_and_non_empty(self):
        r = self.aggregate["residue"]
        self.assertTrue(r["open_residue"])
        self.assertTrue(any("hidden layer" in x for x in r["open_residue"]))
        self.assertTrue(any("precompute" in x for x in r["open_residue"]))
        self.assertIn("scope", r["predicate_is_a_scope_choice"])

    def test_canonical_rendering_is_minimal(self):
        self.assertEqual(MOD.linear_text((1, 0, 0), MOD.NAMES), "a")
        self.assertEqual(MOD.linear_text((-1, 0, 0), MOD.NAMES), "-a")
        self.assertEqual(MOD.linear_text((1, -1, -1), MOD.NAMES), "a - b - c")
        self.assertEqual(MOD.linear_text((2, 0, 1), MOD.NAMES), "2*a + c")
        self.assertEqual(MOD.linear_text((0, 0, 0), MOD.NAMES), "0")

    def test_grammar_rejects_non_straight_line_code(self):
        with self.assertRaises(MOD.StructuralBoundError):
            MOD.opcode_count("def f(x):\n    return 1 if x else 0\n")


if __name__ == "__main__":
    unittest.main()
