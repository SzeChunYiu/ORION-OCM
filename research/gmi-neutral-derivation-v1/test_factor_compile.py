"""Independent finite semantic/cost controls; execution belongs on laptop."""

import itertools
import unittest
from fractions import Fraction

from factor_cases import direct_value, make_case
from factor_compile import eliminate
from factor_model import Algebra, Factor


class CountingAlgebra:
    """Count real operation calls independently from compiler instrumentation."""
    def __init__(self, name):
        self.base = Algebra(name)
        self.calls = {"add": 0, "multiply": 0}

    def __getattr__(self, name):
        return getattr(self.base, name)

    def add(self, left, right):
        self.calls["add"] += 1
        return self.base.add(left, right)

    def multiply(self, left, right):
        self.calls["multiply"] += 1
        return self.base.multiply(left, right)


class FactorCompileTests(unittest.TestCase):
    def test_exhaustive_binary_pair_constraints_every_order(self):
        scopes = ((0, 1), (1, 2))
        for first in itertools.product((False, True), repeat=4):
            for second in itertools.product((False, True), repeat=4):
                factors = [Factor(scopes[0], first), Factor(scopes[1], second)]
                expected = direct_value((2, 2, 2), factors, Algebra("boolean"))
                for order in itertools.permutations(range(3)):
                    self.assertEqual(eliminate((2, 2, 2), factors,
                                               Algebra("boolean"), order)["value"], expected)

    def test_rational_and_min_plus_against_independent_enumeration(self):
        for name in ("rational", "min_plus"):
            for graph in ("chain", "cycle", "clique"):
                spec = dict(graph=graph, variables=3, domain_size=2)
                sizes, factors, algebra = make_case(spec, name)
                expected = direct_value(sizes, factors, algebra)
                for order in itertools.permutations(range(3)):
                    self.assertEqual(eliminate(sizes, factors, algebra, order)["value"],
                                     expected)

    def test_actual_algebra_calls_and_closed_form_chain_counts(self):
        for n, q in ((3, 2), (5, 3)):
            sizes, factors, _ = make_case(dict(graph="chain", variables=n,
                                              domain_size=q), "rational")
            algebra = CountingAlgebra("rational")
            result = eliminate(sizes, factors, algebra, range(n))
            profile = result["profile"]
            for field in ("add", "multiply"):
                self.assertEqual(profile[field], algebra.calls[field])
            self.assertEqual(profile["work"], (5 * n - 7) * q * q + 3 * q + 2)
            self.assertEqual(profile["width"], 1)

    def test_scalar_zero_isolated_variable_and_singleton_domains(self):
        for name in ("boolean", "rational", "min_plus"):
            algebra = Algebra(name)
            for factors in ([], [Factor((), (algebra.zero,))],
                            [Factor((0,), (algebra.one,))]):
                sizes = (1, 3)
                expected = direct_value(sizes, factors, algebra)
                for order in ((0, 1), (1, 0)):
                    self.assertEqual(eliminate(sizes, factors, algebra, order)["value"],
                                     expected)
        rational = eliminate((2, 3), [], Algebra("rational"), (0, 1))
        self.assertEqual(rational["value"], Fraction(6))
        self.assertEqual(rational["profile"]["work"], 9)

    def test_empty_variable_universe_and_scalar_product(self):
        factors = [Factor((), (Fraction(2, 3),)), Factor((), (Fraction(3, 5),))]
        result = eliminate((), factors, Algebra("rational"), ())
        self.assertEqual(result["value"], Fraction(2, 5))
        self.assertEqual(result["profile"]["work"], 4)

    def test_local_support_without_global_solution(self):
        unequal = (False, True, True, False)
        factors = [Factor(scope, unequal) for scope in ((0, 1), (1, 2), (0, 2))]
        # Each edge permits both values in each coordinate.
        for coordinate in (0, 1):
            supported = {row[coordinate] for row, value in
                         zip(itertools.product((0, 1), repeat=2), unequal) if value}
            self.assertEqual(supported, {0, 1})
        self.assertFalse(direct_value((2, 2, 2), factors, Algebra("boolean")))
        for order in itertools.permutations(range(3)):
            self.assertFalse(eliminate((2, 2, 2), factors,
                                       Algebra("boolean"), order)["value"])

    def test_invalid_inputs_are_rejected(self):
        for factors in ([Factor((0,), (True,))],
                        [Factor((0, 0), (True,) * 4)],
                        [Factor((1,), (True, True))],
                        [Factor((0,), (0, 1))]):
            with self.assertRaises(ValueError):
                eliminate((2,), factors, Algebra("boolean"), (0,))
        for order in ((), (0, 0), (1,)):
            with self.assertRaises(ValueError):
                eliminate((2,), [], Algebra("boolean"), order)


if __name__ == "__main__":
    unittest.main()
