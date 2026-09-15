#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("parent_equivalence_v1", HERE / "parent_equivalence_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


class ParentEquivalenceV1Tests(unittest.TestCase):
    def test_receipt_green(self):
        r = mod.build_receipt()
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))

    def test_committed_receipt_reproduces(self):
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(mod.build_receipt(), expected)
        self.assertEqual(mod.canonical_json(expected), (HERE / "RESULT_V1.json").read_text())

    def test_dfa_witness_is_reachable_and_nonminimal(self):
        w = mod.dfa_witness()
        self.assertEqual(w["reachable"], (0, 1, 2, 3))
        self.assertEqual(w["behavior_partition"], ((0,), (1, 2), (3,)))
        self.assertEqual(w["behavior_partition"], w["bisimulation_partition"])
        cls = {s: i for i, block in enumerate(w["behavior_partition"]) for s in block}
        for a in w["actions"]:
            self.assertEqual(cls[w["transition"][(1, a)]], cls[w["transition"][(2, a)]])

    def test_exhaustive_deterministic_bisimulation_certificate(self):
        c = mod.exhaustive_deterministic_census()
        self.assertEqual(c["machines"], 5832)
        self.assertEqual(c["machines"], c["expected_machines"])
        self.assertEqual(c["mismatch_count"], 0)

    def test_nondeterministic_trace_bisimulation_boundary(self):
        h = mod.nondeterministic_hostile()
        self.assertEqual(h["p_traces"], ("", "a", "ab", "ac"))
        self.assertEqual(h["p_traces"], h["q_traces"])
        self.assertTrue(h["trace_equal"])
        self.assertFalse(h["strong_bisimilar"])

    def test_predictive_quotient_is_minimum_exact_statistic(self):
        p = mod.predictive_sufficiency_witness()
        self.assertEqual(p["quotient"], (("hA", "hC"), ("hB",)))
        self.assertEqual(p["quotient_classes"], 2)
        self.assertEqual(p["minimum_value_count"], 2)
        self.assertEqual(p["minimum_partitions"], (p["quotient"],))

    def test_incomplete_psr_coordinate_merges_distinct_classes(self):
        p = mod.predictive_sufficiency_witness()
        self.assertFalse(p["short_tests_separate"])
        self.assertEqual(p["short_partition"], (("hA", "hB", "hC"),))
        self.assertTrue(p["full_tests_separate"])

    def test_predictive_sufficiency_hostile_rejects_bad_merge(self):
        laws = {"x": (1, 0), "y": (0, 1)}
        self.assertFalse(mod.is_predictive_sufficient({"x": 0, "y": 0}, laws))
        self.assertTrue(mod.is_predictive_sufficient({"x": 0, "y": 1}, laws))

    def test_classical_and_predictive_sufficiency_are_incomparable(self):
        s = mod.sufficiency_incomparability_witness()
        self.assertTrue(s["A_predictive_sufficient"])
        self.assertFalse(s["A_parameter_sufficient"])
        self.assertTrue(s["B_parameter_sufficient"])
        self.assertFalse(s["B_predictive_sufficient"])

    def test_claim_ceiling_and_forbidden_promotions_are_narrow(self):
        r = mod.build_receipt()
        self.assertEqual(r["claim_ceiling"], "GMI_PARENT_EQUIVALENCE_BOUNDARIES_AT_REGISTERED_FINITE_SCOPE")
        self.assertIn("COMPLETE_GMI", r["forbidden_promotions"])
        self.assertIn("UNIVERSAL_STOCHASTIC_MINIMALITY", r["forbidden_promotions"])

    def test_parent_map_has_all_registered_parents(self):
        p = mod.build_receipt()["parent_map"]
        self.assertEqual(set(p), {"myhill_nerode", "deterministic_bisimulation", "nondeterministic_trace_vs_bisimulation", "classical_parameter_sufficiency", "predictive_state_representation"})

    def test_no_floats_in_receipt(self):
        def walk(x):
            if isinstance(x, float): self.fail("float found in exact receipt")
            if isinstance(x, dict):
                for v in x.values(): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(mod.build_receipt())


if __name__ == "__main__":
    unittest.main()
