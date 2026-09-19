"""Tests for #833 Section Z / Z7.

Runnable as `python3 -I -B test_z7_impossibility_v1.py -v` and
`python3 -I -O -B test_z7_impossibility_v1.py -v`. Failures are raised
explicitly so that `-O` cannot disable them.
"""
import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import z7_impossibility_v1 as A  # noqa: E402
import independent_impossibility_oracle_v1 as B  # noqa: E402


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
        self.reg = load("COUNTEREXAMPLE_REGISTER_V1.json")

    def test_verdict_green(self):
        bad = [k for k, v in self.a["gates"].items() if not v]
        need(not bad, "gates failed: %s" % bad)
        need(self.a["verdict"] == "GREEN", "verdict %s" % self.a["verdict"])

    def test_universe_agrees(self):
        need(self.a["universe"] == self.b["universe"], "universe disagrees")
        need(self.a["universe"]["candidates"] == 65552, "universe size")

    def test_impossibility_is_real_and_resource_dependent(self):
        im = self.a["IM_1"]
        need(im["zero_error_delay_possible_at_bits_0"] is False,
             "zero-error delay is possible at bits=0; the impossibility is false")
        need(im["zero_error_delay_possible_at_bits_1"] is True,
             "the task is not achievable at bits=1, so the impossibility is not "
             "resource-dependent but task-dependent")
        need(im["failure_is_uniform"] is True, "failure is not uniform")
        need(Fraction(im["delay_accuracy_ceiling_at_bits_0"]) == Fraction(1, 2),
             "delay accuracy ceiling at bits=0 is %s" % im["delay_accuracy_ceiling_at_bits_0"])
        need(self.b["IM_1"]["zero_error_delay_possible_at_bits_0"] is False,
             "route B disagrees on the impossibility")

    def test_regions_agree(self):
        ra = self.a["IM_2"]["R1_attainable"]
        rb = self.b["IM_2"]
        need(ra["S0"] == rb["S0"], "S0 disagrees: %r vs %r" % (ra["S0"], rb["S0"]))
        need(ra["S0_size"] == rb["S0_size"] == 3, "S0 size")
        need(ra["S1_size"] == rb["S1_size"], "S1 size disagrees")
        need(ra["S0_pareto_frontier"] == rb["S0_pareto_frontier"], "S0 frontier")
        need(ra["S1_pareto_frontier"] == rb["S1_pareto_frontier"], "S1 frontier")
        need(ra["S0_impossibility_cells"] == 289 - ra["S0_size"], "S0 complement")
        ga = self.a["IM_2"]["R2_cost_grid"]
        gb = self.b["IM_2"]["R2_cost_grid"]
        for k in ("cells", "feasible", "infeasible", "infeasible_by_budget"):
            need(ga[k] == gb[k], "grid field %s disagrees: %r vs %r" % (k, ga[k], gb[k]))
        need(ga["cells"] == ga["feasible"] + ga["infeasible"], "grid not partitioned")
        need(ga["infeasible"] > 0, "the impossibility region is empty, so the grid "
                                   "tests nothing")

    def test_qualitative_predictions_agree(self):
        q = self.a["IM_3"]
        need(q["Q1"]["verdict"] == "CONFIRMED", "Q1 %s" % q["Q1"]["verdict"])
        need(q["Q2"]["verdict"] == "CONFIRMED", "Q2 %s" % q["Q2"]["verdict"])
        need(q["Q4"]["verdict"] == "REFUTED",
             "the [NAIVE] scarcity hypothesis was not refuted; the counterexample "
             "machinery of row 6 is then untested")
        need(self.b["IM_3"]["Q4_refuted"] is True, "route B disagrees on Q4")
        need(self.b["IM_3"]["modal_pair"] == [8, 8] or q["Q3"]["verdict"] == "REFUTED",
             "routes disagree on the modal failure profile")
        need(q["Q2"]["evidence"].endswith("[0, 8, 16]"), "e_now value set changed")

    def test_ceilings_valid_and_tight(self):
        im4 = self.a["IM_4"]
        need(len(im4["forbidding_bounds"]) >= 3,
             "fewer than three genuine forbidding ceilings: %s" % im4["forbidding_bounds"])
        for cid in im4["forbidding_bounds"]:
            c = im4["ceilings"][cid]
            need(c["valid"] is True, "%s is not valid" % cid)
            need(c["tight"] is True,
                 "%s is valid but slack; a ceiling that cannot be approached "
                 "tests nothing" % cid)
        need(im4["ceilings"]["C1"]["attained_min"] == self.b["IM_4"]["C1_attained_min"],
             "C1 minimum disagrees")
        need(im4["ceilings"]["C4"]["K4"] == self.b["IM_4"]["C4_K4"], "K4 disagrees")
        need(im4["ceilings"]["C5"]["K5"] == self.b["IM_4"]["C5_K5"], "K5 disagrees")
        need(self.b["IM_4"]["C6_violations"] == 0, "route B finds C6 violations")

    def test_vacuous_bounds_are_flagged_and_not_counted(self):
        im4 = self.a["IM_4"]
        need(im4["vacuity_check_recall"] is True,
             "the vacuity check does not fire on a bound at the range boundary")
        need(im4["vacuity_check_no_alarm"] is True,
             "the vacuity check fires on a genuine forbidding bound")
        need(im4["ceilings"]["C4"]["kind"] == "NON_BINDING",
             "C4 claims min(e_now, e_delay) <= 16 over quantities that lie in [0,16] "
             "by construction; it cannot be violated and must not be counted")
        need(im4["ceilings"]["C5"]["kind"] == "MEASURED_IDENTITY",
             "C5's right-hand side is defined as the measured quantity")
        for cid in ("C3", "C4", "C5"):
            need(cid in im4["not_counted_as_ceilings"],
                 "%s is still counted as a ceiling" % cid)
        for cid in ("C1", "C2", "C6"):
            need(cid in im4["forbidding_bounds"], "%s lost its forbidding status" % cid)
        # the check must be exercised live, not merely read from the receipt
        need(A.bound_kind("upper", 16, 0, 16) == "NON_BINDING", "live recall (upper)")
        need(A.bound_kind("lower", 0, 0, 16) == "NON_BINDING", "live recall (lower)")
        need(A.bound_kind("upper", 15, 0, 16) == "FORBIDDING_BOUND", "live no-alarm (upper)")
        need(A.bound_kind("lower", 8, 0, 16) == "FORBIDDING_BOUND", "live no-alarm (lower)")

    def test_families_agree_and_cover(self):
        fa = self.a["IM_5"]["families"]
        fb = self.b["IM_5"]
        need(sorted(fa) == sorted(fb), "family sets differ")
        for name in sorted(fa):
            for k in ("size", "min_e_now", "min_e_delay", "attained_pair_count",
                      "pareto_frontier"):
                need(fa[name][k] == fb[name][k],
                     "family %s field %s disagrees: %r vs %r"
                     % (name, k, fa[name][k], fb[name][k]))
        need(fa["F_STATELESS"]["size"] == 16, "stateless family size")
        need(fa["F_DEAD_TABLE"]["size"] == 4096, "dead-table family size")
        need(fa["F_MOORE"]["size"] + fa["F_MEALY_PURE"]["size"] == 65536,
             "Moore/Mealy split does not cover the stateful half")

    def test_structural_family_impossibility(self):
        st = self.a["IM_5_structural"]
        need(st["separated"] is True,
             "the Moore family shows no structural impossibility, so the "
             "named-family test is inert")
        need(st["F_MOORE_min_e_now"] > st["F_MEALY_PURE_min_e_now"],
             "Moore does not separate from Mealy on the copy channel")

    def test_counterexample_register(self):
        need(self.reg["refuted_hypotheses"] >= 1,
             "the counterexample register is empty; row 6 has nothing to record")
        for e in self.reg["entries"]:
            need(e["witness"] is not None, "register entry %s has no witness" % e["hypothesis"])
            need(e["witness_violates_hypothesis"] is True,
                 "register witness for %s does not violate its hypothesis"
                 % e["hypothesis"])
            need(e["repair"], "register entry %s has no repair" % e["hypothesis"])
        # the witness must be re-verifiable from scratch, not merely asserted
        for e in self.reg["entries"]:
            if e["hypothesis"] != "Q4":
                continue
            w = e["witness"]
            e0, e1 = A.stateful_errors(w["nxt"], w["table"])
            need((e0, e1) == (w["e_now"], w["e_delay"]),
                 "route A rescoring of the Q4 witness gives (%d,%d)" % (e0, e1))
            occ0 = B.occupancy(w["nxt"], 0)
            occ1 = B.occupancy(w["nxt"], 1)
            b0 = B.score(occ0, w["table"], 0)
            b1 = B.score(occ1, w["table"], 1)
            need((b0, b1) == (w["e_now"], w["e_delay"]),
                 "route B rescoring of the Q4 witness gives (%d,%d)" % (b0, b1))
            need(b1 == 0 and b0 == 16,
                 "the Q4 witness does not actually realise e_delay=0 with e_now=16")

    def test_hostiles_moved(self):
        for hid, h in self.a["hostiles"].items():
            need(h["moved"] is True,
                 "hostile %s did not move its quantity: %r" % (hid, h))
        need(self.a["hostiles"]["H1_WRONG_CEILING"]["hostile"] == 16,
             "the wrong ceiling must be violated by all 16 stateless candidates")
        need(self.a["hostiles"]["H2_VACUOUS_CEILING"]["hostile"]
             == [False, "NON_BINDING"],
             "the vacuous lower ceiling was reported tight or binding: %r"
             % (self.a["hostiles"]["H2_VACUOUS_CEILING"]["hostile"],))
        need(self.a["hostiles"]["H6_VACUOUS_UPPER_CEILING"]["hostile"] == "NON_BINDING",
             "an upper bound at the range maximum was not flagged non-binding")
        need(self.a["hostiles"]["H6_VACUOUS_UPPER_CEILING"]["clean"] == "FORBIDDING_BOUND",
             "the upper-bound no-alarm case was flagged")

    def test_null(self):
        n = self.a["null"]
        need(n["witness_soundness_complete"] is True,
             "%d of %d false claims had no verified counterexample"
             % (n["witness_required"] - n["witness_supplied"], n["witness_required"]))
        need(n["witness_required"] > 0, "the null produced no false claims at all")
        need(n["frozen_ceilings_tight"] == n["frozen_ceilings_checked"],
             "not every frozen forbidding ceiling is tight")
        need(n["frozen_ceilings_checked"] >= 3, "fewer than three forbidding ceilings")
        need(n["random_true_and_tight"] * 10 < n["seeds"],
             "random impossibility claims are as tight as the frozen ones "
             "(%d/%d), so tightness does not discriminate"
             % (n["random_true_and_tight"], n["seeds"]))


