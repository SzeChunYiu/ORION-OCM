#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("robustness_controls_v1", HERE / "robustness_controls_v1.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class RobustnessControlsV1Tests(unittest.TestCase):
    def receipt(self):
        return mod.build_receipt()

    def test_receipt_green_and_byte_reproducible(self):
        r = self.receipt()
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(json.loads(mod.canonical_json(r)), expected)
        self.assertEqual(mod.canonical_json(r), (HERE / "RESULT_V1.json").read_text())

    def test_matched_grammar_twin_positive(self):
        rec = mod.positive_fixture()
        r = mod.grammar_twin_audit(rec["grammar_positive"], rec["grammar_negative"], rec["grammar_positive_context"], rec["grammar_negative_context"])
        self.assertTrue(r["matched"])
        self.assertEqual(r["terminal"], "GRAMMAR_TWIN_MATCHED")
        self.assertEqual(r["mechanism_free_positive"], r["mechanism_free_negative"])
        self.assertEqual(r["target_candidates_removed"], 2)

    def test_grammar_twin_background_capacity_hostile(self):
        p, n, ctx = mod.unmatched_grammar_fixture()
        r = mod.grammar_twin_audit(p, n, ctx, dict(ctx))
        self.assertEqual(r["terminal"], "GRAMMAR_TWIN_UNMATCHED")
        self.assertFalse(r["background_multiset_equal"])

    def test_grammar_twin_context_hostile(self):
        rec = mod.positive_fixture()
        ctx2 = dict(rec["grammar_negative_context"])
        ctx2["budget"] = 7
        r = mod.grammar_twin_audit(rec["grammar_positive"], rec["grammar_negative"], rec["grammar_positive_context"], ctx2)
        self.assertEqual(r["terminal"], "GRAMMAR_TWIN_UNMATCHED")
        self.assertFalse(r["context_equal"])

    def test_grammar_twin_target_remaining_hostile(self):
        rec = mod.positive_fixture()
        neg = list(rec["grammar_negative"]) + [rec["grammar_positive"][0]]
        r = mod.grammar_twin_audit(rec["grammar_positive"], neg, rec["grammar_positive_context"], rec["grammar_negative_context"])
        self.assertEqual(r["reason"], "TARGET_MECHANISM_REMAINS_IN_NEGATIVE")

    def test_grammar_twin_missing_fails_closed(self):
        self.assertEqual(mod.grammar_twin_audit(None, None, None, None)["terminal"], "CANNOT_AUDIT_GRAMMAR_TWIN")

    def test_encoding_remint_positive(self):
        rec = mod.positive_fixture()
        r = mod.encoding_audit(rec["encoding_1"], rec["encoding_2"], rec["remint_map"], rec["encoding_result_1"], rec["encoding_result_2"])
        self.assertEqual(r["terminal"], "ENCODING_INVARIANT_AT_REGISTERED_REMINTS")
        self.assertEqual(r["canonical_result_1"], "B")
        self.assertEqual(r["canonical_result_2"], "B")

    def test_encoding_surface_tie_hostile(self):
        rec = mod.sensitive_fixture()
        r = mod.encoding_audit(rec["encoding_1"], rec["encoding_2"], rec["remint_map"], rec["encoding_result_1"], rec["encoding_result_2"])
        self.assertEqual(r["terminal"], "ENCODING_SENSITIVE")
        self.assertNotEqual(r["canonical_result_1"], r["canonical_result_2"])

    def test_nonbijective_remint_fails_closed(self):
        r = mod.encoding_audit({"a": "A", "b": "B"}, {"x": "A", "y": "B"}, {"a": "x", "b": "x"}, "a", "x")
        self.assertEqual(r["reason"], "REMINT_NOT_BIJECTIVE")

    def test_nonsemantic_remint_fails_closed(self):
        r = mod.encoding_audit({"a": "A", "b": "B"}, {"x": "B", "y": "A"}, {"a": "x", "b": "y"}, "a", "x")
        self.assertEqual(r["reason"], "REMINT_NOT_SEMANTICS_PRESERVING")

    def test_alternate_search_positive(self):
        r = mod.search_audit(mod.positive_fixture()["search_runs"])
        self.assertEqual(r["terminal"], "SEARCH_INVARIANT_AT_REGISTERED_ALGORITHMS")
        self.assertEqual(r["winners"], ["B", "B"])
        self.assertEqual(len(set(r["strategy_signatures"])), 2)

    def test_renaming_same_search_is_not_alternate(self):
        r = mod.search_audit([
            {"strategy_id": "a", "strategy_signature": ("same", "same"), "objective_id": "o", "declared_budget": 2, "canonical_winner": "A"},
            {"strategy_id": "b", "strategy_signature": ("same", "same"), "objective_id": "o", "declared_budget": 2, "canonical_winner": "A"},
        ])
        self.assertEqual(r["reason"], "SEARCHERS_NOT_MATERIALLY_DISTINCT")

    def test_alternate_search_early_stop_hostile(self):
        r = mod.search_audit(mod.sensitive_fixture()["search_runs"])
        self.assertEqual(r["terminal"], "SEARCH_ALGORITHM_SENSITIVE")
        self.assertEqual(r["winners"], ["A", "B"])

    def test_search_budget_mismatch_abstains(self):
        r = mod.search_audit([
            {"strategy_id": "a", "strategy_signature": ("a",), "objective_id": "o", "declared_budget": 1, "canonical_winner": "A"},
            {"strategy_id": "b", "strategy_signature": ("b",), "objective_id": "o", "declared_budget": 2, "canonical_winner": "A"},
        ])
        self.assertEqual(r["terminal"], "CANNOT_COMPARE_SEARCH_BUDGETS")

    def test_branch_and_bound_lower_bound_must_be_admissible(self):
        with self.assertRaisesRegex(ValueError, "lower bound"):
            mod.branch_and_bound_search({"A": Fraction(1)}, {"A": Fraction(2)}, ["A"])

    def test_positive_weights_preserve_dominance(self):
        vectors = {"best": (Fraction(1), Fraction(1)), "worse": (Fraction(2), Fraction(3))}
        r = mod.scalarization_audit(vectors, [(1, 4), (4, 1)])
        self.assertEqual(r["pareto_front"], ("best",))
        self.assertEqual(r["winners"], (("best",), ("best",)))

    def test_incomparable_vectors_reverse_under_positive_weights(self):
        r = mod.scalarization_audit({"a": (1, 4), "b": (4, 1)}, [(4, 1), (1, 4)])
        self.assertEqual(r["terminal"], "PRICE_SENSITIVE")
        self.assertEqual(r["pareto_front"], ("a", "b"))
        self.assertEqual(r["winners"], (("a",), ("b",)))

    def test_duplicate_weights_are_not_alternates(self):
        r = mod.scalarization_audit({"a": (1, 4), "b": (4, 1)}, [(1, 1), (1, 1)])
        self.assertEqual(r["reason"], "SCALARIZATIONS_NOT_DISTINCT")

    def test_nonpositive_weight_fails_closed(self):
        r = mod.scalarization_audit({"a": (1, 4), "b": (4, 1)}, [(1, 1), (1, 0)])
        self.assertEqual(r["reason"], "WEIGHTS_MUST_BE_STRICTLY_POSITIVE")

    def test_negative_resource_coordinate_fails_closed(self):
        r = mod.scalarization_audit({"a": (1, -1), "b": (4, 1)}, [(1, 1), (2, 1)])
        self.assertEqual(r["reason"], "INVALID_RESOURCE_VECTOR")

    def test_two_sample_weights_do_not_license_universal_invariance(self):
        sample = mod.scalarization_audit({"a": (1, 4), "b": (4, 1)}, [(3, 2), (4, 2)])
        unseen = mod.scalarization_audit({"a": (1, 4), "b": (4, 1)}, [(3, 2), (1, 4)])
        self.assertEqual(sample["terminal"], "SCALARIZATION_INVARIANT_AT_REGISTERED_WEIGHTS")
        self.assertEqual(unseen["terminal"], "PRICE_SENSITIVE")

    def test_sensitive_record_still_satisfies_control_requirement(self):
        r = mod.audit_record(mod.sensitive_fixture())
        self.assertTrue(r["requirements_satisfied"])
        self.assertEqual(r["control_requirements_terminal"], "CONTROL_REQUIREMENTS_SATISFIED")
        self.assertEqual(r["terminal"], "SENSITIVE_AT_REGISTERED_CONTROLS")

    def test_missing_control_census_exact(self):
        c = mod.missing_control_census()
        self.assertEqual(c["cases"], 16)
        self.assertEqual(c["satisfying_cases"], 1)
        self.assertEqual(c["failures"], [])

    def test_claim_ceiling_and_parent_pins_bounded(self):
        r = self.receipt()
        self.assertEqual(r["claim_ceiling"], "GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE")
        self.assertEqual(len(r["parent_pins"]), 2)
        self.assertIn("COMPLETE_GMI", r["forbidden_promotions"])
        self.assertIn("ALL_GMI_RESULTS_ROBUST", r["forbidden_promotions"])

    def test_no_floats_in_receipt(self):
        def walk(x):
            if isinstance(x, float):
                self.fail("float found in exact receipt")
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, (list, tuple)):
                for v in x:
                    walk(v)
        walk(self.receipt())


if __name__ == "__main__":
    unittest.main()
