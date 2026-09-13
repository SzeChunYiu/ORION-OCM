import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_compositional_language_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_compositional_language_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMICompositionalLanguageV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.run()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_COMPOSITIONAL_LANGUAGE_TRANCHE_ALL_GREEN",
        )

    def test_phase_counts(self):
        phase = self.result["phase"]
        self.assertEqual(phase["configuration_count"], 336)
        self.assertEqual(phase["partition_profile_count"], 4192)
        self.assertEqual(phase["phase_cells"], 43008)
        self.assertEqual(phase["monotone_sweeps_ok"], 2688)
        self.assertEqual(phase["monotone_sweeps"], 2688)

    def test_three_phase_witness(self):
        w = self.result["canonical_ternary_three_role_witness"]
        self.assertEqual(w["1"]["optimal_block_counts"], [3])
        self.assertEqual(w["5"]["optimal_block_counts"], [2])
        self.assertEqual(w["20"]["optimal_block_counts"], [1])

    def test_leave_one_out_recombination(self):
        r = self.result["recombination"]
        self.assertEqual(r["nonholistic_leave_one_out_checks"], 94851)
        self.assertEqual(r["nonholistic_recombination_success"], 94851)
        self.assertEqual(r["holistic_missing_entries"], 7371)

    def test_extreme_profiles(self):
        sizes = (3, 4, 5)
        hol = ((0, 1, 2),)
        comp = ((0,), (1,), (2,))
        self.assertEqual(mod.partition_profile(sizes, hol), (60, 1))
        self.assertEqual(mod.partition_profile(sizes, comp), (12, 3))


if __name__ == "__main__":
    unittest.main()
