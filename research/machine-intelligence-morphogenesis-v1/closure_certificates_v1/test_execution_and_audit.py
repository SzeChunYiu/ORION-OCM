import copy
from itertools import product
import unittest
import claim_audit as audit
import execution_controls as control
from realizability_checks import ExactBitMemory


def receipt():
    return {"schema": "GMIK4NullAwareMeasuredResourceCellV5", "verdict": "THEORY_RED",
            "winner_candidate_id": "rival", "scalar_lifecycle_cost": 5,
            "winner_program_tokens": ["x"], "measured_property_vector": {"a": 1},
            "world_profile": {"scale": 1}, "search_digest": "a" * 64,
            "expressibility_witness": {"expressible": True, "scalar_lifecycle_cost": 10},
            "null_frontier": None}


class AuditTests(unittest.TestCase):
    def test_preserves_original_and_raw_red(self):
        raw = receipt(); before = copy.deepcopy(raw)
        out = audit.audit_receipt(raw)
        self.assertEqual(raw, before)
        self.assertEqual(out["source_receipt"], before)
        self.assertEqual(out["legacy_verdict"], "THEORY_RED")
        self.assertFalse(out["full_GMI_closure"])
        out["source_receipt"]["world_profile"]["scale"] = 9
        self.assertEqual(raw, before)

    def test_dominance_is_not_class_certificate(self):
        out = audit.audit_receipt(receipt())
        self.assertEqual(out["winner_observation"], "RECORDED_WINNER_BEATS_WITNESS")
        self.assertEqual(out["target_class_conclusion"], "UNRESOLVED_WITHOUT_VALID_CLASS_LOWER_BOUND")

    def test_claimed_certificates_cannot_promote(self):
        raw = receipt(); raw.update({"class_lower_bound": 9, "realization_verified": True,
                                    "full_GMI_closure": True})
        out = audit.audit_receipt(raw)
        self.assertFalse(out["full_GMI_closure"])
        self.assertIn("UNRESOLVED", out["real_machine_conclusion"])

    def test_green_keeps_only_registered_verdict(self):
        raw = receipt(); raw["verdict"] = "K4_RECOVERY_GREEN"
        out = audit.audit_receipt(raw)
        self.assertEqual(out["legacy_verdict"], "K4_RECOVERY_GREEN")
        self.assertFalse(out["full_GMI_closure"])

    def test_null_observation_preserved(self):
        raw = receipt(); raw["verdict"] = "THEORY_RED_NULL_DOMINATES"
        raw["null_frontier"] = {"best_admissible_null": {"scalar_lifecycle_cost": 1}}
        self.assertEqual(audit.audit_receipt(raw)["null_observation"], "REPORTED_NULL_BEATS_WITNESS")

    def test_missing_winners_never_prove_noninterference(self):
        raw = receipt(); raw["winner_candidate_id"] = raw["scalar_lifecycle_cost"] = None
        self.assertEqual(audit.compare_search_receipts(raw, raw), "INCONCLUSIVE_NO_WINNER")

    def test_complete_pair_is_only_paired_observation(self):
        self.assertEqual(audit.compare_search_receipts(receipt(), receipt()),
                         "OBSERVED_SEARCH_UNCHANGED_NOT_GENERAL_PROOF")

    def test_missing_projection_inconclusive(self):
        raw = receipt(); del raw["search_digest"]
        self.assertEqual(audit.compare_search_receipts(raw, raw), "INCONCLUSIVE_INCOMPLETE_SEARCH_PROJECTION")

    def test_search_change_detected(self):
        raw = receipt(); raw["scalar_lifecycle_cost"] = 4
        self.assertEqual(audit.compare_search_receipts(receipt(), raw), "OBSERVED_SEARCH_CHANGE")

    def test_tie_is_not_strict(self):
        raw = receipt(); raw["scalar_lifecycle_cost"] = 10
        self.assertEqual(audit.audit_receipt(raw)["winner_observation"], "NO_RECORDED_STRICT_WINNER_DOMINANCE")

    def test_bad_costs_and_nonfinite_extra_fields_fail(self):
        for value in (True, -1, float("nan"), float("inf"), "5", None):
            raw = receipt(); raw["scalar_lifecycle_cost"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): audit.audit_receipt(raw)
        raw = receipt(); raw["other"] = float("nan")
        with self.assertRaises(ValueError): audit.audit_receipt(raw)

    def test_unknown_schema_and_verdict_rejected(self):
        for key in ("schema", "verdict"):
            raw = receipt(); raw[key] = "invented"
            with self.assertRaises(ValueError): audit.audit_receipt(raw)

    def test_cost_without_winner_rejected(self):
        raw = receipt(); raw["winner_candidate_id"] = None
        with self.assertRaises(ValueError): audit.audit_receipt(raw)

    def test_early_inconclusive_schema_is_supported(self):
        raw = {"schema": "GMIK4MeasuredResourceCellV4", "verdict": "INCONCLUSIVE_GRAMMAR",
               "winner_candidate_id": None, "world_profile": None}
        self.assertEqual(audit.audit_receipt(raw)["noninterference_evidence"], "NO_WINNER")

    def test_protected_budget_is_rejected_before_import(self):
        for budget in (True, -1, 20_001, 1_000_000):
            with self.assertRaises(ValueError):
                audit.run_development_cell("x", "x", "w1", freeze={}, seed=17, budget=budget)


