"""Strongest faithful failure-memory policies: first right of refusal.

A failure-memory policy scored only against worlds its own author designed
proves nothing.  These parents exist so that the numbers in
``failure_worlds.py`` are a *comparison* rather than a demonstration.  Each is a
faithful rendering of a policy that is actually used, each is given the identical
event stream with the identical diagnoses attached, and none is weakened to make
the governed policy look better.

``no_memory_parent``
    Forget every failure.  The null policy, and the honest baseline: it cannot
    make a false exclusion, cannot miss a reopening and cannot be broken shut.
    Its entire cost sits in one column -- repeated wasted work -- and any
    scoring rule that ranks it well is the wrong scoring rule.  It is included
    precisely because it makes that failure of scalar scoring visible.

``transcript_parent``
    Keep the raw transcript of every failed attempt and refuse to retry a
    ``(method, task)`` pair that appears in it.  This is the task-ID blacklist
    named in protocol attack A10, and it is what most agent loops actually do:
    the task identity is the handle that is lying around, so it becomes the key.
    It is not a strawman -- within a fixed regime it genuinely stops the machine
    from grinding the same wall twice -- and it is given exactly the same three
    arguments as every other policy, including the assumption context, which it
    chooses not to use.  Its two failure modes are structural rather than
    incidental: a refutation does not transfer to an unseen task in the same
    regime, and a stale refutation does transfer to the same task after the
    rules change.  The protocol has to beat this, and the second failure mode is
    what "broken shut" means.

``nogood_parent``
    Record a nogood on every failure, keyed on the assumption set in force, and
    retract it by dependency-directed backtracking when an assumption it rests
    on changes.  This is an ATMS nogood store, and it is deliberately given the
    *full* strength of one: correct assumption-set keying and correct
    retraction, not a caricature.  That leaves exactly one difference from the
    governed policy -- it excludes on any failure, without asking what caused
    it -- so the comparison isolates the cause filter and nothing else.

    **This parent is PARENT_SUFFICIENT on FW1, FW2, FW4 and FW7.**  On those
    four worlds it produces byte-identical scores to the governed store, and
    saying so is not a caveat but the result: assumption-keyed exclusion with
    retraction is old, well understood, and already does everything the governed
    policy does on any world where every failure is a genuine refutation.  The
    governed policy's whole contribution is confined to the three worlds where a
    failure has a cause that carries no information about correctness (FW3, FW5,
    FW6).  If a future draw contained no such world, the correct report for the
    whole rung would be ``PARENT_SUFFICIENT`` and the governed machinery would be
    unjustified overhead.

``governed_policy``
    The policy under test: :class:`failure.FailureStore` behind the same
    interface.  It is a nogood store plus a cause filter, and it is described
    that way rather than as something new.

What would falsify the claim under test: if ``nogood_parent`` matched the
governed store on the cause-discriminating worlds as well -- or if the governed
store bought its zero false-exclusion count by giving up work saving relative to
the nogood parent -- the cause filter would be paying for itself with something,
and the residual would be nothing.  :func:`sufficiency_report` computes that
comparison rather than assuming its answer, and it reports
``PARENT_SUFFICIENT`` when a parent ties on every registered world.

Limitation, stated plainly: all four policies are handed a correct diagnosis by
the world.  Nothing here measures whether a machine can produce one.  In the
registered worlds the cause is true by construction; a policy that had to infer
"the checker is defective" from the same transcript that says "refuted by
checker" faces a harder problem than any of these arms solve, and this module
does not speak to it.
"""

from __future__ import annotations

from typing import Callable, Sequence

from failure import Assumption, FailureKnowledge, FailureStore, assumption_set
from failure_worlds import WORLDS, FailureWorld, Score, run

__all__ = [
    "GovernedPolicy",
    "NoMemoryPolicy",
    "TranscriptPolicy",
    "NogoodPolicy",
    "POLICIES",
    "PARENTS",
    "sufficiency_report",
    "table",
]


class GovernedPolicy:
    """The policy under test: cause-filtered, assumption-keyed, reopenable."""

    name = "governed"

    def __init__(self) -> None:
        self.store = FailureStore()

    def record(self, knowledge: FailureKnowledge) -> None:
        self.store.record(knowledge)

    def blocked(
        self, method: str, assumptions: Sequence[Assumption], task: str
    ) -> bool:
        # ``task`` is accepted and discarded.  The governed key cannot express a
        # task identity, which is the property attack A10 is testing for.
        return self.store.excluded(method, assumptions)

    def regime_change(self, changed: str) -> set[str]:
        return {e.method for e in self.store.reopen(changed)}


class NoMemoryPolicy:
    """Never remember a failure.  Safe, and pays for it on every repeat."""

    name = "no_memory"

    def __init__(self) -> None:
        self.seen: list[FailureKnowledge] = []

    def record(self, knowledge: FailureKnowledge) -> None:
        # The record is kept so the arm is not cheaper to *run* than the others;
        # it is simply never consulted.  Charging this arm less infrastructure
        # than the rest would confound the comparison in its favour.
        self.seen.append(knowledge)

    def blocked(
        self, method: str, assumptions: Sequence[Assumption], task: str
    ) -> bool:
        return False

    def regime_change(self, changed: str) -> set[str]:
        return set()


