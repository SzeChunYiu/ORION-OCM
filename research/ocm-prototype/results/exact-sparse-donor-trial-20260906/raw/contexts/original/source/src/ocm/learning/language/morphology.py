"""Morphology and exception lifecycle (M5 §5): productive pattern induction from (lemma, form)
pairs, compared across registered strategies, with exceptions that accumulate and a recorded
split point.

Strategies (each a registered finite hypothesis class run through the version-space learner):
  RULE      suffix-rewrite rules  s₁→s₂  (strip s₁, append s₂) over a bounded suffix length
  ANALOGY   nearest paradigm: the form of the closest known lemma's transformation (no rule object)
  HYBRID    RULE for the regular part + EXCEPTION entries for pairs the rule cannot produce
The learned object is a `MorphRule` set for the M3 lexicon: one PRODUCTIVE rule with the ⊗ of the
pairs that pinned it plus one EXCEPTION rule per irregular pair with that pair's evidence.  The
override law (KS-T36) makes exceptions win while live and reopens exactly the blocked forms on
revocation.  When exceptions exceed a registered fraction of the paradigm the learner records
`SPLIT_RECOMMENDED` (a more specific rule should be induced) instead of silently growing the list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence

from ocm.kso.warrant import WarrantProfile, meet_all_profiles

from ocm.language.lexicon import Category, Lexicon, MorphRule, RuleKind


class Strategy(str, Enum):
    RULE = "RULE"
    ANALOGY = "ANALOGY"
    HYBRID = "HYBRID"


@dataclass(frozen=True)
class Pair:
    lemma: str
    form: str
    evidence_id: str


@dataclass(frozen=True)
class SuffixRule:
    strip: str
    append: str

    def apply(self, lemma: str) -> str | None:
        if self.strip and not lemma.endswith(self.strip):
            return None
        return lemma[: len(lemma) - len(self.strip)] + self.append if self.strip else lemma + self.append

    def analyse(self, form: str) -> str | None:
        if not form.endswith(self.append):
            return None
        base = form[: len(form) - len(self.append)] if self.append else form
        return base + self.strip

    @property
    def name(self) -> str:
        return f"-{self.strip or '∅'}+{self.append or '∅'}"


def candidate_rules(pairs: Sequence[Pair], max_suffix: int = 3) -> list[SuffixRule]:
    """The finite class: every (strip, append) suggested by some pair, bounded suffix length."""
    out: dict[tuple[str, str], SuffixRule] = {}
    for p in pairs:
        i = 0
        while i < min(len(p.lemma), len(p.form)) and p.lemma[i] == p.form[i]:
            i += 1
        for k in range(0, max_suffix + 1):
            cut = max(i - k, 0)
            strip, app = p.lemma[cut:], p.form[cut:]
            if len(strip) <= max_suffix and len(app) <= max_suffix + 2:
                out[(strip, app)] = SuffixRule(strip, app)
    return list(out.values())


@dataclass(frozen=True)
class Induction:
    strategy: Strategy
    rule: SuffixRule | None
    covered: tuple[Pair, ...]
    exceptions: tuple[Pair, ...]
    warrant: WarrantProfile
    split_recommended: bool
    detail: str


def induce(pairs: Sequence[Pair], strategy: Strategy, *, exception_fraction: float = 0.5, max_suffix: int = 3) -> Induction:
    if strategy is Strategy.ANALOGY:
        return Induction(strategy, None, tuple(pairs), (), meet_all_profiles([WarrantProfile.of({p.evidence_id}) for p in pairs]), False, "no rule object; forms are produced by nearest paradigm")
    rules = candidate_rules(pairs, max_suffix)
    best, best_cov = None, -1
    for r in rules:
        cov = sum(1 for p in pairs if r.apply(p.lemma) == p.form)
        if cov > best_cov or (cov == best_cov and best is not None and (len(r.strip) + len(r.append)) < (len(best.strip) + len(best.append))):
            best, best_cov = r, cov
    covered = tuple(p for p in pairs if best is not None and best.apply(p.lemma) == p.form)
    exceptions = tuple(p for p in pairs if p not in covered)
    if strategy is Strategy.RULE and exceptions:
        return Induction(strategy, best, covered, (), meet_all_profiles([WarrantProfile.of({p.evidence_id}) for p in covered]), False, f"rule {best.name} contradicted by {len(exceptions)} pair(s): CONTRADICTION (pure rule cannot represent them)")
    warrant = meet_all_profiles([WarrantProfile.of({p.evidence_id}) for p in covered]) if covered else WarrantProfile.zero()
    split = len(pairs) > 0 and len(exceptions) / len(pairs) > exception_fraction
    return Induction(strategy, best, covered, exceptions, warrant, split, f"rule {best.name if best else '—'} covers {len(covered)}/{len(pairs)}; {len(exceptions)} exception(s)" + ("; SPLIT_RECOMMENDED" if split else ""))


def analogy_form(pairs: Sequence[Pair], lemma: str) -> str | None:
    """Nearest paradigm by longest common suffix; applies that pair's transformation."""
    best, score = None, -1
    for p in pairs:
        k = 0
        while k < min(len(p.lemma), len(lemma)) and p.lemma[-1 - k] == lemma[-1 - k]:
            k += 1
        if k > score:
            best, score = p, k
    if best is None:
        return None
    i = 0
    while i < min(len(best.lemma), len(best.form)) and best.lemma[i] == best.form[i]:
        i += 1
    strip, app = best.lemma[i:], best.form[i:]
    return lemma[: len(lemma) - len(strip)] + app if lemma.endswith(strip) else None


def install(lexicon: Lexicon, ind: Induction, category: Category, features: tuple[tuple[str, str], ...], rule_prefix: str) -> list[str]:
    """Turn a HYBRID/RULE induction into M3 MorphRules (productive + exceptions)."""
    ids = []
    if ind.rule is not None and ind.covered:
        rid = f"{rule_prefix}:{ind.rule.name}"
        r = ind.rule
        lexicon.add_rule(MorphRule(rid, RuleKind.PRODUCTIVE, category, features, r.apply, r.analyse, ind.warrant))
        ids.append(rid)
    for p in ind.exceptions:
        rid = f"{rule_prefix}:exc:{p.lemma}"
        lexicon.add_rule(MorphRule(rid, RuleKind.EXCEPTION, category, features, (lambda l, f=p.form: f), (lambda s, f=p.form, l=p.lemma: l if s == f else None), WarrantProfile.of({p.evidence_id}), lemmas=frozenset({p.lemma})))
        ids.append(rid)
    return ids


def mutant_rule_overrides_exception(lexicon: Lexicon, rule_prefix: str) -> None:
    """Planted (M5 §17 'exception stored but general rule still overrides it'): re-tag exceptions as
    productive so the general rule and the exception compete instead of the exception winning."""
    lexicon.rules = [MorphRule(r.rule_id, RuleKind.PRODUCTIVE, r.category, r.features, r.apply, r.analyse, r.warrant, r.scope, frozenset()) if r.rule_id.startswith(f"{rule_prefix}:exc:") else r for r in lexicon.rules]
