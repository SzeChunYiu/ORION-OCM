"""Failure diagnosis under an identical observed signal: paying to find out why.

The prior failure-knowledge pilot (``failure.py``, ``failure_worlds.py``,
``failure_parents.py``) measured what a machine is *entitled to conclude* from a
diagnosed failure, and found that a full-strength truth-maintenance parent ties
the governed store on four of seven worlds.  Its own receipt states the reason
the result is narrow:

    "All four arms are handed a CORRECT diagnosis by the world.  Nothing here
    measures whether a machine can tell an evaluator defect from a genuine
    refutation when both report 'refuted by checker'.  That is the real problem
    and it is not attempted."

This module attempts it.  The gift is withdrawn.  Every case here presents the
identical observed signal --

    the attempt terminated without a certified solution

-- and the cause is one of five, none of which is visible.  A machine that wants
to know which one must *select and pay for probes*, and it must be allowed to
come back and say it still does not know.

**The five causes.**  Named to match the prior module's taxonomy, with
``TRUE_REFUTATION`` in place of ``REFUTED_BY_CHECKER`` because the surface label
"refuted by checker" is precisely what this experiment refuses to take at face
value:

``TRUE_REFUTATION``
    the method is genuinely wrong in this scope; the checker was right
``BUDGET_EXHAUSTED``
    the method is fine; more search would have certified a solution
``EVALUATOR_DEFECT``
    the checker returned a wrong verdict against a method that is correct
``NON_IDENTIFYING_EXPERIMENT``
    the probes actually used could not have discriminated the method even in
    principle, so failing to separate is a fact about the probe set
``ASSUMPTION_VIOLATED``
    a declared precondition of the method did not hold on this task

and a sixth *verdict*, ``CANNOT_IDENTIFY``, which is never a cause a world may
carry and is always a legitimate thing for a policy to say.  Refusing to name a
cause is a first-class outcome.  It is scored as such, in its own columns, and
it is never silently converted into the most likely guess -- that conversion is
the failure mode this module exists to make visible.

**The registered probes.**  Five, each with a declared cost, each returning a
real observation from the world rather than the label:

======================================  ====  ================================
probe                                   cost  what it returns
======================================  ====  ================================
``PRECONDITION_AUDIT``                     1  do the method's declared
                                              preconditions hold on this task
``CHECKER_CONTROL_BATTERY``                2  does the checker still agree with
                                              independently known answers on a
                                              fixed control set for this scope
``SPLIT_TEST``                             3  could the probes actually used
                                              have split the version space
``RERUN_LARGER_BUDGET``                    5  does the attempt certify a
                                              solution with a larger budget
``SECOND_CHECKER``                         7  does an independently built
                                              checker agree with the first on
                                              the disputed position
======================================  ====  ================================

The costs are ordinal and registered before the run.  They are meant to track
what each probe actually takes: an audit is a lookup, the control battery
re-runs an existing checker on a fixed list, the split test enumerates the
version space over the probes already run, a larger-budget rerun is a full
re-solve, and a second checker has to be *built* before it can be run.

**Why the two checker probes are different, which is the whole design.**
``CHECKER_CONTROL_BATTERY`` answers a question about a *scope*: is this checker
sound over this region at all.  ``SECOND_CHECKER`` answers a question about
*this position*: did the first checker get this one wrong.  The first is cheap
and cacheable across tasks; the second is expensive and per-case.  A machine
that has established "checker C is defective on scope S" has learned something
that survives to the next task in S and to no task outside S.  That is the
accumulation coordinate, and it is the only place in this experiment where a
persistent machine could plausibly separate from a stateless decision tree.

**Inference is a table inversion and is shared by every arm.**  The mapping
from a cause to what each probe returns is registered in
:func:`expected_outcome`, and :func:`candidates` inverts it.  Every arm uses the
identical inference step.  What differs between arms is *which probes they buy*
and *what they remember*.  This is deliberate and it caps what the experiment
can claim: nothing here measures whether a machine can learn what a probe means,
only whether it pays for the right ones and reuses what it already established.
Stated here so a reviewer does not have to discover it.

**Parents, with first right of refusal.**  Sequential test selection and
optimal experimental design; decision-theoretic troubleshooting and the
diagnosis trees of Heckerman, Breese and Rommelse; model-based diagnosis with
conflict sets (de Kleer and Williams, Reiter); fault dictionaries and
minimum-expected-cost test ordering from digital test engineering; and, in
practice, the retry-with-a-bigger-budget heuristic that nearly every agent loop
already implements.  None of that is claimed as new.  The greedy selection rule
below is a textbook cost-normalised information heuristic and is expected to be
*matched* by a hand-authored tree on a stationary cause distribution.  If it is,
the honest report is ``PARENT_SUFFICIENT`` and this module says so.

**What would falsify the claim under test.**  If ``decision_tree_parent``
matches the governed policy on diagnosis accuracy *and* on cumulative probe cost
over the registered task sequences, the memory buys nothing, and the terminal is
``PARENT_SUFFICIENT``.  That comparison is computed in ``run_diagnosis.py`` by a
rule written before the numbers existed.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from failure import (
    Assumption,
    FailureCause,
    FailureKnowledge,
    FailureStore,
    Observation,
    ResourceBound,
)
from prereg import Commitment, commit

__all__ = [
    "Cause",
    "TRUE_CAUSES",
    "CAUSE_ORDER",
    "CAUSE_TO_FAILURE_CAUSE",
    "Probe",
    "PROBE_ORDER",
    "PROBE_COST",
    "ALL_PROBES",
    "OBSERVED_SIGNAL",
    "expected_outcome",
    "candidates",
    "CAUSE_PRIOR",
    "PRIOR_CHECKER_SOUND",
    "expected_elimination",
    "probe_score",
    "select_probe",
    "ProbeOutcome",
    "Case",
    "Bench",
    "Diagnosis",
    "CheckerMemory",
    "DiagnosisArm",
    "record_diagnosis",
    "DIAGNOSIS_PLAN",
    "COMMITMENT",
]


# --------------------------------------------------------------------------
# causes and the one verdict that is not a cause
# --------------------------------------------------------------------------


class Cause(enum.Enum):
    """Why the attempt failed.  Never visible; always inferred or refused.

    ``CANNOT_IDENTIFY`` is a member of this enum so that a verdict and a cause
    are the same type and a policy cannot accidentally return something
    unscorable.  It is excluded from :data:`TRUE_CAUSES`, and the worlds are
    forbidden from carrying it as ground truth: "the cause is unknown" is a fact
    about a policy's evidence, never a fact about the world.
    """

    #: the method really is wrong in this scope; the checker was right
    TRUE_REFUTATION = "TRUE_REFUTATION"
    #: the resource bound was spent; more search would have certified a solution
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    #: the checker returned a wrong verdict against a method that is correct
    EVALUATOR_DEFECT = "EVALUATOR_DEFECT"
    #: the probes used could not have discriminated the method even in principle
    NON_IDENTIFYING_EXPERIMENT = "NON_IDENTIFYING_EXPERIMENT"
    #: a declared precondition of the method did not hold on this task
    ASSUMPTION_VIOLATED = "ASSUMPTION_VIOLATED"
    #: verdict only: the evidence bought does not single out a cause
    CANNOT_IDENTIFY = "CANNOT_IDENTIFY"


#: Deterministic iteration order for every table, matrix and receipt.
CAUSE_ORDER: tuple[Cause, ...] = (
    Cause.TRUE_REFUTATION,
    Cause.BUDGET_EXHAUSTED,
    Cause.EVALUATOR_DEFECT,
    Cause.NON_IDENTIFYING_EXPERIMENT,
    Cause.ASSUMPTION_VIOLATED,
)

#: The causes a world may carry.  ``CANNOT_IDENTIFY`` is deliberately absent.
TRUE_CAUSES: frozenset[Cause] = frozenset(CAUSE_ORDER)

#: Bridge to the prior pilot's taxonomy for the downstream half.  ``failure.py``
#: is imported and never modified: this experiment changes how the cause is
#: obtained, not what may follow from it once obtained.
CAUSE_TO_FAILURE_CAUSE: dict[Cause, FailureCause] = {
    Cause.TRUE_REFUTATION: FailureCause.REFUTED_BY_CHECKER,
    Cause.BUDGET_EXHAUSTED: FailureCause.BUDGET_EXHAUSTED,
    Cause.EVALUATOR_DEFECT: FailureCause.EVALUATOR_DEFECT,
    Cause.NON_IDENTIFYING_EXPERIMENT: FailureCause.NON_IDENTIFYING_EXPERIMENT,
    Cause.ASSUMPTION_VIOLATED: FailureCause.ASSUMPTION_VIOLATED,
}


# --------------------------------------------------------------------------
# the registered probe set
# --------------------------------------------------------------------------


class Probe(enum.Enum):
    """The five registered probes.  Frozen before any outcome was computed."""

    #: evaluate the method's declared preconditions against this task
    PRECONDITION_AUDIT = "PRECONDITION_AUDIT"
    #: re-run *this* checker on control positions whose answers are known
    CHECKER_CONTROL_BATTERY = "CHECKER_CONTROL_BATTERY"
    #: could the probes actually used have split the surviving version space
    SPLIT_TEST = "SPLIT_TEST"
    #: re-run the attempt with a larger budget and see whether it certifies
    RERUN_LARGER_BUDGET = "RERUN_LARGER_BUDGET"
    #: build an independent second checker and ask it about the disputed position
    SECOND_CHECKER = "SECOND_CHECKER"


#: Declared order, cheapest first.  Used for tie-breaking and for rendering, and
#: it is *not* the decision tree: the tree is written out separately in
#: ``diagnosis_parents.py`` so that an ordering claim is legible as an ordering
#: claim rather than smuggled in as an enum declaration.
PROBE_ORDER: tuple[Probe, ...] = (
    Probe.PRECONDITION_AUDIT,
    Probe.CHECKER_CONTROL_BATTERY,
    Probe.SPLIT_TEST,
    Probe.RERUN_LARGER_BUDGET,
    Probe.SECOND_CHECKER,
)

#: Registered costs.  Ordinal, counted, and never a wall-clock reading.
PROBE_COST: dict[Probe, int] = {
    Probe.PRECONDITION_AUDIT: 1,
    Probe.CHECKER_CONTROL_BATTERY: 2,
    Probe.SPLIT_TEST: 3,
    Probe.RERUN_LARGER_BUDGET: 5,
    Probe.SECOND_CHECKER: 7,
}

ALL_PROBES: frozenset[Probe] = frozenset(PROBE_ORDER)

#: The single string every case reports.  A world that varied this would be
#: leaking the cause through the surface label, which is the gift this
#: experiment withdraws.  ``diagnosis_worlds`` asserts every case carries it.
OBSERVED_SIGNAL = "attempt terminated without a certified solution"


def expected_outcome(cause: Cause, probe: Probe, checker_sound: bool) -> bool:
    """What ``probe`` returns when the true cause is ``cause``.

    ``checker_sound`` is a property of the ``(checker, scope)`` pair, not of the
    case.  It appears here because exactly one probe --
    ``CHECKER_CONTROL_BATTERY`` -- answers a scope question rather than a case
    question, and that asymmetry is the whole reason a memory can help.

    The table, read as "``True`` means":

    ``PRECONDITION_AUDIT``        the declared preconditions hold
    ``CHECKER_CONTROL_BATTERY``   the checker passed its known-answer controls
    ``SPLIT_TEST``                the probes used could have split the space
    ``RERUN_LARGER_BUDGET``       the larger budget certified a solution
    ``SECOND_CHECKER``            the independent checker agrees with the first

    Note what the table does *not* let a policy do.  A failed control battery
    says the checker is unreliable somewhere in this scope; it does not say this
    particular verdict was wrong.  Only ``SECOND_CHECKER`` settles that, and it
    is the most expensive probe on the list.  The cheap probe narrows suspicion
    and the expensive one convicts, which is how diagnosis actually goes.
    """
    if probe is Probe.PRECONDITION_AUDIT:
        return cause is not Cause.ASSUMPTION_VIOLATED
    if probe is Probe.CHECKER_CONTROL_BATTERY:
        return checker_sound
    if probe is Probe.SPLIT_TEST:
        return cause is not Cause.NON_IDENTIFYING_EXPERIMENT
    if probe is Probe.RERUN_LARGER_BUDGET:
        return cause is Cause.BUDGET_EXHAUSTED
    if probe is Probe.SECOND_CHECKER:
        return cause is not Cause.EVALUATOR_DEFECT
    raise ValueError(f"unregistered probe {probe!r}")


def _soundness_options(known_sound: bool | None) -> tuple[bool, ...]:
    return (known_sound,) if known_sound is not None else (True, False)


def candidates(
    observed: Mapping[Probe, bool], known_sound: bool | None = None
) -> frozenset[Cause]:
    """Every cause consistent with the outcomes bought so far.

    The soundness of the checker in this scope is a latent variable.  When it is
    unknown both values are tried, and a cause survives if *some* value of the
    latent makes every observation come out as seen.  When it is known -- either
    because the control battery was run, or because the policy remembers it from
    an earlier task in the same scope -- the latent is pinned and the candidate
    set is correspondingly smaller for free.  That "for free" is the entire
    mechanism under test.

    ``EVALUATOR_DEFECT`` is inconsistent with a sound checker by construction: a
    checker that passes its controls over this scope has not returned a wrong
    verdict in it.  The worlds enforce the same implication, so this is a shared
    registered fact and not an assumption the policy is making on its own.
    """
    live: set[Cause] = set()
    for cause in CAUSE_ORDER:
        for sound in _soundness_options(known_sound):
            if cause is Cause.EVALUATOR_DEFECT and sound:
                continue
            if all(
                expected_outcome(cause, probe, sound) == value
                for probe, value in observed.items()
            ):
                live.add(cause)
                break
    return frozenset(live)


# --------------------------------------------------------------------------
# the registered prior and the selection rule
# --------------------------------------------------------------------------

#: The registered stationary cause distribution, frozen before the worlds were
#: written and **not** fitted to them.  It is the prior the selection rule uses;
#: the realised distribution over the registered worlds is reported separately
#: in the receipt, and the two are not the same numbers.  A selection rule tuned
#: to the worlds it is scored on would be measuring its author.
CAUSE_PRIOR: dict[Cause, float] = {
    Cause.TRUE_REFUTATION: 8.0,
    Cause.BUDGET_EXHAUSTED: 7.0,
    Cause.EVALUATOR_DEFECT: 6.0,
    Cause.NON_IDENTIFYING_EXPERIMENT: 5.0,
    Cause.ASSUMPTION_VIOLATED: 4.0,
}

#: Registered prior that an unseen ``(checker, scope)`` pair is sound.  Held at
#: one half deliberately: a policy that assumed checkers are usually fine would
#: be encoding the answer to the hardest world in this experiment.
PRIOR_CHECKER_SOUND = 0.5


def _joint(
    live: Iterable[Cause], known_sound: bool | None
) -> list[tuple[Cause, bool, float]]:
    """The ``(cause, soundness, weight)`` support under the registered prior."""
    out: list[tuple[Cause, bool, float]] = []
    live_set = set(live)
    for cause in CAUSE_ORDER:
        if cause not in live_set:
            continue
        for sound in _soundness_options(known_sound):
            if cause is Cause.EVALUATOR_DEFECT and sound:
                continue
            if known_sound is not None:
                weight = CAUSE_PRIOR[cause]
            else:
                weight = CAUSE_PRIOR[cause] * (
                    PRIOR_CHECKER_SOUND if sound else 1.0 - PRIOR_CHECKER_SOUND
                )
            if weight > 0.0:
                out.append((cause, sound, weight))
    return out


def expected_elimination(
    probe: Probe, live: Iterable[Cause], known_sound: bool | None
) -> float:
    """Expected number of candidates ``probe`` removes, under the prior.

    Myopic on purpose.  A full lookahead over the remaining probes *is* the
    optimal decision tree, and hand-authoring that tree is what
    ``decision_tree_parent`` does; computing it inside the governed policy would
    make the two arms the same object and the comparison vacuous.  The governed
    policy therefore uses the standard one-step cost-normalised rule and is
    expected to reproduce the tree's ordering on a stationary distribution.
    """
    live_set = set(live)
    joint = _joint(live_set, known_sound)
    total = sum(w for _, _, w in joint)
    if total <= 0.0:
        return 0.0
    groups: dict[bool, list[tuple[Cause, float]]] = {}
    for cause, sound, weight in joint:
        groups.setdefault(expected_outcome(cause, probe, sound), []).append(
            (cause, weight)
        )
    expected_survivors = 0.0
    for members in groups.values():
        branch_weight = sum(w for _, w in members)
        survivors = len({c for c, _ in members})
        expected_survivors += (branch_weight / total) * survivors
    return len(live_set) - expected_survivors


def probe_score(
    probe: Probe, live: Iterable[Cause], known_sound: bool | None
) -> float:
    """Expected discrimination per unit cost.  Higher is better."""
    return expected_elimination(probe, live, known_sound) / PROBE_COST[probe]


#: Below this, a probe is treated as buying nothing and is never purchased.
#: A policy that bought a probe whose expected discrimination is zero would be
#: spending to confirm what it already knows, which is the specific waste the
#: accumulation half of this experiment is looking for.
ELIMINATION_TOLERANCE = 1e-12


def select_probe(
    live: Iterable[Cause],
    known_sound: bool | None,
    available: Iterable[Probe],
) -> Probe | None:
    """The next probe to buy, or ``None`` when nothing left is worth buying.

    Ties break towards the cheaper probe and then towards the declared order, so
    the rule is a deterministic function of its inputs and the same inputs give
    the same purchase in every run and every arm.
    """
    best: tuple[float, int, int] | None = None
    chosen: Probe | None = None
    for probe in PROBE_ORDER:
        if probe not in set(available):
            continue
        score = probe_score(probe, live, known_sound)
        if score <= ELIMINATION_TOLERANCE:
            continue
        key = (score, -PROBE_COST[probe], -PROBE_ORDER.index(probe))
        if best is None or key > best:
            best = key
            chosen = probe
    return chosen


# --------------------------------------------------------------------------
# what an arm sees, and what it gets back
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ProbeOutcome:
    """One purchased observation: the probe, what it returned, what it cost."""

    probe: Probe
    value: bool
    cost: int
    detail: str = ""

    def as_dict(self) -> dict:
        return {
            "probe": self.probe.name,
            "value": self.value,
            "cost": self.cost,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class Case:
    """The machine-visible situation.  There is no cause field and cannot be.

    Everything here is something a real agent would hold after a failed attempt:
    which method it ran, on what task, in what scope, against which checker,
    under which assumptions, with which declared preconditions, what the checker
    said, and what the attempt spent.  ``observed_signal`` is the same string in
    every case in every world.

    ``available_probes`` is the honest part.  Some situations simply do not
    admit a second independent checker, or a larger budget, and a policy that
    could always buy its way to certainty would not be facing the problem.
    """

    case_id: str
    method: str
    task: str
    scope: str
    checker_id: str
    assumptions: tuple[Assumption, ...]
    declared_preconditions: tuple[str, ...]
    evidence: tuple[Observation, ...]
    resource_bound: ResourceBound
    available_probes: frozenset[Probe]
    probe_budget: int
    observed_signal: str = OBSERVED_SIGNAL

    def __post_init__(self) -> None:
        if self.observed_signal != OBSERVED_SIGNAL:
            raise ValueError(
                "every case must present the identical observed signal; a world "
                "that varies it is leaking the cause through the surface label"
            )
        if not self.evidence:
            raise ValueError("a failed attempt must carry what the checker said")
        if not self.resource_bound.exhausted:
            raise ValueError(
                "an attempt that terminated without a certified solution has by "
                "definition spent its bound; an unexhausted bound would make "
                "BUDGET_EXHAUSTED readable off the record for free"
            )

    @property
    def memory_key(self) -> tuple[str, str]:
        """The pair a scope-keyed checker fact is filed under."""
        return (self.checker_id, self.scope)

    def as_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "method": self.method,
            "task": self.task,
            "scope": self.scope,
            "checker_id": self.checker_id,
            "assumptions": sorted(str(a) for a in self.assumptions),
            "declared_preconditions": list(self.declared_preconditions),
            "available_probes": sorted(p.name for p in self.available_probes),
            "probe_budget": self.probe_budget,
            "observed_signal": self.observed_signal,
        }


class Bench(Protocol):
    """What an arm is handed.  It can buy observations and nothing else.

    The implementation in ``diagnosis_worlds.py`` is constructed from a
    pre-computed outcome vector and does not hold the episode, so there is no
    reference path from an arm to the ground-truth cause even by reflection.
    ``test_diagnosis.py`` asserts both the structural property and the absence
    of the name from every arm's source.
    """

    @property
    def case(self) -> Case: ...

    @property
    def spent(self) -> int: ...

    @property
    def probes_run(self) -> tuple[Probe, ...]: ...

    def run(self, probe: Probe) -> ProbeOutcome: ...


@dataclass(frozen=True)
class Diagnosis:
    """What an arm returns: a verdict, what it bought, and what it reused."""

    verdict: Cause
    probes: tuple[Probe, ...]
    cost: int
    candidates: frozenset[Cause]
    reused: tuple[str, ...] = ()
    note: str = ""

    @property
    def refused(self) -> bool:
        return self.verdict is Cause.CANNOT_IDENTIFY

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict.name,
            "probes": [p.name for p in self.probes],
            "cost": self.cost,
            "candidates": sorted(c.name for c in self.candidates),
            "reused": list(self.reused),
            "note": self.note,
        }


class DiagnosisArm(Protocol):
    """Every arm, governed and parent alike, is this.

    Constructed once per world so that an arm which wants to accumulate can, and
    an arm which does not simply never writes anything down.  Charging the
    stateless arms for state they do not keep, or denying the stateful one the
    chance to keep it, would decide the experiment by construction.
    """

    name: str

    def diagnose(self, bench: Bench) -> Diagnosis: ...


# --------------------------------------------------------------------------
# the accumulation instrument
# --------------------------------------------------------------------------


class CheckerMemory:
    """Scope-keyed beliefs about checker soundness.  The thing being tested.

    Keyed on ``(checker_id, scope)``.  The key is the whole point: a checker
    that mis-tabulates one game family is perfectly sound on another, and a
    memory keyed on the checker alone would carry a true finding into a scope
    where it is false.  ``diagnosis_worlds`` registers exactly that hostile, and
    ``diagnosis_parents`` registers a scope-blind ablation of this class so the
    punishment is demonstrated rather than asserted.

    Two ways a belief is established, and they are asymmetric on purpose:

    * ``CHECKER_CONTROL_BATTERY`` passing establishes **sound**, because the
      control set covers the scope.  Failing establishes **defective**.
    * ``SECOND_CHECKER`` disagreeing establishes **defective**, because a
      disagreement on a position in this scope is a witnessed wrong verdict.
      Agreeing establishes **nothing**: one correct verdict is not soundness.

    That asymmetry is why the cheap probe is the one worth remembering.
    """

    def __init__(self) -> None:
        self._beliefs: dict[tuple[str, str], bool] = {}
        self._reuses = 0

    def belief(self, key: tuple[str, str]) -> bool | None:
        held = self._beliefs.get(key)
        if held is not None:
            self._reuses += 1
        return held

    def learn_sound(self, key: tuple[str, str], sound: bool) -> None:
        self._beliefs[key] = sound

    def witness_defect(self, key: tuple[str, str]) -> None:
        self._beliefs[key] = False

    @property
    def reuses(self) -> int:
        return self._reuses

    @property
    def size(self) -> int:
        return len(self._beliefs)

    def as_dict(self) -> dict:
        return {
            "entries": {f"{c} @ {s}": v for (c, s), v in sorted(self._beliefs.items())},
            "reuses": self._reuses,
        }


class ScopeBlindCheckerMemory(CheckerMemory):
    """The ablation: the same memory with the scope dropped from the key.

    Not a parent and not a policy anyone should ship.  It exists so that the
    over-generalisation hostile has something to punish, and so that "keying on
    the scope matters" is a measured difference rather than a design assertion.
    """

    def belief(self, key: tuple[str, str]) -> bool | None:
        return super().belief((key[0], "*"))

    def learn_sound(self, key: tuple[str, str], sound: bool) -> None:
        super().learn_sound((key[0], "*"), sound)

    def witness_defect(self, key: tuple[str, str]) -> None:
        super().witness_defect((key[0], "*"))


# --------------------------------------------------------------------------
# the downstream half: negative knowledge, built on the prior pilot's store
# --------------------------------------------------------------------------


def record_diagnosis(
    store: FailureStore, case: Case, verdict: Cause
) -> FailureKnowledge | None:
    """Turn a verdict into whatever negative knowledge it licenses, and file it.

    ``failure.py`` is used exactly as it stands and is not modified.  Its
    ``FailureKnowledge.build`` derives the exclusions from the cause, so a wrong
    diagnosis produces wrong negative knowledge *mechanically* rather than
    because this function chose to punish it -- which is what makes the
    downstream columns a consequence of the diagnosis and not of the scoring.

    ``CANNOT_IDENTIFY`` records **nothing**.  ``FailureKnowledge`` has no cause
    meaning "I do not know", and inventing one would be the silent conversion of
    a refusal into a guess.  The attempt is simply not turned into a conclusion,
    which is the correct behaviour and also the honest cost of refusing: the
    machine keeps its repeated work.
    """
    if verdict is Cause.CANNOT_IDENTIFY:
        return None
    knowledge = FailureKnowledge.build(
        attempted_method=case.method,
        task=case.task,
        representation="registered",
        assumptions=case.assumptions,
        evidence=case.evidence,
        resource_bound=case.resource_bound,
        observed_failure=case.observed_signal,
        diagnosed_responsibility=CAUSE_TO_FAILURE_CAUSE[verdict],
        scope=case.scope,
        reopen_conditions=tuple(
            f"{a.name} changes" for a in sorted(set(case.assumptions))
        ),
    )
    store.record(knowledge)
    return knowledge


# --------------------------------------------------------------------------
# the frozen plan
# --------------------------------------------------------------------------

#: Frozen before any outcome.  Editing any value changes the commitment and
#: therefore changes the drawn task sequence, which is what makes analysis drift
#: mechanically visible (CL-D4, ``prereg.py``).
DIAGNOSIS_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "rung": "CL-D2 failure-cause diagnosis under an identical observed signal",
    "observed_signal": OBSERVED_SIGNAL,
    "causes": [c.name for c in CAUSE_ORDER],
    "verdict_only": [Cause.CANNOT_IDENTIFY.name],
    "probes": {p.name: PROBE_COST[p] for p in PROBE_ORDER},
    "registered_cause_prior": {c.name: CAUSE_PRIOR[c] for c in CAUSE_ORDER},
    "registered_prior_checker_sound": PRIOR_CHECKER_SOUND,
    "selection_rule": "greedy expected candidate elimination per unit probe cost",
    "arms": [
        "governed_diagnosis",
        "assume_refutation_parent",
        "retry_once_parent",
        "exhaustive_probe_parent",
        "decision_tree_parent",
        "scope_blind_cache_ablation",
    ],
    "endpoints": [
        "diagnosis accuracy per cause",
        "confusion matrix over targets and verdicts",
        "probe cost per diagnosis",
        "cumulative probe cost over the task sequence",
        "correct CANNOT_IDENTIFY rate",
        "downstream false exclusions and missed reopenings",
        "over-generalisation count on the hostile",
    ],
    "sequence_length": 20,
    "terminal_rule": (
        "PARENT_SUFFICIENT if decision_tree_parent matches governed_diagnosis on "
        "accuracy and does not exceed it on cumulative probe cost"
    ),
}

COMMITMENT: Commitment = commit(DIAGNOSIS_PLAN)
