from __future__ import annotations

import pytest

from ocm.dialogue.field_binding import bind_commitment
from ocm.dialogue.workspace import DialogueWorkspace
from ocm.kso.admission import CertificateKind
from ocm.kso.space import Atom, TypedRejection
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language.field_bridge import binding_liveness, bind_meaning, load_meaning_binding
from ocm.language.meaning import MEdge, MNode, MeaningGraph
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import EventType
from ocm.store.evidence import Channel


def _anchor(runtime: OCMRuntime, atom_id: str) -> str:
    _, eid = runtime.admit_evidence(
        {"fixture_entity": atom_id},
        Channel.IMPORTED,
        "field-support-test",
        authority=Authority.of(world_truth=1),
    )
    runtime.admit_object(
        Atom(
            atom_id,
            "claim",
            WarrantProfile.of({eid}),
            Authority.of(world_truth=1),
            Scope.universal(),
            quarantined=True,
            content_ref=atom_id,
        ),
        (),
        CertificateKind.IMPORTED,
    )
    return eid


def _graph() -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("event", "event", "see"),
            MNode("alice", "entity", "Alice"),
            MNode("bob", "entity", "Bob"),
        ),
        (
            MEdge("ROLE:agent", ("event",), ("alice",)),
            MEdge("ROLE:patient", ("event",), ("bob",)),
        ),
        root="event",
    )


def _workspace(tmp_path) -> DialogueWorkspace:
    runtime = OCMRuntime(tmp_path)
    _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    return DialogueWorkspace(runtime, "conv:field-support")


def _bindings() -> dict[str, str]:
    return {"alice": "field:alice", "bob": "field:bob"}


def test_second_independent_commitment_extends_one_representation_and_revokes_independently(tmp_path) -> None:
    ws = _workspace(tmp_path)
    first = ws.commit("alice", _graph(), utterance="Alice sees Bob")
    second = ws.commit("bob", _graph(), utterance="Alice sees Bob")

    r1 = bind_commitment(ws, first.commitment_id, _bindings())
    r2 = bind_commitment(ws, second.commitment_id, _bindings())

    assert r2.field_binding.representation_id == r1.field_binding.representation_id
    assert r2.field_binding.existing
    assert r2.field_binding.support_extended
    rep = r1.field_binding.representation_id
    edge = ws.runtime.state.ks.edge_view[r1.field_binding.edge_id]
    atom = ws.runtime.state.ks.atom(rep)
    assert {first.evidence_id, second.evidence_id} <= atom.warrant.evidence
    assert {first.evidence_id, second.evidence_id} <= edge.warrant.evidence
    assert sum(a.atom_id == rep for a in ws.runtime.state.ks.atoms) == 1
    assert sum(e.edge_id == edge.edge_id for e in ws.runtime.state.ks.hyperedges) == 1
    assert sum(e.event_type is EventType.OBJECT_SUPPORT_EXTENDED for e in ws.runtime.events) == 1

    ws.retract(first.commitment_id)
    assert binding_liveness(ws.runtime, rep) is Liveness.LIVE
    ws.retract(second.commitment_id)
    assert binding_liveness(ws.runtime, rep) is Liveness.DEAD


def test_support_extension_replays_exactly_and_repeat_is_idempotent(tmp_path) -> None:
    ws = _workspace(tmp_path)
    first = ws.commit("alice", _graph(), utterance="Alice sees Bob")
    second = ws.commit("bob", _graph(), utterance="Alice sees Bob")
    r1 = bind_commitment(ws, first.commitment_id, _bindings())
    bind_commitment(ws, second.commitment_id, _bindings())
    before_hash = ws.runtime.state.kso_state_hash
    before_events = len(ws.runtime.events)

    repeat = bind_commitment(ws, second.commitment_id, _bindings())
    assert repeat.field_binding.existing
    assert not repeat.field_binding.support_extended
    assert len(ws.runtime.events) == before_events
    assert ws.runtime.state.kso_state_hash == before_hash

    replay = ws.runtime.replay()
    assert replay["identical"]
    assert ws.runtime.state.kso_state_hash == before_hash
    loaded = load_meaning_binding(ws.runtime, r1.field_binding.representation_id)
    assert loaded.joint_digest == r1.field_binding.joint_digest


