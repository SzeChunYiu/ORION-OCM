"""Tests for the Z15 decisive falsifiers.

Runnable as `python3 -I -B test_z15_decisive_falsifiers_v1.py -v` and
`python3 -I -O -B test_z15_decisive_falsifiers_v1.py -v`. unittest assertions
only, so -O strips nothing.
"""
import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import z15_decisive_falsifiers_v1 as A          # noqa: E402
import independent_falsifier_oracle_v1 as B     # noqa: E402


_CACHE = {}


def _ctx():
    """Build the expensive artifacts once for the whole module."""
    if not _CACHE:
        _CACHE["a"] = A.build()
        _CACHE["hist"] = B.build_histogram()
        ws, parent = B.worlds()
        _CACHE["ws"] = ws
        _CACHE["parent"] = parent
        _CACHE["b_f4a_clean"] = B.f4a(_CACHE["hist"], ws)
        _CACHE["b_f4a_planted"] = B.f4a(_CACHE["hist"], ws, semantic_break=True)
        ladder = [Fraction(n, d) for n in range(1, 8) for d in range(1, 8)
                  if Fraction(n, d) != 1]
        import random as _r
        caught = 0
        caught_plus = 0
        for seed in range(8000, 8200):
            rr = _r.Random(seed).choice(ladder)
            if B.f1(_CACHE["hist"], ws, mult=rr)[1] > 0:
                caught += 1
            if B.f1(_CACHE["hist"], ws, mult=rr, include_boundary=True)[1] > 0:
                caught_plus += 1
        _CACHE["b_null"] = (caught, caught_plus)
    return _CACHE


class Shared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx = _ctx()
        cls.a = ctx["a"]
        cls.hist = ctx["hist"]
        cls.ws = ctx["ws"]
        cls.parent = ctx["parent"]

    def _f(self, fid):
        for f in self.a["falsifier_checks"]:
            if f["id"] == fid:
                return f
        raise KeyError(fid)


class Verdict(Shared):
    def test_green(self):
        self.assertEqual(self.a["verdict"], "GREEN")
        for name, ok in sorted(self.a["gates"].items()):
            self.assertTrue(ok, "gate %s failed" % name)

    def test_four_falsifiers_registered_within_range(self):
        self.assertEqual(self.a["falsifier_count"], 4)
        self.assertGreaterEqual(self.a["falsifier_count"], 3)
        self.assertLessEqual(self.a["falsifier_count"], 5)


class EveryFalsifierIsReal(Shared):
    def test_each_is_silent_on_clean_data(self):
        for f in self.a["falsifier_checks"]:
            self.assertTrue(f["silent_on_clean"], "%s fired on clean data" % f["id"])

    def test_each_fires_on_its_planted_positive(self):
        for f in self.a["falsifier_checks"]:
            self.assertTrue(f["fires_on_planted"], "%s cannot fire" % f["id"])

    def test_planted_positives_move_the_quantity_they_perturb(self):
        self.assertEqual(self._f("F1")["clean"]["mismatches"], 0)
        self.assertEqual(self._f("F1")["planted"]["mismatches"], 20)
        self.assertEqual(self._f("F1+")["clean"]["mismatches"], 0)
        self.assertEqual(self._f("F1+")["planted"]["mismatches"], 20)
        self.assertEqual(self._f("F2")["clean"]["outside"], 0)
        self.assertEqual(self._f("F2")["planted"]["outside"], 20)
        self.assertEqual(self._f("F3")["clean"]["misses"], 0)
        self.assertEqual(self._f("F3")["planted"]["misses"], 1)
        self.assertEqual(self._f("F4a")["clean"]["changes"], 0)
        self.assertGreater(self._f("F4a")["planted"]["changes"], 0)
        self.assertEqual(self._f("F4b")["clean"]["changes"], 0)
        self.assertEqual(self._f("F4b")["planted"]["changes"], 240)

    def test_f4_distinguishes_irrelevant_from_relevant_transformations(self):
        """The invariance checker is not a constant False."""
        self.assertEqual(self._f("F4a")["clean"]["distinct_multisets"], 1)
        self.assertEqual(self._f("F4a")["planted"]["distinct_multisets"], 200)
        self.assertEqual(self._f("F4b")["clean"]["checks"], 360)
        self.assertEqual(self._f("F4b")["planted"]["checks"], 360)


class F1Blindness(Shared):
    def test_survivors_lie_exactly_inside_the_analytic_blind_interval(self):
        null = self.a["null"]
        self.assertEqual(null["F1_survivors_outside_predicted_blind_interval"], 0)
        self.assertEqual(null["F1_caught_inside_predicted_blind_interval"], 0)
        lo, hi = Fraction(1, 2), Fraction(3, 2)
        for text in null["F1_distinct_survivors"]:
            r = Fraction(text)
            self.assertTrue(lo < r < hi, "survivor %s outside (1/2,3/2)" % text)

    def test_counterexample_is_reproducible(self):
        ce = self.a["F1_boundary_earned_by_counterexample"]
        self.assertEqual(ce["counterexample_r"], "6/7")
        self.assertFalse(ce["F1_endpoint_scope_fires"])
        self.assertTrue(ce["F1PLUS_all_world_scope_fires"])
        self.assertEqual(ce["label"], "EARNED-BY-COUNTEREXAMPLE")

    def test_revival_is_decisive_where_the_frozen_falsifier_was_not(self):
        null = self.a["null"]
        self.assertEqual(null["seeds"], 200)
        self.assertEqual(null["F1_caught"], 143)
        self.assertEqual(null["F1_survived_undetected"], 57)
        self.assertEqual(null["F1PLUS_caught"], 200)
        self.assertEqual(null["F1PLUS_survived_undetected"], 0)


