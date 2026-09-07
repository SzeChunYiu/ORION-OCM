"""Session protocol controls; native process boundaries are mocked, never launched."""
import hashlib
import json
from pathlib import Path
import pytest
import closed_session as C


def digest(value): return hashlib.sha256(value).hexdigest()
def raw(value): return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


@pytest.fixture
def setup(tmp_path, monkeypatch):
    runtime = {"lean_root": str(tmp_path / "lean"), "lean_files": {},
               "python": {"directory": str(tmp_path / "python"), "files": {}, "python_sha256": "0" * 64},
               "shared_libraries": {"files": {}, "mounts": []}, "preparation_wall_s": 1.5}
    (tmp_path / "lean").mkdir(); (tmp_path / "python").mkdir()
    manifest = tmp_path / "manifest.json"; manifest.write_bytes(raw(runtime))
    calls = []
    def worker(argv, **kwargs):
        calls.append(("worker", argv, kwargs))
        value = {"status": "FOUND", "candidate": ["const", 0], "reason": "proposal only",
                 "counters": {"applications": 1}, "limits": dict(C.dispatch.LIMITS), "used_constants": [0],
                 "worker_audit": {"schema": "mechanical-worker-audit-v1", "guard_sealed": True,
                    "prohibited_events": [], "imported_modules": [
                        {"name": n, "origin": "/app/" + n + ".py"}
                        for n in ("worker_guard", "f0_terms", "f0_search")],
                    "constant_occurrences": {"proof_term": {"0": 1}, "type_annotations": {}}}}
        inputs = next(Path(h) for h, g in kwargs["read_only"] if g == "/input")
        value["limits"].update(json.loads((inputs / "task.json").read_bytes()).get("limits", {}))
        return {"terminal": "COMPLETED", "returncode": 0, "stderr": "", "stdout": json.dumps(value),
                "wall_s": .1, "pid": 123, "cleanup": {"reaped": True, "group_absent": True}}
    def checker(stage, lean, mounts, **kwargs):
        calls.append(("checker", stage, kwargs))
        (Path(stage["directory"]) / "Candidate.olean").write_bytes(b"mock compiled")
        return {"terminal": "KERNEL_PASS", "reason": "", "stage": stage, "axioms": [],
                "fresh_kernel_replay": True, "compiled_proof_sha256": digest(b"mock compiled"), "phases": []}
    monkeypatch.setattr(C.D, "run_isolated", worker)
    monkeypatch.setattr(C.D, "check_staged", checker)
    def create(name="session", **kw):
        return C.ProofSession(manifest, digest(manifest.read_bytes()), tmp_path / name, **kw)
    return create, calls, manifest


def proposal(session): return session.propose(raw(session.task), session.task_sha256)
def accepted(session):
    p = proposal(session); return p, session.check(p)


def test_separate_callbacks_and_exact_worker_mount_closure(setup):
    create, calls, _ = setup; s = create(); p = proposal(s)
    assert s.readiness["terminal"] == "READY" and p["status"] == "FOUND"
    assert [c[0] for c in calls] == ["worker"]
    app = next(Path(h) for h, g in calls[0][2]["read_only"] if g == "/app")
    assert {p.name for p in app.iterdir()} == {"worker.py", "worker_guard.py", "f0_terms.py", "f0_search.py"}
    h = s.check(p)
    assert [c[0] for c in calls] == ["worker", "checker"]
    assert s.authentic_for(h, s.task_sha256, h["candidate_sha256"], s.environment_id)
    assert s.bindings["runtime_sha256"] and s.bindings["source_files"]
    assert Path(h["record_path"]).is_file()


@pytest.mark.parametrize("field,value", [("goal", ["sort", 0]), ("constants", {"0": ["sort", 0]})])
def test_fixed_descriptor_is_not_caller_defined(setup, field, value):
    create, calls, _ = setup; s = create(); task = s.task; task[field] = value
    bad = create("changed", task=task)
    assert bad.readiness["terminal"] == "CANNOT_CHECK" and not calls
    assert proposal(bad)["status"] == "CANNOT_CHECK"


def test_injected_constant_and_noncanonical_id_refused(setup):
    create, calls, _ = setup; s = create()
    for i, key in enumerate(("99", "00")):
        task = s.task; task["constants"][key] = task["goal"]
        assert create(str(i), task=task).readiness["terminal"] == "CANNOT_CHECK"
    assert not calls


def test_digest_mismatch_refused_before_dispatch(setup):
    create, calls, _ = setup; s = create()
    p = s.propose(raw(s.task), "0" * 64)
    assert p["status"] == "CANNOT_CHECK" and "registered" in p["reason"] and not calls


@pytest.mark.parametrize("change", ["candidate", "environment_id", "task_sha256", "record_path"])
def test_changed_proposal_cannot_invoke_checker(setup, change):
    create, calls, _ = setup; s = create(); p = proposal(s)
    p[change] = ["const", 1] if change == "candidate" else "changed"
    assert s.check(p)["terminal"] == "CANNOT_CHECK"
    assert [c[0] for c in calls] == ["worker"]


