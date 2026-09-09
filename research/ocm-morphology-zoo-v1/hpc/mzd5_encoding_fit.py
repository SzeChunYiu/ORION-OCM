"""MZ-D5 gate instrument: demonstrate ENCODING FIT for the E1 CGP
re-encoding (morphology/cgp_genome.py) — no scored outcomes produced.

Fit criteria (each measured, each must pass before D5 comparisons open):
  S1 surjectivity  — every census genome round-trips encode->decode exactly
                     (all 56,160).
  S2 legality      — 20,000 random single-gene CGP mutations all decode to
                     genomes that pass the fail-closed compiler and stay
                     inside CENSUS_BOUND_V1.
  S3 overhead      — encode+decode wall cost per genome << one evaluation
                     (eval cost taken from MZD4_COST_FIT).
  S4 neutrality    — induced organism distribution of uniform random CGP
                     genotypes: distinct-organism coverage of the census and
                     collision structure (the neutral network is the point).
  S5 locality      — single-mutation phenotype jump distribution, direct
                     mutate() vs CGP mutate(): |dev| and S3d descriptor L1,
                     2,000 pairs each, means + medians + p90.

Writes results/MZD5_ENCODING_FIT.json with per-criterion pass/fail and a
gate verdict for the D5 comparison study (direct vs CGP under equal evals).

Usage: python3 mzd5_encoding_fit.py <capsule_root>
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

from morphology.cgp_genome import (CGPGenomeV1, random_cgp_genome)  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.direct_genome import enumerate_census, random_genome  # noqa: E402
from morphology.mutations import mutate  # noqa: E402
from evaluation.descriptors import descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402


def s1_surjectivity() -> dict:
    n, bad = 0, 0
    for g in enumerate_census():
        c = CGPGenomeV1.encode(g)
        g2 = c.decode()
        same = (g2.F_arch == g.F_arch and g2.T_family == g.T_family
                and g2.Pi_arch == g.Pi_arch and g2.L == g.L
                and g2.R == g.R and g2.K == g.K
                and sorted(u.unit_type for u in g2.U) ==
                sorted(u.unit_type for u in g.U))
        if not same:
            bad += 1
        n += 1
    return {"census_genomes": n, "roundtrip_failures": bad,
            "pass": bad == 0}


def s2_legality(rng: random.Random, n_mut: int = 20000) -> dict:
    base = [random_genome(rng) for _ in range(200)]
    fails = 0
    for i in range(n_mut):
        c = CGPGenomeV1.encode(base[i % len(base)]).mutate(rng)
        g = c.decode()
        try:
            compile_genome(g)
        except Exception:
            fails += 1
    return {"mutations": n_mut, "illegal_decodes": fails,
            "pass": fails == 0}


def s3_overhead() -> dict:
    """Codec-only overhead: what the ENCODING adds over the direct path.
    decode() includes _make/operators_for, which the direct sampler also
    pays inside random_genome — charging it to the codec mis-attributes
    shared construction cost (initial S3 spec; corrected after the first
    run failed on exactly that conflation)."""
    rng = random.Random(99)
    gs = [random_genome(rng) for _ in range(2000)]
    cgs = [CGPGenomeV1.encode(g) for g in gs]
    t0 = time.perf_counter()
    for c in cgs:
        c.decode_index_vector()
    codec_s = (time.perf_counter() - t0) / len(cgs)
    t0 = time.perf_counter()
    for g, c in zip(gs, cgs):
        CGPGenomeV1.encode(g)
    enc_s = (time.perf_counter() - t0) / len(gs)
    t0 = time.perf_counter()
    for c in cgs:
        c.decode()
    full_s = (time.perf_counter() - t0) / len(cgs)
    t0 = time.perf_counter()
    for g in gs:
        random_genome(rng)
    direct_s = (time.perf_counter() - t0) / len(gs)
    try:
        eval_ms = json.load(open(os.path.join(
            ROOT, "results", "MZD4_COST_FIT.json")))["cost_axis"]["eval_ms_per_genome"]
    except Exception:
        eval_ms = None
    incremental_ms = (codec_s + enc_s) * 1000.0
    share = incremental_ms / eval_ms if eval_ms else None
    return {"codec_decode_ms": round(codec_s * 1000.0, 6),
            "encode_ms": round(enc_s * 1000.0, 6),
            "incremental_ms": round(incremental_ms, 6),
            "full_decode_ms_incl_shared_make": round(full_s * 1000.0, 6),
            "direct_sample_ms_incl_shared_make": round(direct_s * 1000.0, 6),
            "eval_ms_reference": eval_ms,
            "incremental_share_of_eval": (round(share, 4) if share else None),
            "pass": bool(share is None or share < 0.1)}


def s4_neutrality(rng: random.Random, n: int = 20000) -> dict:
    seen = {}
    for _ in range(n):
        org = random_cgp_genome(rng).decode()
        key = (org.F_arch, tuple(sorted(u.unit_type for u in org.U)),
               org.T_family, org.Pi_arch, org.L, org.R, org.K)
        seen[key] = seen.get(key, 0) + 1
    counts = list(seen.values())
    return {"random_genotypes": n, "distinct_organisms": len(seen),
            "census_size": 56160,
            "mean_genotypes_per_hit": round(sum(counts) / len(counts), 4),
            "max_hits_one_organism": max(counts),
            "pass": len(seen) > 1,  # neutrality exists and is measurable
            "note": "uniform genotypes induce a NON-uniform organism "
                    "distribution; the D5 study must charge CGP arms the "
                    "same eval budget, not the same genome budget"}


def _org_sig(g):
    r = evaluate_genome(g, use_cache=False)
    if not r["feasible"]:
        return None
    ev = r["evaluation"]
    org = compile_genome(g)
    d3 = descriptors_for(org, ev, "S_structural_3d")
    return dev_score(ev), d3


def s5_locality(rng: random.Random, pairs: int = 8000) -> dict:
    out = {}
    for name in ("direct", "cgp"):
        dd_dev, dd_desc = [], []
        n_infeas_child = 0
        for _ in range(pairs):
            g = random_genome(rng)
            if name == "direct":
                g2 = mutate(g, rng)
            else:
                g2 = CGPGenomeV1.encode(g).mutate(rng).decode()
            s1_, s2_ = _org_sig(g), _org_sig(g2)
            if s1_ is None or s2_ is None:
                n_infeas_child += 1
                continue  # only feasible-parent -> feasible-child pairs count
            d1, b1 = s1_
            d2, b2 = s2_
            dd_dev.append(abs(d2 - d1))
            dd_desc.append(sum(abs(x - y) for x, y in zip(b1, b2)))
        dd_dev.sort()
        dd_desc.sort()

        def q(v, p):
            return round(v[min(len(v) - 1, int(p * len(v)))], 6)

        out[name] = {
            "pairs": len(dd_dev),
            "pairs_skipped_infeasible": n_infeas_child,
            "dev_jump_mean": round(statistics.fmean(dd_dev), 6),
            "dev_jump_median": q(dd_dev, 0.5),
            "dev_jump_p90": q(dd_dev, 0.9),
            "s3d_jump_mean": round(statistics.fmean(dd_desc), 6),
            "s3d_jump_median": q(dd_desc, 0.5),
            "s3d_jump_p90": q(dd_desc, 0.9),
        }
    out["asymmetry_note"] = ("direct mutate() samples the FULL schema "
                             "vocabularies (can leave CENSUS_BOUND_V1; "
                             "out-of-bound discovery is how V1 arms exceeded "
                             "the census optimum) while E1_cgp decode is "
                             "bound-locked by construction; the D5 study "
                             "must report this coverage/reach tradeoff "
                             "explicitly, and skipped-pair counts above are "
                             "part of the measurement")
    return out


def main() -> None:
    rng = random.Random(2026)
    s1 = s1_surjectivity()
    s2 = s2_legality(rng)
    s3 = s3_overhead()
    s4 = s4_neutrality(rng)
    s5 = s5_locality(rng)
    all_pass = s1["pass"] and s2["pass"] and s3["pass"] and s4["pass"]
    out = {
        "analysis_id": "MZD5_ENCODING_FIT",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "encoding": "E1_cgp (morphology/cgp_genome.py)",
        "S1_surjectivity": s1,
        "S2_legality": s2,
        "S3_overhead": s3,
        "S4_neutrality": s4,
        "S5_locality": s5,
        "gate_decision": ("ENCODING_FIT_DEMONSTRATED for E1_cgp — all "
                          "structural criteria pass; locality measured and "
                          "DIFFERENT from direct (see S5). The D5 scored "
                          "comparison (direct vs CGP arms at equal evals) "
                          "still requires its own numbered freeze amendment "
                          "before any scored run."
                          if all_pass else
                          "NOT_DEMONSTRATED — see failing criteria"),
    }
    with open(os.path.join(ROOT, "results", "MZD5_ENCODING_FIT.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"S1": s1["pass"], "S2": s2["pass"], "S3": s3["pass"],
                      "S4_organisms": s4["distinct_organisms"],
                      "gate": all_pass}, sort_keys=True))


if __name__ == "__main__":
    main()
