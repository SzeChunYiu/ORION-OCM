"""Clarification as an information action (M4 §4; theory batch 3 C1 / MEG-33).

Reference policy (replaceable, not a law): for an ambiguity set A = {a₁…a_k} and the pending
task's registered query family Q (the answers the task needs), the value of asking is the number
of query cells whose answer *differs* across the candidates, i.e. cells that move from UNKNOWN to
LIVE/DEAD once the ambiguity is collapsed — minus the interaction cost and a repeat penalty.

    value(question) = |{q ∈ Q : answer_q(a_i) ≠ answer_q(a_j) for some i, j in the question's split}|
                      − cost(question) − repeat_penalty(question)
    ask  iff  max over questions value > 0

Consequences (tested): ambiguity irrelevant to the answer ⇒ value 0 ⇒ no question; ambiguity that
changes the answer ⇒ ask; a question splitting more hypotheses on Q is preferred under matched
costs; a repeated pointless question has non-positive value.  The policy never collapses the
ambiguity set itself: the answer to the question is INTERACTION evidence (M3 session).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

Answer = Callable[[Hashable], Hashable]        # candidate → answer of one query cell


@dataclass(frozen=True)
class Question:
    question_id: str
    text: str
    split: tuple[frozenset, ...]               # partition of the candidate set the answer would induce
    cost: float = 1.0


@dataclass(frozen=True)
class Decision:
    ask: bool
    question: Question | None
    value: float
    values: dict[str, float]
    reason: str


def cells_separated(candidates: Sequence[Hashable], queries: Mapping[str, Answer], split: Sequence[frozenset]) -> int:
    """Query cells whose answer is not constant on some block-pair the question separates —
    counted as cells that would leave UNKNOWN if the question were answered."""
    moved = 0
    for name, ans in queries.items():
        by_block = [frozenset(ans(c) for c in block if c in candidates) for block in split]
        overall = {ans(c) for c in candidates}
        if len(overall) <= 1:
            continue                                   # constant across candidates: irrelevant cell
        if any(len(b) == 1 for b in by_block if b):    # some block pins the answer
            moved += 1
    return moved


def decide(candidates: Sequence[Hashable], queries: Mapping[str, Answer], questions: Sequence[Question], *, asked_before: Iterable[str] = (), repeat_penalty: float = 1.0) -> Decision:
    if len(candidates) <= 1:
        return Decision(False, None, 0.0, {}, "no ambiguity")
    asked = set(asked_before)
    values: dict[str, float] = {}
    for q in questions:
        v = cells_separated(candidates, queries, q.split) - q.cost - (repeat_penalty if q.question_id in asked else 0.0)
        values[q.question_id] = v
    if not values:
        return Decision(False, None, 0.0, {}, "no question available")
    best_id = max(values, key=lambda k: (values[k], -questions[[q.question_id for q in questions].index(k)].cost))
    best = next(q for q in questions if q.question_id == best_id)
    if values[best_id] > 0:
        return Decision(True, best, values[best_id], values, "ambiguity changes a needed answer")
    if all(cells_separated(candidates, queries, q.split) == 0 for q in questions):
        return Decision(False, None, values[best_id], values, "ambiguity irrelevant to the pending queries")
    return Decision(False, None, values[best_id], values, "value does not cover cost")


def binary_questions(candidates: Sequence[Hashable], describe: Callable[[Hashable], str], cost: float = 1.0) -> list[Question]:
    """One 'did you mean X?' question per candidate (splits {X} vs rest) plus the full menu."""
    cs = list(candidates)
    qs = [Question(f"is:{c}", f"Did you mean {describe(c)}?", (frozenset({c}), frozenset(x for x in cs if x != c)), cost) for c in cs]
    qs.append(Question("menu", "Which did you mean: " + "; ".join(describe(c) for c in cs) + "?", tuple(frozenset({c}) for c in cs), cost))
    return qs


def mutant_always_ask(candidates: Sequence[Hashable]) -> Decision:
    """Planted (M4 §14 'irrelevant ambiguity triggers clarification loop')."""
    return Decision(len(candidates) > 1, None, float("inf"), {}, "mutant: asks whenever ambiguous")


def mutant_never_ask(candidates: Sequence[Hashable]) -> Decision:
    """Planted (M4 §14 'consequential ambiguity ignored')."""
    return Decision(False, None, 0.0, {}, "mutant: never asks")
