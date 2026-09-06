"""Bounded L1 bridge between language ``MeaningGraph`` values and the persistent KSO field.

This module deliberately does *not* flatten every parse node into a KSO atom. A meaning remains a
compact language representation. When a representation needs persistent cross-view identity, the
bridge admits one ``representation`` atom whose identity is bound to:

* the exact bounded meaning structure;
* the explicit meaning-node -> KSO-object correspondences;
* the declared scope.

The bridge is an implementation experiment for ORION-OCM #93. It grants no new factual authority.
Admission still passes through ``OCMRuntime.admit_object`` and the normal KSO event/replay path.
The representation's effective warrant is the correspondence warrant conjoined with every bound
field object's warrant, so loss of either linguistic/correspondence evidence or a referenced field
identity reopens the representation locally.

Meaning structure alone can have automorphisms. Canonicalising the meaning and then attaching
bindings can therefore make persistent identity depend on temporary parser node ids.
``canonical_bound_meaning`` canonicalises the *joint* object (meaning + external bindings), so
alpha-renamed parser outputs produce the same field identity.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from typing import Any, Mapping

from ocm.kso.admission import AdmissionReceipt, CertificateKind
from ocm.kso.ids import canonical_json, object_id
from ocm.kso.space import Atom, Hyperedge, TypedRejection
from ocm.kso.types import Authority, Scope, intersect_scopes
from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile, meet_all_profiles
from ocm.runtime.ocm_runtime import OCMRuntime

from .meaning import MAX_EXACT_CANONICAL, MeaningGraph, canonical

BINDING_SCHEMA = "ocm.meaning-field-binding.v1"


@dataclass(frozen=True, slots=True)
class CanonicalBoundMeaning:
    meaning: MeaningGraph
    meaning_digest: str
    joint_digest: str
    bindings: tuple[tuple[str, str], ...]
    original_to_canonical: tuple[tuple[str, str], ...]

    @property
    def bound_field_atoms(self) -> tuple[str, ...]:
        return tuple(sorted({ref for _, ref in self.bindings}))

    @property
    def unbound_nodes(self) -> tuple[str, ...]:
        bound = {node for node, _ in self.bindings}
        return tuple(n.node_id for n in self.meaning.nodes if n.node_id not in bound)


@dataclass(frozen=True, slots=True)
class MeaningFieldBindingReceipt:
    representation_id: str
    edge_id: str
    meaning_digest: str
    joint_digest: str
    canonical_bindings: tuple[tuple[str, str], ...]
    unbound_nodes: tuple[str, ...]
    existing: bool
    admission: AdmissionReceipt | None
    support_extended: bool = False
    support_event_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": BINDING_SCHEMA,
            "representation_id": self.representation_id,
            "edge_id": self.edge_id,
            "meaning_digest": self.meaning_digest,
            "joint_digest": self.joint_digest,
            "canonical_bindings": [list(x) for x in self.canonical_bindings],
            "unbound_nodes": list(self.unbound_nodes),
            "existing": self.existing,
            "support_extended": self.support_extended,
            "support_event_id": self.support_event_id,
            "admission": None
            if self.admission is None
            else {
                "atom_id": self.admission.atom_id,
                "certificate": self.admission.certificate.value,
                "warranted": self.admission.warranted,
                "edges_added": self.admission.edges_added,
                "quarantined": self.admission.quarantined,
                "reachable_by_navigation": self.admission.reachable_by_navigation,
                "resources": self.admission.resources.as_dict(),
            },
        }


def _joint_encoding(
    g: MeaningGraph,
    order: tuple[str, ...],
    bindings: Mapping[str, str],
) -> tuple[str, tuple[tuple[str, str], ...]]:
    mapping = {v: f"n{i}" for i, v in enumerate(order)}
    nodes = sorted((mapping[n.node_id], n.colour()) for n in g.nodes)
    edges = sorted(
        (
            e.relation,
            tuple(mapping[t] for t in e.tails),
            tuple(mapping[h] for h in e.heads),
            e.value or "",
        )
        for e in g.edges
    )
    root = None if g.root is None else mapping[g.root]
    canonical_bindings = tuple(sorted((mapping[src], ref) for src, ref in bindings.items()))
    encoded = canonical_json(
        {
            "nodes": nodes,
            "edges": edges,
            "root": root,
            "bindings": canonical_bindings,
        }
    )
    return encoded, canonical_bindings


def canonical_bound_meaning(g: MeaningGraph, bindings: Mapping[str, str]) -> CanonicalBoundMeaning:
    """Canonicalise ``(meaning graph, field bindings)`` jointly.

    ``bindings`` keys are the graph's current node ids. Values are persistent KSO atom ids.
    Partial bindings are allowed because a language representation may be only partly grounded.
    An entirely unbound representation is intentionally not persistable by ``bind_meaning``.
    """
    unknown = sorted(set(bindings) - set(g.ids))
    if unknown:
        raise TypedRejection("UNKNOWN_MEANING_NODE_BINDING", ",".join(unknown))
    if any(not isinstance(ref, str) or not ref for ref in bindings.values()):
        raise TypedRejection("INVALID_FIELD_BINDING", "field atom ids must be non-empty strings")
    if len(g.nodes) > MAX_EXACT_CANONICAL:
        raise CannotCheck(
            f"exact bound-meaning canonical form bounded to {MAX_EXACT_CANONICAL} nodes; fragment has {len(g.nodes)}"
        )

    # Binding identity is part of the colour partition. This removes parser-id dependence even
    # when the unbound meaning graph has automorphisms.
    by_colour: dict[str, list[str]] = {}
    for n in g.nodes:
        colour = canonical_json({"meaning_colour": n.colour(), "field_ref": bindings.get(n.node_id)})
        by_colour.setdefault(colour, []).append(n.node_id)
    classes = [by_colour[c] for c in sorted(by_colour)]

    best: tuple[str, tuple[str, ...], tuple[tuple[str, str], ...]] | None = None
    for perms in itertools.product(*(itertools.permutations(c) for c in classes)):
        order = tuple(v for block in perms for v in block)
        encoded, canonical_bindings = _joint_encoding(g, order, bindings)
        if best is None or encoded < best[0]:
            best = (encoded, order, canonical_bindings)
    assert best is not None
    encoded, order, canonical_bindings = best
    mapping = {v: f"n{i}" for i, v in enumerate(order)}
    can_graph = g.relabel(mapping)
    # Keep the existing MEG-24 meaning identity as a separate coordinate. The joint identity adds
    # grounding/correspondence information; it does not redefine meaning equivalence.
    meaning_digest = canonical(g)[1]
    return CanonicalBoundMeaning(
        can_graph,
        meaning_digest,
        hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        canonical_bindings,
        tuple(sorted(mapping.items())),
    )


def _binding_meta(bound: CanonicalBoundMeaning) -> tuple[tuple[str, Any], ...]:
    # Sort by key explicitly because event canonicalisation serialises metadata through a dict and
    # replay reconstructs it in JSON key order. Canonical order makes exact duplicate comparison
    # stable before and after restart.
    return tuple(
        sorted(
            (
                ("binding_schema", BINDING_SCHEMA),
                ("meaning_digest", bound.meaning_digest),
                ("joint_digest", bound.joint_digest),
                ("meaning_json", canonical_json(bound.meaning.as_dict())),
                ("canonical_bindings_json", canonical_json(bound.bindings)),
                ("unbound_nodes_json", canonical_json(bound.unbound_nodes)),
            )
        )
    )


def _effective_epistemic_state(
    runtime: OCMRuntime,
    tails: tuple[str, ...],
    correspondence_warrant: WarrantProfile,
    requested_scope: Scope,
) -> tuple[WarrantProfile, Scope]:
    atoms = [runtime.state.ks.atom(atom_id) for atom_id in tails]
    effective_warrant = meet_all_profiles([correspondence_warrant, *(a.warrant for a in atoms)])
    effective_scope = intersect_scopes([requested_scope, *(a.scope for a in atoms)])
    if effective_warrant.is_zero:
        raise TypedRejection("ZERO_EFFECTIVE_BINDING_WARRANT")
    if effective_scope.is_empty:
        raise TypedRejection("SCOPE_EMPTY", "meaning-field binding incompatible with bound field objects")
    all_evidence = effective_warrant.evidence
    missing_evidence = sorted(str(e) for e in all_evidence if e not in runtime.state.evidence.records)
    if missing_evidence:
        raise TypedRejection("UNKNOWN_EVIDENCE_REFERENCE", ",".join(missing_evidence))
    return effective_warrant, effective_scope


def _validate_assumption_support(
    runtime: OCMRuntime,
    support_evidence_id: str,
    warrant: WarrantProfile,
    certificate: CertificateKind,
    authority: Authority,
    scope: Scope,
) -> None:
    record = runtime.state.evidence.records.get(support_evidence_id)
    if record is None:
        raise TypedRejection("UNKNOWN_SUPPORT_EVIDENCE", support_evidence_id)
    if not record.is_assumption:
        raise TypedRejection("SUPPORT_EVIDENCE_NOT_ASSUMPTION", support_evidence_id)
    if record.warrant.is_zero:
        raise TypedRejection("ZERO_SUPPORT_WARRANT", support_evidence_id)
    if record.warrant.liveness(runtime.state.revoked) is not Liveness.LIVE:
        raise TypedRejection("SUPPORT_EVIDENCE_NOT_LIVE", support_evidence_id)
    if record.warrant != warrant:
        raise TypedRejection("SUPPORT_WARRANT_MISMATCH", support_evidence_id)
    if record.channel.certificate is not certificate:
        raise TypedRejection("SUPPORT_CERTIFICATE_MISMATCH", support_evidence_id)
    if record.authority != authority:
        raise TypedRejection("SUPPORT_AUTHORITY_ARGUMENT_MISMATCH", support_evidence_id)
    if record.scope != scope:
        raise TypedRejection("SUPPORT_SCOPE_MISMATCH", support_evidence_id)


def bind_meaning(
    runtime: OCMRuntime,
    meaning: MeaningGraph,
    bindings: Mapping[str, str],
    *,
    warrant: WarrantProfile,
    certificate: CertificateKind | str = CertificateKind.OBSERVATION,
    authority: Authority | None = None,
    scope: Scope | None = None,
    support_evidence_id: str | None = None,
) -> MeaningFieldBindingReceipt:
    """Admit a bounded meaning/field correspondence through the normal runtime boundary.

    ``warrant`` is the correspondence/utterance warrant. The persisted representation atom carries
    ``warrant ⊗ warrants(bound field objects)`` so cross-view revision is exact. The transport edge
    retains the correspondence warrant itself; the atom's scope is the requested scope intersected
    with all bound object scopes.

    Semantic identity excludes warrant and authority so repeated evidence does not create another
    semantic object. The current runtime has no event for monotonically extending an existing atom's
    alternative support, so a repeat with different epistemic state is rejected fail-closed rather
    than silently dropping support. Exact repeats are idempotent at this bridge layer.
    """
    if not bindings:
        raise TypedRejection("NO_FIELD_BINDING", "transient ungrounded meanings stay outside persistent KSO")
    if warrant.is_zero:
        raise TypedRejection("ZERO_WARRANT_FIELD_BINDING")
    missing_refs = sorted(set(bindings.values()) - set(runtime.state.ks.ids))
    if missing_refs:
        raise TypedRejection("UNKNOWN_FIELD_ATOM", ",".join(missing_refs))

    authority = authority or Authority()
    requested_scope = scope or Scope.universal()
    if requested_scope.is_empty:
        raise TypedRejection("SCOPE_EMPTY", "meaning-field binding")
    certificate = CertificateKind(certificate)
    if support_evidence_id is not None:
        _validate_assumption_support(
            runtime, support_evidence_id, warrant, certificate, authority, requested_scope
        )

    bound = canonical_bound_meaning(meaning, bindings)
    tails = bound.bound_field_atoms
    effective_warrant, effective_scope = _effective_epistemic_state(runtime, tails, warrant, requested_scope)
    identity_payload = {
        "schema": BINDING_SCHEMA,
        "joint_digest": bound.joint_digest,
        "scope": effective_scope.as_dict(),
    }
    representation_id = object_id("meaning-binding", identity_payload)
    edge_id = object_id(
        "meaning-binding-edge",
        {"representation_id": representation_id, "tails": tails, "relation": "REPRESENTATION_TRANSPORT"},
    )
    meta = _binding_meta(bound)
    content_ref = f"meaning:{bound.meaning_digest}"

    if representation_id in runtime.state.ks.ids:
        existing = runtime.state.ks.atom(representation_id)
        existing_edge = runtime.state.ks.edge_view.get(edge_id)
        structural_conflict = (
            existing.atom_type != "representation"
            or existing.content_ref != content_ref
            or existing.meta != meta
            or existing.scope != effective_scope
            or existing_edge is None
            or existing_edge.tails != tails
            or existing_edge.heads != (representation_id,)
            or existing_edge.relation_type != "REPRESENTATION_TRANSPORT"
        )
        if structural_conflict:
            raise TypedRejection("BINDING_IDENTITY_STATE_CONFLICT", "same binding identity has different structure")
        if support_evidence_id is not None:
            event = runtime.extend_representation_support(
                representation_id, edge_id, support_evidence_id, certificate
            )
            return MeaningFieldBindingReceipt(
                representation_id,
                edge_id,
                bound.meaning_digest,
                bound.joint_digest,
                bound.bindings,
                bound.unbound_nodes,
                True,
                None,
                event is not None,
                None if event is None else event.event_id,
            )
        if (
            existing.warrant != effective_warrant
            or existing.authority != authority
            or existing_edge.warrant != warrant
            or existing_edge.authority != authority
            or runtime.state.certificates.get(representation_id) != certificate.value
        ):
            raise TypedRejection(
                "BINDING_IDENTITY_STATE_CONFLICT",
                "same semantic binding already exists with different epistemic state",
            )
        return MeaningFieldBindingReceipt(
            representation_id,
            edge_id,
            bound.meaning_digest,
            bound.joint_digest,
            bound.bindings,
            bound.unbound_nodes,
            True,
            None,
        )

    atom = Atom(
        representation_id,
        "representation",
        warrant=effective_warrant,
        authority=authority,
        scope=effective_scope,
        content_ref=content_ref,
        meta=meta,
    )
    edge = Hyperedge(
        edge_id,
        tails,
        (representation_id,),
        "REPRESENTATION_TRANSPORT",
        warrant=warrant,
        authority=authority,
        scope=requested_scope,
    )
    admission = runtime.admit_object(atom, (edge,), certificate)
    return MeaningFieldBindingReceipt(
        representation_id,
        edge_id,
        bound.meaning_digest,
        bound.joint_digest,
        bound.bindings,
        bound.unbound_nodes,
        False,
        admission,
    )


def load_meaning_binding(runtime: OCMRuntime, representation_id: str) -> CanonicalBoundMeaning:
    """Read and self-check a persisted bridge atom after replay/restart, including its warrant law."""
    if representation_id not in runtime.state.ks.ids:
        raise TypedRejection("UNKNOWN_FIELD_BINDING", representation_id)
    atom = runtime.state.ks.atom(representation_id)
    meta = dict(atom.meta)
    if atom.atom_type != "representation" or meta.get("binding_schema") != BINDING_SCHEMA:
        raise TypedRejection("NOT_MEANING_FIELD_BINDING", representation_id)
    try:
        graph = MeaningGraph.from_dict(json.loads(str(meta["meaning_json"])))
        bindings_raw = json.loads(str(meta["canonical_bindings_json"]))
        bindings = tuple((str(node), str(ref)) for node, ref in bindings_raw)
        meaning_digest = str(meta["meaning_digest"])
        joint_digest = str(meta["joint_digest"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise CannotCheck(f"malformed persisted meaning binding {representation_id}: {exc}") from exc
    if canonical(graph)[1] != meaning_digest:
        raise CannotCheck(f"persisted meaning digest mismatch for {representation_id}")
    checked = canonical_bound_meaning(graph, dict(bindings))
    if checked.joint_digest != joint_digest:
        raise CannotCheck(f"persisted joint binding digest mismatch for {representation_id}")

    tails = checked.bound_field_atoms
    edge_id = object_id(
        "meaning-binding-edge",
        {"representation_id": representation_id, "tails": tails, "relation": "REPRESENTATION_TRANSPORT"},
    )
    edge = runtime.state.ks.edge_map().get(edge_id)
    if edge is None or edge.tails != tails or edge.heads != (representation_id,) or edge.relation_type != "REPRESENTATION_TRANSPORT":
        raise CannotCheck(f"missing or mismatched representation-transport edge for {representation_id}")
    try:
        expected_warrant = meet_all_profiles([edge.warrant, *(runtime.state.ks.atom(t).warrant for t in tails)])
        expected_scope = intersect_scopes([edge.scope, *(runtime.state.ks.atom(t).scope for t in tails)])
    except TypedRejection as exc:
        raise CannotCheck(f"bound field identity missing for {representation_id}: {exc}") from exc
    if atom.warrant != expected_warrant:
        raise CannotCheck(f"persisted binding warrant law mismatch for {representation_id}")
    if atom.scope != expected_scope:
        raise CannotCheck(f"persisted binding scope law mismatch for {representation_id}")
    return checked


def binding_liveness(runtime: OCMRuntime, representation_id: str) -> Liveness:
    if representation_id not in runtime.state.ks.ids:
        raise TypedRejection("UNKNOWN_FIELD_BINDING", representation_id)
    return runtime.state.ks.atom(representation_id).liveness(runtime.state.revoked)
