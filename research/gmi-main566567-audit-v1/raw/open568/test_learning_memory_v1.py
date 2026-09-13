"""Finite controls for LMT-1--8.

The analytic PAC and impossibility results live in the theorem document.  These
checks pin the exact countermodels and accounting identities used there.
"""

from fractions import Fraction
import unittest


class LearningMemoryControls(unittest.TestCase):
    def test_two_world_indistinguishability_ceiling(self) -> None:
        # The learner-visible history law is identical, so one terminal output
        # distribution q must serve both worlds.
        for q in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)):
            success_p0 = 1 - q
            success_p1 = q
            self.assertLessEqual(min(success_p0, success_p1), Fraction(1, 2))

    def test_approximate_erm_decomposition(self) -> None:
        # Fixed exact risks / empirical risks with eta-approximate ERM.
        true = {"a": Fraction(1, 5), "b": Fraction(1, 4), "c": Fraction(2, 5)}
        empirical = {"a": Fraction(1, 4), "b": Fraction(1, 5), "c": Fraction(7, 20)}
        chosen = "b"
        eta = Fraction(0)
        uniform_deviation = max(abs(empirical[h] - true[h]) for h in true)
        lhs = true[chosen] - min(true.values())
        rhs = 2 * uniform_deviation + eta
        self.assertLessEqual(lhs, rhs)

    def test_exact_forgetting_collision_cannot_preserve_two_unique_outputs(self) -> None:
        # k0 and k1 collapse to one forgotten state.  Any deterministic common
        # decoder has one output and must fail one of the two unique obligations.
        forgotten = {"k0": "same", "k1": "same"}
        required = {"k0": 0, "k1": 1}
        self.assertEqual(forgotten["k0"], forgotten["k1"])
        for common_output in (0, 1):
            successes = sum(common_output == required[k] for k in required)
            self.assertEqual(successes, 1)

    def test_componentwise_resource_minima_need_not_be_jointly_attainable(self) -> None:
        attainable = {(1, 3), (3, 1)}
        coordinate_infimum = (1, 1)
        self.assertNotIn(coordinate_infimum, attainable)


if __name__ == "__main__":
    unittest.main()
