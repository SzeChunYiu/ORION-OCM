#!/usr/bin/env python3
"""Reuse-audit bottleneck measurement (#221 sec 2a): what fraction of T0
evaluation can become a cheap vectorized proxy (-> GPU/QDax) vs branchy
object-heavy work that must stay exact on CPU.

Method (100-candidate sample, seed 7, honest timings on the host it runs
on — NEVER the Mac):
  1. exact: wall time of evaluate_genome(g, tier="T0") per candidate;
  2. proxy-loop: time of the vectorizable-CANDIDATE math per candidate
     (genome feature vector + novelty descriptor vector) as a python loop;
  3. proxy-numpy: the same math batched through numpy (the shape a GPU
     kernel / QDax pipeline would consume);
  4. profile split: cProfile over the exact batch, cumulative time
     bucketed by module family (micro-world stepping vs compile/objects
     vs gates/invariants vs descriptors).

Writes results/REUSE_VECTORIZE_MEASUREMENT.json + stdout table.
"""
from __future__ import annotations

import cProfile
import io
import json
import os
import pstats
import random
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)

from evaluation.descriptors import descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.direct_genome import random_genome  # noqa: E402
from morphology.gs_bound import gs_uniform_sample  # noqa: E402

N = int(sys.argv[2]) if len(sys.argv) > 2 else 100


def main() -> None:
    rng = random.Random(7)
    genomes = [gs_uniform_sample(rng) for _ in range(N)]
    # second FRESH batch for profiling: evaluate_genome memoizes by
    # genotype digest, so re-evaluating the timed batch would profile the
    # cache-hit path (compile only) — not the true evaluation
    fresh = [gs_uniform_sample(rng) for _ in range(N)]

    # ---- 1. exact per-candidate wall time (viable / non-viable split)
    t0 = time.perf_counter()
    orgs_evals = []
    t_viable = []
    t_nonviable = []
    for g in genomes:
        ta = time.perf_counter()
        r = evaluate_genome(g, tier="T0")
        dt = time.perf_counter() - ta
        (t_viable if r["feasible"] else t_nonviable).append(dt)
        orgs_evals.append((compile_genome(g), r["evaluation"]))
    exact_s = time.perf_counter() - t0

    # ---- 2. proxy: loop
    from search.novelty_viability import novelty_vector
    t0 = time.perf_counter()
    for org, ev in orgs_evals:
        novelty_vector(org, ev)
    proxy_loop_s = time.perf_counter() - t0

    # ---- 3. proxy: numpy-batched (same math, stacked)
    import numpy as np
    vecs = np.array([novelty_vector(org, ev) for org, ev in orgs_evals],
                    dtype=np.float64)
    t0 = time.perf_counter()
    for _ in range(10):
        # np.ptp(arr, ...) not arr.ptp(...): the ndarray method was REMOVED in
        # numpy 2.0, so the method form raises AttributeError on any host with
        # numpy >= 2 (LUNARC compute nodes carry 2.x). The free function has
        # identical semantics on every numpy version, so this is a
        # compatibility repair and the measurement is unchanged.
        norm = (vecs - vecs.min(axis=0)) / (
            np.ptp(vecs, axis=0) + 1e-12)      # noqa: N806 (vectorized proxy)
        pd = np.sqrt(((vecs[:, None, :] - norm[None, :, :]) ** 2).sum(-1))
        knn = np.sort(pd, axis=1)[:, :15].mean(axis=1)
    proxy_numpy_s = (time.perf_counter() - t0) / 10.0

    # ---- 4. profile split over the FRESH batch (see note above)
    prof = cProfile.Profile()
    prof.enable()
    for g in fresh:
        evaluate_genome(g, tier="T0")
    prof.disable()
    ps = pstats.Stats(prof)
    # named top-level cumulative buckets over the FRESH batch: file-keyed
    # self-time fragments the stepping arithmetic across stdlib builtins
    # (sum/sorted/json), so we attribute by the owning pipeline stage.
    buckets = {"lifetime_micro_worlds": 0.0, "compile_objects": 0.0,
               "digest_canonicalize": 0.0, "other": 0.0}
    named_ct = {}
    total_tt = 0.0
    for (filename, _lineno, fname), (_cc, _nc, tt, ct, _callers) in \
            ps.stats.items():
        total_tt += tt
        if fname == "run_lifetime" and "/evaluation/lifetime" in filename:
            named_ct["lifetime_micro_worlds"] = named_ct.get(
                "lifetime_micro_worlds", 0.0) + ct
        elif fname == "compile_genome" and "/morphology/" in filename:
            named_ct["compile_objects"] = named_ct.get(
                "compile_objects", 0.0) + ct
        elif fname in ("digest", "phenotype_digest", "canonical_json") \
                and "/morphology/" in filename:
            named_ct["digest_canonicalize"] = named_ct.get(
                "digest_canonicalize", 0.0) + ct
    buckets.update({k: round(v, 4) for k, v in named_ct.items()})
    buckets["other"] = round(max(0.0, total_tt - sum(named_ct.values())), 4)
    tot = sum(buckets.values()) or 1.0

    out = {
        "schema": "REUSE_VECTORIZE_MEASUREMENT_V1",
        "n_candidates": N, "sample_seed": 7,
        "host": os.uname().nodename,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_viable_in_sample": len(t_viable),
        "exact_t0_seconds_total": round(exact_s, 4),
        "exact_t0_ms_per_candidate": round(exact_s / N * 1000.0, 4),
        "exact_t0_ms_per_viable": round(1000.0 * sum(t_viable) /
                                        max(1, len(t_viable)), 4),
        "exact_t0_ms_per_nonviable": round(1000.0 * sum(t_nonviable) /
                                           max(1, len(t_nonviable)), 4),
        "proxy_loop_seconds_total": round(proxy_loop_s, 4),
        "proxy_loop_ms_per_candidate": round(proxy_loop_s / N * 1000.0, 4),
        "proxy_numpy_batch_seconds": round(proxy_numpy_s, 4),
        "proxy_numpy_ms_per_candidate": round(proxy_numpy_s / N * 1000.0, 4),
        "profile_buckets_cumulative_s": {k: round(v, 4) for k, v in
                                         buckets.items()},
        "profile_buckets_share": {k: round(v / tot, 4) for k, v in
                                  buckets.items()},
        "vectorizable_fraction_loop_vs_exact": round(
            min(1.0, proxy_loop_s / exact_s), 4),
        "interpretation": {
            "proxy_loop_vs_exact": "upper bound on what a vectorized proxy "
                                   "could save per candidate if the proxy "
                                   "replaced the exact eval outright",
            "profile": "share of exact-eval cumulative time by module "
                       "family: sim stepping is the arrayification target; "
                       "compile/objects and gate checks are branchy and "
                       "stay CPU-exact"},
    }
    path = os.path.join(ROOT, "results", "REUSE_VECTORIZE_MEASUREMENT.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
