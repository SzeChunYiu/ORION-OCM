"""Recorder attribution/interruption controls; mocked outcomes are not native evidence."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("environment_commission", HERE / "commission.py")
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
I = M.I
import commission_contract as K


def example():
    native = {"operation": "prepare", "terminal": "CANNOT_CHECK", "stage": "closure", "reason": "MISSING_REFERENCE x"}
    result = {**native, "native": native.copy(), "files": {}}
    process = {"returncode": 2, "error": None, "interrupted": False, "stderr_base64": "",
               "cleanup": {"reaped": True, "group_absent": True}}
    expected = {k: native[k] for k in ("terminal", "stage")}; expected["reason_contains"] = "MISSING_REFERENCE"
    return result, process, expected


def test_native_refusal_needs_complete_matching_host_evidence():
    result, process, expected = example()
    assert K.assess(result, process, expected, "prepare")
    for change in ({"evidence_complete": False}, {"files": None}, {"artifact_error": "symlink"},
                   {"stage": "custody_or_process"}, {"operation": "inspect"}, {"reason": "infrastructure failure"}):
        assert not K.assess({**result, **change}, process, expected, "prepare")
    altered = {**result, "native": {**result["native"], "operation": "inspect"}}
    assert not K.assess(altered, process, expected, "prepare")
    assert not K.assess(result, {**process, "interrupted": True}, expected, "prepare")


@pytest.mark.parametrize("phase,value", [("prepare", "KERNEL_PASS"), ("check", "PREPARED")])
def test_expectations_cannot_change_operation(phase, value):
    with pytest.raises(ValueError): K.expectation({"terminal": value, "stage": "x", "reason_contains": ""}, phase)


def matrix_fixture(tmp_path):
    packet = tmp_path / "packet"; packet.write_text("authored control")
    binding = M.record(packet)
    data = {"schema": "ocm.proof-environment.controls.v1", "scope": "AUTHORED_NATIVE_ENVIRONMENT_CONTROLS",
            "runtime": binding, "timeout_s": 1, "max_output_bytes": 1024,
            "cases": [{"id": "result.json", "purpose": "reserved names are isolated below cases/",
                       "prepare_freeze": binding, "prepare_expected": {"terminal": "PREPARED", "stage": "replay", "reason_contains": ""},
                       "checks": [{"candidate_packet": binding, "candidate_root": 0,
                                   "expected": {"terminal": "KERNEL_PASS", "stage": "kernel", "reason_contains": ""}}]}]}
    path = tmp_path / "matrix.json"; I.write_json(path, data)
    return path, I.file_record(path)["sha256"]


def bypass_validation_for_recorder_fixture(monkeypatch):
    monkeypatch.setattr(M, "sys", SimpleNamespace(flags=SimpleNamespace(isolated=True, no_site=True)))
    monkeypatch.setattr(M, "verify_matrix", lambda *args: None)


def test_interruption_preserves_fixed_denominator_and_reserved_case_name(tmp_path, monkeypatch):
    path, digest = matrix_fixture(tmp_path); bypass_validation_for_recorder_fixture(monkeypatch)
    def interrupted(*args): raise KeyboardInterrupt()
    monkeypatch.setattr(M, "launch", interrupted)
    root = tmp_path / "run"
    with pytest.raises(KeyboardInterrupt): M.commission(path, digest, root)
    result = I.parse_json((root / "result.json").read_bytes())
    assert result["terminal"] == "CONTROLS_FAILED" and result["evidence_complete"] is False
    assert result["denominator"] == 2 and result["passed"] == 0
    assert (root / "cases/result.json").is_dir() and (root / "seal.json").is_file()


def test_malformed_receipt_keeps_unexecuted_checks_in_denominator(tmp_path, monkeypatch):
    path, digest = matrix_fixture(tmp_path); bypass_validation_for_recorder_fixture(monkeypatch)
    monkeypatch.setattr(M, "launch", lambda *args: (None, {"receipt_error": "malformed"}, None))
    result = M.commission(path, digest, tmp_path / "run")
    assert result["terminal"] == "CONTROLS_FAILED" and result["denominator"] == 2
    assert result["controls"][1]["reason"] == "PREPARATION_NOT_QUALIFIED"


def test_final_nested_validation_failure_cannot_seal_success(tmp_path, monkeypatch):
    path, digest = matrix_fixture(tmp_path); bypass_validation_for_recorder_fixture(monkeypatch)
    calls = []
    def drift_on_final(*args):
        calls.append(1)
        if len(calls) == 2: raise ValueError("registered runtime source drift")
    monkeypatch.setattr(M, "verify_matrix", drift_on_final)
    monkeypatch.setattr(M, "launch", lambda *args: (None, {}, None))
    result = M.commission(path, digest, tmp_path / "run")
    assert result["terminal"] == "CONTROLS_FAILED" and result["evidence_complete"] is False
    assert "runtime source drift" in result["failure"]


def test_final_inventory_failure_refuses_even_after_passing_assessment(tmp_path, monkeypatch):
    path, digest = matrix_fixture(tmp_path); bypass_validation_for_recorder_fixture(monkeypatch)
    data = I.parse_json(path.read_bytes()); data["cases"][0]["checks"] = []
    data["cases"][0]["prepare_expected"] = example()[2]
    path.write_bytes(I.canonical(data)); digest = I.file_record(path)["sha256"]
    result, envelope, _ = example()
    monkeypatch.setattr(M, "launch", lambda *args: (result, envelope, None))
    original = I.inventory; calls = []
    def second_fails(root):
        calls.append(1)
        if len(calls) == 2: raise ValueError("final inventory unavailable")
        return original(root)
    monkeypatch.setattr(I, "inventory", second_fails)
    root = tmp_path / "run"; final = M.commission(path, digest, root)
    assert final["terminal"] == "CONTROLS_FAILED" and not final["evidence_complete"]
    assert I.parse_json((root / "result.json").read_bytes())["terminal"] == "PROVISIONAL_PASS_REQUIRES_COMPLETE_SEAL"
    assert I.parse_json((root / "seal.json").read_bytes())["terminal"] == "CONTROLS_FAILED"


def test_changed_issuer_is_not_reauthorized_for_later_check(tmp_path, monkeypatch):
    path, digest = matrix_fixture(tmp_path); bypass_validation_for_recorder_fixture(monkeypatch)
    data = I.parse_json(path.read_bytes()); data["cases"][0]["checks"] *= 2
    path.write_bytes(I.canonical(data)); digest = I.file_record(path)["sha256"]
    monkeypatch.setattr(M.C, "prepared_inputs", lambda *args: {})
    calls = []; issued_path = None
    def fake_launch(operation, freeze, output, matrix, log):
        nonlocal issued_path
        calls.append(operation); output.mkdir()
        terminal = "PREPARED" if operation == "prepare" else "KERNEL_PASS"
        stage = "replay" if operation == "prepare" else "kernel"
        native = {"operation": operation, "terminal": terminal, "stage": stage, "reason": ""}
        result = {**native, "native": native.copy(), "files": {}, "environment_id": "a" * 64}
        receipt_path = output / ("receipt.json" if operation == "prepare" else "check.json")
        I.write_json(receipt_path, result)
        if operation == "prepare": issued_path = receipt_path
        else: issued_path.write_bytes(b"consistently substituted issuer would need new authorization")
        envelope = {**example()[1], "returncode": 0}
        return result, envelope, M.record(receipt_path)
    monkeypatch.setattr(M, "launch", fake_launch)
    result = M.commission(path, digest, tmp_path / "run")
    assert calls == ["prepare", "check"]
    assert result["terminal"] == "CONTROLS_FAILED" and result["denominator"] == 3
    assert "binding differs" in result["failure"]
