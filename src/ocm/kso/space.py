"""The canonical KnowledgeSpace object model — one schema replacing four inherited wrappers.

``KnowledgeSpace`` (kso_math_v1) · ``GovernedSpace`` (freeze checks) · ``RecursiveKSO`` (recursive
v0) · ``UnifiedKSO`` (multidomain) all become views of this one object: atoms and typed directed
hyperedges, each carrying a warrant interval, authority, scope, epoch and resource/provenance
metadata (contract §2).  Certificates and the meter live on ``GovernedSpace`` in ``admission.py``.

Structural edits return a new space. Nested metadata and the shared TypeRegistry are not deeply
immutable: content digests must observe current values, and edits must revalidate against the
current registry. ``to_reference``/``from_reference`` convert to and from the frozen historical
``kso_math_v1`` types for old-vs-new equivalence checks (M1 D3: no architecture laundering).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from fractions import Fraction
from functools import cached_property
from types import MappingProxyType
from typing import Any, Hashable, Iterable, Mapping

from .ids import canonical_json
from .types import DEFAULT_REGISTRY, Authority, Scope, TypeRegistry
from .warrant import Liveness, WarrantProfile


class TypedRejection(ValueError):
    """A typed rejection at a contract boundary; ``code`` is the registered reason."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


@dataclass(frozen=True, slots=True)
class Atom:
    atom_id: str
    atom_type: str
    warrant: WarrantProfile = field(default_factory=WarrantProfile.one)
    authority: Authority = field(default_factory=Authority)
    scope: Scope = field(default_factory=Scope.universal)
    epoch: int = 0
    quarantined: bool = False
    content_ref: str | None = None          # payload / executable / representation reference
    meta: tuple[tuple[str, Any], ...] = ()   # resource / provenance metadata (κ_v)

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)

    def is_live(self, revoked: Iterable[Hashable]) -> bool:
        return self.warrant.is_live(revoked)

    def content_hash(self) -> str:
        return hashlib.sha256(canonical_json({"id": self.atom_id, "type": self.atom_type, "ref": self.content_ref}).encode()).hexdigest()[:16]

    def as_dict(self) -> dict[str, Any]:
        return {
            "atom_id": self.atom_id,
            "atom_type": self.atom_type,
            "warrant": self.warrant.as_dict(),
            "authority": self.authority.as_dict(),
            "scope": self.scope.as_dict(),
            "epoch": self.epoch,
            "quarantined": self.quarantined,
            "content_ref": self.content_ref,
            "meta": dict(self.meta),
        }


@dataclass(frozen=True, slots=True)
class Hyperedge:
    edge_id: str
    tails: tuple[str, ...]
    heads: tuple[str, ...]
    relation_type: str
    weight: Fraction = Fraction(1, 1)
    head_weights: tuple[Fraction, ...] = ()
    warrant: WarrantProfile = field(default_factory=WarrantProfile.one)
    authority: Authority = field(default_factory=Authority)
    scope: Scope = field(default_factory=Scope.universal)
    executable_ref: str | None = None       # φ_h
    meta: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        # Freeze accepted sequence inputs as well as the dataclass attributes themselves.
        object.__setattr__(self, "tails", tuple(self.tails))
        object.__setattr__(self, "heads", tuple(self.heads))
        object.__setattr__(self, "head_weights", tuple(self.head_weights))
        if not self.tails or not self.heads:
            raise ValueError(f"hyperedge {self.edge_id} needs non-empty tails and heads")
        if len(set(self.tails)) != len(self.tails) or len(set(self.heads)) != len(self.heads):
            raise ValueError(f"hyperedge {self.edge_id} repeats an incident atom")
        if self.weight < 0:
            raise ValueError(f"hyperedge {self.edge_id} has negative weight")
        self.normalized_head_weights()

    def normalized_head_weights(self) -> tuple[Fraction, ...]:
        weights = self.head_weights or tuple(Fraction(1, 1) for _ in self.heads)
        if len(weights) != len(self.heads) or any(w < 0 for w in weights):
            raise ValueError(f"hyperedge {self.edge_id}: bad head weights")
        total = sum(weights, Fraction(0, 1))
        if total <= 0:
            raise ValueError(f"hyperedge {self.edge_id}: head weights need positive mass")
        return tuple(w / total for w in weights)

    @property
    def incident(self) -> frozenset[str]:
        return frozenset((*self.tails, *self.heads))

    @property
    def is_pairwise(self) -> bool:
        return len(self.tails) == 1 and len(self.heads) == 1

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)

    def as_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "tails": list(self.tails),
            "heads": list(self.heads),
            "relation_type": self.relation_type,
            "weight": str(self.weight),
            "head_weights": [str(w) for w in self.normalized_head_weights()],
            "warrant": self.warrant.as_dict(),
            "authority": self.authority.as_dict(),
            "scope": self.scope.as_dict(),
            "executable_ref": self.executable_ref,
            "meta": dict(self.meta),
        }


