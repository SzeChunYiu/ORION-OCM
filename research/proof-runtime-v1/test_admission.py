"""Admission authenticity and complete-body hostile controls; no native dispatch."""
from dataclasses import replace
from pathlib import Path
import json
import pytest
from test_closed_session import setup
from test_adapter import view
from session_bindings import canonical
from route_data import encoded, hashed
from route_plan import make_plan
from ocm.runtime.ocm_runtime import OCMRuntime
from adapter import ProofRuntimeView
from ocm.kso.types import Scope


def issued(v):
    p = v.session.propose(canonical(v.session.task), v.session.task_sha256)
    return p, v.session.check(p)


@pytest.mark.parametrize("field", ["candidate", "proposal_id", "record_path", "counters"])
def test_changed_returned_proposal_refused(view, field):
    v, _, _ = view; p, h = issued(v)
    p[field] = ["const", 1] if field == "candidate" else {} if field == "counters" else "changed"
    with pytest.raises(ValueError): v.admit_checked(p, h)
    assert not v.routes()


@pytest.mark.parametrize("field", ["environment_id", "task_sha256", "record_sha256", "run_id"])
def test_changed_handle_refused(view, field):
    v, _, _ = view; p, h = issued(v); h[field] = "changed"
    with pytest.raises(ValueError): v.admit_checked(p, h)
    assert not v.routes()


def test_cross_session_and_closed_session_are_not_authority(view):
    v, _, create = view; p, h = issued(v); s = v.session
    v.bind(create("other"))
    with pytest.raises(ValueError): v.admit_checked(p, h)
    v.bind(s); s.close()
    with pytest.raises(ValueError): v.admit_checked(p, h)
    assert not v.routes()


def test_existing_evidence_id_with_changed_policy_cannot_be_reused(view):
    v, _, _ = view; p, h = issued(v); plan = make_plan(v, p, h)
    spec = plan["evidence"][0]; payload = spec["event_payload"]
    _, eid = v.rt.admit_evidence(payload["payload"], payload["channel"], payload["source"],
                                scope=Scope.of("wrong"))
    assert eid == spec["id"]
    with pytest.raises(ValueError, match="already exists"): v.admit_checked(p, h)
    assert not v.routes()


def test_changed_complete_atom_body_not_just_short_content_hash(view):
    v, _, _ = view; v.attempt(); p = v.routes()[0]["plan"]
    atom = v.rt.state.ks.atom(p["claim_id"])
    mutant = replace(atom, meta=atom.meta + (("forged", True),))
    assert atom.content_hash() == mutant.content_hash()
    v.rt.state.ks = replace(v.rt.state.ks, atoms=tuple(mutant if a.atom_id == atom.atom_id else a
                                                     for a in v.rt.state.ks.atoms))
    assert v.proof_status()["terminal"] == "CANNOT_CHECK"


def test_missing_artifact_is_not_repaired_by_recovery(view):
    v, calls, _ = view
    v.fault = lambda s: (_ for _ in ()).throw(RuntimeError("stop")) if s == "prepared" else None
    with pytest.raises(RuntimeError): v.attempt()
    plan = v.routes()[0]["plan"]; Path(plan["artifacts"][0]["path"]).unlink(); count = len(calls)
    fresh = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    with pytest.raises(ValueError, match="artifact"): fresh.recover(plan["run_id"])
    assert fresh.proof_status()["terminal"] == "CANNOT_CHECK" and len(calls) == count
    assert not any(a.atom_id == plan["claim_id"] for a in fresh.rt.state.ks.atoms)


def test_stale_runtime_instance_cannot_dispatch_or_serve(view):
    v, calls, _ = view
    other = OCMRuntime(v.rt.root); other.admit_evidence({"new": True}, "instruction", "other")
    with pytest.raises(ValueError, match="replay"): v.attempt()
    assert v.proof_status()["terminal"] == "CANNOT_CHECK" and not calls


def test_status_does_not_load_host_code_from_persistence(view):
    v, calls, _ = view; v.attempt(); v.rt.persist(); count = len(calls)
    fresh = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    assert fresh.session is None
    assert fresh.proof_status()["terminal"] == "LIVE"
    with pytest.raises(ValueError, match="rebinding"): fresh.attempt()
    assert len(calls) == count


def test_stale_issuer_compare_and_swap_preserves_existing_route(view):
    v, _, _ = view; stale = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    v.attempt()
    assert stale.proof_status()["terminal"] == "CANNOT_CHECK"
    assert v.proof_status()["terminal"] == "LIVE"


def test_registration_bytes_changed_on_disk_fail_closed(view):
    v, _, _ = view
    path = v.root / "registration.json"; d = json.loads(path.read_bytes()); d["task"]["goal"] = ["sort", 0]
    path.write_bytes(encoded(d))
    with pytest.raises(ValueError, match="custody"): ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)


def test_prepared_plan_cannot_bind_other_registration(view):
    v, _, _ = view; p, h = issued(v); plan = make_plan(v, p, h)
    plan["registration_sha256"] = "0" * 64
    # Trusted-host diagnostic corruption of private issuer is detected, not a signature attack model.
    v.journal.append("PREPARED", {"run_id": plan["run_id"], "plan": plan, "sha256": hashed(plan)})
    assert v.proof_status()["terminal"] == "CANNOT_CHECK"


def test_pending_second_route_cannot_suppress_valid_independent_route(view):
    v, calls, _ = view; v.attempt(); original = v.routes()[0]["plan"]["run_evidence_id"]
    v.fault = lambda s: (_ for _ in ()).throw(RuntimeError("stop")) if s == "prepared" else None
    with pytest.raises(RuntimeError): v.attempt()
    status = v.proof_status()
    assert status["terminal"] == "LIVE" and status["authenticated_routes"] == 1 and status["pending_routes"] == 1
    count = len(calls)
    fresh = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    assert fresh.proof_status()["terminal"] == "LIVE" and len(calls) == count
    fresh.rt.revoke([original])
    assert fresh.proof_status()["terminal"] == "CANNOT_CHECK"
