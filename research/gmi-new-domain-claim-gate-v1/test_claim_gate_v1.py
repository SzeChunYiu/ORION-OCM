#!/usr/bin/env python3
"""Unittest suite for GMI New-Domain Claim Gate v1 (#602 J4+K).

Python 3.8 safe. No network.
Run: python3 -I -B research/gmi-new-domain-claim-gate-v1/test_claim_gate_v1.py -v
"""

from __future__ import print_function

import os
import sys
import unittest
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claim_gate_v1 import (
    CLAIM_CEILING,
    DOMAIN_IDS,
    DOMAIN_NAMES,
    GATE_BOXES,
    NOVELTY_ALLOWED,
    NOVELTY_REFUSAL,
    discover_siblings,
    evaluate_dossier,
    load_fixture,
    run_report,
)


class TestBoxInventory(unittest.TestCase):
    def test_twenty_five_boxes(self):
        self.assertEqual(len(GATE_BOXES), 25)
        ids = [row[0] for row in GATE_BOXES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(1 for i in ids if i.startswith("J4.")), 11)
        self.assertEqual(sum(1 for i in ids if i.startswith("K.")), 14)


class TestRegistryAlignment(unittest.TestCase):
    def test_domain_ids_match_j2(self):
        self.assertEqual(len(DOMAIN_IDS), 8)
        self.assertEqual(DOMAIN_NAMES["D1"], "coefficient_function_field")
        self.assertEqual(DOMAIN_NAMES["D8"], "morphogenetic_self_rewriting")

    def test_sibling_discovery_shapes(self):
        siblings = discover_siblings()
        self.assertEqual(list(siblings["domain_ids"]), list(DOMAIN_IDS))
        self.assertIn("registry_present", siblings)
        self.assertIn("attack_present", siblings)


class TestPositiveTwin(unittest.TestCase):
    def setUp(self):
        self.dossier = load_fixture("positive_residual_twin.json")
        self.report = evaluate_dossier(self.dossier)

    def test_gate_passes(self):
        self.assertTrue(self.report["structural_pass"])
        self.assertTrue(self.report["residual_survives"])
        self.assertTrue(self.report["gate_pass"])

    def test_all_predicates_pass(self):
        failed = [r["id"] for r in self.report["predicates"] if not r["pass"]]
        self.assertEqual(failed, [])

    def test_novelty_permitted(self):
        self.assertEqual(self.report["novelty_disposition"], NOVELTY_ALLOWED)

    def test_claim_ceiling(self):
        self.assertEqual(self.report["claim_ceiling"], CLAIM_CEILING)


class TestNegativeTwin(unittest.TestCase):
    def setUp(self):
        self.dossier = load_fixture("negative_absorbed_twin.json")
        self.report = evaluate_dossier(self.dossier)

    def test_gate_fails(self):
        self.assertFalse(self.report["gate_pass"])
        self.assertFalse(self.report["residual_survives"])

    def test_novelty_refused(self):
        self.assertEqual(self.report["novelty_disposition"], NOVELTY_REFUSAL)

    def test_has_structural_failures(self):
        failed = [r["id"] for r in self.report["predicates"] if not r["pass"]]
        self.assertIn("J4.1", failed)
        self.assertIn("J4.2", failed)
        self.assertIn("J4.3", failed)
        self.assertIn("J4.11", failed)

    def test_asserted_novelty_blocked(self):
        """Even if wording is present, disposition must refuse."""
        novelty_row = [r for r in self.report["predicates"] if r["id"] == "K.14"][0]
        self.assertEqual(novelty_row.get("novelty"), NOVELTY_REFUSAL)


class TestFailClosedMutations(unittest.TestCase):
    def test_missing_reduction_target_fails(self):
        dossier = load_fixture("positive_residual_twin.json")
        dossier["reduction_attempts"] = dossier["reduction_attempts"][:-1]
        report = evaluate_dossier(dossier)
        self.assertFalse(report["gate_pass"])
        failed = [r["id"] for r in report["predicates"] if not r["pass"]]
        self.assertIn("J4.3", failed)

    def test_open_parent_fails(self):
        dossier = load_fixture("positive_residual_twin.json")
        dossier["parent_review"]["attempts"][-1]["status"] = "OPEN"
        dossier["parent_review"]["verdict"] = "CANNOT_IDENTIFY"
        report = evaluate_dossier(dossier)
        self.assertFalse(report["gate_pass"])
        failed = [r["id"] for r in report["predicates"] if not r["pass"]]
        self.assertIn("J4.11", failed)

    def test_pre_search_phenotype_fails(self):
        dossier = load_fixture("positive_residual_twin.json")
        dossier["phenotype_classification"]["classified_after_search"] = False
        dossier["phenotype_classification"]["pre_search_label_absent"] = False
        report = evaluate_dossier(dossier)
        failed = [r["id"] for r in report["predicates"] if not r["pass"]]
        self.assertIn("K.6", failed)
        self.assertEqual(report["novelty_disposition"], NOVELTY_REFUSAL)

    def test_e3_burden_rejected(self):
        dossier = load_fixture("positive_residual_twin.json")
        dossier["burden_separation"]["burden_class"] = "E3_APPROXIMATE_OR_EMPIRICAL"
        report = evaluate_dossier(dossier)
        failed = [r["id"] for r in report["predicates"] if not r["pass"]]
        self.assertIn("J4.4", failed)

    def test_novelty_without_ceiling_refused(self):
        dossier = load_fixture("positive_residual_twin.json")
        dossier["novelty_claim"]["claim_ceiling"] = "OVERCLAIM"
        report = evaluate_dossier(dossier)
        self.assertFalse(report["gate_pass"])
        novelty_row = [r for r in report["predicates"] if r["id"] == "K.14"][0]
        self.assertFalse(novelty_row["pass"])
        self.assertEqual(novelty_row.get("novelty"), NOVELTY_REFUSAL)

    def test_forbidden_macro_in_grammar(self):
        dossier = load_fixture("positive_residual_twin.json")
        dossier["neutral_grammar"]["symbols"] = ["ATTENTION_ROUTE", "LOCAL_ASSIGN"]
        report = evaluate_dossier(dossier)
        failed = [r["id"] for r in report["predicates"] if not r["pass"]]
        self.assertIn("K.4", failed)


class TestReportInvariant(unittest.TestCase):
    def test_run_report_invariants(self):
        report = run_report()
        self.assertTrue(report["invariant"]["positive_must_pass"])
        self.assertTrue(report["invariant"]["negative_must_fail_or_refuse"])
        self.assertTrue(report["invariant"]["box_count_is_25"])
        self.assertTrue(report["positive"]["gate_pass"])
        self.assertFalse(report["negative"]["gate_pass"])
        self.assertEqual(report["negative"]["novelty_disposition"], NOVELTY_REFUSAL)


class TestDeepcopyIsolation(unittest.TestCase):
    def test_evaluate_does_not_mutate_fixture(self):
        dossier = load_fixture("positive_residual_twin.json")
        before = deepcopy(dossier)
        evaluate_dossier(dossier)
        self.assertEqual(dossier, before)


if __name__ == "__main__":
    unittest.main()
