"""Tests for #833 Section Z / Z5.

Runnable as `python3 -I -B test_z5_critical_phenomena_v1.py -v` and
`python3 -I -O -B test_z5_critical_phenomena_v1.py -v`. Assertions are raised as
explicit failures rather than with the `assert` statement so that `-O` does not
silently disable them.
"""
import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import z5_critical_phenomena_v1 as A  # noqa: E402
import independent_scaling_oracle_v1 as B  # noqa: E402


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def load(name):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        raise AssertionError("missing receipt %s; run the executors first" % name)
    with open(p) as fh:
        return json.load(fh)


class TestReceipts(unittest.TestCase):
    def setUp(self):
        self.a = load("RESULT_V1.json")
        self.b = load("ORACLE_RESULT_V1.json")

    def test_verdict_green(self):
        need(self.a["verdict"] == "GREEN", "route A verdict %s" % self.a["verdict"])
        bad = [k for k, v in self.a["gates"].items() if not v]
        need(not bad, "gates failed: %s" % bad)

    def test_universe_agrees(self):
        need(self.a["universe"] == self.b["universe"],
             "universe disagrees:\nA=%s\nB=%s" % (self.a["universe"], self.b["universe"]))
        need(self.a["universe"]["candidates"] == 65552, "universe size")
        need(self.a["universe"]["distinct_sigma"] == 146, "sigma class count")

    def test_stateless_lattice_agrees(self):
        for k in ("stateless_attained_pairs", "stateless_delay_values",
                  "stateless_now_values", "stateful_attained_pair_count",
                  "stateful_contains_zero_zero", "analytic_crossing_mismatches"):
            need(self.a["CP_2"][k] == self.b["CP_2"][k],
                 "CP_2.%s disagrees: %r vs %r" % (k, self.a["CP_2"][k], self.b["CP_2"][k]))
        need(self.a["CP_2"]["stateless_delay_values"] == [8],
             "stateless delay is not uniformly N/2")
        need(self.a["CP_2"]["stateless_now_values"] == [0, 8, 16], "e_now value set")
        need(self.a["CP_2"]["analytic_crossing_mismatches"] == 0, "crossing mismatch")

    def test_near_transition_agrees(self):
        for k in ("tie_violations", "closed_form_value_mismatches",
                  "derivative_jump_values", "critical_width_violations",
                  "boundary_worlds_checked"):
            need(self.a["CP_3"][k] == self.b["CP_3"][k],
                 "CP_3.%s disagrees: %r vs %r" % (k, self.a["CP_3"][k], self.b["CP_3"][k]))
        need(self.a["CP_3"]["derivative_jump_values"] == ["1"],
             "derivative jump is not exactly 1")
        need(self.a["CP_3"]["exact_ties_at_boundary"] == 20, "tie count")

    def test_finite_size_ladder_agrees(self):
        ra = self.a["CP_4"]["ladder"]
        rb = self.b["CP_4"]["ladder"]
        need(len(ra) == len(rb) == 4, "ladder length")
        for x, y in zip(ra, rb):
            for k in ("L", "N_scored_moments", "candidates", "distinct_sigma",
                      "stateless_delay_values", "stateless_delay_is_uniform_half",
                      "lambda_star_drift_violations", "stateful_attained_pair_count"):
                need(x[k] == y[k], "rung L=%s field %s disagrees: %r vs %r"
                     % (x["L"], k, x[k], y[k]))
            need(x["lambda_star_drift_violations"] == 0,
                 "finite-size drift at L=%s" % x["L"])
            need(x["stateless_delay_values"] == [x["N_scored_moments"] // 2],
                 "delay not N/2 at L=%s" % x["L"])

    def test_alphabet_ladder_agrees(self):
        ra = dict([(r["A"], r) for r in self.a["CP_5"]["ladder"]])
        rb = dict([(r["A"], r) for r in self.b["CP_5"]["ladder"]])
        need(sorted(ra) == sorted(rb) == [2, 3, 4], "alphabet ladder")
        for Aa in (2, 3, 4):
            for k in ("min_stateless_delay_fraction", "stateless_min_e_now",
                      "one_register_witness_e_now", "one_register_witness_e_delay",
                      "S4_derived_matches", "S4_naive_matches", "N_scored_moments"):
                need(ra[Aa][k] == rb[Aa][k],
                     "A=%d field %s disagrees: %r vs %r" % (Aa, k, ra[Aa][k], rb[Aa][k]))
            need(Fraction(ra[Aa]["min_stateless_delay_fraction"]) == Fraction(Aa - 1, Aa),
                 "S4-derived fails at A=%d" % Aa)
        need(ra[2]["S4_naive_matches"] is True,
             "S4-naive should hold exactly at A=2 -- that is why it survived until now")
        need(ra[3]["S4_naive_matches"] is False, "S4-naive must fail at A=3")
        need(ra[4]["S4_naive_matches"] is False, "S4-naive must fail at A=4")

    def test_product_form_is_checked_not_assumed(self):
        need(self.a["CP_5"]["product_form_licensed"] is True,
             "the product form eta*p*(1-1/A) is only licensed when the delay "
             "fraction is constant across the stateless family and e_now=0 is "
             "attainable; the receipt says it is not")

    def test_hostiles_moved(self):
        for hid, h in self.a["hostiles"].items():
            need(h["moved"] is True,
                 "hostile %s did not move its quantity: %r" % (hid, h))
        need(self.a["hostiles"]["H1_DOUBLE_BOUNDARY"]["clean"] == 0, "H1 clean case")
        need(self.a["hostiles"]["H1_DOUBLE_BOUNDARY"]["hostile"] == 20,
             "H1 must flag all 20 low-side endpoints")
        for hid in ("H1_DOUBLE_BOUNDARY", "H4_TRUNCATED_UNIVERSE"):
            need(self.a["hostiles"][hid]["clean"] == self.b["hostiles"][hid]["clean"],
                 "hostile %s clean disagrees" % hid)
            need(self.a["hostiles"][hid]["hostile"] == self.b["hostiles"][hid]["hostile"],
                 "hostile %s hostile disagrees" % hid)

    def test_null(self):
        n = self.a["null"]
        need(n["laws_drawn"] == n["seeds"] == 200, "null must draw all 200 laws")
        need(n["full_ladder_survived"] == 0,
             "%d randomized scaling laws survived the full-ladder adjudicator"
             % n["full_ladder_survived"])
        need(n["guard_failures"] == 0, "probe offset was not strictly smaller "
                                       "than a threshold gap")
        need(n["one_register_witness_verified"] is True, "witness not verified")
        need(n["A2_only_blind"] > 0,
             "the A=2-only adjudicator reported zero blindness, which would mean "
             "the blindness measurement itself is inert")
        need(n["A2_only_blind_all_agree_at_A2"] is True,
             "the blind set is not characterized: some blind law disagrees with "
             "the enumerated threshold at A=2")
        need(n["A2_only_blind"] + n["A2_only_caught"] == n["laws_drawn"],
             "blind/caught split does not account for every law")


class TestRoutesAreIndependent(unittest.TestCase):
    def test_oracle_does_not_import_route_a(self):
        src = open(os.path.join(HERE, "independent_scaling_oracle_v1.py")).read()
        for token in ("z5_critical_phenomena_v1", "z12_prediction_scoring",
                      "z15_decisive_falsifiers", "z3_invariance", "z7_impossibility"):
            need(("import %s" % token) not in src,
                 "route B imports %s" % token)

    def test_routes_use_different_constructions(self):
        # Route A materialises sequences; route B propagates path multiplicities.
        a_src = open(os.path.join(HERE, "z5_critical_phenomena_v1.py")).read()
        b_src = open(os.path.join(HERE, "independent_scaling_oracle_v1.py")).read()
        need("itertools.product" in a_src, "route A should enumerate sequences")
        need("itertools" not in b_src, "route B should not enumerate sequences")


class TestLiveRecomputation(unittest.TestCase):
    """Small live checks that do not rely on the receipts at all."""

    def test_stateless_delay_is_uniform_live(self):
        seqs = A.sequences(3)
        vals = set()
        for table in range(16):
            _e0, e1 = A.stateless_errors_L(table, seqs, 3)
            vals.add(e1)
        need(vals == set([8]), "live stateless delay values %s" % sorted(vals))

    def test_routes_agree_on_a_sample_of_machines(self):
        seqs = A.sequences(3)
        checked = 0
        for nxt in range(0, 256, 17):
            for table in range(0, 256, 13):
                ea = A.stateful_errors_L(nxt, table, seqs, 3)
                eb = (B.stateful_counts(nxt, table, 0, 3),
                      B.stateful_counts(nxt, table, 1, 3))
                need(ea == eb, "machine (%d,%d): A=%s B=%s" % (nxt, table, ea, eb))
                checked += 1
        need(checked >= 300, "sample too small: %d" % checked)

    def test_closed_form_A_matches_a_direct_count(self):
        for Aa in (2, 3):
            frac, min_now, N = B.stateless_optimum_A(Aa, 3)
            seqs = A.sequences(3, Aa)
            best, _n, N2, now_vals = A.min_stateless_delay_fraction(Aa, 3)
            need(N == N2, "N mismatch at A=%d" % Aa)
            need(frac == best, "A=%d closed form %s vs enumeration %s"
                 % (Aa, frac, best))
            need(min_now == min(now_vals), "A=%d e_now minimum mismatch" % Aa)

    def test_hostile_scorer_offset_actually_moves(self):
        # H3: scoring t=0 as a delay moment must move e_delay off N/2.
        seqs = A.sequences(3)
        clean = set()
        for table in range(16):
            _e0, e1 = A.stateless_errors_L(table, seqs, 3)
            clean.add(e1)
        offset = set()
        for table in range(16):
            e1 = 0
            for seq in seqs:
                for t in range(0, 3):
                    cur = seq[t]
                    got = (table >> (2 + cur)) & 1
                    want = seq[t - 1] if t >= 1 else 0
                    if got != want:
                        e1 += 1
            offset.add(e1)
        need(offset != clean, "H3 hostile did not move e_delay")


if __name__ == "__main__":
    unittest.main(verbosity=2)
