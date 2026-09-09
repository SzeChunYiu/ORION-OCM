"""P00B census extension (FREEZE_V1_AMEND_1 prerequisite): exact truth for
the amended descriptor axes — S_structural_3d@10, S_structural_2d@20,
B_behavior_2d@20, and CVT-64 over S_DIMS with EXHAUSTIVE deterministic
centroids (no sampling).  Also emits per-dim value spreads documenting why
the 2-D axes were near-degenerate.

UNSCORED (truth only).  FREEZE_V1_AMEND_1.json denominators are taken from
this file before any scored run.  Controls: S2d@10 must equal 4 and B2d@10
must equal 2 (V1 cross-check).

Usage: python3 census_p00b.py <capsule_root>
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
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from morphology.direct_genome import enumerate_census, census_size  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402

RES = os.path.join(ROOT, "results")
ARC = os.path.join(ROOT, "archives")
MAN = os.path.join(ROOT, "manifests")

K = 64
AXES = ("S_structural_3d@10", "S_structural_2d@20", "B_behavior_2d@20")


def cell_index(d, bounds, res):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(d, bounds))


def kmeans_exhaustive(points, k, iters=30):
    """Deterministic k-means: seeds = evenly spaced indices over the
    lexicographically sorted point list (no RNG anywhere)."""
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
    reg2 = DESCRIPTOR_REGISTRY["S_structural_2d"]
    reg3 = DESCRIPTOR_REGISTRY["S_structural_3d"]
    regb = DESCRIPTOR_REGISTRY["B_behavior_2d"]
    digest = hashlib.sha256(json.dumps(
        {"axes": list(AXES), "k": K, "objectives": 10,
         "census": census_size()}).encode()).hexdigest()
    receipt = make_receipt("zoo-census-p00b",
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T0", digest)
    cells_S2d10, cells_S2d20, cells_S3d10, cells_B2d10, cells_B2d20 = {}, {}, {}, {}, {}
    values = {n: set() for n in set(reg3["dims"]) | set(reg2["dims"]) | set(regb["dims"])}
    best_per = {"S3d10": {}, "S2d20": {}, "B2d20": {}}
    cvt_points = []
    for gi, g in enumerate(enumerate_census()):
        r = evaluate_genome(g, use_cache=False)
        append_record(receipt, gi, {"g": r["genotype_digest"][:16],
                                    "p": r["phenotype_digest"][:16],
                                    "f": int(r["feasible"])})
        if not r["feasible"]:
            continue
        org = compile_genome(g)
        ev = r["evaluation"]
        d2 = descriptors_for(org, ev, "S_structural_2d")
        d3 = descriptors_for(org, ev, "S_structural_3d")
        db = descriptors_for(org, ev, "B_behavior_2d")
        ds = descriptors_for(org, ev, "S_cvtd")
        for name, d in (("S_structural_2d", d2), ("S_structural_3d", d3),
                        ("B_behavior_2d", db)):
            for dim, v in zip(DESCRIPTOR_REGISTRY[name]["dims"], d):
                values[dim].add(round(float(v), 6))
        dev = dev_score(ev)
        cells_S2d10[cell_index(d2, reg2["bounds"], 10)] = 1
        cells_S2d20[cell_index(d2, reg2["bounds"], 20)] = 1
        cells_S3d10[cell_index(d3, reg3["bounds"], 10)] = 1
        cells_B2d10[cell_index(db, regb["bounds"], 10)] = 1
        cells_B2d20[cell_index(db, regb["bounds"], 20)] = 1
        for key, idx in (("S3d10", cell_index(d3, reg3["bounds"], 10)),
                         ("S2d20", cell_index(d2, reg2["bounds"], 20)),
                         ("B2d20", cell_index(db, regb["bounds"], 20))):
            cur = best_per[key].get(idx)
            if cur is None or dev > cur[0]:
                best_per[key][idx] = (dev, r["phenotype_digest"])
        cvt_points.append(ds)
    assert verify_receipt(receipt), "receipt chain broken"
    # CVT truth: deterministic exhaustive centroids over ALL feasible points
    cents = kmeans_exhaustive(cvt_points, K)
    niche = {}
    for p in cvt_points:
        j = min(range(len(cents)),
                key=lambda c: sum((a - b) ** 2 for a, b in zip(p, cents[c])))
        niche[j] = niche.get(j, 0) + 1
    summary = {
        "run_id": "zoo-census-p00b",
        "axes": list(AXES),
        "controls": {"S2d@10_occupied": len(cells_S2d10),
                     "B2d@10_occupied": len(cells_B2d10)},
        "denominators": {
            "S3d@10_occupied": len(cells_S3d10),
            "S2d@20_occupied": len(cells_S2d20),
            "B2d@20_occupied": len(cells_B2d20),
            "CVT64_occupied_niches": len(niche),
            "CVT64_k_after_dedup": len(cents),
        },
        "dim_value_spread": {d: len(v) for d, v in sorted(values.items())},
        "census_size": census_size(),
        "feasible": len(cvt_points),
        "wall_s": round(time.time() - t0, 3),
        "receipt_head": receipt["head_sha256"],
        "config_digest": digest,
        "kmeans_iters_note": "deterministic exhaustive seeds, 30 iters cap",
    }
    os.makedirs(RES, exist_ok=True)
    os.makedirs(ARC, exist_ok=True)
    os.makedirs(MAN, exist_ok=True)
    with open(os.path.join(RES, "CENSUS_P00B_RESULT.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(ARC, "CENSUS_P00B_TRUTH.json"), "w") as f:
        json.dump({"summary": summary,
                   "cells_S3d10": {str(k): list(v) for k, v in sorted(best_per["S3d10"].items())},
                   "cells_S2d20": {str(k): list(v) for k, v in sorted(best_per["S2d20"].items())},
                   "cells_B2d20": {str(k): list(v) for k, v in sorted(best_per["B2d20"].items())},
                   "cvt_centroids": [list(c) for c in cents],
                   "cvt_niche_sizes": niche,
                   "receipt": receipt}, f)
    with open(os.path.join(MAN, "CENSUS_P00B_MANIFEST.json"), "w") as f:
        json.dump({"config_digest": digest, "axes": list(AXES), "k": K,
                   "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f, indent=1)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
