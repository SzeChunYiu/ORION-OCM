"""Protocol tests: OS-process restart, not in-process OCMRuntime reconstruction."""
from __future__ import annotations

from pathlib import Path
import json
import os
import tempfile
import unittest

import experiment as E


class TestPinnedSource(unittest.TestCase):
    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)
        self.assertEqual(E.METHOD_BLOB, "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3")

    def test_partition_is_small_and_disjoint(self):
        tasks = E.frozen_tasks()
        self.assertEqual(len(tasks["train"]), 2)
        self.assertEqual(len(tasks["admit"]), 2)
        self.assertEqual(len(tasks["fresh"]), 2)
        ids = [t.fingerprint for t in tasks["train"] + tasks["admit"] + tasks["fresh"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(E.TRAIN_PROGRAMS[0][:2], E.EXPECTED_FRAGMENT)


class TestRestartMechanism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_is_os_process_restart(self):
        self.assertEqual(self.result["terminal"], "OS_PROCESS_RESTART_HELD_OUT_SOLVE_SUPPORTED")
        self.assertNotEqual(self.result["terminal"], "CAUSAL_METHOD_REUSE_SUPPORTED")
        self.assertFalse(self.result["g24_complete"])
        self.assertTrue(self.result["g24_002_machine_process_restarts"]["earned"])
        self.assertTrue(all(self.result["criteria"].values()))

    def test_child_is_a_distinct_os_process(self):
        parent = self.result["process"]["pid"]
        child = self.result["os_process"]
        reconstruction = self.result["in_process_reconstruction"]
        self.assertNotEqual(child["pid"], parent)
        self.assertEqual(child["ppid"], parent)
        self.assertEqual(reconstruction["pid"], parent)
        self.assertFalse(reconstruction["sufficient_for_g24_002"])
        self.assertEqual(reconstruction["mechanism"], "IN_PROCESS_OCMRUNTIME_RECONSTRUCTION")
        self.assertEqual(child["load_status"], "LIVE")
        self.assertEqual(child["kso_state_hash"], self.result["parent_kso_state_hash"])

    def test_held_out_solve_invokes_reloaded_generator(self):
        rows = self.result["os_process"]["rows"]
        self.assertEqual(len(rows), 2)
        for row, primitive in zip(rows, self.result["primitive_fresh"]):
            self.assertTrue(row["verified"])
            self.assertEqual(row["origin"], "guided")
            self.assertTrue(row["fragment_used"])
            self.assertLess(row["slots"], primitive["slots"])
            self.assertNotIn(row["task"], self.result["partition"]["train_ids"])
            self.assertNotIn(row["task"], self.result["partition"]["admit_ids"])

    def test_revoked_and_empty_ledgers_do_not_serve(self):
        self.assertEqual(self.result["revoked_os_process"]["load_status"], "MISSING_OR_DEAD")
        self.assertEqual(self.result["empty_os_process"]["load_status"], "MISSING_OR_DEAD")
        self.assertNotEqual(self.result["revoked_os_process"]["pid"], self.result["process"]["pid"])
        self.assertNotEqual(self.result["empty_os_process"]["pid"], self.result["process"]["pid"])

    def test_spawn_helper_uses_subprocess_not_in_process_call(self):
        source = (Path(__file__).resolve().parent / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("subprocess.run", source)
        self.assertIn("--restart-consumer", source)
        self.assertIn("IN_PROCESS_OCMRUNTIME_RECONSTRUCTION", source)
        self.assertNotIn("CAUSAL_METHOD_REUSE_SUPPORTED\n", source)


class TestOrdinaryLibraryRoundTrip(unittest.TestCase):
    def test_ordinary_persist_matches_generator(self):
        method = E.M.GeneratorMethod((E.EXPECTED_FRAGMENT,), ("a", "b"))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            E.ordinary_persist(path, method)
            loaded = E.ordinary_load(path)
        self.assertEqual(loaded.fingerprint, method.fingerprint)
        self.assertEqual(loaded.fragments, (E.EXPECTED_FRAGMENT,))


class TestResultFileContract(unittest.TestCase):
    def test_committed_result_earns_only_the_restart_box(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.is_file():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(data["terminal"], "OS_PROCESS_RESTART_HELD_OUT_SOLVE_SUPPORTED")
        self.assertTrue(data["g24_002_machine_process_restarts"]["earned"])
        self.assertFalse(data["g24_complete"])
        self.assertNotEqual(data["os_process"]["pid"], data["process"]["pid"])
        self.assertEqual(data["in_process_reconstruction"]["pid"], data["process"]["pid"])
        self.assertNotEqual(os.getpid(), data["os_process"]["pid"])


if __name__ == "__main__":
    unittest.main()
