#!/usr/bin/env python3
"""Exact exhaustive checks for Grand GMI robust decision precision V1."""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

ACTIONS = 3
ECOLOGIES = 2
DELTA = 1


def robust_scores(flat):
    return [max(flat[a * ECOLOGIES:(a + 1) * ECOLOGIES]) for a in range(ACTIONS)]


def run():
    total = 0
    score_bound_ok = 0
    regret_bound_ok = 0
    maximum_observed_regret = 0
    stable_applicable = 0
    stable_ok = 0
    unstable_wrong_or_tied = 0
    boundary_forced_ties = 0
    reversal_witness = None
    tie_witness = None

    perturbations = tuple(product((-1, 0, 1), repeat=ACTIONS * ECOLOGIES))

    for true_flat in product(range(4), repeat=ACTIONS * ECOLOGIES):
        true_r = robust_scores(true_flat)
        r_star = min(true_r)
        true_opts = [a for a, r in enumerate(true_r) if r == r_star]
        unique = len(true_opts) == 1
        if unique:
            a_star = true_opts[0]
            margin = min(true_r[a] - r_star for a in range(ACTIONS) if a != a_star)
        else:
            a_star = None
            margin = None

        for perturb in perturbations:
            total += 1
            approx_flat = tuple(x + p for x, p in zip(true_flat, perturb))
            approx_r = robust_scores(approx_flat)

            if all(abs(approx_r[a] - true_r[a]) <= DELTA for a in range(ACTIONS)):
                score_bound_ok += 1

            approx_best = min(approx_r)
            approx_opts = [a for a, r in enumerate(approx_r) if r == approx_best]
            regrets = [true_r[a] - r_star for a in approx_opts]
            maximum_observed_regret = max(maximum_observed_regret, max(regrets))
            if all(regret <= 2 * DELTA for regret in regrets):
                regret_bound_ok += 1

            if unique and margin > 2 * DELTA:
                stable_applicable += 1
                if approx_opts == [a_star]:
                    stable_ok += 1

            if unique and margin < 2 * DELTA and any(a != a_star for a in approx_opts):
                unstable_wrong_or_tied += 1
                if reversal_witness is None:
                    reversal_witness = {
                        "true_loss_field": list(true_flat),
                        "true_robust_scores": true_r,
                        "margin": margin,
                        "perturbation": list(perturb),
                        "approx_robust_scores": approx_r,
                        "approx_minimizers": approx_opts,
                    }

            if (
                unique
                and margin == 2 * DELTA
                and len(approx_opts) > 1
                and a_star in approx_opts
            ):
                boundary_forced_ties += 1
                if tie_witness is None:
                    tie_witness = {
                        "true_loss_field": list(true_flat),
                        "true_robust_scores": true_r,
                        "margin": margin,
                        "perturbation": list(perturb),
                        "approx_robust_scores": approx_r,
                        "approx_minimizers": approx_opts,
                    }

    observed = {
        "true_loss_fields": 4 ** (ACTIONS * ECOLOGIES),
        "perturbations_per_field": 3 ** (ACTIONS * ECOLOGIES),
        "total_cases": total,
        "score_bound_ok": score_bound_ok,
        "regret_bound_ok": regret_bound_ok,
        "maximum_observed_regret": maximum_observed_regret,
        "stable_margin_gt_2delta_applicable": stable_applicable,
        "stable_margin_gt_2delta_ok": stable_ok,
        "margin_lt_2delta_wrong_or_tied": unstable_wrong_or_tied,
        "margin_eq_2delta_forced_ties": boundary_forced_ties,
    }
    expected = {
        "true_loss_fields": 4096,
        "perturbations_per_field": 729,
        "total_cases": 2985984,
        "score_bound_ok": 2985984,
        "regret_bound_ok": 2985984,
        "maximum_observed_regret": 2,
        "stable_margin_gt_2delta_applicable": 107163,
        "stable_margin_gt_2delta_ok": 107163,
        "margin_lt_2delta_wrong_or_tied": 613659,
        "margin_eq_2delta_forced_ties": 94974,
    }
    ok = observed == expected and reversal_witness is not None and tie_witness is not None
    return {
        "terminal": (
            "GRAND_GMI_ROBUST_DECISION_PRECISION_TRANCHE_ALL_GREEN"
            if ok else "GRAND_GMI_ROBUST_DECISION_PRECISION_TRANCHE_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-integer-exhaustive-no-rng",
        "delta": DELTA,
        "observed": observed,
        "expected": expected,
        "first_subcritical_instability_witness": reversal_witness,
        "first_exact_boundary_tie_witness": tie_witness,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
