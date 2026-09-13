"""Exact development controls; protected scenarios belong to the frozen runner."""
from copy import deepcopy
from fractions import Fraction as F
import unittest

from neutral_machine import (encode, execute, objective, observable_property,
                             signature, verify_signature, verify_trace, weights)
from neutral_oracle import raw_fibers, raw_programs
from neutral_runner import check_prediction, deterministic_receipt
from neutral_search import enumerate_space, grammar_counts, minimize, verify_optimum


class TestNeutralSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.levels, cls.counters = enumerate_space(2, 4)
        cls.probabilities = weights(2, "1/2")
        cls.prices = ("1", "1/10", "1/4", "1/700")

    def test_raw_exhaustive_oracle_agrees_for_every_fiber_and_multiplicity(self):
        for size in range(1, 5):
            expected = raw_fibers(2, size)
            actual = {sig: f.multiplicity for sig, f in self.levels[size].items()}
            self.assertEqual(actual, dict(expected))
            self.assertEqual(len(raw_programs(2, size)), grammar_counts(2, 4)[size])

    def test_independent_interpreter_checks_every_development_representative(self):
        for size, level in enumerate(self.levels):
            for sig, fiber in level.items():
                self.assertEqual(signature(fiber.program, 2), sig)
                self.assertEqual(len(encode(fiber.program)), 7 * size)

    def test_every_truth_table_opcode_is_generated_and_parameter_is_charged(self):
        words = set()
        for table in range(16):
            program = ("b", table, ("r", 0), ("r", 1))
            word = encode(program)
            self.assertEqual(len(word), 21)
            words.add(word)
            self.assertIn(signature(program, 2), self.levels[3])
        self.assertEqual(len(words), 16)

    def test_duplicates_and_lazy_execution_are_actually_charged(self):
        duplicated = ("b", 8, ("r", 0), ("r", 0))
        self.assertTrue(all(row[1] == 2 for row in signature(duplicated, 2)))
        lazy = ("i", ("r", 0), ("r", 1), ("c", 0))
        sig = signature(lazy, 2)
        self.assertEqual([row[1] for row in sig], [1, 1, 2, 2])
        self.assertEqual(objective(sig, 4, self.probabilities, self.prices), F(179, 100))

    def test_exact_semantics_and_all_tied_property_fibers(self):
        prices = ("1", "1/10", "59/100", "1/700")
        cost, winners = minimize(self.levels, "0001", self.probabilities, prices)
        self.assertEqual(cost, F(213, 100))
        self.assertEqual({observable_property(s) for _, s, _ in winners},
                         {"EAGER", "CONDITIONAL"})
        self.assertEqual(len(winners), 3)
        verify_optimum(self.levels, "0001", self.probabilities, prices, cost, winners)

    def test_omitted_optimum_is_rejected_even_if_minimum_cost_stays_correct(self):
        cost, winners = minimize(self.levels, "0001", self.probabilities, self.prices)
        self.assertGreater(len(winners), 1)
        with self.assertRaises(ValueError):
            verify_optimum(self.levels, "0001", self.probabilities,
                           self.prices, cost, winners[1:])

    def test_tampered_trace_and_signature_are_rejected(self):
        program = ("b", 8, ("r", 0), ("r", 1))
        output, events = execute(program, (1, 1))
        verify_trace(program, (1, 1), output, events)
        with self.assertRaises(ValueError):
            verify_trace(program, (1, 1), output, events[1:])
        sig = signature(program, 2)
        damaged = list(sig)
        damaged[0] = (sig[0][0], 0, *sig[0][2:])
        with self.assertRaises(ValueError):
            verify_signature(program, 2, tuple(damaged))

    def test_wrong_cost_and_property_predictions_are_rejected(self):
        case = {"minimum": "179/100", "properties": ["CONDITIONAL"]}
        check_prediction(case, F(179, 100), ["CONDITIONAL"])
        bad = deepcopy(case)
        bad["minimum"] = "1"
        with self.assertRaises(ValueError):
            check_prediction(bad, F(179, 100), ["CONDITIONAL"])
        with self.assertRaises(ValueError):
            check_prediction(case, F(179, 100), ["EAGER"])

    def test_parity_transcripts_read_every_relevant_input(self):
        for level in self.levels:
            for sig in level:
                if tuple(row[0] for row in sig) == (0, 1, 1, 0):
                    self.assertTrue(all(row[4] == 3 and row[1] >= 2 for row in sig))

    def test_missing_function_is_distinct_from_prediction_failure(self):
        with self.assertRaisesRegex(ValueError, "INCONCLUSIVE_GRAMMAR"):
            minimize(self.levels[:2], "0001", self.probabilities, self.prices)

    def test_resource_count_recurrence_detects_missing_grammar_terms(self):
        self.assertEqual(self.counters["raw_terms_by_size"], [0, 4, 0, 256, 64])
        self.assertGreater(self.counters["compositions"], 0)
        self.assertEqual(self.counters["signature_cells"],
                         4 * self.counters["compositions"])

    def test_forged_multiplicity_representative_and_duplicate_are_rejected(self):
        cost, winners = minimize(self.levels, "0001", self.probabilities, self.prices)
        for field in ("multiplicity", "program", "duplicate"):
            damaged = deepcopy(winners)
            if field == "multiplicity":
                damaged[0][2].multiplicity += 1
            elif field == "program":
                damaged[0][2].program = ("c", 0)
            else:
                damaged.append(damaged[0])
            with self.assertRaises(ValueError):
                verify_optimum(self.levels, "0001", self.probabilities,
                               self.prices, cost, damaged)

    def test_deterministic_projection_removes_only_named_instrumentation(self):
        receipt = {"ranking_and_certificate_seconds": 1,
                   "searches": [{"enumeration_seconds": 2,
                                 "process_peak_resident_kib_linux": 3,
                                 "compositions": 4}], "cases": ["untouched"]}
        self.assertEqual(deterministic_receipt(receipt),
                         {"searches": [{"compositions": 4}], "cases": ["untouched"]})
        self.assertIn("ranking_and_certificate_seconds", receipt)


if __name__ == "__main__":
    unittest.main()
