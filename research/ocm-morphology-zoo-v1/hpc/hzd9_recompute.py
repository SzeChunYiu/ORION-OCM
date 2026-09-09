"""MZ-D9 hostile-subset worker: uniform T2 recompute over the FROZEN amend-3
archives (QDA3 artifacts) with the HZD9 truth lens.

Per (arm, seed) task:
  - re-evaluates every archived elite at tier T2 (identical path to amend-3's
    recompute) and re-derives its census D2d/D3d/CVT-D cells;
  - asserts best_dev_T2 equals the frozen QDA3 result value (free determinism
    xcheck of the whole scored layer against the new code);
  - raw own-axis recovery (must equal the frozen QDA3 metric value —
    determinism xcheck) and JUNK-FREE own-axis recovery: census-occupied cells
    covered ONLY counting elites at/above the HZD9 quality bar (median
    dev_score over the feasible census, frozen pre-score in A4);
  - archive-level genotype -> phenotype / behavioral collapse.

Usage: python3 hzd9_recompute.py <capsule_root> <ARM_ID> <seed>
       ARM_ID in the amend-4 frozen hzd9 arm list (the five amend-3 arms).
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
PREFIX = "SMOKE_HZD9R" if SMOKE else "HZD9R"
HZD9_ARMS = A4["arms_amend4"]["hzd9_recompute_arms"]
if ARM not in HZD9_ARMS:
    raise SystemExit("task %s not in amend-4 hzd9 arm list" % ARM)
_chain = [("FREEZE_V1.json", "freeze_v1_sha256"),
          ("FREEZE_V1_AMEND_1.json", "amend_1_sha256"),
          ("FREEZE_V1_AMEND_2.json", "amend_2_sha256"),
          ("FREEZE_V1_AMEND_3.json", "amend_3_sha256")]
for fn, key in _chain:
    with open(os.path.join(ROOT, fn), "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != A4[key]:
            raise SystemExit("%s does not match amend-4 chain" % fn)
DEN = A4["census_truth_P00C"]["denominators"]
QUALITY_BAR = A4["quality_bar_T2"]

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
with open(os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json")) as f:
    TRUTH_B = json.load(f)
S3_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_B["cells_S3d10"]}
REG_S3 = DESCRIPTOR_REGISTRY["S_structural_3d"]
OWN_AXIS = A4["arms_amend4"]["hzd9_own_axis"][ARM]
OWN_DEN = {"D2d_cell_recovery": DEN["D2d@10_occupied"],
           "D3d_cell_recovery": DEN["D3d@10_occupied"],
           "CVTD_niche_recovery": DEN["CVTD_occupied_niches"],
           "S3d_cell_recovery": DEN["S3d@10_occupied_T0ref"],
           "pareto_recovery_T2": DEN["PARETO_T2"]}[OWN_AXIS]

TAG = "%s_s%d" % (ARM, SEED)
SRC_ARCHIVE = ("SMOKE_QDA3_%s_archive.json" % TAG if SMOKE else
               "QDA3_%s_archive.json" % TAG)
SRC_RESULT = ("SMOKE_QDA3_%s.json" % TAG if SMOKE else "QDA3_%s.json" % TAG)


def nearest_census_niche_d(ds):
    return min(range(len(CENTROIDS_D)),
               key=lambda c: sum((a - b) ** 2 for a, b in zip(ds, CENTROIDS_D[c])))


def cell_idx(d, bounds, res=10):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(d, bounds))


def main():
    t0 = time.time()
    with open(os.path.join(ROOT, "archives", SRC_ARCHIVE)) as f:
        recs = json.load(f)
    with open(os.path.join(ROOT, "results", SRC_RESULT)) as f:
        ref = json.load(f)
    reg2 = DESCRIPTOR_REGISTRY["D_dev_2d"]
    reg3 = DESCRIPTOR_REGISTRY["D_dev_3d"]
    gds, phenos, behs = set(), set(), set()
    raw_hits, clean_hits = set(), set()
    devs = []
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        out = evaluate_genome(g, tier="T2", use_cache=False)
        if not out["feasible"]:
            continue
        ev = out["evaluation"]
        org = compile_genome(g)
        d = dev_score(ev)
        d2 = cell_idx(descriptors_for(org, ev, "D_dev_2d"), reg2["bounds"], 10)
        gds.add(r["genotype_digest"])
        phenos.add(r["phenotype_digest"])
        behs.add((r["phenotype_digest"], d2))
        devs.append(d)
        if OWN_AXIS == "D2d_cell_recovery":
            c = d2
        elif OWN_AXIS == "D3d_cell_recovery":
            c = cell_idx(descriptors_for(org, ev, "D_dev_3d"), reg3["bounds"], 10)
        elif OWN_AXIS == "CVTD_niche_recovery":
            c = nearest_census_niche_d(descriptors_for(org, ev, "D_developmental"))
        elif OWN_AXIS == "S3d_cell_recovery":
            c = cell_idx(descriptors_for(org, ev, "S_structural_3d"),
                         REG_S3["bounds"], 10)
        else:  # pareto_recovery_T2 (P01 axis)
            c = r["phenotype_digest"]
        raw_hits.add(c)
        if d >= QUALITY_BAR:
            clean_hits.add(c)
    best = max(devs) if devs else None
    if abs((best or 0.0) - (ref["best_dev_T2"] or 0.0)) > 1e-9:
        raise SystemExit("determinism xcheck FAILED: best_dev %r != frozen %r"
                         % (best, ref["best_dev_T2"]))
    # own-axis hit space: cells/niches intersect census-occupied sets; the
    # pareto axis intersects the census T2 Pareto digests
    if OWN_AXIS == "pareto_recovery_T2":
        universe = PARETO_T2
    elif OWN_AXIS == "D2d_cell_recovery":
        universe = D2_CELLS
    elif OWN_AXIS == "D3d_cell_recovery":
        universe = D3_CELLS
    elif OWN_AXIS == "S3d_cell_recovery":
        universe = S3_CELLS
    else:  # CVT niches are already census-niche ids
        universe = set(range(OWN_DEN))
    raw_recovery = len(raw_hits & universe) / OWN_DEN
    clean_recovery = len(clean_hits & universe) / OWN_DEN
    frozen_recovery = ref.get(OWN_AXIS)
    if abs(raw_recovery - frozen_recovery) > 1e-6:
        raise SystemExit("determinism xcheck FAILED: %s %r != frozen %r"
                         % (OWN_AXIS, raw_recovery, frozen_recovery))
    receipt = make_receipt("hzd9r-%s-s%d" % (ARM, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2-hzd9",
                           config_digest())
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16]})
    assert verify_receipt(receipt), "receipt chain broken"
    out_json = {
        "run_id": "hzd9r-%s-s%d" % (ARM, SEED), "arm": ARM, "seed": SEED,
        "amendment": A4["amendment_id"], "tier": "T2",
        "quality_bar_T2": QUALITY_BAR,
        "n_elites": len(recs),
        "distinct_genotypes": len(gds),
        "distinct_phenotypes": len(phenos),
        "distinct_phenotype_x_D2dcell": len(behs),
        "archive_genotype_to_phenotype_collapse_ratio": round(
            1.0 - len(phenos) / max(1, len(gds)), 6),
        "own_axis": OWN_AXIS,
        "raw_own_axis_recovery": round(raw_recovery, 6),
        "junk_free_own_axis_recovery": round(clean_recovery, 6),
        "junk_free_ratio": round(clean_recovery / raw_recovery, 6)
        if raw_recovery > 0 else None,
        "best_dev_T2": best,
        "best_dev_matches_frozen": True,
        "n_elites_above_bar": sum(1 for d in devs if d >= QUALITY_BAR),
        "wall_s": round(time.time() - t0, 3),
        "receipt_head": receipt["head_sha256"],
        "host": os.environ.get("ZOO_HOST", "local"),
    }
    os.makedirs(os.path.join(ROOT, "manifests", "receipts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "%s_%s.json" % (PREFIX, TAG)), "w") as f:
        json.dump(out_json, f, indent=1)
    with open(os.path.join(ROOT, "manifests", "receipts",
                           "%s_%s.receipt.json" % (PREFIX, TAG)), "w") as f:
        json.dump(receipt, f)
    with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, TAG)), "w") as f:
        f.write("ok\n")
    print(json.dumps(out_json, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
        with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, TAG)), "w") as f:
            f.write("fail %r\n" % e)
        raise
