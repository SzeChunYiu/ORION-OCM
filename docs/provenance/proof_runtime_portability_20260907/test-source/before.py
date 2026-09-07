"""Lifecycle acceptance controls: native worker/kernel boundaries are mocked."""
import hashlib
import json
import os
from pathlib import Path
import pytest
from test_closed_session import setup
import lifecycle as L
import lifecycle_replay as R

def load(path): return json.loads(Path(path).read_bytes())

@pytest.fixture
def case(setup, tmp_path, monkeypatch):
    _, calls, manifest = setup
    # Bound source sentinel keeps concurrent unrelated development out of mocked controls.
    sentinel = tmp_path / "source.py"; sentinel.write_text("trusted = True\n")
    monkeypatch.setattr(R, "source_files", lambda repo: {str(sentinel): R.sha(sentinel)})
    monkeypatch.setattr(R, "python_files", lambda executable: {str(Path(executable).resolve()): R.sha(executable)})
    def replay(directory, freeze, frozen_sha, executable):
        value = R.restore_status(directory, freeze, frozen_sha)
        return {"returncode": 0, "terminal": "COMPLETED", "result": value,
                "argv": [str(executable), "-I", "-S", "-B"], "wall_s": 0.01, "pid": os.getpid(),
                "cleanup": {"reaped": True, "group_absent": True}, "stderr": ""}
    monkeypatch.setattr(L, "replay", replay)
    monkeypatch.setattr(R, "bound_imports", lambda frozen: {})
    monkeypatch.setattr(L, "host_flags", lambda: {"isolated": 1, "no_site": 1, "dont_write_bytecode": 1}, raising=False)
    return manifest, hashlib.sha256(manifest.read_bytes()).hexdigest(), tmp_path / "run", calls, sentinel

def test_full_lifecycle_consumes_two_real_solve_routes_and_no_extra_checks(case):
    manifest, digest, out, calls, _ = case
    result = L.run(manifest, digest, out)
    assert result["terminal"] == "PROOF_RUNTIME_LIFECYCLE_COMMISSIONING_PASS", result
    assert [c[0] for c in calls] == ["worker", "checker"] * 2
    assert len(result["phases"]) == len(L.PHASES)
    assert [r["name"] for r in result["phases"]] == list(L.PHASES)
    assert all(r["passed"] for r in result["phases"])
    assert result["routes"][0]["run_evidence_id"] != result["routes"][1]["run_evidence_id"]
    assert result["outer_wall_s"] > 0 and result["bytes_before_result_write"] > 0
    for row in result["phases"]:
        saved = load(out / row["record"])
        assert saved["wall_s"] >= 0 and saved["passed"] is True
    phases = {r["name"]: load(out / r["record"]) for r in result["phases"]}
    assert phases["discovery_withdrawn"]["result"]["status"]["applicable"] is False
    assert phases["B_withdrawn_C_live"]["result"]["status"]["terminal"] == "LIVE"
    for name in ("cold_live", "cold_B_open", "cold_final"):
        child = phases[name]["result"]["result"]
        assert child["host_operators"] == [] and child["executable_operators"] == []
        assert child["session_bound"] is False and child["read_only"] is True

def test_bad_manifest_stops_before_session_and_preserves_failure(case):
    manifest, _, out, calls, _ = case
    r = L.run(manifest, "0" * 64, out)
    assert r["terminal"] == "CANNOT_CHECK" and not calls
    assert load(out / "result.json")["terminal"] == "CANNOT_CHECK"

def test_existing_destination_never_overwritten(case):
    manifest, digest, out, calls, _ = case
    out.mkdir(); (out / "keep").write_text("old")
    with pytest.raises(FileExistsError): L.run(manifest, digest, out)
    assert (out / "keep").read_text() == "old" and not calls

def test_wrong_status_cannot_create_success_receipt(case, monkeypatch):
    manifest, digest, out, calls, _ = case
    original = L.ProofRuntimeView.proof_status
    def wrong(self):
        result = original(self)
        if result["terminal"] == "LIVE": result["terminal"] = "OPEN"
        return result
    monkeypatch.setattr(L.ProofRuntimeView, "proof_status", wrong)
    r = L.run(manifest, digest, out)
    assert r["terminal"] == "CANNOT_CHECK" and [c[0] for c in calls] == ["worker", "checker"]
    assert any(not p["passed"] for p in r["phases"])

def test_post_dispatch_source_drift_preserves_returned_raw_value(case, monkeypatch):
    manifest, digest, out, calls, sentinel = case
    original = L.ProofRuntimeView.attempt
    def drift(self):
        result = original(self); sentinel.write_text("changed = True\n"); return result
    monkeypatch.setattr(L.ProofRuntimeView, "attempt", drift)
    r = L.run(manifest, digest, out)
    assert r["terminal"] == "CANNOT_CHECK" and len(calls) == 2
    row = load(out / r["phases"][-1]["record"])
    assert row["result"]["terminal"] == "ADMITTED" and "freeze" in row["reason"].lower()

def test_status_cannot_dispatch_or_mint_even_if_live(case, monkeypatch):
    manifest, digest, out, calls, _ = case
    original = L.ProofRuntimeView.proof_status
    def mint(self):
        if self.routes(): self.rt.admit_evidence({"fake": True}, "instruction", "status")
        return original(self)
    monkeypatch.setattr(L.ProofRuntimeView, "proof_status", mint)
    r = L.run(manifest, digest, out)
    assert r["terminal"] == "CANNOT_CHECK" and len(calls) == 2
    assert "status mutated" in r["reason"]

