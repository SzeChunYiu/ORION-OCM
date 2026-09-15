"""Hostile/unit controls for Attention Sequence Corrigendum V2."""
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).with_name("attention_witness.py")
spec = importlib.util.spec_from_file_location("attention_checked", str(path))
aw = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = aw
spec.loader.exec_module(aw)


class TestT1SparseCost(unittest.TestCase):
    def test_exact_iff_over_grid(self):
        for M in (2, 4, 8, 16):
            for K in range(0, M + 3):
                for L in (F(0), F(1, 16), F(1, 4), F(1, 2), F(1)):
                    numeric = False
                    if 0 < K < M:
                        numeric = aw.sparse_routing_cost(K, M, F(1), L) < aw.full_routing_cost(M, F(1))
                    self.assertEqual(numeric, aw.sparse_wins_condition(K, M, F(1), L))
                    self.assertEqual(numeric, aw.sparse_wins(M, K, F(1), L))

    def test_zero_slots_are_not_a_solution(self):
        self.assertFalse(aw.sparse_wins(8, 0, F(1), F(0)))
        self.assertFalse(aw.sparse_wins_condition(0, 8, F(1), F(0)))

    def test_full_slot_sparse_scheme_pays_lookup_and_does_not_win(self):
        self.assertEqual(aw.full_routing_cost(8, F(1)), F(8))
        self.assertEqual(aw.sparse_routing_cost(8, 8, F(1), F(1, 4)), F(10))
        self.assertFalse(aw.sparse_wins(8, 8, F(1), F(1, 4)))

    def test_strict_boundary_is_tie(self):
        # K=6,M=8 => C(1-K/M)=1/4.
        self.assertFalse(aw.sparse_wins(8, 6, F(1), F(1, 4)))
        self.assertTrue(aw.sparse_wins(8, 6, F(1), F(1, 8)))


class TestT2LocalityBoundary(unittest.TestCase):
    def test_boundary_derived_from_same_cost_model(self):
        # M=8,K=6,C=1,L0=1/2 => lambda*=1/2.
        star = aw.phase_boundary_lambda_star(8, 6, F(1), F(1, 2))
        self.assertEqual(star, F(1, 2))
        self.assertFalse(aw.sparse_dominates_at_lambda(8, 6, F(1, 2), F(1), F(1, 2)))
        self.assertTrue(aw.sparse_dominates_at_lambda(8, 6, F(3, 4), F(1), F(1, 2)))

    def test_negative_raw_threshold_means_all_legal_lambda_win(self):
        # M=8,K=2: cost saving is already larger than worst registered lookup cost.
        star = aw.phase_boundary_lambda_star(8, 2, F(1), F(1, 2))
        self.assertEqual(star, F(-1, 2))
        for lam in (F(0), F(1, 4), F(1)):
            self.assertTrue(aw.sparse_dominates_at_lambda(8, 2, lam, F(1), F(1, 2)))

    def test_high_threshold_has_both_sides(self):
        # M=8,K=7 => lambda*=3/4.
        self.assertEqual(aw.phase_boundary_lambda_star(8, 7, F(1), F(1, 2)), F(3, 4))
        self.assertFalse(aw.sparse_dominates_at_lambda(8, 7, F(3, 4), F(1), F(1, 2)))
        self.assertTrue(aw.sparse_dominates_at_lambda(8, 7, F(7, 8), F(1), F(1, 2)))

    def test_illegal_sparse_regime_has_no_boundary(self):
        self.assertIsNone(aw.phase_boundary_lambda_star(8, 0))
        self.assertIsNone(aw.phase_boundary_lambda_star(8, 8))
        self.assertFalse(aw.sparse_dominates_at_lambda(8, 8, F(1)))

    def test_locality_cost_endpoints(self):
        self.assertEqual(aw.locality_lookup_cost(F(0), F(3, 5)), F(3, 5))
        self.assertEqual(aw.locality_lookup_cost(F(1), F(3, 5)), F(0))
        with self.assertRaises(ValueError):
            aw.locality_lookup_cost(F(5, 4), F(1, 2))


