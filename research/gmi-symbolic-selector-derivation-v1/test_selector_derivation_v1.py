#!/usr/bin/env python3
"""Hostile exact controls for the #602 B14 selector derivation."""

from __future__ import annotations

import unittest

from selector_derivation_v1 import (
    arbitrary_subset_selectors,
    domain,
    equality_selectors,
    evaluate,
    minimum_cover,
    mux_012,
    positional_selectors,
    xor_01,
)


class SelectorDerivationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = evaluate()

    def test_candidate_census_is_exact(self) -> None:
        self.assertEqual(len(domain(3)), 8)
        self.assertEqual(len(positional_selectors(3)), 27)
        self.assertEqual(len(equality_selectors(3)), 11)
        self.assertEqual(len(arbitrary_subset_selectors(3)), 255)

    def test_truth_tables_are_pinned(self) -> None:
        obligations = self.result["obligations"]
        self.assertEqual(obligations["xor_01"]["truth_table_lexicographic_000_to_111"], "00111100")
        self.assertEqual(obligations["mux_012"]["truth_table_lexicographic_000_to_111"], "01010011")

    def test_equality_selector_wins_xor_twin(self) -> None:
        families = self.result["obligations"]["xor_01"]["families"]
        self.assertEqual(families["equality"]["rules"], 2)
        self.assertEqual(families["positional"]["rules"], 3)
        self.assertEqual(families["equality"]["selector_description_atoms_or_bits"], 2)

    def test_positional_selector_wins_mux_twin(self) -> None:
        families = self.result["obligations"]["mux_012"]["families"]
        self.assertEqual(families["positional"]["rules"], 2)
        self.assertEqual(families["equality"]["rules"], 3)
        self.assertEqual(families["positional"]["selector_description_atoms_or_bits"], 2)

    def test_arbitrary_subset_is_table_like_not_free(self) -> None:
        for obligation in self.result["obligations"].values():
            arbitrary = obligation["families"]["arbitrary_subset"]
            self.assertEqual(arbitrary["rules"], 2)
            self.assertEqual(arbitrary["selector_description_atoms_or_bits"], 16)

    def test_minimality_is_recomputed_not_read_from_receipt(self) -> None:
        xor_score, _ = minimum_cover(3, xor_01, equality_selectors(3))
        mux_score, _ = minimum_cover(3, mux_012, positional_selectors(3))
        self.assertEqual(xor_score, (2, 2))
        self.assertEqual(mux_score, (2, 2))

    def test_negative_mutation_changes_the_result(self) -> None:
        # Replacing XOR by one projection must collapse the exact minimum to
        # one global rule; this catches a search that ignores the obligation.
        projection = lambda point: point[0]
        score, _ = minimum_cover(3, projection, equality_selectors(3))
        self.assertEqual(score, (1, 0))


if __name__ == "__main__":
    unittest.main()
