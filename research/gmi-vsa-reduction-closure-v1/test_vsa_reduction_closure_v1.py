from __future__ import annotations

import unittest

from vsa_reduction_closure_v1 import (
    after_independent_bit_noise,
    bundled_member_coordinate_accuracy,
    cleanup_failure_upper_bound,
    neutral_recovery_certificate,
    validate_closure,
    validate_receipt,
)


class VSAReductionClosureTests(unittest.TestCase):
    def test_exact_bundle_and_noise_laws(self) -> None:
        self.assertEqual(bundled_member_coordinate_accuracy(1), 1.0)
        self.assertEqual(bundled_member_coordinate_accuracy(3), 0.75)
        self.assertEqual(bundled_member_coordinate_accuracy(5), 0.6875)
        self.assertEqual(after_independent_bit_noise(0.75, 0.25), 0.625)

    def test_dimension_improves_cleanup_bound(self) -> None:
        self.assertGreater(
            cleanup_failure_upper_bound(1024, 8, 0.75),
            cleanup_failure_upper_bound(2048, 8, 0.75),
        )

    def test_committed_receipt(self) -> None:
        result = validate_receipt()
        self.assertEqual(result["parent_equalities"], 7)
        self.assertEqual(result["vsa_frontier_cells"], 19)
        self.assertEqual(result["parent_frontier_cells"], 5)

    def test_neutral_low_level_recovery_and_negative_ecology(self) -> None:
        result = neutral_recovery_certificate()
        self.assertEqual(result["candidate_count"], 36)
        self.assertEqual(result["structured_exact_count"], 1)
        self.assertEqual(result["structured_winner"], ("xor", "majority", "rotate", "nearest"))
        self.assertEqual(result["twin_exact_count"], 12)
        self.assertNotEqual(result["twin_winner"], result["structured_winner"])

    def test_all_seven_earned_tasks_close(self) -> None:
        self.assertEqual(validate_closure()["ledger_rows"], 7)


if __name__ == "__main__":
    unittest.main()
