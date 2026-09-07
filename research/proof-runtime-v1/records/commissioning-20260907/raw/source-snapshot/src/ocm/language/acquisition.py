"""Construction acquisition from aligned demonstrations (M3 §5, §8 E1) through the M2 learner.

A construction *family* is registered with a **finite hypothesis class** of form patterns (e.g.
the six orders of {S, V, O} for a transitive clause; the presence/absence and position of a
determiner; the negation particle position) and a registered *query family* (the held-out
compositions the family must agree on).  Each aligned demonstration ``(utterance, meaning)`` is
an example for the version-space learner: a hypothesis is consistent with it iff matching the
utterance under that pattern realises a meaning isomorphic to the demonstrated one.

The learner's rules carry over unchanged (KS-T31): ambiguous → GAP_AMBIGUOUS (no promotion),
contradictory demonstrations → CONTRADICTION (preserved, never averaged), promotion only under
agreement on the query family, warrant = ⊗ of the demonstrations that pinned the hypothesis
(per-input reopening follows MEG-12: revoking one demonstration reopens exactly the utterances
whose every minimal agreement set contains it).  Instruction (E0, "the English transitive clause
is SUBJECT VERB OBJECT") names a hypothesis and is checked against the demonstrations.
Parents: Mitchell 1982 version spaces; inherited L0 (`kso_language_v0.induce_clause_order`).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Sequence

from ocm.kso.warrant import WarrantProfile
from ocm.learning.learner import Experience, ExperienceKind, UpdateKind, UpdateProposal, UpdateStatus, VersionSpaceLearner

from .constructions import Construction, Slot, Template, match_constructions, realise_candidate
from .lexicon import Category, Lexicon, Reading
from .meaning import MeaningGraph, isomorphic


@dataclass(frozen=True)
class Demonstration:
    utterance: str
    meaning: MeaningGraph
    evidence_id: str
    source: str = "teacher"


@dataclass(frozen=True)
class ConstructionFamily:
    """A registered finite class of candidate patterns sharing one template."""

    family: str
    hypotheses: Mapping[str, tuple[Slot, ...]]     # name → pattern
    template: Template
    query_family: tuple[str, ...]                  # held-out utterances every surviving hypothesis must agree on
    language: str = "en"
    helpers: tuple[Construction, ...] = ()         # phrase-producing constructions the family composes over (e.g. NP)


def order_hypotheses(roles: Sequence[tuple[str, Slot]]) -> dict[str, tuple[Slot, ...]]:
    """All orders of the given role slots — e.g. the six S/V/O permutations."""
    out: dict[str, tuple[Slot, ...]] = {}
    for perm in itertools.permutations(roles):
        out["".join(name for name, _ in perm)] = tuple(slot for _, slot in perm)
    return out


def _parse_under(pattern: tuple[Slot, ...], template: Template, lexicon: Lexicon, utterance: str, family: str, helpers: Sequence[Construction] = ()):
    from .interpret import tokenize

    toks = tokenize(utterance)
    per = [list(lexicon.analyse(t).readings) for t in toks]
    c = Construction(f"{family}:hyp", family, pattern, template, WarrantProfile.one())
    ms = match_constructions([c, *helpers], per)
    return [realise_candidate(m).meaning for m in ms if m.construction.construction_id == c.construction_id]


def acquire(family: ConstructionFamily, lexicon: Lexicon, demonstrations: Sequence[Demonstration], *, instruction: tuple[str, str] | None = None) -> UpdateProposal:
    """Run the version-space learner over the family's finite class.  ``instruction`` =
    (hypothesis_name, evidence_id) for an E0 lesson."""
    # hypothesis as a function: utterance → canonical meaning digest set (None = no parse)
    def make(pattern: tuple[Slot, ...]) -> Callable[[str], Any]:
        def h(u: str):
            ms = _parse_under(pattern, family.template, lexicon, u, family.family, family.helpers)
            from .meaning import canonical

            return tuple(sorted(canonical(m)[1] for m in ms)) if ms else None
        return h

    hyps = {name: make(p) for name, p in family.hypotheses.items()}
    lr = VersionSpaceLearner(f"construction:{family.family}", hyps, family.query_family)
    for i, d in enumerate(demonstrations):
        from .meaning import canonical

        target = (canonical(d.meaning)[1],)
        lr.observe(Experience(f"demo{i}", ExperienceKind.DEMONSTRATION, d.evidence_id, f"construction:{family.family}", {"pairs": [(d.utterance, target)]}, d.source))
    if instruction is not None:
        name, eid = instruction
        lr.observe(Experience("lesson", ExperienceKind.INSTRUCTION, eid, f"construction:{family.family}", {"hypothesis": name}, "grammar"))
    proposals = lr.propose_updates()
    return proposals[-1]


def construction_from_proposal(family: ConstructionFamily, proposal: UpdateProposal, construction_id: str | None = None) -> Construction:
    if proposal.kind is not UpdateKind.OBJECT or proposal.status is not UpdateStatus.PASS:
        raise ValueError(f"proposal is not a promotable object: {proposal.status.value}")
    name = proposal.payload["hypothesis"]
    return Construction(construction_id or f"{family.language}:{family.family}:{name}", family.family, family.hypotheses[name], family.template, proposal.warrant, language=family.language, lineage=proposal.lineage)


def mutant_transfer_to_other_language(c: Construction, language: str) -> Construction:
    """Planted (L0 stress 9): apply an English construction to a registered SOV language by relabel
    alone — refused by scope: constructions are language-scoped and transfer needs an adapter."""
    return Construction(c.construction_id + f"@{language}", c.family, c.pattern, c.template, c.warrant, language=language)


def scope_check(c: Construction, utterance_language: str) -> bool:
    return c.language == utterance_language
