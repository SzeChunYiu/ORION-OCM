#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("neutral_four_family_v1", HERE / "neutral_four_family_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

ORACLE_SPEC = importlib.util.spec_from_file_location("independent_oracle_v1", HERE / "independent_oracle_v1.py")
O = importlib.util.module_from_spec(ORACLE_SPEC)
assert ORACLE_SPEC and ORACLE_SPEC.loader
sys.modules[ORACLE_SPEC.name] = O
ORACLE_SPEC.loader.exec_module(O)


class NeutralFourFamilyTests(unittest.TestCase):
    def test_parent_pins_are_exact(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 6)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, path, _ in M.PARENT_PINS:
                target = tmp / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, target)
            victim = tmp / M.PARENT_PINS[0][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_grammar_inputs_contain_no_family_names(self):
        serialized = M.canonical_json(M.GRAMMAR).lower()
        for token in ("autom", "regress", "classifier", "glm", "kernel", "basis", "family"):
            self.assertNotIn(token, serialized)

    def test_frozen_obligations_contain_no_family_names(self):
        serialized = (HERE / "FROZEN_OBLIGATIONS_V1.json").read_text().lower()
        for token in ("autom", "regress", "classifier", "glm", "kernel", "basis", "family"):
            self.assertNotIn(token, serialized)

    def test_complete_indexed_universes_are_generated_before_filtering(self):
        self.assertEqual(len(M.generate_indexed(1)), 27)
        self.assertEqual(len(M.generate_indexed(2)), 19683)
        self.assertEqual(len({row.semantics for row in M.generate_indexed(2)}), 19683)

    def test_semantic_no_smuggling_audit(self):
        audit = M.semantic_no_smuggling_audit()
        self.assertTrue(audit["token_scan_clean"])
        self.assertTrue(audit["provenance_closed_over_registered_lower_ops"])
        self.assertTrue(audit["denotations_total_on_full_carrier_domains"])
        self.assertTrue(audit["grammar_unchanged"])

    def test_frozen_predictions_match_primary_recovery(self):
        obligations, predictions = M.load_inputs()
        self.assertTrue(M.prediction_audit(obligations, predictions)["all_match"])

    def test_source_separated_oracle_is_green_and_byte_stable(self):
        result = O.build()
        self.assertTrue(result["all_match"])
        self.assertFalse(result["imports_primary_checker"])
        self.assertEqual(O.canonical(result), (HERE / "ORACLE_RESULT_V1.json").read_text())

    def test_independent_routes_agree(self):
        obligations, _ = M.load_inputs()
        self.assertTrue(M.independent_search_audit(obligations)["all_agree"])

    def test_persistent_state_positive_and_memoryless_negative(self):
        obligations, _ = M.load_inputs()
        by_id = {row["id"]: row for row in obligations["obligations"]}
        self.assertEqual(M.sequence_witness(by_id["O0_POS"])["selected"]["cells"], 1)
        self.assertEqual(M.sequence_witness(by_id["O0_NEG"])["selected"]["cells"], 0)

    def test_three_state_lower_bound_and_price_reversal(self):
        obligations, _ = M.load_inputs()
        positive = next(row for row in obligations["obligations"] if row["id"] == "O0_POS")
        self.assertEqual(M.sequence_lower_bound(positive)["minimum_states"], 3)
        self.assertEqual(M.state_history_crossover(4, 1)["decision"], "PERSISTENT")
        self.assertEqual(M.state_history_crossover(4, 20)["decision"], "REPLAY")
        self.assertTrue(M.state_history_crossover(4, 1)["phase_iff"])

    def test_static_positive_structural_classes(self):
        self.assertEqual(M.blind_structural_class((1, 0, 2), 1), "AFFINE_SHARED_RESPONSE")
        self.assertEqual(M.blind_structural_class((1, 0, 0), 1), "BINARY_DECISION_ON_AFFINE_SCORE")
        self.assertEqual(M.blind_structural_class((0, 1, 1), 1), "NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE")
        self.assertEqual(M.blind_structural_class((0, 0, 0, 1, 2, 0, 2, 1, 0), 2), "CROSS_COORDINATE_LIFTED_INTERACTION")

    def test_negative_structural_regimes(self):
        self.assertNotEqual(M.blind_structural_class((0, 1, 1), 1), "AFFINE_SHARED_RESPONSE")
        self.assertEqual(M.blind_structural_class((1, 0, 2), 1), "AFFINE_SHARED_RESPONSE")
        self.assertEqual(M.blind_structural_class((0, 1, 2, 1, 2, 0, 2, 0, 1), 2), "ADDITIVELY_SEPARABLE_RESPONSE")

    def test_static_resource_crossovers(self):
        obligations, _ = M.load_inputs()
        regimes = {row["id"]: row for row in obligations["resource_regimes"]}
        by_id = {row["id"]: row for row in obligations["obligations"]}
        for obligation_id, arity in (("O1_POS", 1), ("O2_POS", 1), ("O3_POS", 2)):
            target = by_id[obligation_id]["table"]
            low_reuse = M.select_exact(target, arity, regimes["R_STORAGE"])
            high_reuse = M.select_exact(target, arity, regimes["R_REUSE"])
            self.assertNotEqual(low_reuse["winners"], high_reuse["winners"])

    def test_finite_lower_bounds(self):
        self.assertEqual(len({tuple((a * x + b) % 3 for x in M.FIELD) for a, b in M.product(M.FIELD, repeat=2)}), 9)
        self.assertEqual(3 ** 4, 81)

    def test_all_registered_remints(self):
        self.assertEqual(M.remint_audit((1, 0, 2), 1), {"permutations": 6, "all_roundtrips": True})
        state = M.step_remint_audit()
        self.assertEqual(state["transition_output_checks"], 54)
        self.assertTrue(state["all_transport_checks"])

    def test_family_gate_ledger_fails_closed(self):
        ledger = M.family_gate_ledger()
        self.assertEqual(ledger["gate_count"], 10)
        self.assertTrue(ledger["all_family_rows_open"])
        self.assertEqual(len(ledger["rows"]), 4)
        for row in ledger["rows"]:
            self.assertEqual(row["gates"]["real_scale_test"]["status"], "OPEN")
            self.assertFalse(row["complete"])

    def test_target_encoded_parents_are_downgraded(self):
        artifacts = M.validate_artifacts()
        self.assertTrue(artifacts["target_encoded_parent_downgraded"])
        self.assertTrue(artifacts["p0_closure_downgraded"])

    def test_reconciliation_changes_only_shared_row(self):
        artifacts = M.validate_artifacts()
        self.assertTrue(artifacts["family_rows_open"])
        self.assertTrue(artifacts["one_shared_replacement"])
        self.assertTrue(artifacts["direct_pr_reference"])

    def test_contracts_reject_invalid_values(self):
        with self.assertRaises(ValueError):
            M.domain(0)
        with self.assertRaises(ValueError):
            M.indexed_candidate((0,), 1)
        with self.assertRaises(ValueError):
            M.carrier_remint((0, 1, 2), 1, (0, 0, 2))
        with self.assertRaises(ValueError):
            M.state_history_crossover(1, 0)

    def test_result_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(M.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())

    def test_forbidden_family_promotions_preserved(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertIn("REAL_SCALE_VALIDATION_COMPLETE", receipt["forbidden_promotions"])
        self.assertIn("ALL_KNOWN_FAMILIES_RECOVERED", receipt["forbidden_promotions"])
        self.assertTrue(receipt["family_gate_ledger"]["all_family_rows_open"])


if __name__ == "__main__":
    unittest.main()
