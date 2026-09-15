#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import foundation_v1 as f
import reconcile_issue_833_v1 as r


class FoundationTests(unittest.TestCase):
    def test_countable_uniform_prior_impossible(self):
        self.assertFalse(f.countable_equal_mass_witness(0)["possible"])
        for c in (Fraction(1, 2), Fraction(1, 10), Fraction(1, 1000)):
            w = f.countable_equal_mass_witness(c)
            self.assertFalse(w["possible"])
            self.assertGreater(Fraction(w["prefix_mass"]), 1)
        with self.assertRaises(f.FoundationError):
            f.countable_equal_mass_witness(-1)

    def test_no_renaming_invariant_unique_selector_nontrivial(self):
        self.assertTrue(f.deterministic_prior_free_unique_selector_exists(1))
        for n in range(2, 7):
            self.assertFalse(f.deterministic_prior_free_unique_selector_exists(n))

    def test_prior_levels_and_relative_prior_free(self):
        base = {
            "claim_id": "x",
            "named_architecture_visible": False,
            "family_property_vector_visible": False,
            "representation_operator_family_supplied": False,
            "generic_primitives_only": True,
            "recursive_primitive_invention": False,
            "priors": {k: [f"declared-{k}"] for k in f.PRIOR_CATEGORIES},
            "encoding": "prefix syntax",
            "cost_model": "node count",
            "search_strategy": "breadth first",
            "ecology_generator": "registered finite generator",
            "evaluation_rule": "exact behavioral satisfaction",
            "posthoc_family_mapping_only": True,
        }
        for level, mut in (
            ("P0", {"named_architecture_visible": True, "generic_primitives_only": False}),
            ("P1", {"family_property_vector_visible": True, "generic_primitives_only": False}),
            ("P2", {"representation_operator_family_supplied": True, "generic_primitives_only": False}),
            ("P3", {}),
            ("P4", {"recursive_primitive_invention": True}),
        ):
            rec = dict(base)
            rec.update(mut)
            rec["declared_level"] = level
            f.validate_prior_disclosure(rec)
            self.assertEqual(f.infer_prior_level(rec), level)
            self.assertEqual(f.architecture_prior_free_relative(rec), level in {"P3", "P4"})

    def test_prior_disclosure_rejects_hidden_fields(self):
        rec = {
            "claim_id": "x", "declared_level": "P3",
            "named_architecture_visible": False,
            "family_property_vector_visible": False,
            "representation_operator_family_supplied": False,
            "generic_primitives_only": True,
            "recursive_primitive_invention": False,
            "priors": {k: [] for k in f.PRIOR_CATEGORIES},
            "encoding": "e", "cost_model": "c", "search_strategy": "s",
            "ecology_generator": "g", "evaluation_rule": "v",
            "posthoc_family_mapping_only": True,
        }
        bad = dict(rec); bad["priors"] = {"architectural": []}
        with self.assertRaises(f.FoundationError): f.validate_prior_disclosure(bad)
        bad = dict(rec); bad["cost_model"] = ""
        with self.assertRaises(f.FoundationError): f.validate_prior_disclosure(bad)

    def test_open_gap_schema(self):
        gap = {
            "id": "G1", "claim_id": "C1", "premise": "P", "inference": "P -> Q",
            "unresolved_assumption": "A", "possible_counterexample": "X",
            "severity": "CRITICAL", "owner_role": "formal-review", "parent_result": "R0",
            "evidence_needed": "proof or witness", "status": "OPEN",
            "materiality": "could reverse truth or quantifier scope", "descendants": [],
        }
        f.validate_open_gap(gap)
        bad = dict(gap); bad.pop("inference")
        with self.assertRaises(f.FoundationError): f.validate_open_gap(bad)

    def test_behavioral_spec_is_legacy_semantics_preserving(self):
        legal = {"i0": ["ok", "bad"], "i1": ["yes", "no"]}
        legacy = lambda i, t: (i, t) in {("i0", "ok"), ("i1", "yes")}
        spec = f.legacy_obligation_to_behavioral_spec(("i0", "i1"), legal, legacy)
        for i, traces in legal.items():
            for t in traces:
                self.assertEqual(spec.accepts(i, t), legacy(i, t))

    def test_response_quotient_and_bad_encoding(self):
        histories = ("u0", "u1", "s", "l")
        conts = ("query", "teach")
        table = {
            ("u0", "query"): 0, ("u1", "query"): 0, ("s", "query"): 0, ("l", "query"): 1,
            ("u0", "teach"): 1, ("u1", "teach"): 1, ("s", "teach"): 0, ("l", "teach"): 1,
        }
        response = lambda h, c: table[(h, c)]
        q = f.quotient_by_protected_responses(histories, conts, response)
        self.assertEqual(q, (("l",), ("s",), ("u0", "u1")))
        self.assertTrue(f.encoding_refines_response_quotient(histories, conts, response, lambda h: {"u0":0,"u1":0,"s":1,"l":2}[h]))
        self.assertFalse(f.encoding_refines_response_quotient(histories, conts, response, lambda h: 0))

    def test_positive_scalarization_preserves_pareto(self):
        vectors = list(__import__("itertools").product(range(3), repeat=3))
        weights = [(1,1,1), (100,1,1), (1,100,1), (1,1,100)]
        for a in vectors:
            for b in vectors:
                if f.pareto_strictly_dominates(a,b):
                    for w in weights: self.assertLess(f.scalar_cost(a,w), f.scalar_cost(b,w))

    def test_incomparable_pairs_have_positive_weight_reversals(self):
        cert = f.exhaustive_pareto_certificate()
        self.assertEqual(cert["vectors"], 27)
        self.assertEqual(cert["unordered_pairs"], 351)
        self.assertEqual(cert["dominance_pairs"], 189)
        self.assertEqual(cert["incomparable_pairs"], 162)
        self.assertEqual(cert["incomparable_reversals_constructed"], 162)

    def test_negative_or_zero_weights_rejected_for_strict_scalarization(self):
        with self.assertRaises(f.FoundationError): f.scalar_cost((1,2), (1,0))
        with self.assertRaises(f.FoundationError): f.scalar_cost((1,2), (1,-1))

    def test_receipt_is_deterministic(self):
        a = f.build_receipt(); b = f.build_receipt()
        self.assertEqual(a,b)
        self.assertEqual(a["pareto_certificate"]["incomparable_pairs"], 162)
        self.assertIn("ONTOLOGICAL_COMPLETENESS", a["forbidden_promotions"])

    def test_committed_machine_readable_artifacts(self):
        schema = json.loads((HERE / "FOUNDATION_SCHEMA_V1.json").read_text())
        self.assertEqual(schema["prior_categories"], list(f.PRIOR_CATEGORIES))
        self.assertEqual(list(schema["prior_levels"]), list(f.PRIOR_LEVELS))
        prior = json.loads((HERE / "PRIOR_DISCLOSURE_EXAMPLE_V1.json").read_text())
        f.validate_prior_disclosure(prior)
        self.assertTrue(f.architecture_prior_free_relative(prior))
        gap = json.loads((HERE / "OPEN_GAP_EXAMPLE_V1.json").read_text())
        f.validate_open_gap(gap)
        committed = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(committed, f.build_receipt())
        manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
        for name in manifest["artifacts"]: self.assertTrue((HERE / name).is_file(), name)

    def test_reconciliation_spec_is_scoped_and_valid(self):
        spec = json.loads((HERE / "ISSUE_833_RECONCILIATION_FOUNDATION_V1.json").read_text())
        self.assertEqual(spec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(spec["issue"], 833)
        self.assertGreater(len(spec["replacements"]), 0)
        old_lines = [row["old"] for row in spec["replacements"]]
        self.assertEqual(len(old_lines), len(set(old_lines)))
        self.assertNotIn("- [ ] Re-score every major existing GMI result on the maturity ladder.", old_lines)
        self.assertNotIn("- [ ] Replace ambiguous uses of `obligation` in paper-facing theory with academically grounded terminology (`task`, `behavioral specification`, `requirement`, etc.) while preserving exact legacy mappings.", old_lines)


class ReconcilerTests(unittest.TestCase):
    BODY = """# A. Scientific constitution and claim discipline
- [ ] Define architecture-prior-free derivation formally.
- [ ] Prove why literally assumption-free/prior-free derivation is impossible or ill-posed.
- [ ] Define evidence levels for every GMI claim.

## A. Similar but nested heading
- [ ] Define architecture-prior-free derivation formally. EXTRA

# B. Next
- [ ] unrelated
"""

    def test_exact_line_and_heading_matching(self):
        spec = {"schema":"GMI_ISSUE_RECONCILIATION_V2","issue":833,"replacements":[{
            "anchor":"# A. Scientific constitution and claim discipline",
            "old":"- [ ] Define architecture-prior-free derivation formally.",
            "new":"- [x] Define architecture-prior-free derivation formally. — evidence",
        }],"forbidden_promotions":[]}
        updated, rows = r.reconcile_body(self.BODY, spec)
        self.assertIn("- [x] Define architecture-prior-free derivation formally. — evidence", updated)
        self.assertIn("- [ ] Define architecture-prior-free derivation formally. EXTRA", updated)
        self.assertEqual(rows[0]["status"], "READY_TO_APPLY")

    def test_anchor_must_be_exact_heading_line(self):
        spec = {"schema":"GMI_ISSUE_RECONCILIATION_V2","issue":833,"replacements":[
            {"anchor":"A. Scientific constitution","old":"- [ ] x","new":"- [x] x"}],"forbidden_promotions":[]}
        with self.assertRaises(r.ReconcileError): r.reconcile_body(self.BODY, spec)

    def test_short_old_line_cannot_rewrite_longer_line(self):
        spec = {"schema":"GMI_ISSUE_RECONCILIATION_V2","issue":833,"replacements":[{
            "anchor":"## A. Similar but nested heading",
            "old":"- [ ] Define architecture-prior-free derivation formally.",
            "new":"- [x] Define architecture-prior-free derivation formally.",
        }],"forbidden_promotions":[]}
        with self.assertRaises(r.ReconcileError): r.reconcile_body(self.BODY, spec)


if __name__ == "__main__":
    unittest.main(verbosity=2)
