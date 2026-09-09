"""AMEND-3 worker (MZ-D7): one (arm, seed) scored T2 run under
FREEZE_V1_AMEND_3.json.

Verifies before running: FREEZE_V1 -> AMEND_1 -> AMEND_2 -> AMEND_3 sha
chain, frozen arm list, P00C census denominators (Pareto 792, D2d@10 50,
D3d@10 83, CVT-D 64) and the P00B S3d@10 denominator (8, structural
tier-independent reference for the P03 control arm).

Every genome in the arm is evaluated at tier T2 (ZOO_TIER=T2): the long
lifetime battery plus its RESET control.  All Archive-D metrics are
recomputed uniformly from the archive records (census cells, census CVT-D
niches, T2 pareto, retention), never taken from the search loop's bookkeeping.

Writes results/QDA3_<ARM>_s<seed>.json (+ .status, receipt, archive dump).

Usage: python3 qd_run_amend3.py <capsule_root> <ARM_ID> <seed>
       ARM_ID in the amend-3 frozen arm list, e.g. P01_random_search_T2
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import time

ROOT, ARM, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.path.insert(0, ROOT)
os.environ["ZOO_TIER"] = "T2"  # every evaluation in this arm is a T2 lifetime

with open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json")) as f:
    A3 = json.load(f)
SMOKE = os.environ.get("ZOO_SMOKE") == "1"
PREFIX = "SMOKE_QDA3" if SMOKE else "QDA3"
BUDGET = 100 if SMOKE else A3["arms_amend3"]["budget"]
ARMCFG = {a["arm_id"]: a for a in A3["arms_amend3"]["arms"]}
if ARM not in ARMCFG:
    raise SystemExit("task %s not in amend-3 frozen arm list" % ARM)
# sha chain: every ancestor freeze must match its recorded pre-image
_chain = [("FREEZE_V1.json", "freeze_v1_sha256"),
          ("FREEZE_V1_AMEND_1.json", "amend_1_sha256"),
          ("FREEZE_V1_AMEND_2.json", "amend_2_sha256")]
for fn, key in _chain:
    with open(os.path.join(ROOT, fn), "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != A3[key]:
            raise SystemExit("%s does not match amend-3 chain" % fn)
DEN = A3["census_truth_P00C"]["denominators"]

from search import cvt_map_elites, map_elites, random_search  # noqa: E402
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from hpc.census_p00 import config_digest  # noqa: E402

with open(os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json")) as f:
    TRUTH_C = json.load(f)
PARETO_T2 = {p["phenotype_digest"] for p in TRUTH_C["pareto"]}
D2_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_C["cells_D2d10"]}
D3_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_C["cells_D3d10"]}
CENTROIDS_D = [tuple(c) for c in TRUTH_C["cvtd_centroids"]]
assert len(PARETO_T2) == DEN["PARETO_T2"], "T2 pareto truth/denominator drift"
assert len(D2_CELLS) == DEN["D2d@10_occupied"], "D2d truth/denominator drift"
assert len(D3_CELLS) == DEN["D3d@10_occupied"], "D3d truth/denominator drift"
assert len(CENTROIDS_D) == DEN["CVTD_k_after_dedup"], "CVT-D truth drift"
# structural reference (tier-independent): S3d@10 occupied cells from P00B
with open(os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json")) as f:
    TRUTH_B = json.load(f)
S3D_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_B["cells_S3d10"]}
assert len(S3D_CELLS) == DEN["S3d@10_occupied_T0ref"], "S3d ref drift"


def cell_idx(d, bounds, res):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(d, bounds))


def nearest_census_niche_d(ds):
    return min(range(len(CENTROIDS_D)),
               key=lambda c: sum((a - b) ** 2 for a, b in zip(ds, CENTROIDS_D[c])))


def recompute(recs):
    """Uniform T2 recompute of every Archive-D metric from the records."""
    reg2 = DESCRIPTOR_REGISTRY["D_dev_2d"]
    reg3 = DESCRIPTOR_REGISTRY["D_dev_3d"]
    regS = DESCRIPTOR_REGISTRY["S_structural_3d"]
    pareto, d2, d3, niches, s3 = set(), set(), set(), set(), set()
    devs, rets = [], []
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        out = evaluate_genome(g, tier="T2", use_cache=False)
        if not out["feasible"]:
            continue
        ev = out["evaluation"]
        org = compile_genome(g)
        pareto.add(r["phenotype_digest"])
        d2.add(cell_idx(descriptors_for(org, ev, "D_dev_2d"), reg2["bounds"], 10))
        d3.add(cell_idx(descriptors_for(org, ev, "D_dev_3d"), reg3["bounds"], 10))
        niches.add(nearest_census_niche_d(descriptors_for(org, ev, "D_developmental")))
        s3.add(cell_idx(descriptors_for(org, ev, "S_structural_3d"), regS["bounds"], 10))
        devs.append(dev_score(ev))
        rc = ev.get("reset_control", {})
        if rc.get("solved_fraction") is not None:
            rets.append((dev_score(ev),
                         ev["solved_fraction"] - rc["solved_fraction"]))
    return pareto, d2, d3, niches, s3, devs, rets


def main():
    t0 = time.time()
    cfg = ARMCFG[ARM]
    algo = cfg["algorithm"]
    if algo == "random_search":
        res = random_search.run(budget=BUDGET, seed=SEED)
    elif algo == "map_elites":
        res = map_elites.run(budget=BUDGET, seed=SEED, archive=cfg["archive"],
                             res=cfg.get("res", 10))
    elif algo == "cvt_map_elites":
        res = cvt_map_elites.run(budget=BUDGET, seed=SEED, archive=cfg["archive"],
                                 k=cfg.get("k", 64))
    else:
        raise SystemExit("unknown algorithm %s" % algo)
    elapsed = time.time() - t0
    recs = res["archive"]
    pareto, d2, d3, niches, s3, devs, rets = recompute(recs)
    hits = len(pareto & PARETO_T2)
    best = max(devs) if devs else None
    frontier = sorted(rets, key=lambda x: -x[0])[:32]
    frontier_retention = (sum(1 for _, r in frontier if r > 1e-9) / len(frontier)
                          if frontier else 0.0)
    receipt = make_receipt("qda3-%s-s%d" % (ARM, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2-amend3",
                           config_digest())
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16],
                       "f": int(bool(r.get("feasible")))})
    assert verify_receipt(receipt), "receipt chain broken"
    out = {
        "run_id": "qda3-%s-s%d" % (ARM, SEED), "arm": ARM, "seed": SEED,
        "amendment": A3["amendment_id"], "tier": "T2",
        "algorithm": algo, "archive": cfg.get("archive"),
        "own_axis": cfg["own_axis"],
        "budget": BUDGET, "evals": res["evals"],
        "wall_s": round(elapsed, 3), "cpu_hours": round(elapsed / 3600.0, 6),
        "n_elites": len(recs),
        "pareto_recovery_T2": round(hits / DEN["PARETO_T2"], 6),
        "D2d_cell_recovery": round(len(d2 & D2_CELLS) / DEN["D2d@10_occupied"], 6),
        "D3d_cell_recovery": round(len(d3 & D3_CELLS) / DEN["D3d@10_occupied"], 6),
        "CVTD_niche_recovery": round(len(niches) / DEN["CVTD_occupied_niches"], 6),
        "S3d_cell_recovery": round(len(s3 & S3D_CELLS)
                                   / DEN["S3d@10_occupied_T0ref"], 6),
        "best_dev_T2": best,
        "qd_score_T2": res.get("qd_score"),
        "retention_positive_elite_fraction": round(
            sum(1 for _, r in rets if r > 1e-9) / len(rets), 6) if rets else None,
        "retention_max": round(max((r for _, r in rets), default=0.0), 6),
        "frontier_retention_fraction": round(frontier_retention, 6),
        "receipt_head": receipt["head_sha256"],
        "host": os.environ.get("ZOO_HOST", "local"),
    }
    out["own_axis_value"] = out[cfg["own_axis"]]  # must exist by freeze
    os.makedirs(os.path.join(ROOT, "manifests", "receipts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    tag = "%s_s%d" % (ARM, SEED)
    with open(os.path.join(ROOT, "results", "%s_%s.json" % (PREFIX, tag)), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(ROOT, "manifests", "receipts",
                           "%s_%s.receipt.json" % (PREFIX, tag)), "w") as f:
        json.dump(receipt, f)
    with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
        f.write("ok\n")
    if not SMOKE:
        with open(os.path.join(ROOT, "archives",
                               "QDA3_%s_archive.json" % tag), "w") as f:
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
