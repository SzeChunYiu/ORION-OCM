#!/usr/bin/env python3
"""RV-A: per-tier evaluation cost, and the surrogate's ranking overhead.

Successive halving pays a ranking cost to avoid evaluating every candidate at
the expensive tier.  Its benefit therefore scales with the tier COST RATIO.
This measures that ratio on the frozen stack, plus the per-candidate cost of the
surrogate allocation score that the R2 arms rank with.

Offline; no network.  Usage: python3 rva_tiercost.py <CAPSULE_ROOT> <N> <OUT>
"""
from __future__ import annotations

import json, os, random, sys, time

ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
N = int(sys.argv[2]); OUT = os.path.abspath(sys.argv[3])

from morphology.gs_bound import lane_hetero                   # noqa: E402
from evaluation.evaluate import evaluate_genome               # noqa: E402
from evaluation.gs_t1 import evaluate_t1                      # noqa: E402
from evaluation.t3_ecology import evaluate_t3                 # noqa: E402
from search.surrogate_allocate import EnsembleSurrogate       # noqa: E402

freeze = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R2_FREEZE.json")))
T3KEY = freeze["t3_key"]
impl = freeze["environment"]["surrogate_impl"]

rng = random.Random(11)
gs = []
while len(gs) < N:
    try:
        gs.append(lane_hetero(rng))
    except Exception:
        continue

def timeit(fn, items):
    t = time.process_time()
    n = 0
    for g in items:
        try:
            fn(g); n += 1
        except Exception:
            pass
    return (time.process_time() - t) / max(1, n), n

t0_s, n0 = timeit(lambda g: evaluate_genome(g, tier="T0", use_cache=False), gs)
t1_s, n1 = timeit(evaluate_t1, gs)
t2_s, n2 = timeit(lambda g: evaluate_genome(g, tier="T2", use_cache=False), gs)
t3_s, n3 = timeit(lambda g: evaluate_t3(g, T3KEY), gs)

# surrogate: train on a T0 cohort, then time allocation_score per candidate
sur = EnsembleSurrogate(seed=0, impl=impl)
recs = []
for g in gs[:min(400, len(gs))]:
    r = evaluate_genome(g, tier="T0", use_cache=False)
    recs.append({"genome": g.to_json_obj(), "feasible": bool(r["feasible"]),
                 "evaluation": r["evaluation"]})
try:
    sur.train_t0(recs)
except Exception as e:
    print("train_t0 failed:", repr(e)[:120])
alloc_s, na = timeit(sur.allocation_score, gs[:min(2000, len(gs))])

out = {
    "probe_id": "RVA_TIER_COST_V1",
    "surrogate_impl": impl,
    "n_timed": {"T0": n0, "T1": n1, "T2": n2, "T3": n3, "alloc": na},
    "sec_per_eval": {"T0": round(t0_s, 9), "T1": round(t1_s, 9),
                     "T2": round(t2_s, 9), "T3": round(t3_s, 9)},
    "sec_per_allocation_score": round(alloc_s, 9),
    "tier_cost_ratio_T2_over_T0": round(t2_s / max(1e-12, t0_s), 4),
    "alloc_score_cost_in_T0_units": round(alloc_s / max(1e-12, t0_s), 4),
    "read": ("successive halving's saving is bounded by the tier cost ratio: "
             "with eta=3 over T0->T1->T2 it avoids ~(1-1/3) of T1 and ~(1-1/9) "
             "of T2 evaluations, so the saving is small when T2/T0 is small, "
             "while the ranking it pays for costs alloc_score_cost_in_T0_units "
             "T0-evaluations per ranked candidate"),
}
with open(OUT, "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
