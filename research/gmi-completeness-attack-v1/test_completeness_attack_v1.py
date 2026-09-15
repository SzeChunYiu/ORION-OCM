#!/usr/bin/env python3
"""Unittest suite for GMI Completeness Attack v1 (#602 J2).

Python 3.8 safe. Exact Fraction arithmetic. No network.
Run: python3 -I -B research/gmi-completeness-attack-v1/test_completeness_attack_v1.py -v
"""

from __future__ import print_function

import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from completeness_attack_v1 import (
    ATOMIC,
    ATOMIC_DEMANDS,
    BURDEN_CLASS,
    DOMAIN_IDS,
    DOMAIN_NAMES,
    FROZEN_BURDEN,
    HIGHER,
    OBLIGATIONS,
    PAIR,
    atomic_in_budget,
    build_obligation_catalogue,
    coverage_fraction_domain,
    coverage_fraction_union,
    first_unmet_witness,
    higher_order_uncaptured,
    higher_order_uncaptured_obligations,
    meets_alone,
    obligations_unmet_by,
    open_region_fraction,
    pairwise_reduction_fails,
    pairwise_reduction_failures,
    product_meets,
    prove_bounded_completeness_atomic,
    run_completeness_attack,
    union_meets,
)


class TestRegistryAlignment(unittest.TestCase):
    def test_eight_domains(self):
        self.assertEqual(len(DOMAIN_IDS), 8)
        self.assertEqual(set(DOMAIN_NAMES), set(DOMAIN_IDS))
        self.assertEqual(set(FROZEN_BURDEN), set(DOMAIN_IDS))

    def test_correct_domain_names(self):
        self.assertEqual(DOMAIN_NAMES["D1"], "coefficient_function_field")
        self.assertEqual(DOMAIN_NAMES["D3"], "probabilistic_belief")
        self.assertEqual(DOMAIN_NAMES["D5"], "search_deliberative_frontier")
        self.assertEqual(DOMAIN_NAMES["D8"], "morphogenetic_self_rewriting")

    def test_burden_class_e1(self):
        self.assertEqual(BURDEN_CLASS, "E1_CONSTANT_FACTOR")


class TestCatalogue(unittest.TestCase):
    def test_catalogue_nonempty_and_deterministic(self):
        a = build_obligation_catalogue()
        b = build_obligation_catalogue()
        self.assertGreater(len(a), 100)
        self.assertEqual(len(a), len(b))
        self.assertEqual([o.name for o in a], [o.name for o in b])

    def test_atomic_count(self):
        atomics = [o for o in OBLIGATIONS if o.coupling == ATOMIC]
        self.assertEqual(len(atomics), 8 * len(ATOMIC_DEMANDS))

    def test_pair_count(self):
        pairs = [o for o in OBLIGATIONS if o.coupling == PAIR]
        # C(8,2)=28 pairs × 2 (FACTOR + FAIL)
        self.assertEqual(len(pairs), 28 * 2)

    def test_oid_unique(self):
        oids = [o.oid for o in OBLIGATIONS]
        self.assertEqual(len(oids), len(set(oids)))


class TestAloneMeeting(unittest.TestCase):
    def test_each_domain_has_unmet_witness(self):
        """J2 boxes 1–8: search finds obligations no Di meets within burden."""
        for di in DOMAIN_IDS:
            witness = first_unmet_witness(di)
            self.assertIsNotNone(witness, "%s has no unmet witness" % di)
            self.assertFalse(meets_alone(di, witness))
            self.assertEqual(witness.support, frozenset((di,)))
            self.assertGreater(witness.demand_on(di), FROZEN_BURDEN[di])
            unmet = obligations_unmet_by(di)
            self.assertGreater(len(unmet), 0)
            self.assertIn(witness, unmet)

    def test_in_budget_atomic_met(self):
        for di in DOMAIN_IDS:
            for o in OBLIGATIONS:
                if o.coupling != ATOMIC:
                    continue
                if o.support != frozenset((di,)):
                    continue
                expected = o.demand_on(di) <= FROZEN_BURDEN[di]
                self.assertEqual(meets_alone(di, o), expected)

    def test_atomic_over_budget_unmet(self):
        # D8 budget is 4; demand 5..12 must be unmet.
        d8_over = [
            o
            for o in OBLIGATIONS
            if o.name.startswith("ATOMIC_D8_demand_")
            and o.demand_on("D8") > FROZEN_BURDEN["D8"]
        ]
        self.assertGreaterEqual(len(d8_over), 8)
        for o in d8_over:
            self.assertFalse(meets_alone("D8", o))

    def test_pair_never_alone(self):
        for o in OBLIGATIONS:
            if o.coupling != PAIR:
                continue
            for di in DOMAIN_IDS:
                self.assertFalse(meets_alone(di, o))


