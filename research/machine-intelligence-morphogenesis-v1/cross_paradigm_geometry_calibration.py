#!/usr/bin/env python3
"""Exact parent-domain structure->geometry calibrations.

Three deliberately different paradigms:
- program/library search via code length / branching burden;
- symmetric Bayesian evidence accumulation via prior log odds;
- quadratic gradient descent via contraction factors.

These are parent-owned analytic models. The test asks what, if anything, is common
across them beyond a target-conditioned burden profile.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).with_name("EXACT_CROSS_PARADIGM_GEOMETRY_V1.json")
P_POINTS = (0.1, 0.25, 0.5, 0.75, 0.9)


def program_costs():
    # Two target families. A macro for one family shortens code length from 4 to 2.
    # Enumerative binary search proxy is 2^L candidates.
    return {
        "MACRO_A": (2**2, 2**4),
        "MACRO_B": (2**4, 2**2),
    }


def bayes_samples(prior_plus: float, posterior_threshold: float = 0.95, llr_per_observation: float = math.log(3.0)):
    """Exact deterministic-evidence sample count in a symmetric log-odds model."""
    l0 = math.log(prior_plus / (1.0 - prior_plus))
    t = math.log(posterior_threshold / (1.0 - posterior_threshold))
    n_plus = max(0, math.ceil((t - l0) / llr_per_observation))
    n_minus = max(0, math.ceil((t + l0) / llr_per_observation))
    return n_plus, n_minus


def neural_steps(lambda_x: float, lambda_y: float, eta: float = 0.5, amplitude_tolerance: float = 0.1):
    """Steps for coordinate-aligned quadratic GD error to shrink below tolerance."""
    def steps(lam: float) -> int:
        rho = abs(1.0 - eta * lam)
        if rho == 0.0:
            return 1
        return math.ceil(math.log(amplitude_tolerance) / math.log(rho))
    return steps(lambda_x), steps(lambda_y)


def expected(pair, p):
    return p * pair[0] + (1.0 - p) * pair[1]


def winner(costs, p):
    scored = {name: expected(pair, p) for name, pair in costs.items()}
    best = min(scored.values())
    wins = sorted(name for name, value in scored.items() if abs(value - best) < 1e-12)
    return scored, wins


def build_receipt():
    program = program_costs()
    bayes = {
        "PRIOR_PLUS": bayes_samples(0.8),
        "PRIOR_MINUS": bayes_samples(0.2),
    }
    neural = {
        "FAST_X": neural_steps(1.0, 0.25),
        "FAST_Y": neural_steps(0.25, 1.0),
    }

    assert bayes == {"PRIOR_PLUS": (2, 4), "PRIOR_MINUS": (4, 2)}
    assert neural == {"FAST_X": (4, 18), "FAST_Y": (18, 4)}

    families = {
        "programmatic_library": {
            "morphology_cost_vector": {k: list(v) for k, v in program.items()},
            "unit": "binary enumerative candidates proxy",
            "rows": [],
        },
        "probabilistic_bayes": {
            "morphology_cost_vector": {k: list(v) for k, v in bayes.items()},
            "unit": "observations to posterior >=0.95 under fixed log-likelihood-ratio evidence",
            "rows": [],
        },
        "neural_quadratic_gd": {
            "morphology_cost_vector": {k: list(v) for k, v in neural.items()},
            "unit": "gradient steps to coordinate error <=0.1",
            "rows": [],
        },
    }

    for p in P_POINTS:
        for key, costs in (
            ("programmatic_library", program),
            ("probabilistic_bayes", bayes),
            ("neural_quadratic_gd", neural),
        ):
            scored, wins = winner(costs, p)
            families[key]["rows"].append({
                "p_family_X": p,
                "expected_cost": scored,
                "winner": wins,
            })

    # All are symmetric and must switch at p=.5.
    for family in families.values():
        assert len(family["rows"][0]["winner"]) == 1
        assert len(family["rows"][2]["winner"]) == 2
        assert len(family["rows"][-1]["winner"]) == 1

    return {
        "schema": "ExactCrossParadigmGeometryV1",
        "families": families,
        "common_form": "Each morphology induces a target-family-conditioned burden vector c_M; ecology P yields E_P[c_M].",
        "interpretation": [
            "All three paradigm-specific structures induce different developmental burdens on target families and exact ecology-dependent winner reversals.",
            "The mechanism producing c_M is different in each paradigm: code length/search branching, Bayesian prior odds/evidence, and optimization contraction.",
            "The shared expected-cost form is too generic to establish a distinct GMI invariant; it is decision/portfolio mathematics.",
            "A stronger theory must predict c_M or a compressed sufficient signature from morphology structure before target outcomes and transfer that predictor across paradigms."
        ],
        "terminal": "CROSS_PARADIGM_PHASE_CALIBRATED__COMMON_EXPECTED_COST_FORM_TOO_GENERIC",
        "claim_ceiling": "exact parent-domain calibration; no cross-paradigm GMI law established"
    }


def main():
    r = build_receipt()
    OUT.write_text(json.dumps(r, indent=2) + "\n")
    print(r["terminal"])


if __name__ == "__main__":
    main()
