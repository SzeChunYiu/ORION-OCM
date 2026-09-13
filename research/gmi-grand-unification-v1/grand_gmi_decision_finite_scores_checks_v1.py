#!/usr/bin/env python3
"""Exact score-level RDP boundary checks with explicit infinite-score handling.

Inputs are exact integer/rational scores, plus +infinity for unusable actions.
This checks already established scores; finite samples do not establish an
infinite-ecology supremum or a uniform loss-field error certificate.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from itertools import product
from pathlib import Path

INFINITY = math.inf


def exact_finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(f"{name} must be an exact finite integer or rational")
    return Fraction(value)


def score(value):
    if isinstance(value, float) and value == INFINITY:
        return INFINITY
    return exact_finite(value, "score")


def decision_report(true_scores, estimated_scores, delta, alpha=0):
    """Certify score perturbations and all alpha-optimal estimated choices.

There must be a finite optimum. Matching +infinity entries carry only order
information; they are never subtracted. The full field-to-score implication
is proved in RDP-1 and is not inferred from these score inputs.
"""
    true = tuple(score(value) for value in true_scores)
    estimated = tuple(score(value) for value in estimated_scores)
    delta = exact_finite(delta, "delta")
    alpha = exact_finite(alpha, "alpha")
    if not true or len(true) != len(estimated):
        raise ValueError("Require matching nonempty action score vectors")
    if delta < 0 or alpha < 0:
        raise ValueError("Precision and selector slack must be nonnegative")
    infinite_actions = []
    finite_actions = []
    for index, (actual, approx) in enumerate(zip(true, estimated)):
        if actual == INFINITY or approx == INFINITY:
            if actual != approx:
                raise ValueError("Finite uniform error cannot change an infinite-score action")
            infinite_actions.append(index)
        else:
            finite_actions.append(index)
            if abs(approx - actual) > delta:
                raise ValueError("Score perturbation exceeds the declared precision")
    if not finite_actions:
        raise ValueError("All action scores are infinite; finite regret is undefined")
    true_best = min(true[index] for index in finite_actions)
    estimated_best = min(estimated[index] for index in finite_actions)
    true_minimizers = tuple(index for index in finite_actions if true[index] == true_best)
    estimated_minimizers = tuple(index for index in finite_actions if estimated[index] == estimated_best)
    allowed_choices = tuple(
        index for index in finite_actions if estimated[index] <= estimated_best + alpha
    )
    regrets = tuple(true[index] - true_best for index in allowed_choices)
    margin = None
    if len(true_minimizers) == 1:
        optimum = true_minimizers[0]
        gaps = [true[index] - true_best for index in finite_actions if index != optimum]
        # Infinite-score competitors and absence of competitors both give +inf.
        margin = min(gaps, default=INFINITY)
    return {
        "true_minimizers": true_minimizers,
        "estimated_minimizers": estimated_minimizers,
        "allowed_choices": allowed_choices,
        "regrets": regrets,
        "regret_bound": 2 * delta + alpha,
        "margin": margin,
        "infinite_action_indices": tuple(infinite_actions),
    }


def finite_field_report(true_losses, estimated_losses, delta, alpha=0):
    """Check a complete finite action-by-ecology loss field before reducing it."""
    true = tuple(tuple(exact_finite(value, "loss") for value in row) for row in true_losses)
    estimated = tuple(tuple(exact_finite(value, "loss") for value in row) for row in estimated_losses)
    delta = exact_finite(delta, "delta")
    if not true or len(true) != len(estimated):
        raise ValueError("Require matching nonempty finite action sets")
    ecology_count = len(true[0])
    if not ecology_count or any(len(row) != ecology_count for row in true + estimated):
        raise ValueError("Require a matching nonempty finite ecology for every action")
    if delta < 0 or any(
        abs(actual - approx) > delta
        for true_row, estimated_row in zip(true, estimated)
        for actual, approx in zip(true_row, estimated_row)
    ):
        raise ValueError("Loss-field error exceeds finite nonnegative precision")
    return decision_report(tuple(map(max, true)), tuple(map(max, estimated)), delta, alpha)


def run():
    domain_cases = (
        ("empty_actions", (), (), 0, 0),
        ("mismatched_actions", (0,), (0, 1), 0, 0),
        ("all_infinite_scores", (INFINITY, INFINITY), (INFINITY, INFINITY), 0, 0),
        ("infinite_precision", (0,), (0,), INFINITY, 0),
        ("negative_precision", (0,), (0,), -1, 0),
        ("infinite_selection_slack", (0,), (0,), 0, INFINITY),
        ("negative_selection_slack", (0,), (0,), 0, -1),
        ("negative_infinite_score", (-INFINITY,), (-INFINITY,), 0, 0),
        ("nan_score", (math.nan,), (math.nan,), 0, 0),
        ("true_infinite_estimated_finite", (0, INFINITY), (0, 1), 1, 0),
        ("true_finite_estimated_infinite", (0, 1), (0, INFINITY), 1, 0),
        ("false_score_precision", (0, 2), (0, 4), 1, 0),
    )
    rejected = []
    for label, true, estimated, delta, alpha in domain_cases:
        try:
            decision_report(true, estimated, delta, alpha)
        except ValueError:
            rejected.append(label)

    finite_cases = 0
    all_regrets_valid = True
    strict_margin_valid = True
    for true in product(range(5), repeat=2):
        for perturbations in product((-1, 0, 1), repeat=2):
            estimated = tuple(value + perturbation for value, perturbation in zip(true, perturbations))
            report = finite_field_report(tuple((value,) for value in true), tuple((value,) for value in estimated), 1)
            finite_cases += 1
            all_regrets_valid &= all(regret <= 2 for regret in report["regrets"])
            if report["margin"] is not None and report["margin"] > 2:
                strict_margin_valid &= report["estimated_minimizers"] == report["true_minimizers"]

    tie = decision_report((0, 2), (1, 1), 1)
    strict = decision_report((0, 3), (1, 2), 1)
    singleton = decision_report((7,), (8,), 1)
    unusable = decision_report((0, 2, INFINITY), (1, 1, INFINITY), 1)
    only_finite = decision_report((INFINITY, 7, INFINITY), (INFINITY, 8, INFINITY), 1)
    slack = decision_report((0, 3), (1, 2), 1, alpha=1)
    exact = decision_report((0, 2), (0, 2), 0)
    empty_ecology_rejected = False
    hidden_field_error_rejected = False
    try:
        finite_field_report(((),), ((),), 0)
    except ValueError:
        empty_ecology_rejected = True
    try:
        finite_field_report(((0, 100),), ((50, 100),), 1)
    except ValueError:
        hidden_field_error_rejected = True
    checks = {
        "all_invalid_domains_rejected": len(rejected) == len(domain_cases) == 12,
        "empty_ecology_rejected": empty_ecology_rejected,
        "score_agreement_does_not_certify_uniform_field_error": hidden_field_error_rejected,
        "finite_regret_bound": finite_cases == 225 and all_regrets_valid,
        "strict_margin_preserves_unique_optimum": strict_margin_valid,
        "equality_permits_tie_and_sharp_regret": (
            tie["estimated_minimizers"] == (0, 1) and max(tie["regrets"]) == 2
        ),
        "strict_margin_excludes_tie": strict["estimated_minimizers"] == (0,),
        "singleton_uses_infinite_margin_and_zero_regret": (
            singleton["margin"] == INFINITY and singleton["regrets"] == (0,)
        ),
        "infinite_actions_do_not_destroy_finite_optimum": (
            unusable["infinite_action_indices"] == (2,)
            and unusable["allowed_choices"] == (0, 1)
            and max(unusable["regrets"]) == 2
        ),
        "only_finite_action_is_stable": (
            only_finite["margin"] == INFINITY
            and only_finite["allowed_choices"] == (1,)
            and only_finite["regrets"] == (0,)
        ),
        "selection_slack_must_be_added": (
            slack["allowed_choices"] == (0, 1)
            and max(slack["regrets"]) == slack["regret_bound"] == 3
        ),
        "exact_losses_do_not_license_arbitrary_action": exact["allowed_choices"] == (0,),
        "infinity_subtraction_is_undefined": math.isnan(INFINITY - INFINITY),
    }
    green = all(checks.values())
    return {
        "terminal": "GRAND_GMI_DECISION_FINITE_SCORES_TRANCHE_" + ("ALL_GREEN" if green else "RED"),
        "all_checks_green": green,
        "determinism": "exact-rational-with-explicit-infinity-sentinel-no-rng",
        "scope": "Score-level finite-action boundary checks; infinite-ecology uniform bounds require separate evidence",
        "checks": checks,
        "observed": {"finite_perturbation_cases": finite_cases, "invalid_domains_rejected": len(rejected)},
        "rejected_domain_labels": rejected,
        "analytic_unbounded_ecology_counterexample": {
            "ecology": "positive integers n",
            "losses": "L_n(a) = Lhat_n(a) = n for every action",
            "uniform_loss_error": 0,
            "robust_scores": "+infinity for every action",
            "finite_regret_certificate": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["all_checks_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
