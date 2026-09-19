#!/usr/bin/env python3
"""Tests for the E9 exec-rank revival package: exact expectations, hostile
battery, oracle agreement, and receipt validation. Run `python -I -B ... -v`."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
V1_DIR = ROOT.parent / "gmi-833-g0-grammar-growth-v1"
V2_DIR = ROOT.parent / "gmi-833-g0-grammar-growth-v2"
sys.path.insert(0, str(V1_DIR))
sys.path.insert(0, str(V2_DIR))
sys.path.insert(0, str(ROOT))

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402
import exec_rank_revival_v1 as e1  # noqa: E402

FX = json.loads((ROOT / "FROZEN_FIXTURES_E1.json").read_text())
RESULT = json.loads((ROOT / "RESULT_E1.json").read_text())
ORACLE = json.loads((ROOT / "ORACLE_RESULT_E1.json").read_text())

BAT = e1.battery(FX)


class Fixtures(unittest.TestCase):
    def test_fixture_hash_matches_receipt(self):
        self.assertEqual(hashlib.sha256(
            (ROOT / "FROZEN_FIXTURES_E1.json").read_bytes()).hexdigest(),
            RESULT["fixtures_sha256"])

    def test_pins_v1_v2_fixtures(self):
        self.assertEqual(hashlib.sha256(
            (V1_DIR / "FROZEN_FIXTURES_V1.json").read_bytes()).hexdigest(),
            FX["v1_fixtures_sha256"])
        self.assertEqual(hashlib.sha256(
            (V2_DIR / "FROZEN_FIXTURES_V2.json").read_bytes()).hexdigest(),
            FX["v2_fixtures_sha256"])

    def test_freeze_commit_recorded(self):
        self.assertEqual(RESULT["freeze_commit"],
                         "79651e4877b719b7d5575e869ad1c3c7c0018c05")

    def test_claim_ceiling_and_forbidden(self):
        self.assertEqual(RESULT["claim_ceiling"], e1.CLAIM_CEILING)
        for bad in ("RECURSIVE_LIBRARY_EXEC_OPTIMAL",
                    "SINGLE_JOINT_CHARGE_ACHIEVES_BOTH_METRIC_RANK1",
                    "UNIFORM_IN_RHO_RANK1"):
            self.assertIn(bad, RESULT["forbidden_promotions"])


class FastDPs(unittest.TestCase):
    def test_fast_burden_matches_frozen_on_v1ref(self):
        inv = v1.invent(BAT["v1ref"]["corpus"], 1)
        order = ["a", "b", "c"] + inv["library_order"]
        exps = v1.symbol_expansions(order, inv["library"])
        for w in BAT["v1ref"]["hp"]:
            self.assertEqual(e1.fast_burden_dp(w, order, exps)[0],
                             v1.burden_dp(w, order, exps)[0])

    def test_fast_exec_matches_frozen_rho_0_1_4(self):
        inv = v1.invent(BAT["v1ref"]["corpus"], 1)
        order = ["a", "b", "c"] + inv["library_order"]
        for w in BAT["v1ref"]["hp"][:4]:
            for rho in (0, 1, 4):
                self.assertEqual(
                    e1.fast_exec_burden(w, order, inv["library"], rho),
                    v2.exec_burden(w, order, inv["library"], rho))

    def test_fast_exec_matches_naive(self):
        lib = {"m1": ("a", "b"), "m2": ("m1", "m1")}
        order = ["a", "b", "c", "m1", "m2"]
        for w in ("abab", "aabab", "ababab"):
            self.assertEqual(
                e1.fast_exec_burden(tuple(w), order, lib, 1),
                v2.exec_burden_naive(tuple(w), order, lib, 1))

    def test_exec_affine_in_rho(self):
        lib = {"m1": ("a", "b"), "m2": ("m1", "m1")}
        order = ["a", "b", "c", "m1", "m2"]
        w = tuple("aabab")
        a = e1.fast_exec_burden(w, order, lib, 0)
        b = e1.fast_exec_burden(w, order, lib, 1)
        c = e1.fast_exec_burden(w, order, lib, 4)
        self.assertEqual(c - a, 4 * (b - a))


class DispatchDecomposition(unittest.TestCase):
    def test_opcost_equals_expand_plus_rho_dispatch(self):
        for lib in ({"m1": ("a", "b"), "m2": ("m1", "m1")},
                    {"m1": ("a", "b"), "m2": ("m1", "m1", "m1", "m1"),
                     "m3": ("m2", "m2")}):
            for rho in (0, 1, 2, 4):
                cost = v2.opcosts(lib, rho)
                for name, body in lib.items():
                    d = e1.dispatch_counts(lib)[name]
                    self.assertEqual(
                        cost[name],
                        len(v1.expand_word(body, lib)) + rho * d)

    def test_exec_splits_len_plus_rho_disp(self):
        lib = {"m1": ("a", "b"), "m2": ("m1", "m1")}
        order = ["a", "b", "c", "m1", "m2"]
        w = tuple("aabab")
        e0 = e1.fast_exec_burden(w, order, lib, 0)
        e1v = e1.fast_exec_burden(w, order, lib, 1)
        self.assertGreater(e1v, e0)


class NestingFamily(unittest.TestCase):
    def test_flatten_preserves_expansion_and_order(self):
        for cid in ("v1ref", "c3", "c4", "c5"):
            inv = v1.invent(BAT[cid]["corpus"], 1)
            fl = e1.flatten(inv["library"])
            self.assertEqual(list(fl), inv["library_order"])
            for n in fl:
                self.assertEqual(
                    v1.expand_word(fl[n], fl),
                    v1.expand_word(inv["library"][n], inv["library"]))

    def test_family_sizes(self):
        inv = v1.invent(BAT["v1ref"]["corpus"], 1)
        fam = e1.nesting_family(inv["library"], inv["library_order"])
        sigs = {tuple(tuple(lib[n]) for n in names) for lib, names in fam}
        self.assertEqual(len(sigs), 3)  # {ab}, {ab,nested}, {ab,flat}
        inv3 = v1.invent(BAT["c3"]["corpus"], 1)
        fam3 = e1.nesting_family(inv3["library"], inv3["library_order"])
        sigs3 = {tuple(tuple(lib[n]) for n in names) for lib, names in fam3}
        self.assertEqual(len(sigs3), 7)  # prefixes 1 + 2 + 4

    def test_flattening_leaves_count_burden_unchanged(self):
        # same visited sets: the two count burdens differ by exactly dK
        hp = BAT["v1ref"]["hp"]
        inv = v1.invent(BAT["v1ref"]["corpus"], 1)
        fl = e1.flatten(inv["library"])
        names = inv["library_order"]
        nr_i = e1.hplus_nets(names, inv["library"], hp, 1)
        nr_f = e1.hplus_nets(names, fl, hp, 1)
        self.assertEqual(nr_i["count_abs"] - nr_f["count_abs"],
                         v1.k_total(inv["library"], 1) - v1.k_total(fl, 1))
        self.assertEqual(v1.k_total(inv["library"], 1) - v1.k_total(fl, 1), -2)


class AffineLaw(unittest.TestCase):
    def test_all_pairs_exact_per_corpus(self):
        for cid in ("v1ref", "c3", "c4", "c5"):
            entry = RESULT["corpora"][cid]
            self.assertTrue(entry["affine_checks"])
            for c in entry["affine_checks"]:
                self.assertTrue(c["exact"], (cid, c))

    def test_tamper_detected(self):
        self.assertTrue(RESULT["hostiles"]["hexr2"]["tamper_detected"])


class ExecMDL(unittest.TestCase):
    def test_degenerate_on_all_corpora(self):
        for cid, d in BAT.items():
            deg, worst = e1.exec_mdl_degenerate(d["corpus"])
            self.assertTrue(deg, cid)
            self.assertLess(worst, 0)

    def test_gain_formula(self):
        # gain_execMDL(u) = -rho*o - exec(u) - kappa < 0 always
        corpus = BAT["v1ref"]["corpus"]
        pool = v1.candidate_pool(corpus, {})
        for body, (occ, _, _) in pool.items():
            for rho in (1, 2, 4):
                self.assertLess(-rho * occ - len(body) - 1, 0)


class WitnessAndRanks(unittest.TestCase):
    def test_witness_rank1_both_everywhere(self):
        for cid, entry in RESULT["corpora"].items():
            self.assertEqual(entry["ranks"]["witness"]["cb"], 0, cid)
            self.assertEqual(entry["ranks"]["witness"]["eb"], 0, cid)

    def test_v1ref_fragility_reproduced(self):
        self.assertEqual(RESULT["corpora"]["v1ref"]["ranks"]["inv"]["cb"], 0)
        self.assertEqual(RESULT["corpora"]["v1ref"]["ranks"]["inv"]["eb"], 19)

    def test_witness_bodies(self):
        self.assertEqual(RESULT["corpora"]["v1ref"]["witness"]["bodies"],
                         ["ab", "abab"])
        self.assertEqual(RESULT["corpora"]["trap1"]["witness"]["bodies"],
                         ["ab", "abab"])
        self.assertEqual(RESULT["corpora"]["trap3"]["witness"]["bodies"], ["ab"])

    def test_breakevens(self):
        c = RESULT["corpora"]
        self.assertEqual(c["v1ref"]["witness"]["breakeven"], 314)
        self.assertEqual(c["v1ref"]["inv_breakeven"], 164)
        self.assertEqual(c["trap1"]["witness"]["breakeven"], 53)
        self.assertEqual(c["trap1"]["inv_breakeven"], 5)
        self.assertEqual(c["trap3"]["witness"]["breakeven"], 41)
        self.assertEqual(c["trap3"]["inv_breakeven"], 1)

    def test_breakeven_closed_form_matches_bruteforce(self):
        # brute scan on the v1ref witness (1024 rho, fast DPs)
        hp = BAT["v1ref"]["hp"]
        wlib = {"m1": ("a", "b"), "m2": ("a", "b", "a", "b")}
        names = ["m1", "m2"]
        g0 = e1.g0_exec(hp, 1)
        order = ["a", "b", "c"] + names
        K = v1.k_total(wlib, 1)
        brute = "NONE_IN_RANGE"
        for rho in range(1, 1025):
            if sum(e1.fast_exec_burden(w, order, wlib, rho) for w in hp) + K - g0 >= 0:
                brute = rho
                break
        self.assertEqual(brute, RESULT["corpora"]["v1ref"]["witness"]["breakeven"])

    def test_ties_are_identity_draws(self):
        c = RESULT["corpora"]
        self.assertEqual(c["v1ref"]["tie_counts"]["count"],
                         c["v1ref"]["tie_census"]["n_identity_draws"])
        self.assertEqual(c["v1ref"]["tie_counts"]["exec"], 19)
        self.assertEqual(c["trap1"]["tie_counts"]["count"], 4)
        self.assertEqual(c["trap3"]["tie_counts"]["count"], 16)
        self.assertEqual(c["c4"]["tie_counts"]["count"], 0)
        self.assertEqual(c["c5"]["tie_counts"]["count"], 0)

    def test_rung_selection(self):
        for cid, entry in RESULT["corpora"].items():
            self.assertTrue(entry["rung_selection"]["exec_rho1_rung"]["is_full_flattening"], cid)
            self.assertTrue(entry["rung_selection"]["exec_rho2_is_full_flattening"], cid)
            self.assertTrue(entry["rung_selection"]["exec_rho4_is_full_flattening"], cid)
            self.assertTrue(entry["rung_selection"]["count_rung"]["is_min_k_among_full_set"], cid)


class SpacesAndArgmins(unittest.TestCase):
    def test_v1ref_argmins(self):
        entry = RESULT["corpora"]["v1ref"]
        self.assertEqual(entry["space_argmin"]["count"]["net"], -48739)
        self.assertEqual(entry["space_argmin"]["count"]["bodies"],
                         ["ab", "m1m1"])
        self.assertEqual(entry["space_argmin"]["exec"]["net"], -396644)
        self.assertEqual(entry["space_argmin"]["exec"]["bodies"], ["ab", "abab"])

    def test_v1ref_frontier_two_net_points(self):
        fr = RESULT["corpora"]["v1ref"]["frontier"]
        pairs = sorted({(f["count_net"], f["exec_net"]) for f in fr})
        self.assertEqual(pairs, [(-48739, -395484), (-48737, -396644)])

    def test_c3_argmins(self):
        entry = RESULT["corpora"]["c3"]
        self.assertEqual(entry["space_argmin"]["count"]["net"],
                         -31501345179969635)
        self.assertEqual(entry["space_argmin"]["exec"]["net"],
                         -1036301575840176630)

    def test_trap_frontiers_single_net_point(self):
        fr1 = RESULT["corpora"]["trap1"]["frontier"]
        pairs1 = {(f["count_net"], f["exec_net"]) for f in fr1}
        self.assertEqual(len(pairs1), 1)
        self.assertEqual(pairs1, {(-21537, -144023)})
        fr3 = RESULT["corpora"]["trap3"]["frontier"]
        pairs3 = {(f["count_net"], f["exec_net"]) for f in fr3}
        self.assertEqual(len(pairs3), 1)
        self.assertEqual(pairs3, {(-17348, -117867)})

    def test_c4_c5_chain_only_registered(self):
        self.assertEqual(RESULT["corpora"]["c4"]["space"]["kind"], "chain_only")
        self.assertEqual(RESULT["corpora"]["c5"]["space"]["kind"], "chain_only")

    def test_trap_inv_rank_fragility_under_both(self):
        self.assertEqual(RESULT["corpora"]["trap1"]["ranks"]["inv"]["cb"], 52)
        self.assertEqual(RESULT["corpora"]["trap1"]["ranks"]["inv"]["eb"], 49)
        self.assertEqual(RESULT["corpora"]["trap3"]["ranks"]["inv"]["cb"], 33)
        self.assertEqual(RESULT["corpora"]["trap3"]["ranks"]["inv"]["eb"], 33)


class ChargeClass(unittest.TestCase):
    def test_v1ref_charge_paths(self):
        cp = RESULT["corpora"]["v1ref"]["charge_paths"]
        self.assertEqual(cp["count"]["bodies"], ["ab", "m1m1"])
        for p in ("exec", "max", "sum", "countdisp"):
            self.assertEqual(cp[p]["bodies"], ["ab"], p)

    def test_trap_charge_paths_trapped(self):
        expected = {
            "trap1": {"count": ["bcbc", "ab"], "exec": ["bcbc", "ab"],
                      "max": ["bcbc", "ab"], "countdisp": ["bcbc", "ab"],
                      "sum": ["bc"]},
            "trap3": {"count": ["abc"], "exec": ["abc"], "max": ["abc"],
                      "countdisp": ["abc"], "sum": ["abc"]},
        }
        for cid, exp in expected.items():
            for p, bodies in exp.items():
                self.assertEqual(RESULT["corpora"][cid]["charge_paths"][p]["bodies"],
                                 bodies, (cid, p))

    def test_none_universal(self):
        self.assertEqual(RESULT["charge_class_verdict"]
                         ["charges_with_both_rank1_everywhere"], [])
        self.assertTrue(RESULT["charge_class_verdict"]["none_universal"])


class Hostiles(unittest.TestCase):
    def test_all_hostiles_green(self):
        h = RESULT["hostiles"]
        self.assertTrue(h["hexr1"]["all_agree"])
        self.assertTrue(h["hexr2"]["tamper_detected"])
        self.assertTrue(h["hexr3"]["expansion_preserved"])
        self.assertTrue(h["hexr4"]["all_match"])
        self.assertTrue(h["hexr5"]["identity"])
        self.assertTrue(h["hexr6"]["library_byte_identical"])
        self.assertEqual(h["hexr7"]["code"], "CYCLE_REJECTED")

    def test_hexr4_direct(self):
        h = e1.hostile_hexr4()
        self.assertTrue(h["all_match"])

    def test_hexr5_direct(self):
        h = e1.hostile_hexr5(BAT)
        self.assertEqual(h["empty_count_net"], 0)
        self.assertEqual(h["empty_exec_net"], 0)

    def test_hexr7_cycle(self):
        with self.assertRaises(v1.GrammarGrowthError):
            v1.expand_word(("m2",),
                           {"m1": ("a", "b"), "m2": ("m3", "a"), "m3": ("m2", "b")})

    def test_hexr6_leakage(self):
        h = e1.hostile_hexr6(BAT)
        self.assertTrue(h["library_byte_identical"])


class ReceiptAndOracle(unittest.TestCase):
    def test_terminal_green(self):
        self.assertEqual(RESULT["terminal"],
                         "GMI_833_E9_EXEC_RANK_REVIVAL_GREEN_AT_REGISTERED_SCOPE")

    def test_all_checks_true(self):
        failed = [k for k, v in RESULT["checks"].items() if not v]
        self.assertEqual(failed, [])

    def test_oracle_all_ok(self):
        self.assertTrue(ORACLE["all_ok"])
        self.assertGreaterEqual(len(ORACLE["checks"]), 19)

    def test_receipt_reproducible(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            e1.main()
        self.assertEqual(json.loads(buf.getvalue()), RESULT)

    def test_null_ensemble_consistent_with_v2(self):
        # v1ref size-2 count nets must equal v2.null_ensemble_v2's (machinery reuse)
        hp = BAT["v1ref"]["hp"]
        ne = v2.null_ensemble_v2(BAT["v1ref"]["corpus"], 2, list(range(200)),
                                 hp, BAT["v1ref"]["hm"], 1, exec_rho=1)
        self.assertEqual(ne["nets_hplus"],
                         RESULT["corpora"]["v1ref"]["nulls"]["nets_count"])
        self.assertEqual(ne["exec_nets_hplus"],
                         RESULT["corpora"]["v1ref"]["nulls"]["nets_exec"])

    def test_headline_integers(self):
        c = RESULT["corpora"]["v1ref"]
        self.assertEqual(c["inv_nets"]["count_net"], -48739)
        self.assertEqual(c["inv_nets"]["exec_net_rho1"], -395484)
        self.assertEqual(c["witness"]["nets"]["count_net"], -48737)
        self.assertEqual(c["witness"]["nets"]["exec_net_rho1"], -396644)
        self.assertEqual(c["witness"]["nets"]["exec_net_rho2"], -395376)
        self.assertEqual(c["witness"]["nets"]["exec_net_rho4"], -392840)


if __name__ == "__main__":
    unittest.main(verbosity=2)
