#!/usr/bin/env python3
"""Exact hostile controls for issue #602 Section J1 infrastructure."""

from __future__ import annotations

import unittest

from domain_infrastructure_v1 import (
    ParentAttempt,
    collision_pairs,
    freeze_receipt,
    negative_twin,
    parent_reduction_tournament,
    reveal_receipt,
    validate_registry,
)


class DomainInfrastructureTests(unittest.TestCase):
    RECEIPT_METADATA = {
        "candidate_id": "CANDIDATE_7",
        "ecology_digest": "ecology-sha",
        "resource_digest": "resource-sha",
        "grammar_digest": "grammar-sha",
        "split_digest": "split-sha",
        "prediction": "frontier enters",
        "negative_twin_digest": "twin-sha",
        "falsifier": "parent absorbs",
        "evaluator": "independent-evaluator",
    }

    def test_registry_and_complete_matrix_validate(self) -> None:
        self.assertEqual(
            validate_registry(),
            {"domains": 8, "matrix_cells": 64, "burden_classes": 4, "grammar_symbols": 24},
        )

    def test_collision_generator_enumerates_all_pairs(self) -> None:
        rows = [
            {"id": "a", "present_output": 0, "ordinary_score": 1, "future_response": "left"},
            {"id": "b", "present_output": 0, "ordinary_score": 1, "future_response": "right"},
            {"id": "c", "present_output": 0, "ordinary_score": 0, "future_response": "right"},
            {"id": "d", "present_output": 1, "ordinary_score": 1, "future_response": "left"},
        ]
        certificate = collision_pairs(rows)
        self.assertEqual(certificate["pair_count"], 6)
        self.assertEqual(certificate["collision_count"], 1)
        self.assertEqual((certificate["collisions"][0]["left"], certificate["collisions"][0]["right"]), ("a", "b"))

    def test_collision_negative_control(self) -> None:
        rows = [
            {"id": "a", "present_output": 0, "ordinary_score": 1, "future_response": "same"},
            {"id": "b", "present_output": 0, "ordinary_score": 1, "future_response": "same"},
        ]
        self.assertEqual(collision_pairs(rows)["collision_count"], 0)

    def test_negative_twin_changes_one_leaf(self) -> None:
        base = {"ecology": {"locality": "present", "noise": 0}, "budget": {"serve": 8}}
        certificate = negative_twin(base, ("ecology", "locality"), "absent")
        self.assertEqual(certificate["changed_coordinate"], "ecology.locality")
        self.assertNotEqual(certificate["base_digest"], certificate["twin_digest"])
        self.assertEqual(certificate["base"]["budget"], certificate["twin"]["budget"])

    def test_negative_twin_rejects_noop(self) -> None:
        with self.assertRaises(ValueError):
            negative_twin({"x": 1}, ("x",), 1)

    def test_parent_absorption_stops_novelty(self) -> None:
        result = parent_reduction_tournament(
            [
                ParentAttempt("strong", 1, "ABSORBS", "exact", "E1_CONSTANT_FACTOR", "proof-a"),
                ParentAttempt("weak", 2, "REFUTES", "mismatch", "NONE", "proof-b"),
            ]
        )
        self.assertEqual(result["verdict"], "PARENT_SUFFICIENT")
        self.assertEqual(result["owner"], "strong")

    def test_open_parent_forces_abstention(self) -> None:
        result = parent_reduction_tournament(
            [
                ParentAttempt("p1", 1, "REFUTES", "mismatch", "NONE", "proof"),
                ParentAttempt("p2", 2, "OPEN", "unknown", "UNKNOWN", "missing"),
            ]
        )
        self.assertEqual(result["verdict"], "CANNOT_IDENTIFY")
        self.assertFalse(result["all_parents_disposed"])

    def test_residual_requires_every_parent_refuted(self) -> None:
        result = parent_reduction_tournament(
            [
                ParentAttempt("p2", 2, "REFUTES", "mismatch", "NONE", "proof-b"),
                ParentAttempt("p1", 1, "REFUTES", "mismatch", "NONE", "proof-a"),
            ]
        )
        self.assertEqual(result["verdict"], "RESIDUAL_SURVIVES_REGISTERED_PARENT_SET")
        self.assertTrue(result["all_parents_disposed"])
        self.assertEqual([row["parent_id"] for row in result["attempts"]], ["p1", "p2"])

    def test_protected_receipt_commit_reveal(self) -> None:
        outcome = {"winner": "CANDIDATE_7", "burden": [3, 5]}
        freeze = freeze_receipt(self.RECEIPT_METADATA, outcome, "registered-secret")
        self.assertNotIn("outcome", freeze)
        self.assertNotIn("salt", freeze)
        reveal = reveal_receipt(freeze, outcome, "registered-secret")
        self.assertTrue(reveal["commitment_verified"])

    def test_protected_receipt_rejects_changed_outcome(self) -> None:
        freeze = freeze_receipt(self.RECEIPT_METADATA, {"winner": "c"}, "salt")
        with self.assertRaises(ValueError):
            reveal_receipt(freeze, {"winner": "parent"}, "salt")

    def test_protected_receipt_rejects_incomplete_metadata(self) -> None:
        with self.assertRaises(ValueError):
            freeze_receipt({"candidate_id": "c"}, {"winner": "c"}, "salt")


if __name__ == "__main__":
    unittest.main()
