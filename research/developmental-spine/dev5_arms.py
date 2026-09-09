"""Arms for DEV-5.  One serve loop, two decision rules, and a deliberately
deficient language to show that the rule is what changed.

``SINGLETON`` acts on a rule when its version space has collapsed to one
candidate.  ``UNANIMITY`` acts on a QUERY when every survivor agrees about that
index.  Both are sound while the truth is among the survivors, and neither is
sound when it is not -- which is why ``UNANIMITY_SMALL`` exists.

Both rules pay ``CONSULT_COST`` per consultation. Neither was charged in DEV-3 or
DEV-4, and charging them equally is the only way the comparison between them is
about the rule rather than about who was billed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Sequence

import dev5
from dev1 import COMPOSE_COST, D1World, Pair, VERIFY_COST
from dev1_arms import Phase, Store, _evict_for, run_d0
from dev3 import GUARD_BITS
from dev4 import LEVELS, Pred, language
from retain import (APPLY_COST, DERIVE_COST, FACT_BITS, INDUCE_COST, K_INDUCE,
                    LOOKUP_COST, RULE_BITS)

__all__ = ["ARMS", "ARM_ROLES", "run_arm", "VersionStore", "decide"]

UNDECIDED = None


@dataclass
class VersionStore:
    base: Store = field(default_factory=Store)
    versions: dict[int, tuple[Pred, ...]] = field(default_factory=dict)
    observations: dict[tuple[int, int], bool] = field(default_factory=dict)
    #: rules whose version space is small enough to be worth holding bits for
    held: set[int] = field(default_factory=set)
    #: X7. Cells of a compiled decision table currently held, and what one costs.
    #: Both default to zero, so every arm before X7 measures exactly what it did.
    table_cells: int = 0
    table_cell_bits: int = 0

    def bits(self) -> int:
        return (self.base.bits() + len(self.held) * GUARD_BITS
                + self.table_cells * self.table_cell_bits)

    def copy(self) -> "VersionStore":
        return VersionStore(self.base.copy(),
                            {k: tuple(v) for k, v in self.versions.items()},
                            dict(self.observations), set(self.held),
                            self.table_cells, self.table_cell_bits)


def decide(survivors: Sequence[Pred], index: int, rule_name: str) -> bool | None:
    """What the version space determines about ``index``, or None if undecided.

    ``singleton``  acts only when exactly one candidate remains.
    ``unanimity``  acts when every candidate agrees, however many remain.

    Both return the truth's verdict whenever they return anything, because the
    truth is among the survivors; the second simply returns something far more
    often.
    """
    if not survivors:
        return None
    if rule_name == "singleton":
        return survivors[0].excludes(index) if len(survivors) == 1 else None
    first = survivors[0].excludes(index)
    for pred in survivors[1:]:
        if pred.excludes(index) != first:
            return None
    return first


def _run(world: D1World, d0: Sequence[int], d1: Sequence[Pair], budget: int,
         level: int, rule_name: str, oracle: dict[int, Pred] | None = None,
         consult_cost: int | None = None) -> tuple[Phase, Phase, VersionStore]:
    cost = dev5.CONSULT_COST if consult_cost is None else consult_cost
    lang = language(level, world.base.extension)
    base, p0 = run_d0(world, d0, budget)
    store = VersionStore(base=base.copy())
    for rule in range(world.base.rule_count):
        store.versions[rule] = tuple(lang) if oracle is None else (oracle[rule],)

    def observe(answer: int) -> None:
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        excluded = not world.generated_by_rule(answer)
        store.observations[(rule, index)] = excluded
        if oracle is None:
            store.versions[rule] = tuple(
                p for p in store.versions[rule] if p.excludes(index) == excluded)

    for answer in set(d0):
        if (answer in store.base.facts or answer in store.base.known_exceptions
                or world.rule_of[answer] in store.base.rules):
            observe(answer)

    phase = Phase()
    freq: dict[int, int] = {}

    # A rule induced during D0 must arrive at D1 with its guard held, or it will
    # be verified on every use and the decision rule under test never fires. The
    # first run of this module missed that and every arm -- including the oracle
    # holding the true guard -- paid 2000 checks, which is what a broken hook
    # looks like rather than a finding. Guards are trimmed to budget here on the
    # same terms they are elsewhere: least-demanded first.
    store.held = set(store.base.rules)
    while store.bits() > budget and store.held:
        store.held.discard(min(store.held))
    carried = store.copy()

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

    def serve(answer: int) -> bool:
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        if rule in store.base.rules:
            verdict = None
            if rule in store.held:
                phase.lookup_work += cost
                phase.verifications += 0
                verdict = decide(store.versions[rule], index, rule_name)
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
                # correct unless the version space no longer contains the truth,
                # which happens exactly when the language cannot express it
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


def unanimity_full(world, d0, d1, budget, level, truth, consult_cost=None):
    return _run(world, d0, d1, budget, max(LEVELS), "unanimity",
                consult_cost=consult_cost)


def singleton_full(world, d0, d1, budget, level, truth, consult_cost=None):
    return _run(world, d0, d1, budget, max(LEVELS), "singleton",
                consult_cost=consult_cost)


def unanimity_small(world, d0, d1, budget, level, truth, consult_cost=None):
    """Unanimity over a language that may not contain the truth.

    The control. A small version space is unanimous more often and unanimously
    WRONG more often, so if unanimity looked like a general fix rather than a fix
    for the decision rule, this is where the illusion breaks.
    """
    return _run(world, d0, d1, budget, 1, "unanimity", consult_cost=consult_cost)


def oracle_guard_parent(world, d0, d1, budget, level, truth, consult_cost=None):
    """Handed the true guard for every rule. A ceiling, never a competitor."""
    return _run(world, d0, d1, budget, max(LEVELS), "unanimity", oracle=truth,
                consult_cost=consult_cost)


ARMS: dict[str, Callable[..., tuple[Phase, Phase, VersionStore]]] = {
    "UNANIMITY_FULL": unanimity_full,
    "SINGLETON_FULL": singleton_full,
    "UNANIMITY_SMALL": unanimity_small,
    "ORACLE_GUARD_PARENT": oracle_guard_parent,
}

ARM_ROLES = {
    "UNANIMITY_FULL": "MACHINE",
    "SINGLETON_FULL": "PRIOR_MACHINE_DEV3_DEV4",
    "UNANIMITY_SMALL": "CONTROL_DEFICIENT_LANGUAGE",
    "ORACLE_GUARD_PARENT": "CEILING",
}


def run_arm(arm_id, world, d0, d1, budget, level, truth, consult_cost=None):
    return ARMS[arm_id](world, d0, d1, budget, level, truth, consult_cost)
