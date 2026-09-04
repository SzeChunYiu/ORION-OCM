"""Constructions: form ↔ meaning pairings as warranted procedures (M3 §1, §5).

A ``Construction`` is a learned pairing between a *form pattern* over token readings (categories
and features, in order) and a *meaning template* (a MeaningGraph fragment with slots bound to
matched readings).  It is a `LearnedProcedure` in the sense of KS-T26: the interpretation
direction (form → meaning) is one reading of the procedure; realisation (meaning → form) is the
inherited L0 direction and is only claimed where the pattern is invertible on its registered scope.

Warrant: a construction carries the ⊗ of its lessons/demonstrations (learner output); a candidate
meaning produced by matching carries ``Λ(construction) ⊗ ⨂ Λ(reading_i)`` (T6 / MEG-26).
Constructions are registered per family (declarative, transitive, intransitive, copular, negation,
yes/no question, wh-question, passive, coordination, relative clause, embedded clause, …); the
inventory is learned/registered data, never a fixed school-grammar list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles

from .lexicon import Category, Reading
from .meaning import MEdge, MNode, MeaningGraph


@dataclass(frozen=True)
class Slot:
    """One position of a form pattern."""

    name: str
    category: Category
    features: tuple[tuple[str, str], ...] = ()     # required features, e.g. (("tense","past"),)
    lemma: str | None = None                       # fixed word (e.g. "by", "not", "did")
    optional: bool = False
    requires: tuple[str, ...] = ()                 # feature keys that must be present (any value), e.g. ("tense",) = finite
    forbids: tuple[str, ...] = ()                  # feature keys that must be absent, e.g. ("tense","participle") = bare form

    def matches(self, r: Reading) -> bool:
        if r.category is not self.category:
            return False
        if self.lemma is not None and r.lemma != self.lemma:
            return False
        have = dict(r.features)
        if any(k not in have for k in self.requires) or any(k in have for k in self.forbids):
            return False
        return all(have.get(k) == v for k, v in self.features)


Template = Callable[[Mapping[str, Reading]], MeaningGraph]


@dataclass(frozen=True)
class Construction:
    construction_id: str
    family: str
    pattern: tuple[Slot, ...]
    template: Template                             # bindings → meaning fragment
    warrant: WarrantProfile
    scope: Scope = field(default_factory=Scope.universal)
    language: str = "en"
    invertible: bool = False                       # realisation direction licensed
    exceptions: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


@dataclass(frozen=True)
class Match:
    construction: Construction
    bindings: tuple[tuple[str, Reading], ...]      # slot name → reading
    span: tuple[int, int]

    @property
    def readings(self) -> tuple[Reading, ...]:
        return tuple(r for _, r in self.bindings)


def _match_from(pattern: Sequence[Slot], tokens: Sequence[Sequence[Reading]], start: int) -> list[tuple[tuple[tuple[str, Reading], ...], int]]:
    """All ways to match the pattern from `start`, choosing one reading per consumed token."""
    results: list[tuple[tuple[tuple[str, Reading], ...], int]] = []

    def rec(pi: int, ti: int, acc: list[tuple[str, Reading]]) -> None:
        if pi == len(pattern):
            results.append((tuple(acc), ti))
            return
        slot = pattern[pi]
        if slot.optional:
            rec(pi + 1, ti, acc)
        if ti >= len(tokens):
            return
        for r in tokens[ti]:
            if slot.matches(r):
                rec(pi + 1, ti + 1, acc + [(slot.name, r)])

    rec(0, start, [])
    return results


def match_constructions(constructions: Iterable[Construction], tokens: Sequence[Sequence[Reading]], *, revoked: Iterable[Hashable] = (), whole: bool = True) -> list[Match]:
    """Every live construction × every binding that consumes the whole token sequence (default)."""
    rv = frozenset(revoked)
    out: list[Match] = []
    for c in constructions:
        if c.liveness(rv) is Liveness.DEAD:
            continue
        for bindings, end in _match_from(c.pattern, tokens, 0):
            if whole and end != len(tokens):
                continue
            out.append(Match(c, bindings, (0, end)))
    return out


@dataclass(frozen=True)
class CandidateMeaning:
    meaning: MeaningGraph
    construction_id: str
    warrant: WarrantProfile
    readings: tuple[Reading, ...]
    score: float | None = None                      # outside the lattice (ranking only)

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


def realise_candidate(m: Match) -> CandidateMeaning:
    """Λ(candidate) = Λ(construction) ⊗ ⨂ Λ(reading_i)  (T6 / MEG-26)."""
    meaning = m.construction.template(dict(m.bindings))
    warrant = meet_all_profiles([m.construction.warrant, *(r.warrant for r in m.readings)])
    return CandidateMeaning(meaning, m.construction.construction_id, warrant, m.readings)


# --------------------------------------------------------------------------------------------
# a small seed inventory of English constructions (registered data; learnable, revisable)
# --------------------------------------------------------------------------------------------


def _entity(r: Reading, node_id: str, extra: tuple[tuple[str, str], ...] = ()) -> MNode:
    return MNode(node_id, "entity", r.sense.concept if r.sense else r.lemma, tuple(sorted(dict(r.features).items())) + extra)


def _event(r: Reading, node_id: str) -> MNode:
    return MNode(node_id, r.sense.node_type if r.sense else "event", r.sense.concept if r.sense else r.lemma)


def _tense_edges(v: Reading, ev_id: str, aux: Reading | None = None) -> list[MEdge]:
    t = dict(v.features).get("tense") or (dict(aux.features).get("tense") if aux is not None else None)
    return [MEdge("TENSE", (ev_id,), (ev_id,), t)] if t else []


def seed_constructions(evidence_prefix: str = "ev:seed") -> tuple[Construction, ...]:
    """Bootstrap constructions marked as SEED knowledge (warranted by their own seed evidence ids;
    to be compared against learned alternatives, M3 §4)."""
    w = lambda name: WarrantProfile.of({f"{evidence_prefix}:{name}"})  # noqa: E731

    def transitive(b: Mapping[str, Reading]) -> MeaningGraph:
        s, v, o = b["subj_n"], b["verb"], b["obj_n"]
        nodes = [_entity(s, "x1", (("definite", "yes"),) if "subj_d" in b else ()), _event(v, "e"), _entity(o, "x2", (("definite", "yes"),) if "obj_d" in b else ())]
        edges = [MEdge("ROLE:agent", ("e",), ("x1",)), MEdge("ROLE:patient", ("e",), ("x2",))] + _tense_edges(v, "e", b.get("aux"))
        if "obj_a" in b:
            nodes.append(MNode("p2", "property", b["obj_a"].lemma))
            edges.append(MEdge("MODIFIES", ("p2",), ("x2",)))
        return MeaningGraph(tuple(nodes), tuple(edges), root="e")

    def intransitive(b: Mapping[str, Reading]) -> MeaningGraph:
        s, v = b["subj_n"], b["verb"]
        return MeaningGraph((_entity(s, "x1"), _event(v, "e")), (MEdge("ROLE:agent", ("e",), ("x1",)), *_tense_edges(v, "e")), root="e")

    def passive(b: Mapping[str, Reading]) -> MeaningGraph:
        s, v, a = b["subj_n"], b["verb"], b["agent_n"]
        nodes = (_entity(s, "x1", (("definite", "yes"),) if "subj_d" in b else ()), _event(v, "e"), _entity(a, "x2", (("definite", "yes"),) if "agent_d" in b else ()))
        aux_t = dict(b["aux"].features).get("tense", "past")
        edges = (MEdge("ROLE:patient", ("e",), ("x1",)), MEdge("ROLE:agent", ("e",), ("x2",)), MEdge("TENSE", ("e",), ("e",), aux_t))
        return MeaningGraph(nodes, edges, root="e")

    def negated_transitive(b: Mapping[str, Reading]) -> MeaningGraph:
        g = transitive(b)
        return MeaningGraph(g.nodes, g.edges + (MEdge("NEGATES", ("e",), ("e",)),), root="e")

    def yes_no(b: Mapping[str, Reading]) -> MeaningGraph:
        g = transitive(b)
        q = MNode("q", "question_variable", None, underspecified=True)
        return MeaningGraph(g.nodes + (q,), g.edges + (MEdge("ASKS", ("q",), ("e",), "polarity"),), root="e")

    def wh_object(b: Mapping[str, Reading]) -> MeaningGraph:
        s, v, o = b["subj_n"], b["verb"], b["obj_n"]
        subj = MNode("x1", "entity", None, underspecified=True) if s.category is Category.PRON else _entity(s, "x1")
        aux_t = dict(b["aux"].features).get("tense", "past")
        nodes = (subj, _event(v, "e"), _entity(o, "x2"), MNode("which", "question_variable", None, underspecified=True))
        edges = (MEdge("ROLE:agent", ("e",), ("x1",)), MEdge("ROLE:patient", ("e",), ("x2",)), MEdge("ASKS", ("which",), ("x2",)), MEdge("TENSE", ("e",), ("e",), aux_t))
        return MeaningGraph(nodes, edges, root="e")

    D, N, V, A = Category.DET, Category.NOUN, Category.VERB, Category.ADJ
    return (
        Construction("en:transitive", "transitive", (Slot("subj_d", D, optional=True), Slot("subj_n", N), Slot("verb", V, requires=("tense",)), Slot("obj_d", D, optional=True), Slot("obj_a", A, optional=True), Slot("obj_n", N)), transitive, w("transitive"), invertible=True),
        Construction("en:intransitive", "intransitive", (Slot("subj_d", D, optional=True), Slot("subj_n", N), Slot("verb", V, requires=("tense",))), intransitive, w("intransitive"), invertible=True),
        Construction("en:passive", "passive", (Slot("subj_d", D, optional=True), Slot("subj_n", N), Slot("aux", Category.AUX, lemma="be"), Slot("verb", V, (("participle", "past"),)), Slot("by", Category.PREP, lemma="by"), Slot("agent_d", D, optional=True), Slot("agent_n", N)), passive, w("passive")),
        Construction("en:negation-transitive", "negation", (Slot("subj_d", D, optional=True), Slot("subj_n", N), Slot("aux", Category.AUX, lemma="do"), Slot("neg", Category.NEG, lemma="not"), Slot("verb", V, forbids=("tense", "participle")), Slot("obj_d", D, optional=True), Slot("obj_n", N)), negated_transitive, w("negation")),
        Construction("en:yesno-transitive", "yes_no_question", (Slot("aux", Category.AUX, lemma="do"), Slot("subj_d", D, optional=True), Slot("subj_n", N), Slot("verb", V, forbids=("tense", "participle")), Slot("obj_d", D, optional=True), Slot("obj_n", N)), yes_no, w("yesno")),
        Construction("en:wh-object", "wh_question", (Slot("wh", Category.WH, lemma="which"), Slot("obj_n", N), Slot("aux", Category.AUX, lemma="do"), Slot("subj_n", Category.PRON), Slot("verb", V, forbids=("tense", "participle"))), wh_object, w("wh")),
    )


def mutant_word_order_swap(c: Construction) -> Construction:
    """Planted (M3 §12 'word-order mutant maps roles incorrectly'): swap agent and patient."""
    def tmpl(b: Mapping[str, Reading]) -> MeaningGraph:
        g = c.template(b)
        swapped = tuple(MEdge("ROLE:patient" if e.relation == "ROLE:agent" else "ROLE:agent" if e.relation == "ROLE:patient" else e.relation, e.tails, e.heads, e.value) for e in g.edges)
        return MeaningGraph(g.nodes, swapped, g.root)

    return Construction(c.construction_id + "#swapped", c.family, c.pattern, tmpl, c.warrant)


def mutant_drop_negation(c: Construction) -> Construction:
    """Planted (M3 §12 'negation dropped')."""
    def tmpl(b: Mapping[str, Reading]) -> MeaningGraph:
        g = c.template(b)
        return MeaningGraph(g.nodes, tuple(e for e in g.edges if e.relation != "NEGATES"), g.root)

    return Construction(c.construction_id + "#noneg", c.family, c.pattern, tmpl, c.warrant)
