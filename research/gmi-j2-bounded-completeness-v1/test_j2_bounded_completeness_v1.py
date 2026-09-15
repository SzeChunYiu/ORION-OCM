from __future__ import annotations

import unittest

from j2_bounded_completeness_v1 import (
    higher_order_census,
    individual_attacks,
    pairwise_census,
    validate_closure,
)


class J2BoundedCompletenessTests(unittest.TestCase):
    def test_all_eight_attacks_fail_with_positive_controls(self):
        attacks = individual_attacks()
        for name, row in attacks.items():
            exact = row["exact_at_7"] if name == "D5" else row["exact_at_2"] if name == "D6" else row["exact"]
            positive = row["positive_at_8"] if name == "D5" else row["positive_at_3"] if name == "D6" else row["positive"]
            self.assertEqual(exact, 0, name)
            self.assertTrue(positive, name)

    def test_pairwise_census_preserves_nulls(self):
        result = pairwise_census()
        self.assertEqual(len(result["pairs"]), 28)
        self.assertEqual((result["pairs_with_failure"], result["complete_pairs"]), (22, 6))

    def test_higher_order_residual_is_exact(self):
        result = higher_order_census()
        self.assertEqual(result["pairwise_reachable"], 194)
        self.assertEqual(result["triple_reachable"], 256)
        self.assertEqual(result["higher_order_only"], 62)

    def test_exactly_eleven_j2_tasks_close(self):
        self.assertEqual(validate_closure()["ledger_rows"], 11)


if __name__ == "__main__":
    unittest.main()
