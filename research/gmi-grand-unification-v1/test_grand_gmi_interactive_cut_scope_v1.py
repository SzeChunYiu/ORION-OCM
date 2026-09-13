import json
from fractions import Fraction
from pathlib import Path
import unittest

from grand_gmi_interactive_cut_scope_checks_v1 import (
    exact_decoder,
    exact_single_player_status,
    exhaustive_small_one_way_encoders,
    feedback_messages,
    index_witness,
    run,
)


class InteractiveCutScopeTests(unittest.TestCase):
    def test_index_four_refutes_unconditioned_one_way_transfer(self):
        witness = index_witness(4)
        self.assertEqual(witness["one_way_conflict_edges"], 120)
        self.assertEqual(witness["one_way_minimum_complete_message_symbols"], 16)
        self.assertEqual(witness["interactive_input_pairs"], 64)
        self.assertEqual(witness["interactive_complete_transcripts"], 8)
        self.assertLess(witness["interactive_total_fixed_bits"],
                        witness["one_way_minimum_fixed_bits"])
        self.assertEqual(witness["conditioned_minimum_reply_symbols"], 2)

    def test_feedback_changes_encoder_information_for_fixed_word(self):
        word = (0, 1, 0, 1)
        self.assertEqual(feedback_messages(word, 0), ((0, 0), (0,)))
        self.assertEqual(feedback_messages(word, 1), ((0, 1), (1,)))
        self.assertEqual(feedback_messages(word, 2), ((1, 0), (0,)))
        self.assertEqual(feedback_messages(word, 3), ((1, 1), (1,)))

    def test_exhaustive_short_encoders_preserve_exact_one_way_lower_bound(self):
        census = exhaustive_small_one_way_encoders()
        self.assertEqual(sum(row["encoders"] for row in census), 359)
        self.assertEqual([row["successful"] for row in census], [0, 2, 0, 0, 0, 24])
        self.assertIsNone(exact_decoder([(0, 1), (1, 0)], (0, 0)))
        self.assertEqual(exact_decoder([(0,), (0,)], (0, 0)), {(0, 0): 0})

    def test_exact_comparison_preserves_ties_and_tiny_strict_regret(self):
        self.assertEqual(exact_single_player_status((0, 0)), ((0, 1), (0, 1)))
        self.assertEqual(exact_single_player_status((0, Fraction(1, 2**2048))),
                         ((0,), (0,)))
        self.assertEqual(exact_single_player_status((0, -1, -1)), ((1, 2), (1, 2)))

    def test_frozen_receipt_and_bounded_sweep(self):
        receipt = json.loads(Path(__file__).with_name(
            "GRAND_GMI_INTERACTIVE_CUT_SCOPE_RECEIPT_V1.json").read_text())
        actual = run()
        self.assertEqual(actual, receipt)
        self.assertEqual(sum(row["interactive_input_pairs"] for row in actual["index_sweep"]), 3586)
        self.assertEqual(actual["rational_strategic_specialization"]["finite_rational_games"], 150)


if __name__ == "__main__":
    unittest.main()
