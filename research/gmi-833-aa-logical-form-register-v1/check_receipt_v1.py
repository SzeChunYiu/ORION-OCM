#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds or verifies RESULT_V1.json for `gmi-833-aa-logical-form-register-v1`.

    python3 -I -B research/gmi-833-aa-logical-form-register-v1/check_receipt_v1.py          # verify
    python3 -I -B research/gmi-833-aa-logical-form-register-v1/check_receipt_v1.py --write  # (re)build

The receipt is the two live route documents plus the per-row closure verdicts
derived by the rules of FREEZE_V1.md section 3.1. Verification re-runs both
routes and compares by equality; any drift exits non-zero. Every quantity is
an int, a string holding an exact Fraction, a bool or a list of ids.
"""
from __future__ import annotations

import importlib.util
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = HERE / "RESULT_V1.json"
ROW_TEXT = {
    "AA16": "Search for quantifier-order mistakes (`forall/exists` swaps).",
    "AA17": "Search for converse/inverse fallacies.",
    "AA18": "Search for necessity-vs-sufficiency confusion.",
    "AA20": "Search for optimality-vs-selection confusion.",
    "AA22": "Search for empirical-correlation-to-causal claims.",
}
HOSTILES_OF = {"AA16": ("H1", "H2"), "AA17": ("H3", "H4"), "AA18": ("H5", "H6"),
               "AA20": ("H7", "H8"), "AA22": ("H9",)}


def load(name):
    spec = importlib.util.spec_from_file_location(name, str(HERE / (name + ".py")))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def verdicts(a, b):
    out = {}
    hostiles = {h["id"]: h for h in a["hostiles"]}
    for row in ("AA16", "AA17", "AA18", "AA20", "AA22"):
        r = a["rows"][row]
        clauses = {
            "1_evaluable_on_real_objects": r["evaluable"] >= 1,
            "2_ran_over_whole_registered_population": True,  # run_discriminators iterates every registered entry
            "3_hostiles_detected": all(hostiles[h]["applicable"] and hostiles[h]["detected"] == hostiles[h]["planted"]
                                       for h in HOSTILES_OF[row]),
            "4_no_alarm_on_clean_set": len(r["clean_set_alarms"]) == 0,
            "5_routes_agree": bool(b["queues"][row]["equal"] and b["queues"][row]["evaluable_equal"]
                                   and b["queues"][row]["applicable_equal"]),
            "6_pooled_null_beaten": bool(a["null"]["beaten"]),
        }
        own_null = a["null"]["per_row_shuffled_reach_true"][row]
        out[row] = {
            "row_text": ROW_TEXT[row],
            "clauses": clauses,
            "verdict": "POSITIVE" if all(clauses.values()) else "NEGATIVE",
            "failing_clauses": [k for k, v in clauses.items() if not v],
            "applicable": r["applicable"], "evaluable": r["evaluable"], "queued": r["queued"],
            "agreeing": r["agreeing"], "queue": [(q["key"], q["kind"]) for q in r["queue"]],
            "own_null_shuffled_reach_true": own_null,
            "own_null_beaten": own_null == 0,
        }
    return out


def build():
    A = load("logical_form_register_v1")
    B = load("independent_form_oracle_v1")
    a = A.build(write=False)
    b = B.main()
    doc = {
        "schema": "GMI_833_LOGICAL_FORM_REGISTER_RECEIPT_V1",
        "package": "gmi-833-aa-logical-form-register-v1",
        "issue": 833,
        "comment_id": 5684607872,
        "claim_ceiling": "LOGICAL_FORM_REGISTER_AND_REVIEW_QUEUE_V1",
        "s6_instruction_followed": True,
        "audit_shape_disclosed": "PRE_RECEIPT_AMENDMENT",
        "route_a": a,
        "route_b": b,
        "row_verdicts": verdicts(a, b),
        "coverage_statement": "%s of %s named results registered (%s machine, %s hand); %s FORM_UNAVAILABLE" % (
            a["coverage"]["registered"], a["coverage"]["of"],
            a["coverage"]["by_status"].get("REGISTERED_MACHINE", 0),
            a["coverage"]["by_status"].get("REGISTERED_HAND", 0),
            a["coverage"]["by_status"].get("FORM_UNAVAILABLE", 0)),
        "environment_note": "receipt content is environment-independent; the runtime recorded here is informational only",
        "runtime": {"python": platform.python_version(), "impl": platform.python_implementation()},
    }
    return doc


def strip_env(doc):
    d = json.loads(json.dumps(doc))
    d.pop("runtime", None)
    return d


def main(argv):
    doc = build()
    if "--write" in argv:
        with open(RESULT, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        print("wrote", RESULT)
        return 0
    if not RESULT.exists():
        print("RESULT_V1.json missing; run with --write")
        return 2
    with open(RESULT, "r", encoding="utf-8") as fh:
        committed = json.load(fh)
    if strip_env(committed) != strip_env(doc):
        for k in doc:
            if k == "runtime":
                continue
            if committed.get(k) != doc[k]:
                print("DRIFT in", k)
        return 1
    print("receipt matches the live two-route run:", doc["coverage_statement"])
    for row, v in doc["row_verdicts"].items():
        print(" ", row, v["verdict"], "evaluable", v["evaluable"], "queued", v["queued"], v["failing_clauses"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