@dataclass(frozen=True)
class KnowledgeSpace:
    atoms: tuple[Atom, ...]
    hyperedges: tuple[Hyperedge, ...]
    registry: TypeRegistry = field(default_factory=lambda: DEFAULT_REGISTRY, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "atoms", tuple(self.atoms))
        object.__setattr__(self, "hyperedges", tuple(self.hyperedges))
        self.validate()

    # --- structure -----------------------------------------------------------------------
    @cached_property
    def ids(self) -> tuple[str, ...]:
        return tuple(a.atom_id for a in self.atoms)

    @cached_property
    def _atom_index(self) -> dict[str, Atom]:
        return {a.atom_id: a for a in self.atoms}

    @cached_property
    def _edge_index(self) -> dict[str, Hyperedge]:
        return {e.edge_id: e for e in self.hyperedges}

    @cached_property
    def atom_view(self) -> Mapping[str, Atom]:
        """Read-only zero-copy view for internal hot paths.

        ``atom_map`` intentionally remains a mutable detached copy for compatibility.
        The mapping is read-only; nested metadata on its values is not deeply frozen.
        """
        return MappingProxyType(self._atom_index)

    @cached_property
    def edge_view(self) -> Mapping[str, Hyperedge]:
        """Read-only zero-copy edge lookup; nested metadata remains caller-owned."""
        return MappingProxyType(self._edge_index)

    @cached_property
    def _incident_index(self) -> dict[str, tuple[Hyperedge, ...]]:
        by_atom: dict[str, list[Hyperedge]] = {}
        for edge in self.hyperedges:
            for atom_id in edge.incident:
                by_atom.setdefault(atom_id, []).append(edge)
        return {atom_id: tuple(edges) for atom_id, edges in by_atom.items()}

    @cached_property
    def _outgoing_index(self) -> dict[str, tuple[Hyperedge, ...]]:
        by_tail: dict[str, list[Hyperedge]] = {}
        for edge in self.hyperedges:
            for tail in edge.tails:
                by_tail.setdefault(tail, []).append(edge)
        return {tail: tuple(edges) for tail, edges in by_tail.items()}

    def atom_map(self) -> dict[str, Atom]:
        # Preserve the public mutable-copy API; callers cannot mutate a cached index.
        return self._atom_index.copy()

    def edge_map(self) -> dict[str, Hyperedge]:
        return self._edge_index.copy()

    def atom(self, atom_id: str) -> Atom:
        try:
            return self._atom_index[atom_id]
        except KeyError:
            raise TypedRejection("UNKNOWN_ATOM", atom_id) from None

    def validate(self) -> None:
        ids = self.ids
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate atom id")
        eids = [e.edge_id for e in self.hyperedges]
        if len(set(eids)) != len(eids):
            raise ValueError("duplicate edge id")
        known = set(ids)
        for a in self.atoms:
            self.registry.require_atom_type(a.atom_type)
        for e in self.hyperedges:
            if any(x not in known for x in (*e.tails, *e.heads)):
                raise ValueError(f"hyperedge {e.edge_id} references an unknown atom")
            self.registry.require_relation_type(e.relation_type)

    def incident_edges(self, atom_id: str) -> tuple[Hyperedge, ...]:
        return self._incident_index.get(atom_id, ())

    def outgoing_edges(self, atom_id: str) -> tuple[Hyperedge, ...]:
        """Structural tail adjacency in insertion order, independent of warrant/registry state.

        The cache belongs to this immutable space. ``dataclasses.replace`` creates a new
        instance without cached properties, so persistent edits cannot inherit stale indexes.
        No liveness, relevance, dependency classification or activation is cached.
        """
        return self._outgoing_index.get(atom_id, ())

    def index_resources(self):
        """Shallow storage of materialized indexes, views and cached evidence entries.

        ``index_size`` counts tuple references, dict entries (including adjacency entries)
        and evidence-frozenset entries. Mapping proxies share their underlying dict entries.
        ``memory_bytes`` counts the shallow containers on this Python host; existing atom,
        edge and string objects are shared and are not charged again. This is a storage
        observation, not an admission work count, recursive memory total or process-RSS estimate.
        """
        import sys

        from .resources import ResourceVector

        entries = memory = 0
        for name in ("ids", "_atom_index", "_edge_index", "_incident_index", "_outgoing_index", "_evidence_universe_value"):
            value = self.__dict__.get(name)
            if value is None:
                continue
            entries += len(value)
            memory += sys.getsizeof(value)
            if name in ("_incident_index", "_outgoing_index"):
                entries += sum(len(edges) for edges in value.values())
                memory += sum(sys.getsizeof(edges) for edges in value.values())
        for name in ("atom_view", "edge_view"):
            value = self.__dict__.get(name)
            if value is not None:
                memory += sys.getsizeof(value)  # Proxy only; underlying entries already counted.
        return ResourceVector(index_size=entries, memory_bytes=memory)

    # --- liveness ------------------------------------------------------------------------
    def live_atoms(self, revoked: Iterable[Hashable] = ()) -> frozenset[str]:
        rv = frozenset(revoked)
        return frozenset(a.atom_id for a in self.atoms if a.is_live(rv))

    def dead_atoms(self, revoked: Iterable[Hashable] = ()) -> frozenset[str]:
        rv = frozenset(revoked)
        return frozenset(a.atom_id for a in self.atoms if a.liveness(rv) is Liveness.DEAD)

    def unknown_atoms(self, revoked: Iterable[Hashable] = ()) -> frozenset[str]:
        rv = frozenset(revoked)
        return frozenset(a.atom_id for a in self.atoms if a.liveness(rv) is Liveness.UNKNOWN)

    def edge_enabled_liveness(self, edge: Hyperedge, revoked: Iterable[Hashable] = ()) -> Liveness:
        """Three-valued liveness of an edge *as a path*: edge ∧ every tail ∧ every head."""
        from .warrant import kleene_and

        rv = frozenset(revoked)
        amap = self.atom_view
        out = edge.liveness(rv)
        for x in (*edge.tails, *edge.heads):
            out = kleene_and(out, amap[x].liveness(rv))
        return out

    @cached_property
    def _evidence_universe_value(self) -> frozenset:
        ev: set = set()
        for a in self.atoms:
            ev |= a.warrant.evidence
        for e in self.hyperedges:
            ev |= e.warrant.evidence
        return frozenset(ev)

    def evidence_universe(self) -> frozenset:
        return self._evidence_universe_value

    # --- edits (persistent) --------------------------------------------------------------
    def with_atoms(self, *atoms: Atom) -> "KnowledgeSpace":
        # The registry is shared and mutable; old types may have been withdrawn since
        # construction. Retain full validation until a versioned registry contract exists.
        return replace(self, atoms=self.atoms + tuple(atoms))

    def with_edges(self, *edges: Hyperedge) -> "KnowledgeSpace":
        return replace(self, hyperedges=self.hyperedges + tuple(edges))

    def replace_atom(self, atom: Atom) -> "KnowledgeSpace":
        return replace(self, atoms=tuple(atom if a.atom_id == atom.atom_id else a for a in self.atoms))

    def replace_atom_and_edge(self, atom: Atom, edge: Hyperedge) -> "KnowledgeSpace":
        """Replace one existing atom and edge in one validated immutable-space construction."""
        if atom.atom_id not in self._atom_index:
            raise TypedRejection("UNKNOWN_ATOM", atom.atom_id)
        if edge.edge_id not in self._edge_index:
            raise TypedRejection("UNKNOWN_EDGE", edge.edge_id)
        return replace(
            self,
            atoms=tuple(atom if a.atom_id == atom.atom_id else a for a in self.atoms),
            hyperedges=tuple(edge if e.edge_id == edge.edge_id else e for e in self.hyperedges),
        )

    def without(self, atom_ids: Iterable[str] = (), edge_ids: Iterable[str] = ()) -> "KnowledgeSpace":
        drop_a, drop_e = set(atom_ids), set(edge_ids)
        atoms = tuple(a for a in self.atoms if a.atom_id not in drop_a)
        edges = tuple(e for e in self.hyperedges if e.edge_id not in drop_e and not (e.incident & drop_a))
        return replace(self, atoms=atoms, hyperedges=edges)

    # --- identity ------------------------------------------------------------------------
    def digest(self) -> str:
        # A frozen dataclass does not freeze nested Atom/Hyperedge.meta values.
        # Hash current canonical content, including mutations through as_dict aliases.
        body = {"atoms": [a.as_dict() for a in self.atoms], "hyperedges": [e.as_dict() for e in self.hyperedges]}
        return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()

    def resource_counts(self) -> dict[str, int]:
        warrant_size = sum(len(a.warrant.lower) + len(a.warrant.upper) for a in self.atoms)
        warrant_size += sum(len(e.warrant.lower) + len(e.warrant.upper) for e in self.hyperedges)
        return {"object_count": len(self.atoms), "relation_count": len(self.hyperedges), "warrant_size": warrant_size}