class TestPairwiseReductionFailures(unittest.TestCase):
    def test_failures_exist(self):
        fails = pairwise_reduction_failures()
        self.assertGreater(len(fails), 0)
        # Exactly the PAIR_FAIL obligations: C(8,2)=28
        self.assertEqual(len(fails), 28)

    def test_failure_predicate(self):
        for di, dj, o in pairwise_reduction_failures():
            self.assertTrue(pairwise_reduction_fails(di, dj, o))
            self.assertFalse(product_meets((di, dj), o))
            self.assertTrue(o.name.startswith("PAIR_FAIL_"))

    def test_factorizable_pairs_succeed_as_product(self):
        factors = [o for o in OBLIGATIONS if o.name.startswith("PAIR_FACTOR_")]
        self.assertEqual(len(factors), 28)
        for o in factors:
            support = tuple(sorted(o.support))
            self.assertTrue(product_meets(support, o))
            di, dj = support
            self.assertFalse(pairwise_reduction_fails(di, dj, o))


class TestHigherOrder(unittest.TestCase):
    def test_higher_uncaptured_exist(self):
        higher = higher_order_uncaptured_obligations()
        self.assertGreaterEqual(len(higher), 8)
        for o in higher:
            self.assertEqual(o.coupling, HIGHER)
            self.assertTrue(higher_order_uncaptured(o))
            self.assertFalse(union_meets(o))

    def test_full_basis_residue_open(self):
        residue = [o for o in OBLIGATIONS if o.name == "HIGHER_OPEN_FULL_BASIS_RESIDUE"]
        self.assertEqual(len(residue), 1)
        self.assertTrue(higher_order_uncaptured(residue[0]))
        self.assertFalse(union_meets(residue[0]))


class TestBoundedCompleteness(unittest.TestCase):
    def test_atomic_in_budget_complete(self):
        ok, cov, n_in, n_met, counter = prove_bounded_completeness_atomic()
        self.assertTrue(ok)
        self.assertEqual(counter, ())
        self.assertEqual(n_in, n_met)
        self.assertEqual(cov, Fraction(1, 1))
        # D1..D7 budget 8 → 8 each; D8 budget 4 → 4; total 7*8+4=60
        self.assertEqual(n_in, 7 * 8 + 4)

    def test_atomic_in_budget_helper(self):
        scoped = atomic_in_budget()
        self.assertEqual(len(scoped), 60)
        for o in scoped:
            di = next(iter(o.support))
            self.assertTrue(meets_alone(di, o))


class TestCoverageFractions(unittest.TestCase):
    def test_fractions_are_exact(self):
        for di in DOMAIN_IDS:
            frac = coverage_fraction_domain(di)
            self.assertIsInstance(frac, Fraction)
            self.assertGreater(frac, Fraction(0))
            self.assertLess(frac, Fraction(1))

    def test_union_strictly_between_zero_and_one(self):
        union = coverage_fraction_union()
        open_f = open_region_fraction()
        self.assertIsInstance(union, Fraction)
        self.assertGreater(union, Fraction(0))
        self.assertLess(union, Fraction(1))
        self.assertEqual(union + open_f, Fraction(1, 1))

    def test_alone_coverage_formula(self):
        # Each Di meets exactly FROZEN_BURDEN[Di] ATOMIC obligations.
        n = len(OBLIGATIONS)
        for di in DOMAIN_IDS:
            expected = Fraction(FROZEN_BURDEN[di], n)
            self.assertEqual(coverage_fraction_domain(di), expected)


class TestEndToEnd(unittest.TestCase):
    def test_run_report_keys(self):
        report = run_completeness_attack()
        for key in (
            "alone_coverage",
            "unmet_counts",
            "unmet_witnesses",
            "pairwise_reduction_failure_count",
            "higher_order_uncaptured_count",
            "bounded_atomic_completeness",
            "union_coverage",
            "open_region_fraction",
            "j2_tick_advice",
        ):
            self.assertIn(key, report)

    def test_all_j2_ticks_honest(self):
        advice = run_completeness_attack()["j2_tick_advice"]
        for key, val in advice.items():
            self.assertTrue(val, "J2 tick advice failed for %s" % key)

    def test_union_equals_atomic_plus_factor_pairs(self):
        # Met set = 60 in-budget ATOMIC + 28 PAIR_FACTOR.
        union = coverage_fraction_union()
        n = len(OBLIGATIONS)
        self.assertEqual(union, Fraction(60 + 28, n))


if __name__ == "__main__":
    unittest.main(verbosity=2)
