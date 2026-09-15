from __future__ import annotations

import unittest

from falsification_governance_v1 import validate_audit


class FalsificationGovernanceTests(unittest.TestCase):
    def test_four_controls_close_and_three_registry_tasks_stay_open(self):
        result = validate_audit()
        self.assertEqual(result["ledger_rows"], 4)
        self.assertEqual(result["open_registry_tasks"], 3)
        self.assertEqual(result["visible_retractions"], 3)
        self.assertEqual(result["bounded_negative_domains"], 8)
        self.assertEqual(result["pairwise_nulls_preserved"], 6)


if __name__ == "__main__":
    unittest.main()
