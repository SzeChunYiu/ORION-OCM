from __future__ import annotations

import pytest

from ocm.kso.admission import CertificateKind
from ocm.kso.space import Atom, TypedRejection
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile
from ocm.language.field_bridge import (
    bind_meaning,
    binding_liveness,
    canonical_bound_meaning,
    load_meaning_binding,
)
from ocm.language.meaning import MEdge, MNode, MeaningGraph
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


def _anchor(runtime: OCMRuntime, atom_id: str) -> str:
    _, eid = runtime.admit_evidence(
        {"fixture_entity": atom_id},
        Channel.IMPORTED,
        "field-bridge-test",
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


def _seeing_graph() -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("event", "event", "see"),
            MNode("left", "entity", "person"),
            MNode("right", "entity", "person"),
        ),
        (
            MEdge("ROLE:agent", ("event",), ("left",)),
            MEdge("ROLE:patient", ("event",), ("right",)),
        ),
        root="event",
    )


def test_joint_canonical_binding_is_parser_id_invariant() -> None:
    g = _seeing_graph()
    a = canonical_bound_meaning(g, {"left": "field:alice", "right": "field:bob"})
    renamed = g.relabel({"event": "z9", "left": "tmp2", "right": "tmp1"})
    b = canonical_bound_meaning(renamed, {"tmp2": "field:alice", "tmp1": "field:bob"})
    assert a.meaning_digest == b.meaning_digest
    assert a.joint_digest == b.joint_digest
    assert a.bindings == b.bindings


def test_joint_canonical_binding_preserves_semantic_role_assignments() -> None:
    g = _seeing_graph()
    correct = canonical_bound_meaning(g, {"left": "field:alice", "right": "field:bob"})
    swapped = canonical_bound_meaning(g, {"left": "field:bob", "right": "field:alice"})
    assert correct.meaning_digest == swapped.meaning_digest
    assert correct.joint_digest != swapped.joint_digest


def test_bridge_persists_replays_and_revokes_through_one_runtime_field(tmp_path) -> None:
    runtime = OCMRuntime(tmp_path)
    _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    _, said = runtime.admit_evidence(
        {"utterance": "Alice sees Bob", "speaker": "user"},
        Channel.OBSERVATION,
        "user",
        scope=Scope.of("conv:1"),
        authority=Authority.of(speaker=1),
    )
    warrant = WarrantProfile.of({said})
    receipt = bind_meaning(
        runtime,
        _seeing_graph(),
        {"left": "field:alice", "right": "field:bob"},
        warrant=warrant,
        certificate=CertificateKind.OBSERVATION,
        authority=Authority.of(speaker=1),
        scope=Scope.of("conv:1"),
    )
    assert not receipt.existing
    assert receipt.representation_id in runtime.state.ks.ids
    assert binding_liveness(runtime, receipt.representation_id) is Liveness.LIVE
    atom = runtime.state.ks.atom(receipt.representation_id)
    assert atom.atom_type == "representation"
    assert atom.authority == Authority.of(speaker=1)
    assert atom.authority.rank("world_truth") == 0
    # The field representation is warranted by the utterance/correspondence AND both referenced
    # persistent identities. It is not a free-standing duplicate language truth store.
    assert said in atom.warrant.evidence
    assert runtime.state.ks.atom("field:alice").warrant.evidence <= atom.warrant.evidence
    assert runtime.state.ks.atom("field:bob").warrant.evidence <= atom.warrant.evidence
    edge = runtime.state.ks.edge_map()[receipt.edge_id]
    assert edge.relation_type == "REPRESENTATION_TRANSPORT"
    assert set(edge.tails) == {"field:alice", "field:bob"}
    assert edge.warrant == warrant

    runtime.persist()
    restarted = OCMRuntime(tmp_path)
    loaded = load_meaning_binding(restarted, receipt.representation_id)
    assert loaded.joint_digest == receipt.joint_digest
    assert set(dict(loaded.bindings).values()) >= {"field:alice", "field:bob"}
    assert binding_liveness(restarted, receipt.representation_id) is Liveness.LIVE
    events_before_repeat = len(restarted.events)
    replay_repeat = bind_meaning(
        restarted,
        _seeing_graph(),
        {"left": "field:alice", "right": "field:bob"},
        warrant=warrant,
        certificate=CertificateKind.OBSERVATION,
        authority=Authority.of(speaker=1),
        scope=Scope.of("conv:1"),
    )
    assert replay_repeat.existing
    assert len(restarted.events) == events_before_repeat

    report = restarted.revoke([said])
    assert receipt.representation_id in report.cone
    assert binding_liveness(restarted, receipt.representation_id) is Liveness.DEAD
    # The field identities themselves are independent imported objects and remain live.
    assert restarted.state.ks.atom("field:alice").liveness(restarted.state.revoked) is Liveness.LIVE
    assert restarted.state.ks.atom("field:bob").liveness(restarted.state.revoked) is Liveness.LIVE

    restarted.persist()
    restarted_again = OCMRuntime(tmp_path)
    assert binding_liveness(restarted_again, receipt.representation_id) is Liveness.DEAD


