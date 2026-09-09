"""AMEND-1 worker: one (arm, seed) at the FROZEN budget under
FREEZE_V1_AMEND_1.json (finer/higher-D descriptor axes).

Verifies the amendment before running: FREEZE_V1 hash chain, P00B controls
must equal FREEZE_V1 denominators, arm must be in the frozen live list.
Every arm's elites are re-scored on ALL amended axes (uniform recompute):
S3d@10 (den 8), B2d@20 (den 4), CVT census niches (den 18, nearest
exhaustive census centroid).  Pareto denominator (387) unchanged.

Writes results/QDA1_<arm>_s<seed>.json, manifests/receipts/QDA1_*.receipt.json,
results/QDA1_*.status, archives/QDA1_*_archive.json.

Usage: python3 qd_run_amend1.py <capsule_root> <arm> <seed>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT, ARM, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.path.insert(0, ROOT)

with open(os.path.join(ROOT, "FREEZE_V1_AMEND_1.json")) as f:
    A1 = json.load(f)
SMOKE = os.environ.get("ZOO_SMOKE") == "1"
PREFIX = "SMOKE_QDA1" if SMOKE else "QDA1"
# smoke budget must exceed 65 so P06's internal k-means (k=64) can seed
BUDGET = 100 if SMOKE else A1["production_MZ_D3_amend1"]["budget"]
if ARM not in A1["production_MZ_D3_amend1"]["arms_live"]:
    raise SystemExit("arm %s not in amend-1 frozen arm list" % ARM)
# amendment chain: FREEZE_V1 hash must match the recorded pre-image
with open(os.path.join(ROOT, "FREEZE_V1.json"), "rb") as f:
    v1_sha = hashlib.sha256(f.read()).hexdigest()
if v1_sha != A1["freeze_v1_sha256"]:
    raise SystemExit("FREEZE_V1.json does not match amendment chain")
CH = A1["census_truth_P00B"]["controls_reverified"]
DEN = A1["census_truth_P00B"]["denominators_amended"]
if CH["S2d@10_occupied"] != 4 or CH["B2d@10_occupied"] != 2:
    raise SystemExit("amend-1 controls do not reproduce FREEZE_V1 truth")

from search import (cvt_map_elites, lexicase, map_elites, mome, nslc,  # noqa: E402
                    nsga, random_search)
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from hpc.census_p00 import config_digest  # noqa: E402

MODULES = {"P01_random_search": random_search, "P02_nsga2": nsga,
           "P03_map_elites": map_elites, "P04_nslc": nslc,
           "P05_map_elites_B": map_elites, "P06_cvt_map_elites": cvt_map_elites,
           "P09_mome": mome, "P11_lexicase": lexicase}
CHANGES = A1["arm_config_changes"]

with open(os.path.join(ROOT, "archives", "CENSUS_P00_TRUTH.json")) as f:
    TRUTH = json.load(f)
PARETO = {p["phenotype_digest"] for p in TRUTH["pareto"]}
BEST = TRUTH["summary"]["best_dev_score"]

with open(os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json")) as f:
    TRUTH_B = json.load(f)
CENTROIDS = [tuple(c) for c in TRUTH_B["cvt_centroids"]]
assert len(CENTROIDS) == DEN["CVT64_occupied_niches"], "centroid/niche count drift"
import ast  # noqa: E402
S3D_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_B["cells_S3d10"]}
B2D20_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_B["cells_B2d20"]}
assert len(S3D_CELLS) == DEN["S3d@10_occupied"], "S3d truth/denominator drift"
assert len(B2D20_CELLS) == DEN["B2d@20_occupied"], "B2d20 truth/denominator drift"


def cell_idx(d, bounds, res):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(d, bounds))


def nearest_census_niche(ds):
    return min(range(len(CENTROIDS)),
               key=lambda c: sum((a - b) ** 2 for a, b in zip(ds, CENTROIDS[c])))


def recompute(recs):
    """Uniform re-evaluation of elite genomes -> per-arm amended-axis cells."""
    reg3 = DESCRIPTOR_REGISTRY["S_structural_3d"]
    regb = DESCRIPTOR_REGISTRY["B_behavior_2d"]
    s3, b2, niches = set(), set(), set()
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        ev = evaluate_genome(g)["evaluation"]
        org = compile_genome(g)
        s3.add(cell_idx(descriptors_for(org, ev, "S_structural_3d"), reg3["bounds"], 10))
        b2.add(cell_idx(descriptors_for(org, ev, "B_behavior_2d"), regb["bounds"], 20))
        niches.add(nearest_census_niche(descriptors_for(org, ev, "S_cvtd")))
    return s3, b2, niches


def main():
    t0 = time.time()
    mod = MODULES[ARM]
    if ARM in CHANGES:
        cfg = CHANGES[ARM]
        if ARM == "P06_cvt_map_elites":
            res = mod.run(budget=BUDGET, seed=SEED, archive="S_cvtd")
        else:
            res = mod.run(budget=BUDGET, seed=SEED, archive=cfg["archive"], res=cfg["res"])
    elif ARM == "P06_cvt_map_elites":
        res = mod.run(budget=BUDGET, seed=SEED, archive="S_cvtd")
    else:
        res = mod.run(budget=BUDGET, seed=SEED)
    elapsed = time.time() - t0
    recs = res["archive"]
    digs = {r["phenotype_digest"] for r in recs}
    best = max((r["dev_score"] for r in recs), default=None)
    s3, b2, niches = recompute(recs)
    receipt = make_receipt("qda1-%s-s%d" % (ARM, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2-amend1",
                           config_digest())
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16], "d": r["dev_score"]})
    assert verify_receipt(receipt), "receipt chain broken"
    out = {
        "run_id": "qda1-%s-s%d" % (ARM, SEED), "arm": ARM, "seed": SEED,
        "amendment": A1["amendment_id"],
        "budget": BUDGET, "evals": res["evals"],
        "wall_s": round(elapsed, 3),
        "cpu_hours": round(elapsed / 3600.0, 6),
        "n_elites": len(recs),
        "unique_phenotypes": res.get("unique_feasible_phenotypes",
                                     res.get("unique_phenotypes")),
        "pareto_recovery": round(len(digs & PARETO) / len(PARETO), 6),
        "S3d10_cells_hit": len(s3 & S3D_CELLS),
        "S3d10_cell_recovery": round(len(s3 & S3D_CELLS) / DEN["S3d@10_occupied"], 6),
        "B2d20_cells_hit": len(b2 & B2D20_CELLS),
        "B2d20_cell_recovery": round(len(b2 & B2D20_CELLS) / DEN["B2d@20_occupied"], 6),
        "CVT_census_niches_hit": len(niches),
        "CVT_census_niche_recovery": round(len(niches) / DEN["CVT64_occupied_niches"], 6),
        "best_dev": best,
        "best_dev_gap_vs_census": (round(BEST - best, 6) if best is not None else None),
        "qd_score": res.get("qd_score"),
        "receipt_head": receipt["head_sha256"],
        "host": os.environ.get("ZOO_HOST", "local"),
    }
    os.makedirs(os.path.join(ROOT, "manifests", "receipts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    tag = "%s_s%d" % (ARM, SEED)
    with open(os.path.join(ROOT, "results", "%s_%s.json" % (PREFIX, tag)), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(ROOT, "manifests", "receipts", "%s_%s.receipt.json" % (PREFIX, tag)), "w") as f:
        json.dump(receipt, f)
    with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
        f.write("ok\n")
    if not SMOKE:  # production archives only; smoke archives are discarded
        with open(os.path.join(ROOT, "archives", "QDA1_%s_archive.json" % tag), "w") as f:
            json.dump(res["archive"], f)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # retain the crash, never overwrite with success
        tag = "%s_s%d" % (ARM, SEED)
        os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
        with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
            f.write("fail %r\n" % e)
        raise
