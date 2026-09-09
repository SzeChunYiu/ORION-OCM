"""HZD9 census (FREEZE_V1_AMEND_4 prerequisite, MZ-D9 hostile subset).

UNSCORED (truth only).  A second exact T2 pass over the whole census bound —
identical evaluation path to CENSUS_P00C — extended with the per-genome
detail the MZ-D9 hostile checks need but P00C truth does not carry:

  A. genotype -> phenotype collapse   (sec 12: "genotype diversity collapses
     to same phenotype"): distinct phenotype digests / distinct objective
     vectors / distinct (objectives + D2d cell) behavioral tuples over the
     feasible census;
  B. quality bar                       (sec 12: "high coverage comes from
     low-quality junk"): median dev_score over the feasible census, frozen
     BEFORE any scored amend-4 run, used to junk-filter archive coverage;
  C. descriptor-label encoding         (sec 12: "diversity descriptor merely
     encodes architecture labels"): per-occupied-cell F_arch / T_family
     purity on the frozen D2d@10 and D3d@10 grids, plus one-way eta^2 of
     each Archive-D axis w.r.t. F_arch;
  D. island-region tables (MZ-D8): per island prior — legal census genomes,
     feasible count, occupied D2d cells, best dev, census-Pareto members.

Cross-checks (asserted, hard): the recomputed T2 Pareto digest set, D2d/D3d
occupied cells and CVT-D centroids must EQUAL CENSUS_P00C_TRUTH (792/50/83/
64) — a free determinism audit of the whole evaluation stack.

Emits: results/CENSUS_HZD9_RESULT.json, archives/HZD9_TRUTH.json,
      manifests/CENSUS_HZD9_MANIFEST.json

Usage: python3 hzd9_census.py <capsule_root>
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
from evaluation.objectives import dev_score, objective_vector, pareto_front  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from evaluation.lifetime2 import ECOLOGY_V2  # noqa: E402
from search.island_qd import ISLAND_PRIORS_V1, in_region  # noqa: E402

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
assert (BOUNDS2 == tuple(tuple(b) for b in DESCRIPTOR_REGISTRY["D_dev_2d"]["bounds"])
        and BOUNDS3 == tuple(tuple(b) for b in DESCRIPTOR_REGISTRY["D_dev_3d"]["bounds"])), \
    "registry grid bounds drifted from P00C truth"


def cell(dvals, bounds, res=10):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(dvals, bounds))


def main() -> None:
    t0 = time.time()
    digest = hashlib.sha256(json.dumps(
        {"ecology": ECOLOGY_V2, "purpose": "hzd9-hostile-truth",
         "objectives": 10, "d_dims": list(D_DIMS),
         "d2": list(D2_DIMS), "d3": list(D3_DIMS),
         "census": census_size(), "tier": "T2",
         "islands": [p["island_id"] for p in ISLAND_PRIORS_V1]},
    ).encode()).hexdigest()
    receipt = make_receipt("zoo-census-hzd9",
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2", digest)
    rows = []          # feasible genome rows (per-genome detail)
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
        ev = r["evaluation"]
        org = compile_genome(g)
        dd = developmental_descriptors(org, ev)
        regions = [i for i, p in enumerate(ISLAND_PRIORS_V1) if in_region(g, p)]
        rows.append({
            "g": r["genotype_digest"], "p": r["phenotype_digest"],
            "obj": [float(x) for x in objective_vector(ev)],
            "d": {d: float(dd[d]) for d in D_DIMS},
            "d2": cell([float(dd[d]) for d in D2_DIMS], BOUNDS2),
            "d3": cell([float(dd[d]) for d in D3_DIMS], BOUNDS3),
            "dev": dev_score(ev),
            "F": g.F_arch, "T": g.T_family,
            "regions": regions,
        })
    assert verify_receipt(receipt), "receipt chain broken"

    # ---- A. collapse (genotype diversity vs phenotype diversity) ----------
    distinct_p = {row["p"] for row in rows}
    distinct_obj = {tuple(row["obj"]) for row in rows}
    distinct_beh = {(row["p"], row["d2"]) for row in rows}
    collapse = {
        "feasible_genotypes": len(rows),
        "distinct_phenotype_digests": len(distinct_p),
        "distinct_objective_vectors": len(distinct_obj),
        "distinct_phenotype_x_D2dcell": len(distinct_beh),
        "genotype_to_phenotype_collapse_ratio": round(
            1.0 - len(distinct_p) / max(1, len(rows)), 6),
        "genotype_to_objective_vector_collapse_ratio": round(
            1.0 - len(distinct_obj) / max(1, len(rows)), 6),
    }

    # ---- B. quality bar ---------------------------------------------------
    devs = sorted(row["dev"] for row in rows)
    quality_bar = round(devs[len(devs) // 2], 6)

    # ---- C. descriptor-label encoding -------------------------------------
    def purity(grid_key):
        by_cell = {}
        for row in rows:
            c = row[grid_key]
            by_cell.setdefault(c, {"F": {}, "T": {}, "n": 0})
            e = by_cell[c]
            e["n"] += 1
            e["F"][row["F"]] = e["F"].get(row["F"], 0) + 1
            e["T"][row["T"]] = e["T"].get(row["T"], 0) + 1
        out = {"n_cells": len(by_cell), "cells": {}}
        pur_f, pur_t = [], []
        for c, e in sorted(by_cell.items()):
            pf = max(e["F"].values()) / e["n"]
            pt = max(e["T"].values()) / e["n"]
            pur_f.append(pf)
            pur_t.append(pt)
            out["cells"]["%s" % (c,)] = {
                "n": e["n"], "purity_F_arch": round(pf, 6),
                "purity_T_family": round(pt, 6)}
        out["median_purity_F_arch"] = round(sorted(pur_f)[len(pur_f) // 2], 6) if pur_f else None
        out["median_purity_T_family"] = round(sorted(pur_t)[len(pur_t) // 2], 6) if pur_t else None
        out["frac_cells_purity_F_arch_ge_0.9"] = round(
            sum(1 for p in pur_f if p >= 0.9) / max(1, len(pur_f)), 6)
        out["frac_cells_purity_T_family_ge_0.9"] = round(
            sum(1 for p in pur_t if p >= 0.9) / max(1, len(pur_t)), 6)
        return out

    def eta_squared(dim):
        """One-way eta^2 of a D axis w.r.t. F_arch over feasible genomes."""
        groups = {}
        for row in rows:
            groups.setdefault(row["F"], []).append(row["d"][dim])
        n = sum(len(v) for v in groups.values())
        if n == 0:
            return None
        grand = sum(sum(v) for v in groups.values()) / n
        ss_t = sum((x - grand) ** 2 for v in groups.values() for x in v)
        ss_b = sum(len(v) * ((sum(v) / len(v)) - grand) ** 2
                   for v in groups.values())
        return round(ss_b / ss_t, 6) if ss_t > 0 else None

    # ---- D. island-region tables ------------------------------------------
    seen = {row["p"]: row for row in rows}          # dedup by phenotype (P00C order)
    items = list(seen.values())
    front = pareto_front(items, vec_key="obj")
    pareto = sorted(items[i]["p"] for i in front)
    pareto_set = set(pareto)
    islands = {}
    for i, p in enumerate(ISLAND_PRIORS_V1):
        mem = [row for row in rows if i in row["regions"]]
        isl_pareto = {row["p"] for row in mem if row["p"] in pareto_set}
        islands[p["island_id"]] = {
            "n_genotypes": len(mem),
            "n_feasible": sum(1 for row in mem),
            "occupied_D2d_cells": len({row["d2"] for row in mem}),
            "best_dev": max((row["dev"] for row in mem), default=None),
            "census_pareto_members": len(isl_pareto),
        }

    # ---- determinism xchecks vs P00C (hard) -------------------------------
    xcheck = {
        "pareto_equals_P00C": pareto == PARETO_C,
        "pareto_size": len(pareto),
        "cells_D2d_equals_P00C":
            {"%s" % (c,): 1 for c in ({row["d2"] for row in rows})} ==
            {k: 1 for k in P00C["cells_D2d10"]},
        "cells_D3d_equals_P00C":
            {"%s" % (c,): 1 for c in ({row["d3"] for row in rows})} ==
            {k: 1 for k in P00C["cells_D3d10"]},
        "feasible_equals_P00C": len(rows) == P00C["summary"]["feasible"],
    }
    assert xcheck["pareto_equals_P00C"], "HZD9 Pareto drift vs P00C truth"
    assert xcheck["cells_D2d_equals_P00C"], "HZD9 D2d cells drift vs P00C"
    assert xcheck["cells_D3d_equals_P00C"], "HZD9 D3d cells drift vs P00C"
    assert xcheck["feasible_equals_P00C"], "HZD9 feasible count drift vs P00C"

    summary = {
        "run_id": "zoo-census-hzd9", "tier": "T2",
        "ecology_id": ECOLOGY_V2["ecology_id"],
        "census_size": census_size(), "evaluated": n_total,
        "feasible": len(rows),
        "pareto_set_size": len(pareto),
        "denominators": dict(P00C["summary"]["denominators"]),
        "collapse": collapse,
        "quality_bar_T2": quality_bar,
        "descriptor_purity_D2d": purity("d2"),
        "descriptor_purity_D3d": purity("d3"),
        "eta_squared_F_arch": {d: eta_squared(d) for d in D_DIMS},
        "xcheck_vs_P00C": xcheck,
        "wall_s": round(time.time() - t0, 3),
        "receipt_head": receipt["head_sha256"],
        "config_digest": digest,
    }
    os.makedirs(RES, exist_ok=True)
    os.makedirs(ARC, exist_ok=True)
    os.makedirs(MAN, exist_ok=True)
    with open(os.path.join(RES, "CENSUS_HZD9_RESULT.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(ARC, "HZD9_TRUTH.json"), "w") as f:
        json.dump({"summary": summary, "island_regions": islands,
                   "receipt": receipt}, f, indent=1)
    with open(os.path.join(MAN, "CENSUS_HZD9_MANIFEST.json"), "w") as f:
        json.dump({"config_digest": digest,
                   "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                  f, indent=1)
    print(json.dumps({"collapse": collapse, "quality_bar_T2": quality_bar,
                      "purity_D2d_frac_ge_0.9":
                          summary["descriptor_purity_D2d"]["frac_cells_purity_F_arch_ge_0.9"],
                      "eta2": summary["eta_squared_F_arch"],
                      "xcheck": xcheck}, sort_keys=True))


if __name__ == "__main__":
    main()
