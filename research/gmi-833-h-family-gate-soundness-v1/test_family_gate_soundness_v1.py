#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import family_gate_soundness_v1 as subject
import independent_oracle_v1 as oracle


class GateSoundnessTests(unittest.TestCase):
    def setUp(self):
        self.scope = subject.canonical_scope()

    def test_gate_count_and_named_rows_are_frozen(self):
        self.assertEqual(len(subject.GATES), 11)
        self.assertEqual(len(subject.FAMILY_ROWS), 43)
        self.assertEqual(len(set(subject.FAMILY_ROWS)), 43)

    def test_complete_same_scope_bundle_is_eligible(self):
        self.assertTrue(subject.closure_eligible(subject.complete_bundle(self.scope), self.scope))

    def test_proved_lower_bound_nonapplicability_is_eligible(self):
        bundle = subject.complete_bundle(self.scope, lower_bound_applicable=False)
        self.assertTrue(subject.closure_eligible(bundle, self.scope))

    def test_unproved_lower_bound_nonapplicability_fails(self):
        bundle = tuple(
            subject.Certificate(c.gate, subject.FAIL if c.gate == "lower_bound_where_possible" else c.status, c.scope)
            for c in subject.complete_bundle(self.scope)
        )
        self.assertFalse(subject.closure_eligible(bundle, self.scope))

    def test_each_missing_gate_independently_blocks(self):
        rows = subject.single_missing_gate_hostiles(self.scope)
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(not row["eligible"] for row in rows))

    def test_each_failed_gate_independently_blocks(self):
        rows = subject.single_failed_gate_hostiles(self.scope)
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(not row["eligible"] for row in rows))

    def test_duplicate_gate_fails_closed(self):
        bundle = subject.complete_bundle(self.scope)
        malformed = bundle[:-1] + (bundle[0],)
        self.assertFalse(subject.closure_eligible(malformed, self.scope))

    def test_unknown_gate_fails_closed(self):
        bundle = list(subject.complete_bundle(self.scope))
        bundle[-1] = subject.Certificate("unknown", subject.PASS, self.scope)
        self.assertFalse(subject.closure_eligible(tuple(bundle), self.scope))

    def test_each_scope_glue_independently_blocks(self):
        rows = subject.scope_gluing_hostiles(self.scope)
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(not row["eligible"] for row in rows))

    def test_finite_evidence_continuation_construction(self):
        census = subject.finite_evidence_census()
        self.assertEqual(census["observed_prefixes_checked"], 510)
        self.assertEqual(census["expected_prefixes"], 510)
        self.assertTrue(census["first_unobserved_disagreement_proved"])

    def test_invalid_continuation_inputs_rejected(self):
        with self.assertRaises(ValueError):
            subject.continuation_pair(())
        with self.assertRaises(ValueError):
            subject.continuation_pair((0, 2))

    def test_observational_nonidentifiability_witness(self):
        census = subject.observational_nonidentifiability_census()
        self.assertEqual(census["words_checked"], 511)
        self.assertTrue(census["profiles_equal"])
        self.assertTrue(census["hidden_organizations_distinct"])

    def test_remint_invariance(self):
        census = subject.remint_census()
        self.assertTrue(all(census[key] for key in ("gate_ids_unique", "family_ids_unique", "closure_invariant")))

    def test_reconciliation_preview_is_noop(self):
        preview = subject.reconciliation_preview()
        self.assertEqual(preview["mutations"], [])
        self.assertEqual(len(preview["named_rows"]), 43)
        self.assertTrue(all(not row["close"] for row in preview["named_rows"]))
        self.assertEqual(preview["aggregate_row"]["owner_pr"], 987)

    def test_independent_oracle_agrees(self):
        independent = oracle.run()
        primary = subject.build_result()
        self.assertEqual(independent["verdict"], "GREEN")
        self.assertEqual(primary["verdict"], "GREEN")
        self.assertEqual(independent["gate_width"], primary["gate_model"]["gate_count"])
        self.assertEqual(independent["finite_prefixes_checked"], primary["finite_evidence_non_promotion"]["observed_prefixes_checked"])
        self.assertEqual(independent["visible_words_checked"], primary["observational_family_nonidentifiability"]["words_checked"])

    def test_committed_results_are_canonical(self):
        expected = subject.canonical_bytes(subject.build_result())
        self.assertEqual((ROOT / "RESULT_V1.json").read_bytes(), expected)
        expected_preview = subject.canonical_bytes(subject.reconciliation_preview())
        self.assertEqual((ROOT / "ISSUE_833_RECONCILIATION_H_FAMILY_GATE_SOUNDNESS_V1.json").read_bytes(), expected_preview)
        self.assertEqual((ROOT / "ORACLE_RESULT_V1.json").read_bytes(), oracle.canonical_bytes(oracle.run()))

    def test_forbidden_promotions_are_explicit(self):
        result = subject.build_result()
        self.assertEqual(result["claim_ceiling"], subject.CLAIM_CEILING)
        self.assertEqual(set(result["forbidden_promotions"]), set(subject.FORBIDDEN_PROMOTIONS))
        self.assertEqual(result["section_h_audit"]["rows_closed_by_package"], 0)


if __name__ == "__main__":
    unittest.main()
