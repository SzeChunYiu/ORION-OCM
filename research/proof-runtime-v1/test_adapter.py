"""OCM integration controls. Native boundaries are mocked by the session fixture."""
import json
from pathlib import Path
import pytest
from test_closed_session import setup
from adapter import ProofRuntimeView
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.kso.space import Atom
from ocm.kso.admission import CertificateKind
from ocm.kso.warrant import WarrantProfile
from ocm.kso.nogoods import NogoodSet


@pytest.fixture
def view(setup, tmp_path):
    create, calls, _ = setup
    session = create()
    rt = OCMRuntime(tmp_path / "ocm")
    v = ProofRuntimeView.create(rt, session, tmp_path / "issuer")
    return v, calls, create


def test_actual_solve_then_atomic_admission_and_persisted_ast(view):
    v, calls, _ = view
    assert v.proof_status()["terminal"] == "OPEN"
    assert v.rt.state.ks.atom(v.registration["goal_id"]).warrant.liveness(()) .value == "UNKNOWN"
    result = v.attempt()
    assert result["terminal"] == "ADMITTED", result
    assert [c[0] for c in calls] == ["worker", "checker"]
    assert result["solve"]["decision"] == "ANSWER"
    trace = result["solve"]["trace"]["stages"]
    assert any(s["payload"].get("operator_selection", {}).get("mode") == "EXACT_INPUT_INDEX" for s in trace)
    assert v.proof_status()["terminal"] == "LIVE"
    route = v.routes()[0]
    assert route["plan"]["candidate"] == result["solve"]["answer"]["candidate"]
    ev = next(e for e in v.rt.events if e.event_hash == route["commit"]["events"][-1])
    assert ev.event_type.value == "OBJECT_BATCH_ADMITTED_V1"
    assert len(ev.payload["items"]) == 3
    assert v.registration["discovery_id"] not in v.rt.state.ks.atom(route["plan"]["claim_id"]).warrant.evidence


def test_restart_revocation_and_independent_discovery(view):
    v, calls, _ = view; assert v.attempt()["terminal"] == "ADMITTED"
    route = v.routes()[0]["plan"]; count = len(calls)
    v.rt.persist(); v.session.close()
    fresh = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    assert fresh.proof_status()["terminal"] == "LIVE"
    fresh.rt.revoke([fresh.registration["discovery_id"]])
    assert fresh.proof_status()["terminal"] == "LIVE"
    assert fresh.proof_status()["applicable"] is False
    fresh.rt.revoke([route["run_evidence_id"]])
    assert fresh.proof_status()["terminal"] == "OPEN"
    again = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    assert again.proof_status()["terminal"] == "OPEN"
    again.rt.reinstate([route["run_evidence_id"]])
    assert again.proof_status()["terminal"] == "LIVE"
    assert len(calls) == count


def test_two_checked_routes_share_environment_not_discovery(view):
    v, calls, _ = view
    assert v.attempt()["terminal"] == "ADMITTED"
    assert v.attempt()["terminal"] == "ADMITTED"
    a, b = [r["plan"]["run_evidence_id"] for r in v.routes()]
    assert a != b and [c[0] for c in calls] == ["worker", "checker"] * 2
    v.rt.revoke([a]); assert v.proof_status()["terminal"] == "LIVE"
    v.rt.revoke([b]); assert v.proof_status()["terminal"] == "OPEN"
    v.rt.reinstate([a, b]); assert v.proof_status()["terminal"] == "LIVE"
    v.rt.revoke([v.registration["environment_evidence_id"]])
    assert v.proof_status()["terminal"] == "OPEN"


def test_forged_exact_checker_atom_and_handle_do_not_authenticate(view):
    v, _, _ = view
    v.rt.admit_object(Atom("fake", "proof", WarrantProfile.one(), quarantined=True,
                         meta=(("kernel_verified", True),)), (), CertificateKind.EXACT_CHECKER)
    assert v.proof_status()["terminal"] == "OPEN"
    with pytest.raises(ValueError):
        v.admit_checked({"candidate": ["const", 0]}, {"terminal": "KERNEL_PASS", "run_id": "fake"})
    assert not v.routes()


@pytest.mark.parametrize("fault", ["prepared", "run_evidence", "derived_evidence", "batch", "committed"])
def test_crash_prefix_is_nonserving_then_explicit_recovery_is_idempotent(view, fault):
    v, calls, _ = view
    def crash(stage):
        if stage == fault: raise RuntimeError("injected crash " + stage)
    v.fault = crash
    with pytest.raises(RuntimeError, match="injected crash"):
        v.attempt()
    fresh = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    assert fresh.proof_status()["terminal"] == ("LIVE" if fault == "committed" else "CANNOT_CHECK")
    rows = fresh.routes(); run = rows[0]["plan"]["run_id"]
    count = len(calls)
    fresh.recover(run)
    assert fresh.proof_status()["terminal"] == "LIVE"
    before = (len(fresh.rt.events), len(fresh.journal.entries()))
    fresh.recover(run)
    assert before == (len(fresh.rt.events), len(fresh.journal.entries()))
    assert count == len(calls)


def test_intervening_write_prevents_recovery(view):
    v, _, _ = view
    v.fault = lambda stage: (_ for _ in ()).throw(RuntimeError("stop")) if stage == "prepared" else None
    with pytest.raises(RuntimeError): v.attempt()
    v.rt.admit_evidence({"unrelated": True}, "instruction", "other")
    fresh = ProofRuntimeView.restore(OCMRuntime(v.rt.root), v.root)
    with pytest.raises(ValueError, match="intervening"):
        fresh.recover(fresh.routes()[0]["plan"]["run_id"])
    assert fresh.proof_status()["terminal"] == "CANNOT_CHECK"


@pytest.mark.parametrize("where", ["artifact", "journal", "record"])
def test_custody_loss_fails_closed_without_new_check(view, where):
    v, calls, _ = view; v.attempt(); count = len(calls)
    route = v.routes()[0]["plan"]
    if where == "artifact":
        Path(route["artifacts"][0]["path"]).write_bytes(b"tampered")
    elif where == "journal":
        v.journal.path.unlink()
    else:
        Path(v.root / "registration.json").write_bytes(b"{}")
    assert v.proof_status()["terminal"] == "CANNOT_CHECK"
    assert len(calls) == count


def test_combined_nogood_prevents_live(view):
    v, _, _ = view; v.attempt(); p = v.routes()[0]["plan"]
    v.rt.state.nogoods = NogoodSet.of({p["run_evidence_id"], v.registration["environment_evidence_id"]})
    assert v.proof_status()["terminal"] == "OPEN"


def test_kernel_callback_mutation_cannot_admit(view, monkeypatch):
    v, _, _ = view; original = v.session.check
    def mutation(data):
        handle = original(data)
        v.rt.admit_evidence({"callback": True}, "instruction", "mutant")
        return handle
    monkeypatch.setattr(v.session, "check", mutation)
    result = v.attempt()
    assert result["terminal"] == "CANNOT_CHECK" and not v.routes()


def test_candidate_change_after_check_cannot_admit(view, monkeypatch):
    v, _, _ = view; original = v.session.check
    def mutation(data):
        handle = original(data); data["candidate"] = ["const", 1]; return handle
    monkeypatch.setattr(v.session, "check", mutation)
    assert v.attempt()["terminal"] == "CANNOT_CHECK" and not v.routes()
