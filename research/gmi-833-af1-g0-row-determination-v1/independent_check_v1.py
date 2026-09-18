# -*- coding: utf-8 -*-
"""AF1 row determination -- an executable re-derivation, independent of PR #969.

Two things are checked against the definitions committed on `main` in
`research/gmi-833-af-barrier-context-v1/FORMALIZATION_V1.md`:

  1. `Current` is a slice of `Gamma`, so equal `Gamma` forces equal current capability.  The
     literal converse asked by the AF1 row -- different current capability with identical
     `Gamma` -- is therefore unsatisfiable for every pair of machines, not merely unevidenced.
     Checked by exhaustive search over an enumerated finite profile universe.
  2. The weaker post-development projection `Gamma+` (profiles with at least one development
     step) does admit a converse witness, which is the form a repaired row could ask for.
     Exhibited.

Also asserted: the merged AF package contains no reference to the registered `G0` interpreter.
The search is run with a control pattern that must match, so an empty result cannot be read as
a working search that found nothing.

    python3 -I -B  independent_check_v1.py
"""

import json
import os
import re
import sys
from fractions import Fraction
from itertools import combinations, product

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
AF = os.path.join(REPO, "research", "gmi-833-af-barrier-context-v1")

CAPABILITIES = (Fraction(0, 1), Fraction(1, 2), Fraction(1, 1))
STEPS = (0, 1, 2)
PROFILES = tuple((c, s) for c in CAPABILITIES for s in STEPS)


def current(gamma):
    """The registered zero-development slice."""
    return frozenset(c for (c, s) in gamma if s == 0)


def plus(gamma):
    """The post-development projection: profiles that consumed at least one step."""
    return frozenset(c for (c, s) in gamma if s > 0)


def search_literal_converse(max_size=3):
    """Different current capability with identical full `Gamma`."""
    seen = 0
    for size in range(1, max_size + 1):
        for g in combinations(PROFILES, size):
            ga = frozenset(g)
            seen += 1
            for size2 in range(1, max_size + 1):
                for h in combinations(PROFILES, size2):
                    gb = frozenset(h)
                    if ga == gb and current(ga) != current(gb):
                        return {"witness_found": True, "gamma": sorted(map(str, ga))}
    return {"witness_found": False, "gamma_sets_examined": seen}


def search_same_current_different_gamma(max_size=3):
    for size in range(1, max_size + 1):
        for g in combinations(PROFILES, size):
            ga = frozenset(g)
            for size2 in range(1, max_size + 1):
                for h in combinations(PROFILES, size2):
                    gb = frozenset(h)
                    if ga != gb and current(ga) == current(gb):
                        return {"witness_found": True,
                                "gamma_a": sorted("%s@%d" % (c, s) for c, s in ga),
                                "gamma_b": sorted("%s@%d" % (c, s) for c, s in gb),
                                "shared_current": sorted(map(str, current(ga)))}
    return {"witness_found": False}


def search_plus_converse(max_size=3):
    """Different current capability with identical post-development projection."""
    for size in range(1, max_size + 1):
        for g in combinations(PROFILES, size):
            ga = frozenset(g)
            for size2 in range(1, max_size + 1):
                for h in combinations(PROFILES, size2):
                    gb = frozenset(h)
                    if plus(ga) == plus(gb) and current(ga) != current(gb):
                        return {"witness_found": True,
                                "gamma_a": sorted("%s@%d" % (c, s) for c, s in ga),
                                "gamma_b": sorted("%s@%d" % (c, s) for c, s in gb),
                                "shared_projection": sorted(map(str, plus(ga))),
                                "current_a": sorted(map(str, current(ga))),
                                "current_b": sorted(map(str, current(gb)))}
    return {"witness_found": False}


