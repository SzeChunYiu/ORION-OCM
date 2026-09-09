"""MZ-D3 worker: one (arm, seed) at the FROZEN production budget.

Verifies FREEZE_V1.json before running, computes recovery vs census truth,
writes results/QD_<arm>_s<seed>.json, a receipt into manifests/receipts/,
and a disposition file (ok/fail) that aggregate.py gates on.

Usage: python3 qd_run.py <capsule_root> <arm> <seed>
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT, ARM, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.path.insert(0, ROOT)

with open(os.path.join(ROOT, "FREEZE_V1.json")) as f:
    FREEZE = json.load(f)
BUDGET = FREEZE["production_MZ_D3"]["budget_evals_per_arm_seed"]
if ARM not in FREEZE["production_MZ_D3"]["arms"]:
    raise SystemExit("arm %s not in frozen arm list" % ARM)

from search import (cvt_map_elites, lexicase, map_elites, mome, novelty,  # noqa: E402
                    nsga, nslc, random_search)
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.receipts import make_receipt, verify_receipt  # noqa: E402
from hpc.census_p00 import config_digest  # noqa: E402

MODULES = {"P01_random_search": random_search, "P02_nsga2": nsga,
           "P03_map_elites": map_elites, "P04_nslc": nslc,
           "P05_map_elites_B": map_elites, "P06_cvt_map_elites": cvt_map_elites,
           "P09_mome": mome, "P11_lexicase": lexicase}

with open(os.path.join(ROOT, "archives", "CENSUS_P00_TRUTH.json")) as f:
    TRUTH = json.load(f)
PARETO = {p["phenotype_digest"] for p in TRUTH["pareto"]}
BEST = TRUTH["summary"]["best_dev_score"]


def hit_cells(recs, regname):
    reg = DESCRIPTOR_REGISTRY[regname]
    out = set()
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        d = descriptors_for(compile_genome(g),
                            evaluate_genome(g)["evaluation"], regname)
        idx = tuple(min(9, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * 10)))
                    for dv, b in zip(d, reg["bounds"]))
        out.add(idx)
    return out


def main():
    import ast
    cells_S = {tuple(ast.literal_eval(k)) for k in TRUTH["cells_S"]}
    cells_B = {tuple(ast.literal_eval(k)) for k in TRUTH["cells_B"]}
    t0 = time.time()
    mod = MODULES[ARM]
    if ARM == "P05_map_elites_B":
        res = mod.run(budget=BUDGET, seed=SEED, archive="B_behavior_2d")
    elif ARM == "P06_cvt_map_elites":
        res = mod.run(budget=BUDGET, seed=SEED, archive="S_cvtd")
    else:
        res = mod.run(budget=BUDGET, seed=SEED)
    elapsed = time.time() - t0
    recs = res["archive"]
    digs = {r["phenotype_digest"] for r in recs}
    best = max((r["dev_score"] for r in recs), default=None)
    receipt = make_receipt("qd-%s-s%d" % (ARM, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2",
                           config_digest())
    from evaluation.receipts import append_record
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16], "d": r["dev_score"]})
    assert verify_receipt(receipt), "receipt chain broken"
    out = {
        "run_id": "qd-%s-s%d" % (ARM, SEED), "arm": ARM, "seed": SEED,
        "budget": BUDGET, "evals": res["evals"],
        "wall_s": round(elapsed, 3),
        "cpu_hours": round(elapsed / 3600.0, 6),
        "n_elites": len(recs),
        "unique_phenotypes": res.get("unique_feasible_phenotypes",
                                     res.get("unique_phenotypes")),
        "pareto_recovery": round(len(digs & PARETO) / len(PARETO), 6),
        "S_cell_recovery": round(len(hit_cells(recs, "S_structural_2d") & cells_S) / len(cells_S), 6),
        "B_cell_recovery": round(len(hit_cells(recs, "B_behavior_2d") & cells_B) / len(cells_B), 6),
        "best_dev": best,
        "best_dev_gap_vs_census": (round(BEST - best, 6) if best is not None else None),
        "qd_score": res.get("qd_score"),
        "receipt_head": receipt["head_sha256"],
        "host": os.environ.get("ZOO_HOST", "local"),
    }
    os.makedirs(os.path.join(ROOT, "manifests", "receipts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    tag = "%s_s%d" % (ARM, SEED)
    with open(os.path.join(ROOT, "results", "QD_%s.json" % tag), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(ROOT, "manifests", "receipts", "QD_%s.receipt.json" % tag), "w") as f:
        json.dump(receipt, f)
    with open(os.path.join(ROOT, "results", "QD_%s.status" % tag), "w") as f:
        f.write("ok\n")
    # full archive (genomes) for the zoo population
    with open(os.path.join(ROOT, "archives", "QD_%s_archive.json" % tag), "w") as f:
        json.dump(res["archive"], f)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # retain the crash, never overwrite with success
        tag = "%s_s%d" % (ARM, SEED)
        with open(os.path.join(ROOT, "results", "QD_%s.status" % tag), "w") as f:
            f.write("fail %r\n" % e)
        raise
