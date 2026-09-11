#!/usr/bin/env python3

import unittest

from developmental_equivalence_witness import TinyLearner, build_witness


class DevelopmentalEquivalenceWitnessTest(unittest.TestCase):
    def test_same_current_behavior(self) -> None:
        a = TinyLearner((0, 0), "NO_OP")
        b = TinyLearner((0, 0), "SUPERVISED_MEMORIZE")
        self.assertEqual(a.truth_table(), b.truth_table())

    def test_same_experience_causes_divergence(self) -> None:
        a = TinyLearner((0, 0), "NO_OP").update(1, 1)
        b = TinyLearner((0, 0), "SUPERVISED_MEMORIZE").update(1, 1)
        self.assertNotEqual(a.truth_table(), b.truth_table())
        self.assertEqual(a.truth_table(), (0, 0))
        self.assertEqual(b.truth_table(), (0, 1))

    def test_receipt_terminal(self) -> None:
        receipt = build_witness()
        self.assertEqual(
            receipt["terminal"],
            "CURRENT_BEHAVIOR_EQUIVALENCE_DOES_NOT_IMPLY_DEVELOPMENTAL_EQUIVALENCE_EXACT",
        )


if __name__ == "__main__":
    unittest.main()
