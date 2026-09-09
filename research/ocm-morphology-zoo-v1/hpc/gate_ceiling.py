"""GATE-CEILING census (FREEZE_V1_AMEND_5 prerequisite, quality-gate revival).

UNSCORED (truth only).  A third exact T2 pass over the whole census bound —
identical evaluation path to CENSUS_P00C / HZD9 — computing, per frozen
Archive-D axis, the MAXIMUM dev_score over each occupied cell / CVT-D niche.
For a candidate admission bar b, the per-axis CEILING is the number of cells
whose in-cell max dev >= b: the largest own-axis recovery ANY quality-gated
archive can reach at that bar, regardless of search.  This is the structural
reachability number the amend-5 freeze needs BEFORE choosing the frozen bar:

  - if the census-median bar (HZD9 quality_bar_T2 0.224507) leaves ceilings
    below the amend-3 terminal bar 0.25 on either gated axis (D2d@10, D3d@10),
    the revival would be dead by construction and the freeze must relax the
    bar PROSPECTIVELY with the ceiling ladder as justification;
  - the ceilings also bound what a gate kill can mean: a gated arm failing
    0.25 with ceiling >> 0.25 is a search failure, not a structural one.

Ladder: census-dev quantiles q in (0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1)
computed over FEASIBLE GENOMES exactly as HZD9 computed its median
(sorted_devs[int(q*n)]); q0.5 must EQUAL the HZD9 quality bar (hard xcheck —
third independent census of the same space).

Determinism xchecks (hard): feasible == 28584, census Pareto digest set ==
P00C (792), D2d/D3d occupied cells == P00C (50/83), CVT-D niche occupancy ==
denominator (64), q0.5 == HZD9 quality_bar_T2.

Emits: results/CENSUS_GATE_CEILING_RESULT.json,
      archives/GATE_CEILING_TRUTH.json, manifests/CENSUS_GATE_CEILING_MANIFEST.json

Usage: python3 gate_ceiling.py <capsule_root>
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
from evaluation.descriptors import DESCRIPTOR_REGISTRY, D_DIMS, descriptors_for  # noqa: E402
from evaluation.objectives import objective_vector, pareto_front  # noqa: E402
from morphology.direct_genome import enumerate_census, census_size  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from evaluation.lifetime2 import ECOLOGY_V2  # noqa: E402

RES = os.path.join(ROOT, "results")
ARC = os.path.join(ROOT, "archives")
MAN = os.path.join(ROOT, "manifests")

with open(os.path.join(ARC, "CENSUS_P00C_TRUTH.json")) as f:
    P00C = json.load(f)
PARETO_C = sorted(p["phenotype_digest"] for p in P00C["pareto"])
BOUNDS2 = tuple(tuple(b) for b in P00C["summary"]["frozen_grid_bounds"]["D_dev_2d"])
BOUNDS3 = tuple(tuple(b) for b in P00C["summary"]["frozen_grid_bounds"]["D_dev_3d"])
D2_DIMS = DESCRIPTOR_REGISTRY["D_dev_2d"]["dims"]
D3_DIMS = DESCRIPTOR_REGISTRY["D_dev_3d"]["dims"]
CENTROIDS_D = [tuple(c) for c in P00C["cvtd_centroids"]]
assert BOUNDS2 == tuple(tuple(b) for b in DESCRIPTOR_REGISTRY["D_dev_2d"]["bounds"])
assert BOUNDS3 == tuple(tuple(b) for b in DESCRIPTOR_REGISTRY["D_dev_3d"]["bounds"])
with open(os.path.join(ARC, "HZD9_TRUTH.json")) as f:
    HZ9 = json.load(f)["summary"]

LADDER_Q = (0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1)
DEN_D2D = P00C["summary"]["denominators"]["D2d@10_occupied"]
DEN_D3D = P00C["summary"]["denominators"]["D3d@10_occupied"]
DEN_CVTD = P00C["summary"]["denominators"]["CVTD_occupied_niches"]


def cell(dvals, bounds, res=10):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(dvals, bounds))


def nearest_census_niche_d(ds):
    return min(range(len(CENTROIDS_D)),
               key=lambda c: sum((a - b) ** 2 for a, b in zip(ds, CENTROIDS_D[c])))


def main() -> None:
    t0 = time.time()
    digest = hashlib.sha256(json.dumps(
        {"ecology": ECOLOGY_V2, "purpose": "gate-ceiling-truth-amend5",
         "objectives": 10, "d_dims": list(D_DIMS),
         "d2": list(D2_DIMS), "d3": list(D3_DIMS),
         "census": census_size(), "tier": "T2",
         "ladder_q": list(LADDER_Q)},
    ).encode()).hexdigest()
    receipt = make_receipt("zoo-census-gate-ceiling",
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2", digest)
    maxdev_d2, maxdev_d3, maxdev_niche = {}, {}, {}
    phen = {}            # phenotype_digest -> objective vector (dedup, P00C order)
    devs = []            # per feasible GENOME dev (HZD9-matching quantile base)
    n_total = 0
    for gi, g in enumerate(enumerate_census()):
        n_total += 1
        try:
            r = evaluate_genome(g, tier="T2", use_cache=False)
        except Exception:
            continue
        append_record(receipt, gi, {"g": r["genotype_digest"][:16],
                                    "f": int(r["feasible"])})
        if not r["feasible"]:
            continue
        ev = r["evaluation"]
        org = compile_genome(g)
        d = dev_score(ev)
        devs.append(d)
        c2 = cell(descriptors_for(org, ev, "D_dev_2d"), BOUNDS2)
        c3 = cell(descriptors_for(org, ev, "D_dev_3d"), BOUNDS3)
        nich = nearest_census_niche_d(descriptors_for(org, ev, "D_developmental"))
        maxdev_d2[c2] = max(maxdev_d2.get(c2, d), d)
        maxdev_d3[c3] = max(maxdev_d3.get(c3, d), d)
        maxdev_niche[nich] = max(maxdev_niche.get(nich, d), d)
        if r["phenotype_digest"] not in phen:
            phen[r["phenotype_digest"]] = {
                "p": r["phenotype_digest"],
                "obj": [float(x) for x in objective_vector(ev)]}
    assert verify_receipt(receipt), "receipt chain broken"

    # ---- ladder bars (over feasible genomes, HZD9 quantile convention) ----
    sdevs = sorted(devs)
    n = len(sdevs)
    ladder = {}
    for q in LADDER_Q:
        bar = sdevs[min(n - 1, int(q * n))]
        ladder["q%g" % q] = {
            "bar": round(bar, 6),
            "admissible_fraction_feasible": round(
                sum(1 for d in devs if d >= bar) / n, 6),
            "ceil_D2d_cells": sum(1 for m in maxdev_d2.values() if m >= bar),
            "ceil_D2d_recovery": round(
                sum(1 for m in maxdev_d2.values() if m >= bar) / DEN_D2D, 6),
            "ceil_D3d_cells": sum(1 for m in maxdev_d3.values() if m >= bar),
            "ceil_D3d_recovery": round(
                sum(1 for m in maxdev_d3.values() if m >= bar) / DEN_D3D, 6),
            "ceil_CVTD_niches": sum(1 for m in maxdev_niche.values() if m >= bar),
            "ceil_CVTD_recovery": round(
                sum(1 for m in maxdev_niche.values() if m >= bar) / DEN_CVTD, 6),
        }

    # ---- determinism xchecks (hard) ---------------------------------------
    items = list(phen.values())
    front = pareto_front(items, vec_key="obj")
    pareto = sorted(items[i]["p"] for i in front)
    xcheck = {
        "pareto_equals_P00C": pareto == PARETO_C,
        "pareto_size": len(pareto),
        "cells_D2d_equals_P00C":
            {"%s" % (c,): 1 for c in maxdev_d2} ==
            {k: 1 for k in P00C["cells_D2d10"]},
        "cells_D3d_equals_P00C":
            {"%s" % (c,): 1 for c in maxdev_d3} ==
            {k: 1 for k in P00C["cells_D3d10"]},
        "cvtd_occupancy_equals_denominator":
            len(maxdev_niche) == DEN_CVTD,
        "feasible_equals_P00C": n == P00C["summary"]["feasible"],
        "q0.5_equals_HZD9_quality_bar":
            ladder["q0.5"]["bar"] == HZ9["quality_bar_T2"],
    }
    for k in ("pareto_equals_P00C", "cells_D2d_equals_P00C",
              "cells_D3d_equals_P00C", "cvtd_occupancy_equals_denominator",
              "feasible_equals_P00C", "q0.5_equals_HZD9_quality_bar"):
        assert xcheck[k], "GATE-CEILING xcheck %s failed" % k

    summary = {
        "run_id": "zoo-census-gate-ceiling", "tier": "T2",
        "ecology_id": ECOLOGY_V2["ecology_id"],
        "census_size": census_size(), "evaluated": n_total, "feasible": n,
        "denominators": {"D2d@10_occupied": DEN_D2D,
                         "D3d@10_occupied": DEN_D3D,
                         "CVTD_occupied_niches": DEN_CVTD,
                         "PARETO_T2": P00C["summary"]["pareto_set_size"]},
        "ladder": ladder,
        "per_axis_cells_maxdev": {
            "D2d": {"%s" % (c,): round(m, 6) for c, m in sorted(maxdev_d2.items())},
            "D3d": {"%s" % (c,): round(m, 6) for c, m in sorted(maxdev_d3.items())},
            "CVTD": {"%d" % c: round(m, 6) for c, m in sorted(maxdev_niche.items())},
        },
        "xcheck_vs_P00C_HZD9": xcheck,
        "wall_s": round(time.time() - t0, 3),
        "receipt_head": receipt["head_sha256"],
        "config_digest": digest,
    }
    os.makedirs(RES, exist_ok=True)
    os.makedirs(ARC, exist_ok=True)
    os.makedirs(MAN, exist_ok=True)
    with open(os.path.join(RES, "CENSUS_GATE_CEILING_RESULT.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(ARC, "GATE_CEILING_TRUTH.json"), "w") as f:
        json.dump({"summary": summary, "receipt": receipt}, f, indent=1)
    with open(os.path.join(MAN, "CENSUS_GATE_CEILING_MANIFEST.json"), "w") as f:
        json.dump({"config_digest": digest,
                   "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                  f, indent=1)
    print(json.dumps({"ladder": ladder, "xcheck": xcheck}, sort_keys=True))


if __name__ == "__main__":
    main()
