from __future__ import annotations

import unittest

from neutral_safeguards_audit_v1 import validate_audit


class NeutralSafeguardsAuditTests(unittest.TestCase):
    def test_all_ten_safeguards_and_search_accounting(self):
        result = validate_audit()
        self.assertEqual(result["ledger_rows"], 10)
        self.assertEqual(result["candidate_attempts"], 104240)
        self.assertEqual(result["failed_candidates"], 104136)
        self.assertEqual(result["search_algorithms"], 5)

    def test_enrichment_and_failures_are_preserved(self):
        result = validate_audit()
        self.assertEqual((result["positive_recovery_cells"], result["twin_target_recovery_cells"]), (8, 0))
        self.assertEqual(result["preserved_failure_terminals"], 2)


if __name__ == "__main__":
    unittest.main()
