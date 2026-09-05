"""Packed construction parser for N1 open-text experiments.

The historical M3 matcher materialises every recursive phrase attachment.  That
is exact on the bounded microworld but its N1 EWT experiment exhausted memory.
This research-lane parser keeps the *same* Lexeme/Reading/Construction semantics
while packing subderivations that have the same span, phrase type, construction,
head-reading identity and meaning (canonical within the existing size bound,
structurally identical above it).

The chart reports exact derivation multiplicity for the represented construction
inventory.  It does not silently equate derivation multiplicity with semantic
ambiguity: candidate meanings are still deduplicated by canonical meaning and
warrants are joined as alternate support, matching ``ocm.language.interpret``.

Restrictions are fail-closed:
- phrase-producing constructions must consume at least one non-optional lexical
  slot; pure unary/epsilon phrase cycles are CANNOT_CHECK in V1;
- no beam/top-k pruning is permitted;
- every packed multiplicity is an exact Python integer.

This module intentionally lives under ``research/`` until N1 earns a new runtime
receipt; it does not rewrite sealed historical M1-M12 source inventories.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Hashable, Iterable, Mapping, Sequence

from ocm.kso.nogoods import NogoodSet
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, meet_all_profiles
from ocm.language.constructions import CandidateMeaning, Construction, Match, Phrase, Slot, realise_candidate
from ocm.language.interpret import Interpretation, SaidRecord, Verdict, select, tokenize
from ocm.language.lexicon import Analysis, AnalysisStatus, Lexicon, Reading
from ocm.language.meaning import MAX_EXACT_CANONICAL, MeaningGraph, canonical


class ChartCannotCheck(ValueError):
    """The exact packed V1 contract does not cover this grammar shape."""


@dataclass(frozen=True)
class PackedPhrase:
    phrase: Phrase
    derivations: int

    def __post_init__(self) -> None:
        if type(self.derivations) is not int or self.derivations < 1:
            raise ValueError("packed phrase multiplicity must be a positive integer")


@dataclass(frozen=True)
class PackedMatch:
    match: Match
    derivations: int

    def __post_init__(self) -> None:
        if type(self.derivations) is not int or self.derivations < 1:
            raise ValueError("packed match multiplicity must be a positive integer")


@dataclass(frozen=True)
class ChartStats:
    tokens: int
    constructions_considered: int
    phrase_cells: int
    packed_phrases: int
    phrase_derivations: int
    clause_matches: int
    clause_derivations: int
    semantic_candidates: int


@dataclass(frozen=True)
class PackedInterpretation:
    interpretation: Interpretation
    stats: ChartStats


def _reading_signature(r: Reading) -> tuple[Any, ...]:
    sense_id = None if r.sense is None else r.sense.sense_id
    return (
        r.token,
        r.lemma,
        r.category.value,
        sense_id,
        tuple(r.features),
        tuple(r.via),
    )


def _meaning_signature(meaning: MeaningGraph) -> tuple[Any, ...]:
    # Intermediate phrases need not become clause candidates. Above the exact
    # canonical bound, use the immutable graph itself: this packs fewer graphs
    # but neither merges distinct structures nor rejects unused phrases. Final
    # candidates still pass through the historical bounded canonical checker.
    if len(meaning.nodes) > MAX_EXACT_CANONICAL:
        return ("structural", meaning)
    return ("canonical", canonical(meaning)[1])


def _value_signature(value: Any) -> tuple[Any, ...]:
    if isinstance(value, Reading):
        return ("R", *_reading_signature(value), value.warrant)
    if isinstance(value, Phrase):
        return (
            "P",
            value.phrase_type,
            value.span,
            value.construction_id,
            _reading_signature(value.head),
            _meaning_signature(value.meaning),
            value.warrant,
        )
    raise TypeError(f"unsupported chart binding: {type(value).__name__}")


def _bindings_signature(bindings: Sequence[tuple[str, Any]]) -> tuple[Any, ...]:
    return tuple((name, _value_signature(value)) for name, value in bindings)


def _phrase_key(phrase: Phrase) -> tuple[Any, ...]:
    return (
        phrase.span,
        phrase.phrase_type,
        phrase.construction_id,
        _reading_signature(phrase.head),
        _meaning_signature(phrase.meaning),
    )


def _requires_lexical_progress(construction: Construction) -> None:
    if construction.produces is None:
        return
    # Exact V1 deliberately rejects pure phrase->phrase or epsilon producers:
    # their same-span cycles can make derivation multiplicity infinite.
    if not any(slot.phrase is None and not slot.optional for slot in construction.pattern):
        raise ChartCannotCheck(
            f"phrase producer {construction.construction_id} has no mandatory lexical-progress slot"
        )


def _advance(
    construction: Construction,
    tokens: Sequence[Sequence[Reading]],
    start: int,
    phrase_index: Mapping[tuple[int, str], Sequence[PackedPhrase]],
) -> list[tuple[tuple[tuple[str, Any], ...], int, int]]:
    """Exact packed matches of one construction from ``start``.

    States with identical binding identities are merged and their multiplicities
    summed.  A packed child phrase contributes its own exact derivation count.
    """
    # key = (token position, identity-bearing binding signature)
    states: dict[tuple[int, tuple[Any, ...]], tuple[tuple[tuple[str, Any], ...], int]] = {
        (start, ()): ((), 1)
    }
    n = len(tokens)
    for slot in construction.pattern:
        nxt: dict[tuple[int, tuple[Any, ...]], tuple[tuple[tuple[str, Any], ...], int]] = {}

        def add(pos: int, bindings: tuple[tuple[str, Any], ...], multiplicity: int) -> None:
            sig = _bindings_signature(bindings)
            key = (pos, sig)
            if key in nxt:
                old_bindings, old_count = nxt[key]
                nxt[key] = (old_bindings, old_count + multiplicity)
            else:
                nxt[key] = (bindings, multiplicity)

        for (pos, _), (bindings, multiplicity) in states.items():
            if slot.optional:
                add(pos, bindings, multiplicity)
            if slot.phrase is not None:
                for packed in phrase_index.get((pos, slot.phrase), ()):
                    ph = packed.phrase
                    # A child must consume input; same-span epsilon cycles are not
                    # representable in the exact finite V1 chart.
                    if ph.span[0] != pos or ph.span[1] <= pos:
                        raise ChartCannotCheck("non-progressing packed phrase")
                    add(
                        ph.span[1],
                        bindings + ((slot.name, ph),),
                        multiplicity * packed.derivations,
                    )
                continue
            if pos >= n:
                continue
            for reading in tokens[pos]:
                if slot.matches(reading):
                    add(pos + 1, bindings + ((slot.name, reading),), multiplicity)
        states = nxt
        if not states:
            break
    return [(bindings, pos, count) for (pos, _), (bindings, count) in states.items()]


def packed_phrase_table(
    constructions: Iterable[Construction],
    tokens: Sequence[Sequence[Reading]],
    *,
    revoked: Iterable[Hashable] = (),
) -> tuple[dict[tuple[int, int], tuple[PackedPhrase, ...]], dict[tuple[int, str], tuple[PackedPhrase, ...]]]:
    rv = frozenset(revoked)
    producers = [
        c for c in constructions
        if c.produces is not None and c.liveness(rv) is not Liveness.DEAD
    ]
    for c in producers:
        _requires_lexical_progress(c)

    table: dict[tuple[int, int], dict[tuple[Any, ...], PackedPhrase]] = {}
    by_start_type: dict[tuple[int, str], list[PackedPhrase]] = {}
    n = len(tokens)

    # A phrase of length L may only depend on already-completed shorter phrases
    # plus lexical tokens. Mandatory lexical progress makes that sufficient for
    # the supported recursive grammar class.
    for length in range(1, n + 1):
        staged: list[PackedPhrase] = []
        frozen_index = {k: tuple(v) for k, v in by_start_type.items()}
        for start in range(0, n - length + 1):
            end_target = start + length
            cell: dict[tuple[Any, ...], PackedPhrase] = {}
            for c in producers:
                for bindings, end, multiplicity in _advance(c, tokens, start, frozen_index):
                    if end != end_target:
                        continue
                    b = dict(bindings)
                    try:
                        meaning = c.template(b)
                    except Exception as exc:  # noqa: BLE001
                        raise ChartCannotCheck(
                            f"construction template failed for {c.construction_id}: {exc}"
                        ) from exc
                    if c.head_slot:
                        head_value = b[c.head_slot]
                    else:
                        head_value = next(
                            (v for v in b.values() if isinstance(v, (Reading, Phrase))),
                            None,
                        )
                    if head_value is None:
                        raise ChartCannotCheck(f"phrase producer {c.construction_id} has no head")
                    head = head_value.head if isinstance(head_value, Phrase) else head_value
                    warrants = [c.warrant] + [v.warrant for v in b.values()]
                    phrase = Phrase(
                        c.produces,
                        head,
                        meaning,
                        c.head_node,
                        meet_all_profiles(warrants),
                        (start, end),
                        c.construction_id,
                    )
                    key = _phrase_key(phrase)
                    if key in cell:
                        old = cell[key]
                        cell[key] = PackedPhrase(
                            replace(old.phrase, warrant=old.phrase.warrant.join(phrase.warrant)),
                            old.derivations + multiplicity,
                        )
                    else:
                        cell[key] = PackedPhrase(phrase, multiplicity)
            if cell:
                table[(start, end_target)] = cell
                staged.extend(cell.values())
        # Publish the complete length only after every span at this length has
        # been built, preventing order-dependent same-length unary closure.
        for packed in staged:
            by_start_type.setdefault(
                (packed.phrase.span[0], packed.phrase.phrase_type), []
            ).append(packed)

    frozen_table = {cell: tuple(values.values()) for cell, values in table.items()}
    frozen_index = {key: tuple(values) for key, values in by_start_type.items()}
    return frozen_table, frozen_index


def packed_matches(
    constructions: Iterable[Construction],
    tokens: Sequence[Sequence[Reading]],
    *,
    revoked: Iterable[Hashable] = (),
    whole: bool = True,
) -> tuple[tuple[PackedMatch, ...], ChartStats]:
    rv = frozenset(revoked)
    cons = list(constructions)
    table, phrase_index = packed_phrase_table(cons, tokens, revoked=rv)
    matches: dict[tuple[Any, ...], PackedMatch] = {}
    for c in cons:
        if c.produces is not None or c.liveness(rv) is Liveness.DEAD:
            continue
        for bindings, end, multiplicity in _advance(c, tokens, 0, phrase_index):
            if whole and end != len(tokens):
                continue
            match = Match(c, bindings, (0, end))
            key = (
                c.construction_id,
                c.warrant,
                match.span,
                _bindings_signature(bindings),
            )
            if key in matches:
                old = matches[key]
                matches[key] = PackedMatch(old.match, old.derivations + multiplicity)
            else:
                matches[key] = PackedMatch(match, multiplicity)
    values = tuple(matches.values())
    packed_phrases = sum(len(v) for v in table.values())
    phrase_derivations = sum(p.derivations for v in table.values() for p in v)
    stats = ChartStats(
        tokens=len(tokens),
        constructions_considered=len(cons),
        phrase_cells=len(table),
        packed_phrases=packed_phrases,
        phrase_derivations=phrase_derivations,
        clause_matches=len(values),
        clause_derivations=sum(m.derivations for m in values),
        semantic_candidates=0,
    )
    return values, stats


def interpret_packed(
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
) -> PackedInterpretation:
    rv = frozenset(revoked)
    words = tokenize(utterance)
    analyses = tuple(lexicon.analyse(t, rv) for t in words)
    empty_stats = ChartStats(len(words), 0, 0, 0, 0, 0, 0, 0)
    if any(a.status is AnalysisStatus.UNKNOWN_LEXEME for a in analyses):
        bad = [a.token for a in analyses if a.status is AnalysisStatus.UNKNOWN_LEXEME]
        return PackedInterpretation(
            Interpretation(utterance, Verdict.UNKNOWN_LEXEME, (), analyses, f"unknown: {bad}"),
            empty_stats,
        )
    if any(a.status is AnalysisStatus.NO_LIVE_READING for a in analyses):
        bad = [a.token for a in analyses if a.status is AnalysisStatus.NO_LIVE_READING]
        return PackedInterpretation(
            Interpretation(utterance, Verdict.UNKNOWN_LEXEME, (), analyses, f"no live reading: {bad}"),
            empty_stats,
        )
    per_token = [list(a.readings) for a in analyses]
    packed, stats = packed_matches(constructions, per_token, revoked=rv)
    if not packed:
        return PackedInterpretation(
            Interpretation(
                utterance,
                Verdict.UNKNOWN_CONSTRUCTION,
                (),
                analyses,
                "no construction consumes the utterance",
            ),
            stats,
        )

    # Semantic dedupe mirrors the historical interpreter.  Derivation counts are
    # kept in stats, not used to collapse or rank epistemic alternatives.
    merged: dict[str, CandidateMeaning] = {}
    for packed_match in packed:
        c = realise_candidate(packed_match.match)
        if scorer is not None:
            c = CandidateMeaning(
                c.meaning,
                c.construction_id,
                c.warrant,
                c.readings,
                float(scorer(c)),
            )
        digest = canonical(c.meaning)[1]
        if digest in merged:
            old = merged[digest]
            merged[digest] = CandidateMeaning(
                old.meaning,
                old.construction_id + "|" + c.construction_id,
                old.warrant.join(c.warrant),
                old.readings,
                old.score if c.score is None else max(old.score or 0.0, c.score),
            )
        else:
            merged[digest] = c
    candidates = list(merged.values())

    if nogoods is not None:
        filtered = [
            CandidateMeaning(
                c.meaning,
                c.construction_id,
                nogoods.filter_interval(c.warrant),
                c.readings,
                c.score,
            )
            for c in candidates
        ]
        changed = any(f.warrant != c.warrant for f, c in zip(filtered, candidates, strict=True))
        candidates = filtered
        if candidates and changed and all(c.liveness(rv) is Liveness.DEAD for c in candidates):
            interp = Interpretation(
                utterance,
                Verdict.CONTRADICTION,
                tuple(candidates),
                analyses,
                "every reading violates a registered nogood",
            )
            return PackedInterpretation(
                interp,
                ChartStats(**{**stats.__dict__, "semantic_candidates": len(candidates)}),
            )

    verdict, chosen = select(candidates, rv)
    semantic_stats = ChartStats(**{**stats.__dict__, "semantic_candidates": len(candidates)})
    if verdict is Verdict.INTERPRETED:
        meaning = chosen[0].meaning
        unresolved = [
            n.node_id
            for n in meaning.nodes
            if n.underspecified
            and n.node_type == "entity"
            and (context_bindings is None or n.node_id not in context_bindings)
        ]
        if unresolved:
            return PackedInterpretation(
                Interpretation(
                    utterance,
                    Verdict.NEEDS_CONTEXT,
                    chosen,
                    analyses,
                    f"unbound referents: {unresolved}",
                ),
                semantic_stats,
            )
        said = SaidRecord(
            utterance,
            speaker,
            canonical(meaning)[1],
            Authority.of(speaker=1),
            Scope.of(conversation),
        )
        return PackedInterpretation(
            Interpretation(
                utterance,
                verdict,
                chosen,
                analyses,
                "exactly one live candidate",
                said,
            ),
            semantic_stats,
        )
    if verdict is Verdict.AMBIGUOUS:
        ordered = tuple(sorted(chosen, key=lambda c: -(c.score or 0.0)))
        return PackedInterpretation(
            Interpretation(
                utterance,
                verdict,
                ordered,
                analyses,
                f"{len(ordered)} candidates retained",
            ),
            semantic_stats,
        )
    return PackedInterpretation(
        Interpretation(utterance, verdict, chosen, analyses, "no live candidate"),
        semantic_stats,
    )
