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
class Phrase:
    """A sub-construction's output occupying a span: its meaning fragment plus the head reading
    (so a clause construction can bind a whole noun phrase as one argument)."""

    phrase_type: str                     # e.g. "NP"
    head: "Reading"
    meaning: MeaningGraph
    head_node: str                       # the node id in `meaning` that stands for the phrase
    warrant: WarrantProfile
    span: tuple[int, int]
    construction_id: str


@dataclass(frozen=True)
class Slot:
    """One position of a form pattern: a token reading, or (``phrase``) a sub-construction's phrase."""

    name: str
    category: Category
    features: tuple[tuple[str, str], ...] = ()     # required features, e.g. (("tense","past"),)
    lemma: str | None = None                       # fixed word (e.g. "by", "not", "did")
    optional: bool = False
    requires: tuple[str, ...] = ()                 # feature keys that must be present (any value), e.g. ("tense",) = finite
    forbids: tuple[str, ...] = ()                  # feature keys that must be absent, e.g. ("tense","participle") = bare form
    phrase: str | None = None                      # if set, the slot is filled by a Phrase of this type (recursive)

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
    produces: str | None = None                    # phrase type this construction builds (e.g. "NP"); None = clause level
    head_slot: str | None = None                   # slot whose reading heads the produced phrase
    head_node: str = "x"                           # node id of the phrase head in the template output

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


@dataclass(frozen=True)
class Match:
    construction: Construction
    bindings: tuple[tuple[str, Any], ...]          # slot name → Reading | Phrase
    span: tuple[int, int]

    @property
    def readings(self) -> tuple[Reading, ...]:
        out: list[Reading] = []
        for _, v in self.bindings:
            out.append(v.head if isinstance(v, Phrase) else v)
        return tuple(out)

    @property
    def parts(self) -> tuple[Any, ...]:
        return tuple(v for _, v in self.bindings)


Binding = "Reading | Phrase"


def _match_from(pattern: Sequence[Slot], tokens: Sequence[Sequence[Reading]], start: int, phrases: Mapping[tuple[int, int], Sequence["Phrase"]] | None = None) -> list[tuple[tuple[tuple[str, Any], ...], int]]:
    """All ways to match the pattern from `start`, choosing one reading per consumed token or one
    sub-construction phrase per consumed span (recursive composition)."""
    results: list[tuple[tuple[tuple[str, Any], ...], int]] = []
    phrases = phrases or {}

    def rec(pi: int, ti: int, acc: list[tuple[str, Any]]) -> None:
        if pi == len(pattern):
            results.append((tuple(acc), ti))
            return
        slot = pattern[pi]
        if slot.optional:
            rec(pi + 1, ti, acc)
        if ti >= len(tokens):
            return
        if slot.phrase is not None:
            for (a, b), phs in phrases.items():
                if a != ti:
                    continue
                for ph in phs:
                    if ph.phrase_type == slot.phrase:
                        rec(pi + 1, b, acc + [(slot.name, ph)])
            return
        for r in tokens[ti]:
            if slot.matches(r):
                rec(pi + 1, ti + 1, acc + [(slot.name, r)])

    rec(0, start, [])
    return results


def phrase_table(constructions: Iterable["Construction"], tokens: Sequence[Sequence[Reading]], *, revoked: Iterable[Hashable] = ()) -> dict[tuple[int, int], list["Phrase"]]:
    """Bottom-up: every phrase-producing construction (``produces`` set) over every span."""
    rv = frozenset(revoked)
    table: dict[tuple[int, int], list[Phrase]] = {}
    n = len(tokens)
    producers = [c for c in constructions if c.produces is not None and c.liveness(rv) is not Liveness.DEAD]
    for length in range(1, n + 1):
        for start in range(0, n - length + 1):
            for c in producers:
                for bindings, end in _match_from(c.pattern, tokens, start, table):
                    if end != start + length:
                        continue
                    b = dict(bindings)
                    meaning = c.template(b)
                    head = b[c.head_slot] if c.head_slot else next(v for v in b.values() if isinstance(v, Reading))
                    parts = [c.warrant] + [v.warrant for v in b.values()]
                    table.setdefault((start, end), []).append(Phrase(c.produces, head, meaning, c.head_node, meet_all_profiles(parts), (start, end), c.construction_id))
    return table


def match_constructions(constructions: Iterable["Construction"], tokens: Sequence[Sequence[Reading]], *, revoked: Iterable[Hashable] = (), whole: bool = True) -> list["Match"]:
    """Every live clause-level construction × every binding that consumes the whole token sequence;
    phrase slots are filled from the bottom-up phrase table (recursive composition)."""
    rv = frozenset(revoked)
    cons = list(constructions)
    table = phrase_table(cons, tokens, revoked=rv)
    out: list[Match] = []
    for c in cons:
        if c.produces is not None or c.liveness(rv) is Liveness.DEAD:
            continue
        for bindings, end in _match_from(c.pattern, tokens, 0, table):
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
    warrant = meet_all_profiles([m.construction.warrant, *(v.warrant for v in m.parts)])   # a phrase carries its own ⊗
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


def _arg(b: Mapping[str, Any], slot: str, node_id: str) -> tuple[list[MNode], list[MEdge], str]:
    """An argument slot filled by an NP phrase (recursive) or a bare noun reading: returns the
    nodes/edges to merge (relabelled under `node_id`) and the id of the argument's head node."""
    v = b[slot]
    if isinstance(v, Phrase):
        mapping = {n.node_id: (node_id if n.node_id == v.head_node else f"{node_id}.{n.node_id}") for n in v.meaning.nodes}
        g = v.meaning.relabel(mapping)
        return list(g.nodes), list(g.edges), node_id
    return [_entity(v, node_id)], [], node_id


