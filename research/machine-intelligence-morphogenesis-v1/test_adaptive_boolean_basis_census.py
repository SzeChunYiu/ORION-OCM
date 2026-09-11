#!/usr/bin/env python3

import unittest

from adaptive_boolean_basis_census import run_census


class AdaptiveBooleanBasisCensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_census()

    def test_registered_universe(self) -> None:
        self.assertEqual(self.result["basis_count"], 63)
        self.assertEqual(self.result["morphology_universe"], 4096)
        self.assertEqual(self.result["current_behavior_classes_from_initial_state"], 4)
        self.assertEqual(self.result["developmental_classes_history_le_2"], 2884)

    def test_complete_and_minimal_bases(self) -> None:
        self.assertEqual(self.result["complete_basis_count"], 54)
        minimal = {tuple(row["basis"]) for row in self.result["inclusion_minimal_complete"]}
        self.assertEqual(
            minimal,
            {
                ("NAND",),
                ("NOR",),
                ("NOT", "AND"),
                ("NOT", "OR"),
            },
        )

    def test_basis_cardinality_is_not_resource_optimality(self) -> None:
        minimal_singleton = next(
            row
            for row in self.result["inclusion_minimal_complete"]
            if row["basis"] == ["NAND"]
        )
        best = self.result["best_mean_depth_complete_bases"][0]
        self.assertLess(best["mean_depth_sum"], minimal_singleton["mean_depth_sum"])

    def test_terminal_is_parent_bounded(self) -> None:
        self.assertEqual(
            self.result["terminal"],
            "ADAPTIVE_BOOLEAN_BASIS_CENSUS_EXACT__PARENT_MATHEMATICS_DOMINATES",
        )


if __name__ == "__main__":
    unittest.main()
