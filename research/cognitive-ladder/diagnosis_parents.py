"""The six arms: one treatment, four parents, one ablation of the treatment.

A diagnosis policy scored only against worlds its own author wrote proves
nothing.  These arms exist so that the numbers in ``diagnosis_worlds.py`` are a
comparison rather than a demonstration.  Every arm is handed the identical
episode stream, the identical probes at the identical registered prices, the
identical per-case probe budget, and the identical unmodified
``failure.FailureStore`` to file its conclusions in.  None is weakened to make
the governed policy look better.

Every arm also shares the *inference* step -- ``diagnosis.candidates``, which
inverts the registered response table.  That is deliberate.  If the arms
differed in how they read a probe's answer, the comparison would be measuring
two things at once.  They differ only in **which probes they buy** and **what
they carry between episodes**, which are the two variables this experiment is
about.

``assume_refutation_parent``
    The cause-blind nogood policy from the prior pilot, ported.  It never
    probes: a failure is a refutation, a refutation excludes, and the machine
    moves on.  Its accuracy is exactly the constant-predictor baseline, which is
    the useful thing about it -- reporting the baseline separately and then
    running an arm that *is* the baseline means the reader can see immediately
    how much of any arm's accuracy is structure and how much is the base rate.
    Its cost column is zero, and any scoring rule that likes zero cost without
    reading the downstream columns would rank it first.

``retry_once_parent``
    The commonest heuristic in real agent loops: retry with a larger budget,
    and if it still fails, call it a refutation.  It buys exactly one probe.
    It is not a strawman -- on the causes it can see it is exactly right, and it
    genuinely solves the budget-versus-refutation confusion that the escalation
    module treats as the single most important hostile.  What it cannot do is
    ever say ``CANNOT_IDENTIFY``, because its decision procedure has no branch
    for not knowing, and that is a structural property of the heuristic rather
    than an incidental weakness of this implementation.

``exhaustive_probe_parent``
    Buys every available probe on every episode, then infers.  This is the
    accuracy ceiling by construction: no arm can end an episode with a smaller
    candidate set than the one the full outcome vector implies.  It is also the
    honest strongest parent, and if the governed policy cannot beat it on cost
    at equal accuracy then the governed policy has no reason to exist.  Its cost
    is 18 units per episode, every episode, forever.

``decision_tree_parent``
    A fixed, hand-authored probe ordering -- audit, split, rerun, controls,
    second checker -- with early exit when the candidate set collapses and a
    skip when the next probe cannot discriminate.  **This is the strongest
    realistic parent.**  On a stationary cause distribution a fixed ordering is
    sufficient: it is what the whole test-ordering literature says, and the
    governed policy's greedy rule reproduces this exact ordering, which
    ``test_diagnosis.py`` asserts rather than hopes.  Saying so plainly is the
    result, not a caveat.  It is stateless, and it is the arm the treatment has
    to beat on cumulative cost or else report ``PARENT_SUFFICIENT``.

``governed_diagnosis``
    The treatment.  Selects probes greedily by expected candidate elimination
    per unit cost, refuses when nothing left to buy can separate the survivors,
    and carries one thing between episodes: a scope-keyed belief about whether a
    checker is sound.  That memory is the only difference from the decision tree
    and therefore the only thing the experiment can attribute a difference to.

``scope_blind_cache_ablation``
    Not a parent.  The governed policy with two coupled shortcuts: its memory
    key drops the scope, and a remembered defect is promoted from "an evaluator
    defect is possible here" to "this is another one".  Together those are what
    over-generalising a defect actually looks like in a real system, and the
    ``DW3`` hostile is built to punish it.  It is included so that "keying on
    the scope matters" is a measured difference rather than a design assertion.

What would falsify the claim under test: if ``decision_tree_parent`` matches the
governed policy on accuracy and on cumulative probe cost, the memory buys
nothing and the terminal is ``PARENT_SUFFICIENT``.  :func:`sufficiency_report`
computes that comparison rather than assuming its answer.
"""

from __future__ import annotations

from typing import Callable, Sequence

from diagnosis import (
    Bench,
    Cause,
    CheckerMemory,
    Diagnosis,
    Probe,
    PROBE_COST,
    ScopeBlindCheckerMemory,
    candidates,
    expected_elimination,
    select_probe,
)
from diagnosis_worlds import WORLDS, DiagnosisWorld, Score, run, scoreboard

__all__ = [
    "GovernedDiagnosis",
    "AssumeRefutationParent",
    "RetryOnceParent",
    "ExhaustiveProbeParent",
    "DecisionTreeParent",
    "ScopeBlindCacheAblation",
    "FIXED_TREE_ORDER",
    "ARMS",
    "PARENTS",
    "sufficiency_report",
    "table",
]


