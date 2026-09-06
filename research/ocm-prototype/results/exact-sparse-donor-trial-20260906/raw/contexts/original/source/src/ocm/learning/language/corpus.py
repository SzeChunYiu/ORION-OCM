"""Raw-corpus form induction without semantic laundering (M5 §6, E2).

    raw text → ungrounded form/distribution hypotheses      status UNGROUNDED_FORM_ONLY
    aligned/grounded evidence → semantic binding            status CANDIDATE_SEMANTIC_BINDING → GROUNDED_CONSTRUCTION
    contradiction / revocation                              status CONTRADICTED / REVOKED

A `FormHypothesis` records what raw text supports: a recurring token, a suffix regularity, a
collocation, a distributional cluster.  Its warrant is the corpus evidence, but its *authority*
carries no `world_truth` and no `meaning` coordinate: the interpreter never consults an
UNGROUNDED hypothesis, so a frequent pattern that correlates with a protected false meaning cannot
become grounded by frequency (planted mutant `mutant_frequency_grounds`).  Binding requires an
aligned/grounded evidence id (E1/E3) through `bind`, which is the only route to GROUNDED.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.types import Authority
from ocm.kso.warrant import Liveness, WarrantProfile


class FormStatus(str, Enum):
    UNGROUNDED_FORM_ONLY = "UNGROUNDED_FORM_ONLY"
    CANDIDATE_SEMANTIC_BINDING = "CANDIDATE_SEMANTIC_BINDING"
    GROUNDED_CONSTRUCTION = "GROUNDED_CONSTRUCTION"
    CONTRADICTED = "CONTRADICTED"
    REVOKED = "REVOKED"


@dataclass
class FormHypothesis:
    form_id: str
    kind: str                                 # token | suffix | collocation | cluster
    content: dict[str, Any]
    corpus_evidence: tuple[str, ...]
    count: int
    status: FormStatus = FormStatus.UNGROUNDED_FORM_ONLY
    binding: dict[str, Any] | None = None     # concept + aligned evidence once bound
    authority: Authority = field(default_factory=lambda: Authority.of(corpus=1))

    def warrant(self) -> WarrantProfile:
        w = WarrantProfile.of(set(self.corpus_evidence))
        if self.binding:
            w = w.meet(WarrantProfile.of(set(self.binding["evidence"])))
        return w


TOKEN = re.compile(r"[a-z]+")


def tokenize_text(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def mine(text: str, evidence_id: str, *, min_count: int = 3, suffixes: Sequence[str] = ("ed", "ing", "s", "ly")) -> list[FormHypothesis]:
    """Ungrounded hypotheses from surface text only."""
    toks = tokenize_text(text)
    counts = Counter(toks)
    out: list[FormHypothesis] = []
    for w, c in counts.most_common():
        if c >= min_count:
            out.append(FormHypothesis(f"token:{w}", "token", {"token": w}, (evidence_id,), c))
    for suf in suffixes:
        stems = {w[: -len(suf)] for w in counts if w.endswith(suf) and len(w) > len(suf) + 2}
        # a suffix regularity needs the stem to recur in another shape (bare or with another suffix)
        paired = sorted(s for s in stems if s in counts or any(s + o in counts for o in suffixes if o != suf))
        if len(paired) >= min_count:
            out.append(FormHypothesis(f"suffix:{suf}", "suffix", {"suffix": suf, "stems_with_base_form": paired[:20]}, (evidence_id,), len(paired)))
    bigrams = Counter(zip(toks, toks[1:]))
    for (a, b), c in bigrams.most_common():
        if c >= min_count and counts[a] >= min_count and counts[b] >= min_count:
            out.append(FormHypothesis(f"colloc:{a}_{b}", "collocation", {"left": a, "right": b}, (evidence_id,), c))
    return out


def bind(h: FormHypothesis, concept: str, aligned_evidence: Iterable[str], *, channel: str) -> FormHypothesis:
    """The only route from UNGROUNDED to GROUNDED: aligned (E1) or grounded-interaction (E3) evidence."""
    if channel not in ("demonstration", "interaction", "instruction"):
        raise ValueError(f"binding needs aligned/grounded evidence, not {channel}")
    ev = tuple(aligned_evidence)
    if not ev:
        raise ValueError("no aligned evidence")
    h.binding = {"concept": concept, "evidence": ev, "channel": channel}
    h.status = FormStatus.GROUNDED_CONSTRUCTION
    h.authority = Authority.of(corpus=1, speaker=1)
    return h


def propose_binding(h: FormHypothesis, concept: str) -> FormHypothesis:
    """A candidate binding (e.g. from context) — still not consultable by the interpreter."""
    h.binding = {"concept": concept, "evidence": (), "channel": "candidate"}
    h.status = FormStatus.CANDIDATE_SEMANTIC_BINDING
    return h


def revoke(h: FormHypothesis, revoked: Iterable[str]) -> FormHypothesis:
    if h.warrant().liveness(revoked) is Liveness.DEAD:
        h.status = FormStatus.REVOKED
    return h


def contradict(h: FormHypothesis, counter_evidence: str) -> FormHypothesis:
    h.status = FormStatus.CONTRADICTED
    h.content = {**h.content, "contradicted_by": counter_evidence}
    return h


def consultable(h: FormHypothesis) -> bool:
    """What the interpreter may use: only GROUNDED hypotheses whose binding is live."""
    return h.status is FormStatus.GROUNDED_CONSTRUCTION and h.binding is not None and bool(h.binding["evidence"])


def mutant_frequency_grounds(h: FormHypothesis, concept: str, threshold: int = 10) -> FormHypothesis:
    """Planted (M5 §17 'corpus frequency promoted to world truth')."""
    if h.count >= threshold:
        h.binding = {"concept": concept, "evidence": h.corpus_evidence, "channel": "corpus"}
        h.status = FormStatus.GROUNDED_CONSTRUCTION
        h.authority = Authority.of(corpus=1, world_truth=1)
    return h
