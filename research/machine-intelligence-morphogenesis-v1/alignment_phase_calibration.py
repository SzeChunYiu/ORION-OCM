#!/usr/bin/env python3
"""Analytic calibration for ecology-bias alignment + amortized build cost.

Parent-derived information-theoretic result; not a GMI novelty claim.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).with_name("EXACT_ECOLOGY_BIAS_ALIGNMENT_V1.json")

Q_STRUCTURED = (0.4, 0.4, 0.1, 0.1)
Q_UNIFORM = (0.25, 0.25, 0.25, 0.25)


def ecology(p: float) -> tuple[float, float, float, float]:
    return (p / 2.0, p / 2.0, (1.0 - p) / 2.0, (1.0 - p) / 2.0)


def cross_entropy(p_dist, q_dist) -> float:
    return -sum(p * math.log(q) for p, q in zip(p_dist, q_dist) if p > 0)


def phase_threshold(horizon: float, build_cost: float) -> float:
    # CE_structured = ln(10) - p ln(4), CE_uniform = ln(4)
    return (math.log(2.5) + build_cost / horizon) / math.log(4.0)


def lifetime_cost(p: float, horizon: float, build_cost: float, q) -> float:
    build = build_cost if q == Q_STRUCTURED else 0.0
    return build + horizon * cross_entropy(ecology(p), q)


def build_receipt() -> dict:
    build_cost = 1.0
    rows = []
    for horizon in (1, 2, 4, 8, 16, 64, 256):
        threshold = phase_threshold(horizon, build_cost)
        rows.append({
            "horizon": horizon,
            "structured_build_cost": build_cost,
            "p_star": threshold,
            "structured_can_win_for_p_in_[0,1]": threshold <= 1.0,
            "winner_if_p_above_threshold": "STRUCTURED",
            "winner_if_p_below_threshold": "UNIFORM",
        })
    # Sanity checks around a threshold that lies within [0,1].
    h = 16
    p_star = phase_threshold(h, build_cost)
    eps = 1e-6
    assert lifetime_cost(p_star + eps, h, build_cost, Q_STRUCTURED) < lifetime_cost(p_star + eps, h, build_cost, Q_UNIFORM)
    assert lifetime_cost(p_star - eps, h, build_cost, Q_STRUCTURED) > lifetime_cost(p_star - eps, h, build_cost, Q_UNIFORM)
    return {
        "schema": "ExactEcologyBiasAlignmentV1",
        "ecology": "P_p=[p/2,p/2,(1-p)/2,(1-p)/2]",
        "structured_prior": list(Q_STRUCTURED),
        "uniform_prior": list(Q_UNIFORM),
        "per_task_proxy": "ideal surprisal / code length = -ln Q(h)",
        "lifetime_cost": "C_M = C_build(M) + H * E_{h~P}[ -ln Q_M(h) ]",
        "identity": "E[-ln Q]=H(P)+D_KL(P||Q)",
        "phase_boundary": "p*(H,B) = [ln(2.5)+B/H]/ln(4)",
        "rows": rows,
        "interpretation": [
            "At long horizons, a biased morphology wins when the ecology places enough mass on the hypotheses that morphology favors.",
            "At short horizons, the structured morphology's build cost can prevent it from winning even under a favorable ecology.",
            "This is an information-theoretic/amortization calibration, not a novel morphology law.",
            "Track B must derive Q/K/c from morphology structure and predict them prospectively; assuming the priors by hand is insufficient."
        ],
        "terminal": "ECOLOGY_BIAS_ALIGNMENT_PHASE_EXACT__INFORMATION_THEORY_PARENT",
        "claim_ceiling": "analytic calibration of bias/ecology/lifetime interaction"
    }


def main() -> None:
    r = build_receipt()
    OUT.write_text(json.dumps(r, indent=2) + "\n")
    print(r["terminal"])


if __name__ == "__main__":
    main()
