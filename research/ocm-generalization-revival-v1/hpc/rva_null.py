#!/usr/bin/env python3
"""RV-A iteration 2: the lane-distributed null.

Question: is the checker-depletion of the GS-R2 survivor set owned by the T2
GATE (frozen physics -> structural) or by the RANKING/PROMOTION machinery
(operational -> a lever has a target)?

Method: draw from lane_hetero -- the lane every R2 arm used -- and evaluate
EVERY draw at T2 with all ranking machinery disabled: no novelty archive, no
novelty gate, no surrogate, no successive halving, no dedup promotion, no
cross-round promotion.  Report P(can_check | T2-viable) against the observed
survivor rate.

Protocol frozen in FREEZE_RVA_ITER2.json before this ran.  Offline; no network.
Usage: python3 rva_null.py <CAPSULE_ROOT> <SEED> <N_DRAWS> <OUT_JSON>
"""
from __future__ import annotations

import collections
import json
import math
import os
import random
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)
SEED = int(sys.argv[2])
NDRAWS = int(sys.argv[3])
OUT = os.path.abspath(sys.argv[4])

from morphology.compile import InvariantViolation             # noqa: E402
from morphology.gs_bound import lane_hetero                   # noqa: E402
from evaluation.evaluate import evaluate_genome               # noqa: E402
from evaluation.lifetime2 import _capabilities                # noqa: E402
from evaluation.lifetime import Sim                           # noqa: E402
from morphology.compile import compile_genome                 # noqa: E402


def main():
    rng = random.Random(SEED)
    t0 = time.time()

    n_draw = n_legal = n_viable = 0
    n_can_check = n_viable_can_check = 0
    n_viable_fibred = 0
    viable_pheno = {}                       # phenotype -> (can_check, F_arch)
    all_pheno = set()
    farch_viable = collections.Counter()
    farch_draw = collections.Counter()
    viable_by_cc = collections.Counter()    # (can_check, viable)
    # falsifier: a viable organism that is neither can_check nor fibred would
    # break the T2 correctness-route claim outright.
    impossible_cell = []

    while n_draw < NDRAWS:
        n_draw += 1
        try:
            g = lane_hetero(rng)
            org = compile_genome(g)
        except InvariantViolation:
            continue
        except Exception:
            continue
        n_legal += 1
        cc = _capabilities(Sim(org))["can_check"]
        fib = (g.F_arch == "hierarchical_fibred")
        n_can_check += 1 if cc else 0
        farch_draw[g.F_arch] += 1
        try:
            r = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        ph = r["phenotype_digest"]
        all_pheno.add(ph)
        viable = bool(r["feasible"])
        viable_by_cc[(cc, viable)] += 1
        if viable:
            n_viable += 1
            n_viable_can_check += 1 if cc else 0
            n_viable_fibred += 1 if fib else 0
            farch_viable[g.F_arch] += 1
            viable_pheno.setdefault(ph, (cc, g.F_arch))
            if (not cc) and (not fib) and len(impossible_cell) < 20:
                impossible_cell.append({"phenotype_digest": ph,
                                        "F_arch": g.F_arch, "L": g.L})

    d_n = len(viable_pheno)
    d_cc = sum(1 for cc, _ in viable_pheno.values() if cc)
    out = {
        "study_id": "RV_A_NULL_ITER2",
        "protocol_freeze": "FREEZE_RVA_ITER2.json",
        "lane": "hetero",
        "ranking_machinery": "DISABLED (no novelty archive/gate, no surrogate, "
                             "no successive halving, no dedup promotion, no "
                             "cross-round promotion)",
        "seed": SEED,
        "n_draws": n_draw,
        "n_legal": n_legal,
        "n_viable_raw": n_viable,
        "n_can_check_drawn": n_can_check,
        "sampling_can_check_rate": round(n_can_check / max(1, n_legal), 8),
        "viable_rate_raw": round(n_viable / max(1, n_legal), 8),
        "raw": {"n_viable": n_viable, "n_viable_can_check": n_viable_can_check,
                "can_check_fraction": round(n_viable_can_check / max(1, n_viable), 8),
                "fibred_fraction": round(n_viable_fibred / max(1, n_viable), 8)},
        "phenotype_deduped": {
            "n_distinct_viable": d_n, "n_distinct_viable_can_check": d_cc,
            "can_check_fraction": round(d_cc / max(1, d_n), 8),
            "n_distinct_all": len(all_pheno)},
        "gate_selection": {
            "n_can_check_viable": viable_by_cc[(True, True)],
            "n_can_check_dead": viable_by_cc[(True, False)],
            "n_no_check_viable": viable_by_cc[(False, True)],
            "n_no_check_dead": viable_by_cc[(False, False)],
            "P_viable_given_can_check": round(
                viable_by_cc[(True, True)] / max(1, viable_by_cc[(True, True)]
                                                 + viable_by_cc[(True, False)]), 8),
            "P_viable_given_not_can_check": round(
                viable_by_cc[(False, True)] / max(1, viable_by_cc[(False, True)]
                                                  + viable_by_cc[(False, False)]), 8)},
        "farch_draw": dict(farch_draw),
        "farch_viable": dict(farch_viable),
        "falsifier_viable_without_check_and_without_fibred": {
            "n_found": len(impossible_cell), "samples": impossible_cell,
            "expected": 0,
            "note": "a viable organism with neither can_check nor "
                    "hierarchical_fibred would refute the T2 correctness-route "
                    "mechanism outright"},
        "wall_seconds": round(time.time() - t0, 3),
        "python": sys.version.split()[0],
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