def _settle(live: frozenset[Cause]) -> Cause:
    """The verdict a candidate set licenses.

    One survivor is a diagnosis.  Anything else is ``CANNOT_IDENTIFY``, and that
    includes the empty set: a contradictory outcome vector means the registered
    response table does not describe what just happened, which is a reason to
    say nothing rather than to pick the least bad label.
    """
    return next(iter(live)) if len(live) == 1 else Cause.CANNOT_IDENTIFY


class GovernedDiagnosis:
    """The treatment: greedy probe purchase plus a scope-keyed checker memory.

    The loop is small and every line of it is a commitment:

    1. Look up what is already known about ``(checker, scope)``.  A hit costs
       nothing and shrinks the candidate set before a single probe is bought.
    2. While more than one cause survives, buy the probe with the best expected
       elimination per unit cost, and stop when nothing left on offer can
       separate the survivors.
    3. Write back what was learned about the scope, and only what was learned
       about the scope: a passed control battery establishes soundness, a failed
       one or a disagreeing second checker establishes a defect, and a second
       checker that *agrees* establishes nothing -- one correct verdict is not
       soundness.
    4. Return the survivor, or refuse.

    Step 3's asymmetry is the reason the memory is worth anything and also the
    reason it is safe: it only ever records a fact about the scope it was
    witnessed in.
    """

    name = "governed_diagnosis"

    def __init__(self) -> None:
        self.memory = CheckerMemory()

    def diagnose(self, bench: Bench) -> Diagnosis:
        case = bench.case
        key = case.memory_key
        known = self.memory.belief(key)
        reused: tuple[str, ...] = ()
        if known is not None:
            reused = (
                f"{case.checker_id} is "
                f"{'sound' if known else 'defective'} on {case.scope}",
            )
        observed: dict[Probe, bool] = {}
        while True:
            live = candidates(observed, known)
            if len(live) <= 1:
                break
            probe = select_probe(
                live, known, set(case.available_probes) - set(observed)
            )
            if probe is None:
                break
            outcome = bench.run(probe)
            observed[probe] = outcome.value
            if probe is Probe.CHECKER_CONTROL_BATTERY:
                self.memory.learn_sound(key, outcome.value)
                known = outcome.value
            elif probe is Probe.SECOND_CHECKER and not outcome.value:
                self.memory.witness_defect(key)
                known = False
        live = candidates(observed, known)
        return Diagnosis(
            verdict=_settle(live),
            probes=bench.probes_run,
            cost=bench.spent,
            candidates=live,
            reused=reused,
            note="greedy expected elimination per unit cost, scope-keyed memory",
        )


class AssumeRefutationParent:
    """Never probe.  A failure is a refutation.  The prior pilot's cause-blind arm.

    Ported unchanged in spirit from ``failure_parents.NogoodPolicy``: a conflict
    is a conflict and a truth-maintenance system has no notion of a conflict that
    carries no information.  Given the identical observed signal and no probe,
    the only cause it can name is the one that reads straight off the label.
    """

    name = "assume_refutation_parent"

    def diagnose(self, bench: Bench) -> Diagnosis:
        return Diagnosis(
            verdict=Cause.TRUE_REFUTATION,
            probes=(),
            cost=0,
            candidates=frozenset({Cause.TRUE_REFUTATION}),
            note="the label says refuted by checker, so the cause is a refutation",
        )


class RetryOnceParent:
    """Retry with a larger budget; if it still fails, call it a refutation.

    The commonest real heuristic.  It resolves exactly one of the four
    confusions -- budget against refutation -- and collapses the other three
    onto ``TRUE_REFUTATION``.  It has no branch for not knowing, so it never
    refuses, and it therefore scores zero in the ``correct_cannot_identify``
    column by construction rather than by bad luck.
    """

    name = "retry_once_parent"

    def diagnose(self, bench: Bench) -> Diagnosis:
        case = bench.case
        observed: dict[Probe, bool] = {}
        if Probe.RERUN_LARGER_BUDGET in case.available_probes:
            outcome = bench.run(Probe.RERUN_LARGER_BUDGET)
            observed[Probe.RERUN_LARGER_BUDGET] = outcome.value
            if outcome.value:
                return Diagnosis(
                    verdict=Cause.BUDGET_EXHAUSTED,
                    probes=bench.probes_run,
                    cost=bench.spent,
                    candidates=frozenset({Cause.BUDGET_EXHAUSTED}),
                    note="the larger budget certified a solution",
                )
        return Diagnosis(
            verdict=Cause.TRUE_REFUTATION,
            probes=bench.probes_run,
            cost=bench.spent,
            candidates=candidates(observed, None),
            note="more search did not help, so the method must be wrong",
        )


