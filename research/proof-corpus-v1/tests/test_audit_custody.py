import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from helpers import api, wrapper, solution
from git_fixture import repository
from test_audit import files


class AuditCustodyControls(unittest.TestCase):
    def test_invalid_utf8_refuses_one_row_and_accounts_for_remaining_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = files()
            source.update({"Theorems/Thm_B.lean": b"\xff", "P2M/Sol/S_B.lean": solution()})
            pin = repository(base / "repo", source)
            report = api("corpus_audit").run_audit(base / "repo", base / "out",
                                                 commit=pin, expected_count=2)
            self.assertEqual(report["terminal"], "CANNOT_CHECK_LEXICAL_COVERAGE")
            self.assertEqual(report["rows_accounted"]["wrappers"]["unread"], 0)
            self.assertEqual(report["rows_accounted"]["solutions"]["accepted"], 2)
            rows = json.loads((base / "out/WRAPPERS.json").read_text())
            self.assertEqual(rows["B"]["failure_code"], "SOURCE_UTF8")

    def test_actual_audit_source_drift_does_not_publish_success(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pin = repository(base / "repo", files())
            module = api("corpus_audit")
            with patch.object(module, "code_inventory", side_effect=[{"a": "before"}, {"a": "after"}]):
                report = module.run_audit(base / "repo", base / "out", commit=pin, expected_count=1)
            self.assertEqual(report["terminal"], "CANNOT_CHECK_SOURCE_DRIFT")
            self.assertEqual(json.loads((base / "out/REPORT.json").read_text())["failure_code"],
                             "SOURCE_DRIFT")

    def test_partial_blob_failure_has_unread_rows_instead_of_silent_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pin = repository(base / "repo", files())
            module = api("corpus_audit")
            original = module.Snapshot.blobs

            def interrupted(snapshot):
                stream = original(snapshot)
                try:
                    yield next(stream)
                    raise api("corpus_contract").CorpusError("SOURCE_BLOB_TRUNCATED")
                finally:
                    stream.close()

            with patch.object(module.Snapshot, "blobs", interrupted):
                report = module.run_audit(base / "repo", base / "out", commit=pin, expected_count=1)
            self.assertEqual(report["failure_code"], "SOURCE_BLOB_TRUNCATED")
            counts = report["rows_accounted"]
            self.assertEqual(sum(c["examined"] for c in counts.values()), 1)
            self.assertEqual(sum(c["listed"] for c in counts.values()),
                             sum(c["examined"] + c["unread"] for c in counts.values()))

    def test_costs_include_initial_and_final_source_hashing(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pin = repository(base / "repo", files())
            module = api("corpus_audit")
            clock = [0.0]

            def measured_inventory():
                clock[0] += 10.0
                return {"fixture.py": "stable"}

            with patch.object(module, "code_inventory", measured_inventory), patch(
                    "corpus_receipt.time.perf_counter", side_effect=lambda: clock[0]):
                report = module.run_audit(base / "repo", base / "out", commit=pin, expected_count=1)
            self.assertEqual(report["resources"]["wall_seconds"], 20.0)

    def test_wrong_expected_pair_count_is_not_a_syntax_success(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pin = repository(base / "repo", files())
            report = api("corpus_audit").run_audit(base / "repo", base / "out",
                                                 commit=pin, expected_count=2)
            self.assertEqual(report["failure_code"], "PAIR_COVERAGE")


if __name__ == "__main__":
    unittest.main()
