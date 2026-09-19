# -*- coding: utf-8 -*-
"""Tests for the AJ15 flagship package.  Runs under `python3 -I -B` and `python3 -I -O -B`
(no `assert` is load-bearing: every check raises through unittest).

Covers: the B1 numbers from the functions themselves; every hostile is applicable AND
detected (from the receipts and by direct calls); the no-alarm case on the clean run;
custody refusal; S2 residual counts; all-words certification rejects a wrong machine;
exact nulls; the ladder refuses badge 5 on a bare flag and reaches it with a receipt;
no float anywhere in any receipt; the receipt carries the ceiling and forbidden set.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)



def load_module(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = load_module("aj15_flagship_v1")
B = load_module("independent_oracle_v1")
P = load_module("posthoc_adjudicate_v1")
L = load_module("apply_aj13_aj14_v1")


def receipt(name):
    return _load_json(os.path.join(HERE, name))


def walk_floats(x, path="$"):
    if isinstance(x, float):
        return [path]
    if isinstance(x, dict):
        return [p for k, v in x.items() for p in walk_floats(v, path + "." + str(k))]
    if isinstance(x, list):
        return [p for i, v in enumerate(x) for p in walk_floats(v, path + "[%d]" % i)]
    return []


class B1Universe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b1 = A.build_b1(4)
        cls.regimes = A.b1_regimes(cls.b1)
        cls.o = B.b1_atlas(4)

    def test_counts(self):
        self.assertEqual(len(self.b1["candidates"]), 260)
        self.assertEqual(len(self.b1["groups"]), 148)
        self.assertEqual(self.b1["pair_checks"], 33670)
        self.assertEqual(self.b1["equivalent_pairs"], 1624)
        self.assertEqual(["M%03d" % i for i in self.b1["front"]], ["M000", "M001", "M002", "M043", "M169"])
        self.assertEqual(self.b1["digest"], "09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed")

    def test_route_b_agrees(self):
        self.assertEqual(self.o["atlas_sha256"], self.b1["digest"])
        self.assertEqual(self.o["operational_classes"], 148)
        for t in A.B1_TASKS:
            self.assertEqual(self.o["regimes"][t]["exact_solvers"], self.regimes[t]["exact_solvers"])
            self.assertEqual(self.o["regimes"][t]["with_state_dependent_output"], self.regimes[t]["with_state_dependent_output"])

    def test_regime_outcomes(self):
        for t in ("identity", "not", "const0"):
            self.assertEqual((self.regimes[t]["exact_solvers"], self.regimes[t]["with_state_dependent_output"]), (29, 0))
        for t in ("delay1", "toggle"):
            self.assertEqual((self.regimes[t]["exact_solvers"], self.regimes[t]["with_state_dependent_output"]), (1, 1))

    def test_prediction_confirmed_and_falsifier_live(self):
        preds = A.CFG["regime_predictions_operational_vocabulary"]["B1"]
        self.assertEqual(A.verdict_b1(self.regimes, preds), [])
        bad = json.loads(json.dumps(preds))
        bad["delay1"]["predicted_exact_solvers_with_state_dependent_output"] = "NONE"
        self.assertTrue(A.verdict_b1(self.regimes, bad))


class B2Search(unittest.TestCase):
    def test_s2_residual_counts(self):
        self.assertEqual(B.s2_construct("identity")["residual_classes"], 1)
        self.assertEqual(B.s2_construct("delay1")["residual_classes"], 2)
        r = B.s2_construct("delay2")
        self.assertEqual((r["residual_classes"], r["terminal"], r["all_words_certified"]), (4, "RECOVERED", True))
        r3 = B.s2_construct("delay3")
        self.assertEqual((r3["residual_classes"], r3["terminal"]), (8, "NOT_RECOVERED_AT_SCOPE"))

    def test_certification_rejects_wrong_machine(self):
        wrong = tuple((0, 0) for _ in range(8))
        self.assertFalse(A.product_certify(wrong, "delay1"))
        self.assertFalse(B.certify_all_words(wrong, "delay1"))
        good = tuple((int(a), int(b)) for a, b in receipt("BLIND_OUTCOME_V1.json")["B2"]["regimes"]["delay2"]["machine"])
        self.assertTrue(A.product_certify(good, "delay2"))
        self.assertTrue(B.certify_all_words(good, "delay2"))
        self.assertFalse(B.certify_all_words(good, "delay1"))

    def test_budget_starved_search_reports_failure(self):
        r = A.s1_search("delay2", 1, 1, 1)
        self.assertEqual(r["terminal"], "NOT_RECOVERED_AT_SCOPE")
        self.assertEqual(r["evaluations"], 1)


class Nulls(unittest.TestCase):
    def test_n2_exact(self):
        b = receipt("BLIND_OUTCOME_V1.json")
        n2 = A.null_n2(b["B1"]["regimes"], b["B2"]["regimes"])
        self.assertEqual((n2["B1"]["chance"], n2["B2"]["chance"], n2["joint_chance"]), ("1/10", "1/8", "1/80"))

    def test_n1_nondegenerate_and_shared(self):
        a = A.null_n1(200, 20260919)
        o = B.null_n1(200, 20260919)
        self.assertTrue(a["strictly_between_0_and_1"])
        self.assertEqual(a["rate"], o["rate"])

    def test_n3_zero(self):
        self.assertEqual(A.null_n3(200, 20260919)["exact_delay2_solvers"], 0)


class Hostiles(unittest.TestCase):
    def test_all_recorded_hostiles_applicable_and_detected(self):
        seen = set()
        for name in ("BLIND_OUTCOME_V1.json", "POSTHOC_RESULT_V1.json", "LADDER_RESULT_V1.json"):
            for hid, h in receipt(name)["hostiles"].items():
                seen.add(hid)
                self.assertTrue(h["applicable"], hid)
                self.assertTrue(h["detected"], hid)
        self.assertEqual(seen, {"H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"})

    def test_custody_refusal(self):
        with self.assertRaises(RuntimeError):
            P.adjudicate(os.path.join(HERE, "NO_SUCH_BLIND_OUTCOME.json"))

    def test_scanner_validated_and_no_alarm(self):
        reg = _load_json(P.REGISTRY)
        audit = P.source_audit(P.build_vocabulary(reg))
        self.assertEqual(audit["violations"], 0)
        self.assertEqual(audit["planted_recall"], "8/8")
        self.assertTrue(audit["control_nonempty"])

    def test_k02_predicate_and_exclusions(self):
        pure = {"state_cells": 0, "reachable_states": 1, "reachable_state_dependent_output": False, "reachable_state_update": False}
        inert = {"state_cells": 1, "reachable_states": 2, "reachable_state_dependent_output": False, "reachable_state_update": True}
        live = {"state_cells": 1, "reachable_states": 2, "reachable_state_dependent_output": True, "reachable_state_update": True}
        self.assertFalse(P.k02_predicate(pure)["passes"])
        self.assertFalse(P.k02_predicate(inert)["passes"])
        self.assertTrue(P.k02_predicate(live)["passes"])
        self.assertTrue(P.k02_predicate(inert, drop_clause_2=True)["passes"])


class Ladder(unittest.TestCase):
    def test_badge5_needs_receipt(self):
        ev = receipt("LADDER_RESULT_V1.json")["aj14_evidence"]
        self.assertEqual(len(L.ladder(ev)), 4)
        flag = json.loads(json.dumps(ev))
        flag["DISCOVERY"]["novel_replication"] = "REPLICATED"
        self.assertEqual(len(L.ladder(flag)), 4)
        pos = json.loads(json.dumps(ev))
        pos["DISCOVERY"] = {"novel_replication": "REPLICATED", "replication_receipt": "x", "novel_form_claimed": True}
        self.assertEqual(len(L.ladder(pos)), 5)

    def test_aj13_six_and_absolute_refused(self):
        base = receipt("LADDER_RESULT_V1.json")["aj13_input"]
        self.assertEqual(L.aj13_audit(base)["criteria_satisfied"], 6)
        bad = json.loads(json.dumps(base))
        bad["requested_terminal"] = "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN"
        self.assertEqual(L.aj13_audit(bad)["terminal"], "STOPPING_RULE_NOT_SATISFIED")
        bad = json.loads(json.dumps(base))
        bad["operational_base"].append("NEURON")
        self.assertEqual(L.aj13_audit(bad)["criteria_satisfied"], 5)


class Receipts(unittest.TestCase):
    def test_no_floats(self):
        for name in ("BLIND_OUTCOME_V1.json", "ORACLE_RESULT_V1.json", "POSTHOC_RESULT_V1.json",
                     "LADDER_RESULT_V1.json", "LADDER_ORACLE_RESULT_V1.json", "RESULT_V1.json"):
            self.assertEqual(walk_floats(receipt(name)), [], name)

    def test_result_ceiling_and_forbidden(self):
        r = receipt("RESULT_V1.json")
        self.assertEqual(r["status"], "GREEN")
        self.assertEqual(r["claim_ceiling"], "AJ15_FLAGSHIP_END_TO_END_EXECUTED_WITH_FAMILY_REGISTRY_HIDDEN_AT_REGISTERED_FINITE_B1_AND_B2_SCOPES")
        for f in ("NAMED_FAMILY_RECOVERED", "REAL_SCALE_VALIDATION", "INDEPENDENT_TEAM_REPLICATION", "M5", "PREDICTED_SELECTED", "COMPLETE_GMI"):
            self.assertIn(f, r["forbidden_promotions"])
        self.assertFalse(r["results"]["FX-5"]["full_gmi_supported_now"])
        self.assertEqual(r["results"]["FX-3"]["honest_failure_terminal_exercised_on"], ["delay3"])


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != "-v"] + ["-v"])
