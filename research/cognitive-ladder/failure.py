"""Scoped failure knowledge: what a machine is entitled to conclude from a loss.

A machine that remembers nothing about its failures repeats them.  A machine
that remembers them badly stops trying things that would have worked.  Between
those two failure modes there is a narrow, *disciplined* thing to remember, and
this module implements exactly it.

The object under test is the inference

    "attempt A failed"  ==>  "method M is excluded from consideration"

which is almost always invalid.  The protocol's ``FailureAttemptV1`` (CL-R4)
records that a strategy failed **at a scope under a budget** and is explicitly
never promoted to impossibility.  Making that discipline mechanical requires two
separable commitments, and both are enforced here rather than asserted:

**1. Only some causes of failure carry information about correctness.**

``REFUTED_BY_CHECKER``
    An independent exact procedure exhibited a position where the method's
    verdict and the truth differ.  This is a positive witness: it is a fact
    about the method, not about the attempt, and it licenses an exclusion.

``ASSUMPTION_VIOLATED``
    A declared precondition of the method did not hold.  The method is excluded
    *in the assumption context where the precondition fails* and nowhere else.

``BUDGET_EXHAUSTED``
    The attempt stopped because the resource bound was spent.  This carries
    **no information at all** about whether the method is correct.  "I tried
    hard and failed" is the commonest and most seductive false exclusion
    witness, and it is refused here for the same reason ``escalation.py``
    refuses it as a Jump witness.

``NON_IDENTIFYING_EXPERIMENT``
    The probes actually run could not have discriminated the method from its
    rivals even in principle.  A failure to separate hypotheses on a probe set
    where they provably agree is a fact about the probe set.  ``methods.py``
    registers a concrete instance: every combiner in
    ``XOR_LOOKALIKES_ON_BINARY_VALUES`` agrees with ``XOR`` whenever every
    per-heap Grundy value lies in ``{0, 1}``, so no draw confined to such
    positions can refute any of them.

``EVALUATOR_DEFECT``
    The checker itself was wrong.  Excluding a method on a defective checker's
    say-so is how a correct method is lost permanently, and the surface label
    ("refuted by checker") is identical to the licit case.  The cause, not the
    label, decides.

**2. An exclusion is keyed on the pair (method, assumption-set), never on a
task identity.**

Attack A10 of the protocol is precisely *"failure memory is a task-ID
blacklist"*, and its registered control is the scope-recovery family: the same
task with changed rules must be re-attempted and must succeed.  A task-keyed
memory fails that control twice over -- it does not transfer a genuine
refutation to a fresh task in the same regime, and it does transfer a stale
refutation to the same task in a changed regime.  Keying on
``(method, assumptions)`` is what makes both directions come out right, and it
is why :meth:`FailureStore.excluded` never receives a task argument.

Key comparison is **exact set equality**, not containment.  A refutation
obtained under assumption set ``A`` is not evidence about the same method under
``A ∪ {c}``: adding an assumption can change what the method is being asked to
do.  This is deliberately conservative and it costs real transfer -- an
exclusion does not generalise to a strictly richer context and must be re-earned
there -- but the alternative direction manufactures false exclusions, which is
the expensive error.  This is a limitation of the implementation, stated so a
reviewer can price it.

**Reopening.**  Every exclusion carries non-empty ``reopen_conditions``; the
store refuses to create one without them.  An exclusion that cannot be reopened
is a one-way door, and a lifetime learner that accumulates one-way doors becomes
monotonically less capable no matter how correct each individual door was.
:meth:`FailureStore.reopen` fires on the *name* of an assumption an exclusion
depends on: when that assumption changes value, the exclusion's warrant is gone
and the exclusion is retired rather than downgraded.  A retired exclusion must
be re-earned by a fresh refutation, which is stricter than keeping it and
cheaper than never having it.

Parents, with first right of refusal.  Truth-maintenance systems and their
nogoods (Doyle; de Kleer's ATMS), dependency-directed backtracking (Stallman and
Sussman), conflict-driven clause learning in modern SAT solvers, and the
task-keyed failure lists that appear in practically every agent loop.  The
assumption-keyed store below **is** an ATMS nogood store with retraction; none
of that machinery is claimed as new.  The single variable this module adds is
the cause filter: a nogood store records a nogood on any conflict, whereas this
one records nothing unless the diagnosed cause carries information about
correctness.

What would falsify the claim.  If a faithful nogood store that excludes on every
failure scores identically to this one on the registered worlds -- same wasted
work avoided, same false exclusions, same missed reopenings -- then the cause
filter buys nothing and the honest report is ``PARENT_SUFFICIENT``.  That
comparison is run in ``failure_parents.py`` and is not decided here.

Limitations that are not fixed by anything in this file.  The cause is supplied
by the caller: this module enforces what may follow from a diagnosis, not
whether the diagnosis was right.  In the registered worlds the cause is true by
construction; in an open domain, distinguishing an evaluator defect from a
genuine refutation is itself the hard problem, and nothing here solves it.
"""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Sequence

