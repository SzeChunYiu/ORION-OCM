#!/usr/bin/env python3
"""Tests for the real-scale four-family tranche.  CI runs this with -I -B.

Covers: freeze custody (manifest pins + git absence assertions when git is
available), vocabulary screen (lexical + the merged #855 A2 semantic layer
with positive/negative controls), regeneration determinism, CI-scope outcome
replay equality, oracle agreement, zero-arbitrary-constants audit, adjudicator
bijection/hostility, and receipt validation.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import battery_realscale_v1 as bat
import search_realscale_v1 as S

DENYLIST_ENTRIES = [
    "automaton", "automata", "regression", "regressor", "classifier",
    "classification", "glm", "kernel", "basis function", "nearest neighbor",
    "exemplar memory", "perceptron", "neural net", "backprop",
    "decision tree", "transformer", "attention head", "lstm", "gru",
    "recurrent net", "state space model", "mixture of experts",
]
SEARCH_VISIBLE_FILES = [
    "battery_realscale_v1.py", "search_realscale_v1.py",
    "independent_oracle_v1.py", "freeze_predictions_v1.py",
]
DERIVATION_WHITELIST = {
    # every integer literal in the search-visible sources maps to FREEZE
    # D-1..D-14 or the F1/F5b tables; anything else is an arbitrary constant.
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 26,
    27, 31, 32, 33, 34, 52, 63, 64, 71, 81, 100, 128, 200, 966, 1366, 2048, 4096,
    -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -16, -26, -52, -63, -64,
}


def load_audit_core():
    path = ROOT / "research" / "gmi-833-no-smuggling-audit-v1" / "audit_core_v1.py"
    spec = importlib.util.spec_from_file_location("audit_core_v1", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestVocabularyScreen(unittest.TestCase):
    def test_lexical_denylist_clean_on_search_visible_files(self):
        for name in SEARCH_VISIBLE_FILES:
            text = (HERE / name).read_text().lower()
            for entry in DENYLIST_ENTRIES:
                self.assertNotIn(entry, text, f"{entry} leaked in {name}")

    def test_a2_semantic_screen_with_controls(self):
        mod = load_audit_core()
        base = {
            "types": "numeric", "state_access": "none",
            "addressability": "all_coordinates",
            "content_dependent_routing": False, "parameter_sharing": "none",
            "recurrence": False, "stochasticity": "none",
            "verifier_access": "none", "resource_class": "compute",
        }
        prims = [
            {"id": "ADD", "features": {**base, "arity": 2, "locality": "elementwise"}},
            {"id": "MUL", "features": {**base, "arity": 2, "locality": "pairwise_products"}},
            {"id": "GE_c", "features": {**base, "arity": 1, "locality": "order_test"}},
            {"id": "NEG", "features": {**base, "arity": 1, "locality": "sign_flip"}},
            {"id": "DELAY_CELL", "features": {
                **base, "arity": 1, "locality": "stream",
                "state_access": "persistent", "recurrence": True}},
            {"id": "INDEXED_PARAMETER_READ", "features": {
                **base, "arity": 1, "locality": "cell_lookup",
                "addressability": "cell_indexed", "resource_class": "storage"}},
        ]
        fingerprints = [
            {"name": "persistent_state_machine",
             "required_features": {"state_access": "persistent", "recurrence": True,
                                   "arity": 2}},
            {"name": "shared_coefficient_score",
             "required_features": {"parameter_sharing": "shared_coefficients",
                                   "arity": 2, "state_access": "none"}},
            {"name": "monotone_link_composition",
             "required_features": {"parameter_sharing": "shared_coefficients",
                                   "locality": "order_test"}},
            {"name": "lifted_interaction",
             "required_features": {"parameter_sharing": "shared_coefficients",
                                   "locality": "pairwise_products", "arity": 2}},
        ]
        neg = mod.semantic({"primitives": prims, "target_fingerprints": fingerprints})
        self.assertEqual(neg["terminal"], "CLEAN_AT_REGISTERED_AUDIT_SCOPE",
                         msg=f"negative control flagged: {neg}")
        # positive controls: planted family-shaped macro primitives MUST flag
        hostile = prims + [
            {"id": "MACRO_SHARED_DOT", "features": {
                **base, "arity": 2, "locality": "elementwise",
                "parameter_sharing": "shared_coefficients"}},
            {"id": "MACRO_STATE_COMPOSITE", "features": {
                **base, "arity": 2, "locality": "stream",
                "state_access": "persistent", "recurrence": True}},
            {"id": "MACRO_MONO_LINK", "features": {
                **base, "arity": 1, "locality": "order_test",
                "parameter_sharing": "shared_coefficients"}},
        ]
        pos = mod.semantic({"primitives": hostile, "target_fingerprints": fingerprints})
        self.assertEqual(pos["terminal"], "SEMANTIC_MACRO_LEAKAGE")
        flagged = {f["primitive"] for f in pos["findings"]}
        self.assertIn("MACRO_SHARED_DOT", flagged)
        self.assertIn("MACRO_STATE_COMPOSITE", flagged)
        self.assertIn("MACRO_MONO_LINK", flagged)
        # lexical layer with the package denylist on identifier surface
        lex = mod.lexical({
            "search_visible_identifiers": [
                "add", "mul", "ge_c", "neg", "delay_cell",
                "indexed_parameter_read", "s_add", "s_lift", "s_mono"],
            "denylist": {"version": "RSF1-DL1", "entries": DENYLIST_ENTRIES},
        })
        self.assertEqual(lex["terminal"], "CLEAN_AT_REGISTERED_AUDIT_SCOPE")
        lex_bad = mod.lexical({
            "search_visible_identifiers": ["kernel_dot_macro"],
            "denylist": {"version": "RSF1-DL1", "entries": DENYLIST_ENTRIES},
        })
        self.assertEqual(lex_bad["terminal"], "LEXICAL_LEAKAGE")


class TestZeroArbitraryConstants(unittest.TestCase):
    def test_integer_literals_derived(self):
        pattern = re.compile(r"(?<![\w.])-?\d+(?![\w.])")
        for name in SEARCH_VISIBLE_FILES:
            src = (HERE / name).read_text()
            tree = ast.parse(src)
            lits = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, int):
                    lits.add(node.value)
                if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) \
                        and isinstance(node.operand, ast.Constant) \
                        and isinstance(node.operand.value, int):
                    lits.add(-node.operand.value)
            extra = lits - DERIVATION_WHITELIST
            self.assertFalse(extra, f"non-derived integer literals in {name}: {extra}")


class TestBatteryDeterminism(unittest.TestCase):
    def test_registry_regeneration_byte_identical(self):
        reg = bat.registry()
        disk = json.loads((HERE / "BATTERY_REGISTRY_V1.json").read_text())
        self.assertEqual(json.dumps(reg, sort_keys=True, indent=1) + "\n",
                         json.dumps(disk, sort_keys=True, indent=1) + "\n")

    def test_debruijn_complete(self):
        db = bat.de_bruijn(12)
        grams = set(tuple(db[i:i + 12]) for i in range(len(db)))
        self.assertEqual(len(db), 4096)
        self.assertEqual(len(grams), 4096)

    def test_dyadic_arithmetic_hostiles(self):
        a = bat.Dyadic(3, -7)
        b = bat.Dyadic(-5, -4)
        self.assertEqual((a + b).fraction(), a.fraction() + b.fraction())
        self.assertEqual((a * b).fraction(), a.fraction() * b.fraction())
        self.assertTrue(b < a)
        with self.assertRaises(ValueError):
            bat.Dyadic(1, 0).__ge__("x")

    def test_materialization_hostiles(self):
        reg = bat.registry()
        t = next(t for t in reg["tasks"] if t["id"] == "AFF_ANCHOR_0")
        d = bat.materialize(t)
        self.assertEqual(len(d["X_train"]), 2048)
        bad = dict(t)
        bad["gen"] = "nonsense"
        with self.assertRaises(ValueError):
            bat.materialize(bad)


class TestSearchExactness(unittest.TestCase):
    def test_exact_ls_recovers_noise_free_affine(self):
        reg = bat.registry()
        t = next(t for t in reg["tasks"] if t["id"] == "AFF_NOISE_0")
        self.assertIsNone(t["sigma_exp"])
        data = bat.materialize(t)
        iface = S.Interface(data, 0)
        fit = S.fit_stratum(iface, "S_ADD")
        risk = S.risk_of(iface, fit["pred_te"])
        self.assertEqual(risk, 0)

    def test_band_values_derived(self):
        b = S.make_band({"binary": False, "sigma_exp": -6})
        self.assertEqual(b["band"], Fraction(1, 1 << 16))
        b0 = S.make_band({"binary": False, "sigma_exp": None})
        self.assertEqual(b0["mode"], "zero")
        bb = S.make_band({"binary": True, "eps_exp": -6})
        self.assertEqual(bb["mode"], "sqrt4")
        self.assertEqual(bb["four_q"], Fraction(4) * (Fraction(1, 64) * Fraction(63, 64) / 2048))


class TestOutcomeReplay(unittest.TestCase):
    def test_ci_scope_replay_matches_committed_outcome(self):
        rows = S.run_scope("ci")
        committed = json.loads((HERE / "OUTCOME_CI_V1.json").read_text())
        self.assertEqual(committed["scope"], "ci")
        self.assertEqual(json.dumps({"rows": rows}, sort_keys=True),
                         json.dumps({"rows": committed["rows"]}, sort_keys=True))


class TestOracleAgreement(unittest.TestCase):
    def test_oracle_agrees_on_scope(self):
        sys.path.insert(0, str(HERE))
        import independent_oracle_v1 as O
        scope = json.loads((HERE / "ORACLE_SCOPE_V1.json").read_text())["ids"]
        pred = {p["id"]: p for p in
                json.loads((HERE / "FROZEN_PREDICTIONS_V1.json").read_text())["rows"]}
        mismatches = []
        for tid in scope:
            task = next(t for t in bat.registry()["tasks"] if t["id"] == tid)
            noiseless = dict(task)
            noiseless["sigma_exp"] = None
            noiseless["eps_exp"] = None
            ch = O.oracle_champion(noiseless)
            p = pred[tid]
            same_stratum = ch["champion"].split("#")[0] == p["predicted_stratum"]
            if not same_stratum:
                mismatches.append({"id": tid, "oracle": ch["champion"],
                                   "primary_prediction": p["predicted_champion"]})
        self.assertEqual(mismatches, [],
                         msg=f"oracle disagreements: {mismatches[:5]}")


class TestAdjudicatorContracts(unittest.TestCase):
    def test_clause_bijection_and_hostility(self):
        doc = json.loads((HERE / "POSTHOC_RESULT_V1.json").read_text())
        for key, adj in doc["adjudications"].items():
            self.assertEqual(len(adj["clause_map"]), len(adj["checks"]),
                             f"bijection drift in {key}")
            for clause, check in adj["clause_map"].items():
                self.assertIn(check, adj["checks"])
        self.assertTrue(doc["hostility"]["source_self_scan_clean"])
        self.assertTrue(doc["hostility"]["reversed_row_order_verdicts_invariant"])

    def test_receipt_validation(self):
        r = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(r["claim_ceiling"],
                         "GMI_833_H_REALSECALE_FOUR_FAMILY_MORPHOLOGIES_RECOVERED_NEUTRALLY_WITH_MEASURED_BOUNDARIES_AT_REGISTERED_EXACTDYADIC_SCOPE")
        for bad in ("ALL_KNOWN_FAMILIES_RECOVERED", "REAL_SCALE_VALIDATION_COMPLETE",
                    "SMOOTH_LINK_TIER_MEMBERSHIP", "FLOAT64_REQUIRED_FOR_RECOVERY"):
            self.assertIn(bad, r["forbidden_promotions"])
        failed = [k for k, v in r["checks"].items() if not v]
        self.assertEqual(failed, [])


class TestFreezeCustody(unittest.TestCase):
    def test_manifest_pins_and_custody(self):
        man = json.loads((HERE / "MANIFEST_V1.json").read_text())
        for rel, sha in man["pins"].items():
            data = (HERE / rel).read_bytes()
            import hashlib
            self.assertEqual(hashlib.sha256(data).hexdigest(), sha,
                             f"pin drift for {rel}")
        if man.get("freeze_commit") and (ROOT / ".git").exists():
            for commit, absent in man["custody_absence"].items():
                for path in absent:
                    res = subprocess.run(
                        ["/usr/bin/git", "-C", str(ROOT), "cat-file", "-e",
                         f"{commit}:{path}"],
                        capture_output=True)
                    self.assertNotEqual(res.returncode, 0,
                                        f"post-freeze artifact existed at {commit}: {path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
