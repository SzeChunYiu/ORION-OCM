"""Arms for DEV-4.  The one thing that differs between them is which language
they hold, and whether they may change it.

Correctness is tracked per answer here, unlike every earlier arm in this lane.
That is the point: DEV-1 through DEV-3 all had arms that were correct by
construction, so the capability gate never bound on the machine. An arm holding a
language that may not contain the truth can produce a singleton version space
containing a FALSE guard, skip a check on the strength of it, and answer wrongly
-- and nothing in its own state distinguishes that from the sound case.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Sequence

from dev1 import COMPOSE_COST, D1World, Pair, VERIFY_COST
from dev1_arms import Phase, Store, _evict_for, run_d0
from dev3 import GUARD_BITS
from dev4 import EXPAND_COST, LEVELS, Pred, language
from retain import (APPLY_COST, DERIVE_COST, FACT_BITS, INDUCE_COST, K_INDUCE,
                    LOOKUP_COST, RULE_BITS)

__all__ = ["LangStore", "run_arm", "ARMS", "ARM_ROLES"]

EMPTY = "EMPTY"


@dataclass
class LangStore:
    base: Store = field(default_factory=Store)
    #: rule -> the level of language that rule is currently searching
    levels: dict[int, int] = field(default_factory=dict)
    #: rule -> surviving candidates, or EMPTY when nothing in the level fits
    versions: dict[int, tuple[Pred, ...] | str] = field(default_factory=dict)
    guards: dict[int, Pred] = field(default_factory=dict)
    #: (rule, index) -> observed exception status; the evidence, re-used on expansion
    observations: dict[tuple[int, int], bool] = field(default_factory=dict)
    expansions: int = 0

    def bits(self) -> int:
        return self.base.bits() + len(self.guards) * GUARD_BITS

    def copy(self) -> "LangStore":
        return LangStore(self.base.copy(), dict(self.levels),
                         {k: (v if isinstance(v, str) else tuple(v))
                          for k, v in self.versions.items()},
                         dict(self.guards), dict(self.observations), self.expansions)


def _consistent(preds: Sequence[Pred], evidence: dict[int, bool]) -> tuple[Pred, ...]:
    return tuple(p for p in preds
                 if all(p.excludes(i) == e for i, e in evidence.items()))


def _evidence_for(store: LangStore, rule: int) -> dict[int, bool]:
    return {i: e for (r, i), e in store.observations.items() if r == rule}


def _refresh(store: LangStore, world: D1World, rule: int, phase: Phase,
             may_expand: bool, start_level: int, top_level: int) -> None:
    """Recompute a rule's version space, widening the language if allowed."""
    level = store.levels.setdefault(rule, start_level)
    evidence = _evidence_for(store, rule)
    while True:
        survivors = _consistent(language(level, world.base.extension), evidence)
        if survivors:
            store.versions[rule] = survivors
            store.levels[rule] = level
            if len(survivors) == 1:
                store.guards[rule] = survivors[0]
            else:
                store.guards.pop(rule, None)
            return
        if may_expand and level < top_level:
            level += 1
            store.expansions += 1
            phase.induce_work += EXPAND_COST
            continue
        store.versions[rule] = EMPTY
        store.levels[rule] = level
        store.guards.pop(rule, None)
        return


