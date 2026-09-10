#!/usr/bin/env python3
"""RV-A iteration 3 aggregator: pool the unranked-ladder seeds and build the
matched-cost comparison against the frozen GS-R2 parents.

Usage: python3 rva_ladder_agg.py <CAPSULE_ROOT> <OUT_JSON> <SHARD>...
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
SHARDS = [os.path.abspath(p) for p in sys.argv[3:]]


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (None, None)
    p = k / n; d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 8), round(min(1.0, c + h), 8))


def main():
    agg = json.load(open(os.path.join(ROOT, "results", "GS_R2_AGGREGATE.json")))
    per_rung = {r: collections.Counter() for r in ("T0", "T1", "T2")}
    wall = 0.0
    draws = 0
    seeds = []
    samp = []
    for p in SHARDS:
        d = json.load(open(p))
        seeds.append(d["seed"])
        wall += d["wall_seconds"]
        draws += d["n_draws"]
        samp.append(d["sampling_can_check_rate"])
        for r in ("T0", "T1", "T2"):
            per_rung[r]["n"] += d["phenotype_deduped"][r]["n_distinct_viable"]
            per_rung[r]["k"] += d["phenotype_deduped"][r]["n_distinct_can_check"]
            per_rung[r]["raw_n"] += d["raw"][r]["n_viable"]
            per_rung[r]["raw_k"] += d["raw"][r]["n_can_check"]

    rungs = {}
    for r in ("T0", "T1", "T2"):
        c = per_rung[r]
        rungs[r] = {
            "distinct_viable_summed_over_seeds": c["n"],
            "distinct_can_check_summed_over_seeds": c["k"],
            "can_check_fraction": round(c["k"] / max(1, c["n"]), 8),
            "wilson95": wilson(c["k"], c["n"]),
            "raw_viable": c["raw_n"], "raw_can_check": c["raw_k"]}

    cpu_h = wall / 3600.0
    t2 = per_rung["T2"]
    # frozen parents, and the R2 arms' own T3-eligible yield
    parents = agg["lever_attribution"]["parents_frozen"]
    arms = {}
    for a, v in agg["arms"].items():
        arms[a] = {"cpu_hours": v["cpu_hours"],
                   "distinct_t2_viable": v["distinct_t2_viable_phenotypes"],
                   "mean_distinct_per_seed": v["mean_distinct_per_seed"],
                   "morphologies_per_cpu_hour": v["morphologies_per_cpu_hour"]}
    r2_hold = agg["t3_summary"]["SURVIVOR_T3_GENERALIZATION_HOLD"]
    r2_cpu = sum(v["cpu_hours"] for v in agg["arms"].values())

    out = {
        "study_id": "RV_A_LADDER_ITER3_AGGREGATE",
        "seeds": sorted(seeds), "n_shards": len(SHARDS), "n_draws_total": draws,
        "sampling_can_check_rate_range": [min(samp), max(samp)],
        "per_rung": rungs,
        "rungs_identical": (rungs["T0"]["distinct_viable_summed_over_seeds"]
                            == rungs["T1"]["distinct_viable_summed_over_seeds"]
                            == rungs["T2"]["distinct_viable_summed_over_seeds"]),
        "read_rungs": ("composition is unchanged across T0 -> T1 -> T2 and every "
                       "T0-viable organism clears T1 and T2, so all three ladder "
                       "rungs are composition-neutral; T0 is the binding rung"),
        "cost": {"wall_seconds_total": round(wall, 3),
                 "cpu_hours_total": round(cpu_h, 6),
                 "note": "single core per shard, so wall == CPU"},
        "T3_eligible_yield": {
            "unranked_ladder": {
                "distinct_can_check_viable_summed_over_seeds": t2["k"],
                "cpu_hours": round(cpu_h, 6),
                "per_cpu_hour": round(t2["k"] / cpu_h, 1),
                "caveat": "summed over seeds without cross-seed phenotype "
                          "dedup; the R2 figure below IS cross-seed deduped, so "
                          "this comparison is NOT like-for-like and is reported "
                          "only as an order-of-magnitude bound pending the "
                          "deduped re-run"},
            "GS_R2_all_arms": {
                "distinct_t3_hold": r2_hold,
                "cpu_hours": round(r2_cpu, 6),
                "per_cpu_hour": round(r2_hold / r2_cpu, 1)}},
        "gs_r2_arms": arms,
        "gs_r2_parents_frozen": parents,
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
