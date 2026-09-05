"""Runtime custody regressions: durable boundaries and exact evidence lifecycle."""
from __future__ import annotations

import pytest
from dataclasses import replace

from ocm.constitution import action as CA
from ocm.constitution.hard_gates import (
    HardGateContract, HardGateObservation, HardGateRequirement, HardGateState,
)
from ocm.dialogue.workspace import DialogueWorkspace
from ocm.kso.space import Atom
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.language.meaning import MeaningGraph, MNode
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeRefusal
from ocm.store.event import EventStatus, EventType
from ocm.store.evidence import Channel
from ocm.store.ledger import StaleLedgerHead


def _evidence(rt, name, **kwargs):
    return rt.admit_evidence({"claim": name}, Channel.OBSERVATION, name, **kwargs)[1]


def _action_runtime(root):
    rt = OCMRuntime(root, commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    rt.admit_object(Atom("support", "claim", WP.of({"support:evidence"}), quarantined=True), (), "INSTRUCTION")
    contract = HardGateContract("contract", (HardGateRequirement("checked", "checked", evidence_required=True),), frozen_at_round=1)
    observations = [HardGateObservation("checked", "intent", HardGateState.PASS, contract.fingerprint, ("gate:evidence",), "checked")]
    intent = CA.ActionIntent("intent", "record", {}, Scope.universal(), Authority.of(commit=1), ("support",), "recorded", "low")
    return rt, intent, {"contract": contract, "observations": observations}


@pytest.mark.parametrize("snapshot", [False, True])
def test_stale_writer_is_refused_before_ledger_mutation(tmp_path, snapshot):
    current, stale = OCMRuntime(tmp_path), OCMRuntime(tmp_path)
    control = _evidence(current, "unrelated")
    if snapshot:
        current.persist()
    before = current.ledger.path.read_bytes()
    with pytest.raises(StaleLedgerHead):
        _evidence(stale, "stale")
    assert current.ledger.path.read_bytes() == before
    assert not stale.events and not stale.state.evidence.records
    restarted = OCMRuntime(tmp_path)
    assert restarted.state.evidence.liveness([control]) is Liveness.LIVE
    assert restarted.replay()["identical"]
    stale.replay()
    _evidence(stale, "fresh-after-replay")
    assert OCMRuntime(tmp_path).replay()["identical"]


def test_invalid_derived_revocation_does_not_partially_revoke_or_poison_replay(tmp_path):
    rt = OCMRuntime(tmp_path)
    assumption = _evidence(rt, "assumption")
    derived = _evidence(rt, "derived", derived_from=WP.of({assumption}))
    control = _evidence(rt, "unrelated")
    before = rt.ledger.path.read_bytes(), rt.state.snapshot()
    with pytest.raises(ValueError, match="derived evidence"):
        rt.revoke(iter([assumption, derived]))
    assert (rt.ledger.path.read_bytes(), rt.state.snapshot()) == before
    restarted = OCMRuntime(tmp_path)
    assert all(restarted.state.evidence.liveness([eid]) is Liveness.LIVE for eid in (assumption, derived, control))
    restarted.revoke([assumption])
    assert restarted.state.evidence.liveness([derived]) is Liveness.DEAD
    assert restarted.state.evidence.liveness([control]) is Liveness.LIVE


def test_derived_unknown_interval_survives_revoke_restart_reinstate(tmp_path):
    rt = OCMRuntime(tmp_path)
    assumption = _evidence(rt, "assumption")
    control = _evidence(rt, "unrelated")
    interval = WP((), (frozenset({assumption}),))
    derived = _evidence(rt, "unknown-derived", derived_from=interval)
    assert rt.state.evidence.records[derived].derived_from == interval
    assert rt.state.evidence.liveness([derived]) is Liveness.UNKNOWN
    rt.revoke([assumption])
    assert rt.state.evidence.liveness([derived]) is Liveness.DEAD
    rt.persist()
    restarted = OCMRuntime(tmp_path)
    assert restarted.state.evidence.liveness([derived]) is Liveness.DEAD
    restarted.reinstate([assumption])
    restarted.persist()
    final = OCMRuntime(tmp_path)
    assert final.state.evidence.records[derived].derived_from == interval
    assert final.state.evidence.liveness([derived]) is Liveness.UNKNOWN
    assert final.state.evidence.liveness([control]) is Liveness.LIVE


def test_unknown_upper_bound_reference_is_rejected_before_admission(tmp_path):
    rt = OCMRuntime(tmp_path)
    with pytest.raises(RuntimeRefusal, match="UNKNOWN_EVIDENCE_REFERENCE"):
        _evidence(rt, "unknown-derived", derived_from=WP((), (frozenset({"missing"}),)))
    assert not rt.events and not OCMRuntime(tmp_path).state.evidence.records


def test_dialogue_promotion_tracks_bridge_assumptions_across_restart(tmp_path):
    rt = OCMRuntime(tmp_path)
    ws = DialogueWorkspace(rt, "conversation")
    commitment = ws.commit("speaker", MeaningGraph((MNode("claim", "entity", "claim"),), (), root="claim"))
    assumption = _evidence(rt, "bridge-assumption")
    bridge = _evidence(rt, "derived-bridge", derived_from=WP.of({assumption}))
    control = _evidence(rt, "unrelated")
    promoted = ws.propose_promote(commitment.commitment_id, Scope.universal(), bridge_evidence=[bridge], bridge_authority=Authority.of(speaker=1))
    assert promoted["promoted"]
    eid = promoted["evidence_id"]
    assert rt.state.evidence.liveness([eid]) is Liveness.LIVE
    rt.revoke([assumption])
    assert rt.state.evidence.liveness([bridge]) is Liveness.DEAD
    assert rt.state.evidence.liveness([eid]) is Liveness.DEAD
    rt.persist()
    restarted = OCMRuntime(tmp_path)
    assert DialogueWorkspace.load(restarted, "conversation").machine_commitments[0]["evidence_id"] == eid
    assert restarted.state.evidence.liveness([eid]) is Liveness.DEAD
    restarted.reinstate([assumption])
    assert restarted.state.evidence.liveness([eid]) is Liveness.LIVE
    assert restarted.state.evidence.liveness([control]) is Liveness.LIVE


def test_action_intent_is_durable_before_effector_and_receipt_follows(tmp_path):
    rt, intent, kwargs = _action_runtime(tmp_path)
    seen = []

    def effector(_):
        at_effect = OCMRuntime(tmp_path)
        seen.append(at_effect.events[-1].event_type)
        assert seen[-1] is EventType.ACTION_INTENT
        assert not any(e.event_type is EventType.ACTION_RECEIPT for e in at_effect.events)
        return {"effect": "recorded"}

    receipt = rt.commit_external_action(intent, effector=effector, **kwargs)
    assert receipt.status is CA.ActionStatus.EXECUTED
    assert seen == [EventType.ACTION_INTENT]
    restarted = OCMRuntime(tmp_path)
    assert [e.event_type for e in restarted.events[-2:]] == [EventType.ACTION_INTENT, EventType.ACTION_RECEIPT]
    assert restarted.replay()["identical"]


def test_failed_intent_persistence_prevents_effector(tmp_path, monkeypatch):
    rt, intent, kwargs = _action_runtime(tmp_path)
    calls = []
    before = rt.ledger.path.read_bytes()

    def failed_append(*args, **kwargs):
        raise OSError("storage unavailable")

    monkeypatch.setattr(rt.ledger, "append", failed_append)
    with pytest.raises(OSError, match="storage unavailable"):
        rt.commit_external_action(intent, effector=lambda _: calls.append("effect") or {}, **kwargs)
    assert not calls and rt.ledger.path.read_bytes() == before
    assert OCMRuntime(tmp_path).events[-1].event_type is not EventType.ACTION_INTENT


def test_interrupted_action_preserves_pending_intent_and_blocks_id_reuse(tmp_path):
    rt, intent, kwargs = _action_runtime(tmp_path)
    calls = []

    def interrupted(_):
        calls.append("entered")
        raise KeyboardInterrupt("process interrupted before receipt")

    with pytest.raises(KeyboardInterrupt):
        rt.commit_external_action(intent, effector=interrupted, **kwargs)
    restarted = OCMRuntime(tmp_path, commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    assert restarted.events[-1].event_type is EventType.ACTION_INTENT
    assert not any(e.event_type is EventType.ACTION_RECEIPT for e in restarted.events)
    with pytest.raises(RuntimeRefusal, match="ACTION_INTENT_ALREADY_RECORDED"):
        restarted.commit_external_action(intent, effector=lambda _: calls.append("repeated") or {}, **kwargs)
    assert calls == ["entered"]
    assert restarted.events[-1].event_type is EventType.ACTION_INTENT


def test_completed_action_id_cannot_execute_again_after_restart(tmp_path):
    rt, intent, kwargs = _action_runtime(tmp_path)
    calls = []
    rt.commit_external_action(intent, effector=lambda _: calls.append("effect") or {}, **kwargs)
    restarted = OCMRuntime(tmp_path, commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    with pytest.raises(RuntimeRefusal, match="ACTION_INTENT_ALREADY_RECORDED"):
        restarted.commit_external_action(intent, effector=lambda _: calls.append("repeat") or {}, **kwargs)
    assert calls == ["effect"]


def test_stale_action_writer_cannot_execute_or_damage_current_state(tmp_path):
    stale, intent, kwargs = _action_runtime(tmp_path)
    current = OCMRuntime(tmp_path)
    current.revoke(["support:evidence"])
    control = _evidence(current, "unrelated")
    before = current.ledger.path.read_bytes()
    calls = []
    with pytest.raises(StaleLedgerHead):
        stale.commit_external_action(intent, effector=lambda _: calls.append("effect") or {}, **kwargs)
    assert not calls and current.ledger.path.read_bytes() == before
    restarted = OCMRuntime(tmp_path)
    assert restarted.state.ks.atom("support").liveness(restarted.state.revoked) is Liveness.DEAD
    assert restarted.state.evidence.liveness([control]) is Liveness.LIVE


def test_receipt_write_failure_preserves_unresolved_intent(tmp_path, monkeypatch):
    rt, intent, kwargs = _action_runtime(tmp_path)
    original_append = rt.ledger.append
    calls = []

    def append_except_receipt(kind, payload, **options):
        if payload.get("event_type") == EventType.ACTION_RECEIPT.value:
            raise OSError("receipt storage unavailable")
        return original_append(kind, payload, **options)

    monkeypatch.setattr(rt.ledger, "append", append_except_receipt)
    with pytest.raises(OSError, match="receipt storage unavailable"):
        rt.commit_external_action(intent, effector=lambda _: calls.append("effect") or {}, **kwargs)
    assert calls == ["effect"]
    restarted = OCMRuntime(tmp_path)
    assert restarted.events[-1].event_type is EventType.ACTION_INTENT
    assert not any(e.event_type is EventType.ACTION_RECEIPT for e in restarted.events)


def test_legacy_exact_derived_event_still_replays(tmp_path):
    # The previous event format stored raw lower-family IDs, with no upper key.
    rt = OCMRuntime(tmp_path)
    assumption = _evidence(rt, "assumption")
    ev = rt._emit(EventType.EVIDENCE_ADMITTED, EventStatus.PASS,
                  payload={"payload": {"claim": "legacy"}, "channel": Channel.IMPORTED.value,
                           "source": "legacy", "derived_from": [[assumption]], "authority": None})
    rt._apply(ev)
    legacy = rt.state.evidence.log[-1][1]
    rt.revoke([assumption])
    restarted = OCMRuntime(tmp_path)
    assert restarted.state.evidence.liveness([legacy]) is Liveness.DEAD
    restarted.reinstate([assumption])
    assert restarted.state.evidence.liveness([legacy]) is Liveness.LIVE


def _operator(version="1", inputs=()):
    return OperatorSpec("bounded", version, BackendKind.PROGRAMMATIC, lambda ks, args: {"value": args.get("value", 0)}, inputs)


def test_operator_registration_replays_metadata_without_loading_host_code(tmp_path):
    rt = OCMRuntime(tmp_path)
    op = _operator()
    key = rt.register_operator(op)
    revision = rt.state.registry_revision
    control = _evidence(rt, "unrelated")
    rt.persist()
    assert rt.replay()["identical"]
    assert rt.state.operators.operators[key] is op
    restarted = OCMRuntime(tmp_path)
    assert restarted.state.registry_revision == revision
    assert key not in restarted.state.operators.operators
    before = restarted.ledger.path.read_bytes()
    assert restarted.register_operator(op) == key
    assert restarted.ledger.path.read_bytes() == before
    assert restarted.state.operators.operators[key] is op
    assert restarted.state.evidence.liveness([control]) is Liveness.LIVE


def test_operator_contract_collision_after_restart_does_not_mutate_state(tmp_path):
    rt = OCMRuntime(tmp_path)
    rt.register_operator(_operator())
    restarted = OCMRuntime(tmp_path)
    before = restarted.ledger.path.read_bytes(), restarted.state.registry_revision
    from ocm.kso.space import TypedRejection
    with pytest.raises(TypedRejection, match="OPERATOR_VERSION_COLLISION"):
        restarted.register_operator(_operator(inputs=("different",)))
    assert (restarted.ledger.path.read_bytes(), restarted.state.registry_revision) == before
    assert not restarted.state.operators.operators


def test_failed_operator_registration_does_not_install_backend(tmp_path):
    stale, current = OCMRuntime(tmp_path), OCMRuntime(tmp_path)
    _evidence(current, "unrelated")
    with pytest.raises(StaleLedgerHead):
        stale.register_operator(_operator())
    assert not stale.state.operators.operators


def test_authority_callback_revocation_is_checked_before_effector(tmp_path):
    rt, intent, kwargs = _action_runtime(tmp_path)
    control = _evidence(rt, "unrelated")
    calls = []

    class RevokingAuthority:
        def decide(self, candidate, *, gate_state, warrant_liveness):
            rt.revoke(["support:evidence"])
            return CA.StaticCommitAuthority(Authority.of(commit=1)).decide(candidate, gate_state=gate_state, warrant_liveness=warrant_liveness)

    rt._authority = RevokingAuthority()
    receipt = rt.commit_external_action(intent, effector=lambda _: calls.append("effect") or {}, **kwargs)
    assert not calls and receipt.status is CA.ActionStatus.REFUSED
    assert receipt.refusal_code == "REFUSED:AUTHORIZATION_STATE_CHANGED"
    restarted = OCMRuntime(tmp_path)
    assert restarted.state.ks.atom("support").liveness(restarted.state.revoked) is Liveness.DEAD
    assert restarted.state.evidence.liveness([control]) is Liveness.LIVE


def test_operator_declared_effects_are_part_of_registered_contract(tmp_path):
    from ocm.kso.space import TypedRejection
    rt = OCMRuntime(tmp_path)
    rt.register_operator(_operator())
    before = rt.ledger.path.read_bytes()
    with pytest.raises(TypedRejection, match="OPERATOR_VERSION_COLLISION"):
        rt.register_operator(replace(_operator(), expected_effects=("changed",)))
    assert rt.ledger.path.read_bytes() == before
