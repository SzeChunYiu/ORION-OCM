#!/usr/bin/env python3
"""RV-A iteration 3: per-rung composition of the UNRANKED ladder.

The iteration-2 null measured T2 viability directly on fresh draws.  The search
does not do that: it runs a T0 -> T1 -> T2 successive-halving ladder, and 80% of
each cohort after the first round descends from a rank-selected parent pool.  So
the iteration-2 result exonerates sampling and the T2 gate, but it has NOT
exonerated the T0 and T1 rungs.

This measures P(can_check | rung-viable) at EVERY rung, on fresh lane_hetero
draws, with NO ranking, NO promotion and NO parent pool -- every draw that
clears a rung is carried to the next.  If the composition holds near the
iteration-2 value through T2, all three gates are exonerated and the
ranking/parent-pool machinery owns the whole drop.  If it falls at a rung, that
rung owns it.

Offline; no network.  Usage: python3 rva_ladder.py <CAPSULE_ROOT> <SEED> <N> <OUT>
"""
from __future__ import annotations

import collections
import json
import math
import os
import random
import sys
import time

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
SEED = int(sys.argv[2]); N = int(sys.argv[3])
OUT = os.path.abspath(sys.argv[4])

from morphology.gs_bound import lane_hetero                   # noqa: E402
from morphology.compile import compile_genome                 # noqa: E402
from evaluation.evaluate import evaluate_genome               # noqa: E402
from evaluation.gs_t1 import evaluate_t1                      # noqa: E402
from evaluation.lifetime2 import _capabilities                # noqa: E402
from evaluation.lifetime import Sim                           # noqa: E402


def main():
    rng = random.Random(SEED)
    t0 = time.time()
    n = 0
    rung = collections.Counter()        # (rung, can_check) over rung-viable
    drawn = collections.Counter()       # can_check over legal draws
    pheno = {}                          # rung -> {prefix: can_check}
    for r in ("T0", "T1", "T2"):
        pheno[r] = {}
    while n < N:
        try:
            g = lane_hetero(rng)
            org = compile_genome(g)
        except Exception:
            continue
        n += 1
        cc = _capabilities(Sim(org))["can_check"]
        drawn[cc] += 1
        try:
            r0 = evaluate_genome(g, tier="T0", use_cache=False)
        except Exception:
            continue
        if not r0["feasible"]:
            continue
        rung[("T0", cc)] += 1
        pheno["T0"].setdefault(r0["phenotype_digest"][:16], cc)
        try:
            r1 = evaluate_t1(g)
        except Exception:
            continue
        if not r1["feasible"]:
            continue
        rung[("T1", cc)] += 1
        pheno["T1"].setdefault(r0["phenotype_digest"][:16], cc)
        try:
            r2 = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        if not r2["feasible"]:
            continue
        rung[("T2", cc)] += 1
        pheno["T2"].setdefault(r0["phenotype_digest"][:16], cc)

    def frac(r):
        k = rung[(r, True)]; tot = k + rung[(r, False)]
        return {"n_viable": tot, "n_can_check": k,
                "fraction": round(k / tot, 8) if tot else None}

    def dfrac(r):
        d = pheno[r]; tot = len(d); k = sum(1 for v in d.values() if v)
        return {"n_distinct_viable": tot, "n_distinct_can_check": k,
                "fraction": round(k / tot, 8) if tot else None}

    out = {
        "study_id": "RV_A_LADDER_ITER3",
        "protocol_freeze": "FREEZE_RVA_ITER3.json",
        "seed": SEED, "n_draws": n,
        "ranking": "NONE -- no rank_fn, no promotion, no parent pool; every "
                   "draw that clears a rung is carried to the next",
        "sampling_can_check_rate": round(drawn[True] / max(1, n), 8),
        "raw": {r: frac(r) for r in ("T0", "T1", "T2")},
        "phenotype_deduped": {r: dfrac(r) for r in ("T0", "T1", "T2")},
        "wall_seconds": round(time.time() - t0, 3),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
