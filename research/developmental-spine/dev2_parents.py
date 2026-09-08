"""DEV-2: the continual-learning parents DEV-1 never ran.

``SYNTHESIS_V1`` classifies the continual-learning literature ``OPEN`` against
this lane, with the reason stated plainly:

    OPEN because no continual-learning parent has been run against the lineage at
    all; a replay or EWC parent is the obvious next comparator and its absence is
    a hole in the DEV-1 result, not a detail.

DEV-1's only positive is a carry advantage: CONTINUED_OCM beats RESET_OCM at 1024
bits.  RESET_OCM is the right control for "did carrying help", and it is the
WRONG parent for "is carrying the best available use of that budget".  A field
that has spent a decade on exactly that question was not asked.  This module asks
it.

Three parents, each the closest faithful symbolic analogue of a standard method,
each running the SAME world, the SAME D0 stream, the SAME D1 stream and the SAME
bit budget as the lineage:

``REPLAY_ONLY_PARENT``
    Keep the data, not the abstraction.  It stores derived answers and never
    induces a rule, at either stage.  This is experience replay in its purest
    form and it is the cheapest possible use of the same bits.

``REPLAY_AND_CONSOLIDATE_PARENT``
    Keep the data through D0, then consolidate at the boundary.  It induces
    nothing while D0 runs, and at the stage transition it makes one pass over the
    replay buffer and induces every rule the buffer supports, paying ``INDUCE_COST``
    each.  This is the strongest of the three and the one most likely to beat the
    lineage: it makes the same acquisition decisions with strictly more
    information, because it has seen all of D0 before choosing, where the lineage
    had to commit at the moment the third member of a rule turned up.
    Consolidation reads only what the BOUNDED BUFFER still holds -- not the
    lineage's uncharged record of everything it ever saw -- so the parent is not
    handed memory it never paid for.

``EWC_PARENT``
    Do not overwrite what mattered.  Importance is D0 usage, which is the honest
    symbolic analogue of a Fisher diagonal here, and the top quantile of D0
    objects is protected from eviction during D1.  It is the lineage plus a
    protection rule, so it isolates one idea.

What would make DEV-1's result collapse
---------------------------------------

If any of these matches or beats CONTINUED_OCM at every setting, then carrying an
abstracted store is not the best use of the budget, the D0-to-D1 transition is
PARENT_SUFFICIENT under the doctrine, and DEV-1's conditional win has to be
reclassified from a result into an absorption.  That is registered as the kill
criterion and it is the outcome this module expects at the tight budget, where
DEV-1 already loses to a plain reset.

What it cannot settle
---------------------

These are symbolic analogues, not the methods.  EWC's Fisher information over
network parameters is not a usage count over store entries, and a reviewer who
thinks the analogy is too loose is entitled to that objection; the receipt states
it rather than defending it.  What the analogues do share with the originals is
the mechanism under test -- protect-what-mattered, and replay-then-consolidate --
and they are run at a matched budget against the same streams, which is the part
that makes the comparison mean anything at all.
"""

from __future__ import annotations

import random
from typing import Sequence

from dev1 import D1World, Pair
from dev1_arms import Phase, Store, run_d0, run_d1
from retain import FACT_BITS, INDUCE_COST, K_INDUCE, RULE_BITS

__all__ = ["EWC_PROTECTED_QUANTILE", "replay_only", "replay_and_consolidate",
           "ewc_lineage", "consolidate", "d0_importance", "PARENTS", "PARENT_ROLES"]


#: Fraction of D0 objects, by D0 usage, that EWC protects from eviction.
#: Registered before the run. A value of 1.0 would be DEV-1's original failure
#: mode -- nothing can be displaced -- and 0.0 would be CONTINUED_OCM exactly,
#: so the parameter interpolates between two arms that already exist and its
#: interesting values are strictly inside the interval.
EWC_PROTECTED_QUANTILE: float = 0.5


def d0_importance(store: Store, world: D1World, d0: Sequence[int]) -> dict[int, int]:
    """Usage count over D0, the symbolic stand-in for a Fisher diagonal."""
    counts: dict[int, int] = {}
    for answer in d0:
        counts[answer] = counts.get(answer, 0) + 1
    return counts


def consolidate(store: Store, world: D1World, budget: int, phase: Phase) -> Store:
    """One induction pass over the replay buffer, at the stage boundary.

    Only rules supported by ``K_INDUCE`` answers STILL IN THE BUFFER are induced,
    so the parent consolidates from what it paid to keep rather than from a
    record of everything it ever derived. Rules are taken most-supported first,
    and induction stops when the budget cannot hold another.
    """
    by_rule: dict[int, list[int]] = {}
    for answer in store.facts:
        if world.generated_by_rule(answer):
            by_rule.setdefault(world.rule_of[answer], []).append(answer)
    for r in sorted(by_rule, key=lambda r: (-len(by_rule[r]), r)):
        members = by_rule[r]
        if len(members) < K_INDUCE:
            continue
        freed = [g for g in members]
        room = store.bits() - len(freed) * FACT_BITS + RULE_BITS
        if room > budget:
            continue
        phase.induce_work += INDUCE_COST
        phase.inductions += 1
        store.rules.add(r)
        for g in freed:
            store.facts.remove(g)
    return store


def replay_only(world: D1World, d0: Sequence[int], d1: Sequence[Pair],
                budget: int) -> tuple[Phase, Phase, Store]:
    store, p0 = run_d0(world, d0, budget, induce_base=False)
    carried = store.copy()
    after, p1 = run_d1(world, d1, budget, store, induce_base=False)
    return p0, p1, carried


def replay_and_consolidate(world: D1World, d0: Sequence[int], d1: Sequence[Pair],
                           budget: int) -> tuple[Phase, Phase, Store]:
    store, p0 = run_d0(world, d0, budget, induce_base=False)
    consolidate(store, world, budget, p0)
    carried = store.copy()
    after, p1 = run_d1(world, d1, budget, store, induce_base=True)
    return p0, p1, carried


def ewc_lineage(world: D1World, d0: Sequence[int], d1: Sequence[Pair],
                budget: int) -> tuple[Phase, Phase, Store]:
    store, p0 = run_d0(world, d0, budget, induce_base=True)
    carried = store.copy()
    importance = d0_importance(store, world, d0)
    ranked_facts = sorted(store.facts, key=lambda g: (-importance.get(g, 0), g))
    keep_facts = ranked_facts[:int(len(ranked_facts) * EWC_PROTECTED_QUANTILE)]
    rule_importance = {
        r: sum(importance.get(g, 0) for g in world.members[r]) for r in store.rules}
    ranked_rules = sorted(store.rules, key=lambda r: (-rule_importance.get(r, 0), r))
    keep_rules = ranked_rules[:int(len(ranked_rules) * EWC_PROTECTED_QUANTILE)]
    after, p1 = run_d1(world, d1, budget, store, induce_base=True,
                       protect=(frozenset(keep_rules), frozenset(keep_facts)))
    return p0, p1, carried


PARENTS = {
    "REPLAY_ONLY_PARENT": replay_only,
    "REPLAY_AND_CONSOLIDATE_PARENT": replay_and_consolidate,
    "EWC_PARENT": ewc_lineage,
}

PARENT_ROLES = {
    "REPLAY_ONLY_PARENT": "CONTINUAL_LEARNING_PARENT",
    "REPLAY_AND_CONSOLIDATE_PARENT": "CONTINUAL_LEARNING_PARENT_STRONGEST",
    "EWC_PARENT": "CONTINUAL_LEARNING_PARENT",
}