def test_nonzero_or_bound_replay_never_passes(case, monkeypatch):
    manifest, digest, out, calls, _ = case
    monkeypatch.setattr(L, "replay", lambda *args: {"returncode": 1, "terminal": "COMPLETED", "result": {
        "status": {"terminal": "LIVE"}, "session_bound": False, "host_operators": [],
        "executable_operators": [], "read_only": True}})
    r = L.run(manifest, digest, out)
    assert r["terminal"] == "CANNOT_CHECK" and len(calls) == 2

def test_freeze_tamper_refused_before_restoring(case):
    manifest, digest, out, calls, _ = case; out.mkdir()
    frozen, frozen_sha = R.make_freeze(L.REPO, manifest, digest, out, L.PYTHON)
    Path(frozen).write_bytes(Path(frozen).read_bytes() + b" ")
    with pytest.raises(ValueError, match="freeze"):
        R.restore_status(out, frozen, frozen_sha)
    assert not calls

@pytest.mark.parametrize("fault", ["cleanup", "pid", "rebind"])
def test_replay_process_evidence_must_match(case, monkeypatch, fault):
    manifest, digest, out, _, _ = case; original = L.replay
    def broken(*args):
        result = original(*args)
        if fault == "cleanup": result["cleanup"]["group_absent"] = False
        elif fault == "pid": result["result"]["pid"] += 1
        else: result["result"]["host_operators"] = ["invented"]
        return result
    monkeypatch.setattr(L, "replay", broken)
    r = L.run(manifest, digest, out)
    assert r["terminal"] == "CANNOT_CHECK"

@pytest.mark.parametrize("replacement", [["const", 99], ["const", False]])
def test_claim_route_must_match_actual_solve_candidate(case, monkeypatch, replacement):
    manifest, digest, out, _, _ = case; original = L.ProofRuntimeView.attempt
    def changed(self):
        result = original(self)
        result["solve"]["answer"]["candidate"] = replacement
        return result
    monkeypatch.setattr(L.ProofRuntimeView, "attempt", changed)
    assert L.run(manifest, digest, out)["terminal"] == "CANNOT_CHECK"

def test_cold_process_uses_declared_sources_and_no_callbacks(setup, tmp_path):
    create, calls, manifest = setup; out = tmp_path / "real-cold"; out.mkdir()
    frozen, digest = R.make_freeze(L.REPO, manifest, R.sha(manifest), out, L.PYTHON)
    session = create(); rt = L.OCMRuntime(out / "ocm")
    view = L.ProofRuntimeView.create(rt, session, out / "issuer")
    assert view.attempt()["terminal"] == "ADMITTED"; session.close()
    result = R.replay(out, frozen, digest, L.PYTHON)
    assert result["returncode"] == 0, result
    assert result["result"]["status"]["terminal"] == "LIVE"
    assert result["result"]["host_operators"] == [] and result["result"]["read_only"]
    assert result["result"]["pid"] == result["pid"]
    assert result["result"]["imports_bound"] is True
    assert result["cleanup"] == {"reaped": True, "group_absent": True}
    assert len(calls) == 2

def test_unclean_child_stderr_cannot_pass(case, monkeypatch):
    manifest, digest, out, _, _ = case; original = L.replay
    def noisy(*args):
        result = original(*args); result["stderr"] = "unexpected warning"; return result
    monkeypatch.setattr(L, "replay", noisy)
    assert L.run(manifest, digest, out)["terminal"] == "CANNOT_CHECK"

def test_unisolated_parent_refused_before_session(case, monkeypatch):
    manifest, digest, out, calls, _ = case
    monkeypatch.setattr(L, "host_flags", lambda: {"isolated": 0, "no_site": 0, "dont_write_bytecode": 0}, raising=False)
    result = L.run(manifest, digest, out)
    assert result["terminal"] == "CANNOT_CHECK" and not calls

@pytest.mark.parametrize("error", [KeyboardInterrupt(), RuntimeError("pipe failure")])
def test_replay_interruption_reaps_and_retains_envelope(tmp_path, monkeypatch, error):
    class Child:
        pid = 987654321; returncode = None; alive = True; calls = 0
        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls == 1: raise error
            self.returncode = -9; return b"partial output", b"retained stderr"
        def poll(self): return self.returncode
        def wait(self, timeout=None): self.returncode = -9; return self.returncode
    child = Child()
    def kill(pid, sig):
        assert pid == child.pid
        if not child.alive: raise ProcessLookupError
        child.alive = False
    monkeypatch.setattr(R, "verify_freeze", lambda *a: {"python_executable": str(L.PYTHON.resolve())})
    monkeypatch.setattr(R.subprocess, "Popen", lambda *a, **kw: child)
    monkeypatch.setattr(R.os, "killpg", kill)
    result = R.replay(tmp_path, tmp_path / "freeze", "f" * 64, L.PYTHON)
    assert result["terminal"] != "COMPLETED" and result["pid"] == child.pid
    assert result["cleanup"] == {"reaped": True, "group_absent": True}
    assert result["stdout"] == "partial output" and result["stderr"] == "retained stderr"
