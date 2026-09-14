"""Unit tests for the Attention Sequence Theorem V1.

Covers:
  T1: Sparse routing dominance (algebraic and numeric)
  T2: Phase boundary computation and ecology prediction
  T3: Long-sequence crossover for growing-quotient obligations
  Edge cases and consistency checks
"""
from __future__ import annotations

from fractions import Fraction as F
import math
import unittest

from pathlib import Path
import importlib.util
import sys

path = Path(__file__).with_name("attention_witness.py")
spec = importlib.util.spec_from_file_location("attention_checked", str(path))
aw = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = aw
spec.loader.exec_module(aw)

from attention_witness import (
    full_routing_cost,
    sparse_routing_cost,
    sparse_wins,
    sparse_wins_condition,
    phase_boundary_lambda_star,
    sparse_dominates_at_lambda,
    growing_quotient_obligation_cost_fixed,
    growing_quotient_obligation_cost_recurrent,
    compute_crossover_N_star,
    sweep_cost_comparison,
    sweep_phase_boundary,
    sweep_crossover,
)


class TestT1SparseDominance(unittest.TestCase):
    """T1: Sparse routing beats full when K < M and L < C*(1 - K/M)."""

    def test_sparse_wins_basic(self):
        """K=2, M=8, C=1, L=0.25: 2+2=4 < 8*1=8."""
        self.assertTrue(sparse_wins(8, 2, F(1), F(1, 4)))

    def test_sparse_loses_when_K_equals_M(self):
        """K=M: both costs are M*C, so sparse does not strictly win."""
        self.assertFalse(sparse_wins(8, 8, F(1), F(1, 4)))

    def test_sparse_loses_when_L_too_high(self):
        """K=1, M=4, C=1, L=1: 1+4=5 > 4*1=4."""
        self.assertFalse(sparse_wins(4, 1, F(1), F(1)))

    def test_algebraic_matches_numeric(self):
        """Algebraic condition must agree with cost comparison everywhere."""
        for M in [4, 8, 16, 32]:
            for K in range(1, M + 1):
                C, L = F(1), F(1, 4)
                self.assertEqual(
                    sparse_wins(M, K, C, L),
                    sparse_wins_condition(K, M, C, L),
                    f"M={M}, K={K}",
                )

    def test_sparse_wins_boundary_K_equals_M_minus_1(self):
        """K=M-1: sparse wins iff L < C/M."""
        M = 10
        C, L = F(1), F(1, 20)  # L = 0.05 < 0.1 = C/M
        self.assertTrue(sparse_wins(M, M - 1, C, L))
        L2 = F(1, 5)  # L = 0.2 > 0.1 = C/M
        self.assertFalse(sparse_wins(M, M - 1, C, L2))

    def test_savings_grow_as_K_shrinks(self):
        """Fewer slots → larger savings from sparse routing."""
        M, C, L = 16, F(1), F(1, 8)
        savings = []
        for K in [1, 2, 4, 8]:
            s = full_routing_cost(M, C) - sparse_routing_cost(K, M, C, L)
            savings.append(float(s))
        for i in range(len(savings) - 1):
            self.assertGreater(savings[i], savings[i + 1])

    def test_fractional_costs(self):
        """Non-integer cost parameters."""
        C, L = F(3, 7), F(1, 11)
        M, K = 10, 3
        self.assertTrue(sparse_wins(M, K, C, L))

    def test_K_zero_not_valid(self):
        """K=0 means no attention at all; cost is M*L."""
        # sparse cost = 0*C + M*L = M*L; full cost = M*C
        # sparse wins iff M*L < M*C iff L < C
        self.assertTrue(sparse_wins(10, 0, F(2), F(1)))


class TestT2PhaseBoundary(unittest.TestCase):
    """T2: Phase boundary lambda* = log(M/K) / log(N/H)."""

    def test_lambda_star_zero_when_K_equals_M(self):
        """K=M: log(1)/log(N/H) = 0."""
        self.assertAlmostEqual(
            phase_boundary_lambda_star(10, 10, 1024, 8), 0.0
        )

    def test_lambda_star_grows_with_M_over_K(self):
        """Larger M/K ratio → higher lambda*."""
        lam_2 = phase_boundary_lambda_star(8, 2, 1024, 8)
        lam_4 = phase_boundary_lambda_star(16, 2, 1024, 8)
        self.assertGreater(lam_4, lam_2)

    def test_lambda_star_between_0_and_1(self):
        """For valid inputs, lambda* should be in (0, 1]."""
        lam = phase_boundary_lambda_star(16, 2, 1024, 8)
        self.assertGreater(lam, 0.0)
        self.assertLessEqual(lam, 1.0)

    def test_sparse_wins_at_perfect_locality(self):
        """lambda=1 (perfect locality): sparse/local always dominates."""
        for M, K in [(8, 2), (16, 4), (32, 8)]:
            self.assertTrue(
                sparse_dominates_at_lambda(M, K, 1024, 8, 1.0),
                f"M={M}, K={K}",
            )

    def test_sparse_dominance_consistent_with_lambda_star(self):
        """At lambda = lambda* + epsilon, sparse should dominate."""
        for M, K in [(8, 2), (16, 4), (32, 8)]:
            lam_star = phase_boundary_lambda_star(M, K, 1024, 8)
            if lam_star > 0 and lam_star < 1:
                lam_test = min(1.0, lam_star + 0.1)
                self.assertTrue(
                    sparse_dominates_at_lambda(M, K, 1024, 8, lam_test),
                    f"M={M}, K={K}, lambda={lam_test:.4f} >= lambda*={lam_star:.4f}",
                )

    def test_phase_boundary_independence_of_N(self):
        """lambda* should change when N changes (it depends on N/H)."""
        lam_n1 = phase_boundary_lambda_star(16, 4, 512, 8)
        lam_n2 = phase_boundary_lambda_star(16, 4, 1024, 8)
        self.assertNotAlmostEqual(lam_n1, lam_n2, places=6)


