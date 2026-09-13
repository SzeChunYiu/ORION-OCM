import sys
import unittest
from fractions import Fraction
from pathlib import Path
from itertools import product

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terminal_controls_v1 import compare, controls
from terminal_kernel_v1 import reconstruct, terminal_kernel


class TerminalCostTests(unittest.TestCase):
    def test_cost_kernel_equivalence_classes_preserve_profiles(self):
        seen_full, seen_min, collisions = {}, {}, 0
        choices = ((), (0,), (1,), (0, 1))
        for flat in product((0, 1), repeat=4):
            cost = tuple(((flat[2*x],), (flat[2*x+1],)) for x in range(2))
            for rows in product(choices, repeat=2):
                for prune, seen in ((False, seen_full), (True, seen_min)):
                    kernel = terminal_kernel(1, rows, cost, ((1,),), prune)
                    signature = tuple((p, tuple(sorted(v))) for p, v in sorted(kernel.items()))
                    values = set(reconstruct(1, rows, cost, ((1,),), prune)[0])
                    if signature in seen:
                        self.assertEqual(values, seen[signature])
                        collisions += 1
                    else:
                        seen[signature] = values
        self.assertGreater(collisions, 100)

    def test_counterexamples_and_no_alarm_controls(self):
        self.assertEqual(len(controls()), 10)

    def test_missing_output_cost_changes_boolean_prediction(self):
        rows = ((0, 1), (1,))
        cost = (((0,), (3,)),) * 2
        self.assertEqual(set(reconstruct(1, rows, cost, ((1,),))[0]), {(1, 4), (3, 3)})

    def test_zero_cost_recovers_boolean_kernel(self):
        rows = ((0,), (0, 1), (1,), (0,))
        cost = (((0,), (0,)),) * 4
        kernel = terminal_kernel(2, rows, cost, ((1,), (2,)))
        self.assertFalse(kernel[(-1, -1)])
        self.assertEqual(set(kernel[(0, 0)]), {(0,)})
        self.assertTrue(compare(2, rows, cost, ((1,), (2,)))["frontier"])

    def test_same_frontier_different_wasteful_profiles(self):
        rows = ((0, 1),)
        a, b = (((0,), (1,)),), (((0,), (2,)),)
        self.assertEqual(set(reconstruct(0, rows, a, ())[0]), set(reconstruct(0, rows, b, ())[0]))
        self.assertNotEqual(set(reconstruct(0, rows, a, (), False)[0]),
                            set(reconstruct(0, rows, b, (), False)[0]))

    def test_zero_mass_is_not_a_permission_to_fail(self):
        result = compare(1, ((0,), (1,)), (((0,), (0,)),) * 2, ((1,),))
        self.assertEqual(result["frontier"], {(1, 1)})

    def test_negative_query_rejected(self):
        with self.assertRaises(ValueError):
            reconstruct(1, ((0,),) * 2, (((0,),),) * 2, ((-1,),))

    def test_negative_terminal_rejected(self):
        with self.assertRaises(ValueError):
            reconstruct(0, ((0,),), (((-1,),),), ())

    def test_floating_nonexact_cost_rejected(self):
        for bad in (0.0, float("nan"), float("inf"), True):
            with self.subTest(cost=bad), self.assertRaises(ValueError):
                reconstruct(0, ((0,),), (((bad,),),), ())

    def test_exact_rational_retained(self):
        result = reconstruct(0, ((0,),), (((Fraction(1, 7),),),), ())[0]
        self.assertEqual(set(result), {(Fraction(1, 7),)})

    def test_invalid_cube_rejected(self):
        with self.assertRaises(ValueError):
            reconstruct(1, ((0,),), (((0,),),), ((1,),))

    def test_outside_action_rejected(self):
        with self.assertRaises(ValueError):
            reconstruct(0, ((2,),), (((0,),),), ())

    def test_resource_dimension_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reconstruct(1, ((0,),) * 2, (((0, 0),),) * 2, ((1,),))


if __name__ == "__main__":
    unittest.main()
