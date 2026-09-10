"""Protocol tests for G3 source-bound real failure/probe incidents."""
from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import experiment as E
from ocm.kso.ids import evidence_id
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


class TestSourceBoundFailureProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe = E.run_square_invert_probe(E.REMAINING)

    def test_production_source_is_pinned(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)

    def test_predecessor_result_files_are_untouched_terminals(self):
        failmem = json.loads(E.G3_FAILMEM.read_text())
        repr_v1 = json.loads(E.G3_REPR.read_text())
        diag = json.loads(E.G3_DIAG.read_text())
        self.assertEqual(failmem["terminal"], "FAILURE_MEMORY_USEFUL_AT_SCOPE")
        self.assertEqual(repr_v1["terminal"], "PARENT_SUFFICIENT")
        self.assertEqual(
            repr_v1["successor_v2"]["terminal"],
            "REPRESENTATION_CHANGE_CAUSALLY_USEFUL",
        )
        self.assertEqual(
            diag["terminal"],
            "REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE",
        )
        self.assertTrue(diag["jump_refused_on_timeout"])
        competing = E.REPO / "research" / "g3-scoped-failure-memory-v1"
        # Present on origin/main, therefore on pull_request merge commits.
        # Absent on remaining-gates HEAD. Presence is not a scientific result
        # and this capsule must not create, overwrite, or retune that ecology.
        # The result-gating criterion is "no RESULT.json", which holds
        # vacuously when the directory is absent and by inspection when it
        # is present with protocol files only.
        text = Path(E.__file__).read_text()
        self.assertNotIn("FAILURE_MEMORY_NOT_USEFUL", text)
        self.assertNotIn("competing_scoped_failure_memory_absent", text)
        self.assertFalse((competing / "RESULT.json").is_file())

    def test_square_invert_of_one_plus_x_is_real_method_failure_not_timeout(self):
        self.assertEqual(M.normal_form(("inc",)), (Fraction(1), Fraction(1)))
        self.assertNotEqual(M.normal_form(("square",)), (Fraction(1), Fraction(1)))
        self.assertTrue(self.probe["odd_degree"])
        self.assertFalse(self.probe["invertible"])
        self.assertFalse(self.probe["timeout"])
        self.assertFalse(self.probe["jump"])
        self.assertEqual(self.probe["failure_kind"], "METHOD_FAILURE")
        self.assertEqual(self.probe["diagnosis"], "METHOD_FAILURE")

    def test_timeout_only_is_resource_bound_and_mutant_jumps(self):
        timeout = E.classify_timeout_only_probe()
        self.assertEqual(timeout["predicted"], "RESOURCE_BOUND")
        self.assertEqual(timeout["timeout_jump_parent"], "JUMP")
        self.assertTrue(timeout["jump_refused"])
        self.assertNotEqual(timeout["predicted"], "JUMP")

    def test_evidence_id_binds_payload_source_and_channel_not_task_id(self):
        payload = E.incident_payload(E.SOURCE_A, self.probe)
        eid_a = E.expected_evidence_id(payload, E.SOURCE_A)
        eid_b = E.expected_evidence_id(payload, E.SOURCE_B)
        self.assertNotEqual(eid_a, eid_b)
        self.assertNotEqual(eid_a, E.TASK_ALPHA)
        self.assertNotIn("task_id", payload)
        self.assertNotIn("task_id_lineage", payload)
        self.assertTrue(eid_a.startswith("ev:"))
        same = evidence_id(
            E.NAMESPACE,
            {"payload": payload, "source": E.SOURCE_A, "channel": Channel.EXPERIMENT.value},
        )
        self.assertEqual(eid_a, same)

    def test_failure_attempt_scope_is_source_not_task_id(self):
        payload = E.incident_payload(E.SOURCE_A, self.probe)
        eid = E.expected_evidence_id(payload, E.SOURCE_A)
        obj = E.make_failure_attempt(payload, eid, E.TASK_ALPHA)
        body = json.loads(E.emit(obj).decode())
        self.assertEqual(body["schema"], "ocm.g2.failure-attempt.v1")
        self.assertEqual(body["task_id"], E.TASK_ALPHA)
        self.assertEqual(body["failure_kind"], "METHOD_FAILURE")
        self.assertIn(f"source:{E.SOURCE_A}", body["scope"]["contexts"])
        self.assertIn(f"evidence:{eid}", body["scope"]["contexts"])
        self.assertNotEqual(body["scope"]["contexts"][0], body["task_id"])
        self.assertEqual(body["acquisition_lineage"]["discovery_evidence_id"], eid)

    def test_remaining_state_parent_cannot_isolate_source(self):
        incidents = [
            {"source": E.SOURCE_A, "remaining_sig": "1,1", "task_id_lineage": E.TASK_ALPHA, "live": True},
            {"source": E.SOURCE_B, "remaining_sig": "1,1", "task_id_lineage": E.TASK_ALPHA, "live": True},
        ]
        remaining = E.lookup_by_remaining(incidents, "1,1")
        by_a = E.lookup_by_source(incidents, E.SOURCE_A)
        by_beta = E.lookup_by_task_id(incidents, E.TASK_BETA)
        self.assertEqual(len(remaining), 2)
        self.assertEqual(len(by_a), 1)
        self.assertEqual(by_beta, [])

    def test_ledger_recovers_after_in_process_replay_and_revoke_kills_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            planted = E.plant_ledgers(Path(tmp), self.probe)
            live = OCMRuntime(planted["live_root"])
            recovered = E.recover_from_runtime(live)
            self.assertEqual(len(recovered), 2)
            sources = {row["source"] for row in recovered}
            self.assertEqual(sources, {E.SOURCE_A, E.SOURCE_B})
            a = E.lookup_by_source(recovered, E.SOURCE_A)[0]
            self.assertEqual(a["evidence_id"], planted["incident_a"]["evidence_id"])
            self.assertTrue(a["live"])
            self.assertNotEqual(a["evidence_id"], E.TASK_ALPHA)
            self.assertEqual(a["skip_key"], "source+evidence_id")
            self.assertTrue(E.use_source_incident(recovered, E.SOURCE_A)["used"])

            dead = OCMRuntime(planted["revoked_root"])
            revoked = E.recover_from_runtime(dead)
            a_dead = E.lookup_by_source(revoked, E.SOURCE_A)[0]
            b_live = E.lookup_by_source(revoked, E.SOURCE_B)[0]
            self.assertFalse(a_dead["live"])
            self.assertTrue(b_live["live"])
            self.assertFalse(E.use_source_incident(revoked, E.SOURCE_A)["used"])
            self.assertTrue(E.use_source_incident(revoked, E.SOURCE_B)["used"])

    def test_ordinary_json_ties_source_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            planted = E.plant_ledgers(Path(tmp), self.probe)
            ordinary = E.ordinary_load(planted["live_root"] / "incidents.json")
            runtime = E.recover_from_runtime(OCMRuntime(planted["live_root"]))
            self.assertEqual(
                [row["evidence_id"] for row in E.lookup_by_source(ordinary, E.SOURCE_A)],
                [row["evidence_id"] for row in E.lookup_by_source(runtime, E.SOURCE_A)],
            )

    def test_experiment_earns_source_bound_recovery_without_g3_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.run()
            out = Path(tmp) / "RESULT.json"
            out.write_text(json.dumps(result))
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["issue"], 165)
        self.assertFalse(result["programme_wide_g3_close"])
        self.assertFalse(result["production_src_edited"])
        self.assertTrue(result["g32_capsule_untouched"])
        self.assertTrue(result["jump_refused_on_timeout"])
        self.assertIn(result["terminal"], E.LEGAL_TERMINALS)
        self.assertNotEqual(result["os_process"]["pid"], result["process"]["pid"])
        self.assertEqual(result["os_process"]["ppid"], result["process"]["pid"])
        self.assertEqual(result["in_process_reconstruction"]["pid"], result["process"]["pid"])
        self.assertTrue(result["os_process"]["episode2_task_beta_source_A"]["used"])
        self.assertFalse(result["revoked_os_process"]["episode2_task_beta_source_A"]["used"])
        self.assertTrue(result["parents"]["task_id_memory"]["misses_new_episode"])
        self.assertTrue(result["parents"]["remaining_state_memory"]["conflates_source_A_and_B"])
        self.assertFalse(result["parents"]["representation_change"]["recovers_source_A"])
        self.assertIn("G3_PROGRAMME_WIDE_CLOSE", result["not_issued"])
        self.assertIn("JUMP", result["not_issued"])
        self.assertEqual(
            result["boxes"]["G3/recover-source-bound-real-failure-probe-incidents"]["key"],
            "source+evidence_id",
        )
        self.assertNotIn("competing_scoped_failure_memory_absent", result["criteria"])
        self.assertTrue(
            result["criteria"]["competing_scoped_failure_memory_v1_has_no_result_json"]
        )

    def test_capsule_does_not_patch_production_src(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.runtime.ocm_runtime import OCMRuntime", text)
        self.assertIn("from ocm.store.evidence import Channel", text)


class TestWrittenResultFreeze(unittest.TestCase):
    def test_written_result_matches_protocol_if_present(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertIn(data["terminal"], E.LEGAL_TERMINALS)
        self.assertFalse(data["programme_wide_g3_close"])
        self.assertTrue(data["jump_refused_on_timeout"])
        self.assertNotEqual(data["os_process"]["pid"], data["process"]["pid"])
        self.assertNotIn("competing_scoped_failure_memory_absent", data["criteria"])
        self.assertTrue(
            data["criteria"]["competing_scoped_failure_memory_v1_has_no_result_json"]
        )
        live = E.run()
        self.assertEqual(set(live["criteria"]), set(data["criteria"]))


if __name__ == "__main__":
    unittest.main()
