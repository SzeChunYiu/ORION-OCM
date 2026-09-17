#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "ecology_specification_generator_v1", HERE / "ecology_specification_generator_v1.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load ecology/specification generator module")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class EcologySpecificationGeneratorV1Tests(unittest.TestCase):
    def test_freeze_and_scope_are_exact(self):
        freeze = (HERE / "FREEZE_V1.md").read_text()
        self.assertEqual(M.FREEZE_COMMIT, "e5d6443dfe57603245f68abc7fed6c39aac4d677")
        self.assertEqual(M.FROZEN_MAIN, "fcbb8c08ce36b2970079ed715d5e757f28da46d2")
        self.assertEqual(len(M.TARGET_ROWS), 21)
        self.assertIn("The two subsequent sampling-adequacy and sampling-bias rows remain open.", freeze)

    def test_exact_seventeen_axis_registry_is_unique_and_nondegenerate(self):
        audit = M.validate_registry()
        self.assertEqual(audit["axis_count"], 17)
        self.assertTrue(audit["axis_ids_unique"])
        self.assertTrue(audit["probe_ids_unique"])
        self.assertTrue(audit["all_level_tokens_globally_unique"])
        self.assertTrue(audit["all_axes_binary_and_nondegenerate"])
        self.assertTrue(all(row["computed_probe_values"] == [False, True] for row in audit["rows"]))

    def test_probe_values_are_computed_from_payload_not_polarity_label(self):
        for axis in M.AXES:
            with self.subTest(axis=axis["id"]):
                inverted = deepcopy(axis["levels"])
                inverted[0]["expected_probe"] = True
                self.assertFalse(M.evaluate_probe(axis["id"], inverted[0]["payload"]))

    def test_syntax_and_semantic_well_formedness_are_distinct(self):
        control = M.syntax_semantics_control()
        self.assertTrue(control["valid_syntax"])
        self.assertTrue(control["valid_semantics"])
        self.assertTrue(control["hostile_syntax"])
        self.assertFalse(control["hostile_semantics"])

    def test_unregistered_or_malformed_syntax_fails_closed(self):
        ecology = M.ecology_from_indices([0] * 17)
        ecology["coordinates"][0]["level_token"] = "unregistered"
        self.assertFalse(M.syntax_well_formed(ecology))
        self.assertFalse(M.semantic_well_formed(ecology))
        with self.assertRaises(ValueError):
            M.build_behavioral_specification(ecology)

    def test_indices_require_exact_integers_not_booleans(self):
        for bad in (True, False, 0.0, "0"):
            indices = [0] * 17
            indices[3] = bad
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                M.ecology_from_indices(indices)

    def test_mixed_radix_rank_requires_exact_positive_integer_radices_and_digits(self):
        for digits, sizes in (([True], [2]), ([0.0], [2]), ([0], [True]), ([0], [0]), ([0], [2.0])):
            with self.subTest(digits=digits, sizes=sizes), self.assertRaises(ValueError):
                M.mixed_radix_code(digits, sizes)
        self.assertEqual(M.mixed_radix_code([1, 0, 1], [2, 2, 2]), 5)

    def test_external_behavioral_specification_and_exact_score(self):
        ecology = M.ecology_from_indices([index % 2 for index in range(17)])
        specification = M.build_behavioral_specification(ecology)
        expected = {row["probe"]: row["required_response"] for row in specification["required_relation"]}
        self.assertEqual(M.score_behavior(specification, expected), {"correct": 17, "total": 17, "exact_score": "17/17", "accepted": True})
        wrong = dict(expected)
        wrong[M.PROBE_IDS[0]] = 1 - wrong[M.PROBE_IDS[0]]
        self.assertEqual(M.score_behavior(specification, wrong), {"correct": 16, "total": 17, "exact_score": "16/17", "accepted": False})

    def test_score_rejects_bool_noninteger_and_incomplete_responses(self):
        specification = M.build_behavioral_specification(M.ecology_from_indices([0] * 17))
        expected = {row["probe"]: row["required_response"] for row in specification["required_relation"]}
        for bad in (True, False, 0.0, "0"):
            hostile = dict(expected)
            hostile[M.PROBE_IDS[0]] = bad
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                M.score_behavior(specification, hostile)
        incomplete = dict(expected)
        incomplete.pop(M.PROBE_IDS[-1])
        with self.assertRaises(ValueError):
            M.score_behavior(specification, incomplete)

    def test_score_rejects_malformed_or_boolean_target_specifications(self):
        specification = M.build_behavioral_specification(M.ecology_from_indices([0] * 17))
        self.assertTrue(M.behavioral_specification_well_formed(specification))
        for bad in (True, 0.0, "0"):
            hostile = deepcopy(specification)
            hostile["required_relation"][0]["required_response"] = bad
            with self.subTest(bad=repr(bad)):
                self.assertFalse(M.behavioral_specification_well_formed(hostile))
                with self.assertRaises(ValueError):
                    M.score_behavior(hostile, {row["probe"]: 0 for row in specification["required_relation"]})

    def test_registered_product_has_four_independent_exact_counts(self):
        census = M.family_census()
        self.assertEqual(census["carrier_sizes"], [2] * 17)
        self.assertEqual(census["arithmetic_product"], 131072)
        self.assertEqual(census["recursive_product"], 131072)
        self.assertEqual(census["iterator_count"], 131072)
        self.assertEqual(census["unique_mixed_radix_codes"], 131072)
        self.assertTrue(census["complete_integer_interval"])

    def test_every_axis_has_an_isolated_matched_twin(self):
        twins = M.matched_twins()
        self.assertEqual(len(twins), 17)
        self.assertEqual({row["axis"] for row in twins}, set(M.AXIS_IDS))
        for row in twins:
            with self.subTest(axis=row["axis"]):
                self.assertEqual(row["coordinate_differences"], [row["axis"]])
                self.assertEqual(row["payload_differences"], [row["axis"]])
                self.assertEqual(row["target_differences"], [row["probe"]])
                self.assertEqual((row["negative_probe_value"], row["positive_probe_value"]), (0, 1))
                self.assertTrue(row["isolated"])
                self.assertTrue(row["same_input_carrier"])
                self.assertTrue(row["same_response_carrier"])
                self.assertTrue(row["same_score_rule"])

    def test_disjoint_opaque_remint_preserves_semantics_specs_scores_and_twins(self):
        census = M.remint_census()
        self.assertEqual((census["original_token_count"], census["reminted_token_count"]), (34, 34))
        self.assertTrue(census["token_sets_disjoint"])
        self.assertTrue(census["remint_bijective"])
        self.assertTrue(census["carrier_sizes_preserved"])
        self.assertTrue(census["twin_invariants_preserved"])
        self.assertTrue(all(all(row[key] for key in ("token_erased_ecology_equal", "behavioral_specification_equal", "score_equal")) for row in census["witnesses"]))

    def test_architecture_neutrality_has_semantic_and_syntactic_evidence(self):
        audit = M.architecture_neutrality_audit()
        self.assertTrue(audit["passes"])
        self.assertEqual(audit["known_family_phrase_hits_in_operational_contract"], [])
        self.assertEqual(audit["forbidden_parameter_hits"], [])
        self.assertEqual({row["axis"] for row in audit["external_semantics_audit"]}, set(M.AXIS_IDS))
        self.assertTrue(all(row["external_semantics_rationale"] for row in audit["external_semantics_audit"]))
        self.assertTrue(all(row["probe_uses_only_axis_payload"] for row in audit["external_semantics_audit"]))

    def test_registry_ledger_manifest_and_reconciliation_are_exact(self):
        self.assertEqual(M.canonical(M.registry_document()), (HERE / "ECOLOGY_AXIS_REGISTRY_V1.json").read_bytes())
        ledger = M.build_ledger()
        self.assertEqual(M.canonical(ledger), (HERE / "SCIENTIFIC_LEDGER_V1.json").read_bytes())
        self.assertEqual(len(ledger["matched_twins"]), 17)
        self.assertEqual(len(ledger["theorems"]), 5)
        package = M.validate_package_contracts()
        self.assertEqual(package, {"manifest_rows": 21, "reconciliation_rows": 21, "artifacts": 9})
        reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_ECOLOGY_GENERATOR_V1.json").read_text())
        self.assertFalse(any("Sample enough ecology space" in row["old"] or "Quantify ecology sampling" in row["old"] for row in reconciliation["replacements"]))

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.run()
        self.assertEqual(receipt["status"], "GREEN")
        self.assertEqual(receipt["terminal"], M.TERMINAL)
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(receipt["counts"]["registered_product_cardinality"], 131072)
        self.assertEqual(receipt["counts"]["matched_twins"], 17)
        self.assertEqual(M.canonical(receipt), (HERE / "RESULT_V1.json").read_bytes())
        self.assertEqual(json.loads(M.canonical(receipt)), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_keeps_sampling_and_family_recovery_open(self):
        boundary = M.run()["claim_boundary"]
        self.assertIn("No sampling-adequacy", boundary)
        self.assertIn("sampling-bias", boundary)
        self.assertIn("architecture-recovery", boundary)


if __name__ == "__main__":
    unittest.main()
