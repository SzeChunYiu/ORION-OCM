"""Capture/manifest controls use stubs, never native search."""
import importlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
D = importlib.import_module("explicit_phase_diagnostic")


def packet(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "STUDY", tmp_path)
    prep = tmp_path / "preparation"; prep.mkdir()
    request = prep / "request.json"; request.write_text('{"fixed":true}')
    original = tmp_path / "old.json"
    original.write_text(json.dumps({"candidate_commands": {"E0": ["fixed", "/prior/clia_worker.py"]},
                                    "requests": {"E0": str(request)}}))
    bindings = {str(request): D.binding(request), str(original): D.binding(original)}
    monkeypatch.setattr(D, "required_bindings", lambda *args: bindings)
    manifest = {"schema": "ocm.explicit-phase-diagnostic.v1", "assignment": ["E0"],
                "bindings": dict(bindings), "baseline_manifest_sha256": D.sha(original),
                "baseline_manifest": str(original), "request": str(request),
                "argv": ["fixed", str(D.ROOT / "explicit_phase_worker.py")], "watchdog_s": 24,
                "output": str(tmp_path / "run-v1"), "cwd": str(D.ROOT)}
    p = prep / "manifest.json"; p.write_text(json.dumps(manifest)); return p, manifest


@pytest.mark.parametrize("change", ["assignment", "argv", "watchdog_s", "request_bytes", "bindings", "baseline_manifest_sha256", "cwd", "output"])
def test_drift_refuses_before_dispatch(tmp_path, monkeypatch, change):
    p, m = packet(tmp_path, monkeypatch)
    if change == "request_bytes": Path(m["request"]).write_text("changed")
    elif change == "bindings": m[change] = {}
    elif change in {"baseline_manifest_sha256", "cwd", "output"}: m[change] = "changed"
    else: m[change] = ["B"] if change == "assignment" else ["changed"] if change == "argv" else 25
    p.write_text(json.dumps(m)); calls = []
    monkeypatch.setattr(D, "capture_one", lambda *args: calls.append(args))
    with pytest.raises(ValueError): D.run(p, D.sha(p))
    assert calls == [] and not (tmp_path / "run-v1").exists()


def test_one_dispatch_create_only_output_and_raw_seal(tmp_path, monkeypatch):
    p, m = packet(tmp_path, monkeypatch); calls = []
    def capture(*args):
        calls.append(args); Path(args[2]).mkdir()
        (Path(args[2]) / "stderr").write_text("raw phase")
        return {"exit_code": 124, "pid": 1}
    monkeypatch.setattr(D, "capture_one", capture)
    result = D.run(p, D.sha(p))
    assert result["status"] == "RAW_CAPTURE_COMPLETE" and result["semantic_assessment"] == "NOT_GRADED"
    assert len(calls) == 1 and (Path(m["output"]) / "seal.json").is_file()
    with pytest.raises(FileExistsError): D.run(p, D.sha(p))
    assert len(calls) == 1


def test_post_dispatch_drift_preserves_failed_record_and_raw_seal(tmp_path, monkeypatch):
    p, m = packet(tmp_path, monkeypatch)
    def capture(*args):
        Path(args[2]).mkdir(); Path(m["request"]).write_text("changed")
        return {"exit_code": 124}
    monkeypatch.setattr(D, "capture_one", capture)
    result = D.run(p, D.sha(p))
    assert result["status"] == "RAW_CAPTURE_INCOMPLETE" and result["capture"]["exit_code"] == 124
    assert (Path(m["output"]) / "seal.json").is_file()


def test_unregistered_manifest_digest_refuses(tmp_path, monkeypatch):
    p, _ = packet(tmp_path, monkeypatch); calls = []
    monkeypatch.setattr(D, "capture_one", lambda *args: calls.append(args))
    with pytest.raises(ValueError): D.run(p, "0" * 64)
    assert calls == []