__all__ = [
    "Assumption",
    "Observation",
    "ResourceBound",
    "Success",
    "FailureCause",
    "EXCLUSION_BEARING_CAUSES",
    "Exclusion",
    "FailureKnowledge",
    "FailureStore",
    "derive_exclusions",
    "assumption_set",
    "assumption_name",
]


# --------------------------------------------------------------------------
# the small hashable pieces a receipt is built from
# --------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class Assumption:
    """One named assumption in force during an attempt.

    An assumption is a ``name = value`` pair rather than a bare proposition
    because reopening is defined on the *name*: "the move set changed" is the
    event, and which move set it changed to is not something an exclusion
    recorded under the old value can know.
    """

    name: str
    value: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name}={self.value}"


def assumption_name(changed: "Assumption | str") -> str:
    """Normalise a reopen trigger to the assumption *name* it refers to.

    Accepts an :class:`Assumption`, a ``"name=value"`` string, or a bare name,
    so a caller reporting a regime change does not have to know which of those
    three shapes the store wants.
    """
    if isinstance(changed, Assumption):
        return changed.name
    text = str(changed)
    return text.split("=", 1)[0] if "=" in text else text


def assumption_set(assumptions: Iterable[Assumption]) -> frozenset[Assumption]:
    """The canonical key half of an exclusion: an unordered, hashable set."""
    return frozenset(assumptions)


@dataclass(frozen=True)
class Observation:
    """One probe: what the method said, what the checker said.

    ``position`` is a canonical rendering rather than the position object so the
    record stays hashable and serialisable.  A refuting observation is the only
    admissible witness for ``REFUTED_BY_CHECKER``; without one the store has
    been handed an assertion, not evidence.
    """

    position: str
    method_says: bool
    checker_says: bool

    @property
    def refutes(self) -> bool:
        return self.method_says != self.checker_says


@dataclass(frozen=True)
class ResourceBound:
    """The budget an attempt ran under, and what it actually spent.

    Recorded because ``BUDGET_EXHAUSTED`` is only a truthful diagnosis when the
    bound was in fact reached; a machine that reports exhaustion without
    spending its budget is reporting something else.  Units match
    ``games.Work``, so the spend is a counted quantity and never a wall-clock
    reading.
    """

    expansions: int
    checker_calls: int
    spent_expansions: int = 0
    spent_checker_calls: int = 0

    @property
    def exhausted(self) -> bool:
        return (
            self.spent_expansions >= self.expansions
            or self.spent_checker_calls >= self.checker_calls
        )

    def as_dict(self) -> dict:
        return {
            "expansions": self.expansions,
            "checker_calls": self.checker_calls,
            "spent_expansions": self.spent_expansions,
            "spent_checker_calls": self.spent_checker_calls,
            "exhausted": self.exhausted,
        }


