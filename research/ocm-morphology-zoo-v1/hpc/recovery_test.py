"""MZ-D2 optimizer recovery test: each search arm vs exhaustive census truth.

Denominators are FROZEN to census truth (FREEZE_V1.json): the exact Pareto
set, the census-OCCUPIED descriptor cells (not the full 10x10 grid), and the
census best dev_score.  Reports per arm x seed:
  pareto_recovery  fraction of census Pareto phenotypes rediscovered
  cell_recovery    fraction of census-occupied cells (arm's own archive
                   axis) rediscovered
  best_dev_gap     census best dev_score - arm best dev score
Usage: python3 recovery_test.py <capsule_root> [budget] [seeds...]
"""
from __future__ import annotations

import ast
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
BUDGET = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
SEEDS = [int(s) for s in sys.argv[3:]] or [0, 1, 2]

from search import (cvt_map_elites, lexicase, map_elites, mome, novelty,  # noqa: E402
                     nsga, nslc, random_search)
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from search.map_elites import grid_indices  # noqa: E402

# arm -> (module, archive axis its search uses)
ARMS = {
    "P01_random_search": (random_search, "S_structural_2d"),
    "P02_nsga2": (nsga, "S_structural_2d"),
    "P03_map_elites": (map_elites, "S_structural_2d"),
    "P04_nslc": (nslc, "B_behavior_2d"),
    "P05_map_elites_B": (map_elites, "B_behavior_2d"),
    "P06_cvt_map_elites": (cvt_map_elites, "S_cvtd"),
    "P09_mome": (mome, "S_structural_2d"),
    "P11_lexicase": (lexicase, "B_behavior_2d"),
}

with open(os.path.join(ROOT, "archives", "CENSUS_P00_TRUTH.json")) as f:
    TRUTH = json.load(f)
PARETO_DIGESTS = {p["phenotype_digest"] for p in TRUTH["pareto"]}
BEST_DEV = TRUTH["summary"]["best_dev_score"]


def truth_cells(key: str) -> set:
    return {tuple(ast.literal_eval(k)) for k in TRUTH[key]}


CELLS_S = truth_cells("cells_S")
CELLS_B = truth_cells("cells_B")


def cells_hit(recs, regname):
    """Recompute descriptors from genomes so every arm is scored on both
    axes uniformly (an arm's own archive axis may be CVT/high-D)."""
    reg = DESCRIPTOR_REGISTRY[regname]
    out = set()
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        org = compile_genome(g)
        ev = evaluate_genome(g)["evaluation"]
        d = descriptors_for(org, ev, regname)
        out.add(grid_indices(tuple(d), reg["bounds"], 10))
    return out


def main():
    rows = []
    for arm, (mod, axis) in ARMS.items():
        for seed in SEEDS:
            t0 = time.time()
            if arm == "P05_map_elites_B":
                res = mod.run(budget=BUDGET, seed=seed, archive="B_behavior_2d")
            elif arm == "P06_cvt_map_elites":
                res = mod.run(budget=BUDGET, seed=seed, archive="S_cvtd")
            else:
                res = mod.run(budget=BUDGET, seed=seed)
            recs = res["archive"]
            digs = {r["phenotype_digest"] for r in recs}
            pareto_rec = len(digs & PARETO_DIGESTS) / len(PARETO_DIGESTS)
            hit_S = cells_hit(recs, "S_structural_2d")
            hit_B = cells_hit(recs, "B_behavior_2d")
            best = max((r["dev_score"] for r in recs), default=None)
            rows.append({
                "arm": arm, "seed": seed, "evals": res["evals"],
                "elapsed_s": res.get("elapsed_s", round(time.time() - t0, 1)),
                "n_elites": len(recs),
                "pareto_recovery": round(pareto_rec, 6),
                "S_cell_recovery": round(len(hit_S & CELLS_S) / len(CELLS_S), 6),
                "B_cell_recovery": round(len(hit_B & CELLS_B) / len(CELLS_B), 6),
                "cell_axis": axis,
                "best_dev": best,
                "best_dev_gap": (round(BEST_DEV - best, 6)
                                 if best is not None else None),
            })
            print(json.dumps(rows[-1], sort_keys=True), flush=True)
    with open(os.path.join(ROOT, "results", "RECOVERY_TEST.json"), "w") as f:
        json.dump({"budget": BUDGET, "seeds": SEEDS,
                   "truth": {"pareto": len(PARETO_DIGESTS),
                             "cells_S": len(CELLS_S), "cells_B": len(CELLS_B),
                             "best_dev": BEST_DEV},
                   "rows": rows}, f, indent=1)
    # compact per-arm aggregate
    agg = {}
    for r in rows:
        a = agg.setdefault(r["arm"], {"seeds": 0, "pareto": 0.0, "S": 0.0,
                                      "B": 0.0, "gap": 0.0, "gap_n": 0})
        a["seeds"] += 1
        a["pareto"] += r["pareto_recovery"]
        a["S"] += r["S_cell_recovery"]
        a["B"] += r["B_cell_recovery"]
        if r["best_dev_gap"] is not None:
            a["gap"] += r["best_dev_gap"]
            a["gap_n"] += 1
    print("ARM SUMMARY (mean over seeds; denominators = census truth)")
    for arm, a in sorted(agg.items()):
        print("%-20s pareto=%.4f S_cell=%.4f B_cell=%.4f gap=%.6f" % (
            arm, a["pareto"] / a["seeds"], a["S"] / a["seeds"],
            a["B"] / a["seeds"], a["gap"] / max(1, a["gap_n"])))


if __name__ == "__main__":
    main()
