#!/usr/bin/env python3
"""Tests for the tranche-2 package: exact expectations, hostile battery,
oracle agreement, and receipt validation. Run with `python -I -B ... -v`."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
V1_DIR = ROOT.parent / "gmi-833-g0-grammar-growth-v1"
sys.path.insert(0, str(V1_DIR))
sys.path.insert(0, str(ROOT))

import g0_grammar_growth_v1 as v1  # noqa: E402
import g0_grammar_growth_v2 as v2  # noqa: E402

FX = json.loads((ROOT / "FROZEN_FIXTURES_V2.json").read_text())
V1FX = json.loads((V1_DIR / "FROZEN_FIXTURES_V1.json").read_text())
RESULT = json.loads((ROOT / "RESULT_V2.json").read_text())


def P(w):
    return tuple(w)


def subwords(w, lo, hi=None):
    hi = hi or lo
    return {tuple(w[i:j]) for i in range(len(w)) for j in range(i + lo, min(len(w), i + hi) + 1)}


class FixturesAndSuites(unittest.TestCase):
    def test_fixture_hashes(self):
        self.assertEqual(
            hashlib.sha256((ROOT / "FROZEN_FIXTURES_V2.json").read_bytes()).hexdigest(),
            RESULT["fixtures_sha256"],
        )
        self.assertEqual(
            hashlib.sha256((V1_DIR / "FROZEN_FIXTURES_V1.json").read_bytes()).hexdigest(),
            FX["v1_fixtures_sha256"],
        )
        self.assertEqual(v2.V1_FIXTURES_SHA, FX["v1_fixtures_sha256"])

    def test_freeze_files_exist(self):
        self.assertTrue((ROOT / "FREEZE_V2.md").exists())

    def test_suites_reuse_positive(self):
        for cid in ("c3", "c4", "c5", "trap1", "trap3"):
            corp = [P(w) for w in FX["corpora"][cid]["programs"]]
            tsub = set()
            for p in corp:
                tsub |= subwords(p, 1, len(p))
            flat = [w for ws in FX["suites"][cid]["hplus"].values() for w in ws]
            flat += FX["suites"][cid].get("validation_shallow", FX["suites"][cid].get("validation", []))
            flat += FX["suites"][cid].get("validation_deep", [])
            for w in flat:
                tw = P(w)
                self.assertNotIn(tw, tsub, (cid, w))
                ok = any(
                    len(u) >= 2
                    and v1.greedy_count(u, tw) >= 2
                    and sum(v1.greedy_count(u, p) for p in corp) >= 2
                    for u in subwords(tw, 2, len(tw))
                )
                self.assertTrue(ok, (cid, w))
            self.assertEqual(len(flat), len(set(flat)))

    def test_suites_hminus(self):
        for cid in ("c3", "c4", "c5", "trap1", "trap3"):
            corp = [P(w) for w in FX["corpora"][cid]["programs"]]
            tsub = set()
            for p in corp:
                tsub |= subwords(p, 1, len(p))
            forb = set()
            for p in corp:
                for s in subwords(p, 2, 2):
                    if sum(v1.greedy_count(s, q) for q in corp) >= 2:
                        forb.add(s)
            for w in FX["suites"][cid]["hminus"]:
                tw = P(w)
                self.assertNotIn(tw, tsub, (cid, w))
                self.assertFalse(set(subwords(tw, 2, 2)) & forb, (cid, w))
                counts = {}
                for i in range(len(tw)):
                    for j in range(i + 2, len(tw) + 1):
                        u = tuple(tw[i:j])
                        counts[u] = counts.get(u, 0) + 1
                self.assertTrue(all(c < 2 for c in counts.values()), (cid, w))

    def test_validation_disjoint_from_eval(self):
        for cid in ("c3", "c4", "c5", "trap1", "trap3"):
            ev = {P(w) for ws in FX["suites"][cid]["hplus"].values() for w in ws}
            ev |= {P(w) for w in FX["suites"][cid]["hminus"]}
            vv = [P(w) for w in FX["suites"][cid].get("validation_shallow", FX["suites"][cid].get("validation", []))]
            vv += [P(w) for w in FX["suites"][cid].get("validation_deep", [])]
            self.assertFalse(ev & set(vv), cid)
        ev = {P(w) for w in V1FX["heldout_reuse_positive"]} | {P(w) for w in V1FX["heldout_unrelated_control"]}
        vv = {P(w) for w in FX["suites"]["v1ref"]["validation"]}
        self.assertFalse(ev & vv)


class Formation(unittest.TestCase):
    def test_expected_traces(self):
        for cid in ("c3", "c4", "c5", "trap1", "trap3"):
            got = ["".join(a["body"]) for a in RESULT["depth_section"][cid]["admissions"]]
            want = [e["body"] for e in FX["expected_traces_kappa1"][cid]]
            self.assertEqual(got, want, cid)
            self.assertEqual(
                RESULT["depth_section"][cid]["grw1_failures"], 0, cid
            )

    def test_depths(self):
        self.assertEqual(RESULT["depth_section"]["c3"]["max_depth"], 3)
        self.assertEqual(RESULT["depth_section"]["c4"]["max_depth"], 3)
        self.assertEqual(RESULT["depth_section"]["c5"]["max_depth"], 3)

    def test_family_ceiling(self):
        fam = RESULT["family_formation"]
        self.assertEqual(fam["fn5"]["max_depth"], 1)
        self.assertEqual(fam["fn8"]["max_depth"], 1)
        self.assertEqual(fam["fn12"]["max_depth"], 1)
        self.assertLessEqual(fam["fl8"]["max_depth"], 2)
        self.assertLessEqual(fam["fl16"]["max_depth"], 2)

    def test_adm_alt_diagnostic_deeper(self):
        self.assertGreater(RESULT["adm_alt"]["c4"]["max_depth"], 3)
        self.assertGreater(RESULT["adm_alt"]["c5"]["max_depth"], 3)

    def test_adm_alt_semantics_preserved(self):
        # oracle of ADM-ALT semantics: expansions preserved (would have raised)
        corp = [P(w) for w in FX["corpora"]["c4"]["programs"]]
        r = v2.adm_alt(corp, 1)
        self.assertTrue(r["stopped_by"] in ("NO_STRICTLY_BENEFICIAL_CANDIDATE", "DEPTH_LIMIT"))

    def test_hzero2(self):
        corp = [P(w) for w in FX["corpora"]["c3"]["programs"]]
        t2 = v1.invent(corp, 2)
        t1 = v1.invent(corp, 1)
        self.assertEqual(len(t2["admissions"]), len(t1["admissions"]) - 1)
        self.assertNotEqual(t2["admissions"][-1]["gain"], 0)

    def test_kappa_star(self):
        for cid in ("c3", "c4", "c5"):
            self.assertEqual(
                RESULT["econ"][cid + "_kappa_star"]["kappa_star"],
                FX["expected_kappa_star"][cid],
                cid,
            )

    def test_fstar_strict(self):
        for cid in ("c3", "c4", "c5"):
            self.assertIsNotNone(RESULT["econ"][cid]["fstar_strict"], cid)


class Compounding(unittest.TestCase):
    def test_cmp1_receipt_holds(self):
        for cid in ("c3", "c4", "c5"):
            cmp1 = RESULT["tier_tables"][cid]["cmp1"]
            for tname, row in cmp1["tier_monotone_to_match_then_regression"].items():
                self.assertTrue(row["holds"], (cid, tname, row))
            self.assertTrue(cmp1["hminus_monotone_regression"], cid)
            self.assertTrue(cmp1["aggregate_net_strictly_decreasing"], cid)

    def test_tier_match_generations(self):
        tt = RESULT["tier_tables"]
        self.assertEqual(tt["c3"]["cmp1"]["tier_monotone_to_match_then_regression"]["T1"]["match_generation"], 1)
        self.assertEqual(tt["c3"]["cmp1"]["tier_monotone_to_match_then_regression"]["T2"]["match_generation"], 2)
        self.assertEqual(tt["c3"]["cmp1"]["tier_monotone_to_match_then_regression"]["T3"]["match_generation"], 3)
        self.assertEqual(tt["c4"]["cmp1"]["tier_monotone_to_match_then_regression"]["T3sep"]["match_generation"], 2)
        self.assertEqual(tt["c4"]["cmp1"]["tier_monotone_to_match_then_regression"]["T4"]["match_generation"], 3)
        self.assertEqual(tt["c5"]["cmp1"]["tier_monotone_to_match_then_regression"]["T5"]["match_generation"], 3)

    def test_burden_dp_matches_naive_spot(self):
        lib = {"m1": ("a", "b"), "m2": ("m1", "m1"), "m3": ("m2", "c", "m2")}
        order = ["a", "b", "c", "m1", "m2", "m3"]
        exps = v1.symbol_expansions(order, lib)
        for w in ("ababcab", "cac", "ababab", "abca"):
            b, hit = v1.burden_dp(P(w), order, exps)
            nb, nhit = v1.burden_naive(P(w), order, lib)
            self.assertEqual((b, hit), (nb, nhit), w)


class HeadToHead(unittest.TestCase):
    def test_registered_pattern(self):
        h = RESULT["head_to_head"]
        self.assertEqual(h["v1ref"]["compression"]["net_hplus_count"], h["v1ref"]["utility"]["net_hplus_count"])
        self.assertEqual(h["c4"]["compression"]["net_hplus_count"], h["c4"]["utility"]["net_hplus_count"])
        self.assertEqual(h["c5"]["compression"]["net_hplus_count"], h["c5"]["utility"]["net_hplus_count"])
        self.assertLess(h["c3"]["compression"]["net_hplus_count"], h["c3"]["utility"]["net_hplus_count"])
        self.assertLess(h["trap1"]["utility"]["net_hplus_count"], h["trap1"]["compression"]["net_hplus_count"])
        self.assertGreater(h["trap3"]["compression"]["net_hplus_count"], 0)
        self.assertLess(h["trap3"]["utility"]["net_hplus_count"], 0)
        # exec metric preserves the trap3 divergence
        self.assertGreater(h["trap3"]["compression"]["net_hplus_exec"], 0)
        self.assertLess(h["trap3"]["utility"]["net_hplus_exec"], 0)

    def test_trap3_mechanism(self):
        # the greedy 'abc' admission destroys the reusable 'ab' occurrences:
        # after rewrite the corpus has no 'ab' candidate left
        corp = [P("abcabc")] * 3
        t = v1.invent(corp, 1)
        self.assertEqual(["".join(a["body"]) for a in t["admissions"]], ["abc"])
        rewritten = [P("abcabc")] * 3
        rewritten = [v1.greedy_rewrite(("a", "b", "c"), "m1", p) for p in rewritten]
        pool = v1.candidate_pool(rewritten, t["library"])
        self.assertNotIn(("a", "b"), pool)

    def test_utl1_fail_closed(self):
        corp = [P(w) for w in FX["corpora"]["trap1"]["programs"]]
        hminus = [P(w) for w in FX["suites"]["trap1"]["hminus"]]
        res = v2.utility_library(corp, hminus, 1)
        self.assertEqual(len(res["library"]), 0)

    def test_utl1_deep_val_admits_m3(self):
        corp = [P(w) for w in FX["corpora"]["c3"]["programs"]]
        deep = [P(w) for w in FX["suites"]["c3"]["validation_deep"]]
        res = v2.utility_library(corp, deep, 1)
        comp = v1.invent(corp, 1)
        self.assertEqual(
            v2._expansion_signatures(res["library"], res["library_order"]),
            v2._expansion_signatures(comp["library"], comp["library_order"]),
        )

    def test_utl1_ablations_run(self):
        corp = [P(w) for w in FX["corpora"]["c3"]["programs"]]
        shallow = [P(w) for w in FX["suites"]["c3"]["validation_shallow"]]
        for mode in ("primitive", "stop"):
            res = v2.utility_library(corp, shallow, 1, mode=mode)
            self.assertIsInstance(res["library"], dict)

    def test_leakage_hostile(self):
        corp = [P(w) for w in FX["corpora"]["c3"]["programs"]]
        val = [P(w) for w in FX["suites"]["c3"]["validation_shallow"]]
        r = v2.hostile_hlk2(corp, val, None, None, 1)
        self.assertTrue(r["libraries_identical_under_poisoned_eval"])


class ExecMetric(unittest.TestCase):
    def test_dp_naive_battery(self):
        r = v2.hostile_hexec1()
        self.assertTrue(r["all_match"])
        for c in r["cases"]:
            self.assertEqual(c["dp"], c["naive"])

    def test_flagship_grid_negative_and_hminus(self):
        f = RESULT["v1_flagship_exec"]
        for row in f["rho_grid_rows"]:
            self.assertLess(row["net_hplus"], row["rho"])
            self.assertGreaterEqual(row["net_hminus"], 0)
        self.assertIsInstance(f["breakeven_rho"], int)
        self.assertGreater(f["breakeven_rho"], 128)
        self.assertLessEqual(f["breakeven_rho"], 1024)

    def test_exec_g0_independent_of_rho(self):
        w = P("abababab")
        self.assertEqual(v2.exec_burden(w, ["a", "b", "c"], {}, 1), v2.exec_burden(w, ["a", "b", "c"], {}, 7))


class Nulls(unittest.TestCase):
    def test_unrank_hostile(self):
        r = v2.hostile_hunr1()
        self.assertTrue(r["all_match"])

    def test_nulls_present(self):
        for key, ens in RESULT["nulls"].items():
            self.assertEqual(ens["n_seeds"], 200, key)
            self.assertIn("net_hplus_min", ens)

    def test_null_ranks_reported(self):
        for cid in ("c3", "c4", "c5"):
            self.assertIn("rank", RESULT["nulls_ranks"][cid])


class ReceiptValidation(unittest.TestCase):
    def test_terminal_green_and_checks(self):
        self.assertEqual(RESULT["terminal"], "GMI_833_E8_TRANCHE2_GREEN_AT_REGISTERED_SCOPE")
        failed = [k for k, val in RESULT["checks"].items() if not val]
        self.assertEqual(failed, [])

    def test_claim_ceiling_and_forbidden(self):
        self.assertEqual(
            RESULT["claim_ceiling"],
            "GMI_833_E8_TRANCHE2_DEPTH3_FORMATION__TIER_CONDITIONAL_COMPOUNDING__"
            "ADMISSION_RULE_ECONOMICS__EXEC_COST_ROBUST_AT_REGISTERED_SCOPE",
        )
        for bad in ("DEPTH_4_PLUS_FORMED", "COMPRESSION_GATE_DOMINATES", "UTILITY_GATE_DOMINATES"):
            self.assertIn(bad, RESULT["forbidden_promotions"])

    def test_freeze_pinned(self):
        self.assertEqual(RESULT["freeze_commits"][0], "c08112e3a287ff3f95cded5473cd504ec74726ef")
        self.assertEqual(RESULT["source_main"], FX["source_main"])


class OracleAgreement(unittest.TestCase):
    def test_oracle_all_ok(self):
        oracle = json.loads((ROOT / "ORACLE_RESULT_V2.json").read_text())
        self.assertTrue(oracle["all_ok"])
        failed = [k for k, val in oracle["checks"].items() if not val]
        self.assertEqual(failed, [])
        self.assertEqual(oracle["receipt_sha256"], hashlib.sha256((ROOT / "RESULT_V2.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
