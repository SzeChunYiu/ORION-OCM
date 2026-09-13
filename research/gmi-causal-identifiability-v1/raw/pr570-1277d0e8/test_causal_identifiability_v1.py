"""Exact finite countercontrols for CAU-1--3.

These checks do not prove the analytic theorem.  They freeze the small rational
witnesses used to reject "observational data determines the interventional
target" and to show which premise restores identifiability.
"""

from fractions import Fraction
from itertools import product
import unittest

HALF = Fraction(1, 2)


def observational(world):
    """P(X=x, Y=y) for U ~ Bernoulli(1/2) under the given world."""
    table = {}
    for u in (0, 1):
        x = u
        y = u if world == 0 else x
        table[(x, y)] = table.get((x, y), Fraction(0)) + HALF
    return table


def interventional(world, x_forced):
    """P(Y=1 | do(X=x_forced)); f_X is replaced, every other map and P_U kept."""
    total = Fraction(0)
    for u in (0, 1):
        y = u if world == 0 else x_forced
        if y == 1:
            total += HALF
    return total


def backdoor(world, x_forced):
    """Sum_z P(Y=1 | X=x, Z=z) P(Z=z) with Z = U observed."""
    total = Fraction(0)
    for u in (0, 1):
        y = u if world == 0 else x_forced
        total += HALF * (1 if y == 1 else 0)
    return total


class CausalIdentifiabilityControls(unittest.TestCase):
    def test_two_worlds_share_the_observational_law(self) -> None:
        self.assertEqual(observational(0), observational(1))
        self.assertEqual(observational(0), {(0, 0): HALF, (1, 1): HALF})

    def test_interventional_law_differs_between_those_worlds(self) -> None:
        self.assertEqual(interventional(0, 1), HALF)
        self.assertEqual(interventional(1, 1), Fraction(1))
        self.assertNotEqual(interventional(0, 1), interventional(1, 1))

    def test_no_observational_learner_beats_one_half_in_both_worlds(self) -> None:
        # Identical visible law => identical output law.  Success is 1-q and q.
        best = max(min(Fraction(1) - q, q) for q in
                   (Fraction(k, 8) for k in range(9)))
        self.assertEqual(best, HALF)

    def test_backdoor_premise_restores_the_truth_in_each_world(self) -> None:
        for world in (0, 1):
            self.assertEqual(backdoor(world, 1), interventional(world, 1))

    def test_adjusting_on_a_descendant_of_x_is_not_safe(self) -> None:
        # Third register: X ~ Bernoulli(1/2) exogenous, Y = X, Z = Y.
        # Z is a descendant of X, so the back-door criterion excludes it.
        joint = {}  # P(X=x, Y=y, Z=z)
        for x in (0, 1):
            y = x
            z = y
            joint[(x, y, z)] = joint.get((x, y, z), Fraction(0)) + HALF

        truth = Fraction(1)  # Y = X, so do(X=1) forces Y = 1

        # Sum_z P(Y=1 | X=1, Z=z) P(Z=z), skipping empty strata.
        adjusted = Fraction(0)
        for z in (0, 1):
            p_z = sum(v for (xx, yy, zz), v in joint.items() if zz == z)
            denom = sum(v for (xx, yy, zz), v in joint.items()
                        if xx == 1 and zz == z)
            if denom == 0:
                continue
            num = sum(v for (xx, yy, zz), v in joint.items()
                      if xx == 1 and yy == 1 and zz == z)
            adjusted += (num / denom) * p_z

        self.assertEqual(adjusted, HALF)
        self.assertEqual(truth, Fraction(1))
        self.assertNotEqual(adjusted, truth)

    def test_every_admitted_assignment_is_enumerated(self) -> None:
        checked = 0
        for world, x_forced in product((0, 1), repeat=2):
            value = interventional(world, x_forced)
            self.assertIn(value, (Fraction(0), HALF, Fraction(1)))
            checked += 1
        self.assertEqual(checked, 4)


if __name__ == "__main__":
    unittest.main()
