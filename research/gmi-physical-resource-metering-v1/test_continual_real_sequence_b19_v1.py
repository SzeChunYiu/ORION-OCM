from __future__ import annotations

import unittest

from continual_real_sequence_b19_v1 import planted_sequences, run_witness


class B19RealSequenceTests(unittest.TestCase):
    def test_two_concrete_sequences_and_price_ratio_prediction(self):
        seqs = planted_sequences()
        self.assertEqual(len(seqs), 2)
        self.assertNotEqual(seqs[0].name, seqs[1].name)
        result = run_witness()
        self.assertEqual(result["claim_ceiling"], "REAL_SEQUENCE_WITNESS_AT_PLANTED_SCOPE")
        self.assertTrue(result["stable_across_sequences_at_fixed_prices"])
        self.assertTrue(result["price_ratio_moves_winner"])
        for row in result["cheap_capacity"]:
            self.assertEqual(row["winners"], ["expand"])
        for row in result["dear_capacity"]:
            self.assertEqual(row["winners"], ["modularize"])


if __name__ == "__main__":
    unittest.main()
