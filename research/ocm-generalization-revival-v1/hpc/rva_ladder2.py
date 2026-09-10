#!/usr/bin/env python3
"""RV-A iteration 3 arm L1: unranked-breadth control at MATCHED T0 budget.

Runs the T0 -> T1 -> T2 ladder on fresh lane_hetero draws with NO ranking, NO
promotion selection and NO parent pool, at exactly the GS-R2 arms' own
t0_budget_per_seed and seeds, and emits every viable phenotype digest so the
survivor set can be cross-seed deduplicated the same way GS_R2_AGGREGATE.json
deduplicates its arms.  Only then is the comparison like-for-like.

Offline; no network.
Usage: python3 rva_ladder2.py <CAPSULE_ROOT> <SEED> <T0_BUDGET> <OUT> <OUTL>
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
SEED = int(sys.argv[2]); BUDGET = int(sys.argv[3])
OUT = os.path.abspath(sys.argv[4]); OUTL = os.path.abspath(sys.argv[5])

from morphology.gs_bound import lane_hetero                   # noqa: E402
from morphology.compile import compile_genome                 # noqa: E402
from evaluation.evaluate import evaluate_genome               # noqa: E402
from evaluation.gs_t1 import evaluate_t1                      # noqa: E402
from evaluation.lifetime2 import _capabilities                # noqa: E402
from evaluation.lifetime import Sim                           # noqa: E402
from evaluation.t3_ecology import evaluate_t3                 # noqa: E402

freeze = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R2_FREEZE.json")))
T3KEY = freeze["t3_key"]


def main():
    rng = random.Random(SEED)
    t_w = time.time(); t_c = time.process_time()
    n0 = nT0 = nT1 = nT2 = 0
    seen = {}
    fl = open(OUTL, "w")
    n_t3_hold = 0
    while n0 < BUDGET:
        try:
            g = lane_hetero(rng); org = compile_genome(g)
        except Exception:
            continue
        n0 += 1
        cc = _capabilities(Sim(org))["can_check"]
        try:
            r0 = evaluate_genome(g, tier="T0", use_cache=False)
        except Exception:
            continue
        if not r0["feasible"]:
            continue
        nT0 += 1
        try:
            r1 = evaluate_t1(g)
        except Exception:
            continue
        if not r1["feasible"]:
            continue
        nT1 += 1
        try:
            r2 = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        if not r2["feasible"]:
            continue
        nT2 += 1
        ph = r2["phenotype_digest"]
        if ph in seen:
            continue
        # T3 verdict via the real path, exactly as aggregate_gs_r2 computes it
        hold = bool(evaluate_t3(g, T3KEY)["feasible"])
        n_t3_hold += 1 if hold else 0
        seen[ph] = 1
        fl.write("%s %d %d %s\n" % (ph[:16], 1 if cc else 0,
                                    1 if hold else 0, g.F_arch))
    fl.close()
    wall = time.time() - t_w
    cpu = time.process_time() - t_c
    out = {
        "study_id": "RV_A_LADDER2_L1_UNRANKED_BREADTH",
        "arm": "L1_unranked_breadth",
        "ranking": "NONE (no rank_fn, no promotion selection, no parent pool)",
        "seed": SEED, "t0_budget": BUDGET,
        "counts": {"T0_evaluated": n0, "T0_viable": nT0,
                   "T1_viable": nT1, "T2_viable": nT2},
        "distinct_t2_viable_phenotypes_this_seed": len(seen),
        "distinct_t3_hold_this_seed": n_t3_hold,
        "wall_seconds": round(wall, 3), "cpu_seconds": round(cpu, 3),
        "cpu_hours": round(cpu / 3600.0, 8),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
