from __future__ import annotations

import pytest

from ocm.dialogue.field_binding import bind_commitment, commitment_meaning
from ocm.dialogue.workspace import DialogueWorkspace
from ocm.kso.admission import CertificateKind
from ocm.kso.space import Atom, TypedRejection
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language.field_bridge import binding_liveness, load_meaning_binding
from ocm.language.meaning import MEdge, MNode, MeaningGraph
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


def _anchor(runtime: OCMRuntime, atom_id: str) -> str:
    _, eid = runtime.admit_evidence(
        {"fixture_entity": atom_id},
        Channel.IMPORTED,
        "dialogue-field-test",
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
    return DialogueWorkspace(runtime, "conv:field")


def test_active_commitment_binds_with_evidence_authority_not_field_truth(tmp_path) -> None:
    ws = _workspace(tmp_path)
    commitment = ws.commit("user", _seeing_graph(), utterance="Alice sees Bob")
    receipt = bind_commitment(
        ws,
        commitment.commitment_id,
        {"alice": "field:alice", "bob": "field:bob"},
    )
    atom = ws.runtime.state.ks.atom(receipt.field_binding.representation_id)
    evidence = ws.runtime.state.evidence.records[commitment.evidence_id]
    assert atom.authority == evidence.authority == Authority.of(speaker=1)
    assert atom.authority.rank("world_truth") == 0
    assert commitment.evidence_id in atom.warrant.evidence
    assert binding_liveness(ws.runtime, atom.atom_id) is Liveness.LIVE
    loaded = load_meaning_binding(ws.runtime, atom.atom_id)
    assert loaded.joint_digest == receipt.field_binding.joint_digest


def test_negative_commitment_restores_polarity_and_cannot_collapse_with_positive(tmp_path) -> None:
    ws = _workspace(tmp_path)
    pos = ws.commit("alice", _seeing_graph(), utterance="Alice sees Bob")
    neg = ws.commit("bob", _seeing_graph(), negated=True, utterance="Alice does not see Bob")

    pos_receipt = bind_commitment(ws, pos.commitment_id, {"alice": "field:alice", "bob": "field:bob"})
    neg_receipt = bind_commitment(ws, neg.commitment_id, {"alice": "field:alice", "bob": "field:bob"})

    assert pos_receipt.field_binding.meaning_digest != neg_receipt.field_binding.meaning_digest
    assert pos_receipt.field_binding.representation_id != neg_receipt.field_binding.representation_id
    neg_graph = commitment_meaning(ws, neg.commitment_id)
    assert any(edge.relation == "NEGATES" for edge in neg_graph.edges)
    # Contradictory speaker reports may both remain represented; neither gains world truth.
    assert ws.runtime.state.ks.atom(pos_receipt.field_binding.representation_id).authority.rank("world_truth") == 0
    assert ws.runtime.state.ks.atom(neg_receipt.field_binding.representation_id).authority.rank("world_truth") == 0


def test_retraction_revokes_same_evidence_and_kills_only_dependent_field_binding(tmp_path) -> None:
    ws = _workspace(tmp_path)
    commitment = ws.commit("user", _seeing_graph(), utterance="Alice sees Bob")
    receipt = bind_commitment(ws, commitment.commitment_id, {"alice": "field:alice", "bob": "field:bob"})
    rep = receipt.field_binding.representation_id
    assert binding_liveness(ws.runtime, rep) is Liveness.LIVE

    ws.retract(commitment.commitment_id)
    assert commitment.evidence_id in ws.runtime.state.revoked
    assert binding_liveness(ws.runtime, rep) is Liveness.DEAD
    assert ws.runtime.state.ks.atom("field:alice").liveness(ws.runtime.state.revoked) is Liveness.LIVE
    assert ws.runtime.state.ks.atom("field:bob").liveness(ws.runtime.state.revoked) is Liveness.LIVE
    with pytest.raises(TypedRejection) as exc:
        bind_commitment(ws, commitment.commitment_id, {"alice": "field:alice", "bob": "field:bob"})
    assert exc.value.code == "COMMITMENT_NOT_ACTIVE"


def test_adapter_never_infers_field_identity_and_refuses_unknown_commitment(tmp_path) -> None:
    ws = _workspace(tmp_path)
    commitment = ws.commit("user", _seeing_graph(), utterance="Alice sees Bob")
    with pytest.raises(TypedRejection) as exc:
        bind_commitment(ws, commitment.commitment_id, {})
    assert exc.value.code == "NO_FIELD_BINDING"

    with pytest.raises(TypedRejection) as exc:
        bind_commitment(ws, "missing", {"alice": "field:alice"})
    assert exc.value.code == "UNKNOWN_COMMITMENT"