# --------------------------------------------------------------------------------------------
# conjunctive relations are not pairwise (contract §2; M1 A2 hostile)
# --------------------------------------------------------------------------------------------


def pairwise_expansion(edge: Hyperedge) -> tuple[Hyperedge, ...]:
    """The *wrong* reading of a conjunctive relation: one independent pairwise edge per (tail, head).

    Provided only so the hostile test can show it is not equivalent (enabling and navigation both
    differ). Accepting it as equivalent requires an explicit equivalence certificate, never a default.
    """
    out = []
    for t in edge.tails:
        for h in edge.heads:
            out.append(replace(edge, edge_id=f"{edge.edge_id}[{t}->{h}]", tails=(t,), heads=(h,), head_weights=()))
    return tuple(out)


@dataclass(frozen=True, slots=True)
class PairwiseEquivalenceCertificate:
    """Explicit certificate that a hyperedge may be read pairwise on a registered scope."""

    edge_id: str
    scope: Scope
    proof_ref: str


def expand_pairwise(edge: Hyperedge, certificate: PairwiseEquivalenceCertificate | None) -> tuple[Hyperedge, ...]:
    if edge.is_pairwise:
        return (edge,)
    if certificate is None or certificate.edge_id != edge.edge_id or not certificate.proof_ref:
        raise TypedRejection("CONJUNCTIVE_RELATION_NOT_PAIRWISE", edge.edge_id)
    return pairwise_expansion(edge)


