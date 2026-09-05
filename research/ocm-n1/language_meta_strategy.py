"""Exact language-meta-learning calibration for N1/#52/#53.

This separates *reusing grammar content* from *learning how to acquire grammar*.
The target family uses completely new role symbols, so no pairwise order facts can
transfer.  What may transfer is a learned acquisition-policy identity.

Two finite registered strategies are available:
- FIXED: ask pairwise precedence questions in a fixed lexical order;
- BALANCED: at each step ask the question that most evenly splits the current
  version space.

The learner does not invent these algorithms in V1; it learns which strategy to
select from prior paired, isomorphic acquisition episodes.  The learned strategy
is an explicit evidence-scoped object.  Revoking its meta-evidence reopens the
choice and falls back to FIXED.  A strongest persistent strategy-memory parent is
given exactly the same strategy library and meta-evidence and must match.

This is DEVELOPMENT_CALIBRATION_ONLY, not a protected language result.
"""
from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Iterable, Sequence


Order = tuple[str, ...]
Pair = tuple[str, str]


@dataclass(frozen=True)
class StrategyRun:
    strategy: str
    interactions: int
    questions: tuple[Pair, ...]
    learned_order: Order


@dataclass(frozen=True)
class LearnedStrategy:
    strategy: str
    evidence_ids: tuple[str, ...]
    scope: str = "permutation-order-acquisition"

    def live(self, revoked: Iterable[str] = ()) -> bool:
        rv = set(revoked)
        return all(e not in rv for e in self.evidence_ids)


def _before(order: Order, pair: Pair) -> bool:
    a, b = pair
    return order.index(a) < order.index(b)


def _space(roles: Sequence[str]) -> list[Order]:
    return list(itertools.permutations(tuple(roles)))


def _all_pairs(roles: Sequence[str]) -> tuple[Pair, ...]:
    return tuple(itertools.combinations(tuple(roles), 2))


def _choose_fixed(space: Sequence[Order], roles: Sequence[str], asked: set[Pair]) -> Pair:
    for pair in _all_pairs(roles):
        if pair not in asked:
            return pair
    raise AssertionError("fixed policy exhausted questions before unique identification")


def _choose_balanced(space: Sequence[Order], roles: Sequence[str], asked: set[Pair]) -> Pair:
    candidates = []
    for pair in _all_pairs(roles):
        if pair in asked:
            continue
        yes = sum(_before(order, pair) for order in space)
        no = len(space) - yes
        if yes and no:
            candidates.append((abs(yes - no), -min(yes, no), pair))
    if not candidates:
        raise AssertionError("no discriminating pair remains before unique identification")
    return min(candidates)[2]


def acquire_order(roles: Sequence[str], gold: Order, strategy: str) -> StrategyRun:
    if set(roles) != set(gold) or len(roles) != len(gold):
        raise ValueError("gold must be a permutation of roles")
    if strategy not in {"FIXED", "BALANCED"}:
        raise ValueError("unknown acquisition strategy")
    space = _space(roles)
    asked: set[Pair] = set()
    history: list[Pair] = []
    while len(space) > 1:
        pair = _choose_fixed(space, roles, asked) if strategy == "FIXED" else _choose_balanced(space, roles, asked)
        answer = _before(gold, pair)
        asked.add(pair)
        history.append(pair)
        space = [order for order in space if _before(order, pair) == answer]
    if not space or space[0] != gold:
        raise AssertionError("strategy did not identify registered gold")
    return StrategyRun(strategy, len(history), tuple(history), space[0])


def learn_strategy() -> tuple[LearnedStrategy, dict]:
    # Isomorphic paired training families: same n and reverse-order structure,
    # disjoint role names.  This prevents grammar facts from transferring.
    fixed_roles = tuple("ABCDE")
    balanced_roles = tuple("PQRST")
    fixed_gold = tuple(reversed(fixed_roles))
    balanced_gold = tuple(reversed(balanced_roles))
    fixed = acquire_order(fixed_roles, fixed_gold, "FIXED")
    balanced = acquire_order(balanced_roles, balanced_gold, "BALANCED")
    if balanced.interactions >= fixed.interactions:
        raise AssertionError("registered meta-training pair does not discriminate strategy utility")
    evidence = (
        f"meta:paired:isomorphic:fixed:{fixed.interactions}",
        f"meta:paired:isomorphic:balanced:{balanced.interactions}",
    )
    learned = LearnedStrategy("BALANCED", evidence)
    return learned, {
        "fixed_training_interactions": fixed.interactions,
        "balanced_training_interactions": balanced.interactions,
        "isomorphic_family_size": len(fixed_roles),
        "role_overlap": len(set(fixed_roles) & set(balanced_roles)),
    }


def target_run(strategy: LearnedStrategy | None, *, revoked=()) -> StrategyRun:
    # Fresh roles: no learned precedence constraint from meta-training can apply.
    roles = tuple("UVWXYZ")
    gold = tuple(reversed(roles))
    chosen = strategy.strategy if strategy is not None and strategy.live(revoked) else "FIXED"
    return acquire_order(roles, gold, chosen)


def run() -> dict:
    learned, training = learn_strategy()
    meta = target_run(learned)
    reset = target_run(None)
    revoked = target_run(learned, revoked={learned.evidence_ids[0]})
    # Strong parent receives the same finite policy library, paired evidence and
    # persistent learned strategy identity; it must therefore match exactly.
    parent = target_run(LearnedStrategy(learned.strategy, learned.evidence_ids))
    return {
        "receipt": "N1_LANGUAGE_META_STRATEGY_CALIBRATION_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "meta_training": training,
        "learned_strategy": {
            "strategy": learned.strategy,
            "scope": learned.scope,
            "evidence_ids": list(learned.evidence_ids),
        },
        "target": {
            "new_role_symbols_only": True,
            "learned_strategy_interactions": meta.interactions,
            "reset_strategy_interactions": reset.interactions,
            "saving": reset.interactions - meta.interactions,
            "learned_order_equal": meta.learned_order == reset.learned_order,
        },
        "strategy_evidence_revocation": {
            "falls_back_to_fixed": revoked.strategy == "FIXED",
            "interactions": revoked.interactions,
            "matches_reset": revoked.interactions == reset.interactions,
        },
        "strong_persistent_strategy_parent": {
            "interactions": parent.interactions,
            "matches_ocm": parent == meta,
        },
        "meta_strategy_improves_later_acquisition": meta.interactions < reset.interactions,
        "grammar_content_transfer_possible": False,
        "isolated_terminal": "PARENT_SUFFICIENT_META_STRATEGY_CALIBRATION",
        "interpretation": (
            "A persistent evidence-scoped acquisition-policy choice reduces interactions on a fresh role-order family even though no grammar-order fact transfers. "
            "This is a genuine meta-level mechanism calibration, but the equally informed persistent strategy-memory parent matches it exactly; no unique Machine-Epistemics residual is claimed."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
