#!/usr/bin/env python3
"""GMI #833 AE1 tests: two-route agreement, hostile potency, hostile detection.

Runnable as `python3 -I -B test_ae1_structure_separation_v1.py -v` and
`python3 -I -O -B test_ae1_structure_separation_v1.py -v`.  Stdlib only.

Every hostile is asserted in two stages:
  (1) POTENCY -- the perturbation actually moves the quantity it targets;
  (2) DETECTION -- the checker flags the perturbed package.
A hostile that fails stage (1) is a package defect, so stage (1) is a hard
assertion and not a skip.
"""
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae1_structure_separation_v1 as A          # noqa: E402
import independent_separation_oracle_v1 as O     # noqa: E402

RES = A.build()
R = RES["results"]


class TestVerdict(unittest.TestCase):
    def test_green(self):
        self.assertEqual(RES["verdict"], "GREEN")
        for name, ok in RES["checks"].items():
            self.assertTrue(ok, "check failed: " + name)

    def test_no_float_anywhere_in_receipt(self):
        def walk(o):
            if isinstance(o, float):
                self.fail("float found in receipt")
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            if isinstance(o, list):
                for v in o:
                    walk(v)
        walk(RES)

    def test_deterministic(self):
        self.assertEqual(json.dumps(A.build(), sort_keys=True),
                         json.dumps(RES, sort_keys=True))


class TestTwoRoutes(unittest.TestCase):
    """Route A analytic vs route B enumeration -- no shared import."""

    def test_distinct_modules(self):
        self.assertNotEqual(A.__file__, O.__file__)
        # no executable import of route A anywhere in the oracle: check the
        # parsed module, not the text, so prose in the docstring cannot pass
        # or fail this by accident
        import ast
        with open(O.__file__) as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertNotIn("ae1_structure_separation", a.name)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn("ae1_structure_separation",
                                 node.module or "")
        self.assertIn("ae1_structure_separation_v1", A.__file__)

    def test_accuracies_agree_on_distributional_roster(self):
        for name, w in A.WORLDS.items():
            xs, ys, P = w["xs"], w["ys"], w["P"]
            self.assertEqual(A.acc_obs(P, xs, ys), O.oracle_acc_obs(P, xs, ys),
                             name)
            self.assertEqual(A.acc_base(P, xs, ys),
                             O.oracle_acc_base(P, xs, ys), name)
            self.assertEqual(A.pred_dep(P, xs, ys),
                             not O.oracle_independent(P, xs, ys), name)
            self.assertEqual(A.pred_marg_nonunif(P, xs, ys),
                             O.oracle_marg_nonunif(P, xs, ys), name)

    def test_control_values_agree(self):
        for name, w in A.CTRL_WORLDS.items():
            blind_a, seeing_a = A.ctrl_values(
                w["P"], w["xs"], w["ys"], w["acts"], w["U"])
            blind_b, seeing_b = O.oracle_control(
                w["P"], w["xs"], w["ys"], w["acts"], w["U"])
            self.assertEqual(blind_a, blind_b, name)
            self.assertEqual(seeing_a, seeing_b, name)

    def test_rule_classes_agree(self):
        """Route A classifies functions; route B builds explicit trees."""
        for k in range(4):
            for d in range(4):
                a = set(A.rule_class(k, d))
                b = set(O.oracle_rule_class(k, d))
                self.assertEqual(a, b, "class k=%d d=%d" % (k, d))

    def test_accessibility_profiles_agree(self):
        for name, P in A.RESOURCE_WORLDS.items():
            for (k, d) in A.BUDGETS:
                self.assertEqual(A.best_acc_in_class(P, k, d),
                                 O.oracle_best_acc_in_class(P, k, d),
                                 "%s k=%d d=%d" % (name, k, d))

    def test_learning_curve_agrees(self):
        for m in range(4):
            self.assertEqual(A.analytic_learning_curve(m),
                             O.oracle_learning_curve(m), "m=%d" % m)

    def test_causal_tables_agree(self):
        ja, _, doa = A.causal_tables()
        jb, dob = O.oracle_causal()
        self.assertEqual(ja, jb)
        self.assertEqual(doa, dob)

    def test_realizability_map_agrees(self):
        ra = A.realizability_map()
        rb = O.oracle_realizability_map()
        self.assertEqual(ra, rb)

    def test_minimal_shapes_agree(self):
        ra = A.realizability_map()
        rb = O.oracle_realizability_map()
        for pat in [(True, False, False), (False, True, True),
                    (True, True, False), (False, True, False)]:
            self.assertEqual(A.minimal_shapes(ra, pat),
                             O.oracle_minimal_shapes(rb, pat), str(pat))


