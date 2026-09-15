from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PRED = load("b1p_predict_v1", HERE / "predict_v1.py")
SCORE = load("b1p_score_v1", HERE / "score_v1.py")


def independent_rank(matrix):
    rows = [list(map(int, row)) for row in matrix]
    if not rows:
        return 0
    rank = 0
    cols = len(rows[0])
    for col in range(cols):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pv = rows[rank][col]
        for i in range(len(rows)):
            if i == rank or rows[i][col] == 0:
                continue
            f = rows[i][col]
            rows[i] = [pv * a - f * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


class CustodyArtifactTests(unittest.TestCase):
    def test_prediction_receipt_replays(self):
        committed = json.loads((HERE / "PREDICTIONS_V1.json").read_text())
        self.assertEqual(PRED.build_predictions(), committed)
        self.assertFalse(committed["outcomes_seen"])
        self.assertFalse(committed["scorer_exists"])
        self.assertFalse(committed["surface_remints_materialized"])

    def test_result_replays_without_prediction_implementation(self):
        committed = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(SCORE.build_result(), committed)
        self.assertFalse(committed["scorer_imports_prediction_implementation"])
        self.assertEqual(committed["status"], "PASS")

    def test_scorer_never_imports_prediction_module(self):
        src = (HERE / "score_v1.py").read_text()
        self.assertNotIn("import predict_v1", src)
        self.assertNotIn("from predict_v1", src)
        self.assertNotIn("PRED.build_predictions", src)

    def test_predictor_visible_rows_have_no_family_or_architecture_fields(self):
        payload = json.loads((HERE / "PREDICTIONS_V1.json").read_text())
        forbidden = {
            "family", "family_name", "architecture", "architecture_name",
            "phenotype", "donor_path", "donor_file", "measured", "outcome", "result",
        }
        for row in payload["cases"]:
            self.assertFalse(forbidden.intersection(row))


class IndependentSequenceOracleTests(unittest.TestCase):
    def test_all_residues_are_future_distinguishable(self):
        payload = json.loads((HERE / "PREDICTIONS_V1.json").read_text())
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        result_by_id = {row["case_id"]: row for row in result["cases"]}
        for row in payload["cases"]:
            if row["object_kind"] != "periodic_sequence_response":
                continue
            m = int(row["period"])
            a = int(row["accepted_residue"])
            signatures = []
            for residue in range(m):
                signatures.append(tuple(((residue + k) % m) == a for k in range(m)))
            self.assertEqual(len(set(signatures)), m)
            self.assertTrue(all(signatures[i] != signatures[j] for i, j in itertools.combinations(range(m), 2)))
            measured = result_by_id[row["case_id"]]["measured_remint_1"]
            self.assertEqual(measured["quotient_classes"], m)
            self.assertEqual(measured["minimal_recurrent_states"], m)
            self.assertFalse(measured["stateless_sufficient"])
            self.assertEqual(measured["state_first_cheaper_length"], m + 1)

    def test_current_symbol_negative_is_not_forced(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        neg = result["hostiles"]["current_symbol_only_negative"]
        self.assertTrue(neg["control_fired"])
        self.assertTrue(neg["stateless_sufficient"])


class IndependentCoefficientOracleTests(unittest.TestCase):
    def test_rank_and_free_coordinate_counts(self):
        payload = json.loads((HERE / "PREDICTIONS_V1.json").read_text())
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        result_by_id = {row["case_id"]: row for row in result["cases"]}
        for row in payload["cases"]:
            if row["object_kind"] != "finite_coefficient_identification":
                continue
            d = int(row["dimension"])
            grid = row["coefficient_grid"]
            basis = [tuple(1 if j == i else 0 for j in range(d)) for i in range(d)]
            self.assertEqual(independent_rank(basis[: d - 1]), d - 1)
            self.assertEqual(independent_rank(basis), d)
            dependent = basis[: d - 1] + [basis[0]]
            self.assertEqual(independent_rank(dependent), d - 1)
            measured = result_by_id[row["case_id"]]["measured_remint_1"]
            self.assertEqual(measured["consistent_after_d_minus_1_independent"], len(grid))
            self.assertEqual(measured["consistent_after_d_independent"], 1)
            self.assertEqual(measured["consistent_after_d_dependent"], len(grid))
            self.assertFalse(measured["dependent_d_identifies"])
            self.assertEqual(measured["identified_at_independent_n"], d)

    def test_full_basis_equals_boolean_table_by_independent_enumeration(self):
        payload = json.loads((HERE / "PREDICTIONS_V1.json").read_text())
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        result_by_id = {row["case_id"]: row for row in result["cases"]}
        for row in payload["cases"]:
            if row["object_kind"] != "finite_coefficient_identification":
                continue
            d = int(row["dimension"])
            subset_masks = list(range(1 << d))
            table_rows = list(itertools.product((0, 1), repeat=d))
            self.assertEqual(len(subset_masks), len(table_rows))
            measured = result_by_id[row["case_id"]]["measured_remint_2"]
            self.assertEqual(measured["full_boolean_monomial_basis_size"], len(subset_masks))
            self.assertEqual(measured["boolean_input_table_size"], len(table_rows))


class HostileAndBoundaryTests(unittest.TestCase):
    def test_all_registered_hostiles_fire(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        hostiles = result["hostiles"]
        self.assertTrue(hostiles["prediction_tamper"]["mismatch_detected"])
        self.assertTrue(hostiles["label_injection"]["rejected"])
        self.assertTrue(hostiles["current_symbol_only_negative"]["control_fired"])
        self.assertTrue(hostiles["dependent_observation_negative"]["all_registered_cases_remain_ambiguous"])

    def test_both_remints_match_and_agree(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertTrue(result["all_predictions_match"])
        self.assertTrue(result["all_surface_remints_invariant"])
        for row in result["cases"]:
            self.assertTrue(row["match_remint_1"])
            self.assertTrue(row["match_remint_2"])
            self.assertTrue(row["surface_remint_invariant"])
            self.assertEqual(row["measured_remint_1"], row["measured_remint_2"])

    def test_claim_ceiling_forbids_global_promotion(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(
            result["terminal"],
            "B1_PREOUTCOME_PREDICTION_CUSTODY_SUPPORTED_ON_TWO_FRESH_EXACT_FAMILY_REMINTS",
        )
        self.assertIn("B1_COMMON_PROTOCOL_CLOSED", result["nonclaims"])
        self.assertIn("KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE", result["nonclaims"])
        self.assertIn("REAL_REGIME_REPLICATION_COMPLETE", result["nonclaims"])
        self.assertIn("COMPLETE_GMI", result["nonclaims"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
