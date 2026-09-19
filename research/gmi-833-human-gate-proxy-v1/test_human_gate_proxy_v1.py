#!/usr/bin/env python3
"""Tests for gmi-833-human-gate-proxy-v1.  Runnable under -B and -O -B; no
check uses `assert`, so -O cannot make a test vacuous.  Stdlib only."""
import importlib.util
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = load("hgp_a", "human_gate_proxy_v1.py")
B = load("hgp_b", "independent_oracle_v1.py")
ZA = load("z9a", "z9_oracle_a_v1.py")
ZB = load("z9b", "z9_oracle_b_v1.py")


class Freeze(unittest.TestCase):
    def test_forty_rows_and_ids(self):
        rows = A.freeze_rows()
        self.assertEqual(len(rows), 40)
        self.assertEqual(len({r["old"] for r in rows}), 40)
        rows_b, briefs_b, pins_b = B.freeze_tables()
        self.assertEqual([r["old"] for r in rows], [r[2] for r in rows_b])
        self.assertEqual(len(A.freeze_brief_digests()), 18)
        self.assertEqual({k: v[0] for k, v in A.freeze_brief_digests().items()}, briefs_b)
        self.assertEqual(len(A.freeze_artifact_pins()), 43)
        self.assertEqual(A.freeze_artifact_pins(), pins_b)

    def test_briefs_match_digests(self):
        for b, (sha, size) in A.freeze_brief_digests().items():
            self.assertEqual(A.sha256_file(os.path.join(HERE, b)), sha, b)
            self.assertEqual(os.path.getsize(os.path.join(HERE, b)), size, b)

    def test_old_strings_unique_in_snapshots(self):
        rows = A.freeze_rows()
        for r in rows:
            body = open(os.path.join(HERE, A.SNAPSHOTS[r["comment_id"]]), encoding="utf-8").read()
            self.assertEqual(body.count("\n" + r["old"] + "\n"), 1, r["old"])
            self.assertIn(r["anchor"], body)


class VerdictParsing(unittest.TestCase):
    SAMPLE = ("prose\nVERDICT_BLOCK_BEGIN\nrow: Z10-1 | verdict: NOT_SATISFIED | reason: one domain only\n"
              "claim: C1 | verdict: SURVIVES | reason: fine\n"
              "objection: OBJ-1 | claim: C1 | material: yes | text: something\n"
              "reopen: KE-3 | reason: custody\nmodel_self_report: test-model\nVERDICT_BLOCK_END\n")

    def test_routes_agree_on_sample(self):
        a = A.parse_verdict_block(self.SAMPLE)
        rows, claims, sr, reopen = B.parse_block(self.SAMPLE)
        self.assertEqual(a["rows"], rows)
        self.assertEqual(a["claims"], claims)
        self.assertEqual(a["model_self_report"], sr)
        self.assertEqual([d["gate"] for d in a["reopen"]], reopen)
        self.assertEqual(a["objections"][0]["material"], True)

    def test_last_block_wins_and_absent_block(self):
        two = self.SAMPLE + "VERDICT_BLOCK_BEGIN\nrow: Z10-1 | verdict: SATISFIED | reason: x\nmodel_self_report: m\nVERDICT_BLOCK_END\n"
        self.assertEqual(A.parse_verdict_block(two)["rows"]["Z10-1"]["verdict"], "SATISFIED")
        self.assertEqual(B.parse_block(two)[0]["Z10-1"]["verdict"], "SATISFIED")
        self.assertIsNone(A.parse_verdict_block("no block here"))
        self.assertIsNone(B.parse_block("no block here"))