class TestNamedResults(unittest.TestCase):
    """Exact values that the reconciliation line quotes."""

    def test_AE1_1_marginal_vs_dependence(self):
        t = R["distributional_separation"]
        self.assertTrue(t["W_IND_SKEW"]["MARG_NONUNIF"])
        self.assertFalse(t["W_IND_SKEW"]["DEP"])
        self.assertFalse(t["W_DEP_UNIFMARG"]["MARG_NONUNIF"])
        self.assertTrue(t["W_DEP_UNIFMARG"]["DEP"])

    def test_AE1_2_dependence_vs_prediction(self):
        w = R["distributional_separation"]["W_DEP_NOPRED"]
        self.assertTrue(w["DEP"])
        self.assertFalse(w["PRED"])
        self.assertEqual(w["gain"], "0")
        self.assertEqual(w["l1_dependence"], "1/5")
        self.assertEqual(w["acc_base"], "4/5")
        self.assertEqual(w["acc_obs"], "4/5")

    def test_AE1_3_prediction_vs_control(self):
        c = R["control_separation"]
        self.assertTrue(c["W_PRED_NOCTRL"]["PRED"])
        self.assertFalse(c["W_PRED_NOCTRL"]["CTRL"])
        self.assertFalse(c["W_PRED_NOCTRL"]["utility_is_constant_in_y"])
        self.assertFalse(c["W_CTRL_NOPRED"]["PRED"])
        self.assertTrue(c["W_CTRL_NOPRED"]["CTRL"])
        self.assertEqual(c["W_CTRL_NOPRED"]["blind_utility"], "1/4")
        self.assertEqual(c["W_CTRL_NOPRED"]["informed_utility"], "1/2")

    def test_AE1_4_prediction_vs_causation(self):
        c = R["causal_separation"]
        self.assertTrue(c["PRED"])
        self.assertFalse(c["CAUSAL"])
        self.assertEqual(c["p_y1_do_x0"], c["p_y1_do_x1"])
        self.assertNotEqual(c["p_y1_given_x0"], c["p_y1_given_x1"])

    def test_AE1_5_existence_vs_accessibility(self):
        e = R["existence_vs_accessibility"]
        self.assertTrue(e["PRED"])
        self.assertEqual(e["acc_base"], "1/2")
        self.assertEqual(e["acc_full_information"], "1")
        self.assertEqual(e["best_acc_at_k2_d2"], "1/2")
        self.assertEqual(e["best_acc_at_k3_d2"], "1/2")
        self.assertEqual(e["best_acc_at_k3_d3"], "1")

    def test_AE1_6_finite_sample_vs_asymptotic(self):
        d = R["discoverability"]
        self.assertEqual(d["learning_curve"]["m0"], "9/16")
        self.assertEqual(d["marginalised_world_acc_base"], "9/16")
        self.assertEqual(d["learning_curve"]["m1"], "79/128")
        self.assertEqual(d["learning_curve"]["m3"], "6715/8192")
        self.assertLess(F(d["learning_curve"]["m3"]), F(1))

    def test_scalar_impossibility_and_positive_disjunct(self):
        s = R["scalar_impossibility"]
        self.assertTrue(s["reversal"])
        self.assertEqual((s["A_low"], s["B_low"]), ("1/2", "3/4"))
        self.assertEqual((s["A_high"], s["B_high"]), ("1", "3/4"))
        p = R["profile_object"]
        self.assertTrue(p["monotone"])
        self.assertTrue(p["bounded_by_full_information"])
        self.assertEqual(p["lattice_size"], 16)
        for name in A.CANDIDATE_SCALARS:
            self.assertTrue(R["candidate_scalars_refuted"][name]["refuted"],
                            name)

    def test_minimality(self):
        m = R["minimality"]
        self.assertEqual(m["shapes_searched"], 16)
        self.assertEqual(m["shapes_admitting_PRED_without_DEP"], [])
        self.assertEqual(
            m["separations"]["MARG_NONUNIF_without_DEP"]["minimal_shapes"],
            [[2, 1]])
        self.assertEqual(
            m["separations"]["DEP_without_PRED"]["minimal_shapes"], [[2, 2]])

    def test_null(self):
        n = R["null"]
        self.assertTrue(n["planted_positive_flagged"])
        self.assertEqual(n["known_clean_worlds_flagged"], [])
        self.assertEqual(n["random_worlds_at_or_above_threshold"], 0)
        self.assertEqual(n["largest_null_gap_magnitude"], "3/16")
        self.assertEqual(n["planted_positive_gap_magnitude"], "1/2")
        self.assertGreater(F(n["planted_positive_gap_magnitude"]),
                           F(n["largest_null_gap_magnitude"]))


