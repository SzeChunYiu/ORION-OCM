from fractions import Fraction as F
import unittest

from hybrid_complementarity_v1 import (
    best_monolith_cost,
    complementarity_gap,
    hybrid_cost,
    hybrid_strictly_wins,
    misrouting_penalty,
    registered_witness,
)


class HybridComplementarityTests(unittest.TestCase):
    def setUp(self):
        self.w = [F(1, 2), F(1, 2)]
        self.a = [F(0), F(4)]
        self.b = [F(4), F(0)]

    def test_positive_complementarity_gap(self):
        self.assertEqual(best_monolith_cost(self.w, self.a, self.b), F(2))
        self.assertEqual(complementarity_gap(self.w, self.a, self.b), F(2))
        self.assertEqual(hybrid_cost(self.w, self.a, self.b, F(1)), F(1))
        self.assertTrue(hybrid_strictly_wins(self.w, self.a, self.b, F(1)))

    def test_exact_misrouting_threshold(self):
        self.assertEqual(misrouting_penalty(self.w, self.a, self.b, [F(1, 4), F(1, 4)]), F(1))
        self.assertTrue(hybrid_strictly_wins(self.w, self.a, self.b, F(1), [F(1, 5), F(1, 5)]))
        self.assertFalse(hybrid_strictly_wins(self.w, self.a, self.b, F(1), [F(1, 4), F(1, 4)]))
        self.assertFalse(hybrid_strictly_wins(self.w, self.a, self.b, F(1), [F(3, 10), F(3, 10)]))

    def test_pointwise_dominance_negative_twin(self):
        a = [F(0), F(0)]
        b = [F(1), F(1)]
        self.assertEqual(complementarity_gap(self.w, a, b), F(0))
        self.assertFalse(hybrid_strictly_wins(self.w, a, b, F(1)))

    def test_identity_random_finite_tables(self):
        vals = [F(0), F(1), F(2), F(3)]
        for a0 in vals:
            for a1 in vals:
                for b0 in vals:
                    for b1 in vals:
                        a = [a0, a1]
                        b = [b0, b1]
                        gap = complementarity_gap(self.w, a, b)
                        direct = best_monolith_cost(self.w, a, b) - hybrid_cost(self.w, a, b, F(0))
                        self.assertEqual(gap, direct)

    def test_registered_witness(self):
        r = registered_witness()
        self.assertEqual(r["positive"]["gap"], "2")
        self.assertTrue(r["positive"]["wins_h1"])
        self.assertFalse(r["positive"]["epsilon_boundary"])
        self.assertEqual(r["negative_twin"]["gap"], "0")
        self.assertFalse(r["negative_twin"]["wins_h1"])


if __name__ == "__main__":
    unittest.main()
