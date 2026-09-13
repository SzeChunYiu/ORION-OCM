"""Hostile and positive controls for the EFI constructive algorithms."""
from fractions import Fraction
from itertools import product
import unittest

import grand_gmi_empirical_frontier_identification_checks_v1 as e


class EmpiricalFrontierTests(unittest.TestCase):
    def test_exhaustive_censuses(self):
        receipt = e.run_checks()
        self.assertEqual(receipt["two_candidate_two_coordinate_boxes"], 1296)
        self.assertEqual(receipt["independent_integer_worlds"], 10000)
        self.assertEqual(receipt["three_candidate_coordinate_boxes"], 216)
        self.assertEqual(receipt["independent_half_integer_order_worlds"], 2744)

    def test_empty_and_malformed_registers_rejected(self):
        for world in ((), ((),), ((1,), (1, 2)), ((float("nan"),),),
                      ((float("inf"),),), ((True,),)):
            with self.assertRaises(ValueError):
                e.frontier(world)
        for boxes in ((), ((),), (((2, 1),),), (((1,),),), (((0, 1, 2),),),
                      (((0, 1),), ((0, 1), (0, 1))), (((False, 1),),)):
            with self.assertRaises(ValueError):
                e.box_membership(boxes)
        for worlds in ((), (((1,),), ((1,), (2,)))):
            with self.assertRaises(ValueError):
                e.identify(worlds)

    def test_equal_profiles_retain_all_candidates(self):
        world = ((1, 2), (1, 2), (2, 3))
        self.assertEqual(e.frontier(world), frozenset((0, 1)))
        p, n, q = e.identify((world,))
        self.assertEqual(p, n)
        self.assertEqual(q, frozenset((p,)))

    def test_one_candidate_is_always_present(self):
        boxes = (((0, 1), (3, 9)),)
        self.assertEqual(e.box_membership(boxes), (frozenset((0,)),) * 2)
        self.assertEqual(e.rectangle_frontiers(boxes), frozenset((frozenset((0,)),)))

    def test_shared_family_identified_without_necessary_candidate(self):
        p, n, q = e.identify((((0,), (1,)), ((1,), (0,))))
        self.assertEqual(p, frozenset((0, 1)))
        self.assertFalse(n)
        self.assertEqual(e.family_supports(q, ("NN", "NN")), frozenset((frozenset(("NN",)),)))
        self.assertEqual(len(e.family_supports(q, ("NN", "nonNN"))), 2)

    def test_rectangular_relaxation_is_one_sided(self):
        worlds = (((1,), (0,), (2,)), ((1,), (2,), (0,)))
        p, n, _ = e.identify(worlds)
        bp, bn = e.box_membership((((1, 1),), ((0, 2),), ((0, 2),)))
        self.assertLess(p, bp)
        self.assertLessEqual(bn, n)
        positive_worlds = (((0,), (1,)), ((2,), (3,)))
        p, n, _ = e.identify(positive_worlds)
        bp, bn = e.box_membership((((0, 2),), ((1, 3),)))
        self.assertLess(bn, n)
        self.assertLessEqual(p, bp)

    def test_continuous_interior_tie_escapes_endpoints(self):
        q = e.rectangle_frontiers((((0, 2),), ((1, 3),)))
        self.assertIn(frozenset((0, 1)), q)
        corners = {e.frontier(((a,), (b,))) for a, b in product((0, 2), (1, 3))}
        self.assertNotIn(frozenset((0, 1)), corners)
        self.assertEqual(e.frontier(((Fraction(3, 2),), (Fraction(3, 2),))),
                         frozenset((0, 1)))

    def test_three_candidate_two_coordinate_orders(self):
        grid = (Fraction(0), Fraction(1, 2), Fraction(1))
        worlds = tuple(tuple(v[2*i:2*i+2] for i in range(3))
                       for v in product(grid, repeat=6))
        expected = frozenset(e._oracle(w) for w in worlds)
        self.assertEqual(len(worlds), 729)
        boxes = (((0, 1), (0, 1)),) * 3
        self.assertEqual(e.rectangle_frontiers(boxes), expected)

    def test_order_witnesses_preserve_strict_levels_and_bounds(self):
        self.assertEqual([len(tuple(e.ordered_partitions(n))) for n in range(1, 5)],
                         [1, 3, 13, 75])
        intervals = ((Fraction(0), Fraction(1)),) * 4
        for blocks in e.ordered_partitions(4):
            w = e._order_witness(intervals, blocks)
            self.assertIsNotNone(w)
            self.assertTrue(all(0 <= x <= 1 for x in w))
            for left, right in zip(blocks, blocks[1:]):
                self.assertLess(w[left[0]], w[right[0]])
            for block in blocks:
                self.assertEqual(len({w[i] for i in block}), 1)
        impossible = ((Fraction(2), Fraction(2)), (Fraction(1), Fraction(1)))
        self.assertIsNone(e._order_witness(impossible, ((0,), (1,))))

    def test_unique_opcode_minimum_never_disappears(self):
        opcodes = (88, 136, 312, 472)
        mixed = 0
        for times in product(range(1, 4), repeat=8):
            world = tuple((ops, times[2*i], times[2*i+1])
                          for i, ops in enumerate(opcodes))
            f = e._oracle(world)
            self.assertIn(0, f)
            mixed += bool(f & {2, 3})
        self.assertEqual(mixed, 3609)

    def test_positive_unit_transport_preserves_full_identification(self):
        worlds = (((1, 3), (2, 2)), ((1, 1), (2, 2)), ((2, 2), (2, 2)))
        moved = tuple(tuple((3*x + 5, 7*y - 11) for x, y in w) for w in worlds)
        self.assertEqual(e.identify(worlds), e.identify(moved))

    def test_transport_fails_without_common_order_embedding(self):
        w = ((1, 2), (2, 1))
        self.assertEqual(e.frontier(w), frozenset((0, 1)))
        self.assertEqual(e.frontier(tuple((x,) for x, _ in w)), frozenset((0,)))
        self.assertEqual(e.frontier(((1,), (2,))), frozenset((0,)))
        self.assertEqual(e.frontier(((100,), (2,))), frozenset((1,)))
        self.assertEqual(e.frontier(((1,), (1,))), frozenset((0, 1)))
        incomparable = ((0, 3), (1, 0))
        mixed = tuple((2*x + y, x + 2*y) for x, y in incomparable)
        self.assertEqual(e.frontier(incomparable), frozenset((0, 1)))
        self.assertEqual(e.frontier(mixed), frozenset((1,)))

    def test_uncertainty_is_not_observed_coexistence(self):
        boxes = (((88, 88), (1, 3), (1, 3)), ((312, 312), (2, 4), (2, 4)))
        q = e.rectangle_frontiers(boxes)
        support = e.family_supports(q, ("nonNN", "NN"))
        self.assertEqual(support, frozenset((frozenset(("nonNN",)),
                                            frozenset(("nonNN", "NN")))))
        self.assertEqual(e.frontier(((88, 1, 1), (312, 2, 2))), frozenset((0,)))
        self.assertEqual(e.frontier(((88, 3, 3), (312, 2, 2))), frozenset((0, 1)))


if __name__ == "__main__":
    unittest.main()