@dataclass(frozen=True)
class Success:
    """A certified success that a later failure record must not erase.

    Carried on the failure record itself so that "what survives this failure" is
    part of the same receipt as "what this failure kills".  A failure report
    that lists nothing as surviving is usually a report that has over-reached.
    """

    method: str
    assumptions: tuple[Assumption, ...]
    task: str
    note: str = ""

    @property
    def key(self) -> tuple[str, frozenset[Assumption]]:
        return (self.method, assumption_set(self.assumptions))


# --------------------------------------------------------------------------
# causes
# --------------------------------------------------------------------------


class FailureCause(enum.Enum):
    """Why the attempt failed -- which is not the same as what it looked like.

    The surface label of a failure ("no solution found", "refuted by checker")
    is systematically ambiguous between causes that license an exclusion and
    causes that license nothing.  Every member here can present under a label
    shared with some other member, which is what makes the distinction worth
    enforcing mechanically rather than reading off the log.
    """

    #: an independent exact checker exhibited a disagreeing position
    REFUTED_BY_CHECKER = "REFUTED_BY_CHECKER"
    #: the resource bound was spent; nothing was learned about correctness
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    #: the probes run could not have discriminated the method even in principle
    NON_IDENTIFYING_EXPERIMENT = "NON_IDENTIFYING_EXPERIMENT"
    #: the checker was wrong; its verdict is evidence about the checker
    EVALUATOR_DEFECT = "EVALUATOR_DEFECT"
    #: a declared precondition of the method did not hold in this context
    ASSUMPTION_VIOLATED = "ASSUMPTION_VIOLATED"

    @property
    def may_exclude(self) -> bool:
        """Whether a failure with this cause may create an exclusion at all."""
        return self in EXCLUSION_BEARING_CAUSES


#: The whole discipline of the module in one line.  A cause outside this set is
#: a statement about the attempt -- its budget, its probe set, its checker -- and
#: a statement about the attempt is never a statement about the method.
EXCLUSION_BEARING_CAUSES: frozenset[FailureCause] = frozenset(
    {FailureCause.REFUTED_BY_CHECKER, FailureCause.ASSUMPTION_VIOLATED}
)


# --------------------------------------------------------------------------
# exclusions
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Exclusion:
    """A method ruled out in one assumption context, with a way back out.

    The key is ``(method, assumptions)``.  There is deliberately no task field:
    a task identity is an accident of how the instance was drawn, and keying on
    it produces exactly the blacklist behaviour attack A10 is written against.
    """

    method: str
    assumptions: frozenset[Assumption]
    cause: FailureCause
    scope: str
    reopen_conditions: tuple[str, ...]
    witness: tuple[Observation, ...] = ()

    def __post_init__(self) -> None:
        if not self.cause.may_exclude:
            raise ValueError(
                f"cause {self.cause.name} may not create an exclusion; "
                "it is a statement about the attempt, not about the method"
            )
        if not self.reopen_conditions:
            raise ValueError(
                "an exclusion without a reopen condition is a one-way door; "
                "state the condition under which the method is reconsidered"
            )

    @property
    def key(self) -> tuple[str, frozenset[Assumption]]:
        return (self.method, self.assumptions)

    @property
    def depends_on(self) -> frozenset[str]:
        """Assumption *names* whose change retires this exclusion."""
        return frozenset(a.name for a in self.assumptions)

    def applies_to(self, method: str, assumptions: Iterable[Assumption]) -> bool:
        """Exact-key test; see the module docstring for why not containment."""
        return self.method == method and self.assumptions == assumption_set(assumptions)

    def as_dict(self) -> dict:
        return {
            "method": self.method,
            "assumptions": sorted(str(a) for a in self.assumptions),
            "cause": self.cause.name,
            "scope": self.scope,
            "reopen_conditions": list(self.reopen_conditions),
            "witness": [
                {
                    "position": o.position,
                    "method_says": o.method_says,
                    "checker_says": o.checker_says,
                }
                for o in self.witness
            ],
        }


