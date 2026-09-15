from __future__ import annotations

import copy
import unittest

from audit_section_r_v1 import AuditError, load_manifest, validate_manifest


class SectionRAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest()

    def test_registered_audit_result_is_conservative(self) -> None:
        result = validate_manifest(self.manifest)
        self.assertEqual(result["registered_classes"], 14)
        self.assertEqual(result["enumerability"]["pass_count"], 2)
        self.assertEqual(result["enumerability"]["gap_count"], 12)
        self.assertFalse(result["enumerability"]["section_r_row_earned"])
        self.assertEqual(result["minimal_negative_twin"]["pass_count"], 0)
        self.assertEqual(result["minimal_negative_twin"]["gap_count"], 14)
        self.assertFalse(result["minimal_negative_twin"]["section_r_row_earned"])
        self.assertFalse(result["ledger_policy"]["current_reconciliation_required"])

    def test_omitting_registered_class_fails(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["classes"].pop()
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_duplicate_alias_fails(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["classes"][-1]["class_id"] = mutated["classes"][0]["class_id"]
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_missing_pass_artifact_fails(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["classes"][0]["canonical_artifact"] = "research/definitely-missing-R1-artifact.py"
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_pass_without_finite_universe_fails(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["classes"][0]["enumerability"]["finite_universe_definition"] = "bounded examples"
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_gap_cannot_be_laundered_into_enumerability_pass(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        row = mutated["classes"][2]
        row["enumerability"] = {
            "status": "PASS",
            "finite_universe_definition": "all registered examples",
            "certificate_or_exact_oracle": "claimed exact",
            "replay": "python missing.py",
            "evidence_class": "P2",
        }
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_minimal_twin_without_finite_order_fails(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        row = mutated["classes"][0]
        row["minimal_twin"] = {
            "status": "PASS",
            "twin_artifact": row["canonical_artifact"],
            "intervention": {"changed_coordinates": ["task"]},
            "minimality_order": {"finite": False},
            "minimality_proof": "claimed",
        }
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_uncontrolled_multi_coordinate_twin_fails(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        row = mutated["classes"][0]
        row["minimal_twin"] = {
            "status": "PASS",
            "twin_artifact": row["canonical_artifact"],
            "intervention": {"changed_coordinates": ["task", "budget"]},
            "minimality_order": {"finite": True},
            "minimality_proof": "claimed",
        }
        with self.assertRaises(AuditError):
            validate_manifest(mutated)

    def test_counts_are_derived_not_manifest_fields(self) -> None:
        mutated = copy.deepcopy(self.manifest)
        mutated["claimed_enumerability_pass_count"] = 14
        result = validate_manifest(mutated)
        self.assertEqual(result["enumerability"]["pass_count"], 2)
        self.assertFalse(result["enumerability"]["section_r_row_earned"])


if __name__ == "__main__":
    unittest.main()
