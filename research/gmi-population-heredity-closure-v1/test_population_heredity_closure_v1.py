from __future__ import annotations

import unittest
from fractions import Fraction

from population_heredity_closure_v1 import (
    binary_heredity_information_bits,
    capability,
    exhaustive_price_certificate,
    option_value_certificate,
    price_identity,
    selection_information_bits,
    validate_closure,
)


class PopulationHeredityClosureTests(unittest.TestCase):
    def test_price_identity_exact_example(self) -> None:
        law = price_identity((3, 1), (1, 3), (0, 2))
        self.assertEqual(law["observed_change"], law["covariance_over_mean_fitness"])

    def test_price_identity_exhaustive(self) -> None:
        certificate = exhaustive_price_certificate()
        self.assertEqual(certificate["cases"], 2187)
        self.assertEqual(certificate["violations"], 0)

    def test_information_laws(self) -> None:
        self.assertGreater(selection_information_bits((3, 1), (1, 3)), 0)
        self.assertEqual(binary_heredity_information_bits(0.0), 1.0)
        self.assertEqual(binary_heredity_information_bits(0.5), 0.0)

    def test_population_option_value_and_twins(self) -> None:
        self.assertEqual(capability(("A", "B")), Fraction(1, 1))
        self.assertEqual(capability(("A",)), Fraction(1, 2))
        self.assertEqual(capability(("A", "A")), Fraction(1, 2))
        certificate = option_value_certificate()
        self.assertTrue(all(row["parent_exact"] for row in certificate["rows"]))

    def test_four_row_closure(self) -> None:
        result = validate_closure()
        self.assertEqual(result["ledger_rows"], 4)
        self.assertEqual(result["price_cases"], 2187)
        self.assertEqual(result["price_violations"], 0)
        self.assertEqual(result["diverse_capability"], 1.0)
        self.assertEqual(result["single_capability"], 0.5)


if __name__ == "__main__":
    unittest.main()
