#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "capability_bounds_interactions_v1", HERE / "capability_bounds_interactions_v1.py"
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class CapabilityBoundsInteractionsTests(unittest.TestCase):
    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 5)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, path, _, _, _ in M.PARENT_PINS:
                target = tmp / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, target)
            victim = tmp / M.PARENT_PINS[1][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_exact_numeric_contract_rejects_float_and_bool(self):
        for value in (0.5, True, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M.exact(value)

    def test_finite_floor_and_ceiling_are_attained(self):
        result = M.finite_capability_bounds({"a": 3, "b": Fraction(1, 2), "c": 3})
        self.assertEqual(result["status"], "BOUNDED")
        self.assertEqual(result["floor"], Fraction(1, 2))
        self.assertEqual(result["ceiling"], Fraction(3))
        self.assertEqual(result["floor_witnesses"], ("b",))
        self.assertEqual(result["ceiling_witnesses"], ("a", "c"))

    def test_empty_class_is_typed_and_nonnumeric(self):
        self.assertEqual(
            M.finite_capability_bounds({}),
            {"status": M.NO_FEASIBLE, "floor": None, "ceiling": None},
        )

    def test_constructive_ceiling_lower_certificate_is_not_a_uniform_floor(self):
        result = M.witness_ceiling_lower_certificate({"low": 1, "high": 3}, "high")
        self.assertTrue(result["is_ceiling_lower_certificate"])
        self.assertFalse(result["is_uniform_class_lower_bound"])
        with self.assertRaises(ValueError):
            M.witness_ceiling_lower_certificate({"low": 1}, "missing")

    def test_class_inclusion_has_opposite_bound_directions(self):
        result = M.inclusion_bounds({"middle": 2}, {"low": 1, "middle": 2, "high": 3})
        self.assertEqual(
            (result["smaller_floor"], result["larger_floor"], result["smaller_ceiling"], result["larger_ceiling"]),
            (2, 1, 2, 3),
        )
        self.assertTrue(result["floor_nonincreasing"])
        self.assertTrue(result["ceiling_nondecreasing"])

    def test_class_inclusion_rejects_member_or_objective_drift(self):
        with self.assertRaises(ValueError):
            M.inclusion_bounds({}, {"x": 1})
        with self.assertRaises(ValueError):
            M.inclusion_bounds({"x": 1}, {"y": 1})
        with self.assertRaises(ValueError):
            M.inclusion_bounds({"x": 1}, {"x": 2})

    def test_four_cell_mixed_difference_classifies_all_three_signs(self):
        positive = M.registered_interaction(M.make_design((0, 0, 0, 1)))
        zero = M.registered_interaction(M.make_design((0, 1, 1, 2)))
        negative = M.registered_interaction(M.make_design((0, 1, 1, 1)))
        self.assertEqual(positive["mixed_difference"], 1)
        self.assertEqual(zero["mixed_difference"], 0)
        self.assertEqual(negative["mixed_difference"], -1)
        self.assertEqual(
            (positive["classification"], zero["classification"], negative["classification"]),
            ("POSITIVE_SYNERGY", "ADDITIVE_AT_REGISTERED_DESIGN", "NEGATIVE_INTERACTION"),
        )

    def test_four_cell_context_drift_fails_closed(self):
        for field, value in (("contract_id", "other"), ("ecology_id", "other"), ("budget", (2,))):
            design = M.make_design((0, 0, 0, 1))
            design["11"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                M.registered_interaction(design)

    def test_four_cell_schema_flags_and_budget_fail_closed(self):
        design = M.make_design((0, 0, 0, 1))
        design["10"]["factor_a"] = False
        with self.assertRaises(ValueError):
            M.registered_interaction(design)
        design = M.make_design((0, 0, 0, 1), budget=())
        with self.assertRaises(ValueError):
            M.registered_interaction(design)
        design = M.make_design((0, 0, 0, 1))
        design["00"]["extra"] = 1
        with self.assertRaises(ValueError):
            M.registered_interaction(design)

    def test_joint_threshold_positive_synergy_iff(self):
        result = M.joint_threshold_interaction(1, 2, 1, 2, 4)
        self.assertEqual(result["products"], (1, 2, 2, 4))
        self.assertEqual(result["scores"], (0, 0, 0, 1))
        self.assertTrue(result["joint_only_condition"])
        self.assertTrue(result["strict_positive_synergy"])
        self.assertTrue(result["iff_holds"])

    def test_single_upgrade_and_additive_controls_remove_positive_synergy(self):
        twin = M.joint_threshold_interaction(1, 2, 1, 2, 2)
        additive = M.registered_interaction(M.make_design((0, 1, 1, 2)))
        self.assertFalse(twin["joint_only_condition"])
        self.assertFalse(twin["strict_positive_synergy"])
        self.assertEqual(additive["mixed_difference"], 0)

    def test_joint_threshold_contract_rejects_invalid_capacities(self):
        for args in ((2, 1, 1, 2, 4), (1, 2, 2, 1, 4), (0, 2, 1, 2, 4), (1, 2, 1, 2, True)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                M.joint_threshold_interaction(*args)

    def test_shared_budget_interference_iff_and_restoration_twin(self):
        harmed = M.shared_budget_interference(2, 2, 1)
        restored = M.shared_budget_interference(3, 2, 1)
        self.assertTrue(harmed["interferes"])
        self.assertTrue(harmed["iff_holds"])
        self.assertFalse(restored["interferes"])
        self.assertTrue(restored["iff_holds"])

    def test_shared_budget_handles_charge_above_budget_and_rejects_bad_inputs(self):
        result = M.shared_budget_interference(1, 1, 3)
        self.assertEqual(result["remaining"], 0)
        self.assertTrue(result["interferes"])
        for args in ((-1, 1, 0), (1, 0, 0), (1, 1, -1), (1.0, 1, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                M.shared_budget_interference(*args)

    def test_free_option_cannot_harm_and_objective_drift_is_rejected(self):
        result = M.free_option_monotonicity({"a": 2}, {"a": 2, "b": 1})
        self.assertTrue(result["cannot_harm_optimum"])
        self.assertEqual((result["old_optimum"], result["new_optimum"]), (2, 2))
        with self.assertRaises(ValueError):
            M.free_option_monotonicity({"a": 2}, {"a": 1, "b": 3})
        with self.assertRaises(ValueError):
            M.free_option_monotonicity({}, {"a": 1})

    def test_overlap_signature_does_not_identify_interaction_sign(self):
        result = M.overlap_nonidentification_hostile()
        self.assertEqual(result["shared_resource_channel_signature"], ("compute",))
        self.assertFalse(result["overlap_determines_sign"])
        self.assertEqual(len(set(result["classifications"].values())), 3)

    def test_bounded_census_counts(self):
        self.assertEqual(
            M.exhaustive_census(),
            {
                "finite_bound_cases": 340,
                "class_inclusion_cases": 3840,
                "four_cell_interaction_cases": 81,
                "joint_threshold_iff_cases": 1377,
                "shared_budget_iff_cases": 1210,
                "free_option_cases": 27,
            },
        )

    def test_scientific_ledger_is_complete_but_review_stays_open(self):
        self.assertEqual(
            M.validate_ledgers(),
            {"claim_ledgers": 4, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(M.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())
        self.assertEqual(json.loads(M.canonical_json(receipt)), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_excludes_unfinished_section_k_rows(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("ALL_ELEVEN_CAPABILITY_CEILINGS_REPROVED", receipt["forbidden_promotions"])
        self.assertIn("CAPABILITY_PREDICTOR_VALIDATED", receipt["forbidden_promotions"])
        self.assertIn("OVERLAP_IMPLIES_SYNERGY", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
