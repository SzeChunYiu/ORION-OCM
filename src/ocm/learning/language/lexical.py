"""Vocabulary / sense acquisition lifecycle (M5 §3): learn a word from one aligned example, use it
in unseen contexts, add a second sense, disambiguate by context, revoke one sense locally, relearn.

Alignment (E1): given an utterance whose interpretation fails with UNKNOWN_LEXEME on exactly one
token, and the demonstrated meaning graph, the unknown token is aligned to the meaning node that no
known lexeme accounts for (label-level alignment under the current inventory).  The result is a
`Lexeme` with one `Sense` whose warrant is exactly the demonstration's evidence — never a guess
from spelling, never from co-occurrence alone (E2 form hypotheses stay UNGROUNDED_FORM_ONLY,
`corpus.py`).  A second aligned example with a *different* aligned node adds a second sense to the
ambiguity set; disambiguation is left to context (M3: readings ⊗ constructions) and clarification.
Revoking one sense's evidence kills that sense only (interval liveness); the lexeme's other senses
and every unrelated lexeme are untouched (KS-T22); relearning from a new source yields a new sense
record with LINEAGE, not a resurrection.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Sequence

from ocm.kso.warrant import Liveness, WarrantProfile

from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import AnalysisStatus, Category, Lexeme, Lexicon, Sense
from ocm.language.meaning import MeaningGraph, MNode
from ocm.language.constructions import Construction

NODE_TYPE_TO_CATEGORY = {"entity": Category.NOUN, "event": Category.VERB, "property": Category.ADJ, "value": Category.NOUN}


class AlignmentStatus(str, Enum):
    ALIGNED = "ALIGNED"
    NO_UNKNOWN_TOKEN = "NO_UNKNOWN_TOKEN"
    TOO_MANY_UNKNOWN = "TOO_MANY_UNKNOWN"
    NO_UNACCOUNTED_NODE = "NO_UNACCOUNTED_NODE"
    AMBIGUOUS_ALIGNMENT = "AMBIGUOUS_ALIGNMENT"


@dataclass(frozen=True)
class Alignment:
    status: AlignmentStatus
    token: str | None = None
    node: MNode | None = None
    candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class LexicalUpdate:
    kind: str                    # NEW_LEXEME | NEW_SENSE | DUPLICATE_SENSE | REFUSED
    lemma: str | None
    sense_id: str | None
    evidence: tuple[str, ...]
    detail: str = ""
    lineage: tuple[str, ...] = ()


def known_labels(lexicon: Lexicon) -> set[str]:
    return {s.concept for lx in lexicon.lexemes.values() for s in lx.senses}


def align(lexicon: Lexicon, utterance: str, meaning: MeaningGraph) -> Alignment:
    """One unknown token ↔ one meaning node no known lexeme accounts for."""
    toks = tokenize(utterance)
    unknown = [t for t in toks if lexicon.analyse(t).status is AnalysisStatus.UNKNOWN_LEXEME]
    if not unknown:
        return Alignment(AlignmentStatus.NO_UNKNOWN_TOKEN)
    if len(set(unknown)) > 1:
        return Alignment(AlignmentStatus.TOO_MANY_UNKNOWN, candidates=tuple(sorted(set(unknown))))
    labels = known_labels(lexicon)
    unaccounted = [n for n in meaning.nodes if n.label and n.label not in labels and n.node_type in NODE_TYPE_TO_CATEGORY]
    if not unaccounted:
        return Alignment(AlignmentStatus.NO_UNACCOUNTED_NODE, token=unknown[0])
    if len(unaccounted) > 1:
        return Alignment(AlignmentStatus.AMBIGUOUS_ALIGNMENT, token=unknown[0], candidates=tuple(n.label for n in unaccounted))
    return Alignment(AlignmentStatus.ALIGNED, unknown[0], unaccounted[0])


def learn_word(lexicon: Lexicon, utterance: str, meaning: MeaningGraph, evidence_id: str, *, source: str = "teacher", lineage: Sequence[str] = ()) -> LexicalUpdate:
    a = align(lexicon, utterance, meaning)
    if a.status is not AlignmentStatus.ALIGNED:
        # a known surface with a *new* aligned concept is a second sense (polysemy), handled below
        if a.status is AlignmentStatus.NO_UNKNOWN_TOKEN:
            return _maybe_new_sense(lexicon, utterance, meaning, evidence_id, source, lineage)
        return LexicalUpdate("REFUSED", a.token, None, (evidence_id,), f"{a.status.value}: {a.candidates}")
    node = a.node
    cat = NODE_TYPE_TO_CATEGORY[node.node_type]
    lemma = a.token
    sense = Sense(f"{lemma}:{node.label}", node.label, node.node_type, WarrantProfile.of({evidence_id}))
    key = f"{lemma}|{cat.value}"
    if key in lexicon.lexemes:
        lx = lexicon.lexemes[key]
        lexicon.add(Lexeme(lx.lemma, lx.category, lx.senses + (sense,), lx.features, lx.warrant, lx.scope))
        return LexicalUpdate("NEW_SENSE", lemma, sense.sense_id, (evidence_id,), f"{source}: {lemma} ↦ {node.label}", tuple(lineage))
    lexicon.add(Lexeme(lemma, cat, (sense,)))
    return LexicalUpdate("NEW_LEXEME", lemma, sense.sense_id, (evidence_id,), f"{source}: {lemma} ↦ {node.label} ({cat.value})", tuple(lineage))


def _maybe_new_sense(lexicon: Lexicon, utterance: str, meaning: MeaningGraph, evidence_id: str, source: str, lineage: Sequence[str]) -> LexicalUpdate:
    """Every token is known, but the meaning names a concept no lexeme covers: attach it as a new
    sense of the token whose current senses' concepts are absent from the meaning (the token that
    is 'unexplained' by the meaning) — one such token required."""
    labels = known_labels(lexicon)
    new_concepts = [n for n in meaning.nodes if n.label and n.label not in labels and n.node_type in NODE_TYPE_TO_CATEGORY]
    if len(new_concepts) != 1:
        return LexicalUpdate("REFUSED", None, None, (evidence_id,), "no single new concept to bind" if not new_concepts else f"AMBIGUOUS_ALIGNMENT: {[n.label for n in new_concepts]}")
    node = new_concepts[0]
    meaning_labels = {n.label for n in meaning.nodes if n.label}
    unexplained = []
    for t in tokenize(utterance):
        for r in lexicon.analyse(t).readings:
            if r.sense is not None and r.category is NODE_TYPE_TO_CATEGORY[node.node_type] and r.sense.concept not in meaning_labels:
                unexplained.append(r.lemma)
    unexplained = sorted(set(unexplained))
    if len(unexplained) != 1:
        return LexicalUpdate("REFUSED", None, None, (evidence_id,), f"cannot align {node.label}: unexplained tokens {unexplained}")
    lemma = unexplained[0]
    cat = NODE_TYPE_TO_CATEGORY[node.node_type]
    lx = lexicon.lexemes[f"{lemma}|{cat.value}"]
    if any(s.concept == node.label for s in lx.senses):
        return LexicalUpdate("DUPLICATE_SENSE", lemma, None, (evidence_id,), "sense already present (evidence not merged)")
    sense = Sense(f"{lemma}:{node.label}", node.label, node.node_type, WarrantProfile.of({evidence_id}))
    lexicon.add(Lexeme(lx.lemma, lx.category, lx.senses + (sense,), lx.features, lx.warrant, lx.scope))
    return LexicalUpdate("NEW_SENSE", lemma, sense.sense_id, (evidence_id,), f"{source}: second sense {lemma} ↦ {node.label}", tuple(lineage))


def relearn_sense(lexicon: Lexicon, lemma: str, category: Category, concept: str, node_type: str, evidence_id: str, *, replaces: str) -> LexicalUpdate:
    """Relearn a revoked sense from a new source: a *new* sense record with lineage to the old one;
    the old record stays dead (never resurrected by the new evidence)."""
    key = f"{lemma}|{category.value}"
    lx = lexicon.lexemes[key]
    sense = Sense(f"{lemma}:{concept}#2", concept, node_type, WarrantProfile.of({evidence_id}))
    lexicon.add(Lexeme(lx.lemma, lx.category, lx.senses + (sense,), lx.features, lx.warrant, lx.scope))
    return LexicalUpdate("NEW_SENSE", lemma, sense.sense_id, (evidence_id,), "relearned", (replaces,))


def competence(lexicon: Lexicon, constructions: Sequence[Construction], probes: Iterable[tuple[str, MeaningGraph]], *, revoked: Iterable = ()) -> dict[str, int]:
    """Exact-meaning competence on probe (utterance, gold) pairs — a learning-curve point."""
    from ocm.language.meaning import isomorphic

    n = ok = 0
    for u, g in probes:
        n += 1
        r = interpret(u, lexicon, constructions, revoked=revoked)
        ok += int(r.verdict is Verdict.INTERPRETED and isomorphic(r.meaning, g))
    return {"n": n, "exact": ok}


def mutant_learn_from_cooccurrence(lexicon: Lexicon, token: str, cooccurring_concept: str, evidence_id: str) -> LexicalUpdate:
    """Planted (M5 §6 hostile): bind a token to a concept because they co-occur in raw text."""
    sense = Sense(f"{token}:{cooccurring_concept}", cooccurring_concept, "entity", WarrantProfile.of({evidence_id}))
    lexicon.add(Lexeme(token, Category.NOUN, (sense,)))
    return LexicalUpdate("NEW_LEXEME", token, sense.sense_id, (evidence_id,), "mutant: co-occurrence treated as grounding")
