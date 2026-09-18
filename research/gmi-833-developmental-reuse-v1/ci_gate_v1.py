#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI gate for gmi-833-developmental-reuse-v1: verdicts, hostiles, no floats,
manifest/reconciliation consistency, scope discipline.  Stdlib only."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), "r") as fh:
        return json.load(fh)


def find_floats(node, path="$"):
    out = []
    if isinstance(node, float):
        out.append(path)
    elif isinstance(node, dict):
        for k, v in node.items():
            out.extend(find_floats(v, path + "." + str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(find_floats(v, path + "[%d]" % i))
    return out


def main():
    fails = []
    res = load("RESULT_V1.json")
    ora = load("ORACLE_RESULT_V1.json")
    man = load("MANIFEST_V1.json")
    rec = load("ISSUE_833_RECONCILIATION_DEVELOPMENTAL_REUSE_V1.json")

    if res["verdict"] != "GMI_833_L_DEVELOPMENTAL_REUSE_GREEN_AT_REGISTERED_SCOPE":
        fails.append("main verdict: " + res["verdict"])
    if ora["verdict"] != "ORACLE_AGREES":
        fails.append("oracle verdict: " + ora["verdict"])
    if not res["hostiles"]["all_detected"]:
        fails.append("hostiles not all detected")
    if not res["hostiles"]["no_alarm_ok"]:
        fails.append("checker alarmed on clean data")
    if not res["parent_reproduction"]["parent_integers_reproduced"]:
        fails.append("parent integers not reproduced")

    for name, blob in (("RESULT_V1.json", res), ("ORACLE_RESULT_V1.json", ora)):
        bad = find_floats(blob)
        if bad:
            fails.append("floats in %s at %s" % (name, bad[:5]))

    if rec["schema"] != "GMI_ISSUE_RECONCILIATION_V2":
        fails.append("reconciliation schema: " + rec["schema"])
    if len(rec["replacements"]) != 3:
        fails.append("reconciliation replacements: %d" % len(rec["replacements"]))
    if len(rec["rows_deliberately_left_open"]) != 2:
        fails.append("rows left open not declared")
    for r in rec["replacements"]:
        if r["anchor"] != "# L. Development, morphogenesis, and evolvability":
            fails.append("bad anchor: " + r["anchor"])
        if not r["old"].startswith("- [ ] "):
            fails.append("old row not unchecked: " + r["old"][:50])
        if not r["new"].startswith("- [x] "):
            fails.append("new row not checked: " + r["new"][:50])
        if not r["new"].startswith("- [x] " + r["old"][len("- [ ] "):]):
            fails.append("new row does not preserve the verbatim row text")

    joined = " ".join(man["forbidden_promotions"]).lower()
    for needle in ("gradient", "open-ended", "no-free-lunch", "expressive", "#910"):
        if needle not in joined:
            fails.append("forbidden promotion missing: " + needle)
    if man["claim_ceiling"] != rec["claim_ceiling"]:
        fails.append("claim ceiling mismatch between manifest and reconciliation")

    # scope discipline: the two open rows must never be claimed
    open_rows = set(man["rows_left_open"])
    for r in rec["replacements"]:
        for orow in open_rows:
            if orow in r["new"]:
                fails.append("open row claimed in a replacement: " + orow)
    if set(res["rows_left_open"]) != open_rows:
        fails.append("receipt and manifest disagree on the open rows")

    if fails:
        sys.stderr.write("CI GATE FAILED:\n  " + "\n  ".join(fails) + "\n")
        return 1
    print("CI gate OK: verdicts green, hostiles detected, no floats, "
          "manifest/reconciliation consistent, open rows not claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
