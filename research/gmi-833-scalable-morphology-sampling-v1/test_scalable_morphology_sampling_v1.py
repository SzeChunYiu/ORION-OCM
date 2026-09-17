#!/usr/bin/env python3
"""Deterministic tests for scalable morphology probability sampling."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from math import comb
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("gmi833_scalable_sampling_tests", "scalable_morphology_sampling_v1.py")
O = _load("gmi833_scalable_sampling_oracle_tests", "independent_sampling_oracle_v1.py")


class RankUnrankTests(unittest.TestCase):
    def test_instruction_digit_bijection_matches_parent_order(self):
        for labels, registers in ((1, 1), (2, 1), (3, 2), (5, 4)):
            options = S.PARENT.instruction_options(labels, registers)
            self.assertEqual(len(options), S.instruction_alphabet_size(labels, registers))
            for digit, instruction in enumerate(options):
                self.assertEqual(S.instruction_to_digit(instruction, labels, registers), digit)
                self.assertEqual(S.digit_to_instruction(digit, labels, registers), instruction)

    def test_exact_small_enumerator_order_and_bijection(self):
        for code_cells, register_cells in ((1, 1), (2, 1), (1, 2), (2, 2)):
            budget = S.StructuralBudget(code_cells, register_cells)
            candidates = S.PARENT.enumerate_candidates(budget)
            self.assertEqual(S.population_size(budget), len(candidates))
            self.assertEqual(S.population_size(budget), S.PARENT.candidate_count(budget))
            for rank, expected in enumerate(candidates):
                self.assertEqual(S.unrank_program(budget, rank), expected)
                self.assertEqual(S.rank_program(budget, expected), rank)

    def test_large_budget_boundary_and_probe_round_trips(self):
        budget = S.StructuralBudget(64, 32)
        total = S.population_size(budget)
        self.assertEqual(len(S.strata(budget)), 2048)
        self.assertEqual(len(str(total)), 329)
        self.assertEqual(total.bit_length(), 1093)
        for rank in (0, 1, total // 3, total // 2, total - 2, total - 1):
            self.assertEqual(S.rank_program(budget, S.unrank_program(budget, rank)), rank)

    def test_rank_hostiles_fail_closed(self):
        budget = S.StructuralBudget(2, 1)
        with self.assertRaises(ValueError):
            S.unrank_program(budget, -1)
        with self.assertRaises(ValueError):
            S.unrank_program(budget, S.population_size(budget))
        with self.assertRaises(ValueError):
            S.digit_to_instruction(S.instruction_alphabet_size(2, 1), 2, 1)
        outside = S.CandidateProgram(2, (S.Instruction("HALT"),))
        with self.assertRaises(ValueError):
            S.rank_program(budget, outside)


class ProbabilityDesignTests(unittest.TestCase):
    def test_independent_exhaustive_floyd_oracle_is_uniform(self):
        counts = O.exhaustive_floyd_counts(5, 2)
        self.assertEqual(len(counts), comb(5, 2))
        self.assertEqual(sum(counts.values()), 20)
        self.assertEqual(set(counts.values()), {2})

    def test_implementation_matches_every_small_draw_trace(self):
        for first in range(4):
            for second in range(5):
                source = S.FiniteDrawSource((first, second))
                observed = S.floyd_srswor(5, 2, source.uniform_below)
                chosen: set[int] = set()
                for upper, draw in ((3, first), (4, second)):
                    chosen.add(upper if draw in chosen else draw)
                self.assertEqual(observed, tuple(sorted(chosen)))

    def test_global_probabilities_and_exact_hit_miss(self):
        self.assertEqual(
            S.global_inclusion_probabilities(5, 2),
            (Fraction(2, 5), Fraction(1, 10)),
        )
        self.assertEqual(S.miss_probability(5, 1, 2), Fraction(3, 5))
        self.assertEqual(S.miss_probability(5, 4, 2), Fraction(0, 1))
        self.assertEqual(S.miss_probability(5, 0, 2), Fraction(1, 1))
        self.assertEqual(
            S.global_design_terms(5, 2),
            (Fraction(2, 5), Fraction(1, 10), Fraction(5, 2)),
        )

    def test_stratified_hit_miss_formula_is_exact(self):
        # One qualifying member in each of two strata; direct factorization.
        self.assertEqual(
            S.stratified_miss_probability((3, 4), (1, 1), (1, 2)),
            Fraction(2, 3) * Fraction(comb(3, 2), comb(4, 2)),
        )
        self.assertEqual(S.stratified_miss_probability((3,), (3,), (1,)), Fraction(0, 1))
        for args in (
            ((3,), (4,), (1,)),
            ((3,), (1,), (4,)),
            ((3,), (1, 2), (1,)),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                S.stratified_miss_probability(*args)

    def test_positive_hamilton_allocation(self):
        self.assertEqual(S.hamilton_positive_allocation((2, 3), 2), (1, 1))
        self.assertEqual(S.hamilton_positive_allocation((2, 3), 4), (2, 2))
        self.assertEqual(S.hamilton_positive_allocation((2, 3), 5), (2, 3))
        with self.assertRaises(ValueError):
            S.hamilton_positive_allocation((2, 3), 1)

    def test_registered_stratified_replay(self):
        budget = S.StructuralBudget(64, 32)
        entropy = S.CounterEntropy(b"gmi-833-f-scalable-sampling-v1-registered-replay")
        sample = S.positive_stratified_srswor(budget, 4096, entropy.uniform_below)
        self.assertEqual(len(sample.ranks), 4096)
        self.assertEqual(len(set(sample.ranks)), 4096)
        self.assertEqual(len(sample.allocation), 2048)
        self.assertEqual(min(sample.allocation), 1)
        self.assertEqual(sum(sample.allocation), 4096)
        for rank in sample.ranks:
            self.assertEqual(S.rank_program(budget, S.unrank_program(budget, rank)), rank)

    def test_sampler_and_entropy_hostiles_fail_closed(self):
        with self.assertRaises(ValueError):
            S.floyd_srswor(2, 3, lambda upper: 0)
        with self.assertRaises(ValueError):
            S.floyd_srswor(True, 1, lambda upper: 0)
        with self.assertRaises(ValueError):
            S.floyd_srswor(3, 1, lambda upper: upper)
        source = S.FiniteDrawSource(())
        with self.assertRaises(RuntimeError):
            S.floyd_srswor(3, 1, source.uniform_below)
        with self.assertRaises(ValueError):
            S.CounterEntropy(b"")
        self.assertTrue(all(S.hostile_input_audit().values()))


class ReceiptTests(unittest.TestCase):
    def test_manifest_and_reconciliation_are_single_row_and_complete(self):
        manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
        reconciliation = json.loads(
            (HERE / "ISSUE_833_RECONCILIATION_SCALABLE_MORPHOLOGY_SAMPLING_V1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["target_rows"], 1)
        self.assertEqual(len(reconciliation["replacements"]), 1)
        self.assertEqual(
            reconciliation["replacements"][0]["old"],
            "- [ ] Implement scalable sampling for large budgets.",
        )
        self.assertIn("PR #1003 / #1002", reconciliation["replacements"][0]["new"])
        self.assertTrue(
            all((HERE / artifact).is_file() for artifact in manifest["artifacts"])
        )
        self.assertEqual(manifest["adjacent_rows_left_open"], [
            "Generate at least 10^6 architecture-neutral candidates.",
            "Scale to at least 10^8 candidates or justify an equivalent effective coverage method.",
        ])

    def test_result_receipt_is_byte_stable(self):
        expected = (HERE / "RESULT_V1.json").read_bytes()
        self.assertEqual(S.canonical_result_bytes(), expected)
        payload = json.loads(expected)
        self.assertFalse(payload["registered_large_budget"]["population_materialized"])
        self.assertEqual(payload["registered_stratified_replay"]["covered_strata"], 2048)
        self.assertTrue(payload["coverage_diagnostics"]["all_strata_guaranteed_represented"])
        self.assertFalse(payload["coverage_diagnostics"]["global_design_guarantees_every_stratum"])
        self.assertTrue(all(payload["hostile_input_checks"].values()))
        self.assertEqual(payload["resource_bounds"]["registered_stratum_table_entries"], 2048)
        self.assertEqual(payload["adjacent_issue_833_rows_left_open"], [
            "Generate at least 10^6 architecture-neutral candidates.",
            "Scale to at least 10^8 candidates or justify an equivalent effective coverage method.",
        ])

    def test_claim_boundary_is_explicit(self):
        self.assertIn("MILLION_SCALE_GENERATION_EXECUTED", S.FORBIDDEN_PROMOTIONS)
        self.assertIn("HUNDRED_MILLION_SCALE_GENERATION_EXECUTED", S.FORBIDDEN_PROMOTIONS)
        self.assertIn("PHYSICAL_RANDOMNESS_FROM_FIXED_SEED", S.FORBIDDEN_PROMOTIONS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
