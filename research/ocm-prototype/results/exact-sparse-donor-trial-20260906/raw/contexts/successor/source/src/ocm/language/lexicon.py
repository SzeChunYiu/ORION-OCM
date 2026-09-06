"""Lexicon and morphology as warranted objects (M3 §3–§4).

* ``Lexeme`` — surface/lemma, category, and **senses as an ambiguity set** of candidate atoms
  (MEG-26): polysemy is a set of candidates each with its own warrant interval, never a
  ⊕-merged sense; collapse is an evidence event (context, clarification), never a score.
* ``MorphRule`` — a productive transformation with a warrant and a registered scope; exceptions
  are more-specific warranted overrides (the inherited L0 rule: the more specific live rule
  wins), so an irregular form never silently regularises and revoking the exception's evidence
  reopens exactly the forms that depended on it.
* ``Lexicon.analyse(token)`` returns the candidate (lexeme, sense, features) readings with their
  warrants: ``UNKNOWN_LEXEME`` when nothing matches — no hallucination from spelling similarity
  (the planted mutant ``mutant_nearest_spelling``).
Nothing here is constitution: categories, features and rule kinds are registry data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile, kleene_and


class Category(str, Enum):
    NOUN = "N"
    VERB = "V"
    ADJ = "A"
    DET = "D"
    PRON = "PRO"
    PREP = "P"
    AUX = "AUX"
    CONJ = "CONJ"
    ADV = "ADV"
    WH = "WH"
    NEG = "NEG"
    PUNCT = "PUNCT"


@dataclass(frozen=True)
class Sense:
    sense_id: str
    concept: str                         # the meaning-graph label this sense denotes
    node_type: str                       # meaning node type: entity | event | state | property | ...
    warrant: WarrantProfile
    selection: tuple[tuple[str, str], ...] = ()   # argument/selection constraints, e.g. (("ROLE:patient","entity"),)
    scope: Scope = field(default_factory=Scope.universal)

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


@dataclass(frozen=True)
class Lexeme:
    lemma: str
    category: Category
    senses: tuple[Sense, ...]
    features: tuple[tuple[str, str], ...] = ()
    warrant: WarrantProfile = field(default_factory=WarrantProfile.one)   # the form↔category pairing's own evidence
    scope: Scope = field(default_factory=Scope.universal)

    def live_senses(self, revoked: Iterable[Hashable]) -> tuple[Sense, ...]:
        return tuple(s for s in self.senses if s.liveness(revoked) is Liveness.LIVE)


class RuleKind(str, Enum):
    PRODUCTIVE = "PRODUCTIVE"
    EXCEPTION = "EXCEPTION"


@dataclass(frozen=True)
class MorphRule:
    rule_id: str
    kind: RuleKind
    category: Category
    features: tuple[tuple[str, str], ...]         # features the form carries, e.g. (("tense","past"),)
    apply: Callable[[str], str]                    # lemma → surface (generation direction)
    analyse: Callable[[str], str | None]           # surface → lemma or None (interpretation direction)
    warrant: WarrantProfile
    scope: Scope = field(default_factory=Scope.universal)
    lemmas: frozenset[str] = frozenset()           # EXCEPTION rules are scoped to specific lemmas

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


@dataclass(frozen=True)
class Reading:
    """One candidate analysis of a token: lexeme + sense + features, with its ⊗ warrant."""

    token: str
    lemma: str
    category: Category
    sense: Sense | None
    features: tuple[tuple[str, str], ...]
    warrant: WarrantProfile
    via: tuple[str, ...]                           # rule ids used

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


class AnalysisStatus(str, Enum):
    READINGS = "READINGS"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN_LEXEME = "UNKNOWN_LEXEME"
    NO_LIVE_READING = "NO_LIVE_READING"


@dataclass(frozen=True)
class Analysis:
    token: str
    status: AnalysisStatus
    readings: tuple[Reading, ...]


@dataclass
class Lexicon:
    lexemes: dict[str, Lexeme] = field(default_factory=dict)      # key: lemma|category
    rules: list[MorphRule] = field(default_factory=list)

    def add(self, lex: Lexeme) -> str:
        key = f"{lex.lemma}|{lex.category.value}"
        self.lexemes[key] = lex
        return key

    def add_rule(self, rule: MorphRule) -> None:
        self.rules.append(rule)

    def by_lemma(self, lemma: str) -> list[Lexeme]:
        return [l for k, l in self.lexemes.items() if k.split("|")[0] == lemma]

    # --- analysis ------------------------------------------------------------------------
    def _rule_readings(self, token: str, revoked: frozenset) -> list[tuple[MorphRule, str]]:
        """Rules whose analysis matches; EXCEPTION rules (more specific) pre-empt PRODUCTIVE ones
        for the same lemma when live (the inherited override law)."""
        hits: list[tuple[MorphRule, str]] = []
        for r in self.rules:
            lemma = r.analyse(token)
            if lemma is None:
                continue
            if r.kind is RuleKind.EXCEPTION and lemma not in r.lemmas:
                continue
            hits.append((r, lemma))
        # a LIVE exception for a lemma pre-empts every productive rule with the same category and
        # features for that lemma — whatever token is being analysed (so "goed" is blocked while
        # "went" is warranted, and becomes available exactly when the exception's evidence is revoked)
        live_exc = {(l, r.category, tuple(sorted(r.features))) for r in self.rules if r.kind is RuleKind.EXCEPTION and r.liveness(revoked) is Liveness.LIVE for l in r.lemmas}
        return [(r, lemma) for r, lemma in hits if not (r.kind is RuleKind.PRODUCTIVE and (lemma, r.category, tuple(sorted(r.features))) in live_exc)]

    def analyse(self, token: str, revoked: Iterable[Hashable] = ()) -> Analysis:
        rv = frozenset(revoked)
        readings: list[Reading] = []
        # identity (the token is itself a lemma)
        for lex in self.by_lemma(token):
            for sense in lex.senses or (None,):
                w = lex.warrant if sense is None else lex.warrant.meet(sense.warrant)
                readings.append(Reading(token, lex.lemma, lex.category, sense, lex.features, w, ()))
        # via morphology
        for rule, lemma in self._rule_readings(token, rv):
            for lex in self.by_lemma(lemma):
                if lex.category is not rule.category:
                    continue
                for sense in lex.senses or (None,):
                    w = lex.warrant.meet(rule.warrant)
                    if sense is not None:
                        w = w.meet(sense.warrant)
                    readings.append(Reading(token, lemma, lex.category, sense, lex.features + rule.features, w, (rule.rule_id,)))
        if not readings:
            return Analysis(token, AnalysisStatus.UNKNOWN_LEXEME, ())
        # two derivations of the *same* analysis are alternative support for one reading (⊕),
        # not two readings: group by (lemma, category, sense, features)
        grouped: dict[tuple, Reading] = {}
        for r in readings:
            key = (r.lemma, r.category, None if r.sense is None else r.sense.sense_id, tuple(sorted(r.features)))
            if key in grouped:
                g = grouped[key]
                grouped[key] = Reading(r.token, r.lemma, r.category, r.sense, g.features, g.warrant.join(r.warrant), tuple(sorted(set(g.via) | set(r.via))))
            else:
                grouped[key] = r
        readings = list(grouped.values())
        live = [r for r in readings if r.liveness(rv) is Liveness.LIVE]
        unknown = [r for r in readings if r.liveness(rv) is Liveness.UNKNOWN]
        if not live and not unknown:
            return Analysis(token, AnalysisStatus.NO_LIVE_READING, tuple(readings))
        status = AnalysisStatus.READINGS if len(live) == 1 and not unknown else AnalysisStatus.AMBIGUOUS
        return Analysis(token, status, tuple(live + unknown))


def mutant_nearest_spelling(lexicon: Lexicon, token: str) -> Reading | None:
    """Planted: an unknown token is 'recognised' as the lexeme with the smallest edit distance
    (hallucination from spelling similarity)."""
    def dist(a: str, b: str) -> int:
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1]

    best = None
    for key, lex in lexicon.lexemes.items():
        d = dist(token, lex.lemma)
        if best is None or d < best[0]:
            best = (d, lex)
    if best is None:
        return None
    lex = best[1]
    return Reading(token, lex.lemma, lex.category, lex.senses[0] if lex.senses else None, lex.features, lex.warrant, ("SPELLING",))


def mutant_merge_senses(lex: Lexeme) -> Sense:
    """Planted: senses ⊕-merged into one — LIVE while any sense is live (false collapse)."""
    w = WarrantProfile.zero()
    for s in lex.senses:
        w = w.join(s.warrant)
    return Sense(f"{lex.lemma}:merged", "|".join(s.concept for s in lex.senses), lex.senses[0].node_type, w)
