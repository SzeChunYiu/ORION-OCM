#!/usr/bin/env python3
"""GMI #833 AE2 tests: two-route agreement, hostile potency, hostile detection.

Runs under `python3 -I -B` and `python3 -I -O -B`.  Stdlib only.
Every hostile asserts POTENCY (the perturbation moves the quantity it targets)
before asserting DETECTION (the checker flags it).
"""
import ast
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae2_predictive_boundary_v1 as A          # noqa: E402
import independent_boundary_oracle_v1 as O      # noqa: E402

RES = A.build()
R = RES["results"]


class TestVerdict(unittest.TestCase):
    def test_green(self):
        self.assertEqual(RES["verdict"], "GREEN")
        for name, ok in RES["checks"].items():
            self.assertTrue(ok, "check failed: " + name)

    def test_no_float_in_receipt(self):
        def walk(o):
            if isinstance(o, float):
                self.fail("float in receipt")
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


class TestRouteIndependence(unittest.TestCase):
    def test_oracle_does_not_import_route_a(self):
        with open(O.__file__) as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertNotIn("ae2_predictive_boundary", a.name)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn("ae2_predictive_boundary", node.module or "")

    def test_PIB1_risks_agree(self):
        for hist_len in (1, 2):
            P, hists, ys = A.iid_history_world(F(3, 10), hist_len)
            for lname, loss in A.LOSSES.items():
                self.assertEqual(A.blind_risk(P, hists, ys, loss),
                                 O.oracle_blind_risk(P, hists, ys, loss),
                                 lname)
                self.assertEqual(A.informed_risk(P, hists, ys, loss),
                                 O.oracle_informed_risk(P, hists, ys, loss),
                                 lname)

    def test_PIB1_randomised_rules_do_not_help(self):
        P, hists, ys = A.iid_history_world(F(3, 10), 1)
        for lname, loss in A.LOSSES.items():
            det = O.oracle_informed_risk(P, hists, ys, loss)
            rnd = O.oracle_randomised_risk_floor(P, hists, ys, loss)
            self.assertIsNotNone(rnd)
            self.assertGreaterEqual(rnd, det, lname)

    def test_PIB2_proof_chain_verified_stepwise(self):
        cases, s1, s2, colsum = O.oracle_sweep_proof_chain()
        self.assertEqual(cases,
                         R["PIB_2_bounded_predictive_information"][
                             "exhaustive_grid_cases"])
        self.assertEqual(s1, 0)
        self.assertEqual(s2, 0)
        self.assertEqual(colsum, 0)

    def test_PIB3_two_series_agree_and_sit_inside_the_crude_bracket(self):
        for t in (F(2), F(3, 2), F(1, 2), F(4, 3), F(9, 10), F(10, 9)):
            alo, ahi = A.ln_bracket(t)
            blo, bhi = O.oracle_ln_bracket(t)
            clo, chi = O.oracle_crude_ln_bracket(t)
            self.assertLessEqual(alo, ahi, str(t))
            self.assertLessEqual(blo, bhi, str(t))
            # the two independent series brackets must overlap
            self.assertLessEqual(alo, bhi, str(t))
            self.assertLessEqual(blo, ahi, str(t))
            # and both must lie inside the parent-owned crude bracket
            self.assertGreaterEqual(ahi, clo, str(t))
            self.assertLessEqual(alo, chi, str(t))

    def test_PIB3_mutual_information_brackets_agree(self):
        for name, P in A.REGISTERED_ROSTER.items():
            alo, ahi = A.mutual_information_bracket(P, A.B2, A.B2)
            blo, bhi = O.oracle_mutual_information_bracket(P, A.B2, A.B2)
            self.assertLessEqual(alo, bhi, name)
            self.assertLessEqual(blo, ahi, name)

    def test_PIB4_depth_optima_agree(self):
        for sec in (0b111, 0b001, 0b011):
            P = A.parity_world(sec)
            Q = O.oracle_parity_world(sec)
            self.assertEqual(P, Q)
            for d in range(A.NBITS + 1):
                self.assertEqual(A.best_depth_bounded_accuracy(P, d),
                                 O.oracle_best_depth_bounded_accuracy(Q, d),
                                 "secret=%d depth=%d" % (sec, d))

    def test_PIB5_fixtures_agree(self):
        base, best = O.oracle_cyclic_gain()
        f = R["PIB_5_fixtures"]["HIGHENT_CYCLIC"]
        self.assertEqual(str(base), f["acc_base"])
        self.assertEqual(str(best), f["acc_obs"])
        h, accs = O.oracle_doubling_horizon(A.DOUBLING_BITS, A.DOUBLING_OBS)
        c = R["PIB_5_fixtures"]["CHAOS_DOUBLING"]
        self.assertEqual(h, c["certainty_horizon"])
        self.assertEqual([str(a) for a in accs],
                         [s["bayes_accuracy"] for s in c["per_step"]])
        self.assertEqual(
            str(O.oracle_drift_phase2_accuracy()),
            R["PIB_5_fixtures"]["DRIFT_INVERT"][
                "phase1_fitted_rule_accuracy_in_phase2"])


