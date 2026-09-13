import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MODULE_PATH = HERE / "grand_gmi_generalization_radius_checks_v1.py"
spec = importlib.util.spec_from_file_location("grand_gmi_generalization_radius_checks_v1", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIGeneralizationRadiusV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = mod.run()

    def test_aggregate_green(self):
        self.assertTrue(self.result["all_checks_green"])
        self.assertEqual(
            self.result["terminal"],
            "GRAND_GMI_GENERALIZATION_RADIUS_TRANCHE_ALL_GREEN",
        )

    def test_exact_direct_counts(self):
        o = self.result["observed"]
        self.assertEqual(o["direct_cases"], 1296)
        self.assertEqual(o["direct_radius_equals_bruteforce"], 1296)
        self.assertEqual(o["exact_identifiable"], 132)
        self.assertEqual(o["radius_histogram"], {"0": 132, "1": 1164})

    def test_refinement_monotonicity(self):
        o = self.result["observed"]
        self.assertEqual(o["refinement_pairs"], 462)
        self.assertEqual(o["refinement_target_cases"], 37422)
        self.assertEqual(o["refinement_monotone"], 37422)
        self.assertEqual(o["strict_refinement_improvements"], 6120)

    def test_nonidentifiability_witness(self):
        w = self.result["first_nonidentifiable_witness"]
        self.assertNotEqual(w["target_values"][0], w["target_values"][1])
        self.assertGreater(w["minimax_radius"], 0)

    def test_refinement_witness(self):
        w = self.result["first_strict_refinement_witness"]
        self.assertLess(w["fine_radius"], w["coarse_radius"])


if __name__ == "__main__":
    unittest.main()
