"""The interpretation pipeline (M3 §6–§7): utterance → readings → matches → candidate meanings →
verdict → grounding record.

    INTERPRETED(meaning)   exactly one LIVE candidate and none UNKNOWN (T6 `select`)
    AMBIGUOUS([...])       several LIVE, or any UNKNOWN — retained, never forced (→ CLARIFY)
    UNKNOWN_CONSTRUCTION   readings exist but no construction consumes the utterance (→ LEARN)
    UNKNOWN_LEXEME         some token has no live reading (→ LEARN)
    NEEDS_CONTEXT          an underspecified node (pronoun, wh) has no binding candidate
    CONTRADICTION          the meaning violates a registered nogood
    CANNOT_CHECK           a required check could not run

Ranking (a score outside the lattice) may order candidates for a clarification question; it never
collapses them (MEG-26).  Grounding (MEG-05): a successful parse yields a `said(u,p)` OBSERVATION
record with `speaker` authority and conversation scope — never world truth; promotion to machine
knowledge is a separate admit transaction under the authority meet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Hashable, Iterable, Mapping, Sequence

from ocm.kso.nogoods import NogoodSet
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile

from .constructions import CandidateMeaning, Construction, match_constructions, realise_candidate
from .lexicon import Analysis, AnalysisStatus, Lexicon, Reading
from .meaning import MeaningGraph, canonical


class Verdict(str, Enum):
    INTERPRETED = "INTERPRETED"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN_CONSTRUCTION = "UNKNOWN_CONSTRUCTION"
    UNKNOWN_LEXEME = "UNKNOWN_LEXEME"
    NEEDS_CONTEXT = "NEEDS_CONTEXT"
    CONTRADICTION = "CONTRADICTION"
    CANNOT_CHECK = "CANNOT_CHECK"


def tokenize(utterance: str) -> list[str]:
    out = []
    for raw in utterance.strip().split():
        w = raw.lower().strip(".,!?;:")
        if w:
            out.append(w)
    return out


@dataclass(frozen=True)
class SaidRecord:
    """MEG-05 layer 1: what was uttered, as an OBSERVATION with speaker authority."""

    utterance: str
    speaker: str
    meaning_digest: str
    authority: Authority
    scope: Scope
    channel: str = "OBSERVATION"


@dataclass(frozen=True)
class Interpretation:
    utterance: str
    verdict: Verdict
    candidates: tuple[CandidateMeaning, ...]
    analyses: tuple[Analysis, ...]
    reason: str = ""
    said: SaidRecord | None = None

    @property
    def meaning(self) -> MeaningGraph | None:
        return self.candidates[0].meaning if self.verdict is Verdict.INTERPRETED else None


def select(cands: Sequence[CandidateMeaning], revoked: Iterable[Hashable]) -> tuple[Verdict, tuple[CandidateMeaning, ...]]:
    rv = frozenset(revoked)
    live = [c for c in cands if c.liveness(rv) is Liveness.LIVE]
    unknown = [c for c in cands if c.liveness(rv) is Liveness.UNKNOWN]
    if len(live) == 1 and not unknown:
        return Verdict.INTERPRETED, (live[0],)
    if live or unknown:
        return Verdict.AMBIGUOUS, tuple(live + unknown)
    return Verdict.UNKNOWN_CONSTRUCTION, ()


def interpret(
    utterance: str,
    lexicon: Lexicon,
    constructions: Iterable[Construction],
    *,
    speaker: str = "user",
    conversation: str = "conv",
    revoked: Iterable[Hashable] = (),
    nogoods: NogoodSet | None = None,
    context_bindings: Mapping[str, str] | None = None,
    scorer=None,
) -> Interpretation:
    rv = frozenset(revoked)
    tokens = tokenize(utterance)
    analyses = tuple(lexicon.analyse(t, rv) for t in tokens)
    if any(a.status is AnalysisStatus.UNKNOWN_LEXEME for a in analyses):
        bad = [a.token for a in analyses if a.status is AnalysisStatus.UNKNOWN_LEXEME]
        return Interpretation(utterance, Verdict.UNKNOWN_LEXEME, (), analyses, f"unknown: {bad}")
    if any(a.status is AnalysisStatus.NO_LIVE_READING for a in analyses):
        bad = [a.token for a in analyses if a.status is AnalysisStatus.NO_LIVE_READING]
        return Interpretation(utterance, Verdict.UNKNOWN_LEXEME, (), analyses, f"no live reading: {bad}")
    per_token: list[list[Reading]] = [list(a.readings) for a in analyses]
    matches = match_constructions(constructions, per_token, revoked=rv)
    if not matches:
        return Interpretation(utterance, Verdict.UNKNOWN_CONSTRUCTION, (), analyses, "no construction consumes the utterance")
    cands = [realise_candidate(m) for m in matches]
    if scorer is not None:
        cands = [CandidateMeaning(c.meaning, c.construction_id, c.warrant, c.readings, float(scorer(c))) for c in cands]
    # dedupe isomorphic meanings from different derivations: alternative support (⊕), one candidate
    merged: dict[str, CandidateMeaning] = {}
    for c in cands:
        d = canonical(c.meaning)[1]
        if d in merged:
            g = merged[d]
            merged[d] = CandidateMeaning(g.meaning, g.construction_id + "|" + c.construction_id, g.warrant.join(c.warrant), g.readings, g.score if c.score is None else max(g.score or 0.0, c.score))
        else:
            merged[d] = c
    cands = list(merged.values())
    if nogoods is not None:
        filtered = [CandidateMeaning(c.meaning, c.construction_id, nogoods.filter_interval(c.warrant), c.readings, c.score) for c in cands]
        changed = any(f.warrant != c.warrant for f, c in zip(filtered, cands, strict=True))
        cands = filtered
        if cands and changed and all(c.liveness(rv) is Liveness.DEAD for c in cands):
            return Interpretation(utterance, Verdict.CONTRADICTION, tuple(cands), analyses, "every reading violates a registered nogood")
    verdict, chosen = select(cands, rv)
    if verdict is Verdict.INTERPRETED:
        m = chosen[0].meaning
        unresolved = [n.node_id for n in m.nodes if n.underspecified and n.node_type == "entity" and (context_bindings is None or n.node_id not in context_bindings)]
        if unresolved:
            return Interpretation(utterance, Verdict.NEEDS_CONTEXT, chosen, analyses, f"unbound referents: {unresolved}")
        said = SaidRecord(utterance, speaker, canonical(m)[1], Authority.of(speaker=1), Scope.of(conversation))
        return Interpretation(utterance, verdict, chosen, analyses, "exactly one live candidate", said)
    if verdict is Verdict.AMBIGUOUS:
        ordered = tuple(sorted(chosen, key=lambda c: -(c.score or 0.0)))  # ranking for the clarification question only
        return Interpretation(utterance, verdict, ordered, analyses, f"{len(ordered)} candidates retained")
    return Interpretation(utterance, verdict, chosen, analyses, "no live candidate")


def mutant_force_top1(interp: Interpretation) -> CandidateMeaning | None:
    """Planted (M3 §12 'ambiguous forced to one meaning'): collapse AMBIGUOUS by score."""
    if interp.verdict is Verdict.AMBIGUOUS and interp.candidates:
        return interp.candidates[0]
    return None


def mutant_promote_said_to_world_truth(said: SaidRecord) -> Authority:
    """Planted (M3 §7 hostile): parsing success promoted to machine world-truth authority."""
    return Authority.of(world_truth=1, speaker=1)


def promote_authority(said: SaidRecord, bridge: Authority) -> Authority:
    """The only legal promotion: an admit transaction under the authority meet with a warranting
    bridge — never above the bridge, never above the speaker record (MEG-05)."""
    return said.authority.meet(bridge)