class TwoRoutes(Shared):
    """Clean counts and every verdict must agree exactly.

    The F4a plant is a randomized semantics-permuting corruption implemented
    differently in each route, so only its verdict is contracted, never its
    count. Every other plant is deterministic and its count is contracted too.
    """

    def test_clean_counts_agree(self):
        n1, b1 = B.f1(self.hist, self.ws)
        n2, b2 = B.f1(self.hist, self.ws, include_boundary=True)
        self.assertEqual((n1, b1), (self._f("F1")["clean"]["checked"],
                                    self._f("F1")["clean"]["mismatches"]))
        self.assertEqual((n2, b2), (self._f("F1+")["clean"]["checked"],
                                    self._f("F1+")["clean"]["mismatches"]))
        self.assertEqual(B.f2(self.hist, self.ws),
                         (self._f("F2")["clean"]["checked"], self._f("F2")["clean"]["outside"]))
        self.assertEqual(B.f3(), (self._f("F3")["clean"]["checked"],
                                  self._f("F3")["clean"]["misses"]))
        self.assertEqual(_ctx()["b_f4a_clean"][0], self._f("F4a")["clean"]["changes"])
        self.assertEqual(B.f4b(self.hist, self.ws),
                         (self._f("F4b")["clean"]["checks"], self._f("F4b")["clean"]["changes"]))

    def test_deterministic_planted_counts_agree(self):
        self.assertEqual(B.f1(self.hist, self.ws, mult=Fraction(2))[1],
                         self._f("F1")["planted"]["mismatches"])
        self.assertEqual(B.f1(self.hist, self.ws, mult=Fraction(6, 7), include_boundary=True)[1],
                         self._f("F1+")["planted"]["mismatches"])
        self.assertEqual(B.f2(self.hist, self.ws, narrow=True)[1],
                         self._f("F2")["planted"]["outside"])
        self.assertEqual(B.f3(damage=True)[1], self._f("F3")["planted"]["misses"])
        self.assertEqual(B.f4b(self.hist, self.ws, eta_only=True)[1],
                         self._f("F4b")["planted"]["changes"])

    def test_randomized_plant_agrees_on_verdict_not_count(self):
        changes, multisets = _ctx()["b_f4a_planted"]
        self.assertGreater(changes, 0)
        self.assertTrue(self._f("F4a")["fires_on_planted"])
        self.assertEqual(multisets, 200)

    def test_universe_and_parent_controls_agree(self):
        self.assertEqual(sum(self.hist.values()), 65552)
        self.assertEqual(sum(self.hist.values()), self.a["candidate_census"])
        self.assertEqual(len(self.hist), 146)
        self.assertEqual(len(self.hist), self.a["distinct_risk_summaries"])
        self.assertEqual(self.a["summary_reduction_mismatches"], 0)
        c = self.parent["counts"]
        self.assertEqual(self._f("F1")["planted"]["mismatches"], c["shifted_threshold_failures"])
        self.assertEqual(self._f("F1")["clean"]["checked"], c["endpoint_predictions"])
        self.assertEqual(sum(self.hist.values()), c["raw_candidates"])

    def test_null_agrees_across_routes(self):
        caught, caught_plus = _ctx()["b_null"]
        self.assertEqual(caught, self.a["null"]["F1_caught"])
        self.assertEqual(caught_plus, self.a["null"]["F1PLUS_caught"])


class Registers(Shared):
    def test_every_failed_prediction_entry_resolves(self):
        entries = self.a["failed_prediction_register"]
        self.assertEqual(len(entries), 6)
        for e in entries:
            self.assertTrue(e["exists"], e["id"])
            self.assertEqual(e["anchor_count"], 1, e["id"])
            self.assertEqual(len(e["blob_sha"]), 40, e["id"])

    def test_negative_control_is_labelled_not_as_a_discovery(self):
        by_id = dict((e["id"], e) for e in self.a["failed_prediction_register"])
        self.assertEqual(by_id["FP-SHIFTED-BOUNDARY"]["kind"], "REGISTERED_NEGATIVE_CONTROL")
        self.assertIn("NOT a discovered failure", by_id["FP-SHIFTED-BOUNDARY"]["summary"])

    def test_successes_published_alongside(self):
        entries = self.a["success_register"]
        self.assertEqual(len(entries), 2)
        for e in entries:
            self.assertTrue(e["exists"], e["id"])
            self.assertEqual(e["anchor_count"], 1, e["id"])

    def test_register_checker_fires_on_a_bad_anchor(self):
        bad = A.check_register([{"id": "X", "kind": "T", "path": "gmi-833-theory-baseline-v1/BASELINE_V1.md",
                                 "anchor": "this string does not occur anywhere", "summary": ""}])
        self.assertEqual(bad[0]["anchor_count"], 0)
        self.assertFalse(bad[0]["ok"])

    def test_register_checker_fires_on_a_missing_file(self):
        bad = A.check_register([{"id": "Y", "kind": "T", "path": "no-such-package/NOPE.md",
                                 "anchor": "x", "summary": ""}])
        self.assertFalse(bad[0]["exists"])
        self.assertFalse(bad[0]["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
