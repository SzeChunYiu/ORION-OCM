"""MeaningGraph.v1 — an extensible meaning representation as a typed hypergraph fragment (M3 §2).

A meaning is a *fragment* of the knowledge space: nodes (entities, events, states, properties,
quantifiers, question variables, propositions) and typed relations (semantic roles, modifiers,
negation, modality, tense/aspect, coreference, scope, coordination, embedding, reported speech,
asked variables).  The vocabulary is registered data on the KSO type registry (M1 A1) — replaceable,
never constitutional; AMR/UD/PropBank are parents and annotation sources, not the ontology.

Canonical form (MEG-24): ``canonical(g)`` is an isomorphism-invariant relabelling (exhaustive
over vertex orderings for bounded fragments, |V| ≤ MAX_EXACT_CANONICAL) so that two parsers
producing isomorphic meanings yield byte-identical seeds: η = seed ∘ can, which makes KS-T10a's
"equal seeds ⇒ identical extraction" apply to any two parsers that agree on the meaning up to
isomorphism.  A Weisfeiler–Leman-style hash is *not* canonical (planted collision witness).
Parents: canonical graph labelling (nauty / McKay — candidate parent, unverified); AMR (Banarescu
et al. 2013 — annotation parent, not vendored).  No novelty claimed.
"""
from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from ocm.kso.ids import canonical_json
from ocm.kso.types import RelationSpec, TypeRegistry
from ocm.kso.warrant import CannotCheck

NODE_TYPES: tuple[str, ...] = ("entity", "event", "state", "property", "quantifier", "question_variable", "proposition", "value")
ROLES: tuple[str, ...] = ("agent", "patient", "theme", "recipient", "experiencer", "instrument", "location", "source", "goal", "time", "manner", "possessor", "attribute")
RELATION_TYPES: tuple[str, ...] = tuple(f"ROLE:{r}" for r in ROLES) + (
    "MODIFIES", "NEGATES", "MODALITY", "TENSE", "ASPECT", "COREF", "SCOPES_OVER", "COORDINATES", "EMBEDS", "REPORTED_BY", "ASKS", "EQUALS", "COMPARES", "CONDITIONS", "CAUSES",
)
MAX_EXACT_CANONICAL = 7


def meaning_registry(base: TypeRegistry | None = None) -> TypeRegistry:
    """The KSO type registry extended with the meaning vocabulary (data, not code)."""
    reg = base or TypeRegistry()
    for t in NODE_TYPES:
        reg.register_atom_type(f"meaning:{t}")
    for r in RELATION_TYPES:
        reg.register_relation_type(RelationSpec(r, dependency=False))
    return reg


@dataclass(frozen=True)
class MNode:
    node_id: str
    node_type: str                       # one of NODE_TYPES
    label: str | None = None             # lemma / concept / literal; None for unresolved
    features: tuple[tuple[str, str], ...] = ()   # e.g. (("number","plural"),("definite","yes"))
    underspecified: bool = False         # M3 §2 "uncertain/underspecified nodes"

    def __post_init__(self) -> None:
        if self.node_type not in NODE_TYPES:
            raise ValueError(f"unregistered meaning node type {self.node_type}")

    def colour(self) -> str:
        return canonical_json({"t": self.node_type, "l": self.label, "f": sorted(self.features), "u": self.underspecified})


@dataclass(frozen=True)
class MEdge:
    relation: str
    tails: tuple[str, ...]
    heads: tuple[str, ...]
    value: str | None = None             # e.g. MODALITY value "may", TENSE "past"

    def __post_init__(self) -> None:
        if self.relation not in RELATION_TYPES:
            raise ValueError(f"unregistered meaning relation {self.relation}")
        if not self.tails or not self.heads:
            raise ValueError("meaning edge needs tails and heads")


@dataclass(frozen=True)
class MeaningGraph:
    nodes: tuple[MNode, ...]
    edges: tuple[MEdge, ...]
    root: str | None = None              # the top proposition / event, if any

    def __post_init__(self) -> None:
        ids = [n.node_id for n in self.nodes]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate meaning node id")
        known = set(ids)
        for e in self.edges:
            if not set(e.tails) | set(e.heads) <= known:
                raise ValueError(f"edge {e.relation} references an unknown node")
        if self.root is not None and self.root not in known:
            raise ValueError("root is not a node")

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(n.node_id for n in self.nodes)

    def node(self, node_id: str) -> MNode:
        return next(n for n in self.nodes if n.node_id == node_id)

    def as_dict(self) -> dict[str, Any]:
        return {"nodes": [{"id": n.node_id, "type": n.node_type, "label": n.label, "features": sorted(n.features), "underspecified": n.underspecified} for n in self.nodes], "edges": [{"rel": e.relation, "tails": list(e.tails), "heads": list(e.heads), "value": e.value} for e in self.edges], "root": self.root}

    def relabel(self, mapping: Mapping[str, str]) -> "MeaningGraph":
        return MeaningGraph(
            tuple(MNode(mapping[n.node_id], n.node_type, n.label, n.features, n.underspecified) for n in self.nodes),
            tuple(MEdge(e.relation, tuple(mapping[t] for t in e.tails), tuple(mapping[h] for h in e.heads), e.value) for e in self.edges),
            None if self.root is None else mapping[self.root],
        )


