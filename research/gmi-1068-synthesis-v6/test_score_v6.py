"""Independent endpoint enumeration for robust scalar model comparisons."""
from fractions import Fraction as F
from itertools import product
import unittest
from score_intervals_v6 import certify_winner

COVERAGE = {"interval_boxes": 300, "malformed_inputs": 10}


class ScoreTests(unittest.TestCase):
    def test_boxes_against_realized_endpoint_winners(self):
        spans = [(0, 0), (0, 1), (1, 1), (1, 2), (F(1, 2), F(3, 2))]
        count = 0
        for a, b, cost_a, tradeoff in product(spans, spans, (0, 1), (0, F(1, 2), 1, 2, 3, 4)):
            data = {"a": (*a, cost_a, cost_a + 1), "b": (*b, 0, 1)}
            certified = certify_winner(data, tradeoff)["winner"]
            possible = {"a", "b"}
            for qa, qb, ca, cb in product(a, b, (cost_a, cost_a + 1), (0, 1)):
                scores = {"a": qa - tradeoff * ca, "b": qb - tradeoff * cb}
                top = max(scores.values())
                winner = {n for n, s in scores.items() if s == top}
                possible &= winner if len(winner) == 1 else set()
            expected = next(iter(possible)) if possible else None
            self.assertEqual(certified, expected)
            count += 1
        self.assertEqual(count, COVERAGE["interval_boxes"])

    def test_translation_cost_can_reverse_source_ranking(self):
        self.assertEqual(certify_winner({"a": (2, 2, 0, 0), "b": (1, 1, 0, 0)}, 1)["winner"], "a")
        self.assertEqual(certify_winner({"a": (2, 2, 2, 2), "b": (1, 1, 0, 0)}, 1)["winner"], "b")
        self.assertEqual(certify_winner({"a": (2, 2, 0, 2), "b": (1, 1, 0, 0)}, 1)["status"], "UNKNOWN")

    def test_singleton_and_tie(self):
        self.assertEqual(certify_winner({"a": (0, 1, 0, 5)}, 1)["winner"], "a")
        self.assertIsNone(certify_winner({"a": (1, 1, 0, 0), "b": (1, 1, 0, 0)}, 1)["winner"])

    def test_invalid(self):
        bad = [
            ({}, 1), ({"a": (1, 0, 0, 1)}, 1),
            ({"a": (0, 1, -1, 1)}, 1), ({"a": (0, 1, 2, 1)}, 1),
            ({"a": (0, 1, 0, 1)}, -1), ({"a": (0, 1, 0, 1)}, True),
            ({"a": (0, 1, 0, 1.0)}, 1), ({"a": (0, 1)}, 1),
            ({"": (0, 1, 0, 1)}, 1), ({"a": (0, 1, False, 1)}, 1),
        ]
        self.assertEqual(len(bad), COVERAGE["malformed_inputs"])
        for data, tradeoff in bad:
            with self.assertRaises(ValueError):
                certify_winner(data, tradeoff)


if __name__ == "__main__":
    unittest.main()
