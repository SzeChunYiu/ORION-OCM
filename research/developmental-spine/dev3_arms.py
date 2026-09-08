"""The guarded arm: a rule that carries its own precondition, and pays bits for it.

One arm, one idea.  Everything else in this module is imported unchanged from
DEV-1 and DEV-2 so that the comparison is between representations rather than
between implementations.

The soundness rule is the whole design.  A guard may be USED only when the arm's
version space over the guard language is a singleton.  The truth is always
consistent with what has been observed, so a singleton provably contains it, and
skipping the scope check is then a deduction rather than a bet.  When the version
space empties -- which is what happens the moment exceptions have no structure the
language can express -- the arm detects it, records that this rule has no guard,
and verifies every application for ever after.  That degenerate behaviour is
exactly DEV-1's unguarded lineage, which is why the RANDOM regime is a control
rather than a second experiment.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Sequence

from dev1 import COMPOSE_COST, D1World, Pair, VERIFY_COST
from dev1_arms import Phase, Store, _evict_for, run_d0
from dev3 import GUARD_BITS, Guard, guard_candidates
from retain import (APPLY_COST, DERIVE_COST, FACT_BITS, INDUCE_COST, K_INDUCE,
                    LOOKUP_COST, RULE_BITS)

__all__ = ["GuardedStore", "run_guarded_d1", "guarded_lineage", "NO_GUARD_POSSIBLE"]

#: Sentinel for a rule whose version space has emptied: no guard in the language
#: is consistent with what has been seen, so this rule can never skip a check.
NO_GUARD_POSSIBLE = "NO_GUARD_POSSIBLE"


@dataclass
class GuardedStore:
    """DEV-1's store, plus a version space per rule and the guards that collapsed."""

    base: Store = field(default_factory=Store)
    #: rule -> remaining candidate guards, or NO_GUARD_POSSIBLE
    versions: dict[int, tuple[Guard, ...] | str] = field(default_factory=dict)
    #: rule -> the single guard that survived; usable, and charged GUARD_BITS
    guards: dict[int, Guard] = field(default_factory=dict)
    #: (rule, within-rule index) -> observed exception status, the evidence
    observations: dict[tuple[int, int], bool] = field(default_factory=dict)

    def bits(self) -> int:
        return self.base.bits() + len(self.guards) * GUARD_BITS

    def usable_guard(self, rule: int) -> Guard | None:
        return self.guards.get(rule)


def _index_of(world: D1World, answer: int) -> int:
    return answer - world.rule_of[answer] * world.base.extension


def _observe(store: GuardedStore, world: D1World, answer: int) -> None:
    """Fold one derivation into the version space for its rule.

    The derivation was paid for anyway; what a guard costs is BITS, not extra
    interventions, which is the trade the whole experiment is about.
    """
    rule = world.rule_of[answer]
    index = _index_of(world, answer)
    is_exception = not world.generated_by_rule(answer)
    store.observations[(rule, index)] = is_exception
    current = store.versions.get(rule)
    if current == NO_GUARD_POSSIBLE:
        return
    if current is None:
        current = guard_candidates()
    survivors = tuple(g for g in current if g.excludes(index) == is_exception)
    if not survivors:
        store.versions[rule] = NO_GUARD_POSSIBLE
        store.guards.pop(rule, None)
        return
    store.versions[rule] = survivors
    if len(survivors) == 1:
        store.guards[rule] = survivors[0]
    else:
        store.guards.pop(rule, None)


