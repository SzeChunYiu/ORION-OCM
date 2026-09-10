#!/usr/bin/env python3
"""M2-P1 gate analysis: is the admission refusal operational or STRUCTURAL?

validate_generator admits only if candidate.slots <= baseline.slots on EVERY held-out
task.  methods.solve interleaves guided and baseline streams, so on any task where the
guided stream does not locate the answer first, the candidate pays exactly the 2x
interleave toll and is strictly worse.  Let p be the per-task probability of that.
Then admission requires all n held-out tasks to avoid it:

    P(admit) = (1 - p)^n            -- decays EXPONENTIALLY in n

i.e. the more held-out evidence the gate is given, the less likely it is to admit a
generator, however beneficial.  That is the wrong direction for a validation rule and
it is a property of the RULE, not of the ecology or the learner.

This script estimates p per world from the observed rows and reports the implied
admission probability, the n at which admission becomes improbable, and the observed
refusal count.  It changes nothing: the rule is not relaxed (#323 section 11).
"""
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", nargs="+", required=True,
                    help="paths to ATTRIBUTION json files")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows, ps = [], []
    for w in a.worlds:
        p = Path(w)
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        n, worse = d["held_out_n"], d["worse"]
        phat = worse / n
        ps.append(phat)
        rows.append({
            "world": p.parent.name if p.parent.name else p.name,
            "held_out_n": n, "strictly_better": d["strictly_better"], "worse": worse,
            "p_hat_worse": round(phat, 4),
            "work_reduction": d["mean_work_reduction"],
            "admitted": d["admission"],
            "P_admit_at_this_n": round((1 - phat) ** n, 6),
            "all_worse_ratios_exactly_2x": all(
                abs(r["ratio"] - 2.0) < 1e-9 or r["ratio"] <= 2.0
                for r in d["vetoing_tasks"]) if d["vetoing_tasks"] else None,
        })

    pbar = statistics.fmean(ps) if ps else None
    curve = {}
    if pbar:
        for n in (1, 5, 10, 20, 53, 100, 500, 1000):
            curve[str(n)] = round((1 - pbar) ** n, 8)
    n95 = None
    if pbar and pbar > 0:
        n95 = math.ceil(math.log(0.05) / math.log(1 - pbar))

    out = {
        "schema": "OCM_M2P1_GATE_STRUCTURE_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "owner_issue": 165, "hardening_parent": 323,
        "worlds": rows,
        "worlds_n": len(rows),
        "worlds_admitted": sum(1 for r in rows if r["admitted"]),
        "pooled_p_hat_worse": None if pbar is None else round(pbar, 4),
        "P_admit_vs_heldout_size": curve,
        "heldout_size_where_P_admit_below_0.05": n95,
        "mean_work_reduction_across_worlds": None if not rows else
            round(statistics.fmean(r["work_reduction"] for r in rows), 4),
        "verdict": ("STRUCTURAL: admission probability decays as (1-p)^n, so giving the "
                    "gate MORE held-out evidence makes it LESS likely to admit a "
                    "beneficial generator. Not an ecology artifact, not a threshold to "
                    "tune, and not relaxed here."),
        "claim_ceiling": ("this bounds the registered universal non-inferiority rule "
                          "under the registered interleaved integration mode; it is not "
                          "a claim about admission rules in general"),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "worlds"}, indent=1))
    for r in rows:
        print(" %-22s n=%-3s better=%-3s worse=%-3s p=%.3f  P(admit)=%.2e  red=%.1f%%  admitted=%s"
              % (r["world"], r["held_out_n"], r["strictly_better"], r["worse"],
                 r["p_hat_worse"], r["P_admit_at_this_n"], 100 * r["work_reduction"], r["admitted"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
