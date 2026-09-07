"""Driver result/issuer controls. Mocked dispatch is never native commissioning."""
import base64
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import env_dispatch as D
import env_inputs as I


def response(root, operation="check", terminal="KERNEL_PASS"):
    root.mkdir()
    value = {"schema": "ocm.proof-environment.result.v1", "operation": operation, "terminal": terminal,
             "stage": "kernel", "reason": "fixture", "stats": {"checked": 1},
             "dependencies": [], "axioms": [], "files": ["result.json"]}
    I.write_json(root / "result.json", value)
    process = {"terminal": "COMPLETED", "returncode": 0, "timed_out": False, "output_truncated": False,
               "cleanup": {"reaped": True, "group_absent": True},
               "stderr_base64": "",
               "stdout_base64": base64.b64encode(I.canonical(value)).decode()}
    return value, process


def test_structured_response_needs_complete_process_and_matching_bytes(tmp_path):
    value, process = response(tmp_path / "native")
    assert D.native_result(process, tmp_path / "native", "check") == value
    with pytest.raises(ValueError, match="stderr"):
        D.native_result({**process, "stderr_base64": base64.b64encode(b"unexpected diagnostic").decode()},
                        tmp_path / "native", "check")
    for key, changed in (("terminal", "TIMEOUT"), ("returncode", 1), ("timed_out", True), ("output_truncated", True)):
        with pytest.raises(ValueError, match="envelope"):
            D.native_result({**process, key: changed}, tmp_path / "native", "check")
    for key in ("reaped", "group_absent"):
        altered = {**process, "cleanup": {**process["cleanup"], key: False}}
        with pytest.raises(ValueError, match="envelope"): D.native_result(altered, tmp_path / "native", "check")
    altered = {**value, "terminal": "REJECTED"}
    process["stdout_base64"] = base64.b64encode(I.canonical(altered)).decode()
    with pytest.raises(ValueError, match="disagreement"): D.native_result(process, tmp_path / "native", "check")


def test_partial_or_additional_outputs_cannot_authorize_environment(tmp_path):
    _, process = response(tmp_path / "native", "prepare", "PREPARED")
    with pytest.raises(ValueError, match="output files"):
        D.native_result(process, tmp_path / "native", "prepare")
    _, process2 = response(tmp_path / "native2")
    (tmp_path / "native2/private-proof.ndjson").write_text("must not become part of a checked result")
    with pytest.raises(ValueError, match="output files"):
        D.native_result(process2, tmp_path / "native2", "check")


@pytest.mark.parametrize("field,value", [("operation", "prepare"), ("terminal", "PARSED"),
                                        ("stats", {"checked": True}), ("axioms", ["a", "a"])])
def test_invalid_native_claim_shape_refused(tmp_path, field, value):
    data, process = response(tmp_path / "native")
    data[field] = value; (tmp_path / "native/result.json").write_bytes(I.canonical(data))
    process["stdout_base64"] = base64.b64encode(I.canonical(data)).decode()
    with pytest.raises(ValueError): D.native_result(process, tmp_path / "native", "check")


def test_issuer_change_prevents_passing_receipt_seal(tmp_path, monkeypatch):
    input_file = tmp_path / "packet"; input_file.write_text("packet fixture")
    records = {role: {"path": str(input_file), **I.file_record(input_file)} for role in D.OPERATIONS["check"]}
    runtime_file = tmp_path / "runtime.json"; I.write_json(runtime_file, {"fixture": True})
    runtime_hash = I.file_record(runtime_file)["sha256"]
    monkeypatch.setattr(D, "verify_runtime", lambda *args: ({}, []))
    monkeypatch.setattr(D, "source_inventory", lambda: {"fixture": "unit test only"})
    def mocked_execute(runtime, mounts, request, work, inputs, **kwargs):
        _, process = response(work / "native")
        return process
    monkeypatch.setattr(D, "execute", mocked_execute)
    def revoked(): raise ValueError("issuer changed during native call")
    root = tmp_path / "attempt"; root.mkdir()
    I.write_json(root / "freeze.json", {"unit_test_only": True})
    result = D.invoke("check", records, root, runtime_file, runtime_hash, candidate_root=0, verify_issuer=revoked)
    sealed = I.parse_json((root / "receipt.json").read_bytes())
    assert result["terminal"] == sealed["terminal"] == "CANNOT_CHECK"
    assert "issuer changed" in sealed["reason"]
    assert sealed["native"] is None


def test_catchable_interruption_retains_incomplete_nonpassing_record(tmp_path, monkeypatch):
    input_file = tmp_path / "packet"; input_file.write_text("packet fixture")
    records = {role: {"path": str(input_file), **I.file_record(input_file)} for role in D.OPERATIONS["check"]}
    runtime_file = tmp_path / "runtime.json"; I.write_json(runtime_file, {"fixture": True})
    runtime_hash = I.file_record(runtime_file)["sha256"]
    monkeypatch.setattr(D, "verify_runtime", lambda *args: ({}, []))
    monkeypatch.setattr(D, "source_inventory", lambda: {})
    def interrupted(*args, **kwargs): raise KeyboardInterrupt()
    monkeypatch.setattr(D, "execute", interrupted)
    root = tmp_path / "attempt"; root.mkdir()
    I.write_json(root / "freeze.json", {"unit_test_only": True})
    with pytest.raises(KeyboardInterrupt):
        D.invoke("check", records, root, runtime_file, runtime_hash, candidate_root=0)
    receipt = I.parse_json((root / "receipt.json").read_bytes())
    assert receipt["terminal"] == "CANNOT_CHECK"
    assert receipt["evidence_complete"] is False
    assert receipt["process"] is None


def test_actual_module_origin_is_checked(monkeypatch):
    import env_runtime as R
    monkeypatch.setattr(I, "__file__", "/unregistered/env_inputs.py")
    with pytest.raises(ImportError, match="origin"): R.verify_imports()


def test_nonregular_output_still_preserves_refusal_receipt(tmp_path, monkeypatch):
    packet = tmp_path / "packet"; packet.write_text("fixture")
    records = {role: {"path": str(packet), **I.file_record(packet)} for role in D.OPERATIONS["check"]}
    runtime = tmp_path / "runtime"; runtime.write_text("runtime fixture")
    monkeypatch.setattr(D, "verify_runtime", lambda *args: ({}, []))
    monkeypatch.setattr(D, "source_inventory", lambda: {})
    def linked_output(runtime, mounts, request, work, inputs, **kwargs):
        _, process = response(work / "native")
        (work / "native/private").symlink_to(tmp_path / "not-a-mount")
        return process
    monkeypatch.setattr(D, "execute", linked_output)
    root = tmp_path / "attempt"; root.mkdir(); I.write_json(root / "freeze.json", {"fixture": True})
    result = D.invoke("check", records, root, runtime, I.file_record(runtime)["sha256"], candidate_root=0)
    sealed = I.parse_json((root / "receipt.json").read_bytes())
    assert result["terminal"] == sealed["terminal"] == "CANNOT_CHECK"
    assert sealed["files"] is None and sealed["evidence_complete"] is False
    assert {"path": "execution/native/private", "kind": "symlink"} in sealed["artifact_diagnostics"]


def test_large_integer_counter_preserves_exact_finite_value(tmp_path):
    data, process = response(tmp_path / "native")
    data["stats"]["large_integer"] = 10 ** 400
    (tmp_path / "native/result.json").write_bytes(I.canonical(data))
    process["stdout_base64"] = base64.b64encode(I.canonical(data)).decode()
    assert D.native_result(process, tmp_path / "native", "check")["stats"]["large_integer"] == 10 ** 400
