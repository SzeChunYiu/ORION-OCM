"""Exact toy phase calculator for Cognitive Polyphenism prediction v1.

This is a calibration model, not an empirical machine-intelligence result.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(frozen=True)
class PhaseParams:
    k: int
    q: float
    poly_serve: float = 1.15
    core_update: float = 1.0
    compile_cost: float = 2.5
    eager_serve: float = 1.2
    eager_update_per_phenotype: float = 2.0
    fixed_match: float = 1.0
    fixed_mismatch: float = 6.0


def stale_probability_uniform(k: int, q: float) -> float:
    """Probability a regime phenotype is stale when next queried.

    Regime queries are iid uniform over k regimes. An authoritative semantic
    update occurs independently with probability q before each query.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must lie in [0,1]")
    if q == 0.0:
        return 0.0
    p = 1.0 / k
    return q / (p + q - p * q)


def expected_costs(p: PhaseParams) -> dict[str, float]:
    sigma = stale_probability_uniform(p.k, p.q)
    poly = p.poly_serve + p.q * p.core_update + p.compile_cost * sigma
    eager = p.eager_serve + p.q * p.k * p.eager_update_per_phenotype
    fixed = p.fixed_match + (1.0 - 1.0 / p.k) * (
        p.fixed_mismatch - p.fixed_match
    )
    return {
        "POLYPHENIC_LAZY": poly,
        "EAGER_STATIC_HYBRID": eager,
        "BEST_SINGLE_FIXED": fixed,
    }


def evaluate(name: str, p: PhaseParams) -> dict:
    costs = expected_costs(p)
    return {
        "name": name,
        "parameters": asdict(p),
        "stale_probability": stale_probability_uniform(p.k, p.q),
        "costs": costs,
        "winner": min(costs, key=costs.get),
    }


def registered_receipt() -> dict:
    base = dict(
        poly_serve=1.15,
        core_update=1.0,
        compile_cost=2.5,
        eager_serve=1.2,
        eager_update_per_phenotype=2.0,
        fixed_match=1.0,
        fixed_mismatch=6.0,
    )
    scenarios = [
        evaluate(
            "P_PLUS_HETEROGENEOUS",
            PhaseParams(k=16, q=0.05, **base),
        ),
        evaluate(
            "N_TWIN_LOW_DIVERSITY",
            PhaseParams(k=2, q=0.10, **base),
        ),
        evaluate(
            "N_TWIN_EXPENSIVE_COMPILATION",
            PhaseParams(k=16, q=0.05, **{**base, "compile_cost": 8.0}),
        ),
    ]
    return {
        "schema": "ExactCognitivePolyphenismPhaseV1",
        "claim_ceiling": "toy economic phase calibration only",
        "model": (
            "iid uniform regime queries; independent semantic update probability q "
            "before each query; lazy phenotype recompilation when queried stale"
        ),
        "scenarios": scenarios,
    }


def main() -> None:
    receipt = registered_receipt()
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
