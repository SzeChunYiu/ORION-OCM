"""Arms for E12.  The store is free and unbounded; only derivation gets dearer.

Every arm serves every demand, so correctness is 1.0 by construction and the work
comparison is admissible.  What separates them is when they pay to derive and
what they hold afterwards.

Note what free storage does to the arms E10 needed: no eviction policy, no bit
accounting, no budget.  Those are gone on purpose.  If E12 reproduced E10's
result while sharing E10's scarcity machinery, the two experiments would not be
independent tests of anything.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Sequence

from perish import PerishWorld
from retain import APPLY_COST, INDUCE_COST, K_INDUCE, LOOKUP_COST

__all__ = ["Ledger", "ARMS", "ARM_ROLES", "run_arm"]


@dataclass
class Ledger:
    derive_work: float = 0.0
    apply_work: float = 0.0
    lookup_work: float = 0.0
    induce_work: float = 0.0
    derivations: int = 0
    inductions: int = 0
    applications: int = 0
    hits: int = 0
    #: derivations of an answer never demanded before -- the coordinate that
    #: perishability actually acts on
    first_contacts: int = 0
    first_contact_work: float = 0.0
    served: int = 0
    correct: int = 0
    held_facts: int = 0
    held_rules: int = 0

    def total_work(self) -> float:
        return self.derive_work + self.apply_work + self.lookup_work + self.induce_work

    def correctness(self) -> float:
        return self.correct / self.served if self.served else 0.0

    def as_dict(self) -> dict:
        return {
            "derive_work": self.derive_work, "apply_work": self.apply_work,
            "lookup_work": self.lookup_work, "induce_work": self.induce_work,
            "derivations": self.derivations, "inductions": self.inductions,
            "applications": self.applications, "hits": self.hits,
            "first_contacts": self.first_contacts,
            "first_contact_work": self.first_contact_work,
            "served": self.served, "correctness": self.correctness(),
            "held_facts": self.held_facts, "held_rules": self.held_rules,
            "total_work": self.total_work(),
        }


def lazy_parent(world: PerishWorld, stream: Sequence[int], rng: random.Random) -> Ledger:
    """Keeps nothing.  Under a rising price this is the worst possible policy and
    it is here to show how much of any advantage is simply 'do not throw work
    away', which no one needs a machine for."""
    led = Ledger()
    for t, answer in enumerate(stream):
        led.served += 1
        led.correct += 1
        cost = world.derive(t)
        led.derive_work += cost
        led.derivations += 1
    return led


def memoizer_parent(world: PerishWorld, stream: Sequence[int], rng: random.Random) -> Ledger:
    """Keeps every answer it ever derives, forever.  The parent to beat.

    With storage free this is the folklore-optimal instance policy: it never
    forgets, so it never pays twice for the same answer, and the only thing left
    to beat it on is an answer it has never derived.
    """
    led = Ledger()
    held: set[int] = set()
    for t, answer in enumerate(stream):
        led.served += 1
        led.correct += 1
        if answer in held:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
            continue
        cost = world.derive(t)
        led.derive_work += cost
        led.derivations += 1
        led.first_contacts += 1
        led.first_contact_work += cost
        held.add(answer)
    led.held_facts = len(held)
    return led


def generalizing_arm(world: PerishWorld, stream: Sequence[int], rng: random.Random) -> Ledger:
    """Derives on demand; induces a rule once K_INDUCE of its answers are demanded.

    Identical trigger to E10's arm: nothing is acquired on a schedule, and the
    rule is paid for out of demand that has already happened. Because the store
    is free it keeps its derived answers too, so it is strictly a memoizer PLUS
    induction -- which is what makes the comparison against memoizer_parent a
    comparison of one thing.
    """
    led = Ledger()
    held: set[int] = set()
    rules: set[int] = set()
    seen: dict[int, set[int]] = {}
    for t, answer in enumerate(stream):
        led.served += 1
        led.correct += 1
        r = world.base.rule_of[answer]
        if r in rules:
            led.apply_work += APPLY_COST
            led.applications += 1
            continue
        if answer in held:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
            continue
        cost = world.derive(t)
        led.derive_work += cost
        led.derivations += 1
        led.first_contacts += 1
        led.first_contact_work += cost
        held.add(answer)
        members = seen.setdefault(r, set())
        members.add(answer)
        if len(members) >= K_INDUCE:
            led.induce_work += INDUCE_COST
            led.inductions += 1
            rules.add(r)
    led.held_facts, led.held_rules = len(held), len(rules)
    return led


