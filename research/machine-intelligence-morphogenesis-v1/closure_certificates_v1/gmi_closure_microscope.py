"""Exact, bounded microscopes for the ORION-OCM closure review.

These routines do not establish full GMI closure, empirical transfer, or
independent authorship. Fractions avoid floating-point tolerance masquerading
as an exact certificate. No protected beacon or repository state is touched.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import log, sqrt
from typing import Iterable, Sequence

Exact = int | Fraction


def q(value: Exact) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("Exact certificates require int or Fraction, not floats/bools")
    return Fraction(value)


def matrix(rows: Sequence[Sequence[Exact]]) -> list[list[Fraction]]:
    if not rows or not rows[0]:
        raise ValueError("At least one world and one candidate are required")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Ragged cost matrix")
    return [[q(v) for v in row] for row in rows]


def epsilon_optimal_sets(costs: Sequence[Sequence[Exact]], epsilon: Exact = 0) -> list[frozenset[int]]:
    """World-specific sets under a fixed, common admissible candidate domain."""
    e = q(epsilon)
    if e < 0:
        raise ValueError("epsilon must be nonnegative")
    c = matrix(costs)
    return [frozenset(j for j, v in enumerate(row) if v <= min(row) + e) for row in c]


def robust_candidates(costs: Sequence[Sequence[Exact]], epsilon: Exact = 0) -> frozenset[int]:
    sets = epsilon_optimal_sets(costs, epsilon)
    return frozenset.intersection(*sets)


def deterministic_minimax_regret(costs: Sequence[Sequence[Exact]]) -> tuple[Fraction, frozenset[int]]:
    c = matrix(costs)
    regrets = [max(row[j] - min(row) for row in c) for j in range(len(c[0]))]
    optimum = min(regrets)
    return optimum, frozenset(j for j, r in enumerate(regrets) if r == optimum)


def worst_case_error(costs: Sequence[Sequence[Exact]], probabilities: Sequence[Exact], epsilon: Exact = 0) -> Fraction:
    c = matrix(costs)
    p = [q(x) for x in probabilities]
    if len(p) != len(c[0]) or any(x < 0 for x in p) or sum(p) != 1:
        raise ValueError("probabilities must be a simplex point")
    sets = epsilon_optimal_sets(c, epsilon)
    return max(1 - sum(p[j] for j in s) for s in sets)


def rectangular_worst_regret(intervals: Sequence[tuple[Exact, Exact]], choice: int) -> Fraction:
    """Exact for independently variable costs in the FULL Cartesian rectangle.

    For correlated uncertainty this remains an upper bound, not an iff test.
    The own lower endpoint is excluded: a candidate cannot simultaneously take
    its upper and lower values in the same world.
    """
    if not intervals:
        raise ValueError("Empty candidate set")
    bounds = [(q(lo), q(hi)) for lo, hi in intervals]
    if any(lo > hi for lo, hi in bounds):
        raise ValueError("Reversed interval")
    if isinstance(choice, bool) or not isinstance(choice, int) or not 0 <= choice < len(bounds):
        raise ValueError("Invalid candidate index")
    competitors = [lo for j, (lo, _) in enumerate(bounds) if j != choice]
    return max(Fraction(0), bounds[choice][1] - min(competitors)) if competitors else Fraction(0)


def rref(rows: Sequence[Sequence[Exact]]) -> tuple[list[list[Fraction]], list[int]]:
    a = matrix(rows)
    pivots: list[int] = []
    i = 0
    for j in range(len(a[0])):
        pivot = next((k for k in range(i, len(a)) if a[k][j]), None)
        if pivot is None:
            continue
        a[i], a[pivot] = a[pivot], a[i]
        divisor = a[i][j]
        a[i] = [x / divisor for x in a[i]]
        for k in range(len(a)):
            if k != i:
                factor = a[k][j]
                a[k] = [x - factor * y for x, y in zip(a[k], a[i])]
        pivots.append(j)
        i += 1
        if i == len(a):
            break
    return a, pivots


def rank(rows: Sequence[Sequence[Exact]]) -> int:
    return len(rref(rows)[1])


def recover_coefficients(design: Sequence[Sequence[Exact]], observations: Sequence[Exact]) -> tuple[Fraction, ...]:
    """Unique exact recovery INSIDE the explicitly declared linear basis model."""
    a = matrix(design)
    if len(observations) != len(a):
        raise ValueError("Observation count mismatch")
    p = len(a[0])
    if rank(a) != p:
        raise ValueError("UNIDENTIFIABLE: design is not full column rank")
    reduced, pivots = rref([row + [q(y)] for row, y in zip(a, observations)])
    if p in pivots:
        raise ValueError("MODEL_MISMATCH: observations are outside the declared exact model")
    answer = [Fraction(0)] * p
    for row, col in zip(reduced, pivots):
        answer[col] = row[-1]
    return tuple(answer)


def polynomial_design(nodes: Sequence[Exact], degree: int) -> list[list[Fraction]]:
    if isinstance(degree, bool) or not isinstance(degree, int) or degree < 0:
        raise ValueError("degree must be a nonnegative integer")
    if not nodes:
        raise ValueError("No probe points")
    return [[q(x) ** j for j in range(degree + 1)] for x in nodes]


def finite_probe_witness(probes: Iterable[int]) -> tuple[int, dict[int, tuple[int, int]]]:
    """f(n)=n; g(n)=n up to N and n^2 after N. Both are monotone."""
    points = list(probes)
    if not points or any(isinstance(x, bool) or not isinstance(x, int) or x < 1 for x in points):
        raise ValueError("A nonempty finite set of positive integer probes is required")
    nmax = max(points)
    at = set(points) | {nmax + 1}
    return nmax, {n: (n, n if n <= nmax else n * n) for n in sorted(at)}


def anytime_hoeffding_radius(n: int, candidates: int, delta: float) -> float:
    """Elementary alpha-spending CS for [0,1] iid samples PER fixed candidate.

    Sum_{n>=1} delta/(K*n*(n+1)) = delta/K. This allows adaptive
    sample-count stopping, NOT adaptive modification of the candidate itself.
    Cross-candidate independence is not required. Returned arithmetic is numeric,
    not an exact rational certificate.
    """
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be positive")
    if isinstance(candidates, bool) or not isinstance(candidates, int) or candidates < 1:
        raise ValueError("candidates must be positive")
    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0,1)")
    return min(1.0, sqrt(log(2 * candidates * n * (n + 1) / delta) / (2 * n)))


def exhaustive_frontier_check() -> dict[str, int]:
    """All 3-world/3-action tables over {0,1,2}; epsilon 0,1/2,1,2."""
    tables = checks = failures = 0
    shared_optimum_despite_distinct_named_minimizers = 0
    for flat in product(range(3), repeat=9):
        c = [list(flat[0:3]), list(flat[3:6]), list(flat[6:9])]
        rho, _ = deterministic_minimax_regret(c)
        sets = epsilon_optimal_sets(c)
        if robust_candidates(c) and any(a != b for a in sets[0] for b in sets[1]):
            shared_optimum_despite_distinct_named_minimizers += 1
        for e in (0, Fraction(1, 2), 1, 2):
            checks += 1
            failures += bool(robust_candidates(c, e)) != (rho <= e)
        tables += 1
    return {"tables": tables, "equivalence_checks": checks, "failures": failures,
            "distinct_named_minimizers_with_common_optimum": shared_optimum_despite_distinct_named_minimizers}