class TestT3GrowingCrossover(unittest.TestCase):
    C = F(1)
    L = F(1, 16)
    B = F(16)

    def test_registered_target_count(self):
        expected = {1: 1, 2: 2, 3: 6, 4: 8, 5: 15, 8: 24, 16: 64, 32: 160}
        self.assertEqual({n: aw.growing_target_count(n) for n in expected}, expected)

    def test_exact_registered_crossovers(self):
        self.assertEqual(
            {K: aw.compute_crossover_N_star(K, self.C, self.L, self.B) for K in (1, 2, 4, 8, 16)},
            {1: 6, 2: 10, 4: 18, 8: 43, 16: None},
        )

    def test_minimality_and_strictness(self):
        for K, star in ((1, 6), (2, 10), (4, 18), (8, 43)):
            at_fixed = aw.growing_quotient_obligation_cost_fixed(K, star, self.C)
            at_rec = aw.growing_quotient_obligation_cost_recurrent(star, self.B, self.L)
            self.assertLess(at_rec, at_fixed)
            if star > 1:
                before_fixed = aw.growing_quotient_obligation_cost_fixed(K, star - 1, self.C)
                before_rec = aw.growing_quotient_obligation_cost_recurrent(star - 1, self.B, self.L)
                self.assertGreaterEqual(before_rec, before_fixed)

    def test_no_crossover_when_recurrent_marginal_cost_not_lower(self):
        self.assertEqual(aw.crossover_margin_per_target(16, self.C, self.L), F(0))
        self.assertIsNone(aw.compute_crossover_N_star(16, self.C, self.L, self.B))
        self.assertIsNone(aw.compute_crossover_N_star(32, self.C, self.L, self.B))

    def test_more_fixed_slots_move_crossover_later(self):
        stars = [aw.compute_crossover_N_star(K, self.C, self.L, self.B) for K in (1, 2, 4, 8)]
        self.assertEqual(stars, sorted(stars))
        self.assertEqual(len(set(stars)), len(stars))

    def test_build_cost_moves_crossover_later(self):
        small = aw.compute_crossover_N_star(4, self.C, self.L, F(4))
        large = aw.compute_crossover_N_star(4, self.C, self.L, F(32))
        self.assertIsNotNone(small)
        self.assertIsNotNone(large)
        self.assertLess(small, large)


class TestSweepsAndHostileInputs(unittest.TestCase):
    def test_t1_sweep_agrees_everywhere(self):
        rows = aw.sweep_cost_comparison([4, 8, 16, 32], [1, 2, 4, 8])
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r["algebraic_match"] for r in rows))

    def test_t2_sweep_uses_exact_fractions(self):
        rows = aw.sweep_phase_boundary([8], [2, 6, 7])
        self.assertEqual([r["lambda_star"] for r in rows], [F(-1, 2), F(1, 2), F(3, 4)])

    def test_t3_sweep_pins_no_crossover_terminal(self):
        rows = aw.sweep_crossover([1, 2, 4, 8, 16])
        self.assertEqual([(r["K"], r["N_star"]) for r in rows], [(1, 6), (2, 10), (4, 18), (8, 43), (16, None)])
        self.assertTrue(all(r["recurrent_wins_at_star"] for r in rows[:-1]))
        self.assertFalse(rows[-1]["recurrent_wins_at_star"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            aw.full_routing_cost(0, F(1))
        with self.assertRaises(ValueError):
            aw.growing_target_count(0)
        with self.assertRaises(ValueError):
            aw.compute_crossover_N_star(0, F(1), F(1, 16), F(16))
        with self.assertRaises(ValueError):
            aw.compute_crossover_N_star(4, F(0), F(1, 16), F(16))

    def test_main_runs(self):
        result = aw.main()
        self.assertTrue(result["t1_all_algebraic"])
        self.assertEqual(result["t3"], ((1, 6), (2, 10), (4, 18), (8, 43), (16, None)))


if __name__ == "__main__":
    unittest.main()
