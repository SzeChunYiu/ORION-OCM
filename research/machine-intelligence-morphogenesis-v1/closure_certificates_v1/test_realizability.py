from fractions import Fraction
from itertools import product
import unittest
from realizability_checks import (ExactBitMemory, exact_recall_requirement,
                                 parity_compression_collision, witness_comparison)


class RealizabilityTests(unittest.TestCase):
    def test_recall_lower_bound(self):
        for records in (0, 1, 2, 8, 128, 1024):
            self.assertEqual(exact_recall_requirement(records, 8)["minimum_dataset_dependent_bits"], 8*records)

    def test_bad_record_count_rejected(self):
        for records in (-1, True, 1.5):
            with self.assertRaises(ValueError): exact_recall_requirement(records)

    def test_one_bit_compression_collision(self):
        for records in (2, 3, 4, 8):
            r = parity_compression_collision(records)
            a, b, i = r["dataset_a"], r["dataset_b"], r["separating_query_index"]
            self.assertNotEqual(a, b)
            self.assertEqual(sum(a) % 2, sum(b) % 2)
            self.assertNotEqual(a[i], b[i])

    def test_constructive_recall_exhaustive_through_ten_records(self):
        for n in range(11):
            for data in product((0, 1), repeat=n):
                memory = ExactBitMemory.from_records(data)
                self.assertEqual(tuple(memory.recall(i) for i in range(n)), data)
                self.assertTrue(n <= memory.payload_bits <= n+7)

    def test_invalid_bit_values(self):
        for values in ((2,), (True,), ("0",)):
            with self.assertRaises(ValueError): ExactBitMemory.from_records(values)

    def test_invalid_query(self):
        for index in (-1, 3, True, 0.5):
            with self.assertRaises(IndexError): ExactBitMemory.from_records((1, 0, 1)).recall(index)

    def test_noncanonical_padding_rejected(self):
        with self.assertRaises(ValueError): ExactBitMemory(1, b"\x81")

    def test_witness_dominance_does_not_refute_family(self):
        r = witness_comparison(10, 5)
        self.assertEqual(r["status"], "WITNESS_DOMINATED_ONLY")
        self.assertFalse(r["target_class_exclusion_conditional"])

    def test_valid_bound_is_explicitly_conditional(self):
        r = witness_comparison(10, 5, 6)
        self.assertEqual(r["status"], "TARGET_CLASS_EXCLUDED_GIVEN_VALID_BOUND")
        self.assertFalse(r["semantic_admissibility_checked"])
        self.assertFalse(r["lower_bound_validity_checked"])

    def test_equal_bound_does_not_prove_strict_exclusion(self):
        self.assertFalse(witness_comparison(10, 5, 5)["target_class_exclusion_conditional"])

    def test_exact_rationals_preserve_ties(self):
        r = witness_comparison(Fraction(1, 3), Fraction(1, 3))
        self.assertEqual(r["status"], "NO_STRICT_DOMINANCE_ESTABLISHED")

    def test_invalid_cost_claims(self):
        for args in ((10, -1), (True, 0), (10, 1.0), (10, 5, 11)):
            with self.assertRaises(ValueError): witness_comparison(*args)


if __name__ == "__main__":
    unittest.main()
