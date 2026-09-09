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



def _unanimous(survivors, index: int) -> bool | None:
    """The unanimity verdict for one index. Identical to dev5_arms.decide with the
    ``unanimity`` rule; factored out so the precompiled modes cannot drift from it.
    """
    if not survivors:
        return None
    first = survivors[0].excludes(index)
    for pred in survivors[1:]:
        if pred.excludes(index) != first:
            return None
    return first


def _run(world: D1World, d0: Sequence[int], d1: Sequence[Pair], budget: int,
         mode: str, lang_level: int | None = None,
         table_cell_bits: int = 0) -> tuple[Phase, Phase, VersionStore, dict]:
    # lang_level defaults to the full ladder, so every DEV-6 arm is unchanged and
    # its receipt reproduces; X4 passes 1 to run the SMALL language DEV-3 used.
    lang = language(max(LEVELS) if lang_level is None else lang_level,
                    world.base.extension)
    base, p0 = run_d0(world, d0, budget)
    store = VersionStore(base=base.copy())
    # X7 charges a compiled table cell bits from the SAME budget as facts and
    # guards. At the default of zero this is identical to every earlier arm.
    store.table_cell_bits = table_cell_bits
    for rule in range(world.base.rule_count):
        store.versions[rule] = tuple(lang)
    votes = VoteBook(world.base.extension) if mode == "unanimity_incremental" else None
    seeded: set[int] = set()
    #: X6. A compiled decision table per rule: the unanimity verdict for an index,
    #: cached until the rule's version space actually shrinks. The table changes
    #: what a consultation COSTS and never what it returns.
    compiled: dict[int, dict] = {}
    #: last step at which each compiled rule was consulted, for LRU discard
    table_touched: dict[int, int] = {}
    step = 0
    tables_discarded = 0
    cells_refused = 0
    compilations = 0
    compiled_cells = 0
    cache_hits = 0
    cache_misses = 0

    def observe(answer: int) -> None:
        rule = world.rule_of[answer]
        index = answer - rule * world.base.extension
        excluded = not world.generated_by_rule(answer)
        store.observations[(rule, index)] = excluded
        before = store.versions[rule]
        after = tuple(p for p in before if p.excludes(index) == excluded)
        # A filter that removes nothing yields an equal tuple with a NEW identity.
        # Keeping the old object is semantically a no-op -- the contents are the
        # same order and the same members -- and it lets X6's compiled tables tell
        # a real elimination from a re-observation instead of recompiling on both.
        if len(after) != len(before):
            store.versions[rule] = after
            after = store.versions[rule]
        else:
            after = before
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
    consultations = 0

    def charge(n: int) -> None:
        # ``consultations`` counts calls and ``consultation_charge`` counts what
        # those calls examined. X5 needs both to separate the SIZE of a version
        # space from the COST of consulting one; DEV-6 needs only the second and
        # its receipt is unchanged by the extra counter.
        nonlocal consultation_charge, consultations
        consultation_charge += n
        consultations += 1
        phase.lookup_work += n

    def charge_compilation(n: int) -> None:
        # Compiling a table is not a consultation. It costs the same kind of work
        # and is charged into the same channel, but counting it as a consultation
        # would inflate the meter X6 divides its cache hit rate by.
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
        if mode in ("precompiled_eager", "precompiled_demand"):
            nonlocal compilations, compiled_cells, cache_hits, cache_misses
            nonlocal tables_discarded, cells_refused
            table_touched[rule] = step

            def room_for(cells: int) -> bool:
                """Make space for ``cells`` table cells, discarding whole tables.

                Whole tables rather than single cells, and least-recently-consulted
                first: per-cell bookkeeping would itself need bits and work, and
                charging for a policy this study did not measure would be worse than
                choosing a coarse one and saying so. The current rule is never
                discarded to make room for itself.
                """
                need = cells * store.table_cell_bits
                if not need or store.bits() + need <= budget:
                    return True
                order = sorted((r for r in compiled if r != rule),
                               key=lambda r: table_touched.get(r, -1))
                for victim in order:
                    nonlocal tables_discarded
                    store.table_cells -= len(compiled[victim]["cells"])
                    del compiled[victim]
                    table_touched.pop(victim, None)
                    tables_discarded += 1
                    if store.bits() + need <= budget:
                        return True
                return store.bits() + need <= budget

            table = compiled.get(rule)
            if table is None or table["version"] is not survivors:
                table = compiled[rule] = {"version": survivors, "cells": {}}
                compilations += 1
                if mode == "precompiled_eager" and room_for(world.base.extension):
                    # Compile every index whether or not anyone asks for it. This is
                    # what an eagerly grounded bank does, and it is charged for the
                    # whole scan it performs.
                    width = max(1, len(survivors))
                    for i in range(world.base.extension):
                        table["cells"][i] = _unanimous(survivors, i)
                    store.table_cells += world.base.extension
                    compiled_cells += world.base.extension
                    charge_compilation(width * world.base.extension)
            if index in table["cells"]:
                cache_hits += 1
                charge(1)
                return table["cells"][index]
            cache_misses += 1
            charge(max(1, len(survivors)))
            verdict = _unanimous(survivors, index)
            if room_for(1):
                table["cells"][index] = verdict
                store.table_cells += 1
                compiled_cells += 1
            else:
                # No bits for the cell. The arm still answers, and answers the same
                # thing; it simply pays the scan again next time. This is how the
                # compiled arms degrade to the naive rule rather than failing.
                cells_refused += 1
            return verdict
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
        step += 1
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
    meters = {"compilations": compilations, "compiled_cells": compiled_cells,
              "tables_discarded": tables_discarded, "cells_refused": cells_refused,
              "table_cells_held": store.table_cells,
              "cache_hits": cache_hits, "cache_misses": cache_misses,
              "consultation_charge": consultation_charge, "maintenance": maintenance,
              "deliberation_total": consultation_charge + maintenance,
              "consultations": consultations,
              "held_rules_final": len(store.held),
              "rules_final": len(store.base.rules),
              "language_size": len(lang)}
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
