import hashlib
import importlib.util
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("continuous_scope", HERE/"grand_gmi_continuous_lift_boundary_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ContinuousLiftBoundaryTests(unittest.TestCase):
    def test_receipt_and_historical_preservation(self):
        actual = MOD.run()
        self.assertTrue(actual["all_checks_green"])
        self.assertEqual(actual, json.loads((HERE/"GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_RECEIPT_V2.json").read_text()))
        old = (HERE/"GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_RECEIPT_V1.json").read_bytes()
        self.assertEqual(hashlib.sha256(old).hexdigest(), "a19140479730a4729e2f6b9101ee5cf0cbb55926b1fbcea162a4f2fdce8c1aae")

    def test_epsilon_witness_matches_independent_integer_search(self):
        for a, b in product(range(1, 9), range(1, 33)):
            epsilon = F(a, b)
            first = next(n for n in range(1, 33) if F(1, n) <= epsilon)
            n, value = MOD.epsilon_witness(epsilon)
            self.assertEqual(n, first)
            self.assertEqual(value, 1+F(1, first))
            self.assertGreater(value, 1)

    def test_finite_margin_and_equal_infima_are_different_claims(self):
        self.assertEqual(MOD.tail_cost(2), F(3, 2))
        self.assertLess(MOD.tail_cost(2), 2)
        self.assertTrue(all(MOD.tail_cost(n) > 1 for n in range(1, 257)))
        # B={1} beats every observed A member, whereas a B lower bound 2 is excluded.
        self.assertGreater(min(MOD.tail_cost(n) for n in range(1, 257)), 1)

    def test_noncompact_attained_and_compact_discontinuous_controls(self):
        self.assertEqual(min(F(j, 9)**2 for j in range(-100, 101)), 0)
        discontinuous = lambda x: F(1) if x == 0 else x
        self.assertEqual(discontinuous(F(0)), 1)
        for n in (2, 4, 8, 16, 32):
            self.assertGreater(discontinuous(F(1, n)), 0)
            self.assertLess(discontinuous(F(1, 2*n)), discontinuous(F(1, n)))

    def test_exact_and_approximate_certificates_need_both_bounds(self):
        self.assertFalse(MOD.finite_enclosure((2, 3), 1, 2, 0, 0))
        self.assertTrue(MOD.finite_enclosure((2, 3), 2, 2, 0, 0))
        self.assertTrue(MOD.finite_enclosure((2, 3), F(3, 2), 2, 0, F(1, 2)))
        self.assertFalse(MOD.finite_enclosure((2, 3), F(3, 2), 2, 0, F(1, 3)))
        self.assertFalse(MOD.finite_enclosure((1, 2, 3), 2, 2, 1, 0))
        self.assertFalse(MOD.finite_enclosure((2, 3), 2, 2, 1, 0))

    def test_accounting_direction_and_membership(self):
        self.assertTrue(MOD.accounting_certificate((F(5, 6),), 0, F(5, 6), F(4, 3)))
        self.assertFalse(MOD.accounting_certificate((F(4, 3),), 0, F(4, 3), F(5, 6)))
        self.assertFalse(MOD.accounting_certificate((F(4, 3),), 0, F(5, 6), 1))
        self.assertTrue(MOD.accounting_certificate((1, F(4, 3)), 1, F(4, 3), 2))

    def test_lipschitz_enclosures_against_independent_dense_points(self):
        dense = tuple(abs(F(j, 1024)-F(1, 3)) for j in range(1025))
        for n in range(1, 65):
            lower, upper, point = MOD.grid_enclosure(n)
            self.assertTrue(all(value >= lower for value in dense))
            self.assertEqual(abs(point-F(1, 3)), upper)
            self.assertLessEqual(upper-lower, F(1, 2*n))
            self.assertLessEqual(lower, 0)
            self.assertGreaterEqual(upper, 0)

    def test_effective_finite_prefix_does_not_determine_later_halting(self):
        for counter, steps in product(range(10), repeat=2):
            self.assertEqual(MOD.bounded_halt(("countdown", counter), steps), steps >= counter)
            self.assertFalse(MOD.bounded_halt(("loop", counter), steps))
        self.assertEqual([MOD.bounded_halt(("countdown", 5), n) for n in range(5)], [False]*5)
        self.assertTrue(MOD.bounded_halt(("countdown", 5), 5))

    def test_declarations_never_license_results(self):
        for bits in product((False, True), repeat=5):
            actual = MOD.declaration_status(dict(zip(MOD.FIELDS, bits)))
            self.assertNotIn("AVAILABLE", actual.values())
            self.assertNotIn("VERIFIED", actual.values())
        full = dict.fromkeys(MOD.FIELDS, True)
        for bad in ({}, None, {"attainment_witness": True}, full | {"extra": True},
                    full | {"effective_description": "yes"}, full | {"effective_description": 1}):
            with self.assertRaises(MOD.ContractError):
                MOD.declaration_status(bad)

    def test_finite_row_selector_matches_direct_equivalence_classes(self):
        for bits in product((0, 1), repeat=6):
            rows = (bits[:2], bits[2:4], bits[4:])
            chosen = MOD.finite_row_selector(rows)
            for i in range(3):
                cell = {j for j in range(3) if rows[j] == rows[i]}
                self.assertEqual(chosen[i], min(cell))
        with self.assertRaises(MOD.ContractError):
            MOD.finite_row_selector(((0,), (0, 1)))

    def test_invalid_exact_domains_rejected(self):
        for epsilon in (0, -1, True, float("inf"), float("nan")):
            with self.assertRaises(MOD.ContractError):
                MOD.epsilon_witness(epsilon)
        for n in (0, -1, True, 1.5):
            with self.assertRaises(MOD.ContractError):
                MOD.tail_cost(n)
        for values, witness in (((), 0), ((1,), True), ((1,), 1)):
            with self.assertRaises(MOD.ContractError):
                MOD.finite_enclosure(values, 1, 1, witness, 0)


if __name__ == "__main__":
    unittest.main()
