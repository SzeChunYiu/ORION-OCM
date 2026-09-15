from __future__ import annotations
import unittest
from autocatalytic_closure_v1 import collision_certificate, validate_closure, validate_receipt

class AutocatalyticClosureTests(unittest.TestCase):
    def test_present_collision_future_separation(self):
        r = collision_certificate()
        self.assertTrue(r["same_present_response"])
        self.assertTrue(r["productive_future"])
        self.assertFalse(r["sterile_future"])
        self.assertEqual((r["productive_closure_size"], r["sterile_closure_size"]), (14,2))

    def test_committed_receipt(self):
        r = validate_receipt()
        self.assertEqual((r["cells"], r["frontier_cells"]), (36,117))
        self.assertEqual(r["parent_equalities"], 18)
        self.assertEqual(r["twin_separations"], 6)

    def test_only_six_earned_tasks_close(self):
        self.assertEqual(validate_closure()["ledger_rows"], 6)

if __name__ == "__main__": unittest.main()