# --------------------------------------------------------------------------------------------
# canonical form (exact, bounded)
# --------------------------------------------------------------------------------------------


def _encoding(g: MeaningGraph, order: tuple[str, ...]) -> str:
    """A total encoding of g under a given vertex order (nodes renamed n0..nk in that order)."""
    mapping = {v: f"n{i}" for i, v in enumerate(order)}
    nodes = [(mapping[n.node_id], n.colour()) for n in g.nodes]
    nodes.sort()
    edges = sorted((e.relation, tuple(mapping[t] for t in e.tails), tuple(mapping[h] for h in e.heads), e.value or "") for e in g.edges)
    root = None if g.root is None else mapping[g.root]
    return canonical_json({"nodes": nodes, "edges": edges, "root": root})


def canonical(g: MeaningGraph) -> tuple[MeaningGraph, str]:
    """Exact canonical form: the lexicographically least encoding over all vertex orderings that
    respect the colour partition (orderings are enumerated within colour classes only — the
    canonical form is still exact because encodings of orderings that mix colour classes are
    never minimal below a colour-sorted one under the node-first lexicographic key).
    Bounded to |V| ≤ MAX_EXACT_CANONICAL; larger fragments are CANNOT_CHECK (a scalable canonical
    labeller — nauty — is the candidate parent)."""
    if len(g.nodes) > MAX_EXACT_CANONICAL:
        raise CannotCheck(f"exact canonical form bounded to {MAX_EXACT_CANONICAL} nodes; fragment has {len(g.nodes)}")
    by_colour: dict[str, list[str]] = {}
    for n in g.nodes:
        by_colour.setdefault(n.colour(), []).append(n.node_id)
    classes = [by_colour[c] for c in sorted(by_colour)]
    best: tuple[str, tuple[str, ...]] | None = None
    for perms in itertools.product(*(itertools.permutations(c) for c in classes)):
        order = tuple(v for block in perms for v in block)
        enc = _encoding(g, order)
        if best is None or enc < best[0]:
            best = (enc, order)
    assert best is not None
    enc, order = best
    mapping = {v: f"n{i}" for i, v in enumerate(order)}
    return g.relabel(mapping), hashlib.sha256(enc.encode("utf-8")).hexdigest()


def isomorphic(a: MeaningGraph, b: MeaningGraph) -> bool:
    return canonical(a)[1] == canonical(b)[1]


def seed_from_meaning(g: MeaningGraph, bind: Mapping[str, str]) -> dict[str, Any]:
    """η = seed ∘ can: the committed seed is a function of the canonical form and the binding of
    canonical node ids to knowledge-space atoms (unbound nodes are typed rejections upstream)."""
    can, digest = canonical(g)
    parts = []
    for n in can.nodes:
        if n.node_id in bind:
            parts.append({"node": n.node_id, "type": n.node_type, "ref": bind[n.node_id]})
    return {"canonical_digest": digest, "parts": parts}


def wl1_hash(g: MeaningGraph, rounds: int = 3) -> str:
    """Weisfeiler–Leman-1 style hash — NOT canonical (the planted mutant for MEG-24)."""
    colours = {n.node_id: hashlib.sha256(n.colour().encode()).hexdigest()[:12] for n in g.nodes}
    for _ in range(rounds):
        nxt = {}
        for n in g.nodes:
            neigh = sorted(f"{e.relation}:{colours[o]}" for e in g.edges for o in (*e.tails, *e.heads) if n.node_id in (*e.tails, *e.heads) and o != n.node_id)
            nxt[n.node_id] = hashlib.sha256((colours[n.node_id] + "|" + "|".join(neigh)).encode()).hexdigest()[:12]
        colours = nxt
    return hashlib.sha256("|".join(sorted(colours.values())).encode()).hexdigest()


def wl_collision_witness() -> tuple[MeaningGraph, MeaningGraph]:
    """Two non-isomorphic fragments with the same WL-1 hash: a 6-cycle vs two 3-cycles of
    identical-coloured entities under COORDINATES (the classic regular-graph collision)."""
    def cycle(ids: list[str], prefix: str) -> tuple[list[MNode], list[MEdge]]:
        nodes = [MNode(f"{prefix}{i}", "entity", "x") for i in ids]
        edges = [MEdge("COORDINATES", (f"{prefix}{ids[i]}",), (f"{prefix}{ids[(i + 1) % len(ids)]}",)) for i in range(len(ids))]
        return nodes, edges

    n1, e1 = cycle(list("012345"), "a")
    n2a, e2a = cycle(list("012"), "b")
    n2b, e2b = cycle(list("345"), "b")
    return MeaningGraph(tuple(n1), tuple(e1)), MeaningGraph(tuple(n2a + n2b), tuple(e2a + e2b))