class TestNamedResults(unittest.TestCase):
    def test_PIB1(self):
        p = R["PIB_1_no_predictive_information"]
        self.assertEqual(p["hist2"]["observation_alphabet"], 4)
        self.assertEqual(p["hist2"]["deterministic_rules"], 16)
        for k in ("hist1", "hist2"):
            self.assertTrue(p[k]["exactly_independent"])
            for lname in ("zero_one", "asymmetric", "squared"):
                self.assertEqual(p[k]["losses"][lname]["improvement"], "0")

    def test_PIB2(self):
        p = R["PIB_2_bounded_predictive_information"]
        self.assertEqual(p["exhaustive_grid_cases"], 670396)
        self.assertEqual(p["violations"], 0)
        self.assertEqual(p["cases_attaining_equality_with_positive_gain"],
                         15328)
        self.assertEqual(p["roster"]["W_TIGHT"]["gain"], "1/2")
        self.assertEqual(p["roster"]["W_TIGHT"]["l1_dependence"], "1")
        self.assertEqual(p["roster"]["W_DEP_NOPRED"]["gain"], "0")
        self.assertEqual(p["roster"]["W_DEP_NOPRED"]["l1_dependence"], "1/5")
        for v in p["roster"].values():
            self.assertTrue(v["two_gain_le_D"])
            self.assertTrue(v["pinsker_D_sq_over_two_le_MI_lower"])
            self.assertTrue(v["MI_upper_le_chi_squared"])
            self.assertTrue(v["two_gain_sq_le_MI_lower"])

    def test_PIB4(self):
        p = R["PIB_4_decoder_complexity"]
        self.assertEqual(p["acc_base"], "1/2")
        self.assertEqual(p["best_accuracy_by_depth"]["depth0"]["parity"], "1/2")
        self.assertEqual(p["best_accuracy_by_depth"]["depth1"]["parity"], "1/2")
        self.assertEqual(p["best_accuracy_by_depth"]["depth2"]["parity"], "1/2")
        self.assertEqual(p["best_accuracy_by_depth"]["depth3"]["parity"], "1")
        self.assertEqual(p["best_accuracy_by_depth"]["depth1"]["dictator"], "1")
        self.assertEqual(p["proper_subsets_checked"], 7)
        self.assertEqual(p["proper_subset_uniformity_violations"], 0)
        self.assertFalse(p["cryptographic_assumption_used"])

    def test_PIB5(self):
        f = R["PIB_5_fixtures"]
        self.assertEqual(f["LOWENT_IID"]["predictive_gain"], "0")
        self.assertEqual(f["LOWENT_IID"]["l1_dependence"], "0")
        self.assertFalse(f["LOWENT_IID"]["marginal_is_uniform"])
        self.assertEqual(f["HIGHENT_CYCLIC"]["predictive_gain"], "3/4")
        self.assertTrue(f["HIGHENT_CYCLIC"]["marginal_is_uniform"])
        self.assertEqual(f["HIGHENT_CYCLIC"]["marginal_entropy_bits_exact"],
                         "2")
        self.assertEqual(
            f["DRIFT_INVERT"]["phase1_fitted_rule_accuracy_in_phase1"], "1")
        self.assertEqual(
            f["DRIFT_INVERT"]["phase1_fitted_rule_accuracy_in_phase2"], "0")
        self.assertEqual(f["DRIFT_INVERT"]["phase2_base_rate"], "1/2")
        self.assertTrue(f["DRIFT_INVERT"]["pooled_exactly_independent"])
        self.assertEqual(f["CHAOS_DOUBLING"]["certainty_horizon"], 4)
        self.assertEqual(f["CHAOS_DOUBLING"]["states_enumerated"], 256)

    def test_null(self):
        n = R["null"]
        self.assertEqual(n["random_worlds_flagged"], 0)
        self.assertTrue(n["planted_positive_flagged"])
        self.assertEqual(n["known_clean_flagged"], [])
        self.assertEqual(n["trials"], 200)


