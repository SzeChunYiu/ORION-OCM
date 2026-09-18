"""Tests for the Z12 exact prediction-scoring protocol.

Runnable as `python3 -I -B test_z12_prediction_scoring_v1.py -v` and
`python3 -I -O -B test_z12_prediction_scoring_v1.py -v`. unittest assertions are
used throughout, so -O cannot strip a single check.
"""
import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import z12_prediction_scoring_v1 as A            # noqa: E402
import independent_scoring_oracle_v1 as B        # noqa: E402


def fr(x):
    return Fraction(x)


class TwoRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = A.build()
        cls.hist = B.histogram()
        cls.m_raw, cls.worlds, cls.alpha = B.load_m()
        cls.k_rows = B.load_k()

    def test_route_a_green(self):
        self.assertEqual(self.a["verdict"], "GREEN")
        for name, ok in sorted(self.a["gates"].items()):
            self.assertTrue(ok, "gate %s failed" % name)

    def test_route_b_reproduces_parent_controls(self):
        parent = A.load_json(A.P_TRANS)["counts"]
        self.assertEqual(sum(self.hist.values()), 65552)
        self.assertEqual(sum(self.hist.values()), parent["raw_candidates"])
        self.assertEqual(len(self.hist), 146)
        sl_min = min(e1 for (b, e0, e1) in self.hist if b == 0)
        self.assertEqual(Fraction(sl_min, 16), Fraction(1, 2))
        self.assertIn((0, 0, 8), self.hist)   # stateless (err_now=0, err_delay=1/2) witness
        self.assertIn((1, 0, 0), self.hist)   # one-bit zero-risk witness

    def test_route_b_matches_route_a_on_every_score(self):
        b_m = B.scores_from_counts(B.reduce_records(
            [(len(r.A), r.S, r.T) for r in A.load_pop_m()[0]]))
        b_k = B.scores_from_counts(B.reduce_records(
            [(len(r.A), r.S, r.T) for r in A.load_pop_k()[0]]))
        for key in A.SCORE_KEYS:
            self.assertEqual(self.a["POP_M"][key], b_m[key], "POP_M.%s" % key)
            self.assertEqual(self.a["POP_K"][key], b_k[key], "POP_K.%s" % key)

    def test_two_route_block_agrees(self):
        tr = self.a["two_route"]
        self.assertEqual(tr["status"], "COMPARED")
        self.assertEqual(tr["mismatches"], [])
        self.assertEqual(tr["parent_control_mismatches"], [])
        self.assertTrue(tr["agree"])


class Headline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = A.build()

    def test_population_sizes(self):
        self.assertEqual(self.a["POP_M"]["records"], 60)
        self.assertEqual(self.a["POP_K"]["records"], 480)
        self.assertEqual(self.a["POP_K"]["REFUTE_WORLD_excluded_from_mass_scores"], 12)
        self.assertEqual(self.a["POP_K"]["mass_scored_records"], 468)

    def test_coverage_exactly_one(self):
        self.assertEqual(self.a["POP_M"]["COV_1_coverage"], "1/1")
        self.assertEqual(self.a["POP_K"]["COV_1_coverage"], "1/1")

    def test_sharpness_exact(self):
        self.assertEqual(self.a["POP_M"]["SHP_1_mean_set_size"], "4/3")
        self.assertEqual(self.a["POP_K"]["SHP_1_mean_set_size"], "40/13")
        self.assertEqual(self.a["POP_K"]["SHP_1_max_set_size"], 8)

    def test_zero_regret_and_zero_vacuity(self):
        self.assertEqual(self.a["REG_1"]["REG_1_total_regret"], "0/1")
        self.assertEqual(self.a["REG_1"]["REG_1_total_worst_case_regret"], "0/1")
        self.assertEqual(self.a["POP_M"]["VAC_1_vacuous"], 0)
        self.assertEqual(self.a["POP_K"]["VAC_1_vacuous"], 0)

    def test_abstention_is_sound_and_non_trivial(self):
        self.assertEqual(self.a["POP_M"]["ABS_1_unidentifiable"], 20)
        self.assertEqual(self.a["POP_M"]["ABS_1_abstaining"], 20)
        self.assertEqual(self.a["POP_M"]["ABS_1_soundness_violations"], 0)
        self.assertEqual(self.a["POP_K"]["ABS_1_soundness_violations"], 0)
        # non-trivial: the population contains records that must NOT abstain
        self.assertEqual(self.a["POP_M"]["BND_1_types"]["POINT"], 40)

    def test_log_loss_declined_explicitly(self):
        self.assertEqual(self.a["log_loss"],
                         "DECLINED_NO_EXACT_RATIONAL_VALUE__BRIER_SCORED_INSTEAD")


