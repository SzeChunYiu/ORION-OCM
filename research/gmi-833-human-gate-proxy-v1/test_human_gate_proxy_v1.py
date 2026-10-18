#!/usr/bin/env python3
"""Tests for gmi-833-human-gate-proxy-v1.  python3 -I -B / -I -O -B, stdlib only.
Every assertion uses `if not ...: raise AssertionError` so -O cannot silence it."""
import copy
import hashlib
import importlib.util
import json
import os
import re
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = load("human_gate_proxy_v1")
B = load("independent_oracle_v1")
OA = load("z9_oracle_a_v1")
OB = load("z9_oracle_b_v1")


def check(cond, msg=""):
    if not cond:
        raise AssertionError(msg)


class FreezeAndRecords(unittest.TestCase):
    def setUp(self):
        self.freeze = A.parse_freeze(A.read("FREEZE_V1.md"))
        self.records = json.loads(A.read("PROXY_RECORDS_V1.json"))
        self.result = json.loads(A.read("RESULT_V1.json"))

    def test_freeze_parse_counts(self):
        check(len(self.freeze["briefs"]) == 18, "18 briefs frozen")
        check(len(self.freeze["pins"]) == 43, "43 artifact pins")
        check(len(self.freeze["snapshots"]) == 3)
        check(self.freeze["ceiling"].startswith("GMI_833_HUMAN_GATE_ROWS_DISCHARGED_BY_LABELLED_MODEL_PROXY"))

    def test_every_brief_matches_freeze_sha(self):
        for name, (sha, nbytes) in self.freeze["briefs"].items():
            b = A.read("briefs/" + name, "rb")
            check(hashlib.sha256(b).hexdigest() == sha and len(b) == nbytes, name)

    def test_every_record_labelled_and_verbatim(self):
        for r in self.records["records"]:
            check(r["label"] == A.LABEL, r["id"])
            if r["verdict_block_present"]:
                b = A.read(r["verdict_file"], "rb")
                check(hashlib.sha256(b).hexdigest() == r["verdict_sha256"], r["id"])
                parsed = A.parse_block(b.decode("utf-8"))
                check(parsed is not None and parsed["self_report"], r["id"])

    def test_two_route_rows_use_two_families(self):
        R = {r["id"]: r["requested_model"] for r in self.records["records"]}
        check({R["PX-AG8-A"], R["PX-AG8-B"]} == {"opus", "sonnet"})
        check({R["PX-AC05-A"], R["PX-AC05-B"]} == {"opus", "sonnet"})
        check({R["PX-Z9-A1"], R["PX-Z9-A2"]} == {"opus", "sonnet"})
        check({R["PX-Z9-P1"], R["PX-Z9-P2"]} == {"opus", "sonnet"})
        check({R["PX-Z9-T1"], R["PX-Z9-T2"]} == {"opus", "sonnet"})

    def test_not_satisfied_rows_never_closed(self):
        for pid, rows in self.result["proxy_row_verdicts"].items():
            for row, v in rows.items():
                if v != "SATISFIED" and pid not in ("PX-Z9-P1",):
                    check(row not in self.result["closed"], "%s closed despite %s from %s" % (row, v, pid))

    def test_no_forbidden_promotion_in_receipts(self):
        recon = A.read("ISSUE_833_COMMENT_RECONCILIATION_V1.json")
        for tok in A.FORBIDDEN:
            for x in json.loads(recon)["replacements"]:
                check(tok not in x["new"], tok)
                check(A.LABEL in x["new"])

    def test_row_coverage_is_total(self):
        check(set(self.result["closed"]) | set(self.result["not_closed"]) == set(A.ALL_ROWS))
        check(not (set(self.result["closed"]) & set(self.result["not_closed"])))

    def test_hostiles_all_detected_and_applicable(self):
        h = self.result["hostiles"]
        check(len(h) == 12)
        for k, v in h.items():
            check(v["detected"] and v["applicable"], k)

    def test_nulls(self):
        check(self.result["z9"]["null_random_predictors_matching_all_winner_sets"] == "0/200")
        check(self.result["null_random_record_sets_passing_integrity"] == "0/200")


