"""Corrected exact witness for the bounded attention-sequence cost laws.

Historical V1 T2/T3 formulas were internally inconsistent.  This module is the
executable authority for Corrigendum V2:

T1  Conditional on both access schemes being exact/admissible,
    sparse cost K*C + M*L beats full cost M*C iff
    0 < K < M and L < C*(1-K/M).

T2  If locality lambda in [0,1] reduces a registered base lookup price L0 to
    L(lambda)=L0*(1-lambda), the exact cost boundary is
    lambda* = 1 - C*(1-K/M)/L0.
    Sparse wins strictly iff lambda > lambda* (subject to 0<K<M).

T3  For a growing target count M(N)=N*ceil(log2 N), compare
      fixed(K,N)      = M(N)*C/K
      recurrent(N)    = B + M(N)*L
    where B is an explicit one-time carry/build cost.  A finite strict crossover
    exists iff L < C/K, and N* is the least N with
      M(N)*(C/K-L) > B.

All acceptance decisions use integers/Fraction only.  No architecture-family
novelty is claimed; the model is a bounded lifecycle accounting microscope.
"""
from __future__ import annotations

from fractions import Fraction as F
from typing import Dict, Iterable, List, Optional
import itertools


def _positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _nonnegative_fraction(name: str, value: F) -> F:
    value = F(value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


# ---------------------------------------------------------------------------
# T1: full versus sparse cost after obligation/access sufficiency is established
# ---------------------------------------------------------------------------

def full_routing_cost(M: int, C: F) -> F:
    _positive_int("M", M)
    C = F(C)
    if C <= 0:
        raise ValueError("C must be positive")
    return M * C


def sparse_routing_cost(K: int, M: int, C: F, L: F) -> F:
    _positive_int("M", M)
    _positive_int("K", K)
    C = F(C)
    L = _nonnegative_fraction("L", L)
    if C <= 0:
        raise ValueError("C must be positive")
    return K * C + M * L


def sparse_wins(M: int, K: int, C: F, L: F) -> bool:
    """Strict sparse cost win, conditional on legal 0<K<M sparse access."""
    if isinstance(K, bool) or not isinstance(K, int) or K <= 0 or K >= M:
        return False
    return sparse_routing_cost(K, M, C, L) < full_routing_cost(M, C)


def sparse_wins_condition(K: int, M: int, C: F, L: F) -> bool:
    if not isinstance(M, int) or isinstance(M, bool) or M <= 0:
        raise ValueError("M must be a positive integer")
    if not isinstance(K, int) or isinstance(K, bool):
        raise ValueError("K must be an integer")
    C = F(C)
    L = _nonnegative_fraction("L", L)
    if C <= 0:
        raise ValueError("C must be positive")
    return 0 < K < M and L < C * F(M - K, M)


# ---------------------------------------------------------------------------
# T2: locality-induced lookup-price phase boundary
# ---------------------------------------------------------------------------

def locality_lookup_cost(lam: F, L_base: F) -> F:
    lam = F(lam)
    L_base = _nonnegative_fraction("L_base", L_base)
    if lam < 0 or lam > 1:
        raise ValueError("lambda must lie in [0,1]")
    return L_base * (1 - lam)


def phase_boundary_lambda_star(
    M: int,
    K: int,
    C: F = F(1),
    L_base: F = F(1, 2),
) -> Optional[F]:
    """Return the raw strict-cost threshold lambda*.

    ``None`` means there is no legal sparse regime (K<=0 or K>=M).  The raw
    threshold may lie below 0 (sparse wins for every legal lambda) or above 1
    (sparse never wins on lambda in [0,1]).
    """
    _positive_int("M", M)
    if not isinstance(K, int) or isinstance(K, bool) or K <= 0 or K >= M:
        return None
    C = F(C)
    L_base = F(L_base)
    if C <= 0 or L_base <= 0:
        raise ValueError("C and L_base must be positive")
    return F(1) - (C * F(M - K, M) / L_base)


def sparse_dominates_at_lambda(
    M: int,
    K: int,
    lam: F,
    C: F = F(1),
    L_base: F = F(1, 2),
) -> bool:
    if K <= 0 or K >= M:
        return False
    return sparse_wins(M, K, C, locality_lookup_cost(lam, L_base))


# ---------------------------------------------------------------------------
# T3: finite long-sequence crossover with explicit retained-state build cost
# ---------------------------------------------------------------------------

def growing_target_count(N: int) -> int:
    """Registered M(N)=N*ceil(log2 N), with one target per item at N=1."""
    _positive_int("N", N)
    ceil_log2 = max(1, (N - 1).bit_length())
    return N * ceil_log2


def growing_quotient_obligation_cost_fixed(K: int, N: int, C: F) -> F:
    _positive_int("K", K)
    C = F(C)
    if C <= 0:
        raise ValueError("C must be positive")
    return F(growing_target_count(N), K) * C


def growing_quotient_obligation_cost_recurrent(
    N: int,
    build_cost: F,
    lookup_cost: F,
) -> F:
    build_cost = _nonnegative_fraction("build_cost", build_cost)
    lookup_cost = _nonnegative_fraction("lookup_cost", lookup_cost)
    return build_cost + growing_target_count(N) * lookup_cost


def crossover_margin_per_target(K: int, C: F, lookup_cost: F) -> F:
    _positive_int("K", K)
    C = F(C)
    lookup_cost = _nonnegative_fraction("lookup_cost", lookup_cost)
    if C <= 0:
        raise ValueError("C must be positive")
    return C / K - lookup_cost


def compute_crossover_N_star(
    K: int,
    C: F,
    lookup_cost: F,
    build_cost: F,
    *,
    max_N: int = 1_000_000,
) -> Optional[int]:
    """Least N at which recurrent carry is strictly cheaper, else ``None``."""
    _positive_int("max_N", max_N)
    build_cost = _nonnegative_fraction("build_cost", build_cost)
    delta = crossover_margin_per_target(K, C, lookup_cost)
    if delta <= 0:
        return None
    for N in range(1, max_N + 1):
        if growing_target_count(N) * delta > build_cost:
            return N
    return None


# ---------------------------------------------------------------------------
# Exhaustive finite sweeps used by tests/receipt-style console output
# ---------------------------------------------------------------------------

def sweep_cost_comparison(
    M_values: Iterable[int],
    K_values: Iterable[int],
    C: F = F(1),
    L: F = F(1, 4),
) -> List[Dict]:
    rows: List[Dict] = []
    for M, K in itertools.product(M_values, K_values):
        legal = 0 < K < M
        full = full_routing_cost(M, C)
        sparse = sparse_routing_cost(K, M, C, L) if K > 0 else None
        numeric = legal and sparse is not None and sparse < full
        algebraic = sparse_wins_condition(K, M, C, L)
        rows.append({
            "M": M,
            "K": K,
            "legal": legal,
            "full_cost": full,
            "sparse_cost": sparse,
            "wins": numeric,
            "algebraic_match": numeric == algebraic,
        })
    return rows


def sweep_phase_boundary(
    M_values: Iterable[int],
    K_values: Iterable[int],
    C: F = F(1),
    L_base: F = F(1, 2),
) -> List[Dict]:
    rows: List[Dict] = []
    for M, K in itertools.product(M_values, K_values):
        threshold = phase_boundary_lambda_star(M, K, C, L_base)
        if threshold is None:
            continue
        probes = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
        rows.append({
            "M": M,
            "K": K,
            "lambda_star": threshold,
            "probes": tuple((lam, sparse_dominates_at_lambda(M, K, lam, C, L_base)) for lam in probes),
        })
    return rows


def sweep_crossover(
    K_values: Iterable[int],
    C: F = F(1),
    lookup_cost: F = F(1, 16),
    build_cost: F = F(16),
) -> List[Dict]:
    rows: List[Dict] = []
    for K in K_values:
        n_star = compute_crossover_N_star(K, C, lookup_cost, build_cost)
        if n_star is None:
            rows.append({"K": K, "N_star": None, "recurrent_wins_at_star": False})
            continue
        fixed = growing_quotient_obligation_cost_fixed(K, n_star, C)
        recurrent = growing_quotient_obligation_cost_recurrent(n_star, build_cost, lookup_cost)
        before = None
        if n_star > 1:
            before = (
                growing_quotient_obligation_cost_recurrent(n_star - 1, build_cost, lookup_cost)
                < growing_quotient_obligation_cost_fixed(K, n_star - 1, C)
            )
        rows.append({
            "K": K,
            "N_star": n_star,
            "fixed_cost": fixed,
            "recurrent_cost": recurrent,
            "recurrent_wins_at_star": recurrent < fixed,
            "recurrent_wins_before_star": before,
        })
    return rows


def main() -> Dict[str, object]:
    t1 = sweep_cost_comparison([4, 8, 16, 32], [1, 2, 4, 8])
    t2 = sweep_phase_boundary([4, 8, 16, 32], [1, 2, 4, 8])
    t3 = sweep_crossover([1, 2, 4, 8, 16])
    result = {
        "t1_cells": len(t1),
        "t1_all_algebraic": all(r["algebraic_match"] for r in t1),
        "t2_cells": len(t2),
        "t3": tuple((r["K"], r["N_star"]) for r in t3),
    }
    print(result)
    return result


if __name__ == "__main__":
    main()
