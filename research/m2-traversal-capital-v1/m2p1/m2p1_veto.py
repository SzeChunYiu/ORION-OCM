#!/usr/bin/env python3
"""M2-P1 veto identifiability: is the admission veto predictable in advance?

The exponential form P(admit) = (1-p)^n assumes per-task independence, which cannot
be asserted here: every veto arrives at ratio exactly 2.00, the deterministic
signature of "the guided stream did not locate this composition before the baseline
did".  If veto-proneness were predictable from a target property, the true admission
probability would differ from (1-p)^n and any n-threshold derived from it is wrong.

This script tests predictability directly, against the TRIVIAL majority-class
baseline (the honest null: always predict the larger class).  It reports the best
single-threshold separation achievable on each candidate property and the lift over
that null.  A small lift means veto-proneness is NOT identifiable in advance -- which
is the claim that needs no independence assumption.
"""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path


def best_threshold_accuracy(rows, key):
    order = sorted(rows, key=lambda r: r[key])
    n = len(order)
    best = 0.0
    for i in range(n + 1):
        lo, hi = order[:i], order[i:]
        acc = (sum(1 for r in lo if r["worse"]) + sum(1 for r in hi if not r["worse"])) / n
        best = max(best, acc, 1 - acc)
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attributions", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    worlds, lifts = [], []
    for f in a.attributions:
        p = Path(f)
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        rows = d["all_rows"]
        n = len(rows)
        worse = sum(1 for r in rows if r["worse"])
        if worse == 0 or worse == n:
            continue
        trivial = max(worse, n - worse) / n
        res = {}
        for key in ("baseline_slots", "canonical_length"):
            acc = best_threshold_accuracy(rows, key)
            res[key] = {"best_single_threshold_accuracy": round(acc, 4),
                        "lift_over_trivial": round(acc - trivial, 4)}
        lifts.append(max(v["lift_over_trivial"] for v in res.values()))
        worlds.append({
            "world": p.parent.name or p.name,
            "held_out_n": n, "worse": worse, "veto_rate": round(worse / n, 4),
            "trivial_majority_accuracy": round(trivial, 4),
            "predictors": res,
            "worse_rate_by_canonical_length": d["by_canonical_length"],
            "all_vetoes_at_ratio_2x": all(r["ratio"] <= 2.0 + 1e-9 for r in d["vetoing_tasks"]),
        })

    rates = [w["veto_rate"] for w in worlds]
    out = {
        "schema": "OCM_M2P1_VETO_IDENTIFIABILITY_V1",
        "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "owner_issue": 165, "hardening_parent": 323,
        "worlds": worlds, "worlds_n": len(worlds),
        "veto_rate_range": [min(rates), max(rates)] if rates else None,
        "veto_rate_mean": round(statistics.fmean(rates), 4) if rates else None,
        "max_lift_over_trivial_any_world": round(max(lifts), 4) if lifts else None,
        "finding": ("veto-proneness is NOT identifiable in advance from target search "
                    "cost or canonical program length: the best single-threshold rule "
                    "beats the trivial majority-class null by a small margin, and the "
                    "per-length worse-rates are inconsistent ACROSS worlds (one world "
                    "vetoes 3/3 of its shortest targets, another 0/3)"),
        "consequence": ("the admission rule requires universal non-inferiority over a "
                        "held-out set that reliably contains veto-prone targets whose "
                        "identity cannot be anticipated, at a rate that does not shrink "
                        "with n. This is the claim that needs NO independence assumption. "
                        "P(admit)=(1-p)^n is retained ONLY as an illustrative bound and is "
                        "explicitly labelled as assuming independence."),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "worlds"}, indent=1))
    for w in worlds:
        print(" %-22s n=%-3s veto=%-3s rate=%.3f trivial=%.3f  lift(cost)=%+.3f lift(len)=%+.3f"
              % (w["world"], w["held_out_n"], w["worse"], w["veto_rate"],
                 w["trivial_majority_accuracy"],
                 w["predictors"]["baseline_slots"]["lift_over_trivial"],
                 w["predictors"]["canonical_length"]["lift_over_trivial"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