def test_fake_cross_session_and_closed_handles_refused(setup):
    create, _, _ = setup; s = create(); _, h = accepted(s); other = create("other")
    args = (s.task_sha256, h["candidate_sha256"], s.environment_id)
    assert not other.authentic_for(h, *args)
    fake = dict(h, run_id="forged"); assert not s.authentic_for(fake, *args)
    s.close(); assert not s.authentic_for(h, *args)


@pytest.mark.parametrize("where", ["record", "candidate", "snapshot", "manifest"])
def test_changed_custody_invalidates_issued_handle(setup, where):
    create, _, manifest = setup; s = create(); _, h = accepted(s)
    path = {"record": Path(h["record_path"]), "candidate": Path(h["record_path"]).parent / "checker/candidate.json",
            "snapshot": next((s.root / "source-snapshot").rglob("*.py")), "manifest": manifest}[where]
    path.write_bytes(path.read_bytes() + b" ")
    assert not s.authentic_for(h, s.task_sha256, h["candidate_sha256"], s.environment_id)


def test_proposal_record_drift_prevents_checker(setup):
    create, calls, _ = setup; s = create(); p = proposal(s)
    Path(p["record_path"]).write_text("{}")
    assert s.check(p)["terminal"] == "CANNOT_CHECK" and len(calls) == 1


def test_manifest_mismatch_and_missing_environment_are_retained(setup):
    create, calls, manifest = setup; s = create(); task = s.task
    wrong = C.ProofSession(manifest, "0" * 64, s.root.parent / "wrong", task=task)
    assert wrong.readiness["terminal"] == "CANNOT_CHECK" and not calls
    manifest.unlink(); missing = C.ProofSession(manifest, "0" * 64, s.root.parent / "missing")
    assert "FileNotFoundError" in missing.readiness["reason"]
    assert (missing.root / "session.json").is_file()


def test_attempt_roots_are_create_only(setup):
    create, _, _ = setup; create()
    with pytest.raises(FileExistsError): create()


def test_undeclared_candidate_dependency_is_refused(setup, monkeypatch):
    create, calls, _ = setup; initial = create(); task = initial.task
    task["constants"] = {"0": task["constants"]["0"]}; s = create("eq", task=task)
    original = C.D.run_isolated
    def injected(*a, **kw):
        record = original(*a, **kw); p = json.loads(record["stdout"])
        p.update(candidate=["const", 1], used_constants=[1])
        p["worker_audit"]["constant_occurrences"]["proof_term"] = {"1": 1}
        record["stdout"] = json.dumps(p); return record
    monkeypatch.setattr(C.D, "run_isolated", injected)
    p = proposal(s)
    assert p["status"] == "CANNOT_CHECK" and "permitted" in p["reason"]
    assert s.check(p)["terminal"] == "CANNOT_CHECK" and len(calls) == 1


def test_runtime_drift_after_dispatch_and_false_kernel_pass_fail_closed(setup, monkeypatch):
    create, _, _ = setup; s = create(); original = C.D.run_isolated
    def changed(*a, **kw):
        record = original(*a, **kw); (s.root.parent / "python" / "extra").write_text("drift"); return record
    monkeypatch.setattr(C.D, "run_isolated", changed)
    assert proposal(s)["status"] == "CANNOT_CHECK"
    (s.root.parent / "python" / "extra").unlink()
    monkeypatch.setattr(C.D, "run_isolated", original)
    second = create("third"); p = proposal(second)
    monkeypatch.setattr(C.D, "check_staged", lambda *a, **kw: {"terminal": "KERNEL_PASS"})
    result = second.check(p)
    assert result["terminal"] == "CANNOT_CHECK" and "incomplete native" in result["reason"]


@pytest.mark.parametrize("fault", ["extra_metadata", "limits", "boolean_pid", "post_check_source"])
def test_protocol_metadata_cannot_substitute_for_bound_native_data(setup, monkeypatch, fault):
    create, _, _ = setup; s = create(); original = C.D.run_isolated
    def malformed(*a, **kw):
        r = original(*a, **kw); p = json.loads(r["stdout"])
        if fault == "extra_metadata": p["environment_id"] = "forged"
        if fault == "limits": p["limits"] = {"max_terms": 1000000}
        if fault == "boolean_pid": r["pid"] = True
        r["stdout"] = json.dumps(p); return r
    monkeypatch.setattr(C.D, "run_isolated", malformed)
    if fault == "post_check_source":
        checker = C.D.check_staged
        def changed(stage, *a, **kw):
            r = checker(stage, *a, **kw)
            (Path(stage["directory"]) / "Target.lean").write_text("changed")
            return r
        monkeypatch.setattr(C.D, "check_staged", changed)
        assert s.check(proposal(s))["terminal"] == "CANNOT_CHECK"
    else:
        assert proposal(s)["status"] == "CANNOT_CHECK"


def test_refused_descriptor_and_readiness_cost_are_preserved(setup):
    create, calls, _ = setup; original = create(); task = original.task
    task["goal"] = ["sort", 0]
    refused = create("refused", task=task)
    assert json.loads((refused.root / "requested-descriptor.json").read_bytes()) == task
    assert refused.readiness["terminal"] == "CANNOT_CHECK" and not calls
    assert "cost_scope" in refused.readiness
