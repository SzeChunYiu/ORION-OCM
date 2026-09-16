#!/usr/bin/env python3
"""Tests for research/gmi-833-g0-grammar-growth-v1 (issue #897, parent #833)."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m = _load("g0_grammar_growth_v1", "g0_grammar_growth_v1.py")
o = _load("independent_oracle_v1", "independent_oracle_v1.py")


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = m.load_fixtures()
        cls.trace = m.invent(
            [tuple(p) for p in cls.fx["training_corpus"]],
            cls.fx["maintenance_charge_kappa_primary"],
        )
        cls.library = cls.trace["library"]
        cls.order = m.canonical_symbol_order(cls.trace["library_order"])

    # ---- fixtures ----------------------------------------------------------

    def test_fixture_schema_and_source(self):
        self.assertEqual(self.fx["schema"], "GMI833G0GrammarGrowthFrozenFixturesV1")
        self.assertEqual(self.fx["source_main"], m.SOURCE_MAIN)

    def test_heldout_disjoint_from_training(self):
        training = {tuple(p) for p in self.fx["training_corpus"]}
        subwords = set()
        for p in training:
            for i in range(len(p)):
                for j in range(i + 1, len(p) + 1):
                    subwords.add(p[i:j])
        for section in ("heldout_reuse_positive", "heldout_unrelated_control"):
            words = [tuple(w) for w in self.fx[section]]
            self.assertEqual(len(words), len(set(words)))
            for w in words:
                self.assertNotIn(w, training)
                self.assertNotIn(w, subwords)

    def test_unrelated_control_has_no_reusable_structure(self):
        for w in self.fx["heldout_unrelated_control"]:
            seen = set()
            for i in range(len(w) - 1):
                sub = tuple(w[i : i + 2])
                self.assertNotIn(sub, seen, msg=str(w))
                seen.add(sub)

    # ---- GRW-1 semantics ----------------------------------------------------

    def test_expansion_base(self):
        self.assertEqual(m.expand_word(("a", "b", "c"), {}), ("a", "b", "c"))
        self.assertEqual(m.expand_word(("m1",), {"m1": ("a", "b")}), ("a", "b"))

    def test_cycle_rejection_self_and_pair(self):
        with self.assertRaises(m.GrammarGrowthError) as cm:
            m.expand_word(("m1",), {"m1": ("m1", "a")})
        self.assertEqual(str(cm.exception), "RECURSIVE_LIBRARY_CYCLE")
        with self.assertRaises(m.GrammarGrowthError) as cm:
            m.expand_word(("mA",), {"mA": ("mB",), "mB": ("mA",)})
        self.assertEqual(str(cm.exception), "RECURSIVE_LIBRARY_CYCLE")

    def test_grw1_old_programs_unchanged_across_growth(self):
        probes = [
            ("a",), ("c", "b", "a"), ("a", "b", "a", "b", "c"), ("b", "c")
        ]
        for probe in probes:
            before = m.expand_word(probe, {})
            after = m.expand_word(probe, self.library)
            self.assertEqual(before, after)

    def test_grw1_probe_with_macros_protected_semantics(self):
        self.assertEqual(
            m.expand_word(("m2", "c"), self.library), ("a", "b", "a", "b", "c")
        )
        self.assertEqual(
            m.expand_word(("m1", "m1", "m1"), self.library), ("a", "b", "a", "b", "a", "b")
        )

    def test_grw1_failures_zero(self):
        self.assertEqual(self.trace["grw1_failures"], 0)

    # ---- INV-1 deterministic invention --------------------------------------

    def test_invention_first_admission_is_ab(self):
        first = self.trace["admissions"][0]
        self.assertEqual(first["body"], ["a", "b"])
        self.assertEqual(first["occurrences"], 11)
        self.assertEqual(first["gain"], 8)

    def test_invention_second_admission_is_recursive(self):
        second = self.trace["admissions"][1]
        self.assertEqual(second["body"], ["m1", "m1"])
        self.assertEqual(second["occurrences"], 4)
        self.assertEqual(second["gain"], 1)

    def test_invention_stops_by_saturation_at_depth_two(self):
        self.assertEqual(len(self.trace["admissions"]), 2)
        self.assertEqual(self.trace["stopped_by"], "NO_STRICTLY_BENEFICIAL_CANDIDATE")
        self.assertEqual(self.trace["depth_limit"], 23)  # derived D_reg = S_0

    def test_invention_final_corpus_exact(self):
        self.assertEqual(
            self.trace["corpus_final"],
            [["m1", "c", "m1"], ["m2"], ["m2"], ["m2"], ["m2"], ["m1"]],
        )

    def test_invention_deterministic_repeat(self):
        again = m.invent(
            [tuple(p) for p in self.fx["training_corpus"]],
            self.fx["maintenance_charge_kappa_primary"],
        )
        self.assertEqual(
            json.dumps(again, sort_keys=True),
            json.dumps(self.trace, sort_keys=True),
        )

    def test_rec1_witness(self):
        self.assertTrue(m.is_acyclic(self.library))
        self.assertEqual(m.expand_word(("m2",), self.library), ("a", "b", "a", "b"))

    # ---- burden: DP equals naive enumeration --------------------------------

    def test_burden_dp_equals_naive_on_all_registered_targets(self):
        exp_base = m.symbol_expansions(["a", "b", "c"], {})
        exp_full = m.symbol_expansions(self.order, self.library)
        for section in ("heldout_reuse_positive", "heldout_unrelated_control"):
            for w in self.fx[section]:
                w = tuple(w)
                bd, _ = m.burden_dp(w, ["a", "b", "c"], exp_base)
                bn, _ = m.burden_naive(w, ["a", "b", "c"], {})
                self.assertEqual(bd, bn, msg="G0 " + str(w))
                bd, _ = m.burden_dp(w, self.order, exp_full)
                bn, _ = m.burden_naive(w, self.order, self.library)
                self.assertEqual(bd, bn, msg="G2 " + str(w))

    def test_burden_dp_equals_naive_exhaustive_short_words(self):
        exp_full = m.symbol_expansions(self.order, self.library)
        words = []
        for ln in range(1, 5):
            stack = [()]
            for _ in range(ln):
                stack = [p + (s,) for p in stack for s in ("a", "b", "c")]
            words.extend(stack)
        for w in words:
            bd, _ = m.burden_dp(w, self.order, exp_full)
            bn, _ = m.burden_naive(w, self.order, self.library)
            self.assertEqual(bd, bn, msg=str(w))

    def test_hand_derived_burden_anchors(self):
        exp_base = m.symbol_expansions(["a", "b", "c"], {})
        exp_full = m.symbol_expansions(self.order, self.library)
        b, hit = m.burden_dp(("a", "b", "a", "b", "a", "b", "a", "b"), ["a", "b", "c"], exp_base)
        self.assertEqual((b, list(hit)), (4100, ["a", "b", "a", "b", "a", "b", "a", "b"]))
        b, hit = m.burden_dp(("a", "b", "a", "b", "a", "b", "a", "b"), self.order, exp_full)
        self.assertEqual((b, list(hit)), (30, ["m2", "m2"]))
        b, hit = m.burden_dp(("c", "a", "b", "a", "b"), self.order, exp_full)
        self.assertEqual((b, list(hit)), (20, ["c", "m2"]))

    # ---- HLD-1 held-out verdicts ---------------------------------------------

    def test_k_total_charged(self):
        self.assertEqual(m.k_total(self.library, 1), 6)

    def test_hplus_strict_net_reduction(self):
        v = m.heldout_verdict(
            [tuple(w) for w in self.fx["heldout_reuse_positive"]],
            self.library, self.trace["library_order"], 1,
        )
        self.assertLess(v["net"], 0)
        self.assertEqual(v["n_targets"], 12)

    def test_hminus_regression_preserved(self):
        v = m.heldout_verdict(
            [tuple(w) for w in self.fx["heldout_unrelated_control"]],
            self.library, self.trace["library_order"], 1,
        )
        self.assertGreater(v["net"], 0)
        for row in v["targets"]:
            self.assertGreaterEqual(row["delta_burden"], 0)

    # ---- THR-1 threshold ------------------------------------------------------

    def test_threshold_identities(self):
        v = m.heldout_verdict(
            [tuple(w) for w in self.fx["heldout_reuse_positive"]],
            self.library, self.trace["library_order"], 1,
        )
        thr = m.threshold_check(v, self.library, 1)
        self.assertTrue(thr["all_macros_hold_marginal"])
        self.assertTrue(thr["aggregate_holds"])
        for r in thr["per_macro"]:
            self.assertGreaterEqual(r["H_eff"], 4)

    # ---- NULL-1 ---------------------------------------------------------------

    def test_null_ensemble_reproducible(self):
        n1 = m.null_ensemble(
            [tuple(p) for p in self.fx["training_corpus"]], 2,
            [0, 1, 2, 3], self.fx["heldout_reuse_positive"],
            self.fx["heldout_unrelated_control"], 1,
        )
        n2 = m.null_ensemble(
            [tuple(p) for p in self.fx["training_corpus"]], 2,
            [0, 1, 2, 3], self.fx["heldout_reuse_positive"],
            self.fx["heldout_unrelated_control"], 1,
        )
        self.assertEqual(json.dumps(n1, sort_keys=True), json.dumps(n2, sort_keys=True))
        self.assertEqual(n1["pool_size"], 5)
        self.assertEqual(
            n1["pool_bodies"],
            [["a", "b"], ["a", "b", "a"], ["a", "b", "a", "b"], ["b", "a"], ["b", "a", "b"]],
        )

    def test_null_combo_hash(self):
        self.assertEqual(m.null_combo_index(0, 5, 2), (1 * 2654435761 % 2 ** 32) % 10)
        self.assertEqual(m.null_combo_index(199, 5, 2), (200 * 2654435761 % 2 ** 32) % 10)

    # ---- hostiles -------------------------------------------------------------

    def test_hostile_cycle(self):
        h = m.hostile_cycle()
        self.assertTrue(h["all_cycles_rejected"])
        self.assertTrue(h["grammar_unchanged"])

    def test_hostile_definition_charge(self):
        h = m.hostile_uncharged_definition(1)
        self.assertTrue(h["charge_load_bearing"])
        self.assertEqual(h["registered_admissions"], 0)

    def test_hostile_maintenance_charge(self):
        h = m.hostile_uncharged_maintenance()
        self.assertEqual(h["admissions_kappa0"], 2)
        self.assertEqual(h["admissions_kappa1"], 1)
        self.assertTrue(h["maintenance_charge_load_bearing"])

    def test_hostile_zero_gain(self):
        h = m.hostile_zero_gain(1)
        self.assertTrue(h["second_stage_gain_exactly_zero"])
        self.assertEqual(h["admissions"], 1)

    def test_hostile_semantic_rewrite(self):
        self.assertTrue(m.hostile_semantic_rewrite()["corrupt_rewrite_detected"])

    def test_hostile_heldout_hash(self):
        self.assertTrue(m.hostile_heldout_hash(self.fx)["tamper_detected"])

    def test_hostile_leakage(self):
        self.assertTrue(
            m.hostile_leakage(self.fx, 1)["library_identical_under_poisoned_heldouts"]
        )

    # ---- kappa ablation --------------------------------------------------------

    def test_kappa_ablation_formation_boundary(self):
        abl = m.kappa_ablation(
            [0, 1, 2, 3],
            self.fx["training_corpus"],
            self.fx["heldout_reuse_positive"],
            self.fx["heldout_unrelated_control"],
        )
        formed = {r["kappa"]: r["m2_formed"] for r in abl["rows"]}
        self.assertTrue(formed[0] and formed[1])
        self.assertFalse(formed[2] and formed[3])

    # ---- receipt, oracle, determinism -------------------------------------------

    def test_receipt_green(self):
        r = m.build_receipt()
        for k, v in sorted(r["checks"].items()):
            self.assertTrue(v, msg=k)
        self.assertEqual(r["terminal"], m.TERMINAL_GREEN)
        self.assertEqual(r["claim_ceiling"], m.CLAIM_CEILING)
        self.assertEqual(r["freeze_commit"], m.FREEZE_COMMIT)

    def test_receipt_deterministic(self):
        a = json.dumps(m.build_receipt(), sort_keys=True)
        b = json.dumps(m.build_receipt(), sort_keys=True)
        self.assertEqual(a, b)

    def test_module_subprocess_normal_optimized_equal(self):
        out1 = subprocess.check_output(
            [sys.executable, "-I", "-B", str(ROOT / "g0_grammar_growth_v1.py")]
        )
        out2 = subprocess.check_output(
            [sys.executable, "-I", "-O", "-B", str(ROOT / "g0_grammar_growth_v1.py")]
        )
        self.assertEqual(out1, out2)

    def test_oracle_agrees_if_receipt_committed(self):
        result_path = ROOT / "RESULT_V1.json"
        if not result_path.exists():
            self.skipTest("RESULT_V1.json not yet committed")
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "independent_oracle_v1.py")],
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr.decode()[-2000:])
        out = json.loads(proc.stdout.decode())
        self.assertTrue(out["all_ok"], msg=str(out["mismatches"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
