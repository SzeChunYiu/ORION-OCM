#!/usr/bin/env python3
"""RV-A iteration 2 aggregator: pool the per-seed lane-distributed null shards
and apply the frozen decision rule.

Usage: python3 rva_null_agg.py <FREEZE_JSON> <OUT_JSON> <SHARD_JSON>...
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

FREEZE = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
SHARDS = [os.path.abspath(p) for p in sys.argv[3:]]


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 8), round(min(1.0, c + h), 8))


def main():
    fr = json.load(open(FREEZE))
    obs_lo, obs_hi = fr["comparator"]["observed_survivor_can_check_wilson95"]
    obs = fr["comparator"]["observed_survivor_can_check_fraction"]

    tot = collections.Counter()
    farch_v = collections.Counter()
    falsifier = 0
    seeds = []
    for p in SHARDS:
        d = json.load(open(p))
        seeds.append(d["seed"])
        tot["draws"] += d["n_draws"]
        tot["legal"] += d["n_legal"]
        tot["can_check_drawn"] += d["n_can_check_drawn"]
        tot["viable_raw"] += d["raw"]["n_viable"]
        tot["viable_raw_cc"] += d["raw"]["n_viable_can_check"]
        tot["dist_viable"] += d["phenotype_deduped"]["n_distinct_viable"]
        tot["dist_viable_cc"] += d["phenotype_deduped"]["n_distinct_viable_can_check"]
        for k in ("n_can_check_viable", "n_can_check_dead",
                  "n_no_check_viable", "n_no_check_dead"):
            tot[k] += d["gate_selection"][k]
        for k, v in d["farch_viable"].items():
            farch_v[k] += v
        falsifier += d["falsifier_viable_without_check_and_without_fibred"]["n_found"]

    raw_frac = tot["viable_raw_cc"] / max(1, tot["viable_raw"])
    dist_frac = tot["dist_viable_cc"] / max(1, tot["dist_viable"])
    raw_ci = wilson(tot["viable_raw_cc"], tot["viable_raw"])
    dist_ci = wilson(tot["dist_viable_cc"], tot["dist_viable"])

    # frozen decision rule, applied to the phenotype-deduped endpoint
    lo, hi = dist_ci
    if lo is None:
        verdict = "INSUFFICIENT_DATA"
    elif hi < obs_lo:
        verdict = "RANKING_ENRICHES"
    elif lo > obs_hi:
        verdict = "RANKING_OWNS_DEPLETION"
    else:
        verdict = "GATE_OWNS_DEPLETION"

    p_v_cc = tot["n_can_check_viable"] / max(
        1, tot["n_can_check_viable"] + tot["n_can_check_dead"])
    p_v_nc = tot["n_no_check_viable"] / max(
        1, tot["n_no_check_viable"] + tot["n_no_check_dead"])
    odds = ((p_v_nc / max(1e-12, 1 - p_v_nc)) /
            max(1e-12, p_v_cc / max(1e-12, 1 - p_v_cc)))

    out = {
        "study_id": "RV_A_NULL_ITER2_AGGREGATE",
        "protocol_freeze_sha256": fr["self_sha256_note"],
        "freeze_id": fr["freeze_id"],
        "seeds": sorted(seeds),
        "n_shards": len(SHARDS),
        "totals": dict(tot),
        "sampling_can_check_rate": round(
            tot["can_check_drawn"] / max(1, tot["legal"]), 8),
        "sampling_can_check_rate_analytic_expected":
            fr["falsifiers"]["expected_sampling_can_check_rate"],
        "viable_rate": round(tot["viable_raw"] / max(1, tot["legal"]), 8),
        "endpoint_raw_draw": {
            "can_check_fraction": round(raw_frac, 8), "wilson95": raw_ci,
            "n": tot["viable_raw"], "k": tot["viable_raw_cc"]},
        "endpoint_phenotype_deduped": {
            "can_check_fraction": round(dist_frac, 8), "wilson95": dist_ci,
            "n": tot["dist_viable"], "k": tot["dist_viable_cc"]},
        "comparator_observed_survivors": {
            "can_check_fraction": obs, "wilson95": [obs_lo, obs_hi]},
        "gate_selection": {
            "P_viable_given_can_check": round(p_v_cc, 8),
            "P_viable_given_not_can_check": round(p_v_nc, 8),
            "odds_ratio_favouring_checker_free": round(odds, 6)},
        "farch_viable": dict(farch_v),
        "falsifier_viable_without_check_and_without_fibred_total": falsifier,
        "falsifier_passed": falsifier == 0,
        "verdict": verdict,
        "decision_rule": fr["decision_rule"],
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
