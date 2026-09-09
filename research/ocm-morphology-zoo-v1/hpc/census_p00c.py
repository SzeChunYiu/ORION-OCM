"""P00C census (FREEZE_V1_AMEND_3 prerequisite): exact T2 truth over the
whole census bound under LIFETIME_ECOLOGY_V2 (MZ-D7 developmental battery).

UNSCORED (truth only).  FREEZE_V1_AMEND_3.json denominators, Archive D grid
bounds, and the T2 scalar references (W2_REF/B2_REF = feasible medians) are
taken from this file BEFORE any scored T2 run.  Controls: feasible count and
T0 Pareto/feasible structure stay owned by CENSUS_P00_TRUTH.json (untouched);
this file adds the T2 layer only.

Emits:
  results/CENSUS_P00C_RESULT.json  (summary)
  archives/CENSUS_P00C_TRUTH.json  (cells, Pareto digests, CVT-D centroids,
                                    D-axis ranges, retention distribution)
  manifests/CENSUS_P00C_MANIFEST.json

Usage: python3 census_p00c.py <capsule_root>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

from morphology.compile import compile_genome  # noqa: E402
from evaluation.descriptors import (DESCRIPTOR_REGISTRY, D_DIMS,  # noqa: E402
                                    descriptors_for, developmental_descriptors)
from morphology.direct_genome import enumerate_census, census_size  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import objective_vector, pareto_front  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from evaluation.lifetime2 import ECOLOGY_V2  # noqa: E402

RES = os.path.join(ROOT, "results")
ARC = os.path.join(ROOT, "archives")
MAN = os.path.join(ROOT, "manifests")

K = 64
D2_DIMS = ("marginal_acquisition_slope", "persistent_growth_per_capability")
# third axis: primitive_pressure_slope — consolidation_ratio is identically 0
# over the frozen census space (no maintenance-charged topology / L present),
# a dead axis for grid views (P00C finding, 2026-09-09)
D3_DIMS = D2_DIMS + ("primitive_pressure_slope",)


def q05(x: float) -> float:
    """Quantize to 0.05 outward step for frozen grid bounds."""
    import math
    return math.floor(x * 20.0) / 20.0, math.ceil(x * 20.0) / 20.0


def kmeans_exhaustive(points, k, iters=30):
    pts = sorted(points)
    cents = [pts[(i * len(pts)) // k] for i in range(k)]
    cents = sorted(set(cents))[:k]
    for _ in range(iters):
        assign = []
        for p in pts:
            j = min(range(len(cents)),
                    key=lambda c: sum((a - b) ** 2 for a, b in zip(p, cents[c])))
            assign.append(j)
        new = []
        for c in range(len(cents)):
            mem = [p for p, a in zip(pts, assign) if a == c]
            new.append(tuple(sum(m[d] for m in mem) / len(mem) for d in range(len(pts[0])))
                       if mem else cents[c])
        new = sorted(set(new))
        if new == cents:
            break
        cents = new
    return cents


def main() -> None:
    t0 = time.time()
    digest = hashlib.sha256(json.dumps(
        {"ecology": ECOLOGY_V2, "k": K, "objectives": 10,
         "d_dims": list(D_DIMS), "d2": list(D2_DIMS), "d3": list(D3_DIMS),
         "census": census_size(), "tier": "T2"}).encode()).hexdigest()
    receipt = make_receipt("zoo-census-p00c",
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2", digest)
    feasible_rows = []
    d_ranges = {d: [float("inf"), float("-inf")] for d in D_DIMS}
    n_total = 0
    for gi, g in enumerate(enumerate_census()):
        n_total += 1
        try:
            r = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        append_record(receipt, gi, {"g": r["genotype_digest"][:16],
                                    "p": r["phenotype_digest"][:16],
                                    "f": int(r["feasible"])})
        if not r["feasible"]:
            continue
        org = compile_genome(g)
        ev = r["evaluation"]
        dd = developmental_descriptors(org, ev)
        for d in D_DIMS:
            v = float(dd[d])
            if v < d_ranges[d][0]:
                d_ranges[d][0] = v
            if v > d_ranges[d][1]:
                d_ranges[d][1] = v
        rc = ev.get("reset_control", {})
        feasible_rows.append({
            "p": r["phenotype_digest"],
            "obj": objective_vector(ev),
            "d": {d: float(dd[d]) for d in D_DIMS},
            "work": ev["work_total"],
            "bytes": ev["persistent_bytes"],
            "solved": ev["solved_fraction"],
            "reset_solved": rc.get("solved_fraction"),
            "reset_work": rc.get("work_total"),
        })
    assert verify_receipt(receipt), "receipt chain broken"
    # exact T2 Pareto (dedup by phenotype)
    seen = {}
    for row in feasible_rows:
        seen[row["p"]] = row
    items = list(seen.values())
    front = pareto_front(items, vec_key="obj")
    pareto = sorted(items[i]["p"] for i in front)
    # frozen grid bounds: empirical range quantized outward to 0.05
    bounds2 = tuple((q05(d_ranges[d][0])[0], q05(d_ranges[d][1])[1]) for d in D2_DIMS)
    bounds3 = tuple((q05(d_ranges[d][0])[0], q05(d_ranges[d][1])[1]) for d in D3_DIMS)

    def cell(dvals, bounds, res=10):
        return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                     for dv, b in zip(dvals, bounds))
    d2_of = {row["p"]: cell([row["d"][d] for d in D2_DIMS], bounds2) for row in items}
    d3_of = {row["p"]: cell([row["d"][d] for d in D3_DIMS], bounds3) for row in items}
    cells_d2 = sorted(set(d2_of.values()))
    cells_d3 = sorted(set(d3_of.values()))
    # CVT-D over all 5 developmental dims
    pts5 = [tuple(row["d"][d] for d in D_DIMS) for row in items]
    cents = kmeans_exhaustive(pts5, K)
    niche = {}
    for row in items:
        pv = tuple(row["d"][d] for d in D_DIMS)
        j = min(range(len(cents)),
                key=lambda c: sum((a - b) ** 2 for a, b in zip(pv, cents[c])))
        niche[j] = niche.get(j, 0) + 1
    # T2 scalar references: MEDIANS over feasible (frozen before scored runs)
    works = sorted(row["work"] for row in items)
    byts = sorted(row["bytes"] for row in items)
    w2_ref = works[len(works) // 2]
    b2_ref = byts[len(byts) // 2]
    # retention distribution (continued minus reset)
    ret = [row["solved"] - row["reset_solved"] for row in items
           if row["reset_solved"] is not None]
    retention = {
        "n": len(ret),
        "positive": sum(1 for x in ret if x > 1e-9),
        "zero": sum(1 for x in ret if abs(x) <= 1e-9),
        "negative": sum(1 for x in ret if x < -1e-9),
        "max": round(max(ret), 6) if ret else None,
    }
    summary = {
        "run_id": "zoo-census-p00c",
        "tier": "T2",
        "ecology_id": ECOLOGY_V2["ecology_id"],
        "census_size": census_size(),
        "evaluated": n_total,
        "feasible": len(items),
        "pareto_set_size": len(pareto),
        "denominators": {
            "D2d@10_occupied": len(cells_d2),
            "D3d@10_occupied": len(cells_d3),
            "CVTD_occupied_niches": len(niche),
            "CVTD_k_after_dedup": len(cents),
        },
        "d_axis_ranges": {d: [round(lo, 6), round(hi, 6)]
                          for d, (lo, hi) in sorted(d_ranges.items())},
        "frozen_grid_bounds": {
            "D_dev_2d": [list(b) for b in bounds2],
            "D_dev_3d": [list(b) for b in bounds3],
        },
        "t2_scalar_refs": {"W2_REF": w2_ref, "B2_REF": b2_ref},
        "retention_distribution": retention,
        "wall_s": round(time.time() - t0, 3),
        "receipt_head": receipt["head_sha256"],
        "config_digest": digest,
    }
    os.makedirs(RES, exist_ok=True)
    os.makedirs(ARC, exist_ok=True)
    os.makedirs(MAN, exist_ok=True)
    with open(os.path.join(RES, "CENSUS_P00C_RESULT.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(ARC, "CENSUS_P00C_TRUTH.json"), "w") as f:
        json.dump({"summary": summary,
                   "pareto": [{"phenotype_digest": p} for p in pareto],
                   "cells_D2d10": {"%s" % (c,): 1 for c in cells_d2},
                   "cells_D3d10": {"%s" % (c,): 1 for c in cells_d3},
                   "cvtd_centroids": [list(c) for c in cents],
                   "cvtd_niche_sizes": niche,
                   "receipt": receipt}, f, indent=1)
    with open(os.path.join(MAN, "CENSUS_P00C_MANIFEST.json"), "w") as f:
        json.dump({"config_digest": digest, "k": K,
                   "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                  f, indent=1)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
