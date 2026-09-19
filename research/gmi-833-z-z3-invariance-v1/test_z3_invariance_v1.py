"""Tests for #833 Section Z / Z3.

Runnable as `python3 -I -B test_z3_invariance_v1.py -v` and
`python3 -I -O -B test_z3_invariance_v1.py -v`. Failures are raised explicitly
so `-O` cannot disable them.
"""
import json
import os
import random
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import z3_invariance_v1 as A  # noqa: E402
import independent_invariance_oracle_v1 as B  # noqa: E402


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
        self.reg = load("TRANSFORMATION_REGISTRY_V1.json")

    def test_verdict_green(self):
        bad = [k for k, v in self.a["gates"].items() if not v]
        need(not bad, "gates failed: %s" % bad)
        need(self.a["verdict"] == "GREEN", "verdict %s" % self.a["verdict"])

    def test_universe_agrees(self):
        need(self.a["universe"] == self.b["universe"], "universe disagrees")
        need(self.a["universe"]["candidates"] == 65552, "universe size")
        need(self.a["universe"]["distinct_sigma"] == 146, "sigma classes")

    def test_registry_covers_every_row1_category(self):
        need(sorted(self.reg["row1_categories_covered"])
             == sorted(self.reg["row1_categories_required"]),
             "registry misses row-1 categories: %s"
             % sorted(set(self.reg["row1_categories_required"])
                      - set(self.reg["row1_categories_covered"])))
        claimed = [e for e in self.reg["entries"] if e["status"].startswith("CLAIMED")]
        relevant = [e for e in self.reg["entries"] if e["status"] == "DECLARED_RELEVANT"]
        need(len(claimed) >= 6, "fewer than six claimed-irrelevant transformations")
        need(len(relevant) >= 4, "fewer than four declared-relevant transformations")
        for e in self.reg["entries"]:
            need(e["ok"] is True,
                 "registry entry %s failed its requirement (%s)" % (e["id"], e["required"]))
        for e in relevant:
            need(e["observed_alarms"] not in (0, False),
                 "declared-relevant transformation %s moved nothing; a hostile that "
                 "cannot fire tests nothing" % e["id"])

    def test_invariance_group(self):
        inv = self.a["IV_2"]
        need(inv["T1_RENAME"]["alarms"] == 0, "renaming moved a verdict")
        need(inv["T1_RENAME"]["multiset_breaks"] == 0, "renaming moved the sigma multiset")
        need(inv["T1_RENAME"]["instances"] == 200, "fewer than 200 rename instances")
        need(inv["T1_FULL_SCAN_CONTROL"]["mismatches"] == 0,
             "the reduced decision disagrees with a direct scan of the permuted list")
        need(inv["T2_STATE_ENCODING"]["sigma_breaks"] == 0, "state relabeling moved sigma")
        need(inv["T2_STATE_ENCODING"]["exhaustive"] is True,
             "T2 was sampled where the freeze promises the whole universe")
        need(inv["T4_COMPILER"]["exhaustive"] is True,
             "T4 was sampled where the freeze promises the whole universe")
        need(inv["T2_STATE_ENCODING"]["machines_checked"] == 65536, "T2 coverage")
        need(inv["T4_COMPILER"]["machines_checked"] == 65536, "T4 coverage")
        need(inv["T3_IO_CONJUGATION"]["sigma_breaks"] == 0, "conjugation moved sigma")
        need(inv["T3_IO_CONJUGATION"]["is_bijection"] is True,
             "conjugation is not a bijection of the universe")
        need(inv["T4_COMPILER"]["sigma_breaks"] == 0, "composite transform moved sigma")
        need(self.b["IV_2"]["T3_sigma_breaks"] == 0, "route B disagrees on T3")
        need(self.b["IV_2"]["T3_is_bijection"] is True, "route B: T3 not a bijection")

    def test_equivariance_and_dimensionless_reduction(self):
        t5 = self.a["IV_2"]["T5_UNIT"]
        need(t5["equivariance_breaks"] == 0, "unit change is not equivariant")
        need(t5["p_mu_determinism_breaks"] == 0,
             "two worlds with equal (p, lambda/eta) gave different verdicts")
        need(self.b["IV_2"]["T5_equivariance_breaks"] == 0, "route B disagrees on T5")

    def test_row4_branch1_conclusions_survive(self):
        need(self.a["gates"]["row4_branch1_conclusions_survive"] is True,
             "the flagship conclusions do not survive the claimed-irrelevant group")

    def test_row4_branch2_non_invariant_characterized(self):
        iv4 = self.a["IV_4"]
        need(iv4["declared_bits_is_a_semantic_invariant"] is False,
             "no non-invariance was found, so branch 2 has nothing to characterize")
        need(iv4["mixed_convention_flips"] > 0,
             "the mixed convention moved no verdict")
        need(iv4["behaviourally_stateless_declared_stateful"]
             == self.b["IV_4"]["behaviourally_stateless_declared_stateful"],
             "routes disagree on the behavioural census")
        need(iv4["mixed_convention_flips"] == self.b["IV_4"]["mixed_convention_flips"],
             "routes disagree on the mixed-convention flip count")

    def test_syntactic_family_undercounts_and_it_is_recorded(self):
        iv4 = self.a["IV_4"]
        need(iv4["syntactic_dead_table_count"] == 4096,
             "the syntactic dead-table family is not 4096")
        need(iv4["behaviourally_stateless_declared_stateful"] > 4096,
             "the freeze's syntactic count did not undercount; the instrument "
             "hypothesis is then unexercised")
        need(iv4["syntactic_count_undercounts"] is True, "undercount not recorded")
        need(iv4["behaviourally_stateless_not_dead_table"] > 0,
             "no behaviourally stateless machine outside the dead-table family")

    def test_invariant_replacement(self):
        iv5 = self.a["IV_5"]
        need(iv5["effective_convention_is_consistent_with_declared"] is True,
             "the effective-bit convention changes the verdict on clean data")
        need(iv5["effective_convention_invariant_under_dead_padding"] is True,
             "the effective-bit convention is moved by dead padding, so it is not "
             "the invariant replacement")
        need(iv5["declared_convention_moved_by_dead_padding"] > 0,
             "dead padding did not move the declared convention, so the "
             "counterexample is inert")

    def test_grammar_bias_quantified(self):
        a6 = self.a["IV_6a"]
        need(a6["behavioural_classes"] == self.b["IV_6a"]["behavioural_classes"],
             "routes disagree on the behavioural class count")
        need(a6["multiplicity_max"] == self.b["IV_6a"]["multiplicity_max"],
             "routes disagree on the maximum class multiplicity")
        need(a6["multiplicity_min"] == self.b["IV_6a"]["multiplicity_min"],
             "routes disagree on the minimum class multiplicity")
        need(Fraction(a6["multiplicity_ratio_max_over_min"]) > 1,
             "the multiplicity distribution is uniform, so there is no "
             "description-length bias to report")
        radii = self.a["IV_6b"]["radii"]
        need(len(radii) == 9, "expected radii 0..8, got %d" % len(radii))
        need(radii[0]["ball_size"] == 1, "radius 0 ball is not the start word")
        for r in radii:
            need(Fraction(r["ball_fraction_of_universe"]) <= 1, "ball fraction > 1")
        need(radii[-1]["ball_size"] > radii[0]["ball_size"], "ball never grows")
        need(Fraction(radii[1]["declared_bias"]) != 0,
             "the reachability bias is exactly zero at radius 1, which would mean "
             "the mutation graph is unbiased and the row has nothing to quantify")

    def test_hostiles_moved(self):
        for hid, h in self.a["hostiles"].items():
            need(h["moved"] is True,
                 "hostile %s did not move its quantity: %r" % (hid, h))
        need(self.a["hostiles"]["H3_DEAD_PADDING_MIXED"]["hostile"] == 20,
             "the mixed-convention hostile should flip all 20 high-side endpoints")

    def test_null_and_its_revival(self):
        n = self.a["null"]
        need(n["seeds"] == 200, "null seeds")
        need(n["clean_case_alarms"] == 0,
             "the clean case alarmed %d times on genuine renames" % n["clean_case_alarms"])
        need(n["clean_case_multiset_breaks"] == 0, "genuine renames broke the multiset")
        need(n["frozen_detector_detected"] + n["frozen_detector_survived"] == 200,
             "null accounting does not add up")
        need(n["revived_detector_survived"] == 0,
             "%d pseudo-renames survive even the revived detector"
             % n["revived_detector_survived"])
        if n["frozen_detector_survived"]:
            need(n["survivor_characterization_verified"] is True,
                 "the frozen detector's survivors are asserted rather than verified")
            for s in n["survivors"]:
                need(s["holds_the_true_stateless_optimum_pair"] is True,
                     "survivor seed %s does not hold the true stateless optimum pair, "
                     "so the published characterization is wrong" % s["seed"])
                need(s["worlds_where_slot_minimum_equals_true_stateless_minimum"]
                     == s["worlds_total"],
                     "survivor seed %s does not match the true stateless minimum at "
                     "every world" % s["seed"])