# --------------------------------------------------------------------------------------------
# conversion to / from the frozen historical reference types
# --------------------------------------------------------------------------------------------


def from_reference(ks_ref: Any, *, registry: TypeRegistry = DEFAULT_REGISTRY) -> KnowledgeSpace:
    """Lift a ``kso_math_v1.KnowledgeSpace`` (two-valued profiles) into the canonical model."""
    atoms = tuple(
        Atom(a.atom_id, a.atom_type, WarrantProfile.certified(a.profile), quarantined=bool(getattr(a, "quarantined", False)))
        for a in ks_ref.atoms
    )
    edges = tuple(
        Hyperedge(
            e.edge_id,
            tuple(e.tails),
            tuple(e.heads),
            e.relation_type,
            Fraction(e.weight),
            tuple(Fraction(w) for w in (e.head_weights or ())),
            WarrantProfile.certified(e.profile),
        )
        for e in ks_ref.hyperedges
    )
    reg = registry
    for a in atoms:
        if a.atom_type not in reg.atom_types:
            reg = TypeRegistry(set(reg.atom_types) | {a.atom_type}, dict(reg.relation_types))
    for e in edges:
        if e.relation_type not in reg.relation_types:
            from .types import RelationSpec

            reg = TypeRegistry(set(reg.atom_types), {**reg.relation_types, e.relation_type: RelationSpec(e.relation_type)})
    return KnowledgeSpace(atoms, edges, reg)


def to_reference(ks: KnowledgeSpace, ref_module: Any) -> Any:
    """Project the canonical model onto ``kso_math_v1`` types (drops authority/scope/upper)."""
    atoms = tuple(ref_module.Atom(a.atom_id, a.atom_type, a.warrant.lower, a.quarantined) for a in ks.atoms)
    edges = tuple(
        ref_module.Hyperedge(e.edge_id, e.tails, e.heads, e.relation_type, e.weight, e.head_weights, e.warrant.lower)
        for e in ks.hyperedges
    )
    return ref_module.KnowledgeSpace(atoms, edges)


def relation_weights_from(mapping: Mapping[str, Fraction] | None) -> dict[str, Fraction]:
    return {k: Fraction(v) for k, v in (mapping or {}).items()}
