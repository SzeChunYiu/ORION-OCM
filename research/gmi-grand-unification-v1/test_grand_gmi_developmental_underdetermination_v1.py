import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_developmental_underdetermination_checks_v1",
    HERE / "grand_gmi_developmental_underdetermination_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DevelopmentalUnderdeterminationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aggregate = MOD.run()

    def test_terminal_and_ceiling(self):
        self.assertEqual(
            self.aggregate["terminal"],
            "GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_GREEN_AT_FINITE_SCOPE",
        )
        self.assertFalse(self.aggregate["learning_process_measured"])

    def test_du1_same_data_different_verdict(self):
        r = self.aggregate["realization_data_does_not_determine_reachability"]
        self.assertEqual(r["shared_global_best_by_family"], {"NEURAL": 5, "NON_NEURAL": 3})
        self.assertEqual(r["per_development_law"]["D1_grows_neural"]["verdict"], "NEURAL")
        self.assertEqual(
            r["per_development_law"]["D2_grows_non_neural"]["verdict"], "NON_NEURAL"
        )
        self.assertTrue(r["reachable_frontier_is_not_a_function_of_realization_data"])

    def test_du2_schedule_is_load_bearing(self):
        r = self.aggregate["schedule_matters_not_just_the_update_set"]
        self.assertTrue(r["schedules"]["double->add_three"]["admitted"])
        self.assertFalse(r["schedules"]["add_three->double"]["admitted"])
        self.assertEqual(r["schedules"]["double->add_three"]["result"], 5)
        self.assertEqual(r["schedules"]["add_three->double"]["result"], 8)

    def test_du3_bounds_rise_while_the_verdict_inverts(self):
        r = self.aggregate["reachability_asymmetry"]
        self.assertEqual(r["global_best_by_family"], {"A": 2, "B": 5})
        self.assertEqual(r["reachable_best_by_family"], {"A": 9, "B": 5})
        self.assertEqual(r["global_verdict"], "A")
        self.assertEqual(r["reachable_verdict"], "B")
        self.assertTrue(r["reachability_never_lowers_a_lower_bound"])

    def test_du4_no_finite_budget_extrapolates(self):
        r = self.aggregate["no_finite_budget_certifies_the_limit"]
        self.assertEqual(r["chain_length"], 8)
        self.assertEqual(
            [r["per_budget"][str(b)]["frontier"] for b in range(1, 9)],
            [9, 8, 7, 6, 5, 4, 3, 2],
        )
        verdicts = [r["per_budget"][str(b)]["verdict"] for b in range(1, 9)]
        self.assertEqual(len(set(verdicts)), 2)
        for i in range(len(verdicts) - 1):
            self.assertNotEqual(verdicts[i], verdicts[i + 1])


if __name__ == "__main__":
    unittest.main()
