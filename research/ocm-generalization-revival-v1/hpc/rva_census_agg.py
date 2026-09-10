#!/usr/bin/env python3
"""RV-A iteration 2b aggregator: pool the exhaustive GS-bound census shards.

Dedups viable phenotypes globally across shards (shards partition the grammar
space, but distinct grammars can compile to the same phenotype), and reports the
absolute ceiling |{T2-viable AND T3-HOLD}| both per-grammar and per-phenotype.

Usage: python3 rva_census_agg.py <OUT_JSON> <SHARD_DIR>
"""
from __future__ import annotations

import collections
import glob
import json
import math
import os
import sys

OUT = os.path.abspath(sys.argv[1])
SD = os.path.abspath(sys.argv[2])


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0.0, c - h), 8), round(min(1.0, c + h), 8))


def main():
    tot = collections.Counter()
    vbc = collections.Counter()
    t3c = collections.Counter()
    fv, fh = collections.Counter(), collections.Counter()
    falsifier = 0
    shards = sorted(glob.glob(os.path.join(SD, "RVA_CENSUS_sh*.json")))
    for p in shards:
        d = json.load(open(p))
        tot["legal"] += d["n_legal_enumerated"]
        tot["can_check"] += d["n_can_check"]
        tot["viable"] += d["n_viable"]
        for k, v in d["viable_by_can_check"].items():
            vbc[k] += v
        for k, v in d["t3_by_can_check_over_viable"].items():
            t3c[k] += v
        for k, v in d["farch_viable"].items():
            fv[k] += v
        for k, v in d["farch_hold"].items():
            fh[k] += v
        falsifier += d["falsifier_viable_without_check_and_without_fibred"]["n_found"]

    # global phenotype dedup over viable organisms
    pheno = {}
    for p in sorted(glob.glob(os.path.join(SD, "RVA_CENSUS_sh*.jsonl"))):
        with open(p) as fh_:
            for line in fh_:
                parts = line.split()
                if len(parts) != 4:
                    continue
                pref, cc, farch, hold = parts
                if pref not in pheno:
                    pheno[pref] = (cc == "1", farch, hold == "1")
    d_n = len(pheno)
    d_cc = sum(1 for cc, _, _ in pheno.values() if cc)
    d_hold = sum(1 for _, _, h in pheno.values() if h)
    d_farch = collections.Counter(f for _, f, _ in pheno.values())
    d_farch_hold = collections.Counter(f for _, f, h in pheno.values() if h)

    g_hold = t3c.get("True|HOLD", 0) + t3c.get("False|HOLD", 0)
    out = {
        "study_id": "RV_A_CENSUS_ITER2B_AGGREGATE",
        "n_shards": len(shards),
        "gs_bound_closed_form_size": 143881920,
        "totals_grammar_level": dict(tot),
        "viable_by_can_check_grammar": dict(vbc),
        "t3_by_can_check_over_viable_grammar": dict(t3c),
        "grammar_level": {
            "viable": tot["viable"],
            "viable_can_check": vbc.get("True|True", 0),
            "can_check_fraction_of_viable": round(
                vbc.get("True|True", 0) / max(1, tot["viable"]), 8),
            "wilson95": wilson(vbc.get("True|True", 0), tot["viable"]),
            "t3_hold": g_hold,
            "hold_equals_can_check": (g_hold == vbc.get("True|True", 0)
                                      and t3c.get("False|HOLD", 0) == 0
                                      and t3c.get("True|FAIL", 0) == 0)},
        "phenotype_level": {
            "distinct_viable": d_n,
            "distinct_viable_can_check": d_cc,
            "can_check_fraction_of_viable": round(d_cc / max(1, d_n), 8),
            "wilson95": wilson(d_cc, d_n),
            "distinct_t3_hold_CEILING": d_hold},
        "farch_viable_grammar": dict(fv),
        "farch_hold_grammar": dict(fh),
        "farch_viable_phenotype": dict(d_farch),
        "farch_hold_phenotype": dict(d_farch_hold),
        "falsifier_viable_without_check_and_without_fibred_total": falsifier,
        "falsifier_passed": falsifier == 0,
        "search_found_distinct_hold": 15668,
        "read": ("distinct_t3_hold_CEILING is the absolute maximum number of "
                 "distinct T3-holding phenotypes any search over this bound "
                 "could return; the R2 campaign returned 15668. The ceiling is "
                 "a budget statement, not a bias statement -- the bias question "
                 "is decided by the lane-distributed null in FREEZE_RVA_ITER2."),
    }
    with open(OUT, "w") as fhh:
        json.dump(out, fhh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items()
                      if not k.startswith("farch")}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
