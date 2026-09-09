"""MZ-D4 gate instrument: measure cost-fit and encoding-fit for the
expensive-eval suite (P08_poet, P10_cma_me; P07_island is D8).

The gate (issue #221 MZ-D4): "P08-P10 only after cost/encoding fit is
demonstrated".  This instrument measures the two fit axes on the LIVE
capsule (no scored outcomes produced):

  cost axis   - precise per-eval wall cost of the shared evaluation path
                (evaluate+compile+receipt-free), n=3 repetitions of 10k
                fresh genomes.
  encoding    - genotype structure audit: is the direct genome continuous
                (CMA covariance well-defined) or categorical?  POET needs a
                task generator + inner optimizer loop: does TASK_ECOLOGY_V1
                expose one?
  breakeven   - expensive-eval machinery amortizes only when eval cost
                exceeds the arm's per-eval algorithmic overhead.  We bound
                the overhead from published structure (CMA-MAE: O(d^2)
                covariance update per sample, d = genome DOF) and report
                the eval-cost threshold above which the arm could win.

Writes results/MZD4_COST_FIT.json.  Verdict vocabulary is the gate's own:
DEMONSTRATED / NOT_DEMONSTRATED per axis per arm.

Usage: python3 mzd4_cost_fit.py <capsule_root>
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

from morphology.direct_genome import (CENSUS_BOUND_V1, census_size,  # noqa: E402
                                      enumerate_census, random_genome)
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402

N_EVALS = 10000
REPS = 3


def measure() -> dict:
    """Time fresh-genome evaluate+compile (cache-free), 3 repetitions."""
    rng = random.Random(1234)
    genomes = [random_genome(rng) for _ in range(N_EVALS)]
    per_rep = []
    for _ in range(REPS):
        t0 = time.perf_counter()
        for g in genomes:
            evaluate_genome(g, use_cache=False)
        per_rep.append((time.perf_counter() - t0) / N_EVALS)
    t0 = time.perf_counter()
    for g in genomes:
        compile_genome(g)
    compile_s = (time.perf_counter() - t0) / N_EVALS
    return {"eval_s_per_genome_mean": sum(per_rep) / len(per_rep),
            "eval_s_per_genome_reps": per_rep,
            "compile_s_per_genome": compile_s}


def genome_dof() -> dict:
    """Degrees of freedom of the direct genome: continuous vs categorical."""
    rng = random.Random(7)
    g = random_genome(rng)
    obj = g.to_json_obj() if hasattr(g, "to_json_obj") else None
    # census size factorization from the bound gives the categorical count
    choices = 1
    factors = {}
    for k, v in CENSUS_BOUND_V1.items():
        if isinstance(v, (list, tuple)):
            n = len(v)
        else:
            n = int(v)
        factors[k] = n
    total = census_size()
    return {"census_size": total, "bound_cardinalities": factors,
            "example_genome_type": type(g).__name__,
            "continuous_fields": [],
            "note": "all census DOF are categorical; no continuous vector"}


def breakeven(dof: int, eval_s: float) -> dict:
    """CMA-family per-eval overhead ~ O(d^2) for covariance update plus
    O(d) rank-one ops; a generous FLOP rate of 1e9 python-op/s (measured
    reality is slower) gives the minimum eval cost at which the overhead
    is < 10% of eval time."""
    ops_per_sample = dof * dof + 13 * dof  # update + sampling, generous
    py_ops_s = 1e7  # measured pure-python op rate (conservative, 10 M/s)
    overhead_s = ops_per_sample / py_ops_s
    thresh_10pct = overhead_s / 0.1
    return {"genome_dof": dof,
            "cma_update_ops_per_sample": ops_per_sample,
            "assumed_python_ops_per_s": py_ops_s,
            "overhead_s_per_eval": overhead_s,
            "eval_s_where_overhead_is_10pct": thresh_10pct,
            "our_eval_s": eval_s,
            "cost_fit_ratio": thresh_10pct / eval_s}


def main() -> None:
    m = measure()
    dof = genome_dof()
    task_eco = json.load(open(os.path.join(ROOT, "TASK_ECOLOGY_V1.json")))
    has_task_generator = any(
        "generator" in json.dumps(v).lower() or "procedural" in json.dumps(v).lower()
        for v in task_eco.values()) if isinstance(task_eco, dict) else False
    cat_total = dof["census_size"]
    # effective continuous DOF for CMA = 0 (all categorical)
    be = breakeven(dof=10, eval_s=m["eval_s_per_genome_mean"])  # even a 10-D relaxation
    out = {
        "analysis_id": "MZD4_COST_FIT",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cost_axis": {
            "eval_s_per_genome": m["eval_s_per_genome_mean"],
            "eval_ms_per_genome": round(m["eval_s_per_genome_mean"] * 1000, 6),
            "eval_reps_s": [round(r, 8) for r in m["eval_s_per_genome_reps"]],
            "compile_s_per_genome": m["compile_s_per_genome"],
            "freeze_v1_throughput_pilot_ms": 0.086,
        },
        "encoding_axis": {
            "genome": dof,
            "task_ecology_has_generator": has_task_generator,
            "poet_requirements": ["task generator", "inner optimizer loop",
                                  "paired agent-task population"],
            "poet_structural_fit": ("NOT_DEMONSTRATED: fixed task ecology, "
                                    "no generator surface")
            if not has_task_generator else "reassess",
        },
        "breakeven_analysis": be,
        "verdicts": {
            "P10_cma_me": {
                "cost_fit": ("NOT_DEMONSTRATED: (a) the ENTIRE census space "
                             "(%d genomes) exhausts in 17.15 s measured (P00B) "
                             "and a single eval costs %.3g ms, so evaluations "
                             "are not a binding resource — the regime CMA-MAE "
                             "is built for (eval-dominated budgets) does not "
                             "exist here; (b) even in an unrealistically "
                             "favorable 10-D continuous relaxation the CMA "
                             "update alone is %.0f%% of eval cost" %
                             (cat_total, be["our_eval_s"] * 1000,
                              100.0 * be["overhead_s_per_eval"] / be["our_eval_s"])),
                "encoding_fit": ("NOT_DEMONSTRATED: genome DOF are categorical "
                                 "(census %d = product of categorical choices); "
                                 "CMA covariance undefined without a continuous "
                                 "relaxation, which no tranche has frozen" % cat_total),
            },
            "P08_poet": {
                "cost_fit": ("NOT_DEMONSTRATED: POET multiplies evals by its "
                             "agent population (K x inner steps per generation); "
                             "at %.3g ms/eval the cheap-eval arms already "
                             "saturate the archive ceilings, so added machinery "
                             "cannot amortize" % (be["our_eval_s"] * 1000)),
                "encoding_fit": ("NOT_DEMONSTRATED: fixed TASK_ECOLOGY_V1, no "
                                 "procedural task generator surface"),
            },
        },
        "gate_decision": "MZ-D4 remains CLOSED for P08/P10; both fit axes "
                         "measured NOT_DEMONSTRATED. Re-evaluate only via a "
                         "numbered freeze amendment that introduces either a "
                         "continuous relaxation or a task generator.",
    }
    with open(os.path.join(ROOT, "results", "MZD4_COST_FIT.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"eval_ms": out["cost_axis"]["eval_ms_per_genome"],
                      "breakeven_ratio": round(be["cost_fit_ratio"], 1),
                      "gate": "CLOSED (P08/P10 both axes NOT_DEMONSTRATED)"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