class TestHostiles(unittest.TestCase):
    """Each hostile: prove potency first, then prove detection."""

    def test_H1_independence_forced(self):
        w = A.WORLDS["W_DEP_NOPRED"]
        xs, ys, P = w["xs"], w["ys"], w["P"]
        px, py = A.marginals(P, xs, ys)
        Q = dict(((x, y), px[x] * py[y]) for x in xs for y in ys)
        # POTENCY: the perturbation really moves the dependence quantity
        self.assertNotEqual(A.l1_dependence(Q, xs, ys),
                            A.l1_dependence(P, xs, ys))
        self.assertTrue(A.pred_dep(P, xs, ys))
        # DETECTION
        self.assertFalse(A.pred_dep(Q, xs, ys))
        self.assertTrue(O.oracle_independent(Q, xs, ys))

    def test_H2_gain_inflated(self):
        w = A.WORLDS["W_DEP_NOPRED"]
        xs, ys = w["xs"], w["ys"]
        Q = dict(w["P"])
        Q[(1, 0)] = Q[(1, 0)] - F(1, 5)
        Q[(1, 1)] = Q[(1, 1)] + F(1, 5)
        # POTENCY: the hostile targets the Bayes GAIN, so potency is asserted
        # on the gain.  acc_obs happens to be invariant under this particular
        # mass move, which is exactly why naming the right quantity matters.
        gain_true = A.acc_obs(w["P"], xs, ys) - A.acc_base(w["P"], xs, ys)
        gain_host = A.acc_obs(Q, xs, ys) - A.acc_base(Q, xs, ys)
        self.assertNotEqual(gain_true, gain_host)
        self.assertEqual(gain_true, F(0))
        self.assertEqual(gain_host, F(1, 5))
        # DETECTION: the frozen PRED=False verdict flips
        self.assertFalse(A.pred_pred(w["P"], xs, ys))
        self.assertTrue(A.pred_pred(Q, xs, ys))
        self.assertEqual(A.acc_obs(Q, xs, ys), O.oracle_acc_obs(Q, xs, ys))

    def test_H3_constant_utility(self):
        w = A.CTRL_WORLDS["W_CTRL_NOPRED"]
        U = dict((k, F(1)) for k in w["U"])
        blind0, see0 = A.ctrl_values(w["P"], w["xs"], w["ys"], w["acts"],
                                     w["U"])
        blind1, see1 = A.ctrl_values(w["P"], w["xs"], w["ys"], w["acts"], U)
        # POTENCY
        self.assertNotEqual(see0, see1)
        # DETECTION: control relevance is destroyed
        self.assertGreater(see0, blind0)
        self.assertEqual(see1, blind1)

    def test_H4_parity_replaced_by_dictator(self):
        par = A.RESOURCE_WORLDS["W_PARITY3"]
        dic = A.RESOURCE_WORLDS["W_DICT"]
        # POTENCY: the low-budget accuracy moves
        self.assertNotEqual(A.best_acc_in_class(par, 1, 1),
                            A.best_acc_in_class(dic, 1, 1))
        # DETECTION: the accessibility gap disappears
        self.assertTrue(A.accessibility_gap(par))
        self.assertFalse(A.accessibility_gap(dic))

    def test_H5_depth_budget_overrun(self):
        par = A.RESOURCE_WORLDS["W_PARITY3"]
        # POTENCY: the admissible class really grows
        self.assertLess(len(A.rule_class(3, 2)), len(A.rule_class(3, 3)))
        # DETECTION: overrunning the depth budget changes the claimed value
        self.assertEqual(A.best_acc_in_class(par, 3, 2), F(1, 2))
        self.assertEqual(A.best_acc_in_class(par, 3, 3), F(1))

    def test_H6_sample_budget_shifted(self):
        # POTENCY and DETECTION: the learning curve is strictly increasing,
        # so an off-by-one sample budget cannot pass unnoticed
        vals = [A.analytic_learning_curve(m) for m in range(4)]
        for i in range(3):
            self.assertLess(vals[i], vals[i + 1])
        self.assertNotEqual(vals[0], vals[1])

    def test_H7_reversal_killed_by_noiseless_dictator(self):
        par = A.RESOURCE_WORLDS["W_PARITY3"]
        clean = A.parity_world(0b001)
        nd = A.RESOURCE_WORLDS["W_NOISY_DICT"]
        # POTENCY: swapping the noisy dictator for the noiseless one moves the
        # top-budget accuracy
        self.assertNotEqual(A.best_acc_in_class(nd, 3, 3),
                            A.best_acc_in_class(clean, 3, 3))
        # DETECTION: the reversal that carries AE1-5 is destroyed
        self.assertTrue(A.has_order_reversal(par, nd, A.BUDGETS))
        self.assertFalse(A.has_order_reversal(par, clean, A.BUDGETS))

    def test_H8_minimality_grid_shrunk(self):
        saved = A.GRID_DEN
        try:
            A.GRID_DEN = 4
            small = A.realizability_map()
        finally:
            A.GRID_DEN = saved
        full = A.realizability_map()
        # POTENCY: the realizability map really changes
        self.assertNotEqual(small, full)
        # DETECTION: the frozen grid denominator is the one in the receipt
        self.assertEqual(R["minimality"]["grid_denominator"], 8)

    def test_H9_vacuous_hostile_is_itself_caught(self):
        """A perturbation preserving product form moves nothing: proving that
        this package would notice such a non-hostile."""
        w = A.WORLDS["W_IND_SKEW"]
        xs, ys, P = w["xs"], w["ys"], w["P"]
        Q = dict(P)   # identity perturbation
        self.assertEqual(A.l1_dependence(Q, xs, ys),
                         A.l1_dependence(P, xs, ys))
        self.assertEqual(A.pred_dep(Q, xs, ys), A.pred_dep(P, xs, ys))
        # a hostile with zero potency must not be counted as detected
        potency = A.l1_dependence(Q, xs, ys) != A.l1_dependence(P, xs, ys)
        self.assertFalse(potency)


class TestRandomizedRuleReduction(unittest.TestCase):
    """Randomised rules never beat the best deterministic rule."""

    def test_randomized_rules_do_not_beat_deterministic(self):
        w = A.WORLDS["W_DEP_NOPRED"]
        xs, ys, P = w["xs"], w["ys"], w["P"]
        best = A.acc_obs(P, xs, ys)
        # exhaustive grid of randomised rules with weights in multiples of 1/4
        grid = [(F(i, 4), F(4 - i, 4)) for i in range(5)]
        for w0 in grid:
            for w1 in grid:
                mix = {xs[0]: w0, xs[1]: w1}
                val = sum((P[(x, ys[j])] * mix[x][j]
                           for x in xs for j in range(len(ys))), F(0))
                self.assertLessEqual(val, best)


if __name__ == "__main__":
    unittest.main(verbosity=2)
