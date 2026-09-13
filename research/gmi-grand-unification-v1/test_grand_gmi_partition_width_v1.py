import importlib.util
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("partition_width", HERE/"grand_gmi_partition_width_checks_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def all_depth_profiles(truth, inputs):
    """Enumerate complete trees; return per-input depths without Bellman minimization."""
    if len({truth[x] for x in inputs}) == 1:
        return {(0,)*len(inputs)}
    profiles = set()
    for bit in (0, 1):
        left = tuple(x for x in inputs if not x >> bit & 1)
        right = tuple(x for x in inputs if x >> bit & 1)
        if not left or not right:
            continue
        for a, b in product(all_depth_profiles(truth, left), all_depth_profiles(truth, right)):
            depths = dict(zip(left, a)) | dict(zip(right, b))
            profiles.add(tuple(1+depths[x] for x in inputs))
    return profiles


def brute_messages(rows):
    for count in range(1, len(rows)+1):
        for labels in product(range(count), repeat=len(rows)):
            if all(len({row[column] for row, label in zip(rows, labels) if label == message}) <= 1
                   for message in range(count) for column in range(len(rows[0]))):
                return count
    raise AssertionError("finite sender must be encodable")


class PartitionWidthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = MOD.run()

    def test_frozen_receipt_matches_real_truth_table_census(self):
        self.assertTrue(self.receipt["all_checks_green"])
        frozen = json.loads((HERE/"GRAND_GMI_PARTITION_WIDTH_RECEIPT_V1.json").read_text())
        self.assertEqual(self.receipt, frozen)
        self.assertEqual(self.receipt["census"]["partial_assignment_states"], 4*sum(3**n for n in range(2, 9)))
        self.assertEqual(self.receipt["census"]["partition_instances"], 4*sum(2**n for n in range(2, 9)))

    def test_every_two_bit_boolean_tree_against_complete_tree_profiles(self):
        for truth in product((0, 1), repeat=4):
            profiles = all_depth_profiles(truth, tuple(range(4)))
            actual = MOD.query_costs(2, truth)
            self.assertEqual(actual["expected"], min(sum(p)/F(4) for p in profiles))
            self.assertEqual(actual["worstcase"], min(max(p) for p in profiles))

    def test_rows_against_all_message_encoders(self):
        for truth in (*product((0, 1), repeat=4), (0, 1, 2, 3)):
            for subset in range(4):
                rows = MOD.response_rows(2, truth, subset)
                self.assertEqual(len(set(rows)), brute_messages(rows))

    def test_equal_width_does_not_mean_equal_response_rows(self):
        tables = MOD.truth_tables(2)
        a = MOD.response_rows(2, tables["or"], 1)
        b = MOD.response_rows(2, tables["parity"], 1)
        self.assertEqual((len(set(a)), len(set(b))), (2, 2))
        self.assertNotEqual(a, b)
        self.assertTrue(self.receipt["equal_width_unequal_response_rows_control"])

    def test_uniform_average_is_separate_from_worstcase(self):
        tables = MOD.truth_tables(3)
        a, b = (MOD.query_costs(3, tables[name]) for name in ("or", "parity"))
        self.assertEqual((a["expected"], b["expected"]), (F(7, 4), 3))
        self.assertEqual((a["worstcase"], b["worstcase"]), (3, 3))
        self.assertEqual(a["realized_depths"][0], 3)

    def test_reverse_pair_has_common_output_alphabet_and_pointwise_cost(self):
        tables = MOD.truth_tables(3)
        for name in ("identity", "repeat_parity"):
            self.assertTrue(set(tables[name]) <= set(range(8)))
            self.assertEqual(MOD.query_costs(3, tables[name])["realized_depths"], (3,)*8)
        self.assertEqual(MOD.partition_spectrum(3, tables["identity"])[7], 8)
        self.assertEqual(MOD.partition_spectrum(3, tables["repeat_parity"])[7], 2)

    def test_constant_and_one_bit_controls(self):
        self.assertEqual(MOD.partition_spectrum(3, (7,)*8), (1,)*8)
        self.assertEqual(MOD.query_costs(3, (7,)*8)["expected"], 0)
        for truth in MOD.truth_tables(1).values():
            self.assertEqual(MOD.partition_spectrum(1, truth), (1, 2))
            self.assertEqual(MOD.query_costs(1, truth)["expected"], 1)
        self.assertEqual(MOD.query_costs(0, (0,))["expected"], 0)

    def test_invalid_registers_rejected(self):
        for n, truth in ((True, (0, 1)), (-1, ()), (2, (0, 1)),
                         (1, (0, True)), (1, (0, -1)), (1, (0, float("nan")))):
            with self.assertRaises(ValueError):
                MOD.query_costs(n, truth)
        for subset in (-1, 4, True):
            with self.assertRaises(ValueError):
                MOD.response_rows(2, (0, 0, 0, 1), subset)


if __name__ == "__main__":
    unittest.main()
