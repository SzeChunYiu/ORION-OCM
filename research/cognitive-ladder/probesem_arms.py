"""Arms for E11.  Every arm buys probes, commits a diagnosis, and is then told the truth.

The comparison this module exists for is between two REPRESENTATIONS of the same
evidence, so the two learners are given the same interface, the same budget, the
same revelations and the same exploration rule.  What differs is only what they
write down:

``semantics_learner``  a cell per (probe, cause).  One resolved case with three
                       bought probes fills three cells, and those cells are
                       usable on every future case regardless of which other
                       probes were bought with them.
``mapping_parent``     a count per (evidence set, cause).  One resolved case
                       fills one row, and that row is usable only on cases whose
                       bought evidence matches it exactly.

That is the whole of the hypothesis: per-cell evidence composes and per-row
evidence does not.  Everything else is held equal on purpose, including the
optimism bonus that makes both arms try an instrument they have never used --
without it the mapping parent would simply never buy the sixth probe, keep its
old rows, and appear to survive the extension by declining to notice it.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence

from probesem import CAUSES, EXTRA_PROBE, EXTRA_PROBE_COST, Case, World
from diagnosis import CAUSE_PRIOR, PROBE_COST, Cause

__all__ = ["Outcome", "Trace", "ARMS", "ARM_ROLES", "run_arm", "cost_of",
           "OPTIMISM", "UNKNOWN_CELL_BONUS"]

#: Value added to an unseen instrument's score so that every arm tries it.  Held
#: identical across arms: it is a property of the harness, not of any policy.
OPTIMISM: float = 0.75

#: Weight on filling an unknown semantics cell, relative to eliminating a cause.
#: Registered before the run; the semantics learner is the only arm with cells,
#: so this is the one knob it has that the parents do not, and it is disclosed
#: rather than tuned.
UNKNOWN_CELL_BONUS: float = 0.35


def cost_of(probe: str) -> int:
    for p, c in PROBE_COST.items():
        if p.value == probe:
            return c
    if probe == EXTRA_PROBE:
        return EXTRA_PROBE_COST
    raise KeyError(probe)


@dataclass
class Trace:
    """What an arm did, case by case.  Accuracy and refusals never merge."""

    correct: list[bool] = field(default_factory=list)
    refused: list[bool] = field(default_factory=list)
    probe_cost: int = 0
    probes_bought: int = 0

    def rolling_accuracy(self, at: int, window: int) -> float:
        lo = max(0, at - window)
        chunk = self.correct[lo:at]
        return sum(chunk) / len(chunk) if chunk else 0.0

    def first_index_reaching(self, target: float, window: int) -> int | None:
        for i in range(window, len(self.correct) + 1):
            if self.rolling_accuracy(i, window) >= target:
                return i
        return None

    def as_dict(self, target: float, window: int) -> dict:
        reached = self.first_index_reaching(target, window)
        return {
            "cases": len(self.correct),
            "accuracy": sum(self.correct) / len(self.correct) if self.correct else 0.0,
            "refusal_rate": sum(self.refused) / len(self.refused) if self.refused else 0.0,
            "probe_cost": self.probe_cost,
            "probes_bought": self.probes_bought,
            "cases_to_target": reached,
            "reached_target": reached is not None,
        }


def _prior_argmax(counts: Mapping[Cause, int], among: Sequence[Cause]) -> Cause:
    pool = list(among) or list(CAUSES)
    return max(pool, key=lambda c: (counts.get(c, 0), CAUSES.index(c)))


# ---------------------------------------------------------------------------
# the machine: a cell per (probe, cause)
# ---------------------------------------------------------------------------

def semantics_learner(world: World, stream: Sequence[Case], probes_at: Callable[[int], list[str]],
                      budget: int, rng: random.Random) -> Trace:
    cells: dict[tuple[str, str], bool] = {}
    seen_cause: dict[Cause, int] = {}
    trace = Trace()

    def live(observed: dict[str, bool]) -> list[Cause]:
        out = []
        for cause in CAUSES:
            ok = True
            for probe, value in observed.items():
                known = cells.get((probe, cause.value))
                if known is not None and known != value:
                    ok = False
                    break
            if ok:
                out.append(cause)
        return out

    def unknown_in(probe: str, among: Sequence[Cause]) -> int:
        return sum(1 for c in among if (probe, c.value) not in cells)

    def elimination(probe: str, among: Sequence[Cause]) -> float:
        known = [cells[(probe, c.value)] for c in among if (probe, c.value) in cells]
        if not known:
            return 0.0
        yes = sum(1 for v in known if v)
        no = len(known) - yes
        return min(yes, no)

    for case in stream:
        available = list(probes_at(len(trace.correct)))
        observed: dict[str, bool] = {}
        for _ in range(budget):
            among = live(observed)
            best, chosen = None, None
            for probe in available:
                if probe in observed:
                    continue
                score = elimination(probe, among) + UNKNOWN_CELL_BONUS * unknown_in(probe, among)
                if not any((probe, c.value) in cells for c in CAUSES):
                    score += OPTIMISM
                key = (score / cost_of(probe), -cost_of(probe), probe)
                if best is None or key > best:
                    best, chosen = key, probe
            if chosen is None or best[0] <= 0:
                break
            observed[chosen] = world.observe(chosen, case.cause)
            trace.probe_cost += cost_of(chosen)
            trace.probes_bought += 1

        among = live(observed)
        guess = _prior_argmax(seen_cause, among)
        trace.correct.append(guess is case.cause)
        trace.refused.append(len(among) > 1)

        # resolution: the truth arrives after the diagnosis is committed
        seen_cause[case.cause] = seen_cause.get(case.cause, 0) + 1
        for probe, value in observed.items():
            cells[(probe, case.cause.value)] = value
    return trace


# ---------------------------------------------------------------------------
# the parent: a count per (evidence set, cause)
# ---------------------------------------------------------------------------

def _mapping_arm(world: World, stream: Sequence[Case], probes_at, budget: int,
                 rng: random.Random, choose: str) -> Trace:
    rows: dict[frozenset[tuple[str, bool]], dict[Cause, int]] = {}
    marginal: dict[Cause, int] = {}
    #: per (probe, outcome) counts, used only by the information-gain chooser
    seen_probe: dict[str, dict[tuple[bool, Cause], int]] = {}
    trace = Trace()

    def row_for(observed: dict[str, bool]) -> dict[Cause, int]:
        return rows.get(frozenset(observed.items()), {})

    def gain(probe: str, observed: dict[str, bool]) -> float:
        counts = seen_probe.get(probe)
        if not counts:
            return OPTIMISM
        by_outcome: dict[bool, dict[Cause, int]] = {}
        for (value, cause), n in counts.items():
            bucket = by_outcome.setdefault(value, {})
            bucket[cause] = bucket.get(cause, 0) + n
        total = sum(sum(d.values()) for d in by_outcome.values())
        if not total:
            return OPTIMISM
        base = _entropy(marginal)
        cond = 0.0
        for value, d in by_outcome.items():
            w = sum(d.values()) / total
            cond += w * _entropy(d)
        return max(0.0, base - cond)

    for case in stream:
        available = list(probes_at(len(trace.correct)))
        observed: dict[str, bool] = {}
        for _ in range(budget):
            pool = [p for p in available if p not in observed]
            if not pool:
                break
            if choose == "random":
                probe = rng.choice(pool)
            elif choose == "fixed":
                probe = min(pool, key=lambda p: (cost_of(p), p))
            else:
                probe = max(pool, key=lambda p: (gain(p, observed) / cost_of(p),
                                                 -cost_of(p), p))
            observed[probe] = world.observe(probe, case.cause)
            trace.probe_cost += cost_of(probe)
            trace.probes_bought += 1

        row = row_for(observed)
        guess = _prior_argmax(row if row else marginal, list(row) or list(CAUSES))
        trace.correct.append(guess is case.cause)
        trace.refused.append(len(row) > 1 or not row)

        marginal[case.cause] = marginal.get(case.cause, 0) + 1
        key = frozenset(observed.items())
        row_counts = rows.setdefault(key, {})
        row_counts[case.cause] = row_counts.get(case.cause, 0) + 1
        for probe, value in observed.items():
            seen_probe.setdefault(probe, {})
            seen_probe[probe][(value, case.cause)] = (
                seen_probe[probe].get((value, case.cause), 0) + 1)
    return trace


def _entropy(counts: Mapping[Cause, int]) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    out = 0.0
    for n in counts.values():
        if n:
            p = n / total
            out -= p * math.log(p, 2)
    return out


def mapping_parent(world, stream, probes_at, budget, rng):
    return _mapping_arm(world, stream, probes_at, budget, rng, "gain")


def random_probe_parent(world, stream, probes_at, budget, rng):
    return _mapping_arm(world, stream, probes_at, budget, rng, "random")


def fixed_order_parent(world, stream, probes_at, budget, rng):
    return _mapping_arm(world, stream, probes_at, budget, rng, "fixed")


def naive_bayes_parent(world: World, stream: Sequence[Case], probes_at, budget: int,
                       rng: random.Random) -> Trace:
    """Per-probe likelihoods with an independence assumption imposed.

    It sits between the two representations: like the semantics learner its
    evidence is per-probe and composes, and like the mapping parent it holds
    frequencies rather than a table. If it matches the semantics learner then
    what pays is per-probe evidence and not the table, which would narrow the
    claim considerably, so it is here to make that outcome visible.
    """
    counts: dict[str, dict[tuple[bool, Cause], int]] = {}
    marginal: dict[Cause, int] = {}
    trace = Trace()

    def score(cause: Cause, observed: dict[str, bool]) -> float:
        out = math.log(marginal.get(cause, 0) + 1)
        for probe, value in observed.items():
            d = counts.get(probe, {})
            hit = d.get((value, cause), 0)
            tot = d.get((True, cause), 0) + d.get((False, cause), 0)
            out += math.log((hit + 0.5) / (tot + 1.0))
        return out

    def gain(probe: str) -> float:
        d = counts.get(probe)
        if not d:
            return OPTIMISM
        split: dict[bool, dict[Cause, int]] = {}
        for (value, cause), n in d.items():
            bucket = split.setdefault(value, {})
            bucket[cause] = bucket.get(cause, 0) + n
        total = sum(sum(x.values()) for x in split.values()) or 1
        return max(0.0, _entropy(marginal)
                   - sum(sum(x.values()) / total * _entropy(x) for x in split.values()))

    for case in stream:
        available = list(probes_at(len(trace.correct)))
        observed: dict[str, bool] = {}
        for _ in range(budget):
            pool = [p for p in available if p not in observed]
            if not pool:
                break
            probe = max(pool, key=lambda p: (gain(p) / cost_of(p), -cost_of(p), p))
            observed[probe] = world.observe(probe, case.cause)
            trace.probe_cost += cost_of(probe)
            trace.probes_bought += 1
        guess = max(CAUSES, key=lambda c: (score(c, observed), CAUSES.index(c)))
        trace.correct.append(guess is case.cause)
        trace.refused.append(False)
        marginal[case.cause] = marginal.get(case.cause, 0) + 1
        for probe, value in observed.items():
            counts.setdefault(probe, {})
            counts[probe][(value, case.cause)] = counts[probe].get((value, case.cause), 0) + 1
    return trace


def given_semantics_ceiling(world: World, stream: Sequence[Case], probes_at, budget: int,
                            rng: random.Random) -> Trace:
    """E2's arm: handed the true table for free, AND the true cause prior.

    The first version of this arm refused whenever more than one cause survived,
    and the learner beat it -- which prediction R4 registered in advance as
    meaning the ceiling is implemented wrongly rather than that a discovery had
    been made. It was: refusing is an honest policy but it is not an upper bound,
    because an arm with strictly more information was scoring lower purely by
    declining to guess. A ceiling has to be given the best decision rule as well
    as the best information, so it now names the most probable survivor under the
    true prior. Its refusal count is still reported, in its own column.
    """
    trace = Trace()
    sem = world.semantics
    prior = {c: CAUSE_PRIOR[c] for c in CAUSES}

    def live(observed: dict[str, bool]) -> list[Cause]:
        return [c for c in CAUSES
                if all(sem.observe(p, c, world.checker_sound) == v
                       for p, v in observed.items())]

    for case in stream:
        available = list(probes_at(len(trace.correct)))
        observed: dict[str, bool] = {}
        for _ in range(budget):
            among = live(observed)
            if len(among) <= 1:
                break
            best, chosen = None, None
            for probe in available:
                if probe in observed:
                    continue
                yes = sum(1 for c in among if sem.observe(probe, c, world.checker_sound))
                elim = min(yes, len(among) - yes)
                key = (elim / cost_of(probe), -cost_of(probe), probe)
                if best is None or key > best:
                    best, chosen = key, probe
            if chosen is None or best[0] <= 0:
                break
            observed[chosen] = world.observe(chosen, case.cause)
            trace.probe_cost += cost_of(chosen)
            trace.probes_bought += 1
        among = live(observed) or list(CAUSES)
        guess = max(among, key=lambda c: (prior[c], -CAUSES.index(c)))
        trace.correct.append(guess is case.cause)
        trace.refused.append(len(among) > 1)
    return trace


ARMS: dict[str, Callable[..., Trace]] = {
    "semantics_learner": semantics_learner,
    "mapping_parent": mapping_parent,
    "naive_bayes_parent": naive_bayes_parent,
    "random_probe_parent": random_probe_parent,
    "fixed_order_parent": fixed_order_parent,
    "given_semantics_ceiling": given_semantics_ceiling,
}

ARM_ROLES: dict[str, str] = {
    "semantics_learner": "MACHINE",
    "mapping_parent": "PARENT",
    "naive_bayes_parent": "PARENT",
    "random_probe_parent": "PARENT_SELECTION_CONTROL",
    "fixed_order_parent": "PARENT_SELECTION_CONTROL",
    "given_semantics_ceiling": "CEILING",
}


def run_arm(arm_id: str, world: World, stream: Sequence[Case], probes_at, budget: int,
            seed: int) -> Trace:
    return ARMS[arm_id](world, stream, probes_at, budget, random.Random(seed))