def scan_merged_af_package():
    """Searched with controls: an empty result only counts when a control pattern matched."""
    files = []
    for name in sorted(os.listdir(AF)):
        path = os.path.join(AF, name)
        if os.path.isfile(path):
            with open(path, "rb") as fh:
                files.append((name, fh.read().decode("utf-8", "replace")))
    controls = {}
    for pat in ("Gamma", "def "):
        controls[pat] = sum(1 for _n, t in files if pat in t)
    targets = {}
    for pat in ("G0-reg-v1", "G0_RESULT", "check_g0_micro"):
        targets[pat] = sum(len(re.findall(re.escape(pat), t)) for _n, t in files)
    g0_lines = []
    for name, text in files:
        for k, line in enumerate(text.split("\n"), 1):
            if re.search(r"g0", line, re.IGNORECASE):
                g0_lines.append({"file": name, "line": k, "text": line.strip()[:160]})
    converse_lines = []
    for name, text in files:
        for k, line in enumerate(text.split("\n"), 1):
            if re.search(r"convers", line, re.IGNORECASE):
                converse_lines.append({"file": name, "line": k})
    return {"files_scanned": len(files), "control_hits": controls,
            "target_hits": targets, "g0_mentions": g0_lines,
            "converse_mentions": len(converse_lines)}


def reconciliation_state():
    path = os.path.join(AF, "ISSUE_833_AF_RECONCILIATION_V1.json")
    d = json.load(open(path))
    row = ("- [ ] Construct exact finite `G0` microscopes where two machines have the same "
           "current capability but different `Gamma`, and conversely.")
    return {"comment_id": d["comment_id"],
            "tasks": len(d["tasks"]),
            "row_is_auto_reconciled": row in d["tasks"],
            "deferred_tasks": [t["task"][:80] for t in d.get("deferred_tasks", [])],
            "row_is_deferred": any(row == t["task"] for t in d.get("deferred_tasks", []))}


def main():
    out = {
        "schema": "GMI833AF1RowDeterminationV1",
        "issue": 833,
        "comment_id": 5693269426,
        "anchor": "### AF1 — Developmental capability response object",
        "row": ("- [x] Construct exact finite `G0` microscopes where two machines have the "
                "same current capability but different `Gamma`, and conversely."),
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "profile_universe": len(PROFILES),
        "literal_converse": search_literal_converse(),
        "same_current_different_gamma": search_same_current_different_gamma(),
        "post_development_projection_converse": search_plus_converse(),
        "merged_af_package_scan": scan_merged_af_package(),
        "merged_reconciliation_state": reconciliation_state(),
        "repair_pr": {"number": 969, "state_checked_at_source_main": "OPEN",
                      "merged": False,
                      "note": "verified twice, with gh pr view and the pulls API"},
    }
    findings = []
    if out["literal_converse"]["witness_found"]:
        findings.append("LITERAL_CONVERSE_SATISFIABLE__DETERMINATION_WRONG")
    if not out["same_current_different_gamma"]["witness_found"]:
        findings.append("FIRST_DIRECTION_NOT_SATISFIABLE")
    if not out["post_development_projection_converse"]["witness_found"]:
        findings.append("PROJECTION_CONVERSE_NOT_SATISFIABLE")
    scan = out["merged_af_package_scan"]
    for pat, n in scan["control_hits"].items():
        if n == 0:
            findings.append("CONTROL_PATTERN_DID_NOT_MATCH:" + pat)
    if sum(scan["target_hits"].values()):
        findings.append("MERGED_PACKAGE_DOES_REFERENCE_G0_INTERPRETER")
    if len(scan["g0_mentions"]) != 1:
        findings.append("G0_MENTION_COUNT_CHANGED:%d" % len(scan["g0_mentions"]))
    if scan["converse_mentions"] != 1:
        findings.append("CONVERSE_MENTION_COUNT_CHANGED:%d" % scan["converse_mentions"])
    st = out["merged_reconciliation_state"]
    if not st["row_is_auto_reconciled"] or st["row_is_deferred"]:
        findings.append("ROW_NO_LONGER_AUTO_RECONCILED__REPAIR_MAY_HAVE_LANDED")
    out["findings"] = findings
    out["verdict"] = ("CHECKED_BUT_UNSUPPORTED" if not findings
                      else "DETERMINATION_NEEDS_REVIEW")
    with open(os.path.join(HERE, "AF1_DETERMINATION_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True, separators=(",", ": ")) + "\n")
    print(json.dumps({"verdict": out["verdict"], "findings": findings,
                      "literal_converse_witness":
                          out["literal_converse"]["witness_found"],
                      "projection_converse_witness":
                          out["post_development_projection_converse"]["witness_found"],
                      "g0_mentions_in_merged_af_package":
                          len(scan["g0_mentions"])}, indent=2, sort_keys=True))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
