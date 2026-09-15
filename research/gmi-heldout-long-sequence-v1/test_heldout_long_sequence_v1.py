import json
from math import ceil, log2
from pathlib import Path
import unittest

import heldout_long_sequence_v1 as h


class HeldoutLongSequenceTests(unittest.TestCase):
    def test_frozen_candidate_count_and_forbidden_labels(self):
        cs = h.candidates()
        self.assertEqual(len(cs), 44)
        forbidden = ("RNN", "STATE_SPACE", "COUNTER", "MEMORY", "RECURRENT", "ATTENTION")
        joined = " ".join(cs).upper()
        for token in forbidden:
            self.assertNotIn(token, joined)

    def test_calibration_and_heldout_exact_recovery(self):
        for n in h.CALIBRATION_LENGTHS + h.HELDOUT_LENGTHS:
            r = h.score_length(n)
            self.assertEqual(r["exact_candidate_count"], 1)
            self.assertEqual(len(r["winners"]), 1)
            w = r["winners"][0]
            self.assertEqual(w["expr"], "add(s,x)")
            self.assertEqual(w["class"], "ACCUMULATIVE_CARRY")
            self.assertEqual(w["terminal_state_count"], n + 1)

    def test_growing_quotient_and_storage(self):
        for n in h.HELDOUT_LENGTHS:
            r = h.score_length(n)
            self.assertEqual(r["required_terminal_states"], n + 1)
            self.assertEqual(r["carried_state_bits"], ceil(log2(n + 1)))
            self.assertLess(r["carried_state_bits"], r["explicit_history_bits"])

    def test_exact_dynamic_quotient_contains_every_true_count(self):
        for n in (3, 7, 17, 31, 63):
            pairs = h.exact_pairs("add(s,x)", n)
            self.assertEqual(pairs, {(i, i) for i in range(n + 1)})

    def test_negative_candidates_remain_inexact(self):
        for expr in ("s", "x", "xor(s,x)", "min(s,x)", "max(s,x)", "add(s,1)"):
            self.assertFalse(h.exact(expr, 17), expr)

    def test_committed_result_matches_executor_headlines(self):
        committed = json.loads(Path("RESULT_V1.json").read_text())
        generated = h.result()
        self.assertEqual(committed["freeze_commit"], generated["freeze_commit"])
        self.assertEqual(committed["terminal"], generated["terminal"])
        self.assertEqual(committed["grammar_candidate_count"], generated["grammar_candidate_count"])
        for got, exp in zip(committed["heldout"], generated["heldout"]):
            self.assertEqual(got["n"], exp["n"])
            self.assertEqual(got["exact_candidate_count"], exp["exact_candidate_count"])
            self.assertEqual(got["terminal_state_count"], exp["required_terminal_states"])
            self.assertEqual(got["carried_state_bits"], exp["carried_state_bits"])
            self.assertEqual(got["explicit_history_bits"], exp["explicit_history_bits"])
            self.assertEqual(got["winner"], exp["winners"][0]["expr"])
            self.assertEqual(got["class"], exp["winners"][0]["class"])


if __name__ == "__main__":
    unittest.main()