def test_binding_reopens_when_a_referenced_field_identity_loses_support(tmp_path) -> None:
    runtime = OCMRuntime(tmp_path)
    alice_support = _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    _, said = runtime.admit_evidence(
        {"utterance": "Alice sees Bob"},
        Channel.OBSERVATION,
        "user",
        scope=Scope.of("conv"),
    )
    receipt = bind_meaning(
        runtime,
        _seeing_graph(),
        {"left": "field:alice", "right": "field:bob"},
        warrant=WarrantProfile.of({said}),
        scope=Scope.of("conv"),
    )
    assert binding_liveness(runtime, receipt.representation_id) is Liveness.LIVE
    report = runtime.revoke([alice_support])
    assert runtime.state.ks.atom("field:alice").liveness(runtime.state.revoked) is Liveness.DEAD
    assert runtime.state.ks.atom("field:bob").liveness(runtime.state.revoked) is Liveness.LIVE
    assert receipt.representation_id in report.cone
    assert binding_liveness(runtime, receipt.representation_id) is Liveness.DEAD


def test_exact_repeat_is_bridge_idempotent_but_new_support_fails_closed(tmp_path) -> None:
    runtime = OCMRuntime(tmp_path)
    _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    _, e1 = runtime.admit_evidence({"reading": 1}, Channel.OBSERVATION, "user", scope=Scope.of("conv"))
    kwargs = dict(
        warrant=WarrantProfile.of({e1}),
        scope=Scope.of("conv"),
        authority=Authority.of(speaker=1),
    )
    first = bind_meaning(runtime, _seeing_graph(), {"left": "field:alice", "right": "field:bob"}, **kwargs)
    events_before = len(runtime.events)
    second = bind_meaning(runtime, _seeing_graph(), {"left": "field:alice", "right": "field:bob"}, **kwargs)
    assert second.existing
    assert second.representation_id == first.representation_id
    assert len(runtime.events) == events_before

    _, e2 = runtime.admit_evidence({"reading": 2}, Channel.OBSERVATION, "user", scope=Scope.of("conv"))
    with pytest.raises(TypedRejection) as exc:
        bind_meaning(
            runtime,
            _seeing_graph(),
            {"left": "field:alice", "right": "field:bob"},
            warrant=WarrantProfile.of({e2}),
            scope=Scope.of("conv"),
            authority=Authority.of(speaker=1),
        )
    assert exc.value.code == "BINDING_IDENTITY_STATE_CONFLICT"


def test_bridge_refuses_unbound_unknown_and_unregistered_evidence(tmp_path) -> None:
    runtime = OCMRuntime(tmp_path)
    _anchor(runtime, "field:alice")
    _, e = runtime.admit_evidence({"reading": 1}, Channel.OBSERVATION, "user")
    with pytest.raises(TypedRejection) as exc:
        bind_meaning(runtime, _seeing_graph(), {}, warrant=WarrantProfile.of({e}))
    assert exc.value.code == "NO_FIELD_BINDING"

    with pytest.raises(TypedRejection) as exc:
        bind_meaning(runtime, _seeing_graph(), {"left": "field:missing"}, warrant=WarrantProfile.of({e}))
    assert exc.value.code == "UNKNOWN_FIELD_ATOM"

    with pytest.raises(TypedRejection) as exc:
        bind_meaning(runtime, _seeing_graph(), {"left": "field:alice"}, warrant=WarrantProfile.of({"ev:missing"}))
    assert exc.value.code == "UNKNOWN_EVIDENCE_REFERENCE"


def test_bridge_preserves_current_exact_canonicalisation_ceiling() -> None:
    g = MeaningGraph(tuple(MNode(f"n{i}", "entity", "x") for i in range(8)), ())
    with pytest.raises(CannotCheck):
        canonical_bound_meaning(g, {"n0": "field:x"})