def _run(world: D1World, d0: Sequence[int], d1: Sequence[Pair], budget: int,
         start_level: int, top_level: int, may_expand: bool,
         oracle_level: int | None = None) -> tuple[Phase, Phase, LangStore]:
    base, p0 = run_d0(world, d0, budget)
    level = oracle_level if oracle_level is not None else start_level
    store = LangStore(base=base.copy())
    for rule in range(world.base.rule_count):
        store.levels[rule] = level

    def observe(answer: int, phase: Phase) -> None:
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        store.observations[(rule, index)] = not world.generated_by_rule(answer)
        _refresh(store, world, rule, phase, may_expand, store.levels.get(rule, level),
                 top_level)

    for answer in set(d0):
        if (answer in store.base.facts or answer in store.base.known_exceptions
                or world.rule_of[answer] in store.base.rules):
            observe(answer, p0)

    carried = store.copy()
    phase = Phase()
    freq: dict[int, int] = {}

    def evict(room: int) -> None:
        while store.bits() + room > budget:
            before = (store.base.bits(), len(store.guards))
            _evict_for(store.base, world, room + len(store.guards) * GUARD_BITS,
                       budget, phase, freq)
            for rule in [r for r in store.guards if r not in store.base.rules]:
                store.guards.pop(rule)
            if (store.base.bits(), len(store.guards)) == before:
                return

    def on_derive(answer: int) -> None:
        rule = world.rule_of[answer]
        observe(answer, phase)
        if not world.generated_by_rule(answer):
            store.base.known_exceptions.add(answer)
        else:
            store.base.seen.setdefault(rule, set()).add(answer)
        if rule not in store.base.rules and len(store.base.seen.get(rule, ())) >= K_INDUCE:
            need = RULE_BITS + GUARD_BITS
            evict(need)
            if store.bits() + need <= budget:
                phase.induce_work += INDUCE_COST
                phase.inductions += 1
                store.base.rules.add(rule)
                for g in [g for g in store.base.facts
                          if world.rule_of[g] == rule and world.generated_by_rule(g)]:
                    store.base.facts.remove(g)
                return
        evict(FACT_BITS)
        if store.bits() + FACT_BITS <= budget:
            store.base.facts.append(answer)

    def serve(answer: int) -> bool:
        """Returns whether the answer given was CORRECT."""
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        if rule in store.base.rules:
            guard = store.guards.get(rule)
            if guard is not None:
                if guard.excludes(index):
                    if answer in store.base.facts:
                        phase.lookup_work += LOOKUP_COST
                        return True
                    phase.derive_work += DERIVE_COST
                    phase.derivations += 1
                    on_derive(answer)
                    return True
                # the guard says the rule applies. If the guard is FALSE -- which
                # is possible exactly when the truth is outside this arm's
                # language -- the answer produced here is wrong, and the arm has
                # no way to know
                phase.apply_work += APPLY_COST
                phase.applications += 1
                phase.reuse_witnesses += 1
                return world.generated_by_rule(answer)
            phase.verify_work += VERIFY_COST
            phase.verifications += 1
            if world.generated_by_rule(answer):
                phase.apply_work += APPLY_COST
                phase.applications += 1
                return True
            phase.harmful_transfer_refusals += 1
            phase.derive_work += DERIVE_COST
            phase.derivations += 1
            on_derive(answer)
            return True
        if answer in store.base.facts:
            phase.lookup_work += LOOKUP_COST
            return True
        phase.derive_work += DERIVE_COST
        phase.derivations += 1
        on_derive(answer)
        return True

    for pair in d1:
        phase.served += 1
        ok = True
        for answer in (pair.left, pair.right):
            freq[answer] = freq.get(answer, 0) + 1
            ok = serve(answer) and ok
        phase.compose_work += COMPOSE_COST
        phase.correct += 1 if ok else 0
        b = store.bits()
        phase.bit_steps += b
        phase.peak_bits = max(phase.peak_bits, b)
    return p0, phase, carried


def expanding_arm(world, d0, d1, budget, world_level=None):
    return _run(world, d0, d1, budget, start_level=1, top_level=max(LEVELS),
                may_expand=True)


def fixed_full_parent(world, d0, d1, budget, world_level=None):
    return _run(world, d0, d1, budget, start_level=max(LEVELS),
                top_level=max(LEVELS), may_expand=False)


def fixed_small_parent(world, d0, d1, budget, world_level=None):
    return _run(world, d0, d1, budget, start_level=1, top_level=1, may_expand=False)


def oracle_level_parent(world, d0, d1, budget, world_level=None):
    """Told the world's LEVEL for free. A ceiling on what knowing how expressive
    to be is worth; never a competitor."""
    return _run(world, d0, d1, budget, start_level=1, top_level=max(LEVELS),
                may_expand=False, oracle_level=world_level)


ARMS: dict[str, Callable[..., tuple[Phase, Phase, LangStore]]] = {
    "EXPANDING_ARM": expanding_arm,
    "FIXED_FULL_PARENT": fixed_full_parent,
    "FIXED_SMALL_PARENT": fixed_small_parent,
    "ORACLE_LEVEL_PARENT": oracle_level_parent,
}

ARM_ROLES = {
    "EXPANDING_ARM": "MACHINE",
    "FIXED_FULL_PARENT": "PARENT_SOUND_BY_CONSTRUCTION",
    "FIXED_SMALL_PARENT": "PARENT_FAST_AND_UNSOUND",
    "ORACLE_LEVEL_PARENT": "CEILING",
}


def run_arm(arm_id: str, world: D1World, d0, d1, budget: int, world_level: int):
    return ARMS[arm_id](world, d0, d1, budget, world_level)
