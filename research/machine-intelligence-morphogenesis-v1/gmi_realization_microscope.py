"""Exact finite calibration for the GMI Developmental Realization Principle.

This module is intentionally small and parent-owned. It checks semantics of:

* semantic admissibility before resource comparison;
* Pareto dominance over matched-capability realizations;
* price-vector ranking reversal for incomparable resource vectors;
* affine horizon crossovers;
* discovery/build cost reversing a serving-only ranking;
* a bounded morphogenetic search missing the normative optimum.

Passing these checks does not establish a new intelligence law.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Iterable, Mapping, Sequence, Tuple


Vector = Tuple[float, ...]


@dataclass(frozen=True)
class Realization:
    name: str
    semantically_admissible: bool
    capability: float
    resources: Vector


@dataclass(frozen=True)
class LifetimeLine:
    name: str
    build_or_acquire: float
    per_use: float

    def cost(self, horizon: float) -> float:
        if horizon < 0:
            raise ValueError("horizon must be non-negative")
        return self.build_or_acquire + horizon * self.per_use


def _same_dim(a: Vector, b: Vector) -> None:
    if len(a) != len(b):
        raise ValueError("resource vectors have different dimensions")


def resource_weakly_dominates(a: Vector, b: Vector) -> bool:
    """True iff a is no worse than b on every minimized resource coordinate."""

    _same_dim(a, b)
    return all(x <= y for x, y in zip(a, b))


def resource_strictly_dominates(a: Vector, b: Vector) -> bool:
    return resource_weakly_dominates(a, b) and a != b


def feasible(
    candidates: Iterable[Realization], *, capability_floor: float
) -> Tuple[Realization, ...]:
    return tuple(
        c
        for c in candidates
        if c.semantically_admissible and c.capability >= capability_floor
    )


def realization_frontier(
    candidates: Iterable[Realization], *, capability_floor: float
) -> Tuple[Realization, ...]:
    """Pareto frontier over resources after semantic/capability feasibility gates."""

    pts = feasible(candidates, capability_floor=capability_floor)
    out = []
    for i, candidate in enumerate(pts):
        if any(
            i != j
            and other.capability >= candidate.capability
            and resource_strictly_dominates(other.resources, candidate.resources)
            for j, other in enumerate(pts)
        ):
            continue
        out.append(candidate)
    return tuple(sorted(out, key=lambda c: c.name))


def scalar_cost(resources: Vector, weights: Vector) -> float:
    _same_dim(resources, weights)
    if any(w < 0 for w in weights):
        raise ValueError("resource prices must be non-negative")
    return sum(r * w for r, w in zip(resources, weights))


def scalar_optimum(
    candidates: Iterable[Realization],
    *,
    capability_floor: float,
    weights: Vector,
) -> Tuple[str, ...]:
    pts = feasible(candidates, capability_floor=capability_floor)
    if not pts:
        return ()
    scored = [(scalar_cost(c.resources, weights), c.name) for c in pts]
    best = min(score for score, _ in scored)
    return tuple(sorted(name for score, name in scored if isclose(score, best)))


def affine_horizon_crossover(a: LifetimeLine, b: LifetimeLine) -> float | None:
    """Solve a.cost(H) == b.cost(H); None when parallel."""

    denom = a.per_use - b.per_use
    if denom == 0:
        return None
    return (b.build_or_acquire - a.build_or_acquire) / denom


def complete_lifetime_cost(
    *,
    discovery_cost: float,
    build_cost: float,
    per_use_cost: float,
    horizon: float,
    maintenance_cost: float = 0.0,
) -> float:
    if min(discovery_cost, build_cost, per_use_cost, horizon, maintenance_cost) < 0:
        raise ValueError("lifetime components must be non-negative")
    return discovery_cost + build_cost + horizon * per_use_cost + maintenance_cost


def normative_optimum(
    candidates: Iterable[Realization],
    *,
    capability_floor: float,
    weights: Vector,
) -> Tuple[str, ...]:
    """Oracle optimum over the full admissible candidate set."""

    return scalar_optimum(
        candidates,
        capability_floor=capability_floor,
        weights=weights,
    )


def bounded_search_optimum(
    candidates: Mapping[str, Realization],
    *,
    proposal_order: Sequence[str],
    budget: int,
    capability_floor: float,
    weights: Vector,
) -> Tuple[str, ...]:
    """Best admissible realization among only the first `budget` proposals.

    This is intentionally not an optimizer model. It simply makes the distinction
    between the full normative candidate class and a bounded searched subset exact.
    """

    if budget < 0:
        raise ValueError("budget must be non-negative")
    seen = []
    for name in proposal_order[:budget]:
        if name not in candidates:
            raise KeyError(f"unknown realization in proposal order: {name}")
        seen.append(candidates[name])
    return scalar_optimum(
        seen,
        capability_floor=capability_floor,
        weights=weights,
    )


def calibration_receipt() -> dict:
    """Return deterministic exact calibration results."""

    # RP-1/RP-6: inadmissible candidate is excluded even if resource-free;
    # DOMINATED is removed by A while A/B remain incomparable.
    candidates = (
        Realization("A", True, 1.0, (1.0, 4.0)),
        Realization("B", True, 1.0, (4.0, 1.0)),
        Realization("DOMINATED", True, 1.0, (5.0, 5.0)),
        Realization("CHEAP_BUT_WRONG", False, 1.0, (0.0, 0.0)),
    )
    frontier = tuple(c.name for c in realization_frontier(candidates, capability_floor=1.0))

    # RP-2: price changes reverse the scalar winner for incomparable vectors.
    low_first_price = scalar_optimum(
        candidates,
        capability_floor=1.0,
        weights=(1.0, 0.1),
    )
    low_second_price = scalar_optimum(
        candidates,
        capability_floor=1.0,
        weights=(0.1, 1.0),
    )

    # RP-3: high-build/low-use vs low-build/high-use crossover.
    high_build = LifetimeLine("HIGH_BUILD_LOW_USE", 10.0, 1.0)
    low_build = LifetimeLine("LOW_BUILD_HIGH_USE", 1.0, 3.0)
    crossover = affine_horizon_crossover(high_build, low_build)

    # RP-4: serving-only A looks better, but expensive discovery reverses full lifetime.
    serving_only_a = 5.0 * 1.0
    serving_only_b = 5.0 * 3.0
    lifetime_a = complete_lifetime_cost(
        discovery_cost=20.0,
        build_cost=0.0,
        per_use_cost=1.0,
        horizon=5.0,
    )
    lifetime_b = complete_lifetime_cost(
        discovery_cost=0.0,
        build_cost=0.0,
        per_use_cost=3.0,
        horizon=5.0,
    )

    # RP-5/RP-9: bounded search sees only A/B; oracle candidate C is better.
    search_candidates = {
        "A": Realization("A", True, 1.0, (5.0,)),
        "B": Realization("B", True, 1.0, (3.0,)),
        "C": Realization("C", True, 1.0, (1.0,)),
    }
    normative = normative_optimum(
        search_candidates.values(),
        capability_floor=1.0,
        weights=(1.0,),
    )
    bounded = bounded_search_optimum(
        search_candidates,
        proposal_order=("A", "B", "C"),
        budget=2,
        capability_floor=1.0,
        weights=(1.0,),
    )

    return {
        "schema": "GMIRealizationCalibrationReceiptV1",
        "frontier": frontier,
        "price_vector_1_optimum": low_first_price,
        "price_vector_2_optimum": low_second_price,
        "horizon_crossover": crossover,
        "cost_at_h2": {
            high_build.name: high_build.cost(2.0),
            low_build.name: low_build.cost(2.0),
        },
        "cost_at_h10": {
            high_build.name: high_build.cost(10.0),
            low_build.name: low_build.cost(10.0),
        },
        "discovery_reversal": {
            "serving_only_A": serving_only_a,
            "serving_only_B": serving_only_b,
            "full_lifetime_A": lifetime_a,
            "full_lifetime_B": lifetime_b,
        },
        "normative_optimum": normative,
        "bounded_search_optimum": bounded,
        "terminal": "GMI_REALIZATION_FINITE_CALIBRATION_GREEN_V1",
        "claim_boundary": "Exact finite semantics only; all mathematical ideas are parent-owned at this scope.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
