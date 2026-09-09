"""Aggregate AMEND-3 runs ONLY when every expected (arm, seed) has an ok
disposition and a verifiable receipt chain (5 arms x 3 seeds = 15 tasks).

Emits results/AGGREGATE_AMEND3.json: per-arm seed-means on the amend-3 axes,
the FROZEN matched-pair rule (each QD arm vs P01_random_search_T2 on
[pareto_recovery_T2, own_axis_recovery, best_dev_T2]), the retention-frontier
flags (frontier_retention_fraction >= 0.5 on every seed), and the first-match
terminal per FREEZE_V1_AMEND_3.scoring_rules_amend3.terminal_rule_FROZEN.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)  # self-contained import (no PYTHONPATH assumption)
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json")) as f:
    A3 = json.load(f)
ARMS = [a["arm_id"] for a in A3["arms_amend3"]["arms"]]
OWN = {a["arm_id"]: a["own_axis"] for a in A3["arms_amend3"]["arms"]}
SEEDS = A3["arms_amend3"]["seeds"]
QD_ARMS = [a for a in ARMS if a != "P01_random_search_T2"]
D_ARCHIVE_ARMS = ("P05_map_elites_D2d", "P06_cvt_map_elites_D",
                  "P09_map_elites_D3d")

from evaluation.receipts import verify_receipt  # noqa: E402

missing, failed, rows = [], [], []
for arm in ARMS:
    for seed in SEEDS:
        tag = "%s_s%d" % (arm, seed)
        status = os.path.join(ROOT, "results", "QDA3_%s.status" % tag)
        if not os.path.exists(status):
            missing.append(tag)
            continue
        if open(status).read().split()[0] != "ok":
            failed.append((tag, open(status).read().strip()))
            continue
        with open(os.path.join(ROOT, "results", "QDA3_%s.json" % tag)) as f:
            rows.append(json.load(f))
        with open(os.path.join(ROOT, "manifests", "receipts",
                               "QDA3_%s.receipt.json" % tag)) as f:
            rcpt = json.load(f)
        if not verify_receipt(rcpt):
            failed.append((tag, "receipt chain invalid"))
if missing or failed:
    print(json.dumps({"aggregate": "REFUSED", "missing": missing,
                      "failed": [f[0] for f in failed]}, indent=1))
    sys.exit(2)

METRICS = ("pareto_recovery_T2", "D2d_cell_recovery", "D3d_cell_recovery",
           "CVTD_niche_recovery", "S3d_cell_recovery", "best_dev_T2",
           "qd_score_T2", "n_elites", "own_axis_value",
           "retention_positive_elite_fraction", "retention_max",
           "frontier_retention_fraction", "wall_s", "cpu_hours", "evals")


def _mean(vals):
    xs = [v for v in vals if v is not None]
    return round(sum(xs) / len(xs), 6) if xs else None


cells_out = {}
for arm in ARMS:
    rs = [r for r in rows if r["arm"] == arm]
    m = {k: _mean([r.get(k) for r in rs]) for k in METRICS}
    m.update({"seeds": len(rs), "budget": rs[0]["budget"], "own_axis": OWN[arm],
              "frontier_retention_min_seed": min(
                  r["frontier_retention_fraction"] for r in rs),
              "retention_frontier_positive": all(
                  r["frontier_retention_fraction"] >= 0.5 for r in rs),
              "per_seed": {str(r["seed"]): {
                  k: r[k] for k in ("evals", "wall_s", "n_elites",
                                    "pareto_recovery_T2", OWN[arm],
                                    "best_dev_T2", "frontier_retention_fraction",
                                    "retention_positive_elite_fraction")}
                  for r in rs}})
    cells_out[arm] = m


def winner(qd_arm):
    """+1 QD wins the pair, 0 TIE, -1 P01 wins (frozen matched-pair rule);
    None when a criterion is null on either side (no contest recorded)."""
    a, b = cells_out[qd_arm], cells_out["P01_random_search_T2"]
    crit = ["pareto_recovery_T2", OWN[qd_arm], "best_dev_T2"]
    if any(a[c] is None or b[c] is None for c in crit):
        return None
    if all(a[c] >= b[c] for c in crit) and any(a[c] > b[c] for c in crit):
        return 1
    if all(a[c] <= b[c] for c in crit) and any(a[c] < b[c] for c in crit):
        return -1
    return 0


pair_results, qd_wins, p01_wins = {}, 0, 0
for arm in QD_ARMS:
    w = winner(arm)
    label = {1: "QD", -1: "P01", 0: "TIE", None: "NO_CONTEST_NULL"}[w]
    if w == 1:
        qd_wins += 1
    elif w == -1:
        p01_wins += 1
    a, b = cells_out[arm], cells_out["P01_random_search_T2"]
    pair_results[arm] = {
        "winner": label, "own_axis": OWN[arm],
        "qd": {k: a[k] for k in ("pareto_recovery_T2", OWN[arm], "best_dev_T2",
                                 "n_elites", "cpu_hours")},
        "p01": {k: b[k] for k in ("pareto_recovery_T2", OWN[arm],
                                  "best_dev_T2", "n_elites", "cpu_hours")},
        "qd_minus_p01": {k: (round(a[k] - b[k], 6)
                             if a[k] is not None and b[k] is not None else None)
                         for k in ("pareto_recovery_T2", OWN[arm], "best_dev_T2")},
    }

# first-match terminal over the FROZEN rule sequence
rule1 = (qd_wins >= 3 and all(cells_out[a]["retention_frontier_positive"]
                              for a in QD_ARMS
                              if pair_results[a]["winner"] == "QD"))
diverse = [a for a in D_ARCHIVE_ARMS
           if cells_out[a][OWN[a]] is not None
           and cells_out[a][OWN[a]] >= 0.25
           and cells_out[a]["best_dev_T2"] is not None
           and cells_out["P01_random_search_T2"]["best_dev_T2"] is not None
           and cells_out[a]["best_dev_T2"] >=
           cells_out["P01_random_search_T2"]["best_dev_T2"] - 0.01]
if rule1:
    verdict = "DEVELOPMENTAL_MORPHOLOGY_ADVANTAGE_SUPPORTED_AT_SCOPE"
elif diverse:
    verdict = "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE"
elif p01_wins >= 1 and qd_wins == 0:
    verdict = "QD_NO_ADVANTAGE_OVER_MULTI_OBJECTIVE_PARENT"
else:
    verdict = "MIXED_INTERMEDIATE_NO_TERMINAL"

out = {
    "aggregate_id": "MZD7_AMEND3_DEVELOPMENTAL",
    "amendment": A3["amendment_id"],
    "tier": "T2",
    "n_runs": len(rows),
    "budget_per_task": rows[0]["budget"],
    "cells": cells_out,
    "pair_results": pair_results,
    "pair_wins": {"QD": qd_wins, "P01": p01_wins,
                  "TIE": len(QD_ARMS) - qd_wins - p01_wins},
    "diverse_arms_qualified": diverse,
    "verdict_terminal": verdict,
    "terminal_rule_source":
        "FREEZE_V1_AMEND_3.json scoring_rules_amend3.terminal_rule_FROZEN",
}
with open(os.path.join(ROOT, "results", "AGGREGATE_AMEND3.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"aggregate": "OK", "runs": len(rows), "verdict": verdict,
                  "pair_wins": out["pair_wins"],
                  "diverse_arms_qualified": diverse}))
