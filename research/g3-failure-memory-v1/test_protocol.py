import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g3_failure_memory", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
sys.modules["g3_failure_memory"] = E
SPEC.loader.exec_module(E)


class TestProspectiveFailureMemoryProtocol(unittest.TestCase):
    def test_production_source_is_pinned(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)
        self.assertEqual(E.git_blob_sha1(E.G2_PATH), E.G2_BLOB)

    def test_frozen_partitions_are_disjoint_declared_lengths_and_exclude_prior_length6(self):
        parts = E.frozen_partition()
        training, test = parts["training"], parts["test"]
        self.assertEqual((len(training), len(test)), (24, 16))
        ids = [task.fingerprint for task in training + test]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(parts["population"][t.fingerprint][0] == 5 for t in training))
        self.assertTrue(all(parts["population"][t.fingerprint][0] == 6 for t in test))
        self.assertFalse(parts["exposed6"] & {t.fingerprint for t in test})
        self.assertEqual(E.TRAIN_SALT, "orion-ocm-g3-failure-train-v1")
        self.assertEqual(E.TEST_SALT, "orion-ocm-g3-failure-test-v1")

    def test_remaining_signature_is_coefficients_not_task_id(self):
        program = ("inc", "double")
        coeffs = E.G2.M.normal_form(program)
        task = E.G2.M.PolynomialTask("label-must-not-be-the-key", coeffs)
        sig = E.remaining_signature(coeffs)
        self.assertNotEqual(sig, task.fingerprint)
        self.assertNotEqual(sig, task.task_id)
        self.assertEqual(sig, E.remaining_signature(task.coefficients))
        self.assertIn(",", sig)
        self.assertNotEqual(len(sig), 64)
        self.assertNotIn(task.fingerprint, sig)

    def test_skip_keys_never_include_task_identity(self):
        remaining = E.canonicalize((Fraction(1), Fraction(1)))
        memory = E.FailureMemory(policy="scoped")
        rec = memory.compact(
            "square", E.remaining_signature(remaining), E.budget_id(3), E.ENV_V1,
            "METHOD_FAILURE", "INVERT_IMPOSSIBLE", True, "square miss",
        )
        memory.remember(rec, task_fingerprint="must-not-appear-in-keys", root=True)
        exported = memory.export_records()
        self.assertEqual(exported[0]["remaining_sig"], E.remaining_signature(remaining))
        self.assertNotIn("task_id", exported[0])
        self.assertNotIn("task", exported[0])
        self.assertFalse(memory.keys_contain_task_id(["must-not-appear-in-keys"]))
        for key in memory.method_failures:
            self.assertNotIn("must-not-appear-in-keys", key)

    def test_method_failure_is_not_promoted_to_task_impossibility(self):
        remaining = E.canonicalize((Fraction(0), Fraction(2)))  # 2x: inc/dec miss, double succeeds
        self.assertIsNone(E.invert_method("square", remaining))
        self.assertEqual(E.invert_method("double", remaining), E.IDENTITY)
        memory = E.FailureMemory(policy="none")
        meter = E.Meter()
        outcome = E.solve_remaining(remaining, 1, memory, E.ENV_V1, meter, record=True)
        self.assertTrue(outcome.solved)
        root_sig = E.remaining_signature(remaining)
        root_kinds = {record["failure_kind"] for record in memory.records if record["remaining_sig"] == root_sig}
        self.assertIn("METHOD_FAILURE", root_kinds)
        self.assertNotIn("TASK_IMPOSSIBILITY", root_kinds)
        inc_fail = next(
            record for record in memory.records
            if record["method_id"] == "inc" and record["remaining_sig"] == root_sig
        )
        self.assertEqual(inc_fail["failure_kind"], "METHOD_FAILURE")

    def test_all_methods_exhausted_under_bound_may_be_task_impossibility(self):
        remaining = E.canonicalize((Fraction(1), Fraction(1)))
        memory = E.FailureMemory(policy="none")
        meter = E.Meter()
        outcome = E.solve_remaining(remaining, 0, memory, E.ENV_V1, meter, record=True)
        self.assertFalse(outcome.solved)
        self.assertEqual(outcome.kind, "TASK_IMPOSSIBILITY")
        self.assertTrue(any(r["failure_kind"] == "TASK_IMPOSSIBILITY" for r in memory.records))

    def test_scoped_skip_is_remaining_state_specific_not_global_method_ban(self):
        square_poly = E.G2.M.normal_form(("inc", "square"))
        linear = E.canonicalize((Fraction(1), Fraction(1)))
        memory = E.FailureMemory(policy="scoped")
        rec = memory.compact(
            "square", E.remaining_signature(linear), E.budget_id(3), E.ENV_V1,
            "METHOD_FAILURE", "INVERT_IMPOSSIBLE", True, "not a square",
        )
        memory.remember(rec, task_fingerprint=None, root=False)
        meter = E.Meter()
        blocked = memory.lookup_method("square", E.remaining_signature(linear), E.budget_id(3), E.ENV_V1, meter)
        open_elsewhere = memory.lookup_method(
            "square", E.remaining_signature(square_poly), E.budget_id(3), E.ENV_V1, meter,
        )
        self.assertIsNotNone(blocked)
        self.assertIsNone(open_elsewhere)
        inverted = E.invert_method("square", square_poly)
        self.assertEqual(inverted, E.canonicalize((Fraction(1), Fraction(1))))

    def test_reopen_retries_after_budget_raise_and_task_id_blacklist_does_not(self):
        task = E.G2.M.PolynomialTask("reopen", E.G2.M.normal_form(("inc",) * 5))
        tight = E.FailureMemory(policy="scoped")
        tight_row = E.solve_task(task, 4, tight, E.ENV_V1, record=True)
        self.assertFalse(tight_row["solved"])
        scoped = E.clone_memory(tight, policy="scoped")
        reopened = E.solve_task(task, 5, scoped, E.ENV_V1, record=False, reopen_from=tight)
        self.assertTrue(reopened["solved"])
        self.assertGreater(reopened["extra_retries"], 0)
        black = E.clone_memory(tight, policy="blacklist")
        blocked = E.solve_task(task, 5, black, E.ENV_V1, record=False)
        self.assertFalse(blocked["solved"])
        self.assertEqual(blocked["kind"], "BLACKLISTED")

    def test_overclaim_mutant_overprunes_a_solvable_remaining_state(self):
        remaining = E.canonicalize((Fraction(1), Fraction(1)))
        train = E.FailureMemory(policy="scoped")
        rec = train.compact(
            "square", E.remaining_signature(remaining), E.budget_id(2), E.ENV_V1,
            "METHOD_FAILURE", "INVERT_IMPOSSIBLE", True, "square miss",
        )
        train.remember(rec, task_fingerprint=None, root=False)
        scoped = E.clone_memory(train, policy="scoped")
        overclaim = E.clone_memory(train, policy="overclaim")
        scoped_row = E.solve_remaining(remaining, 2, scoped, E.ENV_V1, E.Meter(), record=False)
        over_row = E.solve_remaining(remaining, 2, overclaim, E.ENV_V1, E.Meter(), record=False)
        none_row = E.solve_remaining(remaining, 2, E.FailureMemory(policy="none"), E.ENV_V1, E.Meter(), record=False)
        self.assertTrue(none_row.solved)
        self.assertTrue(scoped_row.solved)
        self.assertFalse(over_row.solved)

    def test_tms_nogood_parent_matches_scoped_skip_keys(self):
        remaining = E.G2.M.normal_form(("inc", "dec", "double"))
        train = E.FailureMemory(policy="scoped")
        E.solve_remaining(remaining, 3, train, E.ENV_V1, E.Meter(), record=True)
        scoped = E.clone_memory(train, policy="scoped")
        tms = E.clone_memory(train, policy="scoped")
        task = E.G2.M.PolynomialTask("parent", remaining)
        a = E.solve_task(task, 3, scoped, E.ENV_V1, record=False)
        b = E.solve_task(task, 3, tms, E.ENV_V1, record=False)
        self.assertEqual(a["enumerations"], b["enumerations"])
        self.assertEqual(a["program"], b["program"])

    def test_backward_invert_roundtrips_registered_primitives(self):
        for program in [(), ("inc",), ("dec", "double"), ("inc", "square"), ("double", "inc", "dec")]:
            remaining = E.G2.M.normal_form(program)
            cursor = remaining
            for op in reversed(program):
                cursor = E.invert_method(op, cursor)
                self.assertIsNotNone(cursor)
            self.assertEqual(cursor, E.IDENTITY)

    def test_failure_attempt_v1_emits_and_keeps_remaining_state_in_scope(self):
        record = {
            "method_id": "square",
            "remaining_sig": "1,1",
            "budget": "max_length=4",
            "environment_version": E.ENV_V1,
            "failure_kind": "METHOD_FAILURE",
            "outcome": "INVERT_IMPOSSIBLE",
            "complete": True,
            "feedback": "method cannot produce this remaining polynomial",
        }
        obj = E.make_failure_attempt(record, task_id="lineage-only")
        payload = json.loads(E.emit(obj).decode())
        self.assertEqual(payload["schema"], "ocm.g2.failure-attempt.v1")
        self.assertEqual(payload["failure_kind"], "METHOD_FAILURE")
        self.assertEqual(payload["task_id"], "lineage-only")
        self.assertTrue(payload["scope"]["contexts"][0].startswith("remaining:"))
        self.assertEqual(payload["scope"]["contexts"][0], "remaining:1,1")
        self.assertNotEqual(payload["scope"]["contexts"][0], payload["task_id"])

    def test_ordinary_persistence_preserves_skip_records(self):
        records = [{
            "method_id": "inc",
            "remaining_sig": "2,1",
            "budget": "max_length=3",
            "environment_version": E.ENV_V1,
            "failure_kind": "METHOD_FAILURE",
            "outcome": "CONTINUATION_FAILED",
            "complete": True,
            "feedback": "residual unsolved",
        }]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "memory.json"
            E.ordinary_persist(path, records)
            loaded = E.ordinary_load(path)
        self.assertEqual(loaded, records)

    def test_ocm_memory_survives_restart_and_revocation_removes_authority(self):
        records = [{
            "method_id": "dec",
            "remaining_sig": "0,2",
            "budget": "max_length=2",
            "environment_version": E.ENV_V1,
            "failure_kind": "METHOD_FAILURE",
            "outcome": "CONTINUATION_FAILED",
            "complete": True,
            "feedback": "residual unsolved",
        }]
        training = {"schema": "test.training", "n": 1}
        utility = {"schema": "test.utility", "accepted": True}
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, _te, _ue = E.admit_memory(
                Path(temp) / "live", records, training, utility, revoke=False,
            )
            dead, _atom2, _te2, _ue2 = E.admit_memory(
                Path(temp) / "dead", records, training, utility, revoke=True,
            )
        self.assertEqual(live, records)
        self.assertIsNone(dead)


if __name__ == "__main__":
    unittest.main()
