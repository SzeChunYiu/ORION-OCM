#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cognitive_reaudit_v1", HERE / "cognitive_reaudit_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class CognitiveReauditTests(unittest.TestCase):
    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 8)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, path, _, _, _ in M.PARENT_PINS:
                target = tmp / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, target)
            victim = tmp / M.PARENT_PINS[0][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_registered_memory_roles_are_pairwise_distinct(self):
        result = M.audit_registered_memory_roles()
        self.assertTrue(result["all_pairwise_distinct"])
        self.assertEqual(len(result["pairs"]), 6)

    def test_memory_function_does_not_identify_partition(self):
        hostile = M.memory_partition_nonidentification_hostile()
        self.assertTrue(hostile["protected_profiles_equal"])
        self.assertFalse(hostile["physical_partition_identifiable"])

    def test_profile_contract_fails_closed(self):
        with self.assertRaises(ValueError):
            M.normalize_profile((1, 0))
        with self.assertRaises(ValueError):
            M.normalize_profile((1, 0, 0, 0, 2))

    def test_attention_exact_phase_law(self):
        win = M.attention_comparison(4, (1,), (1,), 2, 0, 1)
        lose = M.attention_comparison(4, (1,), (1,), 2, 0, 7)
        self.assertTrue(win["selective_strictly_rational"] and win["strict_iff"])
        self.assertFalse(lose["selective_strictly_rational"])
        self.assertTrue(lose["strict_iff"])

    def test_cost_never_legalizes_insufficient_attention(self):
        result = M.attention_comparison(4, (3,), (0,), 10, 100, 0)
        self.assertFalse(result["sufficient"])
        self.assertEqual(result["decision"], "INADMISSIBLE_SELECTION")

    def test_minimum_sufficient_selection_is_relevance_set(self):
        result = M.minimum_sufficient_selection(5, (1, 3))
        self.assertTrue(result["unique"])
        self.assertEqual(result["unique_minimizer"], (1, 3))

    def test_blind_selection_negative_control(self):
        result = M.blind_selection_hostile(4, 1)
        self.assertEqual(result["exact_fraction"], Fraction(1, 4))
        self.assertFalse(result["universally_exact"])

    def test_attention_contract_fails_closed(self):
        with self.assertRaises(ValueError):
            M.attention_comparison(0, (0,), (0,), 1)
        with self.assertRaises(ValueError):
            M.attention_comparison(2, (0,), (0,), 0.5)
        with self.assertRaises(ValueError):
            M.blind_selection_hostile(2, 2)

    def test_response_row_quotient_is_coarsest_exact(self):
        table = ((0, 1), (0, 1), (1, 0))
        quotient = M.response_row_quotient(table)
        minimal = M.quotient_minimality(table)
        self.assertEqual(quotient["labels"], (0, 0, 1))
        self.assertTrue(minimal["quotient_is_exact"] and minimal["coarsest_exact"])

    def test_partial_interface_requires_abstention(self):
        result = M.partial_interface_hostile()
        self.assertFalse(result["identifiable"])
        self.assertEqual(result["status"], M.CANNOT_IDENTIFY)

    def test_partial_interface_contract_fails_closed(self):
        with self.assertRaises(ValueError):
            M.partial_interface_identifiability((), (0,))
        with self.assertRaises(ValueError):
            M.partial_interface_identifiability((((0,),), ((1,),)), (0,))
        with self.assertRaises(ValueError):
            M.partial_interface_identifiability((((0,),),), ())

    def test_abstraction_adoption_is_not_formation(self):
        adopted = M.verified_abstraction_adoption(4, 5, 3, 1)
        rejected = M.verified_abstraction_adoption(2, 1, 1, 2)
        self.assertTrue(adopted["strictly_adopt"] and adopted["strict_iff"])
        self.assertFalse(adopted["semantics_created"])
        self.assertFalse(rejected["strictly_adopt"])
        self.assertTrue(rejected["strict_iff"])

    def test_exact_numeric_contract_rejects_float_bool_and_negative(self):
        for value in (True, 0.5):
            with self.assertRaises(ValueError):
                M.exact(value)
        with self.assertRaises(ValueError):
            M.verified_abstraction_adoption(1, -1, 0, 0)

    def test_exhaustive_census_counts(self):
        self.assertEqual(
            M.exhaustive_census(),
            {
                "memory_profile_pairs": 496,
                "attention_comparisons": 70308,
                "minimum_selection_cases": 57,
                "blind_attention_cases": 35,
                "quotient_tables": 370,
                "encoding_checks": 71662,
                "adoption_cases": 1000,
            },
        )

    def test_scientific_and_package_contracts(self):
        self.assertEqual(M.validate_ledgers(), {"claim_ledgers": 4, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"})
        self.assertEqual(M.validate_package_contracts(), {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 3, "source_pr": 919})

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        actual = M.canonical_json(receipt)
        self.assertEqual(actual, (HERE / "RESULT_V1.json").read_text())
        self.assertEqual(json.loads(actual), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_preserves_negative_results(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertIn("MEMORY_ANATOMY_IDENTIFIED", receipt["forbidden_promotions"])
        self.assertIn("GENERAL_CONCEPT_LEARNING_SOLVED", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