class TestRoutesAreIndependent(unittest.TestCase):
    def test_oracle_does_not_import_route_a(self):
        with open(os.path.join(HERE, "independent_impossibility_oracle_v1.py")) as fh:
            src = fh.read()
        for token in ("z7_impossibility_v1", "z5_critical_phenomena_v1",
                      "z3_invariance_v1", "z12_prediction_scoring",
                      "z15_decisive_falsifiers"):
            need(("import %s" % token) not in src, "route B imports %s" % token)

    def test_constructions_differ(self):
        with open(os.path.join(HERE, "z7_impossibility_v1.py")) as fh:
            a_src = fh.read()
        with open(os.path.join(HERE, "independent_impossibility_oracle_v1.py")) as fh:
            b_src = fh.read()
        need("itertools.product" in a_src, "route A should enumerate sequences")
        need("itertools" not in b_src, "route B should not enumerate sequences")
        need("def occupancy(" in b_src, "route B should factorise via occupancy")


class TestLiveRecomputation(unittest.TestCase):
    def test_routes_agree_on_a_sample(self):
        checked = 0
        for nxt in range(0, 256, 11):
            occ0 = B.occupancy(nxt, 0)
            occ1 = B.occupancy(nxt, 1)
            for table in range(0, 256, 7):
                ea = A.stateful_errors(nxt, table)
                eb = (B.score(occ0, table, 0), B.score(occ1, table, 1))
                need(ea == eb, "machine (%d,%d): A=%s B=%s" % (nxt, table, ea, eb))
                checked += 1
        need(checked >= 800, "sample too small: %d" % checked)

    def test_reduced_grid_scan_matches_a_direct_scan(self):
        """The grid scans 146 distinct triples instead of 65552 candidates.
        Confirm on a sample of cells that this reduction changes nothing."""
        uni = A.build_universe()
        st0 = [r for r in uni if r[0] == 0]
        triples = sorted(set([(r[0], r[3], r[4]) for r in uni]))
        cells = 0
        for ps in ("1/5", "3/5"):
            p = Fraction(ps)
            for ls in ("1/20", "1/2"):
                lam = Fraction(ls)
                for an in (0, 4, 8, 16):
                    for ad in (0, 4, 8, 16):
                        C = Fraction(1, 5)
                        direct = any(r[3] <= an and r[4] <= ad and
                                     A.objective(r[0], r[3], r[4], p, Fraction(2), lam) <= C
                                     for r in uni)
                        reduced = any(t[1] <= an and t[2] <= ad and
                                      A.objective(t[0], t[1], t[2], p, Fraction(2), lam) <= C
                                      for t in triples)
                        need(direct == reduced,
                             "reduction changed cell (p=%s,lam=%s,an=%d,ad=%d)"
                             % (ps, ls, an, ad))
                        cells += 1
        need(cells == 64, "expected 64 sampled cells, got %d" % cells)
        need(len(st0) == 16, "stateless count")


if __name__ == "__main__":
    unittest.main(verbosity=2)