def seed_constructions(evidence_prefix: str = "ev:seed") -> tuple[Construction, ...]:
    """Bootstrap constructions marked as SEED knowledge (warranted by their own seed evidence ids;
    to be compared against learned alternatives, M3 §4).  Noun phrases are their own recursive
    construction (``produces="NP"``); clause constructions take NP phrases as arguments."""
    w = lambda name: WarrantProfile.of({f"{evidence_prefix}:{name}"})  # noqa: E731

    def np(b: Mapping[str, Any]) -> MeaningGraph:
        n = b["n"]
        feats = (("definite", "yes"),) if "d" in b else ()
        nodes = [_entity(n, "x", feats)]
        edges: list[MEdge] = []
        if "a" in b:
            nodes.append(MNode("p", "property", b["a"].sense.concept if b["a"].sense else b["a"].lemma))
            edges.append(MEdge("MODIFIES", ("p",), ("x",)))
        return MeaningGraph(tuple(nodes), tuple(edges), root="x")

    def clause(b: Mapping[str, Any], *, negated: bool = False, question: bool = False) -> MeaningGraph:
        v = b["verb"]
        n1, e1, s_id = _arg(b, "subj", "x1")
        n2, e2, o_id = _arg(b, "obj", "x2")
        nodes = n1 + [_event(v, "e")] + n2
        edges = e1 + e2 + [MEdge("ROLE:agent", ("e",), (s_id,)), MEdge("ROLE:patient", ("e",), (o_id,))] + _tense_edges(v, "e", b.get("aux"))
        if negated:
            edges.append(MEdge("NEGATES", ("e",), ("e",)))
        if question:
            nodes.append(MNode("q", "question_variable", None, underspecified=True))
            edges.append(MEdge("ASKS", ("q",), ("e",), "polarity"))
        return MeaningGraph(tuple(nodes), tuple(edges), root="e")

    def intransitive(b: Mapping[str, Any]) -> MeaningGraph:
        n1, e1, s_id = _arg(b, "subj", "x1")
        v = b["verb"]
        return MeaningGraph(tuple(n1 + [_event(v, "e")]), tuple(e1 + [MEdge("ROLE:agent", ("e",), (s_id,))] + _tense_edges(v, "e")), root="e")

    def passive(b: Mapping[str, Any]) -> MeaningGraph:
        n1, e1, s_id = _arg(b, "subj", "x1")
        n2, e2, a_id = _arg(b, "agent", "x2")
        v = b["verb"]
        aux_t = dict(b["aux"].features).get("tense", "past")
        nodes = n1 + [_event(v, "e")] + n2
        edges = e1 + e2 + [MEdge("ROLE:patient", ("e",), (s_id,)), MEdge("ROLE:agent", ("e",), (a_id,)), MEdge("TENSE", ("e",), ("e",), aux_t)]
        return MeaningGraph(tuple(nodes), tuple(edges), root="e")

    def wh_object(b: Mapping[str, Any]) -> MeaningGraph:
        s, v, o = b["subj_n"], b["verb"], b["obj_n"]
        subj = MNode("x1", "entity", None, underspecified=True) if s.category is Category.PRON else _entity(s, "x1")
        aux_t = dict(b["aux"].features).get("tense", "past")
        nodes = (subj, _event(v, "e"), _entity(o, "x2"), MNode("which", "question_variable", None, underspecified=True))
        edges = (MEdge("ROLE:agent", ("e",), ("x1",)), MEdge("ROLE:patient", ("e",), ("x2",)), MEdge("ASKS", ("which",), ("x2",)), MEdge("TENSE", ("e",), ("e",), aux_t))
        return MeaningGraph(nodes, edges, root="e")

    D, N, V, A = Category.DET, Category.NOUN, Category.VERB, Category.ADJ
    NP = lambda name: Slot(name, N, phrase="NP")  # noqa: E731
    return (
        Construction("en:np", "noun_phrase", (Slot("d", D, optional=True), Slot("a", A, optional=True), Slot("n", N)), np, w("np"), produces="NP", head_slot="n", head_node="x"),
        Construction("en:transitive", "transitive", (NP("subj"), Slot("verb", V, requires=("tense",)), NP("obj")), lambda b: clause(b), w("transitive"), invertible=True),
        Construction("en:intransitive", "intransitive", (NP("subj"), Slot("verb", V, requires=("tense",))), intransitive, w("intransitive"), invertible=True),
        Construction("en:passive", "passive", (NP("subj"), Slot("aux", Category.AUX, lemma="be"), Slot("verb", V, (("participle", "past"),)), Slot("by", Category.PREP, lemma="by"), NP("agent")), passive, w("passive")),
        Construction("en:negation-transitive", "negation", (NP("subj"), Slot("aux", Category.AUX, lemma="do"), Slot("neg", Category.NEG, lemma="not"), Slot("verb", V, forbids=("tense", "participle")), NP("obj")), lambda b: clause(b, negated=True), w("negation")),
        Construction("en:yesno-transitive", "yes_no_question", (Slot("aux", Category.AUX, lemma="do"), NP("subj"), Slot("verb", V, forbids=("tense", "participle")), NP("obj")), lambda b: clause(b, question=True), w("yesno")),
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
