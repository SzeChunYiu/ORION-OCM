from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "af_barrier_context_v1.py"
SPEC = importlib.util.spec_from_file_location("af_barrier_context_v1", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load AF module")
af = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = af
SPEC.loader.exec_module(af)


class AFBarrierContextTests(unittest.TestCase):
    def test_registered_census(self):
        self.assertEqual(len(af.PROVENANCE_TAGS), 8)
        self.assertEqual(len(af.BARRIER_STATUSES), 10)
        self.assertNotIn("SOLVED_FOREVER", af.BARRIER_STATUSES)

    def test_null_condition_hierarchy_is_exact(self):
        self.assertEqual(
            [r["id"] for r in af.NULL_CONDITION_HIERARCHY],
            [
                "NO_SENSORY_OBSERVATIONS",
                "NO_REWARD_OR_EVALUATOR_FEEDBACK",
                "NO_TASK_SPECIFIC_DATA",
                "NO_EXTERNAL_INTERACTION",
                "NO_ENDOGENOUS_RANDOMNESS",
                "NO_TASK_SPECIFIC_INITIALIZATION",
                "ABSOLUTE_REGISTERED_NULL_EXCEPT_SUBSTRATE_AND_DYNAMICS",
            ],
        )

    def test_main_result_green(self):
        r = af.run()
        self.assertEqual(r["status"], "GREEN")
        self.assertEqual(r["af1"]["f1_same_current_score"], "1/2")
        self.assertEqual(r["af1"]["f1_system_b_capability_set"], ["1/2"])
        self.assertTrue(r["af3"]["mandatory_overhead_hostile"]["reversal"])

    def test_oracle_provenance_is_mandatory(self):
        with self.assertRaises(ValueError):
            af.classify_information_case(
                target_correlated_import=True,
                initial_target_information=False,
                random_novelty=False,
                capability_gain=True,
                consumed_provenance=("ENDOGENOUS_COMPUTE",),
            )

    def test_target_correlated_initial_advice_is_imported(self):
        self.assertEqual(
            af.classify_information_case(
                target_correlated_import=True,
                initial_target_information=True,
                random_novelty=False,
                capability_gain=True,
                consumed_provenance=("INITIAL_OR_INHERITED_ORGANIZATION",),
            ),
            "IMPORTED_INFORMATION_OR_ADVICE",
        )

    def test_f7_problem_contracts_are_not_crosswired(self):
        rows = {r["id"]: r for r in af.make_transition_records()}
        self.assertEqual(rows["F7_LIST_OUTPUT"]["source_context"]["Q"], rows["F7_LIST_OUTPUT"]["target_context"]["Q"])
        self.assertEqual(rows["F7_ORACLE_RELATIVIZATION"]["source_context"]["Q"], rows["F7_ORACLE_RELATIVIZATION"]["target_context"]["Q"])
        self.assertNotEqual(rows["F7_LIST_OUTPUT"]["source_context"]["V"], rows["F7_LIST_OUTPUT"]["target_context"]["V"])

    def test_random_novelty_not_target_information(self):
        joint = {(t, r): 0.25 for t in (0, 1) for r in (0, 1)}
        self.assertEqual(af.mutual_information_bits(joint), 0.0)
        self.assertEqual(
            af.classify_information_case(
                target_correlated_import=False,
                initial_target_information=False,
                random_novelty=True,
                capability_gain=False,
                consumed_provenance=("STOCHASTIC_VARIATION",),
            ),
            "RANDOM_NOVELTY_WITHOUT_TARGET_ALIGNMENT",
        )

    def test_unknown_provenance_fails_closed(self):
        with self.assertRaises(ValueError):
            af.classify_information_case(
                target_correlated_import=False,
                initial_target_information=False,
                random_novelty=True,
                capability_gain=False,
                consumed_provenance=("MAGIC_TARGET_HINT",),
            )

    def test_barrier_unknown_status_fails(self):
        rec = af.make_transition_records()[0].copy()
        rec["target_status"] = "SOLVED"
        with self.assertRaises(ValueError):
            af.validate_barrier_transition(rec)

    def test_barrier_missing_residual_fails(self):
        rec = af.make_transition_records()[0].copy()
        rec["nearest_residual_barrier"] = ""
        with self.assertRaises(ValueError):
            af.validate_barrier_transition(rec)

    def test_solved_forever_fails(self):
        rec = af.make_transition_records()[0].copy()
        rec["terminal"] = "SOLVED_FOREVER"
        with self.assertRaises(ValueError):
            af.validate_barrier_transition(rec)

    def test_changed_premise_cannot_be_broke(self):
        rec = af.make_transition_records()[1].copy()
        rec.update(
            terminal="BROKE_TURING",
            claims_literal_contradiction=True,
            contradiction_verified=True,
            transition_classes=["LITERAL_CONTRADICTION"],
        )
        with self.assertRaises(ValueError):
            af.validate_barrier_transition(rec)

    def test_literal_contradiction_requires_same_contracts(self):
        rec = af.make_transition_records()[0].copy()
        rec.update(
            terminal="BROKE_PARENT",
            claims_literal_contradiction=True,
            contradiction_verified=True,
            transition_classes=["LITERAL_CONTRADICTION"],
            retained_premises=rec["original_premises"],
            same_problem_contract=True,
            same_output_contract=False,
        )
        with self.assertRaises(ValueError):
            af.validate_barrier_transition(rec)

    def test_parent_pin_drift_fails(self):
        ledger = json.loads((Path(__file__).resolve().parent / "GMI_BARRIER_PARENT_LEDGER_V1.json").read_text())
        ledger["repository_pins"]["HST_THEOREM_REGISTRY_V1"]["blob_sha"] = "deadbeef"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ledger.json"
            p.write_text(json.dumps(ledger))
            with self.assertRaises(ValueError):
                af.validate_parent_ledger(p)

    def test_possibility_is_not_reachability(self):
        frozen = af.gamma_profiles("C0", {}, {})
        reached = {p["machine"] for p in frozen}
        self.assertIn("NOT", af.POLICIES)
        self.assertNotIn("NOT", reached)


if __name__ == "__main__":
    unittest.main()