class TranscriptPolicy:
    """Raw transcripts, matched by task identity: the A10 blacklist.

    Excludes on any failure of any cause, keyed on ``(method, task)``, and has
    no reopening mechanism at all -- there is nothing in a transcript that says
    when a past failure stopped applying, which is exactly why this shape of
    memory becomes monotonically more restrictive over a long lifetime.
    """

    name = "transcript"

    def __init__(self) -> None:
        self.transcripts: list[FailureKnowledge] = []
        self._failed: set[tuple[str, str]] = set()

    def record(self, knowledge: FailureKnowledge) -> None:
        self.transcripts.append(knowledge)
        self._failed.add((knowledge.attempted_method, knowledge.task))

    def blocked(
        self, method: str, assumptions: Sequence[Assumption], task: str
    ) -> bool:
        return (method, task) in self._failed

    def regime_change(self, changed: str) -> set[str]:
        # A transcript records what happened, not what it depended on, so there
        # is no principled way to decide which entries a rule change invalidates.
        # Retracting nothing is the faithful behaviour, and it is the source of
        # this parent's broken-shut count.
        return set()


class NogoodPolicy:
    """ATMS-style nogoods with dependency-directed retraction, cause-blind.

    Given the full strength of the technique: the nogood is keyed on the
    assumption set that was in force, and changing any assumption the nogood
    rests on retracts it.  The single departure from the governed store is that
    a nogood is recorded for *every* failure, because a conflict is a conflict
    and a truth-maintenance system has no notion of a conflict that carries no
    information.
    """

    name = "nogood"

    def __init__(self) -> None:
        self._nogoods: dict[tuple[str, frozenset[Assumption]], str] = {}

    def record(self, knowledge: FailureKnowledge) -> None:
        key = (knowledge.attempted_method, assumption_set(knowledge.assumptions))
        self._nogoods[key] = knowledge.diagnosed_responsibility.name

    def blocked(
        self, method: str, assumptions: Sequence[Assumption], task: str
    ) -> bool:
        return (method, assumption_set(assumptions)) in self._nogoods

    def regime_change(self, changed: str) -> set[str]:
        fired = {
            key
            for key in self._nogoods
            if any(a.name == changed for a in key[1])
        }
        for key in fired:
            del self._nogoods[key]
        return {method for method, _ in fired}


#: Every arm, governed first.  Constructed fresh per world by the runner.
POLICIES: dict[str, Callable[[], object]] = {
    "governed": GovernedPolicy,
    "no_memory": NoMemoryPolicy,
    "transcript": TranscriptPolicy,
    "nogood": NogoodPolicy,
}

#: The parents alone, for the comparison that decides whether the governed
#: policy has a residual at all.
PARENTS: dict[str, Callable[[], object]] = {
    name: factory for name, factory in POLICIES.items() if name != "governed"
}


def _score_matrix(
    worlds: Sequence[FailureWorld] = WORLDS,
) -> dict[str, dict[str, Score]]:
    return {
        name: {world.world_id: run(world, factory) for world in worlds}
        for name, factory in POLICIES.items()
    }


def sufficiency_report(worlds: Sequence[FailureWorld] = WORLDS) -> dict:
    """Which parents tie the governed policy, and where.

    A parent that ties on every registered world is reported
    ``PARENT_SUFFICIENT``, full stop: the governed machinery would then be
    explaining nothing that the parent does not already explain.  A parent that
    ties on some worlds has those world ids listed, because a residual confined
    to three of seven worlds is a much weaker result than a residual everywhere
    and the report should say which one is being claimed.

    Ties are computed on the whole score row -- work saved and all three error
    columns -- so a parent cannot be called "discriminated" on the strength of a
    column nobody cares about.
    """
    matrix = _score_matrix(worlds)
    governed = matrix["governed"]
    report: dict[str, dict] = {}
    for name in PARENTS:
        rows = matrix[name]
        tied = tuple(
            world.world_id
            for world in worlds
            if _row(rows[world.world_id]) == _row(governed[world.world_id])
        )
        report[name] = {
            "tied_worlds": tied,
            "discriminated_worlds": tuple(
                w.world_id for w in worlds if w.world_id not in tied
            ),
            "verdict": "PARENT_SUFFICIENT" if len(tied) == len(worlds) else "DISCRIMINATED",
        }
    return report


def _row(score: Score) -> tuple[int, int, int, int, int]:
    return (
        score.wasted_work_avoided,
        score.repeated_wasted_work,
        score.false_exclusions,
        score.missed_reopenings,
        score.broken_shut,
    )


def table(worlds: Sequence[FailureWorld] = WORLDS) -> str:
    """The scoring table, rendered.  Aggregate row per policy, no scalar score.

    Printed by ``python -m failure_parents`` and reproduced in the report.  The
    five columns are shown side by side and are never combined, for the reason
    given in :class:`failure_worlds.Score`.
    """
    from failure_worlds import scoreboard

    rows = scoreboard(POLICIES, worlds)
    available = sum(w.available_work_saving for w in worlds)
    header = (
        f"{'policy':<12}{'work avoided':>14}{'work repeated':>15}"
        f"{'false excl':>12}{'missed reopen':>15}{'broken shut':>13}"
    )
    lines = [
        f"failure worlds: {len(worlds)}   avoidable work: {available} counted units",
        header,
        "-" * len(header),
    ]
    for name in POLICIES:
        s = rows[name]
        lines.append(
            f"{name:<12}{s.wasted_work_avoided:>14}{s.repeated_wasted_work:>15}"
            f"{s.false_exclusions:>12}{s.missed_reopenings:>15}{s.broken_shut:>13}"
        )
    lines.append("")
    for name, verdict in sufficiency_report(worlds).items():
        lines.append(
            f"{name:<12}{verdict['verdict']}  tied on: "
            + (", ".join(verdict["tied_worlds"]) or "nothing")
        )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(table())
