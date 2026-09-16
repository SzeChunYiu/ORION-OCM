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
SPEC = importlib.util.spec_from_file_location("capability_abstention_v1", HERE / "capability_abstention_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class CapabilityAbstentionTests(unittest.TestCase):
    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 5)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, path, _, _, _ in M.PARENT_PINS:
                target = tmp / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, target)
            victim = tmp / M.PARENT_PINS[2][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_binary_nonidentification_must_abstain(self):
        result = M.capability_query_disposition(("m0", "m1"), ("m0", "m1"), {"m0": 0, "m1": 1})
        self.assertEqual(result["status"], "CANNOT_IDENTIFY")
        self.assertEqual(result["identified_set"], (0, 1))
        self.assertIsNone(result["point_prediction"])

    def test_singleton_image_emits_exact_point(self):
        result = M.capability_query_disposition(("m0", "m1"), ("m0",), {"m0": Fraction(2, 3), "m1": 1})
        self.assertEqual(result["status"], "IDENTIFIED")
        self.assertEqual(result["identified_set"], (Fraction(2, 3),))
        self.assertEqual(result["point_prediction"], Fraction(2, 3))

    def test_coarser_query_can_be_identified_without_model_identity(self):
        result = M.capability_query_disposition(("m0", "m1"), ("m0", "m1"), {"m0": 7, "m1": 7})
        self.assertEqual(result["status"], "IDENTIFIED")
        self.assertEqual(result["point_prediction"], 7)

    def test_forced_point_on_non_singleton_image_has_counterexample(self):
        for chosen, expected in ((0, 1), (1, 0)):
            result = M.forced_point_counterexample(("m0", "m1"), {"m0": 0, "m1": 1}, chosen)
            self.assertFalse(result["uniformly_sound"])
            self.assertEqual(result["counterexample_value"], expected)

    def test_forced_point_theorem_rejects_wrong_premises(self):
        with self.assertRaises(ValueError):
            M.forced_point_counterexample(("m0",), {"m0": 0}, 0)
        with self.assertRaises(ValueError):
            M.forced_point_counterexample(("m0", "m1"), {"m0": 0, "m1": 1}, 2)

    def test_inconsistency_and_cannot_check_are_distinct(self):
        empty = M.capability_query_disposition(("m0",), (), None)
        missing = M.capability_query_disposition(("m0",), ("m0",), None)
        nontotal = M.capability_query_disposition(("m0", "m1"), ("m0",), {"m0": 0})
        self.assertEqual(empty["status"], "INCONSISTENT_REGISTERED_ASSUMPTIONS")
        self.assertEqual(missing["status"], "CANNOT_CHECK_QUERY_NOT_REGISTERED")
        self.assertEqual(nontotal["status"], "CANNOT_CHECK_QUERY_NOT_TOTAL_ON_DOMAIN")

    def test_confidence_budget_is_preserved_on_abstention(self):
        result = M.capability_query_disposition(
            ("m0", "m1"), ("m0", "m1"), {"m0": 0, "m1": 1},
            uncertainty_kind="CONFIDENCE_SET", alpha=Fraction(1, 20),
        )
        self.assertEqual(result["status"], "CANNOT_IDENTIFY")
        self.assertEqual(result["failure_budget"], Fraction(1, 20))
        self.assertEqual(result["coverage_lower_bound"], Fraction(19, 20))

    def test_confidence_budget_is_preserved_on_identified_point(self):
        result = M.capability_query_disposition(
            ("m0", "m1"), ("m0", "m1"), {"m0": 3, "m1": 3},
            uncertainty_kind="CONFIDENCE_SET", alpha=Fraction(1, 4),
        )
        self.assertEqual(result["status"], "IDENTIFIED")
        self.assertEqual(result["point_prediction"], 3)
        self.assertEqual(result["coverage_lower_bound"], Fraction(3, 4))

    def test_feasible_set_cannot_fabricate_calibration(self):
        with self.assertRaises(ValueError):
            M.capability_query_disposition(("m0",), ("m0",), {"m0": 0}, alpha=Fraction(1, 20))

    def test_confidence_contract_fails_closed(self):
        for alpha in (None, -1, Fraction(5, 4), 0.1, True):
            with self.subTest(alpha=alpha), self.assertRaises(ValueError):
                M.capability_query_disposition(
                    ("m0",), ("m0",), {"m0": 0},
                    uncertainty_kind="CONFIDENCE_SET", alpha=alpha,
                )

    def test_domain_and_query_contract_fail_closed(self):
        with self.assertRaises(ValueError):
            M.capability_query_disposition((), (), {})
        with self.assertRaises(ValueError):
            M.capability_query_disposition(("m0", "m0"), ("m0",), {"m0": 0})
        with self.assertRaises(ValueError):
            M.capability_query_disposition(("m0",), ("outside",), {"m0": 0})
        with self.assertRaises(ValueError):
            M.capability_query_disposition(("m0",), ("m0",), {"m0": 0.5})
        with self.assertRaises(ValueError):
            M.capability_query_disposition(("m0",), ("m0",), {"m0": 0}, uncertainty_kind="OTHER")

    def test_bounded_census_counts(self):
        self.assertEqual(
            M.exhaustive_census(),
            {
                "feasible_query_cases": 64,
                "confidence_query_cases": 192,
                "forced_point_counterexamples": 36,
                "missing_query_cases": 8,
            },
        )

    def test_scientific_ledger_is_complete_but_review_stays_open(self):
        self.assertEqual(
            M.validate_ledgers(),
            {"claim_ledgers": 2, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        )

    def test_manifest_and_reconciliation_are_exactly_scoped_to_pr(self):
        self.assertEqual(
            M.validate_package_contracts(),
            {
                "manifest_ok": True,
                "reconciliation_ok": True,
                "reconciliation_rows": 1,
                "source_pr": 916,
            },
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(M.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())
        self.assertEqual(json.loads(M.canonical_json(receipt)), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_keeps_predictor_and_calibration_open(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("CAPABILITY_PREDICTOR_COMPLETED", receipt["forbidden_promotions"])
        self.assertIn("CALIBRATION_FROM_FEASIBILITY_ALONE", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
