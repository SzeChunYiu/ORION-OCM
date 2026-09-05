"""Active language learning (M5 §11): information-seeking actions chosen by value of information
over the version space, resource-aware; never asks for a gold label the task rules prohibit.

Actions (registered): ASK_MEANING (unknown word), REQUEST_PARAPHRASE, ASK_REFERENT, ASK_EXAMPLE,
PROPOSE_AND_CONFIRM, TEST_IN_SANDBOX (a grounded probe whose outcome is a registered outcome
function).  Each action has a cost and an *expected elimination*: the expected number of
hypotheses removed from the current version space on the registered query family (uniform prior
over surviving hypotheses).  Value = expected elimination / cost; the learner acts iff the best
value exceeds a registered threshold; the M4 clarification policy is the special case where the
hypotheses are the readings of one utterance.  Oracle regret is measured against the action that
maximises realised elimination in hindsight.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Hashable, Mapping, Sequence


class ActionKind(str, Enum):
    ASK_MEANING = "ASK_MEANING"
    REQUEST_PARAPHRASE = "REQUEST_PARAPHRASE"
    ASK_REFERENT = "ASK_REFERENT"
    ASK_EXAMPLE = "ASK_EXAMPLE"
    PROPOSE_AND_CONFIRM = "PROPOSE_AND_CONFIRM"
    TEST_IN_SANDBOX = "TEST_IN_SANDBOX"
    ASK_GOLD_LABEL = "ASK_GOLD_LABEL"       # prohibited under task rules; present so the refusal is testable


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    target: str                                        # utterance / word / referent the action is about
    cost: float
    # answer(h) → what the oracle would reply if h were true (the action partitions the version space)
    answer: Callable[[Hashable], Hashable]


@dataclass(frozen=True)
class Choice:
    action: Action | None
    value: float
    expected_elimination: float
    values: dict[str, float]
    reason: str


def expected_elimination(version_space: Mapping[str, Hashable], action: Action) -> float:
    """E over the true hypothesis (uniform) of the number of hypotheses eliminated by the answer."""
    hs = list(version_space.items())
    n = len(hs)
    if n <= 1:
        return 0.0
    blocks: dict[Hashable, int] = {}
    for _, h in hs:
        a = action.answer(h)
        blocks[a] = blocks.get(a, 0) + 1
    return sum((size / n) * (n - size) for size in blocks.values())


def choose(version_space: Mapping[str, Hashable], actions: Sequence[Action], *, threshold: float = 0.0, prohibited: Sequence[ActionKind] = (ActionKind.ASK_GOLD_LABEL,)) -> Choice:
    if len(version_space) <= 1:
        return Choice(None, 0.0, 0.0, {}, "version space already singleton")
    values: dict[str, float] = {}
    best: tuple[float, float, Action] | None = None
    for a in actions:
        if a.kind in prohibited:
            values[f"{a.kind.value}:{a.target}"] = float("-inf")
            continue
        e = expected_elimination(version_space, a)
        v = e / a.cost if a.cost > 0 else float("inf")
        values[f"{a.kind.value}:{a.target}"] = v
        if best is None or v > best[0]:
            best = (v, e, a)
    if best is None:
        return Choice(None, 0.0, 0.0, values, "no admissible action")
    if best[0] <= threshold:
        return Choice(None, best[0], best[1], values, "no action worth its cost")
    return Choice(best[2], best[0], best[1], values, "expected elimination per unit cost")


def realised_elimination(version_space: Mapping[str, Hashable], action: Action, true_h: Hashable) -> int:
    a = action.answer(true_h)
    return sum(1 for h in version_space.values() if action.answer(h) != a)


def oracle_regret(version_space: Mapping[str, Hashable], actions: Sequence[Action], chosen: Action | None, true_h: Hashable) -> float:
    """Hindsight regret: best realised elimination per cost minus the chosen one's."""
    adm = [a for a in actions if a.kind is not ActionKind.ASK_GOLD_LABEL]
    best = max((realised_elimination(version_space, a, true_h) / a.cost for a in adm), default=0.0)
    got = realised_elimination(version_space, chosen, true_h) / chosen.cost if chosen is not None else 0.0
    return best - got


def mutant_ask_gold_label(version_space: Mapping[str, Hashable], actions: Sequence[Action]) -> Choice:
    """Planted (M5 §17): the active learner asks the gold label directly."""
    gold = [a for a in actions if a.kind is ActionKind.ASK_GOLD_LABEL]
    return Choice(gold[0], float("inf"), float(len(version_space) - 1), {}, "mutant: gold label requested") if gold else Choice(None, 0.0, 0.0, {}, "no gold action")