def eager_all_rules_parent(world: PerishWorld, stream: Sequence[int],
                           rng: random.Random) -> Ledger:
    """Acquires every rule at step 0, before seeing a single demand.

    The schedule that lost in E3, E6, E7 and E10. Here it buys its derivations at
    the cheapest price the world will ever offer, which is exactly the advantage
    the deep root's falsifier was written to look for.
    """
    led = Ledger()
    rules: set[int] = set()
    for r in range(world.base.rule_count):
        for _ in range(min(K_INDUCE, world.base.extension)):
            cost = world.derive(0)
            led.derive_work += cost
            led.derivations += 1
            led.first_contacts += 1
            led.first_contact_work += cost
        led.induce_work += INDUCE_COST
        led.inductions += 1
        rules.add(r)
    for t, answer in enumerate(stream):
        led.served += 1
        led.correct += 1
        led.apply_work += APPLY_COST
        led.applications += 1
    led.held_rules = len(rules)
    return led


def clairvoyant_memoizer_parent(world: PerishWorld, stream: Sequence[int],
                                rng: random.Random) -> Ledger:
    """Shown the whole future; derives exactly the demanded answers at step 0.

    The strongest instance-shaped policy that exists in this world. It buys the
    right set -- no waste on answers never demanded -- at the cheapest moment.
    Nothing that stores instances can beat it, so beating it is a claim about
    representation and not about timing.
    """
    led = Ledger()
    needed = set(stream)
    for _ in needed:
        cost = world.derive(0)
        led.derive_work += cost
        led.derivations += 1
        led.first_contacts += 1
        led.first_contact_work += cost
    for answer in stream:
        led.served += 1
        led.correct += 1
        led.lookup_work += LOOKUP_COST
        led.hits += 1
    led.held_facts = len(needed)
    return led


def oracle_rule_parent(world: PerishWorld, stream: Sequence[int],
                       rng: random.Random) -> Ledger:
    """Handed every rule free.  Charged for application only.  A ceiling."""
    led = Ledger()
    for answer in stream:
        led.served += 1
        led.correct += 1
        led.apply_work += APPLY_COST
        led.applications += 1
    led.held_rules = world.base.rule_count
    return led


ARMS: dict[str, Callable[..., Ledger]] = {
    "generalizing_arm": generalizing_arm,
    "memoizer_parent": memoizer_parent,
    "clairvoyant_memoizer_parent": clairvoyant_memoizer_parent,
    "eager_all_rules_parent": eager_all_rules_parent,
    "lazy_parent": lazy_parent,
    "oracle_rule_parent": oracle_rule_parent,
}

ARM_ROLES: dict[str, str] = {
    "generalizing_arm": "MACHINE",
    "memoizer_parent": "PARENT_TO_BEAT",
    "clairvoyant_memoizer_parent": "CLAIRVOYANT_INSTANCE_OPTIMAL_PARENT",
    "eager_all_rules_parent": "PARENT_DEEP_ROOT_FALSIFIER",
    "lazy_parent": "PARENT_FLOOR",
    "oracle_rule_parent": "CEILING",
}


def run_arm(arm_id: str, world: PerishWorld, stream: Sequence[int], seed: int) -> Ledger:
    return ARMS[arm_id](world, stream, random.Random(seed))
