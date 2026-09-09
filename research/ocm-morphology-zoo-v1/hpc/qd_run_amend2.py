"""AMEND-2 worker: one (pair, encoding, seed) scored run under
FREEZE_V1_AMEND_2.json (E0-direct vs E1-CGP at equal budget).

Verifies before running: FREEZE_V1 -> AMEND_1 -> AMEND_2 sha chain, frozen
pair list, AMEND_1 denominators (pareto 387, S3d@10 8, B2d@20 4, CVT 18).
Uniform recompute on all amended axes, identical to AMEND_1.  CGP-arm codec
cost (encode+variation+decode) is timed per call and charged to the CGP arm
(codec_seconds / codec_share).  E0 arms must reproduce the corresponding
AMEND_1 production numbers (same budget/seed/config): aggregate cross-checks.

Writes results/QDA2_<PAIR>_<ENC>_s<seed>.json (+ .status, receipt, archive).

Usage: python3 qd_run_amend2.py <capsule_root> <PAIR> <ENC> <seed>
       PAIR in {R01,M03,M05,M06}, ENC in {E0,E1}
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT, PAIR, ENC, SEED = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
# the frozen manifest carries the amendment's encoding names (E0_direct /
# E1_cgp); normalize to the internal short codes used in file tags
if ENC == "E0_direct":
    ENC = "E0"
elif ENC == "E1_cgp":
    ENC = "E1"
sys.path.insert(0, ROOT)

with open(os.path.join(ROOT, "FREEZE_V1_AMEND_2.json")) as f:
    A2 = json.load(f)
SMOKE = os.environ.get("ZOO_SMOKE") == "1"
PREFIX = "SMOKE_QDA2" if SMOKE else "QDA2"
BUDGET = 100 if SMOKE else A2["arms_amend2"]["budget"]
PAIRS = {p["pair_id"] for p in A2["arms_amend2"]["pairs"]}
if PAIR not in PAIRS or ENC not in ("E0", "E1"):
    raise SystemExit("task %s_%s not in amend-2 frozen list" % (PAIR, ENC))
# sha chain: FREEZE_V1 and AMEND_1 must match recorded pre-images
with open(os.path.join(ROOT, "FREEZE_V1.json"), "rb") as f:
    if hashlib.sha256(f.read()).hexdigest() != A2["freeze_v1_sha256"]:
        raise SystemExit("FREEZE_V1.json does not match amend-2 chain")
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_1.json"), "rb") as f:
    a1_bytes = f.read()
    if hashlib.sha256(a1_bytes).hexdigest() != A2["amend_1_sha256"]:
        raise SystemExit("FREEZE_V1_AMEND_1.json does not match amend-2 chain")
A1 = json.loads(a1_bytes)
DEN = A1["census_truth_P00B"]["denominators_amended"]

from search import cvt_map_elites, map_elites, random_search  # noqa: E402
from morphology.cgp_genome import (cgp_crossover_direct,  # noqa: E402
                                   cgp_mutate_direct, cgp_sample_direct)
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from hpc.census_p00 import config_digest  # noqa: E402

with open(os.path.join(ROOT, "archives", "CENSUS_P00_TRUTH.json")) as f:
    TRUTH = json.load(f)
PARETO = {p["phenotype_digest"] for p in TRUTH["pareto"]}
BEST = TRUTH["summary"]["best_dev_score"]

with open(os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json")) as f:
    TRUTH_B = json.load(f)
CENTROIDS = [tuple(c) for c in TRUTH_B["cvt_centroids"]]
assert len(CENTROIDS) == DEN["CVT64_occupied_niches"], "centroid/niche drift"
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


# -- CGP codec timing wrappers (charged to the E1 arm) -----------------------
_codec = {"s": 0.0}


def _timed(fn):
    def w(*a):
        t = time.perf_counter()
        out = fn(*a)
        _codec["s"] += time.perf_counter() - t
        return out
    return w


HOOKS = {}
if ENC == "E1":
    HOOKS = {"sampler": _timed(cgp_sample_direct),
             "mutator": _timed(cgp_mutate_direct),
             "crossover_fn": _timed(cgp_crossover_direct)}


def main():
    t0 = time.time()
    if PAIR == "R01":
        res = random_search.run(budget=BUDGET, seed=SEED, sampler=HOOKS.get("sampler"))
    elif PAIR == "M03":
        res = map_elites.run(budget=BUDGET, seed=SEED, archive="S_structural_3d",
                             res=10, **HOOKS)
    elif PAIR == "M05":
        res = map_elites.run(budget=BUDGET, seed=SEED, archive="B_behavior_2d",
                             res=20, **HOOKS)
    else:  # M06
        res = cvt_map_elites.run(budget=BUDGET, seed=SEED, archive="S_cvtd", **HOOKS)
    elapsed = time.time() - t0
    recs = res["archive"]
    digs = {r["phenotype_digest"] for r in recs}
    best = max((r["dev_score"] for r in recs), default=None)
    s3, b2, niches = recompute(recs)
    receipt = make_receipt("qda2-%s-%s-s%d" % (PAIR, ENC, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2-amend2",
                           config_digest())
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16], "d": r["dev_score"]})
    assert verify_receipt(receipt), "receipt chain broken"
    out = {
        "run_id": "qda2-%s-%s-s%d" % (PAIR, ENC, SEED), "pair": PAIR,
        "encoding": ENC, "arm": "%s_%s" % (PAIR, ENC), "seed": SEED,
        "amendment": A2["amendment_id"],
        "budget": BUDGET, "evals": res["evals"],
        "wall_s": round(elapsed, 3),
        "cpu_hours": round(elapsed / 3600.0, 6),
        "codec_seconds": round(_codec["s"], 6),
        "codec_share": (round(_codec["s"] / elapsed, 6) if elapsed > 0 else None),
        "effective_evals_charged": (round(res["evals"] * (1 + _codec["s"] / max(elapsed - _codec["s"], 1e-9)), 3) if ENC == "E1" else res["evals"]),
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
    tag = "%s_%s_s%d" % (PAIR, ENC, SEED)
    with open(os.path.join(ROOT, "results", "%s_%s.json" % (PREFIX, tag)), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(ROOT, "manifests", "receipts", "%s_%s.receipt.json" % (PREFIX, tag)), "w") as f:
        json.dump(receipt, f)
    with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
        f.write("ok\n")
    if not SMOKE:
        with open(os.path.join(ROOT, "archives", "QDA2_%s_archive.json" % tag), "w") as f:
            json.dump(res["archive"], f)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # retain the crash, never overwrite with success
        tag = "%s_%s_s%d" % (PAIR, ENC, SEED)
        os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
        with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
            f.write("fail %r\n" % e)
        raise
