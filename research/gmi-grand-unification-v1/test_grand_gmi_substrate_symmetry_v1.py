import importlib.util
import pathlib
import unittest
from fractions import Fraction

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

    def test_circle_average_has_only_finite_subgroup_invariance(self):
        # Independent expected law: averaging delta_0 under order 3 rotations.
        averaged = MOD.finite_orbit_average({Fraction(0): Fraction(1)}, 3)
        self.assertEqual(averaged, {Fraction(i, 3): Fraction(1, 3) for i in range(3)})
        self.assertEqual(MOD.rotate_atomic_measure(averaged, Fraction(1, 3)), averaged)
        rotated = MOD.rotate_atomic_measure(averaged, Fraction(1, 6))
        self.assertNotEqual(rotated, averaged)
        self.assertEqual(MOD.atomic_total_variation(averaged, rotated), 1)

    def test_nonatomic_mass_breaks_compact_jensen_without_regularity(self):
        atomic = ({Fraction(0): Fraction(1)}, Fraction(0))
        haar = ({}, Fraction(1))
        atoms, nonatomic = MOD.mix_circle_measures(atomic, haar, Fraction(2, 3))
        self.assertEqual(atoms, {Fraction(0): Fraction(2, 3)})
        self.assertEqual(nonatomic, Fraction(1, 3))
        self.assertEqual(atomic[1], 0)
        self.assertEqual(haar[1], 1)

    def test_compact_boundary_microscope_is_explicitly_finite(self):
        r = MOD.check_compact_averaging_boundary()
        self.assertEqual(r["circle_rotation_separating_witnesses"], 32)
        self.assertEqual(r["finite_cyclic_invariance_checks"], 528)
        self.assertEqual(r["nonatomic_mass_affinity_checks"], 45)
        self.assertEqual(r["scope"], "FINITE_SEPARATING_WITNESSES_WITH_ANALYTIC_HAAR_COMPONENT")

    def test_stability_and_attainment_are_separate_hypotheses(self):
        r = MOD.check_feasible_stability_and_frontier_boundaries()
        self.assertFalse(r["convex_nonstable_class_average_feasible"])
        self.assertEqual(r["strict_resource_improvement_witnesses"], 256)

    def test_aggregate(self):
        r = MOD.run()
        self.assertEqual(r["terminal"], "GRAND_GMI_SUBSTRATE_SYMMETRY_TRANCHE_ALL_GREEN")


if __name__ == "__main__":
    unittest.main()
