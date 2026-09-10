#!/usr/bin/env python3
"""RV-A iteration 3: aggregate the L1 unranked-breadth control with CROSS-SEED
phenotype dedup, and compare like-for-like against every GS-R2 arm.

GS_R2_AGGREGATE.json dedups its arms' survivors by phenotype across seeds; this
does the same for L1, so distinct-yield and T3-hold counts are comparable.

Also computes the shuffle-equal-n null: subsample the L1 survivor set down to a
comparator arm's n and report the hypergeometric expectation, which is what
distinguishes a real gain in ABSOLUTE hold count from a selectivity artifact.

Usage: python3 rva_l1_agg.py <CAPSULE_ROOT> <OUT_JSON> <L1_DIR>
"""
from __future__ import annotations

import collections, glob, json, math, os, sys

ROOT = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2])
L1 = os.path.abspath(sys.argv[3])


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (None, None)
    p = k / n; d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 8), round(min(1.0, c + h), 8))


def main():
    agg = json.load(open(os.path.join(ROOT, "results", "GS_R2_AGGREGATE.json")))
    # ---- L1: cross-seed dedup
    pheno = {}
    cpu = 0.0; t0_evals = 0; seeds = []
    per_seed_distinct = []       # per-seed, NOT cross-seed deduped
    per_seed_hold = []
    for p in sorted(glob.glob(os.path.join(L1, "RVA_L1_s?.json"))):
        d = json.load(open(p))
        seeds.append(d["seed"]); cpu += d["cpu_seconds"]
        t0_evals += d["counts"]["T0_evaluated"]
        per_seed_distinct.append(d["distinct_t2_viable_phenotypes_this_seed"])
        per_seed_hold.append(d["distinct_t3_hold_this_seed"])
    for p in sorted(glob.glob(os.path.join(L1, "RVA_L1_s?.jsonl"))):
        for line in open(p):
            q = line.split()
            if len(q) != 4:
                continue
            pref, cc, hold, farch = q
            if pref not in pheno:
                pheno[pref] = (cc == "1", hold == "1", farch)
    n = len(pheno)
    k_hold = sum(1 for _, h, _ in pheno.values() if h)
    k_cc = sum(1 for c, _, _ in pheno.values() if c)
    mismatch = sum(1 for c, h, _ in pheno.values() if c != h)
    cpu_h = cpu / 3600.0
    farch = collections.Counter(f for _, _, f in pheno.values())

    # ---- comparators
    comp = {}
    for a, v in agg["arms"].items():
        comp[a] = {"cpu_hours": v["cpu_hours"],
                   "distinct_t2_viable": v["distinct_t2_viable_phenotypes"],
                   "mean_distinct_per_seed": v["mean_distinct_per_seed"],
                   "morphologies_per_cpu_hour": v["morphologies_per_cpu_hour"]}
    # per-arm hold counts, from the aggregate's own verdicts
    arm_hold = collections.Counter(); arm_n = collections.Counter()
    for t in agg["t3_verdicts"]:
        for a in t["arms"]:
            arm_n[a] += 1
            if t["verdict"].endswith("HOLD"):
                arm_hold[a] += 1
    for a in comp:
        comp[a]["distinct_t3_hold"] = arm_hold[a]
        comp[a]["t3_hold_rate"] = round(arm_hold[a] / max(1, arm_n[a]), 8)
        comp[a]["t3_hold_per_cpu_hour"] = round(
            arm_hold[a] / max(1e-12, comp[a]["cpu_hours"]), 1)
    pooled_hold = agg["t3_summary"]["SURVIVOR_T3_GENERALIZATION_HOLD"]
    pooled_n = agg["n_distinct_survivors"]
    pooled_cpu = sum(v["cpu_hours"] for v in agg["arms"].values())

    # ---- shuffle-equal-n null against the pooled R2 survivor set
    # H0: L1's hold rate is the R2 pooled rate; subsample L1 to n_R2 and ask
    # how many holds that predicts (hypergeometric mean and sd).
    p0 = pooled_hold / pooled_n
    exp_hold_at_L1_n = p0 * n
    sd = math.sqrt(n * p0 * (1 - p0))
    z = (k_hold - exp_hold_at_L1_n) / sd if sd > 0 else None

    out = {
        "study_id": "RV_A_L1_AGGREGATE",
        "arm": "L1_unranked_breadth",
        "protocol": ("lane_hetero, T0->T1->T2 ladder, NO rank_fn, NO promotion "
                     "selection, NO parent pool; t0_budget 45000/seed, seeds "
                     "0..5 -- matched to the GS-R2 arms"),
        "seeds": sorted(seeds), "t0_evaluations": t0_evals,
        "cpu_seconds": round(cpu, 3), "cpu_hours": round(cpu_h, 8),
        "L1": {
            "distinct_t2_viable": n,
            "distinct_t3_hold": k_hold,
            "distinct_can_check": k_cc,
            "can_check_equals_hold": mismatch == 0,
            "t3_hold_rate": round(k_hold / max(1, n), 8),
            "t3_hold_rate_wilson95": wilson(k_hold, n),
            "mean_distinct_per_seed": round(
                sum(per_seed_distinct) / max(1, len(per_seed_distinct)), 2),
            "mean_distinct_per_seed_definition": (
                "per-seed distinct phenotype count then averaged, matching "
                "aggregate_gs_r2.py's dist_per_seed/statistics.mean; NOT the "
                "cross-seed-deduped total divided by seeds"),
            "per_seed_distinct_t2_viable": per_seed_distinct,
            "per_seed_distinct_t3_hold": per_seed_hold,
            "mean_distinct_t3_hold_per_seed": round(
                sum(per_seed_hold) / max(1, len(per_seed_hold)), 2),
            "cross_seed_deduped_total_over_seeds": round(
                n / max(1, len(seeds)), 2),
            "morphologies_per_cpu_hour": round(n / max(1e-12, cpu_h), 1),
            "t3_hold_per_cpu_hour": round(k_hold / max(1e-12, cpu_h), 1)},
        "gs_r2_arms": comp,
        "gs_r2_pooled": {
            "distinct_t2_viable": pooled_n, "distinct_t3_hold": pooled_hold,
            "t3_hold_rate": round(p0, 8), "cpu_hours": round(pooled_cpu, 6),
            "t3_hold_per_cpu_hour": round(pooled_hold / pooled_cpu, 1)},
        "gs_r2_parents_frozen": agg["lever_attribution"]["parents_frozen"],
        "shuffle_equal_n_null": {
            "H0": "L1's survivors hold at the GS-R2 pooled rate",
            "R2_pooled_hold_rate": round(p0, 8),
            "L1_n": n,
            "expected_holds_under_H0": round(exp_hold_at_L1_n, 1),
            "observed_holds": k_hold,
            "sd_under_H0": round(sd, 2),
            "z": round(z, 2) if z is not None else None,
            "read": ("the null asks whether L1's hold COUNT is what the R2 rate "
                     "would predict at L1's n; a lever that only raised the RATE "
                     "by finding fewer survivors would not beat it")},
        "farch_of_L1_survivors": dict(farch),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({kk: vv for kk, vv in out.items()
                      if kk != "farch_of_L1_survivors"}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