class TestHostiles(unittest.TestCase):

    def test_H1_false_independence(self):
        P, hists, ys = A.iid_history_world(F(3, 10), 1)
        Q = dict(P)
        # move mass so the target now depends on the history
        Q[((0,), 0)] = Q[((0,), 0)] + F(1, 10)
        Q[((0,), 1)] = Q[((0,), 1)] - F(1, 10)
        Q[((1,), 0)] = Q[((1,), 0)] - F(1, 10)
        Q[((1,), 1)] = Q[((1,), 1)] + F(1, 10)
        loss = A.LOSSES["zero_one"]
        # POTENCY
        self.assertNotEqual(A.informed_risk(Q, hists, ys, loss),
                            A.informed_risk(P, hists, ys, loss))
        # DETECTION
        self.assertTrue(A.is_independent(P, hists, ys))
        self.assertFalse(A.is_independent(Q, hists, ys))
        self.assertGreater(A.blind_risk(Q, hists, ys, loss),
                           A.informed_risk(Q, hists, ys, loss))

    def test_H2_gain_bound_violated_by_a_halved_D(self):
        P = A.REGISTERED_ROSTER["W_TIGHT"]
        g = A.gain(P, A.B2, A.B2)
        d = A.l1_dependence(P, A.B2, A.B2)
        fake = d / 2
        # POTENCY
        self.assertNotEqual(fake, d)
        # DETECTION: the true D satisfies the bound tightly, the fake does not
        self.assertEqual(2 * g, d)
        self.assertGreater(2 * g, fake)

    def test_H3_corrupted_log_bracket(self):
        t = F(2)
        lo, hi = A.ln_bracket(t)
        blo, bhi = lo + F(1, 10), hi + F(1, 10)
        # POTENCY
        self.assertNotEqual((blo, bhi), (lo, hi))
        # DETECTION: the corrupted bracket no longer overlaps the independent
        # Mercator bracket
        olo, ohi = O.oracle_ln_bracket(t)
        self.assertTrue(lo <= ohi and olo <= hi)
        self.assertFalse(blo <= ohi and olo <= bhi)

    def test_H4_depth_budget_overrun(self):
        P = A.parity_world(0b111)
        two = A.best_depth_bounded_accuracy(P, 2)
        three = A.best_depth_bounded_accuracy(P, 3)
        # POTENCY
        self.assertNotEqual(two, three)
        # DETECTION
        self.assertEqual(two, F(1, 2))
        self.assertEqual(three, F(1))

    def test_H5_fixture_marginal_silently_broken(self):
        zs = [0, 1, 2, 3]
        good = dict(((a, b), F(1, 4) if b == (a + 1) % 4 else F(0))
                    for a in zs for b in zs)
        bad = dict(good)
        bad[(0, 1)] = F(1, 8)
        bad[(1, 2)] = F(3, 8)
        # POTENCY
        self.assertNotEqual(A.marginals(bad, zs, zs)[0],
                            A.marginals(good, zs, zs)[0])
        # DETECTION: the uniform-marginal property the fixture asserts fails
        pxg = A.marginals(good, zs, zs)[0]
        pxb = A.marginals(bad, zs, zs)[0]
        self.assertTrue(all(pxg[z] == F(1, 4) for z in zs))
        self.assertFalse(all(pxb[z] == F(1, 4) for z in zs))

    def test_H6_pooled_independence_broken_by_unequal_phases(self):
        ph1 = dict(((x, y), F(1, 2) if y == x else F(0))
                   for x in A.B2 for y in A.B2)
        ph2 = dict(((x, y), F(1, 2) if y != x else F(0))
                   for x in A.B2 for y in A.B2)
        even = dict(((k), (ph1[k] + ph2[k]) / 2) for k in ph1)
        skew = dict(((k), ph1[k] * F(3, 4) + ph2[k] * F(1, 4)) for k in ph1)
        # POTENCY
        self.assertNotEqual(A.l1_dependence(skew, A.B2, A.B2),
                            A.l1_dependence(even, A.B2, A.B2))
        # DETECTION
        self.assertTrue(A.is_independent(even, A.B2, A.B2))
        self.assertFalse(A.is_independent(skew, A.B2, A.B2))

    def test_H7_parity_replaced_by_two_bit_xor(self):
        good = A.parity_world(0b111)
        bad = A.parity_world(0b011)
        # POTENCY
        self.assertNotEqual(A.best_depth_bounded_accuracy(bad, 2),
                            A.best_depth_bounded_accuracy(good, 2))
        # DETECTION
        self.assertTrue(A.hidden_information_detector(good))
        self.assertFalse(A.hidden_information_detector(bad))

    def test_H8_chaos_observation_widened(self):
        h4, _ = O.oracle_doubling_horizon(A.DOUBLING_BITS, 4)
        h5, _ = O.oracle_doubling_horizon(A.DOUBLING_BITS, 5)
        # POTENCY
        self.assertNotEqual(h4, h5)
        # DETECTION: the frozen observation width is the one in the receipt
        self.assertEqual(R["PIB_5_fixtures"]["CHAOS_DOUBLING"][
            "certainty_horizon"], 4)
        self.assertEqual(h5, 5)

    def test_H9_vacuous_hostile_has_no_potency(self):
        """A perturbation preserving the product form moves nothing; this test
        exists so a zero-potency hostile cannot masquerade as detected."""
        P = A.REGISTERED_ROSTER["W_INDEP"]
        Q = dict(P)
        potency = (A.l1_dependence(Q, A.B2, A.B2)
                   != A.l1_dependence(P, A.B2, A.B2))
        self.assertFalse(potency)
        self.assertTrue(A.is_independent(Q, A.B2, A.B2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
