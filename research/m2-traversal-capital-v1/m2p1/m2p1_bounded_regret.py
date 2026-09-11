#!/usr/bin/env python3
"""Discharge proof obligation P1: bounded regret of the registered interleaved solver.

CLAIM under test (THEORY_GAPS.md section 4.1):

    for every method m, task T and budget b,
        slots(solve(T,b,m))  <=  RHO_MAX * slots(solve(T,b,empty))     with RHO_MAX = 2

If this holds, deploying ANY generator can cost at most a bounded factor and can never
make a target unsolvable or incorrect -- which is what makes universal non-inferiority a
dominated admission rule rather than a safety property.

This is an EXHAUSTIVE empirical discharge against the REAL iterator (duplicate filtering,
guided exhaustion, counterexample pruning all live), not a model of it. It sweeps
adversarially chosen libraries, including ones designed to make the guided stream as
useless and as long-winded as possible:

  empty, true motifs, random fragments, LONGEST admissible fragments (max dilution),
  maximum-count library (16 fragments), and fragments that can never appear in any
  solution (pure waste).

A single observed ratio > RHO_MAX falsifies the claim and blocks the proposed delta.
"""
from __future__ import annotations
import argparse, json, random, statistics, sys
from fractions import Fraction
from itertools import product
from pathlib import Path

RHO_MAX = 2.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecologies", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=int, default=200000)
    ap.add_argument("--targets-per-ecology", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260910)
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "src"))
    import ocm.learning.methods as M

    rng = random.Random(a.seed)
    pool2 = [p for p in product(M.PRIMITIVES, repeat=2)]
    pool3 = [p for p in product(M.PRIMITIVES, repeat=3)]
    pool4 = [p for p in product(M.PRIMITIVES, repeat=4)]

    rows, worst = [], None
    for ecopath in a.ecologies:
        eco = json.loads(Path(ecopath).read_text())
        motifs = tuple(tuple(m) for m in eco.get("hidden_motifs", []))
        targets = eco["streams"]["protected"][: a.targets_per_ecology]

        libraries = {
            "empty": (),
            "true_motifs": motifs[:16],
            "random_len2": tuple(rng.sample(pool2, 8)),
            "random_len3": tuple(rng.sample(pool3, 12)),
            "longest_fragments": tuple(rng.sample(pool4, 16)),   # maximum dilution
            "max_count_mixed": tuple(rng.sample(pool2, 6) + rng.sample(pool3, 6)
                                     + rng.sample(pool4, 4)),
        }
        libraries = {k: v for k, v in libraries.items() if k == "empty" or v}

        for row in targets:
            task = M.PolynomialTask("br:%s" % row["normal_form_digest"][:12],
                                    tuple(Fraction(c) for c in row["coefficients"]))
            budget = M.SearchBudget(slots=a.budget, max_length=8)
            base = M.solve(task, budget)
            if not M.verify_solution(task, base):
                continue
            for name, frags in libraries.items():
                if name == "empty":
                    continue
                try:
                    method = M.GeneratorMethod(frags, ("br-train",))
                except ValueError:
                    continue
                cand = M.solve(task, budget, method)
                ratio = cand.slots / base.slots if base.slots else None
                ok_correct = (not cand.program) or M.verify_solution(task, cand)
                rec = {"ecology": Path(ecopath).stem, "library": name,
                       "target": row["normal_form_digest"][:12],
                       "baseline_slots": base.slots, "candidate_slots": cand.slots,
                       "ratio": round(ratio, 4) if ratio else None,
                       "candidate_verified_or_none": ok_correct,
                       "candidate_status": cand.status}
                rows.append(rec)
                if ratio and (worst is None or ratio > worst["ratio"]):
                    worst = rec

    ratios = [r["ratio"] for r in rows if r["ratio"] is not None]
    violations = [r for r in rows if r["ratio"] is not None and r["ratio"] > RHO_MAX + 1e-9]
    wrong = [r for r in rows if not r["candidate_verified_or_none"]]

    out = {
        "schema": "OCM_M2_BOUNDED_REGRET_P1_V1",
        "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "obligation": "P1 bounded regret: slots(solve with m) <= 2 * slots(solve without m)",
        "rho_max": RHO_MAX,
        "measurements": len(rows),
        "distinct_libraries": sorted({r["library"] for r in rows}),
        "max_observed_ratio": round(max(ratios), 4) if ratios else None,
        "mean_ratio": round(statistics.fmean(ratios), 4) if ratios else None,
        "violations_of_bound": len(violations),
        "correctness_violations": len(wrong),
        "worst_case_row": worst,
        "verdict": ("DISCHARGED_EMPIRICALLY" if not violations and not wrong
                    else "FALSIFIED"),
        "scope": ("exhaustive over the registered iterator at this budget and these "
                  "adversarial libraries; a proof over all budgets and libraries is still "
                  "owed, so this discharges the obligation EMPIRICALLY, not formally"),
    }
    Path(a.out).write_text(json.dumps({**out, "rows": rows}, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1))
    return 0 if not violations and not wrong else 1


if __name__ == "__main__":
    raise SystemExit(main())