class CalLem(unittest.TestCase):
    """CAL-LEM validated on a planted-clean and a planted-dirty population."""

    def _pop(self, triples):
        return [A.Record("r%d" % i, S, T, alpha, {}) for i, (S, T, alpha) in enumerate(triples)]

    def test_clean_population_has_zero_calibration_error(self):
        alpha = ("a", "b", "c")
        pop = self._pop([(("a", "b"), ("a",), alpha),
                         (("a", "b", "c"), ("b", "c"), alpha),
                         (("c",), ("c",), alpha)])
        s = A.score_population(pop)
        self.assertEqual(s["COV_1_coverage"], "1/1")
        self.assertEqual(s["CAL_1_max_error"], "0/1")

    def test_miscovering_population_has_strictly_positive_error(self):
        alpha = ("a", "b", "c")
        pop = self._pop([(("a", "b"), ("c",), alpha),
                         (("a",), ("a",), alpha)])
        s = A.score_population(pop)
        self.assertNotEqual(s["COV_1_coverage"], "1/1")
        self.assertGreater(fr(s["CAL_1_max_error"]), 0)

    def test_checker_is_not_a_coverage_alias_on_the_bin_table(self):
        """The bin table must localize the failure to the bin that miscovers."""
        alpha = ("a", "b", "c")
        pop = self._pop([(("a", "b"), ("c",), alpha),
                         (("a",), ("a",), alpha)])
        s = A.score_population(pop)
        by_k = dict((row["set_size"], row["calibration_error"]) for row in s["CAL_1_bins"])
        self.assertEqual(by_k[1], "0/1")
        self.assertGreater(fr(by_k[2]), 0)


class Hostiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = A.build()

    def test_every_hostile_can_actually_fire(self):
        for h in self.a["hostiles"]:
            self.assertTrue(h["delta_nonzero"],
                            "hostile %s did not move its quantity" % h["id"])

    def test_every_hostile_is_detected(self):
        for h in self.a["hostiles"]:
            self.assertTrue(h["detected"], "hostile %s not detected" % h["id"])

    def test_no_alarm_on_the_true_population(self):
        for h in self.a["hostiles"]:
            self.assertTrue(h["no_alarm_on_true"],
                            "hostile %s alarms on clean data" % h["id"])

    def test_six_hostiles_present(self):
        ids = sorted(h["id"] for h in self.a["hostiles"])
        self.assertEqual(ids, ["H1_VACUOUS", "H2_WIDENER", "H3_NEVER_ABSTAIN",
                               "H4_MISCALIBRATED", "H5_TRUTH_LEAK", "H6_REGRET_BLIND"])

    def test_widener_delta_is_exactly_one_over_mass_n(self):
        h2 = [h for h in self.a["hostiles"] if h["id"] == "H2_WIDENER"][0]
        self.assertEqual(h2["moves"]["observed_delta"], h2["moves"]["expected_delta"])
        self.assertEqual(h2["moves"]["expected_delta"], "1/468")

    def test_regret_blind_pays_strictly_more(self):
        h6 = [h for h in self.a["hostiles"] if h["id"] == "H6_REGRET_BLIND"][0]
        self.assertEqual(h6["moves"]["REG_1_total_regret"][0], "0/1")
        self.assertGreater(fr(h6["moves"]["REG_1_total_regret"][1]), 0)


class Refusals(unittest.TestCase):
    def test_empty_prediction_with_nonempty_truth_is_refused(self):
        rec = A.Record("bad", (), ("a",), ("a", "b"), {})
        self.assertEqual(A.type_record(rec), "REFUSED")
        self.assertRaises(SystemExit, A.score_population, [rec])

    def test_refute_world_is_admitted_and_covers(self):
        rec = A.Record("rw", (), (), ("a", "b"), {})
        self.assertEqual(A.type_record(rec), "REFUTE_WORLD")
        other = A.Record("ok", ("a",), ("a",), ("a", "b"), {})
        s = A.score_population([rec, other])
        self.assertEqual(s["REFUTE_WORLD_excluded_from_mass_scores"], 1)
        self.assertEqual(s["COV_1_coverage"], "1/1")
        self.assertEqual(s["mass_scored_records"], 1)

    def test_out_of_alphabet_value_is_refused(self):
        rec = A.Record("oob", ("z",), ("a",), ("a", "b"), {})
        self.assertEqual(A.type_record(rec), "REFUSED")


class Provenance(unittest.TestCase):
    def test_every_scored_set_is_derivable_from_its_pinned_blob(self):
        pop_k, admitted, refused = A.load_pop_k()
        first = A.provenance_digests(pop_k)
        again, _adm, _ref = A.load_pop_k()
        second = A.provenance_digests(again)
        self.assertEqual(first, second)
        self.assertEqual(len(refused), 0)
        self.assertGreater(len(admitted), 0)

    def test_pinned_source_hashes_recorded(self):
        a = A.build()
        for key, rec in a["pinned_sources"].items():
            self.assertEqual(len(rec["sha256"]), 64, key)


class Null(unittest.TestCase):
    def test_frozen_predictor_beats_all_two_hundred_randomized_controls(self):
        a = A.build()
        self.assertEqual(a["null"]["seeds"], 200)
        self.assertEqual(a["null"]["matched_or_beat_frozen"], 0)
        self.assertEqual(a["null"]["beaten_by_frozen"], 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
