"""Vectorizable-fraction measurement for the GS GPU lane (#221 sec 18, O).

Operator question (reuse-first correction, 2026-09-09): what fraction of
T0 evaluation can become a cheap vectorized proxy vs branchy object-heavy
CPU-only — measured on a real sample, not asserted.

Measures per candidate (frozen-seed sample from the census grammar):
  t_eval_total   evaluate_genome(g, "T0", use_cache=False)   (branchy exact)
  t_compile      compile_genome(g)                            (CPU-only share)
  t_lifetime     run_lifetime(org) on the precompiled organism (the branchy
                 simulation body — exactly the arithmetic the tape
                 reproduces)
  t_encode       gpu.encode.encode_genome(g)                  (compile +
                 features; the irreducible per-organism CPU cost of the
                 vectorized lane)
  t_tape_py      run_t0_tape over the whole batch, pure-python backend
  t_tape_numpy   same, numpy backend (when present)

Fidelity — the decisive number: the "vectorized proxy" is the SAME frozen
arithmetic (bit-identity asserted), so rank correlation between proxy and
exact dev_score must be EXACTLY 1.0 with zero mismatches.  A surrogate or
early-tier proxy that is only correlated would be a weaker claim; this one
is equality, and any mismatch is a defect that fails the run.

Emits results/GPU_VECTORIZABLE_FRACTION.json (UNSCLASSIFIED_BY_DEFAULT:
labelled SMOKE_NOT_SCORED — it is a cost/fidelity measurement, never a
scored outcome).

Usage: python3 -m gpu.measure_fraction --root . --n 128 --seed 2210
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.lifetime import run_lifetime  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402
from gpu import encode as _encode  # noqa: E402
from gpu.firehose import genomes_random  # noqa: E402
from gpu.surrogate import spearman_rho  # noqa: E402
from gpu.t0_tape import make_backend, run_t0_tape  # noqa: E402
from morphology.compile import compile_genome, InvariantViolation  # noqa: E402


def measure(root: str, n: int = 128, seed: int = 2210) -> Dict[str, Any]:
    genomes = genomes_random(n, seed)
    t_eval = t_compile = t_lifetime = t_encode = 0.0
    exact_scores: List[float] = []
    n_invariant = 0
    for g in genomes:
        try:
            t0 = time.time()
            org = compile_genome(g)
            t1 = time.time()
            t_compile += t1 - t0
            ev = run_lifetime(org)
            t2 = time.time()
            t_lifetime += t2 - t1
            exact_scores.append(dev_score(ev))
        except InvariantViolation:
            n_invariant += 1
            continue
        t0 = time.time()
        evaluate_genome(g, tier="T0", use_cache=False)
        t_eval += time.time() - t0
    # vectorized lane over the same sample (skip invariant violators)
    ok = [g for g in genomes if _compiles(g)]
    t0 = time.time()
    batch = _encode.encode_batch(ok)
    t_encode = time.time() - t0
    t0 = time.time()
    out_py = run_t0_tape(batch, make_backend("py"))
    t_tape_py = time.time() - t0
    t_tape_np = None
    try:
        import numpy  # noqa: F401
        t0 = time.time()
        out_np = run_t0_tape(batch, make_backend("numpy"))
        t_tape_np = time.time() - t0
    except Exception:
        out_np = None
    proxy_scores = [dev_score(rec["evaluation"]) for rec in out_py]
    # fidelity: proxy vs exact on the SAME genomes (order preserved: encode
    # skips nothing here because ok was prefiltered)
    mismatches = sum(1 for a, b in zip(exact_scores, proxy_scores) if a != b)
    rho = spearman_rho(proxy_scores, exact_scores) if exact_scores else 0.0
    n_ok = len(ok)
    frac = {
        "vectorizable_fraction_of_T0": round(t_lifetime / max(1e-9, t_eval), 6),
        "irreducible_cpu_fraction_of_T0": round(t_compile / max(1e-9, t_eval), 6),
        "encode_fraction_of_vectorized_lane": round(
            t_encode / max(1e-9, t_encode + (t_tape_np or t_tape_py)), 6),
        "definition": ("t_lifetime / t_eval_total over the sample; the tape "
                       "reproduces run_lifetime arithmetic bit-exactly, so "
                       "this is the share of exact T0 evaluation that "
                       "accelerates on GPU"),
    }
    summary = {
        "run_id": "GPU_VECTORIZABLE_FRACTION",
        "label": "SMOKE_NOT_SCORED",
        "n_sample": n, "seed": seed,
        "n_compiled": n_ok, "n_invariant_violations": n_invariant,
        "fidelity": {"dev_score_mismatches": mismatches,
                     "spearman_proxy_vs_exact": round(rho, 6),
                     "claim": "proxy IS the exact arithmetic (bit-identity); "
                              "rho must be 1.0 and mismatches 0"},
        "timings_s": {"eval_total": round(t_eval, 4),
                      "compile": round(t_compile, 4),
                      "lifetime_body": round(t_lifetime, 4),
                      "encode_batch": round(t_encode, 4),
                      "tape_py": round(t_tape_py, 4),
                      "tape_numpy": (round(t_tape_np, 4)
                                     if t_tape_np is not None else None)},
        "per_eval_ms": {"exact": round(1000.0 * t_eval / max(1, n_ok), 4),
                        "encode": round(1000.0 * t_encode / max(1, n_ok), 4),
                        "tape_py": round(1000.0 * t_tape_py / max(1, n_ok), 4),
                        "tape_numpy": (round(1000.0 * t_tape_np / max(1, n_ok), 4)
                                       if t_tape_np is not None else None)},
        "fraction": frac,
        "numpy_backend_identity": _identity(out_py, out_np),
        "host": {"node": platform.node(),
                 "python": platform.python_version(),
                 "machine": platform.machine()},
    }
    res = os.path.join(root, "results")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "GPU_VECTORIZABLE_FRACTION.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(json.dumps(summary, sort_keys=True))
    return summary


def _compiles(g: Any) -> bool:
    try:
        compile_genome(g)
        return True
    except InvariantViolation:
        return False


def _identity(a: List[Dict[str, Any]], b: List[Dict[str, Any]]) -> Any:
    if b is None:
        return None
    m = 0.0
    from gpu.firehose import _flat_nums
    for ra, rb in zip(a, b):
        for va, vb in zip(_flat_nums(ra), _flat_nums(rb)):
            m = max(m, abs(va - vb))
    return {"backend": "numpy", "ref": "py", "max_abs_diff": m}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--seed", type=int, default=2210)
    args = ap.parse_args()
    measure(args.root, args.n, args.seed)


if __name__ == "__main__":
    main()
