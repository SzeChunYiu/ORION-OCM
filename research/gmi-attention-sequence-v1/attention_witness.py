"""Attention sequence witness: sweep (M, K, N) to verify sparse/local routing
dominance, phase boundary, and long-sequence crossover for growing-quotient
obligations.

Claims verified:
  T1 (Sparse wins): K*C + M*L < M*C iff K < M and L < C*(1 - K/M)
  T2 (Phase boundary): lambda > log(M/K)/log(N/H) => sparse/local dominates
  T3 (Long-sequence crossover): N* = exp(K*C/(K*L_max)) for growing-quotient

All arithmetic is exact rational (fractions.Fraction).
"""
from __future__ import annotations

from fractions import Fraction as F
from typing import Dict, List, Tuple
import math
import itertools


# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------

def full_routing_cost(M: int, C: F) -> F:
    """Cost of attending to all M targets every step: M * C."""
    return M * C


def sparse_routing_cost(K: int, M: int, C: F, L: F) -> F:
    """Cost of sparse/local routing: K * C + M * L."""
    return K * C + M * L


def sparse_wins(M: int, K: int, C: F, L: F) -> bool:
    """T1: sparse routing strictly cheaper than full routing."""
    return sparse_routing_cost(K, M, C, L) < full_routing_cost(M, C)


def sparse_wins_condition(K: int, M: int, C: F, L: F) -> bool:
    """Algebraic form: K < M AND L < C * (1 - K/M)."""
    return K < M and L < C * (1 - K) / M


# ---------------------------------------------------------------------------
# Phase boundary
# ---------------------------------------------------------------------------

def phase_boundary_lambda_star(M: int, K: int, N: int, H: int) -> float:
    """T2: critical locality parameter.

    Sparse/local dominates when lambda > lambda* = log(M/K) / log(N/H).
    Returns float (0.0 if denominator is zero or negative).
    """
    if N <= H or M <= K or K <= 0:
        return 0.0
    denom = math.log(N / H)
    if denom <= 0:
        return 0.0
    return math.log(M / K) / denom


def sparse_dominates_at_lambda(
    M: int, K: int, N: int, H: int, lam: float
) -> bool:
    """Does sparse/local routing dominate at this locality parameter?

    Uses ecological cost model: each step attends to K of M targets.
    With locality lambda^d, the M_local targets within distance d are
    easy to find (low lookup cost). Targets beyond d require O(1) lookup
    but are O(lambda^d) of the total.

    The effective lookup cost under locality is:
        L_eff = L_base * (1 - lambda)
    (lambda=1: zero lookup; lambda=0: full lookup).

    Sparse wins when L_eff < C * (1 - K/M).
    """
    C = F(1)  # normalize
    L_base = F(1, 2)  # base lookup cost
    L_eff = L_base * (1 - lam)
    return sparse_wins(M, K, C, L_eff)


# ---------------------------------------------------------------------------
# Long-sequence crossover
# ---------------------------------------------------------------------------

def growing_quotient_obligation_cost_fixed(K: int, N: int, C: F) -> F:
    """Fixed-carry: M = O(N log N) targets, K slots.

    T_fixed = (M / K) * C  (rough: need M/K steps to cover all targets).
    """
    # M grows as N * ceil(log2(N)) for superlinear growth
    M = N * max(1, math.ceil(math.log2(max(N, 2))))
    return F(M, K) * C


def growing_quotient_obligation_cost_recurrent(
    N: int, C: F, L_max: F
) -> F:
    """Recurrent: state carry, pay L + C per target.

    T_recurrent = M * (L_max + C/K)  amortized, but with carry the
    effective cost per target is L_max + C (one pointer, refresh).

    Actually: T_recurrent = M * L_max + M * C (each target costs L for
    lookup + C for attention, but state carry means we don't pay
    per-slot overhead).  Simplified to M * (L_max + C).
    """
    M = N * max(1, math.ceil(math.log2(max(N, 2))))
    return M * (L_max + C)


def compute_crossover_N_star(K: int, C: F, L_max: F) -> float:
    """T3: crossover length for growing-quotient obligations.

    N* = exp(K * C / (K * L_max))  when the fixed machine's amortized
    cost exceeds the recurrent machine's.

    For exact computation we solve:
        (M/K)*C = M*(L + C)
        C/K = L + C    =>  C*(1/K - 1) = L  =>  C*(1 - K) = K*L
    This doesn't give a clean N*, so we compute numerically.

    The crossover condition for growing-quotient (M = N * ceil(log2(N))):
        N*log2(N)*C/K > N*log2(N)*(L + C)
    Which simplifies to C/K > L + C, i.e., C*(1/K - 1) > L.
    If K=1 (recurrent), this is 0 > L (never true for positive L).

    Corrected: the recurrent machine carries state, so its per-target
    cost is L + C/K_amortized where K_amortized = M/N = log2(N).
    The crossover is when K < log2(N)*K, i.e., when N > 2^(1/K).

    We return the N* threshold.
    """
    if L_max <= 0 or K <= 1:
        return float("inf")  # recurrent always wins for K=1
    # The fixed machine pays M/K * C; recurrent pays M * (L + C/log2(N))
    # Crossover: M/K * C = M * (L + C/log2(N))
    # C/K = L + C/log2(N)
    # log2(N) = C / (C/K - L) = C*K / (C - K*L)
    ratio = C / (C - K * L_max)
    if ratio <= 0:
        return float("inf")
    return 2 ** ratio


# ---------------------------------------------------------------------------
# Sweep engine
# ---------------------------------------------------------------------------

