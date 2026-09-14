"""Exact positive and hostile controls; no general theorem or physical validation."""

from fractions import Fraction as F
from itertools import product
from pathlib import Path
import importlib.util
import unittest

# Compile the sibling source explicitly; works under isolated Python -I.
path = Path(__file__).with_name("causal_tables_v1.py")
spec = importlib.util.spec_from_loader("causal_tables_checked", loader=None)
tables = importlib.util.module_from_spec(spec)
exec(compile(path.read_bytes(), str(path), "exec"), tables.__dict__)


class CausalIdentifiabilityControls(unittest.TestCase):
    def test_two_worlds_share_observed_xy_law(self):
        a, b = [tables.marginal_xy(tables.observed(w)) for w in (0, 1)]
        self.assertEqual(a, b)
        self.assertEqual(a, {(0, 0): F(1, 2), (1, 1): F(1, 2)})

    def test_surgical_laws_differ(self):
        self.assertEqual(tables.intervene(0, 1), F(1, 2))
        self.assertEqual(tables.intervene(1, 1), F(1))

    def test_common_randomized_decoder_has_disjoint_success_events(self):
        # Any common output law has disjoint masses at the two exact answers.
        for a, b in product(range(9), repeat=2):
            if a + b <= 8:
                self.assertLessEqual(min(F(a, 8), F(b, 8)), F(1, 2))
        self.assertEqual(min(F(1, 2), F(1, 2)), F(1, 2))

    def test_old_w2_observational_adjustment_is_unsupported(self):
        for world, x in product((0, 1), repeat=2):
            with self.assertRaisesRegex(ValueError, "unsupported"):
                tables.adjustment(tables.observed(world), x)

    def test_supported_backdoor_uses_observational_ratios(self):
        for world, x in product((0, 1), repeat=2):
            joint = tables.observed(world, F(1, 4))
            self.assertEqual(tables.adjustment(joint, x), tables.intervene(world, x))
            for z in (0, 1):
                self.assertGreater(sum(p for (xx, _y, zz), p in joint.items()
                                       if xx == x and zz == z), 0)

    def test_supported_confounded_unadjusted_value_differs(self):
        joint = tables.observed(0, F(1, 4))
        self.assertEqual(tables.conditional_y1(joint, 1), F(3, 4))
        self.assertEqual(tables.adjustment(joint, 1), F(1, 2))

    def test_positive_descendant_control(self):
        joint = tables.descendant_joint()
        self.assertEqual(len(joint), 8)
        self.assertTrue(all(p > 0 for p in joint.values()))
        self.assertEqual(tables.adjustment(joint, 1), F(7, 10))
        self.assertEqual(tables.descendant_do(1), F(3, 4))
        self.assertNotEqual(tables.adjustment(joint, 1), tables.descendant_do(1))

    def test_descendant_conditional_terms(self):
        joint = tables.descendant_joint()
        terms = []
        for z in (0, 1):
            mass = sum(p for (x, _y, zz), p in joint.items() if x == 1 and zz == z)
            terms.append(joint.get((1, 1, z), F(0)) / mass)
        self.assertEqual(terms, [F(1, 2), F(9, 10)])

    def test_old_descendant_control_rejects_empty_strata(self):
        joint = {(0, 0, 0): F(1, 2), (1, 1, 1): F(1, 2)}
        with self.assertRaisesRegex(ValueError, "unsupported"):
            tables.adjustment(joint, 1)

    def test_randomized_positive_assignments_match_surgery(self):
        for world, x in product((0, 1), repeat=2):
            for p in (F(1, 4), F(1, 2), F(3, 4)):
                self.assertEqual(tables.conditional_y1(tables.randomized(world, p), x),
                                 tables.intervene(world, x))

    def test_randomized_unassigned_value_is_not_observationally_defined(self):
        with self.assertRaisesRegex(ValueError, "zero probability"):
            tables.conditional_y1(tables.randomized(1, F(0)), 1)

    def test_independence_does_not_authorize_other_equation_changes(self):
        # X remains randomized independently, but an extra intervention fixes Y=0.
        changed = {(x, 0, z): F(1, 4) for x, z in product((0, 1), repeat=2)}
        self.assertEqual(tables.conditional_y1(changed, 1), F(0))
        self.assertNotEqual(tables.conditional_y1(changed, 1), tables.intervene(1, 1))

    def test_joint_validation_rejects_bad_mass(self):
        for joint in ({}, {(0, 0, 0): F(2)}, {(0, 0, 0): F(-1)}):
            with self.assertRaises(ValueError):
                tables.adjustment(joint, 0)

    def test_unfaithful_arrow_and_empty_graph_have_same_law(self):
        arrow, empty = {}, {}
        for x, u in product((0, 1), repeat=2):
            arrow[(x, x ^ u)] = F(1, 4)
            empty[(x, u)] = F(1, 4)
        self.assertEqual(arrow, empty)
        # The structural Y=x xor u depends on x, despite observational independence.
        self.assertNotEqual(0 ^ 0, 1 ^ 0)

    def test_assignment_interfaces_refuse_outside_binary_domain(self):
        for operation in (tables.descendant_do, lambda x: tables.intervene(0, x),
                          lambda x: tables.adjustment(tables.observed(0), x)):
            with self.assertRaises(ValueError):
                operation(2)


if __name__ == "__main__":
    unittest.main()
