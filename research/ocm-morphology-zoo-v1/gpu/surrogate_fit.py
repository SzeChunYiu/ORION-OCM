"""Fit + calibrate the search-side surrogate on real tape outputs (GPU lane).

Trains gpu.surrogate.SurrogateEnsemble on (archive descriptors -> dev_score)
over a frozen-seed sample evaluated by the bit-identical batched T0 tape,
then reports held-out Spearman calibration.  Search-side only (#71): the
surrogate ranks promotions; exact reevaluation stays the ground truth.

Usage: python3 -m gpu.surrogate_fit --root . --n 8000 --seed 4211 \
          --archive B_behavior_2d [--backend torch]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpu import encode as _encode  # noqa: E402
from gpu.batch_descriptors import descriptor_matrix  # noqa: E402
from gpu.firehose import genomes_random  # noqa: E402
from gpu.surrogate import SurrogateEnsemble  # noqa: E402
from gpu.t0_tape import make_backend, run_t0_tape  # noqa: E402
from morphology.compile import InvariantViolation  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=4211)
    ap.add_argument("--archive", default="B_behavior_2d")
    ap.add_argument("--backend", default="auto")
    ap.add_argument("--holdout", type=float, default=0.2)
    args = ap.parse_args()

    t0 = time.time()
    genomes = [g for g in genomes_random(args.n, args.seed) if _ok(g)]
    batch = _encode.encode_batch(genomes)
    tape = run_t0_tape(batch, make_backend(args.backend))
    X = descriptor_matrix(batch, tape, args.archive)
    y = [dev_score(rec["evaluation"]) for rec in tape]
    n_h = max(2, int(len(y) * args.holdout))
    Xtr, ytr = X[:-n_h], y[:-n_h]
    Xh, yh = X[-n_h:], y[-n_h:]
    sur = SurrogateEnsemble()
    stamp = sur.fit(Xtr, ytr)
    cal = sur.calibrate(Xh, yh)
    out: Dict[str, Any] = {
        "run_id": "GS_GPU_SURROGATE",
        "label": "SMOKE_NOT_SCORED",  # search-side ranking aid, never a score
        "archive": args.archive, "n_train": len(ytr), "n_holdout": n_h,
        "seed": args.seed, "members": stamp["members"],
        "sklearn_version": stamp["sklearn_version"],
        "torch_version": stamp["torch_version"],
        "backend": make_backend(args.backend).name,
        "calibration_spearman": cal,
        "note": "ranks promotions only; exact reevaluation is ground truth",
        "wall_s": round(time.time() - t0, 3),
        "host": os.environ.get("ZOO_HOST", "")}
    res = os.path.join(args.root, "results")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "GS_GPU_SURROGATE.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps(out, sort_keys=True))


def _ok(g: Any) -> bool:
    try:
        from morphology.compile import compile_genome
        compile_genome(g)
        return True
    except InvariantViolation:
        return False


if __name__ == "__main__":
    main()