# --------------------------------------------------------------------------------------------
# the required M3 example meanings (§2), built by hand as fixtures
# --------------------------------------------------------------------------------------------


def example_meanings() -> dict[str, MeaningGraph]:
    robot = MNode("robot", "entity", "robot", (("definite", "yes"),))
    door = MNode("door", "entity", "door", (("definite", "yes"),))
    red = MNode("red", "property", "red")
    opened = MNode("open", "event", "open")
    mary = MNode("mary", "entity", "Mary")
    repair = MNode("repair", "event", "repair")
    john = MNode("john", "entity", "John")
    think = MNode("think", "state", "think")
    leave = MNode("leave", "event", "leave")
    box = MNode("box", "entity", "box")
    key = MNode("key", "entity", "key")
    contain = MNode("contain", "state", "contain")
    every = MNode("every", "quantifier", "every")
    atleast1 = MNode("atleast1", "quantifier", "at_least_one")
    which = MNode("which", "question_variable", None, underspecified=True)
    it = MNode("it", "entity", None, underspecified=True)
    tomorrow = MNode("tomorrow", "value", "tomorrow")
    active = MeaningGraph((robot, door, red, opened), (MEdge("ROLE:agent", ("open",), ("robot",)), MEdge("ROLE:patient", ("open",), ("door",)), MEdge("MODIFIES", ("red",), ("door",)), MEdge("TENSE", ("open",), ("open",), "past")), root="open")
    passive = MeaningGraph((door, robot, opened), (MEdge("ROLE:patient", ("open",), ("door",)), MEdge("ROLE:agent", ("open",), ("robot",)), MEdge("TENSE", ("open",), ("open",), "past")), root="open")
    return {
        "the robot opened the red door": active,
        "the door was opened by the robot": passive,
        "did the robot open the door": MeaningGraph((robot, door, opened, MNode("q", "question_variable", None, underspecified=True)), (MEdge("ROLE:agent", ("open",), ("robot",)), MEdge("ROLE:patient", ("open",), ("door",)), MEdge("TENSE", ("open",), ("open",), "past"), MEdge("ASKS", ("q",), ("open",), "polarity")), root="open"),
        "the robot did not open the door": MeaningGraph((robot, door, opened), (MEdge("ROLE:agent", ("open",), ("robot",)), MEdge("ROLE:patient", ("open",), ("door",)), MEdge("TENSE", ("open",), ("open",), "past"), MEdge("NEGATES", ("open",), ("open",))), root="open"),
        "the robot might open the door tomorrow": MeaningGraph((robot, door, opened, tomorrow), (MEdge("ROLE:agent", ("open",), ("robot",)), MEdge("ROLE:patient", ("open",), ("door",)), MEdge("MODALITY", ("open",), ("open",), "may"), MEdge("ROLE:time", ("open",), ("tomorrow",)), MEdge("TENSE", ("open",), ("open",), "future")), root="open"),
        "the robot that mary repaired opened the door": MeaningGraph((robot, door, opened, mary, repair), (MEdge("ROLE:agent", ("open",), ("robot",)), MEdge("ROLE:patient", ("open",), ("door",)), MEdge("ROLE:agent", ("repair",), ("mary",)), MEdge("ROLE:patient", ("repair",), ("robot",)), MEdge("EMBEDS", ("robot",), ("repair",)), MEdge("TENSE", ("open",), ("open",), "past"), MEdge("TENSE", ("repair",), ("repair",), "past")), root="open"),
        "john thinks mary may leave": MeaningGraph((john, mary, think, leave), (MEdge("ROLE:experiencer", ("think",), ("john",)), MEdge("EMBEDS", ("think",), ("leave",)), MEdge("ROLE:agent", ("leave",), ("mary",)), MEdge("MODALITY", ("leave",), ("leave",), "may"), MEdge("REPORTED_BY", ("leave",), ("john",))), root="think"),
        "every red box contains at least one key": MeaningGraph((box, key, red, contain, every, atleast1), (MEdge("MODIFIES", ("red",), ("box",)), MEdge("SCOPES_OVER", ("every",), ("box",)), MEdge("SCOPES_OVER", ("atleast1",), ("key",)), MEdge("SCOPES_OVER", ("every",), ("atleast1",)), MEdge("ROLE:agent", ("contain",), ("box",)), MEdge("ROLE:theme", ("contain",), ("key",))), root="contain"),
        "which door did it open": MeaningGraph((it, MNode("door_q", "entity", "door"), opened, which), (MEdge("ROLE:agent", ("open",), ("it",)), MEdge("ROLE:patient", ("open",), ("door_q",)), MEdge("ASKS", ("which",), ("door_q",)), MEdge("TENSE", ("open",), ("open",), "past")), root="open"),
    }
