import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_continuous_checks_v1",
    HERE / "grand_gmi_continuous_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMIContinuousTests(unittest.TestCase):
    def test_compact_witness(self):
        r = MOD.check_compact_finite_witness()
        self.assertEqual(r["nonempty_binary_cube_subsets"], 255)
        self.assertTrue(r["positive_weight_minimizers_all_nondominated"])

    def test_noncompact_boundary(self):
        r = MOD.check_noncompact_frontier_boundary()
        self.assertEqual(r["successor_dominance_checks"], 256)
        self.assertTrue(r["finite_prefix_minima_strictly_improve"])
        self.assertFalse(r["infinite_sequence_has_attained_infimum"])
        self.assertEqual(r["compactified_prefix_unique_pareto"], "0")

    def test_cover_monotonicity(self):
        r = MOD.check_cover_monotonicity()
        self.assertEqual(r["rows"][0]["cover_counts_radius_0_1_2_3"], [5, 2, 1, 1])
        self.assertTrue(r["larger_tolerance_never_increases_cover_number"])

    def test_infimum_minimum(self):
        r = MOD.check_infimum_vs_minimum()
        self.assertEqual(r["infimum"], "0")
        self.assertFalse(r["infimum_attained"])
        self.assertEqual(r["first_100_minimum"], "1/100")

    def test_aggregate(self):
        self.assertEqual(
            MOD.run()["terminal"],
            "GRAND_GMI_MEASURABLE_CONTINUOUS_TRANCHE_ALL_GREEN",
        )


if __name__ == "__main__":
    unittest.main()
