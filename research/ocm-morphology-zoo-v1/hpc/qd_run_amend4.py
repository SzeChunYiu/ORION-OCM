"""AMEND-4 worker (MZ-D8 islands): one (arm, seed) scored T2 island run
under FREEZE_V1_AMEND_4.json.

Arms (frozen in A4):
  I01_islands_ring_mig  — 7 prior-locked islands, ring migration every 500
                           rounds (best elite per island, simultaneous)
  I02_islands_nomig     — identical islands and per-island RNG streams,
                           migration disabled (the control)

Every genome is evaluated at tier T2 (ZOO_TIER=T2).  All pooled metrics are
recomputed uniformly from the pooled archive records (census cells, census
CVT-D niches, T2 pareto), never from the search loop's bookkeeping.  Hostile
metrics (sec 12): island-class entropy mid vs final ("island diversity
disappears after migration") and frontier birth-island concentration ("one
mature parent architecture reproduces the entire frontier").

Writes results/QDA4_<ARM>_s<seed>.json (+ .status, receipt, archive dump).

Usage: python3 qd_run_amend4.py <capsule_root> <ARM_ID> <seed>
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
os.environ["ZOO_TIER"] = "T2"

with open(os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")) as f:
    A4 = json.load(f)
SMOKE = os.environ.get("ZOO_SMOKE") == "1"
PREFIX = "SMOKE_QDA4" if SMOKE else "QDA4"
ARMCFG = {a["arm_id"]: a for a in A4["arms_amend4"]["island_arms"]}
if ARM not in ARMCFG:
    raise SystemExit("task %s not in amend-4 frozen island arm list" % ARM)
BUDGET = 100 if SMOKE else A4["arms_amend4"]["budget"]
INTERVAL = 25 if SMOKE else A4["island_priors_amend4"]["migration_interval_rounds"]
_chain = [("FREEZE_V1.json", "freeze_v1_sha256"),
          ("FREEZE_V1_AMEND_1.json", "amend_1_sha256"),
          ("FREEZE_V1_AMEND_2.json", "amend_2_sha256"),
          ("FREEZE_V1_AMEND_3.json", "amend_3_sha256")]
for fn, key in _chain:
    with open(os.path.join(ROOT, fn), "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != A4[key]:
            raise SystemExit("%s does not match amend-4 chain" % fn)
DEN = A4["census_truth_P00C"]["denominators"]

from search.island_qd import run_islands, N_ISLANDS  # noqa: E402
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
CENTROIDS_D = [tuple(c) for c in TRUTH_C["cvtd_centroids"]]
assert len(PARETO_T2) == DEN["PARETO_T2"], "T2 pareto truth/denominator drift"
assert len(D2_CELLS) == DEN["D2d@10_occupied"], "D2d truth/denominator drift"
assert len(CENTROIDS_D) == DEN["CVTD_k_after_dedup"], "CVT-D truth drift"


def cell_idx(d, bounds, res=10):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(d, bounds))


def nearest_census_niche_d(ds):
    return min(range(len(CENTROIDS_D)),
               key=lambda c: sum((a - b) ** 2 for a, b in zip(ds, CENTROIDS_D[c])))


def main():
    t0 = time.time()
    cfg = ARMCFG[ARM]
    res = run_islands(budget=BUDGET, seed=SEED, archive="D_dev_2d", res=10,
                      migration=bool(cfg["migration"]), interval=INTERVAL)
    elapsed = time.time() - t0
    recs = res["archive"]
    reg2 = DESCRIPTOR_REGISTRY["D_dev_2d"]
    pareto, d2, niches = set(), set(), set()
    devs, rets = [], []
    pooled = []
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        out = evaluate_genome(g, tier="T2", use_cache=False)
        if not out["feasible"]:
            continue
        ev = out["evaluation"]
        org = compile_genome(g)
        pareto.add(r["phenotype_digest"])
        d2.add(cell_idx(descriptors_for(org, ev, "D_dev_2d"), reg2["bounds"], 10))
        niches.add(nearest_census_niche_d(descriptors_for(org, ev, "D_developmental")))
        devs.append(dev_score(ev))
        rc = ev.get("reset_control", {})
        if rc.get("solved_fraction") is not None:
            rets.append((dev_score(ev),
                         ev["solved_fraction"] - rc["solved_fraction"]))
        b = r["genome"].get("provenance", {}).get("birth_island", -1)
        pooled.append({
            "genotype_digest": r["genotype_digest"],
            "phenotype_digest": r["phenotype_digest"],
            "dev": dev_score(ev),
            "birth_island": b,
            "residence_island": r.get("residence_island", -1),
            "migrant": bool(r.get("migrant", False)),
        })
    best = max(devs) if devs else None
    # hostile: frontier birth-island concentration (top-32 pooled by dev)
    frontier = sorted(pooled, key=lambda x: -x["dev"])[:32]
    f_counts = [0] * N_ISLANDS
    for e in frontier:
        if 0 <= e["birth_island"] < N_ISLANDS:
            f_counts[e["birth_island"]] += 1
    frontier_conc = (max(f_counts) / len(frontier)) if frontier else None
    cross = sum(1 for e in pooled
                if e["residence_island"] != e["birth_island"]
                and 0 <= e["birth_island"] < N_ISLANDS
                and 0 <= e["residence_island"] < N_ISLANDS)
    frontier_ret = sorted(rets, key=lambda x: -x[0])[:32]
    frontier_retention = (sum(1 for _, r in frontier_ret if r > 1e-9) / len(frontier_ret)
                          if frontier_ret else 0.0)
    receipt = make_receipt("qda4-%s-s%d" % (ARM, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2-amend4",
                           config_digest())
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16]})
    assert verify_receipt(receipt), "receipt chain broken"
    mid = res["island_entropy_mid"]
    fin = res["island_entropy_final"]
    out = {
        "run_id": "qda4-%s-s%d" % (ARM, SEED), "arm": ARM, "seed": SEED,
        "amendment": A4["amendment_id"], "tier": "T2",
        "migration": bool(cfg["migration"]),
        "budget": BUDGET, "evals": res["evals"],
        "per_island_budget": res["per_island_budget"],
        "wall_s": round(elapsed, 3), "cpu_hours": round(elapsed / 3600.0, 6),
        "n_elites_pooled": len(recs),
        "pareto_recovery_T2_pooled": round(
            len(pareto & PARETO_T2) / DEN["PARETO_T2"], 6),
        "D2d_cell_recovery_pooled": round(
            len(d2 & D2_CELLS) / DEN["D2d@10_occupied"], 6),
        "CVTD_niche_recovery_pooled": round(
            len(niches) / DEN["CVTD_occupied_niches"], 6),
        "best_dev_T2_pooled": best,
        "island_entropy_mid": mid,
        "island_entropy_final": fin,
        "diversity_retention_final_over_mid": round(fin / mid, 6) if mid else None,
        "island_class_counts_mid": res["island_class_counts_mid"],
        "island_class_counts_final": res["island_class_counts_final"],
        "frontier_birth_concentration": round(frontier_conc, 6)
        if frontier_conc is not None else None,
        "frontier_birth_counts": f_counts,
        "cross_island_survivor_fraction": round(cross / len(pooled), 6)
        if pooled else None,
        "n_migration_events": res["n_migration_events"],
        "n_migrants_planted": res["n_migrants_planted"],
        "retention_positive_elite_fraction": round(
            sum(1 for _, r in rets if r > 1e-9) / len(rets), 6) if rets else None,
        "frontier_retention_fraction": round(frontier_retention, 6),
        "islands": res["islands"],
        "receipt_head": receipt["head_sha256"],
        "host": os.environ.get("ZOO_HOST", "local"),
    }
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
                               "QDA4_%s_archive.json" % tag), "w") as f:
            json.dump(pooled, f, indent=1)
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
