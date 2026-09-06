"""Retention, negative transfer and the multilingual preflight (M5 §12–§14).

Retention protocol: after each learning episode evaluate a frozen retention set and report the
vector (new gain, old loss, unrelated change, reopened objects, update work) — never a scalar.

Transfer decisions are *registered* scope moves: a learned object may be applied outside the scope
it was learned in only through `propose_transfer`, which checks (a) the object's registered scope
(language / domain / register), (b) counter-evidence in the target scope, and (c) that the class
of the object is transferable by declaration (semantic structures transfer; word order does not).
Transfer precision = P(beneficial | chosen); harmful-transfer rate is reported separately.

Multilingual preflight: a registered SOV mini-language (same lexicon labels, different order) —
the English transitive construction is language-scoped, so `interpret` on the mini-language yields
UNKNOWN_CONSTRUCTION rather than a wrong role assignment; the SOV construction is learned from
demonstrations over the same {NP, V, NP} order class, and the *meaning graphs* transfer intact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

from ocm.language.constructions import Construction
from ocm.language.interpret import Verdict, interpret
from ocm.language.lexicon import Lexicon
from ocm.language.meaning import MeaningGraph, isomorphic


@dataclass(frozen=True)
class RetentionVector:
    new_gain: int
    old_loss: int
    unrelated_change: int
    reopened_objects: int
    update_work: int
    denominators: dict[str, int]


def evaluate(lexicon: Lexicon, constructions: Sequence[Construction], probes: Iterable[tuple[str, MeaningGraph]], *, revoked: Iterable = (), language: str = "en") -> dict[str, bool]:
    out = {}
    cons = [c for c in constructions if c.language == language]
    for u, g in probes:
        r = interpret(u, lexicon, cons, revoked=revoked)
        out[u] = r.verdict is Verdict.INTERPRETED and isomorphic(r.meaning, g)
    return out


def retention(before: Mapping[str, bool], after: Mapping[str, bool], *, new_set: Iterable[str], old_set: Iterable[str], unrelated_set: Iterable[str], reopened: int, work: int) -> RetentionVector:
    new_set, old_set, unrelated_set = set(new_set), set(old_set), set(unrelated_set)
    gain = sum(1 for u in new_set if after.get(u) and not before.get(u))
    loss = sum(1 for u in old_set if before.get(u) and not after.get(u))
    unrelated = sum(1 for u in unrelated_set if before.get(u) != after.get(u))
    return RetentionVector(gain, loss, unrelated, reopened, work, {"new": len(new_set), "old": len(old_set), "unrelated": len(unrelated_set)})


class TransferClass(str, Enum):
    MEANING_STRUCTURE = "MEANING_STRUCTURE"     # transfers across languages
    LEXEME = "LEXEME"                           # language-scoped
    MORPHOLOGY = "MORPHOLOGY"                   # language-scoped
    WORD_ORDER = "WORD_ORDER"                   # language-scoped, never transfers
    SENSE = "SENSE"                             # domain-scoped
    STYLE = "STYLE"                             # register-scoped, not grammar


TRANSFERABLE_ACROSS_LANGUAGE = {TransferClass.MEANING_STRUCTURE}


@dataclass(frozen=True)
class TransferDecision:
    allowed: bool
    reason: str
    object_id: str
    source_scope: str
    target_scope: str


def propose_transfer(object_id: str, cls: TransferClass, source_scope: str, target_scope: str, *, counter_evidence: Iterable[str] = (), same_kind_of_scope: str = "language") -> TransferDecision:
    if source_scope == target_scope:
        return TransferDecision(True, "same scope", object_id, source_scope, target_scope)
    ce = list(counter_evidence)
    if ce:
        return TransferDecision(False, f"counter-evidence in target scope: {ce}", object_id, source_scope, target_scope)
    if same_kind_of_scope == "language" and cls not in TRANSFERABLE_ACROSS_LANGUAGE:
        return TransferDecision(False, f"{cls.value} is language-scoped; transfer needs demonstrations in {target_scope}", object_id, source_scope, target_scope)
    if same_kind_of_scope == "domain" and cls is TransferClass.SENSE:
        return TransferDecision(False, "domain-specific sense does not transfer to the general domain without evidence", object_id, source_scope, target_scope)
    if cls is TransferClass.STYLE:
        return TransferDecision(False, "a stylistic pattern is not a grammar rule", object_id, source_scope, target_scope)
    return TransferDecision(True, "transferable class, no counter-evidence", object_id, source_scope, target_scope)


def transfer_precision(decisions: Sequence[tuple[TransferDecision, bool]]) -> dict[str, Any]:
    """decisions: (decision, beneficial_in_hindsight).  Precision over chosen transfers; harmful
    rate over all proposals."""
    chosen = [(d, b) for d, b in decisions if d.allowed]
    harmful = sum(1 for d, b in chosen if not b)
    return {"chosen": len(chosen), "beneficial": sum(1 for _, b in chosen if b), "precision": (sum(1 for _, b in chosen if b) / len(chosen)) if chosen else None, "harmful_transfers": harmful, "proposals": len(decisions), "harmful_rate": harmful / len(decisions) if decisions else None}


def mutant_transfer_word_order(c: Construction, target_language: str) -> Construction:
    """Planted (M5 §17 'multilingual transfer reuses English word order despite counterevidence')."""
    return Construction(c.construction_id + f"@{target_language}", c.family, c.pattern, c.template, c.warrant, language=target_language)


def sov_utterance(agent: str, patient: str, verb_past: str) -> str:
    """The registered SOV mini-language: same lexemes, order S O V, no determiners."""
    return f"{agent} {patient} {verb_past}"
