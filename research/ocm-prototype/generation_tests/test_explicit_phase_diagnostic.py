"""Capture/manifest controls use stubs, never native search."""
import importlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
D = importlib.import_module("explicit_phase_diagnostic")


def packet(tmp_path):
    request = tmp_path / "request.json"; request.write_text('{"fixed":true}')
    original = tmp_path / "old.json"
    original.write_text(json.dumps({"candidate_commands": {"E0": ["fixed", "/prior/clia_worker.py"]},
                                    "requests": {"E0": str(request)}}))
    manifest = {"schema": "ocm.explicit-phase-diagnostic.v1", "assignment": ["E0"],
                "bindings": {str(request): D.binding(request), str(original): D.binding(original)},
                "baseline_manifest": str(original), "request": str(request),
                "argv": ["fixed", str(D.ROOT / "explicit_phase_worker.py")], "watchdog_s": 24,
                "output": str(tmp_path / "run"), "cwd": str(tmp_path)}
    p = tmp_path / "manifest.json"; p.write_text(json.dumps(manifest)); return p, manifest


@pytest.mark.parametrize("change", ["assignment", "argv", "watchdog_s", "request_bytes"])
def test_drift_refuses_before_dispatch(tmp_path, monkeypatch, change):
    p, m = packet(tmp_path)
    if change == "request_bytes": Path(m["request"]).write_text("changed")
    else: m[change] = ["B"] if change == "assignment" else ["changed"] if change == "argv" else 25
    p.write_text(json.dumps(m)); calls = []
    monkeypatch.setattr(D, "capture_one", lambda *args: calls.append(args))
    with pytest.raises(ValueError): D.run(p)
    assert calls == [] and not Path(m["output"]).exists()


def test_one_dispatch_create_only_output_and_raw_seal(tmp_path, monkeypatch):
    p, m = packet(tmp_path); calls = []
    def capture(*args):
        calls.append(args); Path(args[2]).mkdir()
        (Path(args[2]) / "stderr").write_text("raw phase")
        return {"exit_code": 124, "pid": 1}
    monkeypatch.setattr(D, "capture_one", capture)
    result = D.run(p)
    assert result["status"] == "RAW_CAPTURE_COMPLETE" and result["semantic_assessment"] == "NOT_GRADED"
    assert len(calls) == 1 and (Path(m["output"]) / "seal.json").is_file()
    with pytest.raises(FileExistsError): D.run(p)
    assert len(calls) == 1


def test_post_dispatch_drift_preserves_failed_record_and_raw_seal(tmp_path, monkeypatch):
    p, m = packet(tmp_path)
    def capture(*args):
        Path(args[2]).mkdir(); Path(m["request"]).write_text("changed")
        return {"exit_code": 124}
    monkeypatch.setattr(D, "capture_one", capture)
    result = D.run(p)
    assert result["status"] == "RAW_CAPTURE_INCOMPLETE" and result["capture"]["exit_code"] == 124
    assert (Path(m["output"]) / "seal.json").is_file()
