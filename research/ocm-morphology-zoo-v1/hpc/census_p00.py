"""P00 exact finite morphology census (MZ-D2): exhaustive truth first.

Enumerates every legal genome under CENSUS_BOUND_V1, evaluates each
deterministically, and emits:
  manifests/CENSUS_P00_MANIFEST.json   (frozen config, expected size)
  results/CENSUS_P00_RESULT.json       (summary + recovery bookkeeping)
  archives/CENSUS_P00_TRUTH.json       (exact Pareto set + descriptor truth)

Usage: python3 census_p00.py <capsule_root> [--chunk i/n]  (chunk = shard for
array jobs; shard files merge deterministically by index).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
CHUNK = None
if "--chunk" in sys.argv:
    spec = sys.argv[sys.argv.index("--chunk") + 1]
    i, n = spec.split("/")
    CHUNK = (int(i), int(n))

from morphology.canonicalize import collapse_duplicates  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from morphology.direct_genome import CENSUS_BOUND_V1, enumerate_census, census_size  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import (OBJECTIVE_NAMES, dev_score, objective_vector,  # noqa: E402
                                   pareto_front)
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402

RES = os.path.join(ROOT, "results")
ARC = os.path.join(ROOT, "archives")
MAN = os.path.join(ROOT, "manifests")


def config_digest() -> str:
    payload = {
        "bound": {k: (list(v) if isinstance(v, (list, tuple)) else v)
                  for k, v in CENSUS_BOUND_V1.items()},
        "objectives": list(OBJECTIVE_NAMES),
        "archive_S": DESCRIPTOR_REGISTRY["S_structural_2d"],
        "res": 10,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def main() -> None:
    t0 = time.time()
    expected = census_size()
    receipt = make_receipt("zoo-census-p00", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T0", config_digest())
    records = []
    feas = 0
    total_eval_s = 0.0
    for gi, g in enumerate(enumerate_census()):
        if CHUNK is not None:
            i, n = CHUNK
            if gi % n != i:
                continue
        ts = time.time()
        r = evaluate_genome(g, use_cache=False)
        total_eval_s += time.time() - ts
        org = compile_genome(g)
        if r["feasible"]:
            feas += 1
            records.append({
                "index": gi,
                "genotype_digest": r["genotype_digest"],
                "phenotype_digest": r["phenotype_digest"],
                "objectives": objective_vector(r["evaluation"]),
                "dev_score": dev_score(r["evaluation"]),
                "descriptors_S": descriptors_for(org, r["evaluation"], "S_structural_2d"),
                "descriptors_B": descriptors_for(org, r["evaluation"], "B_behavior_2d"),
                "genome": g.to_json_obj(),
                "solved_fraction": r["evaluation"]["solved_fraction"],
            })
        append_record(receipt, gi, {
            "g": r["genotype_digest"][:16], "p": r["phenotype_digest"][:16],
            "f": int(r["feasible"])})
    assert verify_receipt(receipt), "receipt chain broken"
    # exact Pareto set over feasible census members
    front_idx = pareto_front(records, "objectives")
    pareto = [records[i] for i in front_idx]
    # exact descriptor truth: best dev_score per grid cell, S and B archives
    def _cells(dkey: str, regname: str):
        reg = DESCRIPTOR_REGISTRY[regname]
        bounds = reg["bounds"]
        out = {}
        for rec in records:
            d = rec[dkey]
            idx = tuple(min(9, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * 10)))
                        for dv, b in zip(d, bounds))
            cur = out.get(idx)
            if cur is None or rec["dev_score"] > cur[0]:
                out[idx] = (rec["dev_score"], rec["phenotype_digest"])
        return out

    cells = _cells("descriptors_S", "S_structural_2d")
    cells_B = _cells("descriptors_B", "B_behavior_2d")
    uniq = collapse_duplicates(
        [{"phenotype_digest": r["phenotype_digest"]} for r in records],
        "phenotype_digest")
    summary = {
        "run_id": "zoo-census-p00",
        "expected_census_size": expected,
        "evaluated_genomes": receipt["chain"] and len(receipt["chain"]),
        "feasible": feas,
        "feasible_fraction": round(feas / max(1, len(receipt["chain"])), 6),
        "unique_feasible_phenotypes": len(uniq),
        "pareto_set_size": len(pareto),
        "descriptor_cells_occupied_S": len(cells),
        "descriptor_cells_occupied_B": len(cells_B),
        "descriptor_cells_total": 100,
        "best_dev_score": max((r["dev_score"] for r in records), default=None),
        "wall_s": round(time.time() - t0, 3),
        "eval_s_total": round(total_eval_s, 3),
        "receipt_head": receipt["head_sha256"],
        "config_digest": config_digest(),
        "chunk": CHUNK,
    }
    tag = "" if CHUNK is None else "_c%dof%d" % CHUNK
    with open(os.path.join(MAN, "CENSUS_P00_MANIFEST.json"), "w") as f:
        json.dump({"config_digest": config_digest(), "bound": CENSUS_BOUND_V1,
                   "expected": expected, "chunk": CHUNK,
                   "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f, indent=1)
    with open(os.path.join(RES, "CENSUS_P00_RESULT%s.json" % tag), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(ARC, "CENSUS_P00_TRUTH%s.json" % tag), "w") as f:
        json.dump({"summary": summary, "pareto": pareto,
                   "cells_S": {str(k): list(v) for k, v in sorted(cells.items())},
                   "cells_B": {str(k): list(v) for k, v in sorted(cells_B.items())},
                   "receipt": receipt}, f)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    os.makedirs(ARC, exist_ok=True)
    os.makedirs(MAN, exist_ok=True)
    main()
