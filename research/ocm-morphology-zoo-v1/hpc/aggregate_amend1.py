"""Aggregate AMEND-1 runs ONLY when every expected (arm, seed) has an ok
disposition and a verifiable receipt chain.

Emits results/AGGREGATE_AMEND1.json: per-arm means on the amended axes
(S3d@10 den 8, B2d@20 den 4, CVT census niches den 18), Pareto recovery
(den 387, unchanged), elite counts vs the amended ceilings, and both
comparison views (same-eval-count, same-CPU-hour).  Smoke-prefixed runs
(SMOKE_QDA1_*) are ignored.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = sys.argv[1]
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_1.json")) as f:
    A1 = json.load(f)
ARMS = A1["production_MZ_D3_amend1"]["arms_live"]
SEEDS = A1["production_MZ_D3_amend1"]["seeds"]
DEN = A1["census_truth_P00B"]["denominators_amended"]
CEIL = {"S3d@10": DEN["S3d@10_occupied"], "B2d@20": DEN["B2d@20_occupied"],
        "CVT64": DEN["CVT64_occupied_niches"]}

from evaluation.receipts import verify_receipt  # noqa: E402

missing, failed, rows = [], [], []
for arm in ARMS:
    for seed in SEEDS:
        tag = "%s_s%d" % (arm, seed)
        status = os.path.join(ROOT, "results", "QDA1_%s.status" % tag)
        if not os.path.exists(status):
            missing.append(tag)
            continue
        if open(status).read().split()[0] != "ok":
            failed.append((tag, open(status).read().strip()))
            continue
        with open(os.path.join(ROOT, "results", "QDA1_%s.json" % tag)) as f:
            rows.append(json.load(f))
        with open(os.path.join(ROOT, "manifests", "receipts", "QDA1_%s.receipt.json" % tag)) as f:
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
        "n_elites_mean": round(sum(r["n_elites"] for r in rs) / len(rs), 3),
        "S3d10_cells_hit_mean": round(sum(r["S3d10_cells_hit"] for r in rs) / len(rs), 3),
        "B2d20_cells_hit_mean": round(sum(r["B2d20_cells_hit"] for r in rs) / len(rs), 3),
        "CVT_census_niches_hit_mean": round(sum(r["CVT_census_niches_hit"] for r in rs) / len(rs), 3),
        "pareto_recovery_mean": round(sum(r["pareto_recovery"] for r in rs) / len(rs), 6),
        "S3d10_cell_recovery_mean": round(sum(r["S3d10_cell_recovery"] for r in rs) / len(rs), 6),
        "B2d20_cell_recovery_mean": round(sum(r["B2d20_cell_recovery"] for r in rs) / len(rs), 6),
        "CVT_census_niche_recovery_mean": round(sum(r["CVT_census_niche_recovery"] for r in rs) / len(rs), 6),
        "best_dev_mean": round(sum(r["best_dev"] for r in rs) / len(rs), 6),
        "best_dev_max": max(r["best_dev"] for r in rs),
        "per_seed": {str(r["seed"]): {k: r[k] for k in
                                      ("evals", "wall_s", "n_elites",
                                       "pareto_recovery", "S3d10_cell_recovery",
                                       "B2d20_cell_recovery",
                                       "CVT_census_niche_recovery", "best_dev")} for r in rs},
    }

# cap-lift verdict inputs: does the MAP-Elites family now retain elites
# commensurate with the amended ceilings (V1: <=5 elites, saturated)?
map_family = [a for a in ARMS if a.startswith(("P03_", "P05_", "P06_", "P09_"))]
cap_lift = {a: {"n_elites_mean": arms_out[a]["n_elites_mean"],
                "S3d@10_ceiling": CEIL["S3d@10"],
                "S3d10_cells_hit_mean": arms_out[a]["S3d10_cells_hit_mean"],
                "B2d@20_ceiling": CEIL["B2d@20"],
                "B2d20_cells_hit_mean": arms_out[a]["B2d20_cells_hit_mean"],
                "CVT64_ceiling": CEIL["CVT64"],
                "CVT_census_niches_hit_mean": arms_out[a]["CVT_census_niches_hit_mean"]}
            for a in map_family}

cpu_view = {a: round(arms_out[a]["pareto_recovery_mean"] / max(1e-9, arms_out[a]["cpu_hours_total"]), 6)
            for a in ARMS}
out = {
    "aggregate_id": "MZD3_AMEND1",
    "amendment": A1["amendment_id"],
    "n_runs": len(rows),
    "budget_per_arm_seed": rows[0]["budget"],
    "arms": arms_out,
    "same_eval_count_ranking_pareto": sorted(ARMS, key=lambda a: -arms_out[a]["pareto_recovery_mean"]),
    "same_eval_count_ranking_S3d10": sorted(ARMS, key=lambda a: -arms_out[a]["S3d10_cell_recovery_mean"]),
    "same_cpu_hour_view": cpu_view,
    "map_elites_family_cap_lift": cap_lift,
    "amended_denominators": DEN,
    "pareto_denominator_unchanged": 387,
}
with open(os.path.join(ROOT, "results", "AGGREGATE_AMEND1.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"aggregate": "OK", "runs": len(rows),
                  "ranking_pareto": out["same_eval_count_ranking_pareto"],
                  "ranking_S3d10": out["same_eval_count_ranking_S3d10"]}))