def test_support_extension_refuses_derived_or_mismatched_actual_evidence(tmp_path) -> None:
    runtime = OCMRuntime(tmp_path)
    _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    scope = Scope.of("conv:field-support")
    authority = Authority.of(speaker=1)

    _, base = runtime.admit_evidence(
        {"statement": "Alice sees Bob"}, Channel.OBSERVATION, "alice", scope=scope, authority=authority
    )
    initial = bind_meaning(
        runtime,
        _graph(),
        _bindings(),
        warrant=runtime.state.evidence.records[base].warrant,
        certificate=CertificateKind.OBSERVATION,
        authority=authority,
        scope=scope,
        support_evidence_id=base,
    )

    _, derived = runtime.admit_evidence(
        {"derived": True},
        Channel.OBSERVATION,
        "derived",
        scope=scope,
        authority=authority,
        derived_from=WarrantProfile.of({base}),
    )
    with pytest.raises(TypedRejection) as exc:
        bind_meaning(
            runtime,
            _graph(),
            _bindings(),
            warrant=runtime.state.evidence.records[derived].warrant,
            certificate=CertificateKind.OBSERVATION,
            authority=authority,
            scope=scope,
            support_evidence_id=derived,
        )
    assert exc.value.code == "SUPPORT_EVIDENCE_NOT_ASSUMPTION"

    _, wrong_channel = runtime.admit_evidence(
        {"checker": True}, Channel.EXACT_CHECKER, "checker", scope=scope, authority=authority
    )
    with pytest.raises(TypedRejection) as exc:
        bind_meaning(
            runtime,
            _graph(),
            _bindings(),
            warrant=runtime.state.evidence.records[wrong_channel].warrant,
            certificate=CertificateKind.OBSERVATION,
            authority=authority,
            scope=scope,
            support_evidence_id=wrong_channel,
        )
    assert exc.value.code == "SUPPORT_CERTIFICATE_MISMATCH"
    assert runtime.state.ks.atom(initial.representation_id).warrant.evidence == runtime.state.evidence.records[base].warrant.evidence | set().union(*(runtime.state.ks.atom(x).warrant.evidence for x in ("field:alice", "field:bob")))


def test_support_extension_refuses_authority_or_scope_change_without_event(tmp_path) -> None:
    runtime = OCMRuntime(tmp_path)
    _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    scope = Scope.of("conv:field-support")
    authority = Authority.of(speaker=1)
    _, first = runtime.admit_evidence(
        {"statement": 1}, Channel.OBSERVATION, "alice", scope=scope, authority=authority
    )
    receipt = bind_meaning(
        runtime,
        _graph(),
        _bindings(),
        warrant=runtime.state.evidence.records[first].warrant,
        certificate=CertificateKind.OBSERVATION,
        authority=authority,
        scope=scope,
        support_evidence_id=first,
    )
    events_before = len(runtime.events)
    warrant_before = runtime.state.ks.atom(receipt.representation_id).warrant

    _, wrong_authority = runtime.admit_evidence(
        {"statement": 2}, Channel.OBSERVATION, "bob", scope=scope, authority=Authority.of(speaker=2)
    )
    events_after_evidence = len(runtime.events)
    with pytest.raises(TypedRejection) as exc:
        bind_meaning(
            runtime,
            _graph(),
            _bindings(),
            warrant=runtime.state.evidence.records[wrong_authority].warrant,
            certificate=CertificateKind.OBSERVATION,
            authority=Authority.of(speaker=2),
            scope=scope,
            support_evidence_id=wrong_authority,
        )
    assert exc.value.code in {"BINDING_IDENTITY_STATE_CONFLICT", "SUPPORT_AUTHORITY_MISMATCH"}
    assert len(runtime.events) == events_after_evidence
    assert runtime.state.ks.atom(receipt.representation_id).warrant == warrant_before
    assert events_after_evidence == events_before + 1

    _, wrong_scope = runtime.admit_evidence(
        {"statement": 3}, Channel.OBSERVATION, "carol", scope=Scope.of("conv:other"), authority=authority
    )
    events_after_scope_evidence = len(runtime.events)
    with pytest.raises(TypedRejection):
        bind_meaning(
            runtime,
            _graph(),
            _bindings(),
            warrant=runtime.state.evidence.records[wrong_scope].warrant,
            certificate=CertificateKind.OBSERVATION,
            authority=authority,
            scope=Scope.of("conv:other"),
            support_evidence_id=wrong_scope,
        )
    assert len(runtime.events) == events_after_scope_evidence
    assert runtime.state.ks.atom(receipt.representation_id).warrant == warrant_before
