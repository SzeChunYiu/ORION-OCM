"""Tests for IMB-v1 (Z11).

Runs under `python3 -I -B` and `python3 -I -O -B`; every check is a unittest
assertion, never a bare `assert`. The two route receipts are compared without
re-running either route; small unit checks exercise both routes' primitives.
"""
import hashlib
import io
import json
import os
import sys
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imb_benchmark_v1 as A                 # noqa: E402
import independent_imb_oracle_v1 as B        # noqa: E402

FREEZE_SHA256 = "1f83b91eb831c76aaed7a5ebc745f5e9458828c5749fd7a772316385851afc95"
AMEND_SHA256 = "e20954f02021c0b62ac6abee9440351ae58d267ad0e49714f9aab0220585693f"


def load(name):
    with io.open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


def floats(obj, path="$"):
    if isinstance(obj, float):
        return [path]
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += floats(v, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += floats(v, path + "[%d]" % i)
    return out


class Custody(unittest.TestCase):
    def test_freeze_bytes(self):
        with io.open(os.path.join(HERE, "FREEZE_V1.md"), "rb") as fh:
            raw = fh.read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), FREEZE_SHA256)
        self.assertIn(b"No neighboring row is earned here.", raw)
        with io.open(os.path.join(HERE, "FREEZE_V1_AMENDMENT_1.md"), "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), AMEND_SHA256)

    def test_commitment(self):
        self.assertEqual(hashlib.sha256(A.HIDDEN_PREIMAGE.encode("utf-8")).hexdigest(), A.HIDDEN_COMMITMENT)
        self.assertEqual(A.HIDDEN_COMMITMENT, B.COMMITMENT)
        self.assertEqual(load("CASES_V1.json")["hidden_seed_preimage"], A.HIDDEN_PREIMAGE)

    def test_no_floats(self):
        self.assertEqual(floats(load("RESULT_V1.json")), [])
        self.assertEqual(floats(load("ORACLE_RESULT_V1.json")), [])
        self.assertEqual(floats(load("FAILED_PREDICTION_REGISTER_V1.json")), [])
        self.assertNotIn("timing", json.dumps(load("RESULT_V1.json")))


class TwoRoutes(unittest.TestCase):
    def setUp(self):
        self.a = load("RESULT_V1.json")
        self.b = load("ORACLE_RESULT_V1.json")

    def test_routes_and_sha(self):
        self.assertEqual(self.a["route"], "A")
        self.assertEqual(self.b["route"], "B")
        self.assertFalse(self.b["imports_route_A"])
        self.assertEqual(self.a["case_set_sha256"], self.b["case_set_sha256"])
        self.assertEqual(self.a["case_set_sha256"], load("CASES_V1.json")["case_set_sha256"])
        self.assertEqual(self.a["case_set_sha256"], load("PREDICTIONS_V1.json")["case_set_sha256"])

    def test_every_score_equal(self):
        self.assertEqual(self.b["score_mismatches"], [])
        self.assertEqual(self.b["class_score_mismatches"], [])
        for tid in self.a["scores"]:
            self.assertEqual(self.a["scores"][tid], self.b["scores"][tid], tid)
        self.assertEqual(self.b["truths_equal"], 519)
        self.assertEqual(self.b["n_cases"], 519)

    def test_oracle_checks_all_green(self):
        self.assertEqual(self.b["verdict"], "GREEN")
        for k, v in sorted(self.b["checks"].items()):
            self.assertTrue(v, k)
        self.assertEqual(self.b["distinct_laws_enumerated"], self.a["enumeration"]["n_laws"])

    def test_scrambled_control_equal(self):
        sa = self.a["scrambled_truth_control"]
        sb = self.b["scrambled"]
        self.assertEqual(sa["literal_all_cells"]["class_choice"], sb["literal"])
        self.assertEqual(sa["informative_cells"]["class_choice"], sb["informative"])
        self.assertEqual(sa["informative_cells"]["cells"], sb["informative_cells"])
        self.assertEqual(sb["truth_reader_informative"], "1")


class Content(unittest.TestCase):
    def setUp(self):
        self.a = load("RESULT_V1.json")
        self.reg = load("FAILED_PREDICTION_REGISTER_V1.json")

    def test_gates_and_verdict(self):
        self.assertEqual(self.a["verdict"], "GREEN")
        for k, v in sorted(self.a["gates"].items()):
            self.assertTrue(v, k)
        self.assertEqual(self.a["case_census"], {"C1_LADDER": 135, "C2_TWO_LEVEL_IID": 189, "C3_ALPHABET": 81,
                                                 "C4_EMPIRICAL_STREAM": 45, "C5_HIDDEN": 60,
                                                 "C6_NEGATIVE_CONTROL": 9, "total": 519})

    def test_headline_scores(self):
        s = self.a["scores"]
        g = s["T_GMI_IC1"]
        self.assertEqual((g["class_choice"]["score"], g["class_choice"]["hits"], g["class_choice"]["misses"],
                          g["class_choice"]["abstains"]), ("1", 11380, 0, 155))
        for f in ("thresholds", "frontier", "failure_modes"):
            self.assertEqual(g[f]["score"], "1", f)
        self.assertEqual((g["profile"]["covered"], g["profile"]["cells"]), (1250, 1250))
        self.assertTrue(g["calibration"]["calibrated"])
        self.assertEqual(s["T_DECLARED"], g)
        self.assertEqual(s["T_HALF"]["class_choice"]["score"], "2111/2307")
        self.assertFalse(s["T_HALF"]["calibration"]["calibrated"])
        self.assertEqual(s["T_LEVEL"]["class_choice"]["score"], "11311/11535")
        self.assertFalse(s["T_LEVEL"]["calibration"]["calibrated"])
        self.assertEqual(s["T_MDL"]["class_choice"]["score"], "1157/3845")
        self.assertEqual(s["T_OCCAM_HARD"]["class_choice"]["score"], "8341/11535")
        self.assertEqual(s["T_SRM"]["class_choice"]["score"], "7819/11535")
        self.assertEqual(s["T_SATISFICE"]["class_choice"]["score"], "488/769")
        ab = s["T_ABSTAIN"]
        for f in ("class_choice", "thresholds", "frontier", "failure_modes"):
            self.assertEqual((ab[f]["hits"], ab[f]["misses"]), (0, 0), f)

    def test_null_and_controls(self):
        n = self.a["null"]
        self.assertTrue(n["all_fields_beaten"])
        self.assertEqual(n["best"], {"class_choice": "3071/11535", "thresholds": "20/731",
                                     "frontier": "157/519", "failure_modes": "27/125"})
        d = self.a["discrimination"]
        self.assertEqual(d["T_DECLARED_vs_T_GMI_IC1_disagreements"], 0)
        self.assertEqual(d["T_DECLARED_status"], "NON_DISCRIMINATING")
        self.assertEqual(d["cases"], 517)
        sc = self.a["scrambled_truth_control"]
        self.assertEqual(sc["governing_form"], "INFORMATIVE_CELLS_AMENDMENT_1")
        self.assertFalse(sc["s6_instruction_followed"])
        self.assertEqual(sc["audit_shape_disclosed"], "POST_HOC_SUSPECT")
        self.assertFalse(sc["literal_all_cells"]["T_GMI_IC1_at_or_below_best_null"])
        self.assertEqual(sc["informative_cells"]["class_choice"]["T_GMI_IC1"], "0")
        self.assertEqual(sc["informative_cells"]["cells"], 1536)
        for t, dg in sc["leakage_alarm_diagnosis"].items():
            self.assertTrue(dg["price_blind"], t)
            self.assertEqual(dg["classification"], "FALSE_ALARM_ON_CLEAN_THEORY", t)
        self.assertNotIn("T_GMI_IC1", sc["leakage_alarms"])

    def test_hostiles(self):
        h = self.a["hostiles"]
        self.assertEqual(sorted(h), ["HZ%d" % i for i in range(1, 9)])
        for k, v in h.items():
            self.assertTrue(v["applicable"], k)
            self.assertTrue(v["detected"], k)
        self.assertEqual(h["HZ1"]["T_PEEK_scrambled_score_leaky_harness"], "1")
        self.assertEqual(h["HZ8"]["T_LEVEL_C1_coverage_gamma_1"], "21/25")

    def test_register_matches_receipt(self):
        fp = self.a["frozen_predictions"]
        by_id = dict((e["id"], e) for e in self.reg["entries"])
        for bid in ("B1", "B2", "B3", "B4", "B5", "B6"):
            self.assertEqual(by_id[bid]["verdict"], fp[bid]["verdict"], bid)
        self.assertEqual(self.reg["misses"], ["B3"])
        self.assertEqual(fp["B3"]["evidence"]["T_HALF_C2_q_ne_half"]["threshold_miss_cases"], 144)
        self.assertEqual(fp["B3"]["evidence"]["T_HALF_C3_A_ne_2"]["threshold_miss_cases"], 48)
        self.assertIn("attributed_stage", by_id["B3"])
        self.assertIn("not scored", by_id["B3"]["post_hoc_note"])
        self.assertEqual(fp["B2"]["evidence"]["stateless_cells_equal"], "9/9")
        self.assertEqual(fp["B2"]["evidence"]["b1_delay2_covered"], "3/3")


class Primitives(unittest.TestCase):
    def test_frontier_two_routes_agree(self):
        grid = [F(k, 8) for k in range(9)]
        n = 0
        for e0 in grid:
            for e1 in grid:
                for e2 in grid:
                    E = {0: e0, 1: e1, 2: e2}
                    self.assertEqual(A.frontier_set(E), B.frontier_by_halflines(E), E)
                    n += 1
        self.assertEqual(n, 729)
        self.assertEqual(B.frontier_by_halflines({0: F(0), 1: F(0), 2: F(0)}), frozenset([0]))
        self.assertEqual(B.frontier_by_halflines({0: F(1), 1: F(1, 2), 2: F(0)}), frozenset([0, 2]))
        self.assertEqual(B.frontier_by_halflines({0: F(1), 1: F(1, 4), 2: F(0)}), frozenset([0, 1, 2]))

    def test_argmin_ties(self):
        E = {0: F(1, 2), 1: F(0)}
        self.assertEqual(A.argmin_set(E, F(1, 2)), frozenset([0, 1]))
        self.assertEqual(B.argmin_set(E, F(1, 2)), frozenset([0, 1]))
        self.assertEqual(A.argmin_set(E, F(1, 4)), frozenset([1]))
        self.assertEqual(B.argmin_set(E, F(3, 4)), frozenset([0]))

    def test_schema_rejects_missing_field(self):
        spec = {"universe": {"levels": [0, 1], "modes": [0, 1]}, "prices": ["0", "1/16"], "accounting": {"eta": "1"}}
        rec = {"profile": {0: ("POINT", F(0)), 1: ("POINT", F(0))}, "thresholds": {1: ("POINT", F(0))},
               "frontier": ("SET", frozenset([0])), "selection_by_price": {F(0): ("SET", frozenset([0, 1])), F(1, 16): ("SET", frozenset([0]))},
               "failure_modes": {0: ("SET", frozenset()), 1: ("SET", frozenset())}}
        self.assertTrue(A.validate_record(rec, spec))
        self.assertTrue(B.valid(rec, spec))
        bad = dict(rec)
        del bad["frontier"]
        self.assertFalse(A.validate_record(bad, spec))
        self.assertFalse(B.valid(bad, spec))

    def test_registered_floors_by_both_routes(self):
        A.build_signatures()
        w, D = A.law_weights({"kind": "UNIFORM"})
        self.assertEqual(A.ladder_floors(w, D), A.REGISTERED_BASE_FLOORS)
        self.assertEqual(B.ladder_floors(B.law_probs({"kind": "UNIFORM"})), A.REGISTERED_BASE_FLOORS)
        p2 = B.ladder_floors(B.law_probs({"kind": "PERIOD2"}))
        self.assertEqual((p2[(0, 1)], p2[(0, 2)], p2[(1, 2)]), (F(1, 2), F(0), F(0)))
        self.assertEqual(B.alphabet_floor(3), F(2, 3))
        self.assertEqual(A.alphabet_R0(4), F(3, 4))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != "-v"] + ["-v"])
