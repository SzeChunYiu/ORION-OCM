#!/usr/bin/env python3
"""CI: the committed receipts must equal a live two-route run, and the two routes
must agree on the closed-row set, the AA10 counts and the Z9 scores."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
a = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
b = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))
bad = []
if a["closed_rows"] != b["closed_rows"]:
    bad.append("closed rows differ: %s vs %s" % (a["closed_rows"], b["closed_rows"]))
if a["record_integrity_violations"] != [] or b["integrity_violations"] != 0:
    bad.append("integrity violations")
if (a["aa10_gate"]["records"], a["aa10_gate"]["exhausted"], len(a["aa10_gate"]["violations"])) != \
        (b["aa10"]["records"], b["aa10"]["exhausted"], b["aa10"]["violations"]):
    bad.append("aa10 counts differ")
for x, y in zip(a["z9"], b["z9"]):
    if [x["score"]["class_hits"], x["score"]["class_total"]] != y["class"] or \
            [x["score"]["capability_hits"], x["score"]["capability_total"]] != y["capability"] or \
            [x["score"]["crossover_hits"], x["score"]["crossover_total"]] != y["crossover"]:
        bad.append("z9 scores differ on batch %s" % x["batch"])
    if not y["oracle_b_agrees_with_committed_outcomes"]:
        bad.append("oracle B disagrees with committed outcomes on batch %s" % x["batch"])
if len(a["z9"]) != len(b["z9"]) or len(a["z9"]) < 2:
    bad.append("fewer than two Z9 batches")
if not all(a["gates"].values()):
    bad.append("route A gates: %s" % a["gates"])
if bad:
    print("\n".join(bad)); sys.exit(1)
print("receipts agree across routes; closed rows: %d, not closed: %d" % (len(a["closed_rows"]), len(a["not_closed_rows"])))