class Z9Oracles(unittest.TestCase):
    ENVS = {"batch": 0, "environments": [
        {"env_id": "S1", "L": 3, "target_0": "CUR", "target_1": "PREV", "p": "2/5", "eta": "1", "lambdas": ["1/10", "1/5", "1/2"]},
        {"env_id": "S2", "L": 4, "target_0": "AND", "target_1": "PREV2", "p": "1/2", "eta": "3", "lambdas": ["1/8", "1/2"]},
        {"env_id": "S4", "L": 3, "target_0": "AND2", "target_1": "OR2", "p": "1/3", "eta": "1", "lambdas": ["1/24", "1/4"]},
    ]}

    def test_parent_law_reproduced(self):
        self.assertEqual(ZA.self_test(), 20)

    def test_routes_agree_and_two_step_target_beats_carry_clause(self):
        a = ZA.run(self.ENVS)["outcomes"]
        b = ZB.run(self.ENVS)["outcomes"]
        for x, y in zip(a, b):
            for k in ("E_stateless", "E_onebit", "lambda_star", "J_best_stateless", "J_best_onebit", "winner_class_set"):
                self.assertEqual(x[k], y[k], (x["env_id"], k))
        self.assertEqual(a[0]["lambda_star"], "1/5")
        self.assertEqual(a[0]["winner_class_set"]["1/5"], ["PERSISTENT_STATE", "STATELESS"])
        # AND/PREV2 at L=4: exhaustive one-bit optimum 1/8 < the carry-previous-bit value 1/6
        self.assertEqual(a[1]["E_onebit"], "1/8")
        self.assertEqual(a[1]["candidates_evaluated"], 65552)

    def test_scoring_and_null(self):
        outs = ZA.run(self.ENVS)
        preds = {"predictions": [{"env_id": o["env_id"], "lambda_star": o["lambda_star"], "winner_class_set": o["winner_class_set"],
                                  "J_best_stateless": o["J_best_stateless"], "J_best_onebit": o["J_best_onebit"]} for o in outs["outcomes"]]}
        s = A.score_batch(preds, outs)
        self.assertEqual((s["class_hits"], s["class_total"]), (7, 7))
        self.assertEqual((s["capability_hits"], s["capability_total"]), (7, 7))
        self.assertEqual((s["crossover_hits"], s["crossover_total"]), (3, 3))
        self.assertEqual(s["environments_with_miss"], 0)
        preds["predictions"][0]["lambda_star"] = "1/7"
        self.assertEqual(A.score_batch(preds, outs)["crossover_hits"], 2)


class Gates(unittest.TestCase):
    def test_exhaustion_gate_clean_and_planted(self):
        gaps = A.load_gaps()
        g = A.exhaustion_gate(gaps)
        self.assertEqual(g["records"], 1140)
        self.assertEqual(g["exhausted"], 0)
        self.assertEqual(g["violations"], [])
        self.assertEqual(B.aa10()["violations"], 0)
        planted = gaps + [{"id": "P", "status": "RECURSION_EXHAUSTED", "owner_role": "lane"}]
        self.assertEqual(len(A.exhaustion_gate(planted)["violations"]), 1)
        ok = gaps + [{"id": "Q", "status": "EXHAUSTED", "owner_role": "lane",
                      "independent_hostile_review": {"reviewer_kind": A.LABEL, "reviewer_id": "PX-X", "verdict_sha256": "a" * 64}}]
        self.assertEqual(A.exhaustion_gate(ok)["violations"], [])


@unittest.skipUnless(os.path.exists(os.path.join(HERE, "PROXY_RECORDS_V1.json")), "records not yet assembled")
class LiveRecords(unittest.TestCase):
    def test_integrity_and_cross_route_closure(self):
        res, rec = A.compute(recompute_z9=False)
        self.assertEqual(res["record_integrity_violations"], [])
        self.assertEqual(res["reconciliation_violations"], [])
        doc = json.load(open(os.path.join(HERE, "PROXY_RECORDS_V1.json")))
        rows, briefs, pins = B.freeze_tables()
        self.assertEqual(B.integrity(doc, briefs, pins), 0)
        reopened = json.load(open(os.path.join(HERE, "REOPENED_GATES_V1.json")))
        closed_b = B.decide(doc, B.z9(doc), B.aa10(), reopened)
        self.assertEqual(set(res["closed_rows"]), {k for k, v in closed_b.items() if v})
        self.assertEqual(len(rec["replacements"]) + len(rec["not_closed"]), 40)
        for e in rec["replacements"]:
            self.assertIn(A.LABEL, e["new"])
        for e in rec["not_closed"]:
            self.assertIn(A.LABEL, e["reason"])

    def test_hostiles_all_detected(self):
        h = A.hostiles()
        self.assertGreaterEqual(len(h), 12)
        self.assertTrue(all(h.values()), h)

    def test_null(self):
        self.assertEqual(A.null_records(50, 7)["random_record_sets_passing_integrity"], 0)
        z = A.z9_null(json.load(open(os.path.join(HERE, "PROXY_RECORDS_V1.json"))), 50, 7)
        self.assertEqual(z["random_predictors_matching_all"], 0)

    def test_committed_receipts_match_live(self):
        res, rec = A.compute(recompute_z9=False)
        committed = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
        for k in ("closed_rows", "not_closed_rows", "aa10_gate", "gates", "two_route_agreement"):
            self.assertEqual(committed[k], res[k], k)
        crec = json.load(open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")))
        self.assertEqual(crec["replacements"], rec["replacements"])
        self.assertEqual(crec["not_closed"], rec["not_closed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
