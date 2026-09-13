import importlib.util
import pathlib
import unittest
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "grand_gmi_generalization_attainment_checks_v1",
    HERE / "grand_gmi_generalization_attainment_checks_v1.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestGrandGMIGeneralizationAttainmentV1(unittest.TestCase):
    def test_value_only_equality_gate_is_false(self):
        self.assertIsNone(mod.feasible_center((-1, 1), 1, removed=(0,)))
        for n in range(1, 65):
            output = Fraction(1, n)
            self.assertEqual(mod.error(output, (-1, 1)), 1 + output)
            self.assertGreater(mod.error(output, (-1, 1)), 1)

    def test_arbitrarily_small_positive_slack_gives_a_legal_output(self):
        for denominator in (2, 3, 17, 10**100):
            tolerance = 1 + Fraction(1, denominator)
            output = mod.feasible_center((-1, 1), tolerance, removed=(0,))
            self.assertIsNotNone(output)
            self.assertNotEqual(output, 0)
            self.assertLessEqual(mod.error(output, (-1, 1)), tolerance)

    def test_restoring_excluded_center_changes_equality_feasibility(self):
        self.assertEqual(mod.feasible_center((-1, 1), 1), 0)
        self.assertIsNone(mod.feasible_center((-1, 1), Fraction(3, 4)))

    def test_local_nonattainment_can_coexist_with_global_attainment(self):
        self.assertIsNone(mod.feasible_center((-1, 1), 1, removed=(0,)))
        outputs = (
            mod.feasible_center((-1, 1), 2, removed=(0,)),
            mod.feasible_center((-1, 3), 2, removed=(0,)),
        )
        self.assertEqual(max(mod.error(outputs[0], (-1, 1)), mod.error(outputs[1], (-1, 3))), 2)

    def test_many_exclusions_do_not_remove_a_nontrivial_interval(self):
        removed = tuple(Fraction(k, 100) for k in range(-99, 100))
        output = mod.feasible_center((-1, 1), Fraction(101, 100), removed=removed)
        self.assertNotIn(output, removed)
        self.assertLessEqual(mod.error(output, (-1, 1)), Fraction(101, 100))

    def test_actual_output_must_be_feasible_even_when_one_exists(self):
        self.assertIsNotNone(mod.feasible_center((-1, 1), 2, removed=(0,)))
        self.assertGreater(mod.error(Fraction(100), (-1, 1)), 2)

    def test_zero_radius_target_is_itself_a_center(self):
        self.assertEqual(mod.feasible_center((1, 1), 0, removed=(0,)), 1)

    def test_empty_or_ill_typed_target_problem_is_rejected(self):
        for targets, tolerance, removed in (((), 1, ()), ((1,), -1, ()), ((0,), 1, (0,))):
            with self.assertRaises(ValueError):
                mod.feasible_center(targets, tolerance, removed)

    def test_additive_boundary_receipt(self):
        result = mod.run()
        self.assertTrue(result["all_checks_green"], result["checks"])
        self.assertEqual(result["observed"]["finite_boundary_cases"], 144)
        self.assertEqual(result["observed"]["value_only_false_licenses"], 4)


if __name__ == "__main__":
    unittest.main()