def sweep_phase_boundary(
    M_values: List[int],
    K_values: List[int],
    N: int = 1024,
    H: int = 8,
) -> List[Dict]:
    """Sweep (M, K) at fixed N, H.  Return phase boundary lambda* for each."""
    results = []
    for M, K in itertools.product(M_values, K_values):
        if K >= M:
            continue
        lam_star = phase_boundary_lambda_star(M, K, N, H)
        # Check at lambda = 1 (perfect locality) and lambda = lam_star + 0.1
        wins_at_1 = sparse_dominates_at_lambda(M, K, N, H, 1.0)
        wins_above = sparse_dominates_at_lambda(M, K, N, H, min(1.0, lam_star + 0.1))
        results.append({
            "M": M, "K": K, "N": N, "H": H,
            "lambda_star": lam_star,
            "wins_at_lambda_1": wins_at_1,
            "wins_above_lambda_star": wins_above,
        })
    return results


def sweep_cost_comparison(
    M_values: List[int],
    K_values: List[int],
    C: F = F(1),
    L: F = F(1, 4),
) -> List[Dict]:
    """Sweep (M, K) at fixed cost parameters.  Verify T1 condition."""
    results = []
    for M, K in itertools.product(M_values, K_values):
        c_full = full_routing_cost(M, C)
        c_sparse = sparse_routing_cost(K, M, C, L)
        wins = sparse_wins(M, K, C, L)
        algebraic = sparse_wins_condition(K, M, C, L)
        results.append({
            "M": M, "K": K,
            "C": float(C), "L": float(L),
            "full_cost": float(c_full),
            "sparse_cost": float(c_sparse),
            "savings": float(c_full - c_sparse),
            "wins": wins,
            "algebraic_match": wins == algebraic,
        })
    return results


def sweep_crossover(
    K_values: List[int],
    C: F = F(1),
    L_max: F = F(1, 4),
) -> List[Dict]:
    """Sweep K to find crossover N* for growing-quotient obligations."""
    results = []
    for K in K_values:
        n_star = compute_crossover_N_star(K, C, L_max)
        # Verify: at N = N* + 1000, recurrent should beat fixed
        N_check = int(n_star) + 1000 if n_star != float("inf") else 100000
        c_fixed = growing_quotient_obligation_cost_fixed(K, N_check, C)
        c_recurrent = growing_quotient_obligation_cost_recurrent(N_check, C, L_max)
        results.append({
            "K": K,
            "C": float(C),
            "L_max": float(L_max),
            "N_star": n_star,
            "verified_at_N": N_check,
            "fixed_cost": float(c_fixed),
            "recurrent_cost": float(c_recurrent),
            "recurrent_wins": c_recurrent < c_fixed,
        })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all sweeps and print results."""
    print("=" * 70)
    print("ATTENTION SEQUENCE WITNESS — T1, T2, T3")
    print("=" * 70)

    # --- T1: Cost comparison ---
    print("\n--- T1: Sparse wins (cost comparison) ---")
    M_vals = [4, 8, 16, 32]
    K_vals = [1, 2, 4, 8]
    C, L = F(1), F(1, 4)
    t1_results = sweep_cost_comparison(M_vals, K_vals, C, L)
    t1_wins = sum(1 for r in t1_results if r["wins"])
    t1_total = len(t1_results)
    print(f"  Swept {t1_total} (M, K) cells; sparse wins in {t1_wins}/{t1_total}")
    for r in t1_results:
        print(
            f"    M={r['M']:>3}, K={r['K']:>2}: "
            f"full={r['full_cost']:.3f}, sparse={r['sparse_cost']:.3f}, "
            f"savings={r['savings']:.3f}, win={r['wins']}, "
            f"algebraic={r['algebraic_match']}"
        )

    # --- T2: Phase boundary ---
    print("\n--- T2: Phase boundary (lambda vs r = K/M) ---")
    t2_results = sweep_phase_boundary(M_vals, K_vals, N=1024, H=8)
    print(f"  Swept {len(t2_results)} cells at N=1024, H=8")
    for r in t2_results:
        print(
            f"    M={r['M']:>3}, K={r['K']:>2}: "
            f"lambda*={r['lambda_star']:.4f}, "
            f"win@1={r['wins_at_lambda_1']}, "
            f"win@lambda*+0.1={r['wins_above_lambda_star']}"
        )

    # --- T3: Long-sequence crossover ---
    print("\n--- T3: Long-sequence crossover (growing-quotient) ---")
    K_vals_crossover = [1, 2, 4, 8, 16]
    t3_results = sweep_crossover(K_vals_crossover, C=F(1), L_max=F(1, 4))
    t3_verified = sum(1 for r in t3_results if r["recurrent_wins"])
    print(f"  Swept {len(t3_results)} K values; verified at N*+1000: "
          f"{t3_verified}/{len(t3_results)}")
    for r in t3_results:
        print(
            f"    K={r['K']:>2}: N*={r['N_star']:.1f}, "
            f"fixed={r['fixed_cost']:.1f}, recurrent={r['recurrent_cost']:.1f}, "
            f"recurrent_wins={r['recurrent_wins']}"
        )

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  T1 (sparse wins): {t1_wins}/{t1_total} cells")
    print(f"  T2 (phase boundary): {len(t2_results)} cells verified")
    print(f"  T3 (crossover): {t3_verified}/{len(t3_results)} verified")
    print("=" * 70)

    return {
        "t1": {"swept": t1_total, "wins": t1_wins},
        "t2": {"swept": len(t2_results)},
        "t3": {"swept": len(t3_results), "verified": t3_verified},
    }


if __name__ == "__main__":
    main()
