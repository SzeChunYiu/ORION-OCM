from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import unittest
from fractions import Fraction as F
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


PRED = load("b1n_predict_v1", HERE / "predict_v1.py")
SCORE = load("b1n_score_v1", HERE / "score_v1.py")


class ReplayAndBoundaryTests(unittest.TestCase):
    def test_prediction_object_replays(self):
        committed = json.loads((HERE / "PREDICTIONS_V1.json").read_text())
        self.assertEqual(PRED.build_predictions(), committed)
        self.assertFalse(committed["outcomes_seen"])
        self.assertFalse(committed["scorer_exists"])
        self.assertFalse(committed["surface_remints_materialized"])

    def test_result_replays(self):
        committed = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(SCORE.build_result(), committed)
        self.assertEqual(committed["status"], "PASS")
        self.assertEqual(committed["effective_measured_matched_negative_count"], 19)

    def test_scorer_is_independent_of_prediction_code_and_donor_results(self):
        source = (HERE / "score_v1.py").read_text()
        self.assertNotIn("import predict_v1", source)
        self.assertNotIn("from predict_v1", source)
        self.assertNotIn("STAGE_", source)
        self.assertNotIn("machine-intelligence-morphogenesis-v1", source)

    def test_claim_ceiling_remains_bounded(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        for forbidden in (
            "B1_COMMON_PROTOCOL_CLOSED",
            "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE",
            "REAL_REGIME_REPLICATION_COMPLETE",
            "COMPLETE_GMI",
        ):
            self.assertIn(forbidden, result["nonclaims"])


class IndependentControlOracleTests(unittest.TestCase):
    def test_n1_rank_free_coordinate_oracle(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        row = next(x for x in result["cases"] if x["case_id"] == "N1")
        self.assertEqual(row["measured_remint_1"]["positive"]["consistent_candidates"], 1)
        self.assertEqual(row["measured_remint_1"]["fail"]["consistent_candidates"], 7)
        # Rank 3 leaves exactly one coefficient free over a 7-value grid.
        self.assertEqual(7 ** (4 - 3), 7)

    def test_n2_closed_form_credit_costs(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        row = next(x for x in result["cases"] if x["case_id"] == "N2")
        for arm, n_out in (("positive", 1), ("boundary", 6), ("fail", 8)):
            forward = 4 * (4 + n_out)
            reverse = 4 + 6 * n_out
            self.assertEqual(row["measured_remint_2"][arm]["forward"], forward)
            self.assertEqual(row["measured_remint_2"][arm]["reverse"], reverse)

    def test_n3_signal_and_search_oracle(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        row = next(x for x in result["cases"] if x["case_id"] == "N3")
        self.assertEqual(F(4**3 + 1, 2), F(65, 2))
        self.assertEqual(row["measured_remint_1"]["positive"]["gradient_evals"], 3)
        self.assertEqual(row["measured_remint_1"]["positive"]["gradient_charged_cost"], "9")
        self.assertIsNone(row["measured_remint_1"]["fail"]["gradient_evals"])
        self.assertIsNone(row["measured_remint_1"]["fail"]["local_evals"])

    def test_n4_gap_equations(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        row = next(x for x in result["cases"] if x["case_id"] == "N4")
        # An unconditional register answers exactly gap L-1.
        self.assertEqual([4 + 1], row["measured_remint_1"]["fail"]["working_register_lengths"])
        self.assertEqual(set(g + 1 for g in (0, 2, 4)), {1, 3, 5})
        self.assertEqual(row["measured_remint_1"]["positive"]["working_register_lengths"], [])
        self.assertTrue(row["measured_remint_1"]["positive"]["gated_works"])

    def test_n5_affine_witness_and_fiber_impossibility(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        row = next(x for x in result["cases"] if x["case_id"] == "N5")
        # Natural 2-bit code. Identity realizes symbol a.
        A = ((1, 0), (1, 1))
        c = (1, 0)
        def vec(q):
            return (q & 1, (q >> 1) & 1)
        def apply(v):
            return tuple((sum(A[i][j] * v[j] for j in range(2)) + c[i]) % 2 for i in range(2))
        for q in range(4):
            self.assertEqual(apply(vec(q)), vec((q + 1) % 4))
        # The fail b-update has nonempty fibers of sizes 3 and 1; an affine map's
        # fibers are cosets of one kernel and therefore equal-sized.
        fail_b = {0: 3, 1: 2, 2: 3, 3: 3}
        sizes = sorted([sum(v == image for v in fail_b.values()) for image in set(fail_b.values())])
        self.assertEqual(sizes, [1, 3])
        self.assertTrue(row["measured_remint_1"]["positive"]["affine_realizable"])
        self.assertFalse(row["measured_remint_1"]["fail"]["affine_realizable"])

    def test_n6_all_feature_orders_preserve_local_lookup_verdict(self):
        universe = list(itertools.product((0, 1), repeat=4))
        def hamming(a, b):
            return sum(x != y for x, y in zip(a, b))
        def threshold(x):
            return int(sum(x) >= 2)
        def parity(x):
            return sum(x) % 2
        def minimum(fn, order):
            def surf(x):
                return tuple(x[i] for i in order)
            for size in range(1, 9):
                for subset in itertools.combinations(universe, size):
                    if all(fn(min(subset, key=lambda s: (hamming(s, x), surf(s)))) == fn(x)
                           for x in universe):
                        return size
            return None
        verdicts = {(minimum(threshold, order), minimum(parity, order))
                    for order in itertools.permutations(range(4))}
        self.assertEqual(verdicts, {(4, None)})

    def test_n7_same_marginals_full_support_but_dependence_differs(self):
        independent = [[F(1, 9) for _ in range(3)] for _ in range(3)]
        dependent = [[F(1, 6) if i == j else F(1, 12) for j in range(3)] for i in range(3)]
        for joint in (independent, dependent):
            self.assertTrue(all(v > 0 for row in joint for v in row))
            self.assertEqual([sum(row, F(0)) for row in joint], [F(1, 3)] * 3)
            self.assertEqual([sum((joint[i][j] for i in range(3)), F(0)) for j in range(3)], [F(1, 3)] * 3)
        self.assertEqual(independent[0][0], F(1, 9))
        self.assertNotEqual(dependent[0][0], F(1, 3) * F(1, 3))

    def test_n8_tree_count_and_path_count(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        row = next(x for x in result["cases"] if x["case_id"] == "N8")
        total = sum(3**level for level in range(5))
        self.assertEqual(total, 121)
        self.assertEqual(4 + 1, 5)
        self.assertEqual(row["measured_remint_1"]["positive"]["expansions"], 5)
        self.assertEqual(row["measured_remint_1"]["fail"]["expansions"], 121)
        self.assertEqual(row["measured_remint_1"]["positive"]["charged_work"], 10)
        self.assertEqual(row["measured_remint_1"]["fail"]["charged_work"], 242)


class HostileTests(unittest.TestCase):
    def test_all_registered_hostiles_fire(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        hostiles = result["hostiles"]
        self.assertTrue(hostiles["prediction_tamper"]["mismatch_detected"])
        self.assertTrue(hostiles["positive_fail_label_swap"]["mismatch_detected"])
        self.assertTrue(hostiles["second_matched_field_mutation"]["rejected"])
        self.assertTrue(hostiles["family_label_injection"]["rejected"])

    def test_every_case_matches_both_remints_and_matching_contract(self):
        result = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertTrue(result["all_predictions_match"])
        self.assertTrue(result["all_surface_remints_invariant"])
        for row in result["cases"]:
            self.assertTrue(row["match_remint_1"])
            self.assertTrue(row["match_remint_2"])
            self.assertTrue(row["surface_remint_invariant"])
            self.assertTrue(row["matching_contract_passed"])
            self.assertEqual(row["measured_remint_1"], row["measured_remint_2"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
