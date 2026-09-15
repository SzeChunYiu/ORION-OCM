#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import validate_foundations as vf


class FoundationTests(unittest.TestCase):
    def test_clean_package_validates(self):
        out = vf.run_all()
        self.assertEqual(out["gap_graph"], "valid")
        self.assertEqual(out["B1_B3_finite_reconstruction"]["minimum_used_states"], 3)
        self.assertFalse(out["N1_finite_reconstruction"]["bisimilar"])

    def test_critical_open_descendant_blocks_parent_closure(self):
        graph = vf.load_json("GMI_GAP_GRAPH.json")
        hostile = copy.deepcopy(graph)
        root = next(n for n in hostile["nodes"] if n["id"] == "ISSUE-833")
        root["status"] = "LOCALLY_CLOSED"
        with self.assertRaisesRegex(vf.ValidationError, "critical descendant"):
            vf.validate_gap_graph(hostile)

    def test_missing_falsifier_is_rejected(self):
        graph = vf.load_json("GMI_GAP_GRAPH.json")
        hostile = copy.deepcopy(graph)
        del hostile["nodes"][2]["falsifier"]
        with self.assertRaisesRegex(vf.ValidationError, "missing"):
            vf.validate_gap_graph(hostile)

    def test_parent_cycle_is_rejected(self):
        graph = vf.load_json("GMI_GAP_GRAPH.json")
        hostile = copy.deepcopy(graph)
        root = next(n for n in hostile["nodes"] if n["id"] == "ISSUE-833")
        root["parent"] = "ISSUE-834"
        with self.assertRaisesRegex(vf.ValidationError, "cycle"):
            vf.validate_gap_graph(hostile)

    def test_dependency_cycle_is_rejected(self):
        graph = vf.load_json("GMI_GAP_GRAPH.json")
        hostile = copy.deepcopy(graph)
        s1 = next(n for n in hostile["nodes"] if n["id"] == "CLAIM-S1")
        b = next(n for n in hostile["nodes"] if n["id"] == "CLAIM-B1-B3")
        s1["dependencies"] = ["CLAIM-B1-B3"]
        b["dependencies"] = ["CLAIM-S1"]
        with self.assertRaisesRegex(vf.ValidationError, "dependency cycle"):
            vf.validate_gap_graph(hostile)

    def test_unknown_prior_category_is_rejected(self):
        ledger = vf.load_json("PRIOR_LEDGER.json")
        hostile = copy.deepcopy(ledger)
        hostile["entries"][0]["category"] = "HIDDEN_ARCHITECTURE"
        with self.assertRaisesRegex(vf.ValidationError, "unknown prior category"):
            vf.validate_prior_ledger(hostile)

    def test_finite_check_cannot_be_declared_universal_proof(self):
        results = vf.load_json("RESULTS.json")
        hostile = copy.deepcopy(results)
        hostile["claims"][0]["universal_proof_from_finite_check"] = True
        with self.assertRaisesRegex(vf.ValidationError, "launders"):
            vf.validate_results(hostile)

    def test_symmetry_reconstruction_has_no_global_fixed_candidate(self):
        out = vf.symmetry_sanity(6)
        self.assertEqual(out["hypothesis_sizes"], 5)
        self.assertEqual(out["candidate_fixed_point_checks"], sum(range(2, 7)))

    def test_behavior_fixture_needs_three_exact_states(self):
        out = vf.behavior_quotient_sanity()
        self.assertEqual(
            {frozenset(x) for x in out["classes"]},
            {frozenset({0, 1}), frozenset({2}), frozenset({3})},
        )

    def test_n1_is_trace_equivalent_but_not_bisimilar(self):
        out = vf.nondeterminism_boundary_sanity()
        self.assertEqual(set(out["traces"]), {"epsilon", "a", "ab", "ac"})
        self.assertFalse(out["bisimilar"])

    def test_breaking_n1_trace_is_detected(self):
        graph = {
            "p0": [("a", "p1")],
            "p1": [("b", "z"), ("c", "z")],
            "q0": [("a", "qb"), ("a", "qc")],
            "qb": [("b", "z")],
            "qc": [],
            "z": [],
        }
        self.assertNotEqual(vf.finite_traces(graph, "p0"), vf.finite_traces(graph, "q0"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
