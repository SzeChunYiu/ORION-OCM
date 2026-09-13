"""Exact control for AEM-7 (capability obstruction).

Freezes the two reported scopes and the caveat that governs them.  It does not
re-derive the census; it pins the numbers so a later claim cannot drift from
them, and asserts the arithmetic that makes AEM-7 a *capability* statement
rather than an underdetermination one.
"""

from fractions import Fraction
import unittest

# five retained source receipts (census contract)
CENSUS_CELLS, CENSUS_GRAD = 350, 8
# nine of eleven live archives (B6 freeze)
LIVE_CELLS, LIVE_GRAD = 677, 34
LIVE_DENSE_INTO_GRAD, LIVE_CONSUMED, LIVE_AT_THRESHOLD = 33, 8, 0
# exported arm cohort (elites, not the searched population)
ARM_ROWS, ARM_DISTINCT, ARM_GRAD = 70, 63, 0


class Aem7Witness(unittest.TestCase):
    def test_generator_assembles_gradient_machines_in_both_scopes(self) -> None:
        self.assertGreater(CENSUS_GRAD, 0)
        self.assertGreater(LIVE_GRAD, 0)
        # ~5% of live cells, so assembly is routine rather than incidental
        rate = Fraction(LIVE_GRAD, LIVE_CELLS)
        self.assertGreater(rate, Fraction(1, 25))
        self.assertLess(rate, Fraction(1, 15))

    def test_the_hard_half_is_wired_but_the_output_usually_is_not(self) -> None:
        self.assertEqual(LIVE_DENSE_INTO_GRAD, 33)
        self.assertLess(LIVE_CONSUMED, LIVE_DENSE_INTO_GRAD)
        self.assertEqual(Fraction(LIVE_CONSUMED, LIVE_GRAD), Fraction(4, 17))

    def test_no_assembled_machine_attains_the_obligation(self) -> None:
        # This is what makes AEM-7 a capability obstruction.
        self.assertEqual(LIVE_AT_THRESHOLD, 0)

    def test_arm_cohort_is_not_the_searched_population(self) -> None:
        # grad_rows = 0 here; an absence claim drawn from it was retracted.
        self.assertEqual(ARM_GRAD, 0)
        self.assertLess(ARM_DISTINCT, ARM_ROWS)
        self.assertLess(ARM_ROWS, CENSUS_CELLS)
        self.assertLess(CENSUS_CELLS, LIVE_CELLS)

    def test_occurrence_is_not_certified_use(self) -> None:
        causal_coefficient_use_certified = False
        self.assertFalse(causal_coefficient_use_certified)
        self.assertGreater(LIVE_GRAD, LIVE_AT_THRESHOLD)

    def test_scopes_are_reported_separately_not_merged(self) -> None:
        self.assertNotEqual(CENSUS_GRAD, LIVE_GRAD)
        self.assertNotEqual(CENSUS_CELLS, LIVE_CELLS)


if __name__ == "__main__":
    unittest.main()
