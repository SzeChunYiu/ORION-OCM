"""Authored failure-custody controls: no native calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from native_test import invoke

class CaptureFailureRecords(unittest.TestCase):
    def exercise(self, error, expected, stream):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "records"; root.mkdir()
            def fail(argv, **_):
                out = Path(argv[-1]); out.mkdir()
                (out / "partial.ndjson").write_bytes(b"retained partial")
                if isinstance(error, BaseException): raise error
                return error
            with patch.dict(os.environ, {"OCM_NATIVE_TEST_RECORD_DIR": str(root)}):
                with patch("native_test.subprocess.run", side_effect=fail):
                    with self.assertRaises(expected): invoke({"registered": "fixture"})
            captures = list(root.glob("capture-*"))
            self.assertEqual(len(captures), 1)
            record = captures[0]
            self.assertEqual((record / "out/partial.ndjson").read_bytes(), b"retained partial")
            self.assertEqual((record / "process.stdout").read_bytes(), stream)
            self.assertEqual(json.loads((record / "request.json").read_bytes()), {"registered": "fixture"})
            return json.loads((record / "process.json").read_bytes())

    def test_success_retains_identical_stream_and_result(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "records"; root.mkdir()
            def succeed(argv, **_):
                out = Path(argv[-1]); out.mkdir()
                (out / "result.json").write_bytes(b'{"terminal":"fixture"}')
                return subprocess.CompletedProcess(argv, 0, b'{"terminal":"fixture"}', b"")
            with patch.dict(os.environ, {"OCM_NATIVE_TEST_RECORD_DIR": str(root)}):
                with patch("native_test.subprocess.run", side_effect=succeed):
                    result, files = invoke({"registered": "fixture"})
            self.assertEqual(result, {"terminal": "fixture"})
            self.assertEqual(files["result.json"], (root / "capture-1/process.stdout").read_bytes())

    def test_nonzero_retains_request_streams_and_partial_artifact(self):
        rec = self.exercise(subprocess.CompletedProcess([], 2, b"rejected", b"error"), AssertionError, b"rejected")
        self.assertEqual(rec["returncode"], 2)
        self.assertEqual(rec["outcome"], "COMPLETED")

    def test_timeout_retains_available_partial_streams_without_cleanup_claim(self):
        rec = self.exercise(subprocess.TimeoutExpired([], 30, output=b"partial", stderr=b"err"),
                            subprocess.TimeoutExpired, b"partial")
        self.assertEqual(rec["outcome"], "TIMEOUT")
        self.assertIsNone(rec["returncode"])
        self.assertEqual(rec["cleanup"], "NOT_OBSERVED")

    def test_spawn_failure_retains_request_and_unknown_stream_availability(self):
        rec = self.exercise(OSError("fixture spawn refusal"), OSError, b"")
        self.assertEqual(rec["outcome"], "PROCESS_EXCEPTION")
        self.assertFalse(rec["stdout_available"])

if __name__ == "__main__": unittest.main()
