import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "grand_gmi_substrate_symmetry_checks_v1",
    HERE / "grand_gmi_substrate_symmetry_checks_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class GrandGMISubstrateSymmetryTests(unittest.TestCase):
    def test_unique_deterministic_symmetry(self):
        r = MOD.check_unique_deterministic_symmetry()
        self.assertEqual(r["invariant_loss_tables"], 9)
        self.assertEqual(r["unique_optimum_cases"], 6)
        self.assertTrue(r["all_unique_optima_equivariant"])

    def test_randomized_symmetrization(self):
        r = MOD.check_randomized_symmetrization()
        self.assertEqual(r["exact_policy_loss_checks"], 3375)
        self.assertTrue(r["risk_preserved"])
        self.assertTrue(r["convex_invariant_resource_not_worsened"])

    def test_nonconvex_boundary(self):
        r = MOD.check_nonconvex_resource_boundary()
        self.assertFalse(r["no_worse_equivariant_claim_without_convexity"])
        self.assertEqual(r["symmetrized_resource"], "1/2")

    def test_substrate_refinement(self):
        r = MOD.check_substrate_refinement()
        self.assertEqual(r["trace_checks"], 1020)
        self.assertEqual(r["semantic_classes"], 2)
        self.assertEqual(r["microstates_per_semantic_class"], [2, 2])
        self.assertTrue(r["observable_traces_preserved"])

    def test_aggregate(self):
        r = MOD.run()
        self.assertEqual(r["terminal"], "GRAND_GMI_SUBSTRATE_SYMMETRY_TRANCHE_ALL_GREEN")


if __name__ == "__main__":
    unittest.main()