class TestT3LongSequenceCrossover(unittest.TestCase):
    """T3: Crossover N* for growing-quotient obligations."""

    def test_N_star_positive_finite(self):
        """For K > 1, N* should be positive and finite."""
        for K in [2, 4, 8]:
            n_star = compute_crossover_N_star(K, F(1), F(1, 4))
            self.assertGreater(n_star, 0)
            self.assertNotEqual(n_star, float("inf"))

    def test_recurrent_wins_beyond_crossover(self):
        """For N >> N*, recurrent cost should be lower than fixed cost."""
        for K in [2, 4]:
            n_star = compute_crossover_N_star(K, F(1), F(1, 4))
            N_check = int(n_star) + 5000
            c_fixed = growing_quotient_obligation_cost_fixed(K, N_check, F(1))
            c_recurrent = growing_quotient_obligation_cost_recurrent(
                N_check, F(1), F(1, 4)
            )
            self.assertLess(c_recurrent, c_fixed, f"K={K}, N={N_check}")

    def test_fixed_wins_at_small_N(self):
        """For very small N, fixed-carry should be competitive or cheaper."""
        # At N=4, K=8: fixed has plenty of slots, recurrent has 1 pointer
        c_fixed = growing_quotient_obligation_cost_fixed(8, 4, F(1))
        c_recurrent = growing_quotient_obligation_cost_recurrent(4, F(1), F(1, 4))
        # Fixed should be cheaper or comparable
        self.assertLessEqual(c_fixed, c_recurrent)

    def test_N_star_decreases_with_K(self):
        """More attention slots → lower crossover N* (fixed machine survives longer)."""
        n_star_2 = compute_crossover_N_star(2, F(1), F(1, 4))
        n_star_4 = compute_crossover_N_star(4, F(1), F(1, 4))
        self.assertGreater(n_star_2, n_star_4)

    def test_growing_quotient_cost_superlinear(self):
        """The obligation count should grow faster than linear."""
        c4 = growing_quotient_obligation_cost_fixed(4, 16, F(1))
        c8 = growing_quotient_obligation_cost_fixed(4, 32, F(1))
        # 32 has log2(32)=5, 16 has log2(16)=4, so ratio = 32*5/(16*4) = 2.5
        ratio = float(c8 / c4)
        self.assertGreater(ratio, 2.0)


class TestSweepConsistency(unittest.TestCase):
    """Sweep functions should produce consistent results."""

    def test_sweep_cost_algebraic_agreement(self):
        """Every cell in the sweep should have algebraic == numeric."""
        results = sweep_cost_comparison([4, 8, 16], [1, 2, 4])
        for r in results:
            self.assertTrue(
                r["algebraic_match"],
                f"M={r['M']}, K={r['K']}: mismatch",
            )

    def test_sweep_phase_boundary_range(self):
        """All lambda* values should be in [0, 1]."""
        results = sweep_phase_boundary([4, 8, 16, 32], [1, 2, 4, 8])
        for r in results:
            self.assertGreaterEqual(r["lambda_star"], 0.0)
            self.assertLessEqual(r["lambda_star"], 1.0)

    def test_sweep_crossover_non_empty(self):
        """Sweep should produce results for at least some K values."""
        results = sweep_crossover([1, 2, 4, 8, 16])
        self.assertGreater(len(results), 0)

    def test_sweep_4x4x4_cell_count(self):
        """The full (M, K, C/L) sweep should cover 4*4*2 = 32 base cells
        (with K < M filter reducing some)."""
        M_vals = [4, 8, 16, 32]
        K_vals = [1, 2, 4, 8]
        results = sweep_cost_comparison(M_vals, K_vals)
        # K < M filter: K=4 excluded from M=4, K=8 excluded from M=4 and M=8
        # Valid cells: 4*4=16 minus (K=4 at M=4: 1) minus (K=8 at M=4, M=8: 2) = 13
        # But K=1,2,4,8 for M=4: K=1,2 valid (K=4: K<M is False for M=4, so excluded)
        # M=4: K=1,2 → 2 cells; M=8: K=1,2,4 → 3; M=16: K=1,2,4,8 → 4; M=32: K=1,2,4,8 → 4
        # Total: 2+3+4+4 = 13
        self.assertEqual(len(results), 13)

    def test_witness_main_runs(self):
        """The main() function should run without error."""
        result = aw.main()
        self.assertGreater(result["t1"]["swept"], 0)
        self.assertGreater(result["t2"]["swept"], 0)
        self.assertGreater(result["t3"]["swept"], 0)


if __name__ == "__main__":
    unittest.main()