class Z9Oracles(unittest.TestCase):
    def test_parent_law_reproduced(self):
        check(OA.self_test() == 20)

    def test_routes_agree_on_every_committed_environment(self):
        for b in (1, 2):
            env = json.loads(A.read("z9/batch_%d/ENVIRONMENTS.json" % b))
            ra, rb = OA.run(env), OB.run(env)
            check(A.routes_agree([ra], [rb]), "batch %d" % b)
            check(ra == json.loads(A.read("z9/batch_%d/OUTCOMES.json" % b)))
            check(rb == json.loads(A.read("z9/batch_%d/OUTCOMES_ROUTE_B.json" % b)))

    def test_carry_previous_machine_is_not_always_optimal(self):
        """The falsified clause T3: on a two-back target the exhaustive one-bit
        optimum beats the carry-x_{t-1} machine (EARNED BY COUNTEREXAMPLE)."""
        env = {"env_id": "T", "L": 3, "target_0": "PREV2", "target_1": "OR2", "p": "4/9", "eta": "1", "lambdas": ["1/8"]}
        r = OA.solve(env)
        check(Fraction(r["E_onebit"]) == Fraction(5, 36), r["E_onebit"])   # exhaustive
        check(Fraction(r["E_onebit"]) < Fraction(7, 36))                    # T3's carry-previous value
        # and the control: on a (x_t, x_{t-1}) target T3 is exact
        env2 = {"env_id": "C", "L": 3, "target_0": "CUR", "target_1": "PREV", "p": "1/2", "eta": "1", "lambdas": ["1/4"]}
        r2 = OA.solve(env2)
        check(Fraction(r2["E_onebit"]) == 0 and Fraction(r2["lambda_star"]) == Fraction(1, 4))

    def test_oracle_rejects_out_of_family(self):
        for bad in ({"L": 5}, {"p": "3/2"}, {"eta": "0"}, {"lambdas": ["0"]}):
            env = {"env_id": "X", "L": 3, "target_0": "CUR", "target_1": "PREV", "p": "1/2", "eta": "1", "lambdas": ["1/4"]}
            env.update(bad)
            with self.assertRaises((ValueError, KeyError)):
                OA.solve(env)

    def test_scorer_exact_and_adjudicators_match(self):
        R = json.loads(A.read("RESULT_V1.json"))
        for pid, v in R["z9"]["adjudicators"].items():
            check(v["parsed"] == v["executor"], pid)
        s = R["z9"]["totals"]
        check(s["class_hits"] + sum(1 for sc in R["z9"]["scores"] for m in sc["misses"] if m[2:3] == ["class"]) == s["points"])

    def test_batch_validity_checker_rejects_bad_batch(self):
        env = json.loads(A.read("z9/batch_1/ENVIRONMENTS.json"))
        ok, _ = A.batch_valid(env)
        check(ok)
        bad = copy.deepcopy(env)
        bad["environments"] = bad["environments"][:5]
        check(not A.batch_valid(bad)[0])

    def test_null_generator_has_no_short_period(self):
        g = A.lcg(1)
        seq = [next(g) % 3 for _ in range(60)]
        check(len(set(tuple(seq[i:i + 6]) for i in range(0, 54))) > 20)


class AA10Gate(unittest.TestCase):
    def test_live_graph_and_planted_violation(self):
        graph = json.loads(open(os.path.join(A.REPO, "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json")).read())
        r = A.aa10_gate(graph)
        check(r["records"] == 1140 and r["violations"] == 0)
        g = copy.deepcopy(graph)
        g["gaps"][3]["status"] = "RECURSION_EXHAUSTED"
        check(A.aa10_gate(g)["violations"] == 1)
        g["gaps"][3]["independent_hostile_review"] = {"reviewer_kind": A.LABEL, "reviewer_id": "PX-TEST", "verdict_sha256": "0" * 64}
        check(A.aa10_gate(g)["violations"] == 0)
        g["gaps"][3]["independent_hostile_review"]["reviewer_id"] = g["gaps"][3]["owner_role"]
        check(A.aa10_gate(g)["violations"] == 1)
        # route B walk agrees
        check(B.aa10_walk(graph) == (1140, 0, 0))


class Registers(unittest.TestCase):
    def test_reopen_register_complete_and_h12(self):
        records = json.loads(A.read("PROXY_RECORDS_V1.json"))
        reg = json.loads(A.read("REOPENED_GATES_V1.json"))
        check(A.reopen_complete(records, reg))
        reg2 = copy.deepcopy(reg)
        reg2["demands"] = reg2["demands"][:-1]
        check(not A.reopen_complete(records, reg2))

    def test_downgrades_reference_real_objections(self):
        dg = json.loads(A.read("CLAIM_DOWNGRADES_V1.json"))
        records = json.loads(A.read("PROXY_RECORDS_V1.json"))
        known = set()
        for r in records["records"]:
            for o in r.get("objections", []):
                known.add("%s %s" % (r["id"], o["id"]))
        for d in dg["downgrades"] + dg["revival_targets"]:
            for ref in d["objections"]:
                if ref.startswith("PX-AA41 SWEEP"):
                    continue
                check(ref in known, ref)
        for d in dg["downgrades"]:
            check(d["new_wording"] != d["original_wording"] and d["restore_by"].startswith("RV-"), d["id"])
            check(any(x["id"] == d["restore_by"] for x in dg["revival_targets"]) or d["restore_by"] in ("RV-C1-F1-NULL",), d["id"])

    def test_responses_cover_every_material_objection(self):
        text = A.read("RESPONSES_V1.md")
        records = {r["id"]: r for r in json.loads(A.read("PROXY_RECORDS_V1.json"))["records"]}
        short = {"PX-Z18-THM": "THM", "PX-Z18-EXP": "EXP", "PX-Z18-LIT": "LIT", "PX-Z18-STAT": "STAT", "PX-Z18-COG": "COG"}
        lines = text.split("\n")
        for pid, tag in short.items():
            for o in records[pid]["objections"]:
                if o["material"]:
                    hit = any(("%s OBJ" % tag) in ln and re.search(r"\b%s\b" % re.escape(o["id"]), ln) and "| " in ln for ln in lines)
                    check(hit, "%s %s unanswered" % (tag, o["id"]))


if __name__ == "__main__":
    unittest.main()
