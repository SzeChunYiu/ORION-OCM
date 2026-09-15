from __future__ import annotations

import unittest

from relational_sheaf_closure_v1 import (
    reduction_disposition,
    validate_closure,
    validate_receipt,
)


class RelationalSheafClosureTests(unittest.TestCase):
    def test_committed_exact_receipt(self) -> None:
        result = validate_receipt()
        self.assertEqual(result["cells"], 110)
        self.assertEqual(result["frontier_cells"], 508)
        self.assertEqual(result["table_equalities"], 22)
        self.assertEqual(result["search_equalities"], 22)
        self.assertEqual(result["negative_twin_separations"], 22)
        self.assertGreater(result["late_niche_cells"], 0)

    def test_burden_witness_gate_fails_closed(self) -> None:
        self.assertEqual(
            reduction_disposition(
                preserves_answers=False, status="REDUCTION_FAILED", burden_witness=None
            ),
            "CANNOT_IDENTIFY",
        )
        self.assertEqual(
            reduction_disposition(
                preserves_answers=False, status="REDUCTION_FAILED", burden_witness="Omega(n)"
            ),
            "RESIDUAL_WITH_BURDEN_WITNESS",
        )

    def test_only_seven_earned_tasks_close(self) -> None:
        self.assertEqual(validate_closure()["ledger_rows"], 7)


if __name__ == "__main__":
    unittest.main()
