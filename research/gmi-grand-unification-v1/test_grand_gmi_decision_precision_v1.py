import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_decision_precision_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_decision_precision_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIDecisionPrecisionV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.run()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_ROBUST_DECISION_PRECISION_TRANCHE_ALL_GREEN",
        )

    def test_exact_counts(self):
        self.assertEqual(self.result["observed"], self.result["expected"])
        self.assertEqual(self.result["observed"]["total_cases"], 2985984)

    def test_sharp_regret(self):
        self.assertEqual(self.result["observed"]["maximum_observed_regret"], 2)
        self.assertGreater(self.result["observed"]["margin_lt_2delta_wrong_or_tied"], 0)
        self.assertGreater(self.result["observed"]["margin_eq_2delta_forced_ties"], 0)

    def test_supercritical_margin_stable(self):
        o = self.result["observed"]
        self.assertEqual(
            o["stable_margin_gt_2delta_applicable"],
            o["stable_margin_gt_2delta_ok"],
        )

    def test_witnesses_exist(self):
        self.assertIsNotNone(self.result["first_subcritical_instability_witness"])
        self.assertIsNotNone(self.result["first_exact_boundary_tie_witness"])


if __name__ == "__main__":
    unittest.main()
