"""Successor presentation controls; decode saved bytes without a native donor."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from later_consumption_capture import decode_result


@pytest.mark.parametrize("status", ["PASS", "FAIL", "SOLUTION"])
@pytest.mark.parametrize("reason", [None, "explicit native explanation"])
def test_completed_native_result_does_not_inherit_unavailable_reason(tmp_path, status, reason):
    value = {"status": status, "candidate": "(define-fun f () Int 1)",
             "metrics": {"worker_pid": 123}, "solver_result": "unsat"}
    if reason is not None:
        value["reason"] = reason
    (tmp_path / "stdout").write_text(json.dumps(value))
    got = decode_result(tmp_path, {"exit_code": 0, "pid": 123, "elapsed_ns": 100})
    assert got["status"] == status and got["native_invoked"] is True
    assert got["reason"] == ("" if reason is None else reason)
    assert got["solver_result"] == "unsat"
    assert got["metrics"]["envelope_wall_s"] == 1e-7


@pytest.mark.parametrize("raw", [
    "not JSON", "[]", '{}',
    '{"status":"PASS","metrics":{"worker_pid":true}}',
    '{"status":"SOLUTION","candidate":null,"metrics":{"worker_pid":123}}',
])
def test_malformed_native_result_remains_refusal(tmp_path, raw):
    (tmp_path / "stdout").write_text(raw)
    got = decode_result(tmp_path, {"exit_code": 0, "pid": 123})
    assert got["status"] == "CANNOT_CHECK" and got["native_invoked"] == "UNKNOWN"
    assert got["reason"].startswith("UNREADABLE_NATIVE_RESULT:")


def test_incomplete_native_result_keeps_reason_and_timeout_refuses(tmp_path):
    value = {"status": "CANNOT_CHECK", "metrics": {"worker_pid": 123}}
    (tmp_path / "stdout").write_text(json.dumps(value))
    assert decode_result(tmp_path, {"exit_code": 0})["reason"] == "native return unavailable"
    got = decode_result(tmp_path, {"exit_code": 124, "pid": 123})
    assert got["status"] == "CANNOT_CHECK"
    assert got["reason"] == "NATIVE_PROCESS_FAILED_OR_TIMEOUT"
