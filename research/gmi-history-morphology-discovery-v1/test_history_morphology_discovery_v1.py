import json
from pathlib import Path
import unittest

import history_morphology_discovery_v1 as h


class HistoryMorphologyDiscoveryTests(unittest.TestCase):
    def test_targets_are_unseen_and_candidate_space_identical(self):
        self.assertTrue(set(h.HISTORY).isdisjoint(h.TARGETS))
        self.assertEqual(h.START_MORPHOLOGY, 0)
        self.assertEqual(set(h.reset_order()), set(range(64)))
        self.assertEqual(set(h.learned_order(h.HISTORY)), set(range(64)))
        shuffled = tuple(h.permute_mask(m) for m in h.HISTORY)
        self.assertEqual(set(h.learned_order(shuffled)), set(range(64)))

    def test_shuffled_history_preserves_example_hamming_weights(self):
        shuffled = tuple(h.permute_mask(m) for m in h.HISTORY)
        original_weights = [sum(h.bits(m)) for m in h.HISTORY]
        shuffled_weights = [sum(h.bits(m)) for m in shuffled]
        self.assertEqual(original_weights, shuffled_weights)

    def test_exact_discovery_ranks(self):
        self.assertEqual(h.arm_ranks(), {
            "RESET": [40, 54],
            "CONTINUED": [5, 6],
            "SHUFFLED_HISTORY": [16, 20],
        })

    def test_history_improves_discovery_without_warm_start(self):
        ranks = h.arm_ranks()
        self.assertLess(h.mean_rank(ranks["CONTINUED"]), h.mean_rank(ranks["RESET"]))
        self.assertLess(h.mean_rank(ranks["CONTINUED"]), h.mean_rank(ranks["SHUFFLED_HISTORY"]))
        # Historical masks are still the first four CONTINUED proposals: they cost work.
        self.assertEqual(h.learned_order(h.HISTORY)[:4], h.HISTORY)

    def test_committed_result_matches_executor(self):
        committed = json.loads(Path("RESULT_V1.json").read_text())
        generated = h.result()
        for key in (
            "freeze_commit", "start_morphology_all_arms", "candidate_count_each_arm",
            "history", "targets", "targets_unseen", "shuffled_history",
            "history_bit_counts", "shuffled_bit_counts", "ranks", "mean_ranks",
            "continued_first_ten", "shuffled_first_ten", "same_candidate_space",
            "historical_candidates_remain_charged", "terminal", "claim_ceiling",
        ):
            self.assertEqual(committed[key], generated[key], key)


if __name__ == "__main__":
    unittest.main()
