#!/usr/bin/env python3
"""Unit and hostile tests for the finite clustering quartet."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


Q = _load("gmi833_f3_check_tests", HERE / "check_finite_posthoc_clustering_v1.py")
C, P, O, M = Q.C, Q.P, Q.O, Q.M


class FinitePosthocClusteringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result, cls.ledger = Q.build_artifacts()
        cls.snapshots = C.generate_evaluate_retain()
        cls.records = C.distinct_records(cls.snapshots)
        cls.clusters = C.cluster_records(cls.records)

    def test_result_is_green(self) -> None:
        self.assertEqual(self.result["verdict"], "GREEN")
        self.assertTrue(all(self.result["checks"].values()))

    def test_freeze_custody(self) -> None:
        self.assertTrue(self.result["freeze_custody"]["all_ok"])

    def test_parent_pins(self) -> None:
        self.assertTrue(self.result["parent_audit"]["all_ok"])

    def test_candidate_retention(self) -> None:
        self.assertEqual(len(self.snapshots), 576)
        self.assertEqual(len(self.ledger["rows"]), 576)
        self.assertEqual(len({row["candidate_id"] for row in self.ledger["rows"]}), 576)
        self.assertEqual(len({json.dumps(row["canonical_code"]) for row in self.ledger["rows"]}), 576)

    def test_distinct_carrier(self) -> None:
        self.assertEqual(len(self.records), 47)

    def test_cluster_partition(self) -> None:
        self.assertEqual(len(self.clusters), 12)
        self.assertEqual(sorted((len(row.members) for row in self.clusters), reverse=True), [12, 6, 5, 5, 4, 3, 2, 2, 2, 2, 2, 2])
        self.assertEqual(sum(len(row.members) for row in self.clusters), 47)

    def test_independent_oracle(self) -> None:
        self.assertTrue(self.result["independent_oracle"]["exact_partition_match"])

    def test_posthoc_known_and_unknown(self) -> None:
        posthoc = self.result["posthoc_mapping"]
        self.assertEqual(posthoc["known_mapped_cluster_count"], 4)
        self.assertEqual(posthoc["unknown_cluster_count"], 8)
        self.assertFalse(posthoc["nearest_label_fallback"])

    def test_unmatched_is_unknown(self) -> None:
        fingerprint = (("HALTED", (9,)), ("HALTED", (9,)), ("HALTED", (9,)))
        self.assertEqual(P.map_fingerprint(fingerprint, P.load_registry()), P.UNKNOWN)

    def test_ambiguous_is_unknown(self) -> None:
        row = P.load_registry()[0]
        registry = (row, {"family": "SECOND_NAME", "observations": row["observations"]})
        self.assertEqual(P.map_fingerprint(row["observations"], registry), P.UNKNOWN)

    def test_core_has_no_reference_tokens(self) -> None:
        self.assertEqual(self.result["posthoc_mapping"]["causal_core_registry_token_hits"], 0)

    def test_remint_equivariance(self) -> None:
        remint = self.result["remint_stability"]
        self.assertEqual(remint["candidate_membership_equivariance_checks"], 69120)
        self.assertTrue(remint["all_candidate_memberships_invariant"])

    def test_metric_edge_and_partition_stability(self) -> None:
        stable = self.result["metric_perturbation_stability"]
        self.assertEqual(stable["edge_decision_checks"], 1081)
        self.assertEqual(stable["minimum_base_threshold_margin"], "1/2")
        self.assertTrue(stable["edge_set_preserved"])
        self.assertTrue(stable["partition_preserved"])

    def test_medoid_and_label_stability(self) -> None:
        stable = self.result["metric_perturbation_stability"]
        self.assertTrue(stable["all_deterministic_medoids_preserved"])
        self.assertTrue(stable["all_posthoc_labels_and_UNKNOWN_preserved"])
        self.assertTrue(all(row["base_minimizers_componentwise_tied"] for row in stable["medoid_rows"]))

    def test_out_of_bound_metric_hostile(self) -> None:
        stable = self.result["metric_perturbation_stability"]
        self.assertGreater(stable["out_of_bound_hostile_edge_changes"], 0)
        self.assertNotEqual(stable["out_of_bound_hostile_cluster_count"], 12)

    def test_semantics_changing_remint_hostile(self) -> None:
        self.assertTrue(self.result["remint_stability"]["semantics_changing_pseudo_remint_detected"])
        self.assertNotEqual(self.result["remint_stability"]["pseudo_remint_morphology_distance"], "0/1")

    def test_duplicate_carrier_rejected(self) -> None:
        with self.assertRaises(ValueError):
            C.cluster_records((self.records[0], self.records[0]))

    def test_bad_threshold_rejected(self) -> None:
        with self.assertRaises(ValueError):
            C.cluster_records(self.records, threshold=Fraction(0))

    def test_malformed_fingerprint_rejected(self) -> None:
        with self.assertRaises(ValueError):
            P.map_fingerprint((("HALTED", ()),))

    def test_asymmetric_oracle_matrix_rejected(self) -> None:
        matrix = ((Fraction(0), Fraction(1)), (Fraction(2), Fraction(0)))
        with self.assertRaises(ValueError):
            O.threshold_components(matrix, Fraction(1))

    def test_committed_artifacts_match_replay(self) -> None:
        self.assertEqual((HERE / "RESULT_V1.json").read_text(encoding="utf-8"), Q.artifact_text(self.result))
        self.assertEqual((HERE / "CANDIDATE_MEMBERSHIP_V1.json").read_text(encoding="utf-8"), Q.artifact_text(self.ledger))


if __name__ == "__main__":
    unittest.main(verbosity=2)
