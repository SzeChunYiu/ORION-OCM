import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_phenomenology_checks_v1",
    HERE / "grand_gmi_phenomenology_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIPhenomenologyTests(unittest.TestCase):
    def test_memory(self):
        r = MOD.check_temporal_memory()
        self.assertEqual(r["encoding_checks"], 71992)
        self.assertTrue(r["all_minimum_states_equal_message_count"])
        self.assertEqual(r["rows"][-1]["minimum_memory_states"], 6)

    def test_dynamic_routing(self):
        r = MOD.check_conditional_routing()
        self.assertEqual(r["routes"]["0"]["best_correct_of_8"], 6)
        self.assertEqual(r["routes"]["1"]["best_correct_of_8"], 6)
        self.assertEqual(r["routes"]["dynamic"]["best_correct_of_8"], 8)
        self.assertTrue(r["dynamic_strictly_better_than_every_fixed_route"])

    def test_in_context(self):
        r = MOD.check_in_context_side_information()
        self.assertEqual(r["no_prompt_best_correct_of_4"], 2)
        self.assertEqual(r["prompt_best_correct_of_4"], 4)
        self.assertEqual(r["perfect_prompt_policies"], 1)

    def test_retention(self):
        r = MOD.check_continual_retention()
        self.assertEqual(r["encoding_checks"], 354)
        self.assertEqual(r["minimum_final_states"], 4)
        self.assertEqual(r["minimum_bits"], 2)

    def test_tool_boundary(self):
        r = MOD.check_tool_parity_boundary()
        self.assertEqual(r["pivotal_bit_checks"], 78)
        self.assertEqual(r["rows"][-1]["exact_worst_case_bit_queries_without_tool"], 12)
        self.assertEqual(r["rows"][-1]["exact_parity_tool_calls"], 1)

    def test_feature_sufficiency(self):
        r = MOD.check_feature_sufficiency()
        self.assertEqual(r["fixed_phi_x0_best_correct_of_4"], 2)
        self.assertEqual(r["semantic_sufficient_parity_feature_best_correct_of_4"], 4)

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_PHENOMENOLOGY_REDUCTION_TRANCHE_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