#: The hand-authored ordering.  Written out here rather than derived, because an
#: ordering claim should be legible as an ordering claim.  Cheapest-first is not
#: the rule: ``SPLIT_TEST`` costs three and precedes ``CHECKER_CONTROL_BATTERY``
#: at two, because the split test resolves a cause outright while the control
#: battery only narrows the field.
FIXED_TREE_ORDER: tuple[Probe, ...] = (
    Probe.PRECONDITION_AUDIT,
    Probe.SPLIT_TEST,
    Probe.RERUN_LARGER_BUDGET,
    Probe.CHECKER_CONTROL_BATTERY,
    Probe.SECOND_CHECKER,
)


class DecisionTreeParent:
    """A fixed, hand-authored, optimal-ish probe ordering.  Stateless.

    The strongest realistic parent.  It walks :data:`FIXED_TREE_ORDER`, skipping
    probes that are unavailable or that cannot discriminate among the survivors,
    and exiting as soon as one cause remains.  It is expected to be *sufficient*
    on a stationary cause distribution, and the governed policy's greedy rule is
    expected to reproduce exactly this ordering; ``test_diagnosis.py`` asserts
    the reproduction on the stationary world instead of leaving it as a claim.

    It carries nothing between episodes.  That is the single variable separating
    it from the treatment, which is the point of building it this way.
    """

    name = "decision_tree_parent"

    def diagnose(self, bench: Bench) -> Diagnosis:
        case = bench.case
        observed: dict[Probe, bool] = {}
        for probe in FIXED_TREE_ORDER:
            live = candidates(observed, None)
            if len(live) <= 1:
                break
            if probe not in case.available_probes:
                continue
            if expected_elimination(probe, live, None) <= 0.0:
                continue
            observed[probe] = bench.run(probe).value
        live = candidates(observed, None)
        return Diagnosis(
            verdict=_settle(live),
            probes=bench.probes_run,
            cost=bench.spent,
            candidates=live,
            note="fixed hand-authored ordering, no state between episodes",
        )


class ExhaustiveProbeParent:
    """Buy everything on offer, every time.  The accuracy ceiling and the cost ceiling.

    No arm can end an episode knowing more than this one does, because no arm
    can observe more than every available probe.  Its accuracy is therefore an
    upper bound on every other arm's, and its cost is an upper bound too: the
    full set costs eighteen units and it pays that on every episode of its life.
    """

    name = "exhaustive_probe_parent"

    def diagnose(self, bench: Bench) -> Diagnosis:
        case = bench.case
        observed: dict[Probe, bool] = {}
        for probe in FIXED_TREE_ORDER:
            if probe in case.available_probes:
                observed[probe] = bench.run(probe).value
        live = candidates(observed, None)
        return Diagnosis(
            verdict=_settle(live),
            probes=bench.probes_run,
            cost=bench.spent,
            candidates=live,
            note="every available probe, every episode",
        )


class ScopeBlindCacheAblation:
    """The over-generalising ablation.  Not a parent; not a policy to ship.

    Two coupled shortcuts, which is what over-generalisation actually is:

    * the memory key drops the scope, so a defect witnessed on ``SUB(1,2,3)``
      is believed on ``SUB(1,2)`` where the same checker is exactly right;
    * a remembered defect is promoted from "an evaluator defect is possible
      here" to "this is another one", so the expensive second checker is never
      bought again.

    Each shortcut is individually tempting and locally cheap.  Together they
    answer ``EVALUATOR_DEFECT`` against methods that were genuinely refuted, and
    ``DW3`` counts every such answer.
    """

    name = "scope_blind_cache_ablation"

    def __init__(self) -> None:
        self.memory = ScopeBlindCheckerMemory()

    def diagnose(self, bench: Bench) -> Diagnosis:
        case = bench.case
        key = case.memory_key
        known = self.memory.belief(key)
        reused: tuple[str, ...] = ()
        if known is not None:
            reused = (f"{case.checker_id} is {'sound' if known else 'defective'}",)
        observed: dict[Probe, bool] = {}
        while True:
            live = candidates(observed, known)
            if known is False and live == frozenset(
                {Cause.TRUE_REFUTATION, Cause.EVALUATOR_DEFECT}
            ):
                return Diagnosis(
                    verdict=Cause.EVALUATOR_DEFECT,
                    probes=bench.probes_run,
                    cost=bench.spent,
                    candidates=live,
                    reused=reused,
                    note="this checker is known broken, so this is another one",
                )
            if len(live) <= 1:
                break
            probe = select_probe(
                live, known, set(case.available_probes) - set(observed)
            )
            if probe is None:
                break
            outcome = bench.run(probe)
            observed[probe] = outcome.value
            if probe is Probe.CHECKER_CONTROL_BATTERY:
                self.memory.learn_sound(key, outcome.value)
                known = outcome.value
            elif probe is Probe.SECOND_CHECKER and not outcome.value:
                self.memory.witness_defect(key)
                known = False
        live = candidates(observed, known)
        return Diagnosis(
            verdict=_settle(live),
            probes=bench.probes_run,
            cost=bench.spent,
            candidates=live,
            reused=reused,
            note="scope-blind memory",
        )


