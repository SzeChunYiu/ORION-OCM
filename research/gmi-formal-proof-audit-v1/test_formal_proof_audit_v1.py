from __future__ import annotations

import unittest

from formal_proof_audit_v1 import finite_schema_checks, validate_audit


class FormalProofAuditTests(unittest.TestCase):
    def test_every_finite_schema_is_green(self):
        self.assertTrue(all(finite_schema_checks().values()))

    def test_canonical_corpus_and_all_section_o_controls(self):
        result = validate_audit()
        self.assertEqual(result["theorems"], 39)
        self.assertEqual(result["nearest_counterexamples"], 39)
        self.assertEqual(result["limit_families"], 5)
        self.assertEqual(result["ledger_rows"], 9)


if __name__ == "__main__":
    unittest.main()
