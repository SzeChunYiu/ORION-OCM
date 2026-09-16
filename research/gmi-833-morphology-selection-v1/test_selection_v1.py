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
SPEC = importlib.util.spec_from_file_location("selection_v1", HERE / "selection_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class NicheRepricingTests(unittest.TestCase):
    def test_parent_receipts_are_exactly_pinned(self):
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
            victim = tmp / M.PARENT_PINS[-1][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_positive_mass_niches_coexist(self):
        utilities = {"left": {"a": 4, "b": 0}, "right": {"a": 0, "b": 4}}
        self.assertEqual(M.niche_support(utilities, {"left": 1, "right": 2}), frozenset({"a", "b"}))

    def test_zero_mass_niche_does_not_add_support(self):
        utilities = {"left": {"a": 4, "b": 0}, "right": {"a": 0, "b": 4}}
        self.assertEqual(M.niche_support(utilities, {"left": 1, "right": 0}), frozenset({"a"}))

    def test_local_tie_preserves_complete_argmax_set(self):
        self.assertEqual(M.niche_support({"n": {"a": 1, "b": 1}}, {"n": 1}), frozenset({"a", "b"}))

    def test_global_aggregation_is_a_distinct_problem(self):
        utilities = {"left": {"a": 4, "b": 0}, "right": {"a": 0, "b": 4}}
        self.assertEqual(M.niche_support(utilities, {"left": 1, "right": 2}), frozenset({"a", "b"}))
        self.assertEqual(M.maximizers(M.aggregate_scores(utilities, {"left": 1, "right": 2})), ("b",))

    def test_niche_contract_fails_closed(self):
        with self.assertRaises(ValueError):
            M.niche_support({"x": {"a": 1}, "y": {"b": 1}}, {"x": 1, "y": 1})
        with self.assertRaises(ValueError):
            M.niche_support({"x": {"a": 1}}, {"x": 0})
        with self.assertRaises(ValueError):
            M.niche_support({"x": {"a": 1}}, {"x": -1})

    def test_repricing_transition_occurs_at_exact_boundary(self):
        qualities = {"a": 5, "b": 4}
        resources = {"a": (3,), "b": (1,)}
        boundary = M.one_dimensional_boundary(5, 3, 4, 1)
        self.assertEqual(boundary, Fraction(1, 2))
        self.assertEqual(M.maximizers(M.repriced_scores(qualities, resources, (0,))), ("a",))
        self.assertEqual(M.maximizers(M.repriced_scores(qualities, resources, (boundary,))), ("a", "b"))
        self.assertEqual(M.maximizers(M.repriced_scores(qualities, resources, (1,))), ("b",))

    def test_vector_repricing_hyperplane_is_exact(self):
        self.assertEqual(
            M.repricing_hyperplane(5, (3, 1), 4, (1, 2)),
            {"quality_gap": Fraction(1), "resource_gap": (Fraction(2), Fraction(-1))},
        )

    def test_dominance_prevents_repricing_flip(self):
        self.assertTrue(M.dominance_no_flip(5, (1, 0), 4, (2, 0), (100, 3)))
        with self.assertRaises(ValueError):
            M.dominance_no_flip(4, (2,), 5, (1,), (1,))

    def test_repricing_contract_fails_closed(self):
        with self.assertRaises(ValueError):
            M.repriced_scores({"a": 1}, {"a": (1,)}, (-1,))
        with self.assertRaises(ValueError):
            M.repriced_scores({"a": 1}, {"a": (1, 2)}, (1,))
        with self.assertRaises(ValueError):
            M.repriced_scores({"a": 1}, {"a": (1,)}, (0.5,))

    def test_exact_numeric_contract_rejects_float_and_bool(self):
        for value in (0.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M.exact(value)

    def test_bounded_census_counts(self):
        self.assertEqual(
            M.exhaustive_census(),
            {
                "niche_allocation_cases": 243,
                "disjoint_unique_coexistence_cases": 18,
                "repricing_cases": 1024,
                "dominance_no_flip_cases": 400,
                "strict_crossing_interval_cases": 26,
            },
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(M.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())
        self.assertEqual(json.loads(M.canonical_json(receipt)), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_keeps_all_other_rows_out(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("PROSPECTIVE_20_TRANSITIONS", receipt["forbidden_promotions"])
        self.assertIn("UNCONDITIONAL_UNIQUE_MORPHOLOGY", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
