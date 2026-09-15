from __future__ import annotations

import unittest
from fractions import Fraction

from reaction_network_closure_v1 import (
    embedded_choice_probabilities,
    exhaustive_generator_certificate,
    program_compiler,
    reversible_generator,
    validate_closure,
)


class ReactionNetworkClosureTests(unittest.TestCase):
    def test_exact_reversible_generator(self) -> None:
        generator = reversible_generator(2, Fraction(2), Fraction(3))
        self.assertEqual(generator[0], (Fraction(-6), Fraction(6), Fraction(0)))
        self.assertEqual(generator[1], (Fraction(2), Fraction(-5), Fraction(3)))
        self.assertEqual(generator[2], (Fraction(0), Fraction(4), Fraction(-4)))
        self.assertEqual(generator, program_compiler(2, Fraction(2), Fraction(3)))

    def test_embedded_probabilities(self) -> None:
        probabilities = embedded_choice_probabilities(
            reversible_generator(2, Fraction(2), Fraction(3))
        )
        self.assertEqual(probabilities[1], (Fraction(2, 5), Fraction(0), Fraction(3, 5)))
        self.assertTrue(all(sum(row) == 1 for row in probabilities))

    def test_exhaustive_generator_family(self) -> None:
        certificate = exhaustive_generator_certificate()
        self.assertEqual(certificate["systems"], 54)
        self.assertEqual(certificate["state_rows"], 243)
        for key in (
            "compiler_mismatches", "conservation_violations", "generator_violations",
            "probability_violations",
        ):
            self.assertEqual(certificate[key], 0)

    def test_three_row_closure(self) -> None:
        self.assertEqual(
            validate_closure(),
            {
                "ledger_rows": 3,
                "systems": 54,
                "state_rows": 243,
                "violations": 0,
                "resource_coordinates": 16,
            },
        )


if __name__ == "__main__":
    unittest.main()
