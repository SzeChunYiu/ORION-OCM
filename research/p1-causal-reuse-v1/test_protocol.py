"""Protocol tests: P1 causal reuse via G2 macro + OS-process restart."""
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
        self.assertEqual(E.G2.METHOD_BLOB, E.METHOD_BLOB)

    def test_partition_is_tiny_and_disjoint(self):
        tasks = E.frozen_tasks()
        self.assertEqual(len(tasks["train"]), 2)
        self.assertEqual(len(tasks["admit"]), 2)
        self.assertEqual(len(tasks["fresh"]), 2)
        ids = [t.fingerprint for t in tasks["train"] + tasks["admit"] + tasks["fresh"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_g2_macro_serving_is_imported_not_forked(self):
        source = (Path(__file__).resolve().parent / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("g2-macro-operator-v1", source)
        self.assertIn("G2.admit_macro", source)
        self.assertIn("G2.build_search_index", source)
        self.assertIn("subprocess.run", source)
        self.assertIn("--restart-consumer", source)
        self.assertNotIn("CAUSAL_METHOD_REUSE_SUPPORTED\n", source)


class TestTinyCausalReuse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = E.run()

    def test_terminal_earns_remaining_p1_boxes(self):
        self.assertEqual(self.result["terminal"], "P1_CAUSAL_REUSE_SUPPORTED_AT_POLYNOMIAL_MICROSCOPE")
        self.assertNotEqual(self.result["terminal"], "CAUSAL_METHOD_REUSE_SUPPORTED")
        self.assertFalse(self.result["g24_complete"])
        self.assertTrue(all(self.result["criteria"].values()))
        self.assertEqual(self.result["p1_boxes_earned"], list(E.P1_BOXES))
        for box in E.P1_BOXES:
            self.assertTrue(self.result["p1_boxes"][box]["earned"], box)

    def test_child_is_a_distinct_os_process(self):
        parent = self.result["process"]["pid"]
        child = self.result["os_process"]
        reconstruction = self.result["in_process_reconstruction"]
        self.assertNotEqual(child["pid"], parent)
        self.assertEqual(child["ppid"], parent)
        self.assertEqual(reconstruction["pid"], parent)
        self.assertFalse(reconstruction["sufficient_for_p1_restart"])
        self.assertEqual(reconstruction["mechanism"], "IN_PROCESS_OCMRUNTIME_RECONSTRUCTION")
        self.assertEqual(child["load_status"], "LIVE")
        self.assertEqual(child["kso_state_hash"], self.result["parent_kso_state_hash"])

    def test_fresh_solve_uses_reloaded_macro_and_saves_attempts(self):
        rows = self.result["os_process"]["rows"]
        self.assertEqual(len(rows), 2)
        for row, primitive in zip(rows, self.result["primitive_fresh"]):
            self.assertTrue(row["verified"])
            self.assertTrue(row["macro_used"])
            self.assertLess(row["enumeration_attempts"], primitive["enumeration_attempts"])
            self.assertNotIn(row["task"], self.result["partition"]["train_ids"])
            self.assertNotIn(row["task"], self.result["partition"]["admit_ids"])

    def test_method_removal_falls_back_to_primitive(self):
        self.assertEqual(self.result["revoked_os_process"]["load_status"], "MISSING_OR_DEAD")
        self.assertEqual(self.result["empty_os_process"]["load_status"], "MISSING_OR_DEAD")
        self.assertTrue(E.rows_match(
            self.result["revoked_os_process"]["rows"],
            self.result["primitive_fresh"],
        ))
        self.assertTrue(E.rows_match(
            self.result["empty_os_process"]["rows"],
            self.result["primitive_fresh"],
        ))
        self.assertFalse(any(row["macro_used"] for row in self.result["revoked_os_process"]["rows"]))
        self.assertNotEqual(self.result["revoked_os_process"]["pid"], self.result["process"]["pid"])
        self.assertNotEqual(self.result["empty_os_process"]["pid"], self.result["process"]["pid"])

    def test_ordinary_persistent_parent_matches_ocm_live(self):
        self.assertTrue(self.result["os_process"]["ordinary_library_matches"])
        self.assertTrue(E.rows_match(
            self.result["os_process"]["rows"],
            self.result["ordinary_fresh"],
        ))
        self.assertEqual(
            self.result["p1_boxes"]["P1/011-strongest_persistent_parent"]["residual_vs_ordinary"],
            "none",
        )

    def test_admitted_method_is_scoped_and_training_derived(self):
        self.assertEqual(self.result["admission"]["scope"], E.SCOPE_NAME)
        self.assertEqual(self.result["admission"]["kind"], "macro.operator.v1")
        self.assertEqual(self.result["learned_macro"], ["inc", "square"])
        self.assertGreaterEqual(self.result["tournament"]["selected"]["support"], 2)


class TestOrdinaryLibraryRoundTrip(unittest.TestCase):
    def test_ordinary_persist_matches_macro(self):
        macro = ("inc", "square")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            E.G2.ordinary_persist(path, macro)
            loaded = E.G2.ordinary_load(path)
        self.assertEqual(loaded, macro)


class TestResultFileContract(unittest.TestCase):
    def test_committed_result_earns_the_seven_remaining_p1_boxes(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.is_file():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(data["terminal"], "P1_CAUSAL_REUSE_SUPPORTED_AT_POLYNOMIAL_MICROSCOPE")
        self.assertEqual(data["p1_boxes_earned"], list(E.P1_BOXES))
        self.assertFalse(data["g24_complete"])
        self.assertNotEqual(data["os_process"]["pid"], data["process"]["pid"])
        self.assertEqual(data["in_process_reconstruction"]["pid"], data["process"]["pid"])
        self.assertNotEqual(os.getpid(), data["os_process"]["pid"])
        self.assertTrue(all(data["criteria"].values()))


if __name__ == "__main__":
    unittest.main()
