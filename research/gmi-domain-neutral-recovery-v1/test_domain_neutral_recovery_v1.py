from __future__ import annotations

import unittest

from domain_neutral_recovery_v1 import (
    constructive_recovery_certificate,
    local_recovery_certificate,
    relational_recovery_certificate,
    validate_closure,
)


class DomainNeutralRecoveryTests(unittest.TestCase):
    def test_relational_recovery_changes_in_disjoint_twin(self):
        result = relational_recovery_certificate()
        self.assertEqual(result["winner"], ("equal", "merge"))
        self.assertNotEqual(result["winner"], result["twin_winner"])

    def test_local_recovery_changes_when_site_law_changes(self):
        result = local_recovery_certificate()
        self.assertEqual(result["winner"], ("triple", "shared", "snapshot"))
        self.assertEqual(result["twin_winner"], ("triple", "site", "snapshot"))

    def test_constructive_recovery_changes_for_shallow_queries(self):
        result = constructive_recovery_certificate()
        self.assertEqual(result["closure_size"], 14)
        self.assertEqual(result["winner"], (True, 2))
        self.assertEqual(result["twin_winner"], (False, 0))

    def test_exactly_three_scoped_tasks_close(self):
        self.assertEqual(validate_closure()["ledger_rows"], 3)


if __name__ == "__main__":
    unittest.main()
