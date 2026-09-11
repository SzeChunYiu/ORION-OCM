#!/usr/bin/env python3
"""OCM-specific residual over the strongest ordinary parent (#323, #165 M3 question).

ORDINARY_ADAPTIVE_PARENT receives the IDENTICAL mined library but serves it WITHOUT
OCM's admission gate, evidence supports, revocation or support-sensitive reload. It is
therefore the exact control for "what does OCM's bookkeeping buy?".

Regret is measured in the benefit currency (mean B slots to first verified success):

    regret(world) = mean_B(OCM) - mean_B(PARENT)      lower is better for OCM

A positive regret means the gate COST work relative to simply serving the library.
"""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summaries", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows = []
    for f in a.summaries:
        p = Path(f)
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        arms = d.get("arms", {})
        need = ("CONTINUED", "ORDINARY_ADAPTIVE_PARENT", "RESET")
        if not all(k in arms and arms[k].get("mean_B_slots") for k in need):
            continue
        ocm = arms["CONTINUED"]["mean_B_slots"]
        par = arms["ORDINARY_ADAPTIVE_PARENT"]["mean_B_slots"]
        res = arms["RESET"]["mean_B_slots"]
        admitted = abs(ocm - res) > 1e-9
        rows.append({
            "world": p.parent.name or p.name,
            "admitted": admitted,
            "mean_B_OCM": ocm, "mean_B_PARENT": par, "mean_B_RESET": res,
            "regret_vs_parent": round(ocm - par, 1),
            "ocm_better_than_parent": ocm < par - 1e-9,
            "ocm_ties_parent": abs(ocm - par) <= 1e-9,
            "parent_harmful_vs_reset": par > res + 1e-9,
            "gate_protected": (not admitted) and par > res + 1e-9,
            "gate_over_rejected": (not admitted) and par < res - 1e-9,
        })

    wins = sum(1 for r in rows if r["ocm_better_than_parent"])
    ties = sum(1 for r in rows if r["ocm_ties_parent"])
    losses = len(rows) - wins - ties
    protected = sum(1 for r in rows if r["gate_protected"])
    over = sum(1 for r in rows if r["gate_over_rejected"])

    out = {
        "schema": "OCM_M2P1_PARENT_REGRET_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "owner_issue": 165, "hardening_parent": 323,
        "worlds": len(rows),
        "ocm_wins": wins, "ocm_ties": ties, "ocm_losses": losses,
        "gate_protected_worlds": protected, "gate_over_rejected_worlds": over,
        "mean_regret": round(statistics.fmean(r["regret_vs_parent"] for r in rows), 1) if rows else None,
        "median_regret": round(statistics.median(r["regret_vs_parent"] for r in rows), 1) if rows else None,
        "rows": rows,
        "terminal": ("OCM_NO_RESIDUAL_OVER_ORDINARY_PARENT" if wins == 0 else
                     "OCM_RESIDUAL_PRESENT"),
        "reading": ("the admission gate is the only difference between the two arms; where "
                    "it admits, the arms are identical by construction, and where it refuses, "
                    "OCM forfeits whatever the library would have delivered"),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
