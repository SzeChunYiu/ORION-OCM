#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "capability_ceiling_reaudit_v1", HERE / "capability_ceiling_reaudit_v1.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load capability ceiling re-audit module")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class CapabilityCeilingReauditV1Tests(unittest.TestCase):
    def test_all_nine_source_blobs_are_exactly_pinned(self):
        observed = M.verify_pins()
        self.assertEqual(set(observed), set(M.PINS))
        self.assertEqual(len(observed), 9)

    def test_source_drift_fails_closed(self):
        path, expected = M.PINS["contract"]
        self.assertNotEqual(M.git_blob_sha((M.ROOT / path).read_bytes() + b"\n"), expected)

    def test_exact_27_definition_inventory_and_fields(self):
        rows = M.architecture_audit()
        self.assertEqual(len(rows), 27)
        self.assertEqual(len({row["id"] for row in rows}), 27)
        self.assertTrue(all(not row["missing_fields"] for row in rows))
        self.assertTrue(all(not row["extra_fields"] for row in rows))
        self.assertTrue(all(not row["malformed_fields"] for row in rows))

    def test_all_27_normalized_contracts_pass_registered_architecture_audit(self):
        rows = M.architecture_audit()
        self.assertTrue(all(row["semantic_rationale"] for row in rows))
        self.assertTrue(all(not row["normalized_residual_forbidden_family_tokens"] for row in rows))
        self.assertTrue(all(not row["normalized_residual_mechanism_prior_triggers"] for row in rows))
        self.assertTrue(all(row["normalized_status"] == "ARCHITECTURE_INDEPENDENT_AT_REGISTERED_EXTERNAL_CONTRACT_SCOPE" for row in rows))

    def test_original_and_normalized_dispositions_are_explicit(self):
        rows = M.architecture_audit()
        original = [row for row in rows if row["disposition"] == "ORIGINAL_OPERATIONAL_CONTRACT_ACCEPTED_AS_EXTERNAL"]
        normalized = [row for row in rows if row["disposition"] == "NORMALIZED_OPERATIONAL_REPLACEMENT_REQUIRED"]
        self.assertEqual((len(original), len(normalized)), (11, 16))
        self.assertTrue(all(not row["changed_operational_fields"] for row in original))
        self.assertTrue(all(row["changed_operational_fields"] for row in normalized))

    def test_self_improvement_architecture_edit_is_replaced_not_excused(self):
        row = next(row for row in M.architecture_audit() if row["id"] == "cap-self-improvement")
        self.assertIn("architecture edit", row["original_operational_contract"]["inputs"])
        self.assertNotIn("architecture edit", row["normalized_operational_contract"]["inputs"])
        self.assertEqual(row["changed_operational_fields"], ["allowed_info", "inputs"])

    def test_named_mechanism_priors_are_replaced_field_by_field(self):
        rows = {row["id"]: row for row in M.architecture_audit()}
        for row_id in (
            "cap-procedural-memory", "cap-compositional-reasoning", "cap-hierarchical-skill",
            "cap-exploration", "cap-causal-inference", "cap-counterfactual-reasoning",
            "cap-social-cognition",
        ):
            with self.subTest(row_id=row_id):
                self.assertEqual(rows[row_id]["disposition"], "NORMALIZED_OPERATIONAL_REPLACEMENT_REQUIRED")
                self.assertTrue(rows[row_id]["changed_operational_fields"])

    def test_normalized_contract_file_is_canonical_and_source_bound(self):
        contract = M.normalized_capability_contract()
        self.assertEqual(contract["source_contract_blob"], M.PINS["contract"][1])
        self.assertEqual(len(contract["rows"]), 27)
        self.assertEqual(M.canonical(contract), (HERE / "ARCHITECTURE_NEUTRAL_CAPABILITY_CONTRACT_V1.json").read_bytes())

    def test_exact_eleven_historical_ids_are_reconstructed(self):
        rows = M.ceiling_audit()
        self.assertEqual(len(rows), 11)
        self.assertEqual(len({row["id"] for row in rows}), 11)
        self.assertEqual({row["id"] for row in rows}, set(M.THEOREM_SPECS))
        self.assertTrue(all(not row["architecture_argument_present"] for row in rows))

    def test_ceiling_ledger_preserves_historical_assumptions_and_custody(self):
        rows = M.ceiling_audit()
        self.assertTrue(all(row["historical_assumptions"] for row in rows))
        self.assertTrue(all(len(row["canonical_source_row_sha256"]) == 64 for row in rows))
        self.assertTrue(all(row["strongest_parent"] for row in rows))
        self.assertTrue(all(row["falsifier"] for row in rows))

    def test_precision_is_code_carrier_not_universal_threshold_claim(self):
        row = next(row for row in M.ceiling_audit() if row["id"] == "F2_PRECISION_BOUNDARY")
        self.assertIn("CODE_CARRIER", row["status"])
        self.assertIn("old one-threshold", row["generalization_beyond_toy_finite_space"])

    def test_search_distinguishes_direct_verification_from_n_minus_one_identification(self):
        boundary = M.search_boundary()
        self.assertEqual(boundary["cases"], 35)
        self.assertEqual(boundary["direct_positive_failures_at_n_minus_1"], 7)
        self.assertEqual(boundary["mere_identification_successes_at_n_minus_1"], 35)
        row = next(row for row in M.ceiling_audit() if row["id"] == "F2_SEARCH_BUDGET_VERIFIED_CLASS")
        self.assertEqual(row["status"], "NARROWED_TO_DIRECT_POSITIVE_VERIFICATION")

    def test_rank_claim_is_exact_linear_or_explicit_first_order_only(self):
        row = next(row for row in M.ceiling_audit() if row["id"] == "F2_PROTECTED_RANK_FRONTIER")
        self.assertIn("LINEAR_OR_EXPLICIT_FIRST_ORDER", row["status"])
        self.assertIn("explicit derivative", row["generalization_beyond_toy_finite_space"])

    def test_factorization_census(self):
        self.assertEqual(M.factorization_census(), {"cases": 64, "agreements": 64, "nonfactorable_hostiles": 36})

    def test_injection_and_product_censuses(self):
        self.assertEqual(M.injection_census(), {"cases": 25, "agreements": 25})
        self.assertEqual(M.product_channel_census(), {"cases": 40, "agreements": 40})

    def test_verification_census(self):
        self.assertEqual(M.verification_census(), {"cases": 168, "agreements": 168})

    def test_all_eleven_nearest_hostiles_are_rejected(self):
        controls = M.adversarial_controls()
        self.assertEqual(len(controls), 11)
        self.assertTrue(all(row["hostile_rejected"] for row in controls))
        self.assertEqual({row["id"] for row in controls}, set(M.THEOREM_SPECS))

    def test_three_corrections_and_only_three(self):
        ledger = M.build_ledger()
        self.assertEqual(
            {row["id"] for row in ledger["historical_corrections"]},
            {"F2_PRECISION_BOUNDARY", "F2_SEARCH_BUDGET_VERIFIED_CLASS", "F2_PROTECTED_RANK_FRONTIER"},
        )

    def test_manifest_and_reconciliation_are_exactly_three_section_k_rows(self):
        self.assertEqual(M.validate_package_contracts(), {"manifest_rows": 3, "reconciliation_rows": 3})

    def test_ledger_file_is_canonical_and_complete(self):
        ledger = M.build_ledger()
        self.assertEqual(M.canonical(ledger), (HERE / "SCIENTIFIC_LEDGER_V1.json").read_bytes())
        self.assertEqual(len(ledger["capability_definitions"]), 27)
        self.assertEqual(len(ledger["ceilings"]), 11)

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.run()
        self.assertEqual(receipt["status"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(receipt["counts"]["exact_census_cases"], 332)
        self.assertEqual(receipt["counts"]["capability_definitions_audited"], 27)
        self.assertEqual(receipt["counts"]["original_operational_contracts_accepted_as_external"], 11)
        self.assertEqual(receipt["counts"]["normalized_operational_replacements_required"], 16)
        self.assertEqual(receipt["counts"]["normalized_architecture_independent_definitions"], 27)
        self.assertEqual(receipt["counts"]["ceilings_reproved"], 11)
        self.assertEqual(M.canonical(receipt), (HERE / "RESULT_V1.json").read_bytes())
        self.assertEqual(json.loads(M.canonical(receipt)), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_forbids_predictor_empirics_and_universal_architecture(self):
        boundary = M.run()["claim_boundary"]
        self.assertIn("No G6 predictor", boundary)
        self.assertIn("empirical transfer", boundary)
        self.assertIn("universal architecture ranking", boundary)


if __name__ == "__main__":
    unittest.main()
