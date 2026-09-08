"""Arms for DEV-6: one decision rule, three honest bills.

The serve loop is DEV-5's. What changes is the charge for consulting the version
space, and for the incremental arm, where that charge is paid.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Sequence

from dev1 import COMPOSE_COST, D1World, Pair, VERIFY_COST
from dev1_arms import Phase, Store, _evict_for, run_d0
from dev3 import GUARD_BITS
from dev4 import LEVELS, Pred, language
from dev5_arms import VersionStore
from retain import (APPLY_COST, DERIVE_COST, FACT_BITS, INDUCE_COST, K_INDUCE,
                    LOOKUP_COST, RULE_BITS)

__all__ = ["ARMS", "ARM_ROLES", "run_arm", "VoteBook"]


@dataclass
class VoteBook:
    """Per (rule, index) counts of survivors voting each way.

    A query is determined exactly when one of the two counts is zero, which is
    O(1). The cost moves to elimination time: withdrawing a survivor's votes
    touches every index, so it is charged ``extension`` per elimination. That is
    a bet on query volume and it can lose, which is why P3 registers that it
    should lose at short D1 lengths.
    """

    extension: int
    yes: dict[tuple[int, int], int] = field(default_factory=dict)
    no: dict[tuple[int, int], int] = field(default_factory=dict)
    maintenance: int = 0

    def seed(self, rule: int, survivors: Sequence[Pred]) -> None:
        for index in range(self.extension):
            y = sum(1 for p in survivors if p.excludes(index))
            self.yes[(rule, index)] = y
            self.no[(rule, index)] = len(survivors) - y
        self.maintenance += self.extension * len(survivors)

    def eliminate(self, rule: int, gone: Sequence[Pred]) -> None:
        for pred in gone:
            for index in range(self.extension):
                key = (rule, index)
                if pred.excludes(index):
                    self.yes[key] -= 1
                else:
                    self.no[key] -= 1
            self.maintenance += self.extension

    def decided(self, rule: int, index: int) -> bool | None:
        key = (rule, index)
        y, n = self.yes.get(key, 0), self.no.get(key, 0)
        if y and n:
            return None
        if y:
            return True
        if n:
            return False
        return None


def _run(world: D1World, d0: Sequence[int], d1: Sequence[Pair], budget: int,
         mode: str) -> tuple[Phase, Phase, VersionStore, dict]:
    lang = language(max(LEVELS), world.base.extension)
    base, p0 = run_d0(world, d0, budget)
    store = VersionStore(base=base.copy())
    for rule in range(world.base.rule_count):
        store.versions[rule] = tuple(lang)
    votes = VoteBook(world.base.extension) if mode == "unanimity_incremental" else None
    seeded: set[int] = set()

    def observe(answer: int) -> None:
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        excluded = not world.generated_by_rule(answer)
        store.observations[(rule, index)] = excluded
        before = store.versions[rule]
        after = tuple(p for p in before if p.excludes(index) == excluded)
        store.versions[rule] = after
        if votes is not None:
            if rule not in seeded:
                votes.seed(rule, before)
                seeded.add(rule)
            votes.eliminate(rule, [p for p in before if p not in set(after)])

    for answer in set(d0):
        if (answer in store.base.facts or answer in store.base.known_exceptions
                or world.rule_of[answer] in store.base.rules):
            observe(answer)

    store.held = set(store.base.rules)
    while store.bits() > budget and store.held:
        store.held.discard(min(store.held))
    carried = store.copy()

    phase = Phase()
    freq: dict[int, int] = {}
    consultation_charge = 0

    def charge(n: int) -> None:
        nonlocal consultation_charge
        consultation_charge += n
        phase.lookup_work += n

    def evict(room: int) -> None:
        while store.bits() + room > budget:
            before = (store.base.bits(), len(store.held))
            _evict_for(store.base, world, room + len(store.held) * GUARD_BITS,
                       budget, phase, freq)
            for rule in [r for r in store.held if r not in store.base.rules]:
                store.held.discard(rule)
            if (store.base.bits(), len(store.held)) == before:
                return

    def on_derive(answer: int) -> None:
        rule = world.rule_of[answer]
        observe(answer)
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
                store.held.add(rule)
                for g in [g for g in store.base.facts
                          if world.rule_of[g] == rule and world.generated_by_rule(g)]:
                    store.base.facts.remove(g)
                return
        evict(FACT_BITS)
        if store.bits() + FACT_BITS <= budget:
            store.base.facts.append(answer)

    def consult(rule: int, index: int) -> bool | None:
        survivors = store.versions[rule]
        if mode == "singleton":
            charge(1)
            return survivors[0].excludes(index) if len(survivors) == 1 else None
        if mode == "unanimity_naive":
            charge(max(1, len(survivors)))
            if not survivors:
                return None
            first = survivors[0].excludes(index)
            return first if all(p.excludes(index) == first for p in survivors[1:]) else None
        charge(1)
        if rule not in seeded:
            votes.seed(rule, store.versions[rule])
            seeded.add(rule)
        return votes.decided(rule, index)

    def serve(answer: int) -> bool:
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        if rule in store.base.rules:
            verdict = consult(rule, index) if rule in store.held else None
            if verdict is True:
                if answer in store.base.facts:
                    phase.lookup_work += LOOKUP_COST
                    return True
                phase.derive_work += DERIVE_COST
                phase.derivations += 1
                on_derive(answer)
                return True
            if verdict is False:
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

    maintenance = votes.maintenance if votes is not None else 0
    phase.lookup_work += maintenance
    meters = {"consultation_charge": consultation_charge, "maintenance": maintenance,
              "deliberation_total": consultation_charge + maintenance}
    return p0, phase, carried, meters


ARMS: dict[str, Callable[..., tuple]] = {
    "SINGLETON": lambda w, a, b, c: _run(w, a, b, c, "singleton"),
    "UNANIMITY_NAIVE": lambda w, a, b, c: _run(w, a, b, c, "unanimity_naive"),
    "UNANIMITY_INCREMENTAL": lambda w, a, b, c: _run(w, a, b, c, "unanimity_incremental"),
}

ARM_ROLES = {
    "SINGLETON": "PRIOR_RULE_DEV3_DEV4",
    "UNANIMITY_NAIVE": "DEV5_ARM_WITH_AN_HONEST_BILL",
    "UNANIMITY_INCREMENTAL": "MACHINE",
}


def run_arm(arm_id: str, world, d0, d1, budget: int):
    return ARMS[arm_id](world, d0, d1, budget)
