#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import unittest

import foundation_v1 as f

HERE = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((HERE / name).read_text())


def assert_exact_tokens(testcase: unittest.TestCase, candidate, canonical):
    testcase.assertIsInstance(candidate, list)
    testcase.assertEqual(candidate, canonical)
    testcase.assertEqual(len(candidate), len(set(candidate)))


class GovernanceTokenTests(unittest.TestCase):
    def setUp(self):
        self.canonical = list(f.canonical_forbidden_promotions())

    def test_all_governance_consumers_match_exactly(self):
        registry = load("FORBIDDEN_PROMOTIONS_V1.json")
        manifest = load("MANIFEST_V1.json")
        reconciliation = load("ISSUE_833_RECONCILIATION_FOUNDATION_V1.json")
        receipt = load("RESULT_V1.json")
        self.assertEqual(registry["tokens"], self.canonical)
        for obj in (manifest, reconciliation, receipt, f.build_receipt()):
            assert_exact_tokens(self, obj["forbidden_promotions"], self.canonical)

    def test_missing_token_fails_exact_contract(self):
        bad = self.canonical[:-1]
        self.assertNotEqual(bad, self.canonical)

    def test_alias_token_fails_exact_contract(self):
        bad = list(self.canonical)
        bad[bad.index("P3_KNOWN_FAMILY_RECOVERY_COMPLETE")] = "KNOWN_FAMILIES_DERIVED_AT_P3"
        self.assertNotEqual(bad, self.canonical)

    def test_extra_token_fails_exact_contract(self):
        bad = self.canonical + ["UNREGISTERED_PROMOTION"]
        self.assertNotEqual(bad, self.canonical)

    def test_duplicate_token_fails_registry_validator(self):
        data = load("FORBIDDEN_PROMOTIONS_V1.json")
        duplicate = list(data["tokens"]) + [data["tokens"][0]]
        self.assertNotEqual(len(duplicate), len(set(duplicate)))

    def test_required_scientific_boundaries_are_present(self):
        required = {
            "COMPLETE_GMI",
            "ONTOLOGICAL_COMPLETENESS",
            "UNIVERSAL_ARCHITECTURE_PRIOR_FREEDOM",
            "ALL_EXISTING_RESULTS_AUDITED",
            "CORPUS_TERMINOLOGY_MIGRATED",
            "P3_KNOWN_FAMILY_RECOVERY_COMPLETE",
            "UNSEEN_FORM_DISCOVERY",
            "INDEPENDENT_REPLICATION",
            "REAL_SCALE_VALIDATION",
        }
        self.assertEqual(set(self.canonical), required)


if __name__ == "__main__":
    unittest.main(verbosity=2)
