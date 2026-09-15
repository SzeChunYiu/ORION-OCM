#!/usr/bin/env python3

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import unittest

from evolvability_kernel_v1 import (
    ADMISSIBILITY,
    CLAIM_CEILING,
    CURRENT_OBJECT,
    DEVELOPMENT_OBLIGATIONS,
    FROZEN_EXPECTED,
    KERNEL_PARAMETERS,
    STATES,
    UTILITIES,
    VERIFIER,
    ZERO_MASS_TERMINAL,
    build_kernels,
    build_receipt,
    direct_useful_mass,
    factorized_kernel,
    factorized_useful_mass,
    first_useful_mean,
    history_nonidentity,
    probability_multiset_signature,
    truth_table,
    zero_mass_hostile,
)

ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "RESULT_V1.json"


class EvolvabilityKernelTests(unittest.TestCase):
    def test_shared_present_contract_is_exactly_frozen(self) -> None:
        self.assertEqual(CURRENT_OBJECT, (0, 0, 0, 0, 0, 0))
        self.assertEqual(len(STATES), 64)
        self.assertEqual(len(set(STATES)), 64)
        self.assertEqual(ADMISSIBILITY, "ALL_64_DESCENDANTS_ADMISSIBLE")
        self.assertEqual(VERIFIER, "EXACT_FROZEN_UTILITY_MEMBERSHIP")

    def test_all_registered_kernels_normalize_exactly(self) -> None:
        kernels = build_kernels()
        self.assertEqual(set(kernels), {"CONTINUED", "RESET", "SHUFFLED_HISTORY"})
        for distribution in kernels.values():
            self.assertEqual(sum(distribution.values(), Fraction(0)), 1)
            self.assertEqual(len(distribution), 64)
            self.assertTrue(all(mass > 0 for mass in distribution.values()))

    def test_registered_frozen_mass_predictions_by_two_independent_routes(self) -> None:
        kernels = build_kernels()
        for utility_name, requirements in UTILITIES.items():
            for kernel_name, parameters in KERNEL_PARAMETERS.items():
                direct = direct_useful_mass(kernels[kernel_name], requirements)
                factorized = factorized_useful_mass(parameters, requirements)
                expected_mass, expected_mean = FROZEN_EXPECTED[utility_name][kernel_name]
                self.assertEqual(direct, factorized)
                self.assertEqual(direct, expected_mass)
                self.assertEqual(first_useful_mean(direct), expected_mean)

    def test_structured_unseen_composition_continued_wins(self) -> None:
        kernels = build_kernels()
        continued = direct_useful_mass(kernels["CONTINUED"], UTILITIES["U_AND"])
        reset = direct_useful_mass(kernels["RESET"], UTILITIES["U_AND"])
        shuffled = direct_useful_mass(kernels["SHUFFLED_HISTORY"], UTILITIES["U_AND"])
        self.assertEqual((continued, reset, shuffled), (Fraction(9,16), Fraction(1,4), Fraction(1,4)))
        self.assertGreater(continued, reset)

    def test_harmful_transfer_negative_twin_reset_wins(self) -> None:
        kernels = build_kernels()
        continued = direct_useful_mass(kernels["CONTINUED"], UTILITIES["U_ANTI"])
        reset = direct_useful_mass(kernels["RESET"], UTILITIES["U_ANTI"])
        shuffled = direct_useful_mass(kernels["SHUFFLED_HISTORY"], UTILITIES["U_ANTI"])
        self.assertEqual((continued, reset, shuffled), (Fraction(1,16), Fraction(1,4), Fraction(1,4)))
        self.assertLess(continued, reset)
        self.assertEqual(first_useful_mean(continued), 16)
        self.assertEqual(first_useful_mean(reset), 4)

    def test_semantic_remint_moves_advantage_to_coordinates_4_5(self) -> None:
        kernels = build_kernels()
        continued = direct_useful_mass(kernels["CONTINUED"], UTILITIES["U_45"])
        reset = direct_useful_mass(kernels["RESET"], UTILITIES["U_45"])
        shuffled = direct_useful_mass(kernels["SHUFFLED_HISTORY"], UTILITIES["U_45"])
        self.assertEqual((continued, reset, shuffled), (Fraction(1,4), Fraction(1,4), Fraction(9,16)))
        self.assertGreater(shuffled, continued)

    def test_continued_and_shuffled_have_identical_probability_multisets(self) -> None:
        kernels = build_kernels()
        continued = probability_multiset_signature(kernels["CONTINUED"])
        shuffled = probability_multiset_signature(kernels["SHUFFLED_HISTORY"])
        reset = probability_multiset_signature(kernels["RESET"])
        self.assertEqual(continued, shuffled)
        self.assertNotEqual(continued, reset)
        self.assertEqual(
            continued,
            (
                (Fraction(1,256), 16),
                (Fraction(3,256), 32),
                (Fraction(9,256), 16),
            ),
        )

    def test_history_tasks_are_extensionally_distinct_from_all_held_utilities(self) -> None:
        rows = history_nonidentity()
        for utility_name, row in rows.items():
            self.assertFalse(row["identical_to_D0"], utility_name)
            self.assertFalse(row["identical_to_D1"], utility_name)
        # Independent direct truth-table cross-check.
        for utility in UTILITIES.values():
            utable = truth_table(utility)
            for development in DEVELOPMENT_OBLIGATIONS.values():
                self.assertNotEqual(utable, truth_table(development))

    def test_zero_useful_mass_is_unreachable_not_finite(self) -> None:
        hostile = zero_mass_hostile()
        self.assertEqual(hostile["useful_mass"], "0")
        self.assertEqual(hostile["first_useful_mean"], ZERO_MASS_TERMINAL)
        self.assertEqual(first_useful_mean(Fraction(0)), ZERO_MASS_TERMINAL)

    def test_factorized_kernel_rejects_bad_parameters(self) -> None:
        with self.assertRaises(ValueError):
            factorized_kernel((Fraction(1,2),) * 5)
        with self.assertRaises(ValueError):
            factorized_kernel((Fraction(1,2),) * 5 + (Fraction(3,2),))
        with self.assertRaises(ValueError):
            factorized_kernel((Fraction(1,2),) * 5 + (Fraction(-1,2),))

    def test_geometric_mean_boundary_p_equals_one(self) -> None:
        self.assertEqual(first_useful_mean(Fraction(1)), 1)

    def test_geometric_mean_rejects_nonprobabilities(self) -> None:
        with self.assertRaises(ValueError):
            first_useful_mean(Fraction(-1,10))
        with self.assertRaises(ValueError):
            first_useful_mean(Fraction(11,10))

    def test_receipt_headlines(self) -> None:
        receipt = build_receipt()
        self.assertEqual(receipt["terminal"], CLAIM_CEILING)
        self.assertTrue(receipt["all_dual_methods_agree"])
        self.assertTrue(receipt["all_frozen_predictions_match"])
        self.assertTrue(receipt["continued_shuffled_probability_multisets_equal"])
        self.assertTrue(receipt["continued_entropy_equals_shuffled_by_exact_multiset_certificate"])
        self.assertFalse(receipt["continued_reset_probability_multisets_equal"])
        self.assertTrue(receipt["all_held_utilities_nonidentical_to_development_tasks"])
        self.assertTrue(receipt["harmful_transfer_twin"]["continued_better_on_U_AND"])
        self.assertTrue(receipt["harmful_transfer_twin"]["continued_worse_on_U_ANTI"])
        self.assertTrue(receipt["semantic_remint_control"]["shuffled_better_on_U_45"])

    def test_committed_receipt_is_exactly_reproducible(self) -> None:
        committed = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(build_receipt(), committed)

    def test_receipt_contains_no_float_values(self) -> None:
        def walk(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from walk(child)
            elif isinstance(value, list):
                for child in value:
                    yield from walk(child)
            else:
                yield value
        for value in walk(build_receipt()):
            self.assertNotIsInstance(value, float)


if __name__ == "__main__":
    unittest.main()