def derive_exclusions(
    *,
    cause: FailureCause,
    method: str,
    assumptions: Sequence[Assumption],
    scope: str,
    reopen_conditions: Sequence[str],
    evidence: Sequence[Observation] = (),
) -> tuple[Exclusion, ...]:
    """The one place an exclusion is allowed to come into existence.

    Returns the empty tuple for every cause outside
    :data:`EXCLUSION_BEARING_CAUSES`.  Callers construct failure records through
    this function rather than writing an exclusion list by hand, so that a world
    or an agent cannot smuggle in an exclusion that its own diagnosis does not
    license.
    """
    if not cause.may_exclude:
        return ()
    return (
        Exclusion(
            method=method,
            assumptions=assumption_set(assumptions),
            cause=cause,
            scope=scope,
            reopen_conditions=tuple(reopen_conditions),
            witness=tuple(o for o in evidence if o.refutes),
        ),
    )


# --------------------------------------------------------------------------
# the failure record
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class FailureKnowledge:
    """Everything one failed attempt is entitled to assert.

    This is the CL-R4 ``FailureAttemptV1`` body with the diagnosis and its
    consequences made explicit.  The three fields that matter for the discipline
    are ``diagnosed_responsibility`` (the cause), ``justified_exclusions`` (what
    may follow from it, which is often nothing) and ``reopen_conditions`` (how
    the conclusion is unwound).  ``still_live_alternatives`` and
    ``preserved_successes`` are the negative space: a failure report that does
    not say what survives has not been thought through.

    ``__post_init__`` enforces the invariants rather than documenting them,
    because a discipline that depends on the caller remembering it is not a
    discipline.
    """

    attempted_method: str
    task: str
    representation: str
    assumptions: tuple[Assumption, ...]
    evidence: tuple[Observation, ...]
    resource_bound: ResourceBound
    observed_failure: str
    diagnosed_responsibility: FailureCause
    justified_exclusions: tuple[Exclusion, ...]
    still_live_alternatives: tuple[str, ...]
    preserved_successes: tuple[Success, ...]
    scope: str
    reopen_conditions: tuple[str, ...]

    def __post_init__(self) -> None:
        cause = self.diagnosed_responsibility
        if not cause.may_exclude and self.justified_exclusions:
            raise ValueError(
                f"{cause.name} justifies no exclusion; "
                "budget exhaustion, a non-identifying probe set and a defective "
                "checker are facts about the attempt, not about the method"
            )
        if cause is FailureCause.REFUTED_BY_CHECKER and not any(
            o.refutes for o in self.evidence
        ):
            raise ValueError(
                "REFUTED_BY_CHECKER without a refuting observation is an "
                "assertion, not a witness"
            )
        if cause is FailureCause.BUDGET_EXHAUSTED and not self.resource_bound.exhausted:
            raise ValueError(
                "BUDGET_EXHAUSTED reported while the declared bound was not reached"
            )
        for exclusion in self.justified_exclusions:
            if exclusion.method != self.attempted_method:
                raise ValueError(
                    "an attempt may only exclude the method it actually attempted"
                )
            if exclusion.assumptions != assumption_set(self.assumptions):
                raise ValueError(
                    "an exclusion must be keyed on the assumption set in force"
                )
            if exclusion.method in self.still_live_alternatives:
                raise ValueError(
                    "a method cannot be both excluded and a live alternative"
                )

    @property
    def created_exclusions(self) -> bool:
        return bool(self.justified_exclusions)

    @property
    def attempt_id(self) -> str:
        """``sha256`` of the canonical body, as CL-R4 requires.

        Content addressed rather than counter addressed so that two runs of the
        same registered world produce the same identifier and a receipt can be
        rechecked without the run that produced it.
        """
        return hashlib.sha256(
            json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def as_dict(self) -> dict:
        return {
            "attempted_method": self.attempted_method,
            "task": self.task,
            "representation": self.representation,
            "assumptions": sorted(str(a) for a in self.assumptions),
            "evidence": [
                {
                    "position": o.position,
                    "method_says": o.method_says,
                    "checker_says": o.checker_says,
                }
                for o in self.evidence
            ],
            "resource_bound": self.resource_bound.as_dict(),
            "observed_failure": self.observed_failure,
            "diagnosed_responsibility": self.diagnosed_responsibility.name,
            "justified_exclusions": [e.as_dict() for e in self.justified_exclusions],
            "still_live_alternatives": list(self.still_live_alternatives),
            "preserved_successes": [
                {
                    "method": s.method,
                    "assumptions": sorted(str(a) for a in s.assumptions),
                    "task": s.task,
                    "note": s.note,
                }
                for s in self.preserved_successes
            ],
            "scope": self.scope,
            "reopen_conditions": list(self.reopen_conditions),
        }

    @classmethod
    def build(
        cls,
        *,
        attempted_method: str,
        task: str,
        representation: str,
        assumptions: Sequence[Assumption],
        evidence: Sequence[Observation],
        resource_bound: ResourceBound,
        observed_failure: str,
        diagnosed_responsibility: FailureCause,
        still_live_alternatives: Sequence[str] = (),
        preserved_successes: Sequence[Success] = (),
        scope: str,
        reopen_conditions: Sequence[str],
    ) -> "FailureKnowledge":
        """Construct a record whose exclusions are *derived* from its cause.

        The only supported way to build a record in the registered worlds.  It
        removes the possibility of a world author writing down a cause and an
        inconsistent exclusion list, which would make the worlds test the author
        rather than the policy.
        """
        return cls(
            attempted_method=attempted_method,
            task=task,
            representation=representation,
            assumptions=tuple(assumptions),
            evidence=tuple(evidence),
            resource_bound=resource_bound,
            observed_failure=observed_failure,
            diagnosed_responsibility=diagnosed_responsibility,
            justified_exclusions=derive_exclusions(
                cause=diagnosed_responsibility,
                method=attempted_method,
                assumptions=tuple(assumptions),
                scope=scope,
                reopen_conditions=tuple(reopen_conditions),
                evidence=tuple(evidence),
            ),
            still_live_alternatives=tuple(still_live_alternatives),
            preserved_successes=tuple(preserved_successes),
            scope=scope,
            reopen_conditions=tuple(reopen_conditions),
        )


# --------------------------------------------------------------------------
# the store
# --------------------------------------------------------------------------


class FailureStore:
    """The governed failure memory: assumption-keyed, cause-filtered, reopenable.

    Mutable by design -- it is the machine's persistent state across a cognitive
    lifetime -- while every object it holds is frozen.  Nothing here reads a
    clock, a task identity or a checker; the store's whole job is bookkeeping
    over records the diagnosis produced.

    Three operations, and the interesting content is in what each refuses to do:

    ``record``   stores the attempt and installs only the exclusions the cause
                 licensed, which for three of the five causes is none.
    ``excluded`` answers on ``(method, assumptions)`` and has no task parameter,
                 so a task-keyed answer is not expressible.
    ``reopen``   retires every live exclusion that depended on the changed
                 assumption, so an exclusion is a lease and not a deletion.
    """

    def __init__(self) -> None:
        self._live: dict[tuple[str, frozenset[Assumption]], Exclusion] = {}
        self._reopened: list[Exclusion] = []
        self._attempts: list[FailureKnowledge] = []
        self._successes: set[tuple[str, frozenset[Assumption]]] = set()

    # ---- writing --------------------------------------------------------

    def record(self, knowledge: FailureKnowledge) -> tuple[Exclusion, ...]:
        """Record one failed attempt; return the exclusions it actually created.

        An empty return is the common and correct case.  Recording a failure is
        always allowed -- the attempt is data -- but concluding from it is not.

        Refuses to exclude a ``(method, assumptions)`` pair for which a success
        has already been preserved.  A checker that both certifies and refutes
        the same pair is not delivering a refutation; it is delivering evidence
        of its own defect, and the caller should be diagnosing
        ``EVALUATOR_DEFECT`` instead.
        """
        for success in knowledge.preserved_successes:
            self._successes.add(success.key)
        self._attempts.append(knowledge)
        created: list[Exclusion] = []
        for exclusion in knowledge.justified_exclusions:
            if exclusion.key in self._successes:
                raise ValueError(
                    f"refusing to exclude {exclusion.method} under assumptions where "
                    "a success is already preserved; the checker contradicts itself "
                    "and the diagnosis should be EVALUATOR_DEFECT"
                )
            self._live[exclusion.key] = exclusion
            created.append(exclusion)
        return tuple(created)

    def note_success(self, success: Success) -> None:
        """Register a certified success, retiring any exclusion it contradicts.

        This is the CL-R4 ``scope_recovery`` path: a later success in the same
        scope must reopen the failure rather than sit beside it.
        """
        self._successes.add(success.key)
        held = self._live.pop(success.key, None)
        if held is not None:
            self._reopened.append(held)

    # ---- reading --------------------------------------------------------

    def excluded(self, method: str, assumptions: Iterable[Assumption]) -> bool:
        """Is ``method`` ruled out in exactly this assumption context?

        Note the absent parameter: there is no task.  Two different tasks under
        the same assumptions get the same answer, which is the transfer a
        task-keyed memory cannot make, and the same task under different
        assumptions gets different answers, which is the recovery a task-keyed
        memory cannot make either.
        """
        return (method, assumption_set(assumptions)) in self._live

    def live_exclusion(
        self, method: str, assumptions: Iterable[Assumption]
    ) -> Exclusion | None:
        return self._live.get((method, assumption_set(assumptions)))

    @property
    def live_exclusions(self) -> tuple[Exclusion, ...]:
        return tuple(self._live.values())

    @property
    def reopened_exclusions(self) -> tuple[Exclusion, ...]:
        return tuple(self._reopened)

    @property
    def attempts(self) -> tuple[FailureKnowledge, ...]:
        return tuple(self._attempts)

    def permanently_closed(self) -> tuple[Exclusion, ...]:
        """Exclusions with no way back.  Empty by construction, and checked.

        :class:`Exclusion` refuses to exist without a reopen condition, so this
        is always empty.  It is exposed anyway because "we made it impossible"
        is a claim a reviewer should be able to test rather than take, and
        because a future change that weakened the constructor would show up here
        instead of silently.
        """
        return tuple(e for e in self._live.values() if not e.reopen_conditions)

    # ---- reopening ------------------------------------------------------

    def reopen(self, changed_assumption: Assumption | str) -> set[Exclusion]:
        """Retire every live exclusion that depended on the changed assumption.

        Fires on the assumption *name*.  An exclusion whose warrant rested on
        ``move_set = 1,2,3`` knows nothing about the world once the move set
        changes, whatever it changed to, so the exclusion is retired rather than
        adjusted.  Exclusions that did not depend on that name are untouched --
        "exactly when" is a two-sided requirement and over-firing would destroy
        knowledge just as surely as under-firing preserves error.

        A retired exclusion is not forgotten: it moves to
        :attr:`reopened_exclusions` and its method becomes reachable again.  If
        the method is still wrong under the new assumptions, a fresh refutation
        re-establishes the exclusion at the cost of one attempt.  Paying that
        cost every regime change is the price of never being broken shut.
        """
        name = assumption_name(changed_assumption)
        fired = {e for e in self._live.values() if name in e.depends_on}
        for exclusion in fired:
            del self._live[exclusion.key]
            self._reopened.append(exclusion)
        return fired

    # ---- reporting ------------------------------------------------------

    def as_dict(self) -> dict:
        return {
            "attempts": len(self._attempts),
            "live_exclusions": [e.as_dict() for e in self._live.values()],
            "reopened_exclusions": [e.as_dict() for e in self._reopened],
            "preserved_successes": sorted(
                m + " | " + ",".join(sorted(str(a) for a in s)) for m, s in self._successes
            ),
            "permanently_closed": len(self.permanently_closed()),
        }
