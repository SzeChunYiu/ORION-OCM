"""The recorded action declaration is immutable; uncertain effects stay uncertain."""
from dataclasses import replace

import pytest

from ocm.constitution import action as A
from ocm.constitution import boundary as B
from ocm.constitution.hard_gates import HardGateContract, HardGateObservation, HardGateRequirement, HardGateState
from ocm.kso.resources import ResourceVector
from ocm.kso.space import Atom, KnowledgeSpace
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile


def intent(arguments=None):
    return A.ActionIntent("test", "host-operation", arguments or {"items": [1]}, Scope.universal(),
                          Authority.of(commit=1), ("plan",), "completed", "low")


def boundary_inputs():
    contract = HardGateContract("c", (HardGateRequirement("g", "approved"),), frozen_at_round=0)
    return dict(ks=KnowledgeSpace((Atom("plan", "procedure", WarrantProfile.one()),), ()), revoked=(),
                contract=contract, observations=(HardGateObservation("g", "test", HardGateState.PASS, contract.fingerprint, ("e",), "ok"),),
                authority=A.StaticCommitAuthority(Authority.of(commit=1)), log=B.BoundaryLog(), sequence=1)


def test_complete_declaration_is_bound():
    i = intent()
    for other in (replace(i, expected_outcome="other"), replace(i, risk_estimate="high"),
                  replace(i, resource_estimate=ResourceVector(io_calls=1))):
        assert i.fingerprint != other.fingerprint


def test_arguments_are_detached_and_nested_mutation_is_refused():
    args = {"items": [1]}
    i = intent(args)
    original = i.fingerprint
    args["items"].append(2)
    assert i.fingerprint == original
    exported = i.as_dict()
    exported["arguments"]["items"].append(3)
    assert i.as_dict()["arguments"] == {"items": [1]}


def test_exception_after_effect_is_unknown_not_definite_failure():
    effects = []
    def effector(i):
        effects.append(i.intent_id)
        raise RuntimeError("connection lost after host operation")
    result = B.commit_external_action(intent(), effector=effector, **boundary_inputs())
    assert effects == ["test"]
    assert result.status is A.ActionStatus.UNKNOWN
    assert result.resource_observation == "UNKNOWN"


def test_one_shot_observation_evidence_is_preserved():
    kw = boundary_inputs()
    kw["observations"] = iter(kw["observations"])
    result = B.commit_external_action(intent(), effector=lambda i: {"effect": "done"}, **kw)
    assert result.evidence_ids == ("e",)


def pending_runtime(path, reconciler=None):
    from ocm.runtime.ocm_runtime import OCMRuntime
    from ocm.store.event import EventStatus, EventType
    rt = OCMRuntime(path, action_reconciler=reconciler)
    if not rt.events:
        rt._emit(EventType.ACTION_INTENT, EventStatus.PROPOSAL, payload={"intent": intent().as_dict()})
    return rt


@pytest.mark.parametrize("outcome", ["EXECUTED", "NOT_EXECUTED", "UNKNOWN"])
def test_restart_reconciliation_is_host_reported_and_never_reexecutes(tmp_path, outcome):
    class Host:
        def observe(self, pending):
            i = pending["intent"]
            return A.HostActionObservation(i["intent_id"], i["fingerprint"], outcome, "host:lookup", ("receipt:external",))
    rt = pending_runtime(tmp_path, Host())
    rt.reconcile_external_action("test")
    restored = pending_runtime(tmp_path)
    assert len(restored.pending_external_actions()) == (1 if outcome == "UNKNOWN" else 0)
    assert restored.events[-1].payload["observation"]["authority"].startswith("HOST_REPORTED_ONLY")
    assert restored.replay()["identical"]


def test_missing_host_and_mismatched_identity_refuse_without_recording(tmp_path):
    from ocm.runtime.ocm_runtime import RuntimeRefusal
    rt = pending_runtime(tmp_path)
    with pytest.raises(RuntimeRefusal, match="NO_HOST_ACTION_RECONCILER"):
        rt.reconcile_external_action("test")
    class Host:
        def observe(self, pending):
            return A.HostActionObservation("test", "wrong", "EXECUTED", "host", ("e",))
    rt = pending_runtime(tmp_path, Host())
    before = rt.ledger.path.read_bytes()
    with pytest.raises(RuntimeRefusal, match="IDENTITY_MISMATCH"):
        rt.reconcile_external_action("test")
    assert rt.ledger.path.read_bytes() == before


def test_reconciliation_callback_cannot_mutate_runtime_and_close_old_state(tmp_path):
    from ocm.runtime.ocm_runtime import RuntimeRefusal
    class Host:
        def observe(self, pending):
            rt.persist()
            return A.HostActionObservation("test", intent().fingerprint, "EXECUTED", "host", ("e",))
    rt = pending_runtime(tmp_path, Host())
    with pytest.raises(RuntimeRefusal, match="STATE_CHANGED"):
        rt.reconcile_external_action("test")
    assert len(rt.pending_external_actions()) == 1


def test_legacy_effector_exception_can_be_reconciled_without_rewriting_old_receipt(tmp_path):
    from ocm.store.event import EventStatus, EventType
    rt = pending_runtime(tmp_path)
    receipt = {"intent_id": "test", "status": "FAILED", "actual_effect": "RuntimeError: lost connection",
               "refusal_code": "EFFECTOR_FAILED"}
    rt._emit(EventType.ACTION_RECEIPT, EventStatus.FAIL, payload={"receipt": receipt})
    restored = pending_runtime(tmp_path)
    assert restored.pending_external_actions()[0]["receipt"] == receipt
    assert restored.events[-1].payload["receipt"]["status"] == "FAILED"
