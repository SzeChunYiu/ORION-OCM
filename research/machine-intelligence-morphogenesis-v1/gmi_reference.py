"""Small exact reference evaluator for GMI-v1 definitions.

This is not an intelligence implementation.  It exists to lock the semantics of:

* capability/resource Pareto frontiers,
* ecology-family dominance,
* scalarization only after a declared utility/measure,
* lifecycle break-even,
* pre-solution rank information shift.

The scientific theory lives in GMI_THEORY_V1.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Callable, Iterable, Mapping, Sequence, Tuple


Vector = Tuple[float, ...]


@dataclass(frozen=True)
class FrontierPoint:
    """One reachable capability/resource operating point.

    Capability coordinates are maximized; resource coordinates are minimized.
    """

    capability: Vector
    resources: Vector


def _same_shape(a: FrontierPoint, b: FrontierPoint) -> None:
    if len(a.capability) != len(b.capability):
        raise ValueError("capability vectors have different dimensions")
    if len(a.resources) != len(b.resources):
        raise ValueError("resource vectors have different dimensions")


def weakly_dominates(a: FrontierPoint, b: FrontierPoint) -> bool:
    """Return True iff a is no worse than b on every registered coordinate."""

    _same_shape(a, b)
    capability_ok = all(x >= y for x, y in zip(a.capability, b.capability))
    resources_ok = all(x <= y for x, y in zip(a.resources, b.resources))
    return capability_ok and resources_ok


def strictly_dominates(a: FrontierPoint, b: FrontierPoint) -> bool:
    if not weakly_dominates(a, b):
        return False
    return a != b


def pareto_frontier(points: Iterable[FrontierPoint]) -> Tuple[FrontierPoint, ...]:
    pts = tuple(points)
    out = []
    for i, p in enumerate(pts):
        if any(i != j and strictly_dominates(q, p) for j, q in enumerate(pts)):
            continue
        out.append(p)
    return tuple(sorted(set(out), key=lambda p: (p.capability, p.resources)))


def frontier_weakly_dominates(
    a: Sequence[FrontierPoint], b: Sequence[FrontierPoint]
) -> bool:
    """Every operating point in b is weakly dominated by some point in a."""

    return all(any(weakly_dominates(pa, pb) for pa in a) for pb in b)


def profile_dominance(
    profile_a: Mapping[str, Sequence[FrontierPoint]],
    profile_b: Mapping[str, Sequence[FrontierPoint]],
) -> Tuple[bool, bool]:
    """Return (A weakly dominates B on the whole family, A strictly dominates B).

    Strict family-wide dominance means weak dominance on every registered ecology and a
    strict frontier improvement on at least one ecology. Winning one ecology while losing
    another is a tradeoff, not strict generality dominance.
    """

    if set(profile_a) != set(profile_b):
        raise ValueError("profiles must cover the same registered ecology family")

    all_weak = True
    strict_somewhere = False
    for ecology in sorted(profile_a):
        fa = pareto_frontier(profile_a[ecology])
        fb = pareto_frontier(profile_b[ecology])
        a_over_b = frontier_weakly_dominates(fa, fb)
        b_over_a = frontier_weakly_dominates(fb, fa)
        if not a_over_b:
            all_weak = False
        if a_over_b and not b_over_a:
            strict_somewhere = True
    return all_weak, all_weak and strict_somewhere


def scalar_profile_score(
    profile: Mapping[str, Sequence[FrontierPoint]],
    ecology_weights: Mapping[str, float],
    utility: Callable[[FrontierPoint], float],
) -> float:
    """Distributional scalarization after ecology weights and utility are declared."""

    if set(profile) != set(ecology_weights):
        raise ValueError("weights must cover exactly the registered ecology family")
    total_weight = sum(ecology_weights.values())
    if total_weight <= 0:
        raise ValueError("ecology weights must sum to a positive value")

    value = 0.0
    for ecology, points in profile.items():
        frontier = pareto_frontier(points)
        if not frontier:
            raise ValueError(f"empty reachable set for ecology {ecology!r}")
        value += ecology_weights[ecology] * max(utility(p) for p in frontier)
    return value / total_weight


def lifecycle_cost(build_cost: float, per_use_cost: float, horizon: int) -> float:
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    return build_cost + horizon * per_use_cost


def break_even_horizon(
    build_i: float, per_use_i: float, build_j: float, per_use_j: float
) -> float | None:
    """Solve C_i(H)=C_j(H); None when lines are parallel."""

    denom = per_use_i - per_use_j
    if denom == 0:
        return None
    return (build_j - build_i) / denom


def rank_information_shift(reset_rank: int, history_rank: int) -> float:
    """log2(rank_RESET / rank_HISTORY); positive means earlier proposal with history."""

    if reset_rank <= 0 or history_rank <= 0:
        raise ValueError("ranks must be positive")
    return log2(reset_rank / history_rank)


def median(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot take median of empty sequence")
    xs = sorted(values)
    n = len(xs)
    mid = n // 2
    if n % 2:
        return xs[mid]
    return (xs[mid - 1] + xs[mid]) / 2


def median_rank_information_shift(
    reset_ranks: Sequence[int], history_ranks: Sequence[int]
) -> float:
    if len(reset_ranks) != len(history_ranks):
        raise ValueError("rank sequences must have equal length")
    return median(
        [rank_information_shift(r0, rh) for r0, rh in zip(reset_ranks, history_ranks)]
    )