class TestRoutesAreIndependent(unittest.TestCase):
    def test_oracle_does_not_import_route_a(self):
        with open(os.path.join(HERE, "independent_invariance_oracle_v1.py")) as fh:
            src = fh.read()
        for token in ("z3_invariance_v1", "z5_critical_phenomena_v1",
                      "z7_impossibility_v1", "z12_prediction_scoring",
                      "z15_decisive_falsifiers"):
            need(("import %s" % token) not in src, "route B imports %s" % token)

    def test_constructions_differ(self):
        with open(os.path.join(HERE, "z3_invariance_v1.py")) as fh:
            a_src = fh.read()
        with open(os.path.join(HERE, "independent_invariance_oracle_v1.py")) as fh:
            b_src = fh.read()
        need("itertools.product" in a_src, "route A should enumerate sequences")
        need("itertools" not in b_src, "route B should not enumerate sequences")
        need("def reachable_states(" in b_src,
             "route B should decide behavioural statelessness by reachability closure")


class TestLiveRecomputation(unittest.TestCase):
    def test_error_counts_agree_on_a_sample(self):
        checked = 0
        for nxt in range(0, 256, 11):
            o0 = B.occupancy(nxt, 0)
            o1 = B.occupancy(nxt, 1)
            for table in range(0, 256, 7):
                sa = A.stateful_sigma(nxt, table)
                sb = (1, B.errors(o0, table, 0), B.errors(o1, table, 1))
                need(sa == sb, "machine (%d,%d): A=%s B=%s" % (nxt, table, sa, sb))
                checked += 1
        need(checked >= 800, "sample too small: %d" % checked)

    def test_behavioural_statelessness_agrees_on_a_sample(self):
        stateless_traces = set([A.stateless_trace(t) for t in range(16)])
        checked = 0
        for nxt in range(0, 256, 5):
            for table in range(0, 256, 3):
                a_flag = A.stateful_trace(nxt, table) in stateless_traces
                b_flag = B.behaviourally_stateless(nxt, table)
                need(a_flag == b_flag,
                     "machine (%d,%d): trace-match=%s reachability-closure=%s"
                     % (nxt, table, a_flag, b_flag))
                checked += 1
        need(checked >= 4000, "sample too small: %d" % checked)

    def test_memoised_scan_equals_a_direct_fraction_scan(self):
        """The full-scan control memoises the objective by (bits, e_now, e_delay).
        Confirm on a sample of worlds that this changes nothing."""
        uni = A.build_universe()
        for (p, eta, lam) in ((Fraction(1, 5), Fraction(1), Fraction(1, 20)),
                              (Fraction(3, 5), Fraction(3), Fraction(1, 2))):
            best_direct = None
            cls_direct = set()
            for r in uni:
                v = eta * ((1 - p) * Fraction(r[4], A.N) + p * Fraction(r[5], A.N)) \
                    + lam * r[1]
                lab = A.STATELESS if r[1] == 0 else A.PERSISTENT
                if best_direct is None or v < best_direct:
                    best_direct = v
                    cls_direct = set([lab])
                elif v == best_direct:
                    cls_direct.add(lab)
            best_memo, cls_memo = A.argmin_classes_scan(uni, p, eta, lam,
                                                        A.DECLARED, A.LABEL_DECLARED)
            need(best_direct == best_memo, "memoised scan value differs")
            need(frozenset(cls_direct) == cls_memo, "memoised scan class set differs")

    def test_dead_padding_is_behaviour_preserving(self):
        for table4 in range(16):
            nxt, t16 = A.dead_pad(table4, 0)
            need(A.stateful_trace(nxt, t16) == A.stateless_trace(table4),
                 "dead padding of table %d changes the behavioural trace" % table4)
            sa = A.stateless_sigma(table4)
            sb = A.stateful_sigma(nxt, t16)
            need(sa[1:] == sb[1:],
                 "dead padding of table %d changes the error counts" % table4)
            need(sa[0] != sb[0],
                 "dead padding of table %d does not change the declared bits, so "
                 "the counterexample is vacuous" % table4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
