"""Aggregate MZ-D3 runs ONLY when every expected (arm, seed) has a disposition.

Verifies each receipt chain first; missing/failed dispositions abort with the
missing list.  Emits results/AGGREGATE_MZD3.json with per-arm means, plus
same-eval-count and same-CPU-hour comparison tables (#221 sec 10).
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = sys.argv[1]
with open(os.path.join(ROOT, "FREEZE_V1.json")) as f:
    FREEZE = json.load(f)
ARMS = FREEZE["production_MZ_D3"]["arms"]
SEEDS = FREEZE["production_MZ_D3"]["seeds"]

from evaluation.receipts import verify_receipt  # noqa: E402

missing, failed, rows = [], [], []
for arm in ARMS:
    for seed in SEEDS:
        tag = "%s_s%d" % (arm, seed)
        status = os.path.join(ROOT, "results", "QD_%s.status" % tag)
        if not os.path.exists(status):
            missing.append(tag)
            continue
        first = open(status).read().split()[0]
        if first != "ok":
            failed.append((tag, open(status).read().strip()))
            continue
        with open(os.path.join(ROOT, "results", "QD_%s.json" % tag)) as f:
            rows.append(json.load(f))
        with open(os.path.join(ROOT, "manifests", "receipts", "QD_%s.receipt.json" % tag)) as f:
            rcpt = json.load(f)
        if not verify_receipt(rcpt):
            failed.append((tag, "receipt chain invalid"))
if missing or failed:
    print(json.dumps({"aggregate": "REFUSED", "missing": missing,
                      "failed": [f[0] for f in failed]}, indent=1))
    sys.exit(2)

arms_out = {}
for arm in ARMS:
    rs = [r for r in rows if r["arm"] == arm]
    arms_out[arm] = {
        "seeds": len(rs),
        "evals_per_seed": rs[0]["evals"],
        "wall_s_mean": round(sum(r["wall_s"] for r in rs) / len(rs), 3),
        "cpu_hours_total": round(sum(r["cpu_hours"] for r in rs), 6),
        "pareto_recovery_mean": round(sum(r["pareto_recovery"] for r in rs) / len(rs), 6),
        "S_cell_recovery_mean": round(sum(r["S_cell_recovery"] for r in rs) / len(rs), 6),
        "B_cell_recovery_mean": round(sum(r["B_cell_recovery"] for r in rs) / len(rs), 6),
        "best_dev_mean": round(sum(r["best_dev"] for r in rs) / len(rs), 6),
        "best_dev_max": max(r["best_dev"] for r in rs),
        "per_seed": {str(r["seed"]): {k: r[k] for k in
                                      ("evals", "wall_s", "pareto_recovery",
                                       "S_cell_recovery", "B_cell_recovery",
                                       "best_dev", "n_elites")} for r in rs},
    }
# same-CPU-hour view: rank arms by recovery achieved per CPU hour, reported
# ALONGSIDE the same-eval-count view (they can reverse the ranking)
cpu_view = {a: round(v["pareto_recovery_mean"] / max(1e-9, v["cpu_hours_total"]), 6)
            for a, v in arms_out.items()}
out = {
    "aggregate_id": "MZD3_V1",
    "n_runs": len(rows),
    "budget_per_arm_seed": rows[0]["budget"],
    "arms": arms_out,
    "same_eval_count_ranking": sorted(ARMS, key=lambda a: -arms_out[a]["pareto_recovery_mean"]),
    "same_cpu_hour_view": cpu_view,
    "truth_denominators": FREEZE["census_truth_P00"],
}
with open(os.path.join(ROOT, "results", "AGGREGATE_MZD3.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"aggregate": "OK", "runs": len(rows),
                  "ranking": out["same_eval_count_ranking"]}))
