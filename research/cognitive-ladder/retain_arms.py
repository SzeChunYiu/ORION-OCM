"""Arms for E10: what a machine keeps when keeping costs something.

Every arm answers every demand, so correctness is 1.0 everywhere and the
capability gate of publication constitution section 7 is satisfied by
construction rather than by argument.  What separates the arms is what they
spend and what they hold.

The ledger keeps five work coordinates apart -- derivation, application, lookup,
induction, and the bit-step integral -- and never sums them itself.  Summation
happens once, in ``total_work``, under an explicitly passed ``sigma``, and the
sweep reports the whole ``sigma`` curve.

``belady_instance_cache`` is the arm to beat.  It is shown the entire future
demand stream and evicts furthest-in-future, which for uniform-size uniform-cost
items is optimal: no instance policy, offline or online, can hold fewer misses.
It is not a strawman parent and it is not a fair-information parent -- it has
strictly more information than the arm, deliberately, because a win against it
cannot then be explained by scheduling or by luck.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Sequence

from retain import (
    APPLY_COST,
    DERIVE_COST,
    FACT_BITS,
    INDUCE_COST,
    K_INDUCE,
    LOOKUP_COST,
    RULE_BITS,
    World,
)

__all__ = [
    "Ledger",
    "ARMS",
    "ARM_ROLES",
    "lazy_parent",
    "generalizing_arm",
    "belady_instance_cache",
    "lru_instance_cache",
    "lfu_instance_cache",
    "eager_all_rules_parent",
    "oracle_rule_parent",
    "random_retention_placebo",
    "belady_mixed_reference",
    "run_arm",
]


@dataclass
class Ledger:
    """Five work coordinates, kept apart until an explicit sigma is supplied."""

    derive_work: int = 0
    apply_work: int = 0
    lookup_work: int = 0
    induce_work: int = 0
    #: Integral of held bits over the demand stream.  Storage work at price
    #: ``sigma`` is exactly ``sigma * bit_steps``; one run yields every sigma.
    bit_steps: int = 0
    derivations: int = 0
    inductions: int = 0
    applications: int = 0
    hits: int = 0
    served: int = 0
    correct: int = 0
    peak_bits: int = 0

    def total_work(self, sigma: float) -> float:
        return (self.derive_work + self.apply_work + self.lookup_work
                + self.induce_work + sigma * self.bit_steps)

    def correctness(self) -> float:
        return self.correct / self.served if self.served else 0.0

    def as_dict(self, sigmas: Sequence[float]) -> dict:
        return {
            "derive_work": self.derive_work, "apply_work": self.apply_work,
            "lookup_work": self.lookup_work, "induce_work": self.induce_work,
            "bit_steps": self.bit_steps, "derivations": self.derivations,
            "inductions": self.inductions, "applications": self.applications,
            "hits": self.hits, "served": self.served, "peak_bits": self.peak_bits,
            "correctness": self.correctness(),
            "total_work_by_sigma": {str(s): self.total_work(s) for s in sigmas},
        }


# ---------------------------------------------------------------------------
# parents that hold nothing, or hold everything without choosing
# ---------------------------------------------------------------------------

def lazy_parent(world: World, stream: Sequence[int], budget_bits: int,
                rng: random.Random) -> Ledger:
    """Retains nothing and re-derives on demand.

    This is the arm that won E3, E6, E7 and E8.  It is here to reproduce those
    wins wherever the budget or the compressibility makes retention pointless.
    """
    led = Ledger()
    for _ in stream:
        led.derive_work += DERIVE_COST
        led.derivations += 1
        led.served += 1
        led.correct += 1
    return led


# ---------------------------------------------------------------------------
# instance caches: they may hold answers and may not hold rules
# ---------------------------------------------------------------------------

def lru_instance_cache(world: World, stream: Sequence[int], budget_bits: int,
                       rng: random.Random) -> Ledger:
    """``held`` is use-ordered: a hit moves the answer to the back, so held[0] is
    the least recently USED rather than the least recently inserted."""
    capacity = budget_bits // FACT_BITS
    led = Ledger()
    held: list[int] = []
    for t, f in enumerate(stream):
        led.served += 1
        led.correct += 1
        if f in held:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
            held.remove(f)
            held.append(f)
        else:
            led.derive_work += DERIVE_COST
            led.derivations += 1
            if capacity:
                if len(held) >= capacity:
                    held.pop(0)
                held.append(f)
        bits = len(held) * FACT_BITS
        led.bit_steps += bits
        led.peak_bits = max(led.peak_bits, bits)
    return led


def lfu_instance_cache(world: World, stream: Sequence[int], budget_bits: int,
                       rng: random.Random) -> Ledger:
    freq: dict[int, int] = {}
    capacity = budget_bits // FACT_BITS
    led = Ledger()
    held: list[int] = []
    for t, f in enumerate(stream):
        led.served += 1
        led.correct += 1
        freq[f] = freq.get(f, 0) + 1
        if f in held:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
        else:
            led.derive_work += DERIVE_COST
            led.derivations += 1
            if capacity:
                if len(held) >= capacity:
                    held.remove(min(held, key=lambda g: (freq.get(g, 0), g)))
                held.append(f)
        bits = len(held) * FACT_BITS
        led.bit_steps += bits
        led.peak_bits = max(led.peak_bits, bits)
    return led


def belady_instance_cache(world: World, stream: Sequence[int], budget_bits: int,
                          rng: random.Random) -> Ledger:
    """Clairvoyant, instance-optimal.  The arm to beat.

    Evicts the held answer whose next demand is furthest in the future.  For
    items of uniform size and uniform miss cost this is Belady's rule and is
    optimal, so no instance-keeping policy can serve this stream for less.  It is
    given the entire future; the arm is given none of it.
    """
    horizon = len(stream)
    future: dict[int, list[int]] = {}
    for t, f in enumerate(stream):
        future.setdefault(f, []).append(t)

    def next_after(f: int, t: int) -> int:
        for u in future.get(f, ()):  # streams here are short enough for a scan
            if u > t:
                return u
        return horizon

    capacity = budget_bits // FACT_BITS
    led = Ledger()
    held: list[int] = []
    cursor: dict[int, int] = {}
    for t, f in enumerate(stream):
        led.served += 1
        led.correct += 1
        if f in held:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
        else:
            led.derive_work += DERIVE_COST
            led.derivations += 1
            if capacity:
                if len(held) >= capacity:
                    held.remove(max(held, key=lambda g: (next_after(g, t), g)))
                held.append(f)
        bits = len(held) * FACT_BITS
        led.bit_steps += bits
        led.peak_bits = max(led.peak_bits, bits)
    return led


# ---------------------------------------------------------------------------
# the arm, and the two acquisition schedules it is being separated from
# ---------------------------------------------------------------------------

def _serve_with_stores(world: World, stream: Sequence[int], budget_bits: int,
                       rules: set[int], facts: list[int],
                       on_derive: Callable[[int, int, int], None] | None,
                       led: Ledger) -> Ledger:
    for t, f in enumerate(stream):
        led.served += 1
        led.correct += 1
        r = world.rule_of[f]
        if r in rules:
            led.apply_work += APPLY_COST
            led.applications += 1
        elif f in facts:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
        else:
            led.derive_work += DERIVE_COST
            led.derivations += 1
            if on_derive is not None:
                on_derive(t, f, r)
        bits = len(facts) * FACT_BITS + len(rules) * RULE_BITS
        led.bit_steps += bits
        led.peak_bits = max(led.peak_bits, bits)
    return led


def generalizing_arm(world: World, stream: Sequence[int], budget_bits: int,
                     rng: random.Random) -> Ledger:
    """Derives on demand; induces a rule once demand for it is demonstrated.

    The induction trigger is the thing four earlier experiments said was
    missing: nothing is acquired on a schedule.  A rule is induced only after
    ``K_INDUCE`` distinct answers of that rule have been separately demanded and
    derived, so acquisition is paid for out of demand that has already happened.
    On induction the covered answers are evicted, because holding both the
    generator and its outputs is the one policy that is dominated by construction.
    """
    led = Ledger()
    rules: set[int] = set()
    facts: list[int] = []
    seen: dict[int, set[int]] = {}
    freq: dict[int, int] = {}

    def bits() -> int:
        return len(facts) * FACT_BITS + len(rules) * RULE_BITS

    def evict_until(room: int) -> None:
        while facts and bits() + room > budget_bits:
            facts.remove(min(facts, key=lambda g: (freq.get(g, 0), g)))

    def on_derive(t: int, f: int, r: int) -> None:
        members = seen.setdefault(r, set())
        members.add(f)
        if r not in rules and len(members) >= K_INDUCE:
            evict_until(RULE_BITS)
            if bits() + RULE_BITS <= budget_bits:
                led.induce_work += INDUCE_COST
                led.inductions += 1
                rules.add(r)
                for g in [g for g in facts if world.rule_of[g] == r]:
                    facts.remove(g)
                return
        evict_until(FACT_BITS)
        if bits() + FACT_BITS <= budget_bits:
            facts.append(f)

    for t, f in enumerate(stream):
        freq[f] = freq.get(f, 0) + 1
        led.served += 1
        led.correct += 1
        r = world.rule_of[f]
        if r in rules:
            led.apply_work += APPLY_COST
            led.applications += 1
        elif f in facts:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
        else:
            led.derive_work += DERIVE_COST
            led.derivations += 1
            on_derive(t, f, r)
        b = len(facts) * FACT_BITS + len(rules) * RULE_BITS
        led.bit_steps += b
        led.peak_bits = max(led.peak_bits, b)
    return led


def eager_all_rules_parent(world: World, stream: Sequence[int], budget_bits: int,
                           rng: random.Random) -> Ledger:
    """Acquires every rule before the first demand, then serves.

    This is the acquisition schedule that lost in E3, E6, E7 and E8, run here so
    that the comparison is against it rather than against a memory of it.  It
    pays ``K_INDUCE`` derivations and one induction per rule up front and then
    keeps as many rules as the budget holds, most-popular-by-rule-index first,
    which is the best it can do without seeing demand.
    """
    led = Ledger()
    rules: set[int] = set()
    capacity_rules = budget_bits // RULE_BITS
    for r in range(world.rule_count):
        for _ in range(min(K_INDUCE, world.extension)):
            led.derive_work += DERIVE_COST
            led.derivations += 1
        led.induce_work += INDUCE_COST
        led.inductions += 1
        if len(rules) < capacity_rules:
            rules.add(r)
    facts: list[int] = []
    return _serve_with_stores(world, stream, budget_bits, rules, facts, None, led)


def oracle_rule_parent(world: World, stream: Sequence[int], budget_bits: int,
                       rng: random.Random) -> Ledger:
    """Handed every rule for free, and told which ones the future will demand.

    Charged for storage and for application, never for derivation or induction.
    A ceiling on rule-keeping, not a competitor.
    """
    led = Ledger()
    demand: dict[int, int] = {}
    for f in stream:
        r = world.rule_of[f]
        demand[r] = demand.get(r, 0) + 1
    capacity_rules = budget_bits // RULE_BITS
    ranked = sorted(demand, key=lambda r: (-demand[r], r))[:capacity_rules]
    return _serve_with_stores(world, stream, budget_bits, set(ranked), [], None, led)


def random_retention_placebo(world: World, stream: Sequence[int], budget_bits: int,
                             rng: random.Random) -> Ledger:
    """CL-D2 structural placebo: the arm's shape with the information removed.

    It performs inductions at the same trigger, pays the same induction cost, and
    fills the same budget -- but the rule it induces is drawn uniformly at random
    from the whole rule set rather than being the rule whose demand triggered it,
    and eviction is random rather than by demand. Anything the arm gains over
    this is gained by USING the demand signal, not by having the machinery.
    """
    led = Ledger()
    rules: set[int] = set()
    facts: list[int] = []
    seen: dict[int, set[int]] = {}

    def bits() -> int:
        return len(facts) * FACT_BITS + len(rules) * RULE_BITS

    def evict_until(room: int) -> None:
        while facts and bits() + room > budget_bits:
            facts.remove(rng.choice(facts))

    def on_derive(t: int, f: int, r: int) -> None:
        members = seen.setdefault(r, set())
        members.add(f)
        if len(members) >= K_INDUCE:
            pick = rng.randrange(world.rule_count)
            if pick not in rules:
                evict_until(RULE_BITS)
                if bits() + RULE_BITS <= budget_bits:
                    led.induce_work += INDUCE_COST
                    led.inductions += 1
                    rules.add(pick)
                    for g in [g for g in facts if world.rule_of[g] == pick]:
                        facts.remove(g)
                    return
        evict_until(FACT_BITS)
        if bits() + FACT_BITS <= budget_bits:
            facts.append(f)

    return _serve_with_stores(world, stream, budget_bits, rules, facts, on_derive, led)


def belady_mixed_reference(world: World, stream: Sequence[int], budget_bits: int,
                           rng: random.Random) -> Ledger:
    """Clairvoyant over BOTH representations.  A reference, NOT a proven ceiling.

    Greedily takes the rules with the highest future demand while a rule still
    saves more than the answers its bits would otherwise hold, then fills the
    remainder with Belady instances.  Greedy knapsack over two item types is not
    optimal in general, so a number from this arm bounds nothing; it is reported
    to show how much of the achievable mixed gain the online arm captures, and
    the plan registers that the arm beating it means the reference is wrong
    rather than that a discovery has been made.
    """
    demand: dict[int, int] = {}
    rule_demand: dict[int, int] = {}
    for f in stream:
        demand[f] = demand.get(f, 0) + 1
        r = world.rule_of[f]
        rule_demand[r] = rule_demand.get(r, 0) + 1

    slots_per_rule = RULE_BITS // FACT_BITS
    chosen_rules: set[int] = set()
    remaining = budget_bits
    for r in sorted(rule_demand, key=lambda r: (-rule_demand[r], r)):
        if remaining < RULE_BITS:
            continue
        rule_saving = rule_demand[r] * (DERIVE_COST - APPLY_COST)
        best_instances = sorted(
            (demand[f] for f in world.members[r] if f in demand), reverse=True
        )[:slots_per_rule]
        instance_saving = sum(c * (DERIVE_COST - LOOKUP_COST) for c in best_instances)
        if rule_saving > instance_saving:
            chosen_rules.add(r)
            remaining -= RULE_BITS

    led = Ledger()
    horizon = len(stream)
    future: dict[int, list[int]] = {}
    for t, f in enumerate(stream):
        future.setdefault(f, []).append(t)

    def next_after(f: int, t: int) -> int:
        for u in future.get(f, ()):
            if u > t:
                return u
        return horizon

    capacity = remaining // FACT_BITS
    held: list[int] = []
    for t, f in enumerate(stream):
        led.served += 1
        led.correct += 1
        r = world.rule_of[f]
        if r in chosen_rules:
            led.apply_work += APPLY_COST
            led.applications += 1
        elif f in held:
            led.lookup_work += LOOKUP_COST
            led.hits += 1
        else:
            led.derive_work += DERIVE_COST
            led.derivations += 1
            if capacity:
                if len(held) >= capacity:
                    held.remove(max(held, key=lambda g: (next_after(g, t), g)))
                held.append(f)
        bits = len(held) * FACT_BITS + len(chosen_rules) * RULE_BITS
        led.bit_steps += bits
        led.peak_bits = max(led.peak_bits, bits)
    return led


#: Arms by id.  ``MACHINE`` is the thing under test; everything else is a parent,
#: a placebo, or a declared ceiling, and the roles are asserted in the tests.
ARMS: dict[str, Callable[..., Ledger]] = {
    "generalizing_arm": generalizing_arm,
    "lazy_parent": lazy_parent,
    "lru_instance_cache": lru_instance_cache,
    "lfu_instance_cache": lfu_instance_cache,
    "belady_instance_cache": belady_instance_cache,
    "eager_all_rules_parent": eager_all_rules_parent,
    "oracle_rule_parent": oracle_rule_parent,
    "random_retention_placebo": random_retention_placebo,
    "belady_mixed_reference": belady_mixed_reference,
}

ARM_ROLES: dict[str, str] = {
    "generalizing_arm": "MACHINE",
    "lazy_parent": "PARENT",
    "lru_instance_cache": "PARENT",
    "lfu_instance_cache": "PARENT",
    "belady_instance_cache": "CLAIRVOYANT_OPTIMAL_PARENT",
    "eager_all_rules_parent": "PARENT",
    "oracle_rule_parent": "CEILING",
    "random_retention_placebo": "PLACEBO",
    "belady_mixed_reference": "REFERENCE_NOT_A_CEILING",
}


def run_arm(arm_id: str, world: World, stream: Sequence[int], budget_bits: int,
            seed: int) -> Ledger:
    return ARMS[arm_id](world, stream, budget_bits, random.Random(seed))
