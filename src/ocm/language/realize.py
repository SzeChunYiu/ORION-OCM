"""Realisation: meaning graph → surface text through the same constructions and lexicon, gated by
reverse interpretation (M6 §2, §6; MEG-25 semantic half).

The realiser is a *codec*: it has no store handle, only the meaning to express, the lexicon, the
construction inventory and a style request.  For each candidate construction whose template is
invertible on this meaning it fills the slots from the meaning nodes (lexicon in the generation
direction: lemma → form via the live morphology rules, exceptions winning), producing candidate
surfaces.  Every candidate is re-interpreted; it is kept only if the reverse reading is
INTERPRETED with a canonical digest equal to the intended meaning (`Realization.checked`).
Alternatives (active/passive, contraction, pronoun where the workspace says the reference is
safe, discourse connectives) are *variants* chosen by style — never by changing the meaning.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.warrant import Liveness

from .constructions import Construction
from .interpret import Verdict, interpret
from .lexicon import Category, Lexicon, RuleKind
from .meaning import MeaningGraph, canonical


@dataclass(frozen=True)
class Style:
    register: str = "neutral"          # neutral | brief | detailed | formal | casual
    contractions: bool = False
    prefer_passive: bool = False
    pronoun_for: Mapping[str, str] = field(default_factory=dict)   # label → pronoun, when the workspace certifies safety


@dataclass(frozen=True)
class Realization:
    text: str
    construction_id: str
    checked: bool                      # reverse reading equals the intended meaning
    digest: str
    reason: str = ""
    channel: str = "ATOMIC"            # batch 11 K3 (H7): the surface is delivered whole after the reverse check; no prefix is
                                       # ever emitted, so no streaming-safety claim is made (STREAMING needs the K3 prefix criterion)


def _form(lexicon: Lexicon, lemma: str, category: Category, features: Mapping[str, str], revoked: Iterable) -> str | None:
    """Generation direction: the live rule whose features match produces the form; EXCEPTION wins."""
    rv = frozenset(revoked)
    if not features:
        return lemma
    want = dict(features)
    live = [r for r in lexicon.rules if r.category is category and dict(r.features) == want and r.liveness(rv) is Liveness.LIVE]
    for r in live:
        if r.kind is RuleKind.EXCEPTION and lemma in r.lemmas:
            return r.apply(lemma)
    for r in live:
        if r.kind is RuleKind.PRODUCTIVE:
            return r.apply(lemma)
    return None


def _lemma_for(lexicon: Lexicon, label: str, category: Category, revoked: Iterable) -> str | None:
    rv = frozenset(revoked)
    for key, lx in lexicon.lexemes.items():
        if lx.category is category and any(s.concept == label and s.liveness(rv) is Liveness.LIVE for s in lx.senses):
            return lx.lemma
    return None


def _np(lexicon: Lexicon, m: MeaningGraph, node_id: str, style: Style, revoked: Iterable) -> str | None:
    n = m.node(node_id)
    if n.label in style.pronoun_for:
        return style.pronoun_for[n.label]
    lemma = _lemma_for(lexicon, n.label, Category.NOUN, revoked)
    if lemma is None:
        return None
    mods = [m.node(e.tails[0]).label for e in m.edges if e.relation == "MODIFIES" and e.heads == (node_id,)]
    adj = []
    for lab in mods:
        a = _lemma_for(lexicon, lab, Category.ADJ, revoked)
        if a is None:
            return None
        adj.append(a)
    det = "the " if dict(n.features).get("definite") == "yes" else ""
    return det + " ".join(adj + [lemma])


def realize(m: MeaningGraph, lexicon: Lexicon, constructions: Sequence[Construction], *, style: Style = Style(), revoked: Iterable = ()) -> list[Realization]:
    """All checked realisations of a clause meaning, ordered by style preference."""
    rv = frozenset(revoked)
    intended = canonical(m)[1]
    roles = {e.relation: e.heads[0] for e in m.edges if e.relation.startswith("ROLE:")}
    ev = m.node(m.root) if m.root else None
    if ev is None or ev.node_type != "event":
        return []
    verb = _lemma_for(lexicon, ev.label, Category.VERB, rv)
    if verb is None:
        return []
    tense = next((e.value for e in m.edges if e.relation == "TENSE" and e.tails == (m.root,)), None)
    negated = any(e.relation == "NEGATES" for e in m.edges)
    question = any(e.relation == "ASKS" for e in m.edges)
    agent = _np(lexicon, m, roles["ROLE:agent"], style, rv) if "ROLE:agent" in roles else None
    patient = _np(lexicon, m, roles["ROLE:patient"], style, rv) if "ROLE:patient" in roles else None
    cands: list[tuple[str, str]] = []
    if agent and patient and not negated and not question:
        past = _form(lexicon, verb, Category.VERB, {"tense": tense} if tense else {}, rv)
        if past:
            cands.append(("en:transitive", f"{agent} {past} {patient}"))
        pp = _form(lexicon, verb, Category.VERB, {"participle": "past"}, rv)
        if pp:
            cands.append(("en:passive", f"{patient} was {pp} by {agent}"))
    elif agent and patient and negated and not question:
        aux = "didn't" if style.contractions else "did not"
        cands.append(("en:negation-transitive", f"{agent} {aux} {verb} {patient}"))
    elif agent and patient and question:
        cands.append(("en:yesno-transitive", f"did {agent} {verb} {patient}"))
    elif agent and not patient and not negated and not question:
        past = _form(lexicon, verb, Category.VERB, {"tense": tense} if tense else {}, rv)
        if past:
            cands.append(("en:intransitive", f"{agent} {past}"))
    if style.prefer_passive:
        cands.sort(key=lambda c: 0 if c[0] == "en:passive" else 1)
    out: list[Realization] = []
    for cid, text in cands:
        probe = text.replace("didn't", "did not")
        r = interpret(probe, lexicon, constructions, revoked=rv)
        ok = r.verdict is Verdict.INTERPRETED and canonical(r.meaning)[1] == intended
        reason = "" if ok else (r.verdict.value if r.verdict is not Verdict.INTERPRETED else "meaning drift")
        out.append(Realization(text[0].upper() + text[1:] + ("?" if question else "."), cid, ok, intended, reason))
    return out


def best(reals: Sequence[Realization]) -> Realization | None:
    for r in reals:
        if r.checked:
            return r
    return None


def mutant_paraphrase_changes_negation(r: Realization) -> Realization:
    """Planted (M6 §13 'surface paraphraser changes negation/quantity')."""
    t = r.text.replace("did not ", "").replace("didn't ", "")
    return Realization(t, r.construction_id, r.checked, r.digest, "mutant")
