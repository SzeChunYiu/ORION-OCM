#!/usr/bin/env python3
"""CI cross-route check: RESULT_V1.json (route A) and ORACLE_RESULT_V1.json (route B)
must both be GREEN and agree on the closed-row set (set equality), the AA10 counts,
the Z9 score totals, the material-objection and reopen-demand totals, and the
reconciliation must carry exactly the closed rows.  Stdlib only, python3.8."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
a = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
b = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))
r = json.load(open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")))
bad = []
if a["verdict"] != "GREEN" or b["verdict"] != "GREEN":
    bad.append("verdicts: A=%s B=%s" % (a["verdict"], b["verdict"]))
if sorted(a["closed"]) != sorted(b["closed"]) or not b["closed_set_equals_route_a"]:
    bad.append("closed sets differ: only_in_a=%s only_in_b=%s" % (b["only_in_a"], b["only_in_b"]))
if a["integrity_violations"]:
    bad.append("integrity violations: %s" % a["integrity_violations"])
if (a["aa10_gate"]["records"], a["aa10_gate"]["exhausted"], a["aa10_gate"]["violations"]) != (b["aa10"]["records"], b["aa10"]["exhausted"], b["aa10"]["violations"]):
    bad.append("aa10 counts differ")
tb = {"class_hits": b["z9"]["scores_batch1"]["class"] + b["z9"]["scores_batch2"]["class"],
      "capability_hits": b["z9"]["scores_batch1"]["capability"] + b["z9"]["scores_batch2"]["capability"],
      "points": b["z9"]["scores_batch1"]["points"] + b["z9"]["scores_batch2"]["points"],
      "crossover_hits": b["z9"]["scores_batch1"]["crossover"] + b["z9"]["scores_batch2"]["crossover"],
      "environments": b["z9"]["scores_batch1"]["environments"] + b["z9"]["scores_batch2"]["environments"]}
if a["z9"]["totals"] != tb:
    bad.append("z9 totals differ: %s vs %s" % (a["z9"]["totals"], tb))
if not (a["z9"]["oracle_recompute_matches"] and b["z9"]["oracle_b_recompute_matches"] and a["z9"]["routes_agree"] and b["z9"]["routes_agree"]):
    bad.append("oracle recompute / route agreement")
if a["material_objections_total"] != b["material_objections_total"] or a["reopen_demands_total"] != b["reopen_demands_total"]:
    bad.append("objection / reopen totals differ")
if a["z9"]["null_random_predictors_matching_all_winner_sets"] != "0/200" or b["z9"]["null_random_predictors_matching_all"] != "0/200" or a["null_random_record_sets_passing_integrity"] != "0/200":
    bad.append("a null was not beaten")
if sum(1 for h in a["hostiles"].values() if h["detected"] and h["applicable"]) != len(a["hostiles"]) or len(a["hostiles"]) != 12:
    bad.append("hostiles: %s" % {k: v for k, v in a["hostiles"].items() if not (v["detected"] and v["applicable"])})
if sorted(x["row"] for x in r["replacements"]) != sorted(a["closed"]) or sorted(x["row"] for x in r["not_closed"]) != sorted(a["not_closed"]):
    bad.append("reconciliation rows differ from RESULT")
for x in r["replacements"]:
    if a["label"] not in x["new"] or any(t in x["new"] for t in a["forbidden_promotions"]):
        bad.append("bad new line for %s" % x["row"])
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("receipts agree across routes; closed %d, not closed %d; hostiles %d/12; z9 %s" % (len(a["closed"]), len(a["not_closed"]), len(a["hostiles"]), json.dumps(a["z9"]["totals"], sort_keys=True)))