#: Every arm, governed first.  Constructed fresh per world by the runner, so a
#: memory accumulates within a task sequence and never across unrelated ones.
ARMS: dict[str, Callable[[], object]] = {
    "governed_diagnosis": GovernedDiagnosis,
    "assume_refutation_parent": AssumeRefutationParent,
    "retry_once_parent": RetryOnceParent,
    "exhaustive_probe_parent": ExhaustiveProbeParent,
    "decision_tree_parent": DecisionTreeParent,
    "scope_blind_cache_ablation": ScopeBlindCacheAblation,
}

#: The parents alone.  The ablation is excluded: it is a weakened copy of the
#: treatment, and calling it a parent would let the treatment beat itself.
PARENTS: dict[str, Callable[[], object]] = {
    name: factory
    for name, factory in ARMS.items()
    if name not in ("governed_diagnosis", "scope_blind_cache_ablation")
}


def _score_matrix(
    worlds: Sequence[DiagnosisWorld] = WORLDS,
) -> dict[str, dict[str, Score]]:
    return {
        name: {world.world_id: run(world, factory) for world in worlds}
        for name, factory in ARMS.items()
    }


def _row(score: Score) -> tuple:
    """The comparable row: accuracy, cost and every error column."""
    return (
        score.correct,
        score.probe_cost,
        score.correct_cannot_identify,
        score.missed_cannot_identify,
        score.false_cannot_identify,
        score.over_generalisations,
        score.false_exclusions,
        score.missed_reopenings,
        score.wasted_work_avoided,
        score.repeated_wasted_work,
    )


def sufficiency_report(worlds: Sequence[DiagnosisWorld] = WORLDS) -> dict:
    """Which parents tie or beat the governed policy, and where.

    A parent is ``PARENT_SUFFICIENT`` when it is at least as accurate on every
    world and never spends more in total.  A parent that ties on some worlds has
    those world ids listed, because a residual confined to the worlds with
    repeated scopes is a much weaker result than a residual everywhere, and the
    report should say which one is being claimed.
    """
    matrix = _score_matrix(worlds)
    governed = matrix["governed_diagnosis"]
    report: dict[str, dict] = {}
    for name in PARENTS:
        rows = matrix[name]
        tied = tuple(
            world.world_id
            for world in worlds
            if _row(rows[world.world_id]) == _row(governed[world.world_id])
        )
        at_least_as_accurate = all(
            rows[w.world_id].correct >= governed[w.world_id].correct for w in worlds
        )
        no_more_costly = sum(rows[w.world_id].probe_cost for w in worlds) <= sum(
            governed[w.world_id].probe_cost for w in worlds
        )
        if at_least_as_accurate and no_more_costly:
            verdict = "PARENT_SUFFICIENT"
        elif at_least_as_accurate:
            verdict = "EQUALLY_ACCURATE_MORE_EXPENSIVE"
        else:
            verdict = "LESS_ACCURATE"
        report[name] = {
            "tied_worlds": tied,
            "discriminated_worlds": tuple(
                w.world_id for w in worlds if w.world_id not in tied
            ),
            "accuracy": sum(rows[w.world_id].correct for w in worlds),
            "probe_cost": sum(rows[w.world_id].probe_cost for w in worlds),
            "verdict": verdict,
        }
    return report


def table(worlds: Sequence[DiagnosisWorld] = WORLDS) -> str:
    """The scoring table, rendered.  Columns side by side, never combined."""
    rows = scoreboard(ARMS, worlds)
    episodes = sum(len(w.episodes) for w in worlds)
    header = (
        f"{'arm':<28}{'correct':>9}{'acc':>7}{'cost':>7}{'probes':>8}"
        f"{'ok-refuse':>11}{'guessed':>9}{'over-gen':>10}{'false-excl':>12}"
    )
    lines = [
        f"diagnosis worlds: {len(worlds)}   episodes: {episodes}   "
        f"probe set cost: {sum(PROBE_COST.values())} units",
        header,
        "-" * len(header),
    ]
    for name in ARMS:
        s = rows[name]
        lines.append(
            f"{name:<28}{s.correct:>9}{s.accuracy:>7.3f}{s.probe_cost:>7}"
            f"{s.probes_bought:>8}{s.correct_cannot_identify:>11}"
            f"{s.missed_cannot_identify:>9}{s.over_generalisations:>10}"
            f"{s.false_exclusions:>12}"
        )
    lines.append("")
    for name, verdict in sufficiency_report(worlds).items():
        lines.append(
            f"{name:<28}{verdict['verdict']:<32}tied on: "
            + (", ".join(verdict["tied_worlds"]) or "nothing")
        )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(table())