def run_guarded_d1(world: D1World, stream: Sequence[Pair], budget: int,
                   store: GuardedStore) -> tuple[GuardedStore, Phase]:
    phase = Phase()
    freq: dict[int, int] = {}
    base = store.base

    def evict(room: int) -> None:
        """Make room WITHOUT ever giving up a guard to make space for a fact.

        The first version of this arm let facts crowd guards out, and the effect
        was severe enough to hide the whole result: at 1024 bits it learned all
        sixteen guards during D0, filled the remaining budget with facts, evicted
        every guard to fit them, and then paid to verify 1958 of 2000 member
        demands -- an arm holding sixteen sound guards and using none of them.

        A guard is part of its rule's representation, not an optional extra
        competing with the cache. A rule is admitted only if it and its guard
        both fit, a guard is discarded only when its rule is, and facts are
        evicted to make room for neither. That is a policy correction rather than
        a cost change: guards are charged exactly what they were charged before.
        """
        while store.bits() + room > budget:
            before = (base.bits(), len(store.guards))
            _evict_for(base, world, room + len(store.guards) * GUARD_BITS, budget,
                       phase, freq)
            for rule in [r for r in store.guards if r not in base.rules]:
                store.guards.pop(rule)
            if (base.bits(), len(store.guards)) == before:
                return

    def on_derive(answer: int) -> None:
        rule = world.rule_of[answer]
        _observe(store, world, answer)
        if not world.generated_by_rule(answer):
            base.known_exceptions.add(answer)
        else:
            base.seen.setdefault(rule, set()).add(answer)
        if rule not in base.rules and len(base.seen.get(rule, ())) >= K_INDUCE:
            # reserve the guard's bits at admission: a rule whose guard cannot be
            # held is a rule that will be paid for twice, once in bits and again
            # in checks
            need = RULE_BITS + (GUARD_BITS if rule in store.guards
                                or store.versions.get(rule) != NO_GUARD_POSSIBLE else 0)
            evict(need)
            if store.bits() + need <= budget:
                phase.induce_work += INDUCE_COST
                phase.inductions += 1
                base.rules.add(rule)
                for g in [g for g in base.facts
                          if world.rule_of[g] == rule and world.generated_by_rule(g)]:
                    base.facts.remove(g)
                return
        evict(FACT_BITS)
        if store.bits() + FACT_BITS <= budget:
            base.facts.append(answer)

    def serve(answer: int) -> None:
        rule = world.rule_of[answer]
        if rule in base.rules:
            guard = store.usable_guard(rule)
            if guard is not None:
                # sound: the version space is a singleton, so this guard IS the
                # truth, and no check is needed to know whether the rule applies
                if guard.excludes(_index_of(world, answer)):
                    if answer in base.facts:
                        phase.lookup_work += LOOKUP_COST
                        return
                    phase.derive_work += DERIVE_COST
                    phase.derivations += 1
                    on_derive(answer)
                    return
                phase.apply_work += APPLY_COST
                phase.applications += 1
                phase.reused_object_ids.add(f"guarded_rule:{rule}")
                phase.reuse_witnesses += 1
                return
            phase.verify_work += VERIFY_COST
            phase.verifications += 1
            if world.generated_by_rule(answer):
                phase.apply_work += APPLY_COST
                phase.applications += 1
                phase.reused_object_ids.add(f"rule:{rule}")
                phase.reuse_witnesses += 1
                return
            phase.harmful_transfer_refusals += 1
            phase.negative_transfer_work += VERIFY_COST
            phase.derive_work += DERIVE_COST
            phase.derivations += 1
            on_derive(answer)
            return
        if answer in base.facts:
            phase.lookup_work += LOOKUP_COST
            return
        phase.derive_work += DERIVE_COST
        phase.derivations += 1
        on_derive(answer)

    for pair in stream:
        phase.served += 1
        phase.correct += 1
        for answer in (pair.left, pair.right):
            freq[answer] = freq.get(answer, 0) + 1
            serve(answer)
        phase.compose_work += COMPOSE_COST
        b = store.bits()
        phase.bit_steps += b
        phase.peak_bits = max(phase.peak_bits, b)
    return store, phase


def guarded_lineage(world: D1World, d0: Sequence[int], d1: Sequence[Pair],
                    budget: int) -> tuple[Phase, Phase, GuardedStore]:
    """D0 exactly as DEV-1 runs it, then D1 with guards learned from D0's own
    derivations. No extra intervention is bought to learn a guard."""
    base, p0 = run_d0(world, d0, budget)
    store = GuardedStore(base=base.copy())
    for answer in set(d0):
        # every one of these was derived and paid for during D0; folding the
        # observation into the version space costs nothing but the guard's bits
        if answer in store.base.facts or answer in store.base.known_exceptions \
                or world.rule_of[answer] in store.base.rules:
            _observe(store, world, answer)
    carried = GuardedStore(base=store.base.copy(), versions=dict(store.versions),
                           guards=dict(store.guards),
                           observations=dict(store.observations))
    after, p1 = run_guarded_d1(world, d1, budget, store)
    return p0, p1, carried