class ExecutionTests(unittest.TestCase):
    def test_all_programs_structural_certificate_matches_execution(self):
        programs = control.enumerate_programs(2)
        self.assertEqual(len(programs), 548)
        self.assertEqual(len({p.tokens() for p in programs}), 548)
        for p, x in product(programs, range(-4, 5)):
            observed, claimed = control.execute(p, x), control.certificate(p)
            for key in ("executed_steps", "temporary_peak_words", "retained_parameter_words", "description_tokens"):
                self.assertEqual(observed[key], claimed[key])

    def test_actual_output_controls(self):
        functions = (lambda x: x, lambda x: 1, lambda x: x*x, lambda x: 2*x+1)
        for fn in functions:
            out = control.search([(x, fn(x)) for x in range(-4, 5)])
            self.assertEqual(out["status"], "FINITE_CONTROL_WITNESS")
            self.assertTrue(out["exhaustive"])
            self.assertGreater(out["candidate_execution_work"], 0)

    def test_budget_and_no_winner_not_green(self):
        self.assertFalse(control.search([(0, 100)], budget=0)["exhaustive"])
        self.assertEqual(control.search([(0, 100)])["status"], "NO_CONTROL_WITNESS")

    def test_no_mutable_or_executable_duck_typed_ast(self):
        for args in ([], (object(), object())):
            with self.assertRaises(TypeError): control.Expr("+", args)

    def test_all_binary_memories_through_ten_records(self):
        queries = datasets = 0
        for n in range(11):
            for bits in product((0, 1), repeat=n):
                memory = ExactBitMemory.from_records(bits)
                self.assertTrue(n <= memory.payload_bits <= n+7)
                for i, bit in enumerate(bits):
                    self.assertEqual(memory.recall(i), bit); queries += 1
                datasets += 1
        self.assertEqual((datasets, queries), (2047, 18434))


class FiniteClassTests(unittest.TestCase):
    def test_computed_class_minimum_refutes_multiplication_for_identity(self):
        out = control.certify_finite_frontier([(x, x) for x in range(-2, 3)],
                                              target_uses_multiplication=True)
        self.assertEqual(out["status"], "FINITE_RIVAL_STRICTLY_BEATS_CLASS")
        self.assertLess(out["exact_rival_minimum"], out["exact_target_minimum"])
        self.assertEqual(out["domain_size"], 548)

    def test_target_change_cannot_change_stream_or_winner(self):
        data = [(x, x) for x in range(-2, 3)]
        a = control.certify_finite_frontier(data, target_uses_multiplication=True)
        b = control.certify_finite_frontier(data, target_uses_multiplication=False)
        self.assertEqual(a["domain_and_evaluation_sha256"], b["domain_and_evaluation_sha256"])
        self.assertEqual(a["global_winner_tokens"], b["global_winner_tokens"])
        self.assertNotEqual(a["status"], b["status"])

    def test_absent_class_is_not_development_failure(self):
        out = control.certify_finite_frontier([(x, x*x) for x in range(-2, 3)],
                                              target_uses_multiplication=False)
        self.assertEqual(out["status"], "FINITE_TARGET_CLASS_EMPTY")
        self.assertIsNone(out["exact_target_minimum"])

    def test_no_admissible_program_and_no_forged_budget(self):
        out = control.certify_finite_frontier([(0, 100)], target_uses_multiplication=False)
        self.assertIsNone(out["global_winner_tokens"])
        with self.assertRaises(TypeError):
            control.certify_finite_frontier([(0, 0)], target_uses_multiplication=False, budget=0)
        with self.assertRaises(ValueError):
            control.certify_finite_frontier([(0, 0)], target_uses_multiplication=1)


if __name__ == "__main__":
    unittest.main()
