#!/usr/bin/env python3
"""Exact/numerical checks for GENERALIZATION_ECOLOGY_INFERENCE_THEOREM_V1."""

import json
import math


def finite_class_radius(h_size, n, delta):
    return math.sqrt(math.log((2.0 * h_size) / delta) / (2.0 * n))


def main():
    # A. Finite-sample non-identifiability: both worlds agree on observed x=0,label=0.
    worlds = {
        "W0": {0: 0, 1: 0},
        "W1": {0: 0, 1: 1},
    }
    assert worlds["W0"][0] == worlds["W1"][0] == 0

    predictor_failures = {}
    for unseen_prediction in (0, 1):
        failed = [name for name, target in worlds.items() if unseen_prediction != target[1]]
        assert len(failed) == 1
        predictor_failures[str(unseen_prediction)] = failed[0]

    # B. Frozen finite-class certificate.
    h_size = 8
    n = 200
    delta = 0.05
    empirical_risk = 0.02
    radius = finite_class_radius(h_size, n, delta)
    upper = empirical_risk + radius
    assert abs(radius - 0.12008664575832081) < 1e-15
    assert upper <= 0.15
    assert upper > 0.10

    # C. Radius monotonicity in sample size and class size.
    sample_sizes = [50, 100, 200, 400]
    by_n = [finite_class_radius(h_size, k, delta) for k in sample_sizes]
    assert all(a > b for a, b in zip(by_n, by_n[1:]))

    class_sizes = [2, 8, 32]
    by_h = [finite_class_radius(k, n, delta) for k in class_sizes]
    assert all(a < b for a, b in zip(by_h, by_h[1:]))

    receipt = {
        "terminal": "GRAND_GMI_GENERALIZATION_ECOLOGY_INFERENCE_ALL_GREEN",
        "no_free_lunch_worlds": 2,
        "unseen_predictors_checked": 2,
        "predictor_failure_world": predictor_failures,
        "finite_class_size": h_size,
        "sample_count": n,
        "delta": delta,
        "empirical_risk": empirical_risk,
        "generalization_radius": radius,
        "certified_upper_risk": upper,
        "threshold_0_15_certified": upper <= 0.15,
        "threshold_0_10_certified": upper <= 0.10,
        "radius_decreases_with_sample_count": True,
        "radius_increases_with_class_size": True,
        "iid_and_fixed_class_assumptions_required": True,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
