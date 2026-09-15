#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import random
import sys
import unittest

HERE = Path(__file__).resolve().parent
# CI uses python -I; admit only this package directory.
sys.path.insert(0, str(HERE))
import corpus_census_v1 as c


class CensusProtocolTests(unittest.TestCase):
    def test_discovery_rule(self):
        self.assertTrue(c.is_primary_candidate("research/gmi-foo-v1/CORE.md"))
        self.assertTrue(c.is_primary_candidate("research/gmi_bar/a.py"))
        self.assertTrue(c.is_primary_candidate("research/machine-intelligence-morphogenesis-v1/x.md"))
        self.assertFalse(c.is_primary_candidate("research/heritable-search-transformation-v1/x.md"))
        self.assertFalse(c.is_primary_candidate("src/gmi-foo/x.py"))

    def test_file_omission_fails_closed(self):
        expected = ["research/gmi-a/a.md", "research/gmi-b/b.md"]
        rows = [{"path": expected[0]}]
        with self.assertRaises(c.CensusError):
            c.validate_complete_file_census(expected, rows)

    def test_extra_file_fails_closed(self):
        with self.assertRaises(c.CensusError):
            c.validate_complete_file_census(["a"], [{"path":"a"}, {"path":"b"}])

    def test_cycle_detection(self):
        cycles = c.detect_cycles(["A","B","C"], {"A":["B"], "B":["C"], "C":["A"]})
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0][0], cycles[0][-1])

    def test_acyclic_graph(self):
        self.assertEqual(c.detect_cycles(["A","B","C"], {"A":["B"], "B":["C"]}), [])

    def test_provisional_id_is_location_and_statement_bound(self):
        a = c.provisional_id("p", 1, "Theorem T")
        self.assertEqual(a, c.provisional_id("p", 1, "Theorem   T"))
        self.assertNotEqual(a, c.provisional_id("p", 2, "Theorem T"))
        self.assertNotEqual(a, c.provisional_id("q", 1, "Theorem T"))

    def test_quantifier_narrowing_prefers_finite_marker(self):
        self.assertEqual(c.quantifier_for("For all 64 states in this finite exact scope"), "FINITE_EXACT")
        self.assertEqual(c.quantifier_for("universal over all systems"), "UNIVERSAL")
        self.assertEqual(c.quantifier_for("held-out protected split"), "HELD_OUT")

    def test_exhaustive_evidence_is_computer_assisted_not_universal_proof(self):
        mode = c.proof_mode_for("exhaustive enumeration of all 128 cases", "x.md")
        self.assertEqual(mode, "COMPUTER_ASSISTED_EXHAUSTIVE")
        self.assertNotEqual(mode, "ANALYTIC_DEDUCTIVE")

    def test_scientific_marker_is_not_silently_dropped(self):
        objs = c.scientific_objects("research/gmi-x/THEOREM.md", "## Theorem T-1: finite exact law", "a"*40)
        self.assertEqual(len(objs), 1)
        self.assertEqual(objs[0]["object_class"], "THEOREM")
        self.assertIn(objs[0]["audit_disposition"], {"AMBER","GREEN"})

    def test_claim_dependency_parser_is_explicit_only(self):
        self.assertEqual(c.claim_dependencies_for("theorem-dependencies: A-1, B-2"), ["A-1","B-2"])
        self.assertEqual(c.claim_dependencies_for("see theorem A-1 for discussion"), [])

    def test_canonical_json_is_order_invariant_for_mappings(self):
        a = c.canonical_json_bytes({"z":1,"a":{"q":2,"b":3}})
        b = c.canonical_json_bytes({"a":{"b":3,"q":2},"z":1})
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))

    def test_gap_schema_has_recursive_closure_fields(self):
        gap = c.make_gap(gap_id="G", claim_id="C", premise="p", inference="i",
                         assumption="a", counterexample="x", severity="CRITICAL", evidence="e")
        for key in ("id","claim_id","premise","inference","unresolved_assumption",
                    "possible_counterexample","severity","owner_role","parent_result",
                    "evidence_needed","status","materiality","descendants"):
            self.assertIn(key, gap)
        self.assertEqual(gap["status"], "OPEN")

    def test_file_role_receipt_and_tests(self):
        self.assertEqual(c.file_role("research/gmi-x/RESULT_V1.json", b"{}") [0], "RECEIPT_OR_RESULT")
        self.assertEqual(c.file_role("research/gmi-x/test_x.py", b"") [0], "TEST_OR_HOSTILE")

    def test_output_determinism_under_input_mapping_reorder(self):
        items = [(str(i), i) for i in range(20)]
        m1 = dict(items)
        random.Random(9).shuffle(items)
        m2 = dict(items)
        self.assertEqual(c.canonical_json_bytes(m1), c.canonical_json_bytes(m2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
