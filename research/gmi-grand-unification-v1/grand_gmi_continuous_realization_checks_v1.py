#!/usr/bin/env python3
"""Exact/numerical witnesses for CONTINUOUS_REALIZATION_BRIDGE_THEOREM_V1."""

import json
import math


def relu(x):
    return max(0.0, x)


def neural_abs(x):
    return relu(x) + relu(-x)


def program_abs(x):
    return x if x >= 0.0 else -x


def main():
    # A. Exact dual realization of |x| on a binary-rational grid.
    dual_checks = 0
    for k in range(-64, 65):
        x = k / 64.0
        target = abs(x)
        assert neural_abs(x) == target
        assert program_abs(x) == target
        assert neural_abs(x) == program_abs(x)
        dual_checks += 1
    assert dual_checks == 129

    # B. Approximation-to-capability transport under 1-Lipschitz absolute loss.
    eta = 1.0 / 32.0
    stability_checks = 0
    max_error = 0.0
    for k in range(-128, 129):
        x = k / 128.0
        f = x * x
        g = f + eta * math.sin(math.pi * x)
        err = abs(g - f)
        assert err <= eta + 1e-15
        # Absolute loss against the exact target differs from zero by exactly err.
        assert abs(g - f) <= eta + 1e-15
        max_error = max(max_error, err)
        stability_checks += 1
    assert stability_checks == 257

    # C. Margin transports approximate scores into exact zero-error decisions.
    gamma = 0.25
    perturb = 0.125
    margin_checks = 0
    for score in (-1.0, -0.5, -0.25, 0.25, 0.5, 1.0):
        assert abs(score) >= gamma
        for delta in (-perturb, 0.0, perturb):
            approx = score + delta
            assert (approx > 0) == (score > 0)
            margin_checks += 1
    assert margin_checks == 18

    receipt = {
        "terminal": "GRAND_GMI_CONTINUOUS_REALIZATION_BRIDGE_ALL_GREEN",
        "absolute_value_dual_realization_grid_checks": dual_checks,
        "stability_grid_checks": stability_checks,
        "certified_uniform_error": eta,
        "observed_max_error": max_error,
        "margin_preservation_checks": margin_checks,
        "neural_universal_approximation_used_as_parent_theory": True,
        "neural_necessity_from_density_claimed": False,
        "trainability_from_existence_claimed": False,
        "scope_boundary": "Checker validates exact witnesses and stability transport, not a universal-approximation theorem or architecture-specific rates."
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
