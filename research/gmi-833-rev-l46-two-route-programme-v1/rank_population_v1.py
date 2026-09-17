#!/usr/bin/env python3
"""Rank the 75 SINGLE_ROUTE packages of PASS-L46 by claim criticality.

Mechanical, stdlib-only, judgment-input-free. Reads only frozen artifacts:
  - research/gmi-833-corpus-passes-v2-v1/P3_SCREENS_V1.json   (population)
  - research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json    (GREEN-mainline)
  - research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json (maturity)

Ranking key (frozen in PROGRAMME_V1.md section 1):
  1. GREEN-mainline object count desc  (blast radius)
  2. comp_claims desc                  (exposure)
  3. max maturity_M, then max evidence_EV desc
  4. package name asc                  (stable total order)

Usage: python3 -I -B research/gmi-833-rev-l46-two-route-programme-v1/rank_population_v1.py
Writes RANKING_V1.json next to this file. Exit 2 on any inconsistency.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

P3 = "research/gmi-833-corpus-passes-v2-v1/P3_SCREENS_V1.json"
CENSUS = "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
SCORES = "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"

M_ORDER = {"M0": 0, "M1": 1, "M2": 2, "M3": 3, "M4": 4, "M5": 5, "M6": 6,
           "UNKNOWN": -1}
EV_ORDER = {"EV0": 0, "EV1": 1, "EV2": 2, "EV3": 3, "EV4": 4, "EV5": 5,
            "UNKNOWN": -1}

TRANCHE1 = [
    "gmi-formal-proof-audit-v1",
    "gmi-developmental-uncertainty-transport-v1",
    "gmi-analog-semantics-closure-v1",
    "gmi-uncertainty-composition-v1",
    "gmi-dependency-aware-uncertainty-composition-v1",
    "gmi-capability-ceilings-v1",
    "gmi-structural-threshold-repair-v1",
    "gmi-learning-law-selection-v1",
]
COLLISION_EXCLUSIONS = {
    "gmi-novel-intelligence-w4-v1": "w4 family-cluster lane active",
    "gmi-morphology-phase-rv-v1": "w1 lane (open PR #993) adjacent",
}
TRANCHE2_DEFERRED_WITH_REASON = {
    "gmi-main566567-audit-v1": "rank-9 green=1 but no in-package route-1 executor "
                                "(source-bound review package); first tranche-2 item",
}


def load(rel):
    with open(REPO / rel, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    p3 = load(P3)
    census = load(CENSUS)
    scores = load(SCORES)

    single = [(k, v) for k, v in p3["packages"].items()
              if v.get("L46", {}).get("status") == "SINGLE_ROUTE"]
    if len(single) != 75:
        print("REFUSED: SINGLE_ROUTE population is %d, expected 75" % len(single))
        return 2

    green = {}
    for obj in census["scientific_objects"]:
        if obj.get("audit_disposition") == "GREEN" and obj.get("id_kind") == "EXPLICIT":
            src = obj.get("source_path", "")
            if src.startswith("research/"):
                green.setdefault(src.split("/")[1], []).append(obj["object_id"])

    maturity = {}
    for row in scores:
        pkg = row.get("package", "")
        m = M_ORDER.get(row.get("maturity_M", "UNKNOWN"), -1)
        ev = EV_ORDER.get(row.get("evidence_EV", "UNKNOWN"), -1)
        best = maturity.get(pkg, (-1, -1))
        maturity[pkg] = (max(best[0], m), max(best[1], ev))

    rows = []
    for name, meta in single:
        g = green.get(name, [])
        m, ev = maturity.get(name, (-1, -1))
        rows.append({
            "package": name,
            "comp_claims": meta["comp_claims"],
            "green_mainline_objects": len(g),
            "green_mainline_ids": sorted(g),
            "max_maturity_M": ("M%d" % m) if m >= 0 else "UNKNOWN",
            "max_evidence_EV": ("EV%d" % ev) if ev >= 0 else "UNKNOWN",
            "tranche": ("TRANCHE_1" if name in TRANCHE1 else
                        "TRANCHE_2_COLLISION_EXCLUDED" if name in COLLISION_EXCLUSIONS
                        else "TRANCHE_2_DEFERRED_WITH_REASON"
                        if name in TRANCHE2_DEFERRED_WITH_REASON
                        else "TRANCHE_2"),
            "note": (COLLISION_EXCLUSIONS.get(name, "") or
                     TRANCHE2_DEFERRED_WITH_REASON.get(name, "")),
        })
    if sum(1 for r in rows if r["tranche"] == "TRANCHE_1") != len(TRANCHE1):
        missing = [t for t in TRANCHE1
                   if t not in {r["package"] for r in rows}]
        print("REFUSED: tranche-1 selections absent from population: %s" % missing)
        return 2

    rows.sort(key=lambda r: (-r["green_mainline_objects"], -r["comp_claims"],
                             -M_ORDER.get(r["max_maturity_M"], -1),
                             -EV_ORDER.get(r["max_evidence_EV"], -1),
                             r["package"]))

    out = {
        "schema": "GMI_833_REV_L46_TWO_ROUTE_RANKING_V1",
        "programme": "REV-L46-TWO-ROUTE-PROGRAMME tranche 1 (PROGRAMME_V1.md)",
        "inputs": [P3, CENSUS, SCORES],
        "ranking_key": [
            "green_mainline_objects desc",
            "comp_claims desc",
            "max maturity_M desc",
            "max evidence_EV desc",
            "package asc",
        ],
        "counts": {
            "population": len(rows),
            "tranche_1": len(TRANCHE1),
            "tranche_2": sum(1 for r in rows if r["tranche"] == "TRANCHE_2"),
            "deferred_with_reason": sum(1 for r in rows
                                        if r["tranche"] == "TRANCHE_2_DEFERRED_WITH_REASON"),
            "collision_excluded": sum(1 for r in rows
                                      if r["tranche"] == "TRANCHE_2_COLLISION_EXCLUDED"),
        },
        "rows": rows,
    }
    dest = Path(__file__).resolve().parent / "RANKING_V1.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote %s (%d rows; tranche1=%d tranche2=%d excluded=%d)" % (
        dest, len(rows), out["counts"]["tranche_1"], out["counts"]["tranche_2"],
        out["counts"]["collision_excluded"]))
    for i, r in enumerate(rows[:12], 1):
        print("%2d. %-46s comp=%2d green=%d %s/%s %s" % (
            i, r["package"], r["comp_claims"], r["green_mainline_objects"],
            r["max_maturity_M"], r["max_evidence_EV"], r["tranche"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
