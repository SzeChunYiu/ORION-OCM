"""The registered diagnosis worlds: five causes behind one observed signal.

Every episode in this file presents the identical surface fact -- the attempt
terminated without a certified solution -- and carries a true cause that no arm
can read.  The cause is true **by construction**, and the construction is the
same one ``failure_worlds.py`` uses: take two rules from ``games.py`` and
``methods.py`` whose exact agreement set is computable, and place the boundary
of that agreement set where the episode needs it.  Every disagreement set below
is computed at import time and exported in :data:`GROUND_TRUTH`, so a reviewer
can recheck any episode's premise with arithmetic and never has to trust the
file.

**The four rule pairs carrying every world.**

``grundy_mod3`` versus ``grundy_mod4``
    ``SUB(1,2)`` has Grundy sequence ``0,1,2,0,1,2,…`` and ``SUB(1,2,3)`` has
    ``0,1,2,3,0,1,2,3,…``.  ``n mod 3 == 0`` is exactly the P-rule of
    ``SUB(1,2)`` and refutable on ``SUB(1,2,3)``; ``n mod 4 == 0`` is the mirror
    image.  Each scope therefore has a method that is exactly right in it and a
    method that is demonstrably wrong in it, which is what separates a genuine
    refutation from a wrong verdict about a correct method.

``xor_combiner`` versus ``sum_mod_2_combiner``
    ``SUM_MOD_2`` is registered in ``XOR_LOOKALIKES_ON_BINARY_VALUES``: on
    ``NIM(2)`` with heaps in ``{0,1}`` it is extensionally identical to ``XOR``,
    and ``(1,3)`` separates them.  That supplies a probe set which *provably*
    could not have discriminated -- the witness a timeout can never supply.

``xor_combiner`` versus ``max_mod_2_combiner``
    ``MAX_MOD_2`` is deliberately **not** a registered lookalike: ``methods.py``
    says so, because it already disagrees with ``XOR`` at ``(1,1)``.  It is
    therefore the method that a genuine refutation can refute on binary heaps,
    which is what the over-generalisation hostile needs on its *sound* side.

the mis-tabulated checkers
    ``sub12_table_applied_to_sub123`` answers with the ``SUB(1,2)`` Grundy table
    whatever game it is asked about.  On ``SUB(1,2)`` that is exactly correct;
    on ``SUB(1,2,3)`` it is wrong infinitely often.  ``sub12_table_applied_to_nim``
    is the same trick against ``NIM(2)``: the ``SUB(1,2)`` table agrees with the
    per-heap Nim value on heaps ``0,1,2`` and diverges from heap ``3``, so the
    checker is exactly sound on binary heaps and defective on heaps up to four.
    **One checker id, sound in one scope and defective in another**, computed
    rather than declared, is the hostile.

**What each world is for.**

``DW1`` stationary, sound checker, all four causes that a sound scope admits.
        The base rate world: whatever a policy scores here it scores without any
        checker question ever being live.
``DW2`` one scope, one defective checker, repeated tasks.  The accumulation
        world: the scope fact is established once and is worth remembering.
``DW3`` **hostile.**  One checker id, defective on ``SUB(1,2,3)`` and sound on
        ``SUB(1,2)``, alternating.  A machine that generalises "this checker is
        broken" past the scope where it witnessed the defect answers
        ``EVALUATOR_DEFECT`` against methods that were genuinely refuted.
``DW4`` **hostile.**  Probes are withheld.  On several episodes the available
        evidence provably cannot single out a cause, and the only correct answer
        is ``CANNOT_IDENTIFY``.  An arm that always names a cause fails here by
        construction, and that is what the column is for.
``DW5`` the drawn sequence.  Twenty episodes over four ``(checker, scope)``
        pairs, order and causes derived from the pre-registration commitment,
        two of the pairs sharing a checker id across a soundness boundary.  This
        is where the cumulative-cost curve is read.

**Targets, and why refusing is sometimes the right answer.**  An episode's
scoring target is *not* always its true cause.  :meth:`Episode.identifiable`
computes whether the full set of probes available in that episode singles the
true cause out; when it does not, the target is ``CANNOT_IDENTIFY``.  An arm
that names the true cause anyway has guessed, and guessing right is not scored
as knowing.  This is computed from the registered response table, not asserted,
so a reviewer can recheck every target.

**The downstream half.**  Each episode carries one query about a later task,
and the query's verdict is fixed by the arithmetic above: a genuinely refuted
method must be blocked on a fresh task in the same scope, and a correct method
that failed for a reason carrying no information about correctness must not be.
The queries are answered out of ``failure.FailureStore``, used exactly as the
prior pilot ships it and never modified, so that the downstream columns are a
consequence of the diagnosis and not of a second policy sitting behind it.
"""

from __future__ import annotations

import enum
import random
from dataclasses import dataclass
from typing import Callable, Sequence

from diagnosis import (
    ALL_PROBES,
    CAUSE_ORDER,
    CAUSE_PRIOR,
    COMMITMENT,
    Case,
    Cause,
    Diagnosis,
    DiagnosisArm,
    PROBE_COST,
    PROBE_ORDER,
    Probe,
    ProbeOutcome,
    candidates,
    expected_outcome,
    record_diagnosis,
)
from failure import Assumption, FailureStore, Observation, ResourceBound
from games import MultiHeapGame, SubtractionGame, Work
from methods import COMBINERS, XOR_LOOKALIKES_ON_BINARY_VALUES

__all__ = [
    "GROUND_TRUTH",
    "CHECKER_SOUNDNESS",
    "SCOPES",
    "QueryKind",
    "DownstreamQuery",
    "RegimeChange",
    "Episode",
    "EpisodeBench",
    "DiagnosisWorld",
    "WORLDS",
    "world_by_id",
    "Score",
    "run",
    "scoreboard",
    "cause_counts",
    "target_counts",
    "constant_predictor_baseline",
    "PROBE_BUDGET",
]

HORIZON = 40

#: Registered per-case probe budget.  Generous by design: the whole probe set
#: costs 18 and the budget is 32, so it never binds anywhere in this experiment.
#: It is carried and enforced anyway, because "the budget never bound" is a
#: claim a reviewer should be able to test rather than take, and
#: ``test_diagnosis.py`` tests it.
PROBE_BUDGET = 32


def _require(condition: bool, message: str) -> None:
    """Fail loudly at import if a world's premise is not actually true.

    Used instead of ``assert`` so the checks survive ``python -O``.  A world
    whose ground truth stopped holding must not quietly become a world that
    tests nothing.
    """
    if not condition:
        raise AssertionError("diagnosis-world ground truth violated: " + message)


# --------------------------------------------------------------------------
# ground truth, computed rather than asserted
# --------------------------------------------------------------------------

SUB12 = SubtractionGame((1, 2))
SUB123 = SubtractionGame((1, 2, 3))
NIM2 = MultiHeapGame.nim(2, 4)

_T12 = SUB12.grundy_upto(HORIZON)
_T123 = SUB123.grundy_upto(HORIZON)

_XOR = COMBINERS["XOR"]
_SUM_MOD_2 = COMBINERS["SUM_MOD_2"]
_MAX_MOD_2 = COMBINERS["MAX_MOD_2"]


def _mod3(n: int) -> bool:
    return n % 3 == 0


def _mod4(n: int) -> bool:
    return n % 4 == 0


def _sub_disagreements(rule, table) -> tuple[int, ...]:
    return tuple(n for n in range(1, HORIZON + 1) if rule(n) != (table[n] == 0))


MOD3_WRONG_ON_SUB123 = _sub_disagreements(_mod3, _T123)
MOD3_WRONG_ON_SUB12 = _sub_disagreements(_mod3, _T12)
MOD4_WRONG_ON_SUB12 = _sub_disagreements(_mod4, _T12)
MOD4_WRONG_ON_SUB123 = _sub_disagreements(_mod4, _T123)

#: the mis-tabulated subtraction checker: it answers with the ``SUB(1,2)`` table
#: whatever game it was asked about
SUB_CHECKER_WRONG_ON_SUB123 = tuple(
    n for n in range(1, HORIZON + 1) if (_T12[n] == 0) != (_T123[n] == 0)
)
SUB_CHECKER_WRONG_ON_SUB12 = ()

NIM_WIDE_POSITIONS = tuple((a, b) for a in range(5) for b in range(5))
NIM_BINARY_POSITIONS = tuple((a, b) for a in range(2) for b in range(2))


def _combiner_disagreements(fn, positions) -> tuple[tuple[int, ...], ...]:
    return tuple(p for p in positions if (fn(p) == 0) != (_XOR(p) == 0))


SUM_MOD_2_WRONG_WIDE = _combiner_disagreements(_SUM_MOD_2, NIM_WIDE_POSITIONS)
SUM_MOD_2_WRONG_BINARY = _combiner_disagreements(_SUM_MOD_2, NIM_BINARY_POSITIONS)
MAX_MOD_2_WRONG_BINARY = _combiner_disagreements(_MAX_MOD_2, NIM_BINARY_POSITIONS)
MAX_MOD_2_WRONG_WIDE = _combiner_disagreements(_MAX_MOD_2, NIM_WIDE_POSITIONS)


def _nim_via_sub12(position: Sequence[int]) -> int:
    acc = 0
    for h in position:
        acc ^= _T12[h]
    return acc


#: the mis-tabulated Nim checker: exact on binary heaps, wrong from heap three
NIM_CHECKER_WRONG_WIDE = tuple(
    p for p in NIM_WIDE_POSITIONS if (_nim_via_sub12(p) == 0) != (_XOR(p) == 0)
)
NIM_CHECKER_WRONG_BINARY = tuple(
    p for p in NIM_BINARY_POSITIONS if (_nim_via_sub12(p) == 0) != (_XOR(p) == 0)
)

_require(MOD3_WRONG_ON_SUB12 == (), "n mod 3 must be exactly the P-rule of SUB(1,2)")
_require(MOD3_WRONG_ON_SUB123 != (), "n mod 3 must be refutable on SUB(1,2,3)")
_require(MOD4_WRONG_ON_SUB123 == (), "n mod 4 must be exactly the P-rule of SUB(1,2,3)")
_require(MOD4_WRONG_ON_SUB12 != (), "n mod 4 must be refutable on SUB(1,2)")
_require(
    SUB_CHECKER_WRONG_ON_SUB123 != (),
    "the SUB(1,2) table must be a defective checker for SUB(1,2,3)",
)
_require(
    SUM_MOD_2_WRONG_BINARY == () and "SUM_MOD_2" in XOR_LOOKALIKES_ON_BINARY_VALUES,
    "SUM_MOD_2 must be a registered XOR lookalike on binary heaps",
)
_require((1, 3) in SUM_MOD_2_WRONG_WIDE, "(1,3) must separate SUM_MOD_2 from XOR")
_require(
    "MAX_MOD_2" not in XOR_LOOKALIKES_ON_BINARY_VALUES and (1, 1) in MAX_MOD_2_WRONG_BINARY,
    "MAX_MOD_2 must be refutable on binary heaps; methods.py says it is not a lookalike",
)
_require(
    NIM_CHECKER_WRONG_BINARY == () and NIM_CHECKER_WRONG_WIDE != (),
    "the SUB(1,2) table must be an exact Nim checker on binary heaps and defective "
    "on heaps up to four; this is the over-generalisation hostile and it is computed",
)

#: Exported so the tests can restate every premise independently of the world
#: objects, and so a reader can check the claims without running anything.
GROUND_TRUTH = {
    "sub12_grundy_prefix": tuple(_T12[:12]),
    "sub123_grundy_prefix": tuple(_T123[:12]),
    "mod3_wrong_on_sub123": MOD3_WRONG_ON_SUB123,
    "mod3_wrong_on_sub12": MOD3_WRONG_ON_SUB12,
    "mod4_wrong_on_sub12": MOD4_WRONG_ON_SUB12,
    "mod4_wrong_on_sub123": MOD4_WRONG_ON_SUB123,
    "sub_checker_wrong_on_sub123": SUB_CHECKER_WRONG_ON_SUB123,
    "sub_checker_wrong_on_sub12": SUB_CHECKER_WRONG_ON_SUB12,
    "sum_mod_2_wrong_wide": SUM_MOD_2_WRONG_WIDE,
    "sum_mod_2_wrong_binary": SUM_MOD_2_WRONG_BINARY,
    "max_mod_2_wrong_binary": MAX_MOD_2_WRONG_BINARY,
    "nim_checker_wrong_wide": NIM_CHECKER_WRONG_WIDE,
    "nim_checker_wrong_binary": NIM_CHECKER_WRONG_BINARY,
}


# ---- exact work counters, so downstream work is counted and not invented ----


def _sub_work(game: SubtractionGame, n: int) -> int:
    work = Work()
    game.grundy_upto(n, work=work)
    return work.total


def _nim_work(position: Sequence[int]) -> int:
    work = Work()
    NIM2.is_p_position(position, work=work)
    return work.total


# --------------------------------------------------------------------------
# scopes and checkers
# --------------------------------------------------------------------------

EXACT_SUB = "grundy_dp_exact"
SUB_DUAL = "sub12_table_applied_to_sub123"
EXACT_NIM = "sprague_grundy_exact"
NIM_DUAL = "sub12_table_applied_to_nim"


@dataclass(frozen=True)
class ScopeSpec:
    """One registered scope: its assumptions and the two methods it separates.

    ``correct_method`` is exactly right here, so any failure of it is a failure
    that carries no information about correctness -- a spent budget, a dud probe
    set, or a wrong verdict.  ``refuted_method`` is demonstrably wrong here, and
    ``refuting_positions`` is the computed set of tasks that witness it.  The
    pairing is what makes every downstream verdict in this file a fact rather
    than a judgement.
    """

    scope_id: str
    base_assumptions: tuple[Assumption, ...]
    correct_method: str
    refuted_method: str
    refuting_positions: tuple
    neutral_positions: tuple
    satisfied_precondition: tuple[str, ...]
    violated_precondition: tuple[str, ...]
    control_positions: int
    work: Callable[[object], int]
    task_label: Callable[[object], str]


def _sub_task(n) -> str:
    return f"T[n={n}]"


def _nim_task(p) -> str:
    return f"T[{p[0]},{p[1]}]"


SCOPES: dict[str, ScopeSpec] = {
    "SUB123": ScopeSpec(
        scope_id="SUB(1,2,3), one heap, n <= 40",
        base_assumptions=(
            Assumption("move_set", "1,2,3"),
            Assumption("play", "normal"),
        ),
        correct_method="grundy_mod4",
        refuted_method="grundy_mod3",
        refuting_positions=MOD3_WRONG_ON_SUB123,
        neutral_positions=tuple(range(1, HORIZON + 1)),
        satisfied_precondition=("move set is finite", "play convention is normal"),
        violated_precondition=("move_set == 1,2",),
        control_positions=HORIZON,
        work=lambda n: _sub_work(SUB123, n),
        task_label=_sub_task,
    ),
    "SUB12": ScopeSpec(
        scope_id="SUB(1,2), one heap, n <= 40",
        base_assumptions=(
            Assumption("move_set", "1,2"),
            Assumption("play", "normal"),
        ),
        correct_method="grundy_mod3",
        refuted_method="grundy_mod4",
        refuting_positions=MOD4_WRONG_ON_SUB12,
        neutral_positions=tuple(range(1, HORIZON + 1)),
        satisfied_precondition=("move set is finite", "play convention is normal"),
        violated_precondition=("move_set == 1,2,3",),
        control_positions=HORIZON,
        work=lambda n: _sub_work(SUB12, n),
        task_label=_sub_task,
    ),
    "NIM_WIDE": ScopeSpec(
        scope_id="NIM(2), heaps 0..4",
        base_assumptions=(
            Assumption("family", "NIM(2)"),
            Assumption("heap_values", "0..4"),
        ),
        correct_method="xor_combiner",
        refuted_method="sum_mod_2_combiner",
        refuting_positions=SUM_MOD_2_WRONG_WIDE,
        neutral_positions=NIM_WIDE_POSITIONS[1:],
        satisfied_precondition=("heaps are independent", "per-heap values are exact"),
        violated_precondition=("heap_values in {0,1}",),
        control_positions=len(NIM_WIDE_POSITIONS),
        work=_nim_work,
        task_label=_nim_task,
    ),
    "NIM_BINARY": ScopeSpec(
        scope_id="NIM(2), heaps 0..1",
        base_assumptions=(
            Assumption("family", "NIM(2)"),
            Assumption("heap_values", "0..1"),
        ),
        correct_method="xor_combiner",
        refuted_method="max_mod_2_combiner",
        refuting_positions=MAX_MOD_2_WRONG_BINARY,
        neutral_positions=NIM_BINARY_POSITIONS[1:],
        satisfied_precondition=("heaps are independent", "per-heap values are exact"),
        violated_precondition=("heaps == 1",),
        control_positions=len(NIM_BINARY_POSITIONS),
        work=_nim_work,
        task_label=_nim_task,
    ),
}

#: Checker soundness per ``(checker, scope)``, **computed** from the
#: disagreement sets above rather than declared.  The two ``*_DUAL`` checkers
#: are the point: one identity, sound in one scope and defective in another.
CHECKER_SOUNDNESS: dict[tuple[str, str], bool] = {
    (EXACT_SUB, "SUB123"): True,
    (EXACT_SUB, "SUB12"): True,
    (SUB_DUAL, "SUB123"): SUB_CHECKER_WRONG_ON_SUB123 == (),
    (SUB_DUAL, "SUB12"): SUB_CHECKER_WRONG_ON_SUB12 == (),
    (EXACT_NIM, "NIM_WIDE"): True,
    (EXACT_NIM, "NIM_BINARY"): True,
    (NIM_DUAL, "NIM_WIDE"): NIM_CHECKER_WRONG_WIDE == (),
    (NIM_DUAL, "NIM_BINARY"): NIM_CHECKER_WRONG_BINARY == (),
}

_require(
    CHECKER_SOUNDNESS[(SUB_DUAL, "SUB123")] is False
    and CHECKER_SOUNDNESS[(SUB_DUAL, "SUB12")] is True,
    "sub12_table_applied_to_sub123 must be defective in one scope and sound in the other",
)
_require(
    CHECKER_SOUNDNESS[(NIM_DUAL, "NIM_WIDE")] is False
    and CHECKER_SOUNDNESS[(NIM_DUAL, "NIM_BINARY")] is True,
    "sub12_table_applied_to_nim must be defective in one scope and sound in the other",
)

_WRONG_POSITIONS: dict[tuple[str, str], tuple] = {
    (EXACT_SUB, "SUB123"): (),
    (EXACT_SUB, "SUB12"): (),
    (SUB_DUAL, "SUB123"): SUB_CHECKER_WRONG_ON_SUB123,
    (SUB_DUAL, "SUB12"): SUB_CHECKER_WRONG_ON_SUB12,
    (EXACT_NIM, "NIM_WIDE"): (),
    (EXACT_NIM, "NIM_BINARY"): (),
    (NIM_DUAL, "NIM_WIDE"): NIM_CHECKER_WRONG_WIDE,
    (NIM_DUAL, "NIM_BINARY"): NIM_CHECKER_WRONG_BINARY,
}


# --------------------------------------------------------------------------
# episodes, benches and downstream queries
# --------------------------------------------------------------------------


class QueryKind(enum.Enum):
    """What the arithmetic says a later query's answer must be."""

    #: the method is genuinely wrong here; not blocking repeats known-wasted work
    MUST_BLOCK = "MUST_BLOCK"
    #: the method is live here; blocking it is a false exclusion
    MUST_NOT_BLOCK = "MUST_NOT_BLOCK"
    #: the exclusion's reopen condition has fired; blocking leaves it unreachable
    MUST_REOPEN = "MUST_REOPEN"


@dataclass(frozen=True)
class DownstreamQuery:
    """Would this arm attempt this method on a later task in this context?"""

    method: str
    task: str
    assumptions: tuple[Assumption, ...]
    kind: QueryKind
    work_if_attempted: int
    ground_truth: str


@dataclass(frozen=True)
class RegimeChange:
    """An assumption changed value.  Announced to every arm identically."""

    changed: str
    to_value: str
    note: str = ""


class EpisodeBench:
    """What an arm holds during one episode.  It cannot reach the cause.

    Constructed from a pre-computed outcome vector, **not** from the episode, so
    there is no reference path from an arm to the ground-truth cause even by
    reflection.  ``test_diagnosis.py`` asserts that no attribute of a live bench
    is a :class:`Cause`, and separately greps every arm's source for the name of
    the ground-truth field, the way ``test_scaling.py`` greps for ``true_cone``.
    """

    def __init__(
        self,
        case: Case,
        outcomes: dict[Probe, bool],
        details: dict[Probe, str],
    ) -> None:
        self._case = case
        self._outcomes = dict(outcomes)
        self._details = dict(details)
        self._spent = 0
        self._probes_run: list[Probe] = []

    @property
    def case(self) -> Case:
        return self._case

    @property
    def spent(self) -> int:
        return self._spent

    @property
    def probes_run(self) -> tuple[Probe, ...]:
        return tuple(self._probes_run)

    def run(self, probe: Probe) -> ProbeOutcome:
        """Buy one observation.  Refuses what the case does not offer."""
        if probe not in self._case.available_probes:
            raise ValueError(
                f"{probe.name} is not available in {self._case.case_id}; "
                "a situation that does not admit a probe is part of the problem"
            )
        cost = PROBE_COST[probe]
        if self._spent + cost > self._case.probe_budget:
            raise ValueError(
                f"probe budget {self._case.probe_budget} exhausted in "
                f"{self._case.case_id} at {self._spent}"
            )
        self._spent += cost
        self._probes_run.append(probe)
        return ProbeOutcome(
            probe=probe,
            value=self._outcomes[probe],
            cost=cost,
            detail=self._details.get(probe, ""),
        )


@dataclass(frozen=True)
class Episode:
    """One failed attempt with a cause the world knows and no arm can read.

    ``true_cause`` is the scorer's field.  It is named so that a source grep for
    it identifies every place the ground truth is touched, and every such place
    is either this dataclass, the episode builder, or the scoring loop.
    """

    case: Case
    true_cause: Cause
    checker_sound: bool
    outcomes: tuple[tuple[Probe, bool], ...]
    details: tuple[tuple[Probe, str], ...]
    downstream: DownstreamQuery | None
    note: str = ""

    def __post_init__(self) -> None:
        if self.true_cause not in {c for c in CAUSE_ORDER}:
            raise ValueError(
                "CANNOT_IDENTIFY is a verdict, never a cause a world may carry"
            )
        if self.true_cause is Cause.EVALUATOR_DEFECT and self.checker_sound:
            raise ValueError(
                "a checker that passes its controls over this scope has not "
                "returned a wrong verdict in it"
            )

    def bench(self) -> EpisodeBench:
        return EpisodeBench(self.case, dict(self.outcomes), dict(self.details))

    @property
    def identifiable(self) -> bool:
        """Do the probes available *here* single the true cause out?

        Computed by running the registered response table forward over every
        available probe and inverting it, with the checker's soundness left
        latent.  This is the same inference every arm performs; an arm cannot do
        better than it, and an arm that names a cause where this returns
        ``False`` has guessed.
        """
        observed = {
            probe: expected_outcome(self.true_cause, probe, self.checker_sound)
            for probe in self.case.available_probes
        }
        return candidates(observed, None) == frozenset({self.true_cause})

    @property
    def target(self) -> Cause:
        """The verdict that is correct here: the cause, or an honest refusal."""
        return self.true_cause if self.identifiable else Cause.CANNOT_IDENTIFY


def _episode(
    *,
    case_id: str,
    cause: Cause,
    scope_key: str,
    checker_id: str,
    index: int,
    available: frozenset[Probe] = ALL_PROBES,
    note: str = "",
) -> Episode:
    """Build one episode with its outcome vector and its downstream query.

    The method is chosen by the cause, and the choice is what makes the
    downstream verdict a fact:

    * ``TRUE_REFUTATION`` and ``ASSUMPTION_VIOLATED`` run the scope's
      ``refuted_method`` on a task drawn from the computed disagreement set, so
      the exclusion they license is licit and a later task in the same scope
      **must** be blocked;
    * every other cause runs the scope's ``correct_method``, which is exactly
      right here, so blocking it later is a false exclusion.

    The observed signal, the exhausted bound and the disagreeing checker
    observation are identical in all five cases.  Nothing on the record
    separates them.
    """
    scope = SCOPES[scope_key]
    sound = CHECKER_SOUNDNESS[(checker_id, scope_key)]
    if cause is Cause.EVALUATOR_DEFECT and sound:
        raise AssertionError(
            f"{case_id}: EVALUATOR_DEFECT needs a checker that is defective here"
        )

    refuting = cause in (Cause.TRUE_REFUTATION, Cause.ASSUMPTION_VIOLATED)
    method = scope.refuted_method if refuting else scope.correct_method
    pool = scope.refuting_positions if refuting else scope.neutral_positions
    here = pool[index % len(pool)]
    later = pool[(index + 1) % len(pool)]

    assumptions = scope.base_assumptions + (Assumption("checker", checker_id),)
    preconditions = (
        scope.violated_precondition
        if cause is Cause.ASSUMPTION_VIOLATED
        else scope.satisfied_precondition
    )

    # What the checker reported: a disagreement at the disputed position.  This
    # is the same shape for every cause, which is exactly why it identifies
    # none of them.
    evidence = (
        Observation(
            position=scope.task_label(here), method_says=True, checker_says=False
        ),
    )
    bound = ResourceBound(
        expansions=512,
        checker_calls=64,
        spent_expansions=512,
        spent_checker_calls=17,
    )

    case = Case(
        case_id=case_id,
        method=method,
        task=scope.task_label(here),
        scope=scope.scope_id,
        checker_id=checker_id,
        assumptions=assumptions,
        declared_preconditions=preconditions,
        evidence=evidence,
        resource_bound=bound,
        available_probes=available,
        probe_budget=PROBE_BUDGET,
    )

    outcomes = {
        probe: expected_outcome(cause, probe, sound) for probe in PROBE_ORDER
    }
    wrong_here = len(_WRONG_POSITIONS[(checker_id, scope_key)])
    survivors = len(XOR_LOOKALIKES_ON_BINARY_VALUES) + 1
    details = {
        Probe.PRECONDITION_AUDIT: (
            f"{len(preconditions) if outcomes[Probe.PRECONDITION_AUDIT] else 0}"
            f" of {len(preconditions)} declared preconditions hold on {case.task}"
        ),
        Probe.CHECKER_CONTROL_BATTERY: (
            f"{wrong_here} of {scope.control_positions} control positions disagree "
            f"with the independently known answer"
        ),
        Probe.SPLIT_TEST: (
            f"{survivors} hypotheses survive the probes actually run; "
            + (
                "some probe run separates them"
                if outcomes[Probe.SPLIT_TEST]
                else "every survivor agrees with every other on every probe run"
            )
        ),
        Probe.RERUN_LARGER_BUDGET: (
            "budget raised to 2048 expansions: "
            + (
                "a solution was certified"
                if outcomes[Probe.RERUN_LARGER_BUDGET]
                else "still no certified solution"
            )
        ),
        Probe.SECOND_CHECKER: (
            f"independently built checker at {case.task}: "
            + (
                "same verdict as the incumbent"
                if outcomes[Probe.SECOND_CHECKER]
                else "opposite verdict to the incumbent"
            )
        ),
    }

    if refuting:
        downstream = DownstreamQuery(
            method=method,
            task=scope.task_label(later),
            assumptions=assumptions,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=scope.work(later),
            ground_truth=(
                f"{scope.task_label(later)} is in the computed disagreement set of "
                f"{method} on {scope.scope_id}; the method is wrong there too"
            ),
        )
    else:
        downstream = DownstreamQuery(
            method=method,
            task=scope.task_label(later),
            assumptions=assumptions,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=scope.work(later),
            ground_truth=(
                f"{method} is exactly the P-rule of {scope.scope_id}; its "
                f"disagreement set there is empty, so excluding it forfeits the answer"
            ),
        )

    return Episode(
        case=case,
        true_cause=cause,
        checker_sound=sound,
        outcomes=tuple(sorted(outcomes.items(), key=lambda kv: kv[0].name)),
        details=tuple(sorted(details.items(), key=lambda kv: kv[0].name)),
        downstream=downstream,
        note=note,
    )


# --------------------------------------------------------------------------
# worlds
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DiagnosisWorld:
    """A sequence of episodes, then the queries their conclusions answer."""

    world_id: str
    hostile: bool
    tests: str
    episodes: tuple[Episode, ...]
    regime_change: RegimeChange | None = None
    notes: str = ""

    @property
    def script(self) -> tuple:
        """Episodes, then downstream queries, then any regime change and reopen.

        The downstream queries come after every episode rather than interleaved
        so that an arm's conclusions are all in place before any of them is
        tested; interleaving would score early conclusions on less evidence than
        late ones and confound the diagnosis with the ordering.
        """
        events: list = list(self.episodes)
        events.extend(e.downstream for e in self.episodes if e.downstream is not None)
        if self.regime_change is not None:
            events.append(self.regime_change)
            for episode in self.episodes:
                query = episode.downstream
                if query is None or query.kind is not QueryKind.MUST_BLOCK:
                    continue
                if not any(a.name == self.regime_change.changed for a in query.assumptions):
                    continue
                events.append(
                    DownstreamQuery(
                        method=query.method,
                        task=query.task,
                        assumptions=query.assumptions,
                        kind=QueryKind.MUST_REOPEN,
                        work_if_attempted=query.work_if_attempted,
                        ground_truth=(
                            f"{self.regime_change.changed} changed; the warrant for "
                            "the exclusion is gone and the method must be reachable"
                        ),
                    )
                )
                break
        return tuple(events)

    @property
    def cause_counts(self) -> dict[Cause, int]:
        counts = {c: 0 for c in CAUSE_ORDER}
        for episode in self.episodes:
            counts[episode.true_cause] += 1
        return counts


def _dw1() -> DiagnosisWorld:
    """Stationary, sound checker.  The base-rate world."""
    plan = [
        Cause.TRUE_REFUTATION,
        Cause.BUDGET_EXHAUSTED,
        Cause.NON_IDENTIFYING_EXPERIMENT,
        Cause.ASSUMPTION_VIOLATED,
        Cause.TRUE_REFUTATION,
        Cause.BUDGET_EXHAUSTED,
        Cause.TRUE_REFUTATION,
        Cause.NON_IDENTIFYING_EXPERIMENT,
    ]
    return DiagnosisWorld(
        world_id="DW1_STATIONARY_SOUND_CHECKER",
        hostile=False,
        tests=(
            "with an exact checker the evaluator-defect branch is never live; every "
            "arm that pays for it is paying for nothing, and the cheap control "
            "battery is what establishes that once instead of every time"
        ),
        episodes=tuple(
            _episode(
                case_id=f"DW1-{i:02d}",
                cause=cause,
                scope_key="SUB123",
                checker_id=EXACT_SUB,
                index=i,
            )
            for i, cause in enumerate(plan)
        ),
        regime_change=RegimeChange(
            changed="move_set",
            to_value="1,2",
            note="the move set reverts and grundy_mod3 is exactly right again",
        ),
        notes=(
            "EVALUATOR_DEFECT cannot occur here by construction, so this world "
            "measures the cost of keeping the possibility open rather than the "
            "benefit of resolving it"
        ),
    )


def _dw2() -> DiagnosisWorld:
    """One defective checker, one scope, repeated tasks."""
    plan = [
        Cause.EVALUATOR_DEFECT,
        Cause.TRUE_REFUTATION,
        Cause.EVALUATOR_DEFECT,
        Cause.BUDGET_EXHAUSTED,
        Cause.EVALUATOR_DEFECT,
        Cause.NON_IDENTIFYING_EXPERIMENT,
        Cause.TRUE_REFUTATION,
        Cause.EVALUATOR_DEFECT,
        Cause.ASSUMPTION_VIOLATED,
        Cause.EVALUATOR_DEFECT,
    ]
    return DiagnosisWorld(
        world_id="DW2_DEFECTIVE_CHECKER_ONE_SCOPE",
        hostile=False,
        tests=(
            "the checker is defective throughout one scope; the fact is established "
            "once by a cheap control battery and is worth exactly the same on every "
            "later task, so an arm that re-establishes it every time is paying twice "
            "for one finding"
        ),
        episodes=tuple(
            _episode(
                case_id=f"DW2-{i:02d}",
                cause=cause,
                scope_key="SUB123",
                checker_id=SUB_DUAL,
                index=i,
            )
            for i, cause in enumerate(plan)
        ),
        notes=(
            "half the episodes are genuine evaluator defects, so an arm that never "
            "considers the possibility loses half this world outright"
        ),
    )


def _dw3() -> DiagnosisWorld:
    """HOSTILE: one checker, defective in one scope and sound in the other."""
    plan = [
        ("SUB123", Cause.EVALUATOR_DEFECT),
        ("SUB12", Cause.TRUE_REFUTATION),
        ("SUB123", Cause.TRUE_REFUTATION),
        ("SUB12", Cause.TRUE_REFUTATION),
        ("SUB123", Cause.EVALUATOR_DEFECT),
        ("SUB12", Cause.BUDGET_EXHAUSTED),
        ("SUB123", Cause.EVALUATOR_DEFECT),
        ("SUB12", Cause.TRUE_REFUTATION),
        ("SUB123", Cause.BUDGET_EXHAUSTED),
        ("SUB12", Cause.NON_IDENTIFYING_EXPERIMENT),
        ("SUB123", Cause.TRUE_REFUTATION),
        ("SUB12", Cause.TRUE_REFUTATION),
    ]
    return DiagnosisWorld(
        world_id="DW3_ONE_CHECKER_TWO_SCOPES_HOSTILE",
        hostile=True,
        tests=(
            "sub12_table_applied_to_sub123 is wrong infinitely often on SUB(1,2,3) "
            "and exactly right on SUB(1,2); an arm that carries the witnessed defect "
            "out of the scope where it witnessed it answers EVALUATOR_DEFECT against "
            "methods that were genuinely refuted, and every such answer is counted"
        ),
        episodes=tuple(
            _episode(
                case_id=f"DW3-{i:02d}",
                cause=cause,
                scope_key=scope_key,
                checker_id=SUB_DUAL,
                index=i,
            )
            for i, (scope_key, cause) in enumerate(plan)
        ),
        regime_change=RegimeChange(
            changed="move_set",
            to_value="1,4",
            note="a move set neither exclusion was earned under",
        ),
        notes=(
            "five of the six SUB(1,2) episodes are genuine refutations of "
            "grundy_mod4, which is the method a scope-blind memory will excuse"
        ),
    )


def _dw4() -> DiagnosisWorld:
    """HOSTILE: the probes needed are not on offer, so refusal is the answer."""
    no_second = ALL_PROBES - {Probe.SECOND_CHECKER}
    no_rerun = ALL_PROBES - {Probe.RERUN_LARGER_BUDGET}
    no_split = ALL_PROBES - {Probe.SPLIT_TEST}
    no_precondition = ALL_PROBES - {Probe.PRECONDITION_AUDIT}
    plan = [
        ("SUB123", SUB_DUAL, Cause.TRUE_REFUTATION, no_second),
        ("SUB123", SUB_DUAL, Cause.EVALUATOR_DEFECT, no_second),
        ("SUB123", EXACT_SUB, Cause.TRUE_REFUTATION, no_rerun),
        ("SUB123", EXACT_SUB, Cause.BUDGET_EXHAUSTED, no_rerun),
        ("NIM_WIDE", EXACT_NIM, Cause.TRUE_REFUTATION, no_split),
        ("NIM_WIDE", EXACT_NIM, Cause.NON_IDENTIFYING_EXPERIMENT, no_split),
        ("NIM_WIDE", EXACT_NIM, Cause.ASSUMPTION_VIOLATED, no_precondition),
        ("NIM_WIDE", EXACT_NIM, Cause.BUDGET_EXHAUSTED, ALL_PROBES),
        ("SUB12", EXACT_SUB, Cause.TRUE_REFUTATION, ALL_PROBES),
    ]
    return DiagnosisWorld(
        world_id="DW4_WITHHELD_PROBES_HOSTILE",
        hostile=True,
        tests=(
            "on seven of these nine episodes the available probes provably cannot "
            "single out a cause and the only correct verdict is CANNOT_IDENTIFY; the "
            "last two are identifiable, so an arm cannot pass by refusing everything"
        ),
        episodes=tuple(
            _episode(
                case_id=f"DW4-{i:02d}",
                cause=cause,
                scope_key=scope_key,
                checker_id=checker,
                index=i,
                available=available,
            )
            for i, (scope_key, checker, cause, available) in enumerate(plan)
        ),
        notes=(
            "the control battery is available in every episode here, so a scope "
            "memory can pin the checker's soundness but can never pin more than the "
            "episode's own probes would have; the targets are therefore well defined "
            "independently of what an arm remembers"
        ),
    )


def _dw5() -> DiagnosisWorld:
    """The drawn sequence: order and causes derive from the commitment."""
    pairs = [
        ("SUB123", EXACT_SUB),
        ("SUB123", SUB_DUAL),
        ("NIM_WIDE", NIM_DUAL),
        ("NIM_BINARY", NIM_DUAL),
    ]
    rng = random.Random(COMMITMENT.stream("dw5-task-sequence") % (2**63))
    slots = [pair for pair in pairs for _ in range(5)]
    rng.shuffle(slots)
    weighted = [(c, CAUSE_PRIOR[c]) for c in CAUSE_ORDER]
    episodes = []
    for i, (scope_key, checker) in enumerate(slots):
        sound = CHECKER_SOUNDNESS[(checker, scope_key)]
        pool = [
            (c, w)
            for c, w in weighted
            if not (c is Cause.EVALUATOR_DEFECT and sound)
        ]
        cause = rng.choices([c for c, _ in pool], weights=[w for _, w in pool])[0]
        episodes.append(
            _episode(
                case_id=f"DW5-{i:02d}",
                cause=cause,
                scope_key=scope_key,
                checker_id=checker,
                index=i,
            )
        )
    return DiagnosisWorld(
        world_id="DW5_COMMITMENT_DRAWN_SEQUENCE",
        hostile=False,
        tests=(
            "twenty episodes over four (checker, scope) pairs in an order no author "
            "chose after seeing an outcome; two pairs share the checker id "
            "sub12_table_applied_to_nim across a soundness boundary, so the "
            "over-generalisation hostile is present here too"
        ),
        episodes=tuple(episodes),
        notes=(
            "the causes are drawn from the registered prior with EVALUATOR_DEFECT "
            "suppressed in sound scopes, so the realised distribution over this "
            "world is not the registered prior and the receipt reports both"
        ),
    )


WORLDS: tuple[DiagnosisWorld, ...] = (_dw1(), _dw2(), _dw3(), _dw4(), _dw5())


def world_by_id(world_id: str) -> DiagnosisWorld:
    for world in WORLDS:
        if world.world_id == world_id:
            return world
    raise KeyError(world_id)


def cause_counts(worlds: Sequence[DiagnosisWorld] = WORLDS) -> dict[str, int]:
    """The realised cause distribution over every registered episode."""
    counts = {c.name: 0 for c in CAUSE_ORDER}
    for world in worlds:
        for episode in world.episodes:
            counts[episode.true_cause.name] += 1
    return counts


def target_counts(worlds: Sequence[DiagnosisWorld] = WORLDS) -> dict[str, int]:
    """The realised *target* distribution, which includes honest refusals."""
    counts = {c.name: 0 for c in CAUSE_ORDER}
    counts[Cause.CANNOT_IDENTIFY.name] = 0
    for world in worlds:
        for episode in world.episodes:
            counts[episode.target.name] += 1
    return counts


def constant_predictor_baseline(
    worlds: Sequence[DiagnosisWorld] = WORLDS,
) -> dict:
    """What a policy that always answers the same thing would score.

    Reported explicitly and early, because on a skewed cause distribution a
    constant predictor can look like a diagnosis policy.  The comparison is made
    against the *targets*, since that is what every arm is scored on.
    """
    counts = target_counts(worlds)
    total = sum(counts.values())
    best = max(counts.items(), key=lambda kv: (kv[1], kv[0]))
    return {
        "target_counts": counts,
        "episodes": total,
        "best_constant_answer": best[0],
        "best_constant_accuracy": best[1] / total if total else 0.0,
    }


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Score:
    """Diagnosis columns, cost columns and downstream columns, never summed.

    The columns trade against each other on purpose.  ``probe_cost`` buys
    ``correct``; ``correct_cannot_identify`` is bought by giving up
    ``correct`` on episodes an arm could have guessed right; and the downstream
    columns are what the diagnosis was *for*.  Collapsing them into one number
    would let an arm buy any one of them with any other, which is exactly the
    trade this experiment exists to display.
    """

    world_id: str
    arm: str
    episodes: int
    correct: int
    probe_cost: int
    probes_bought: int
    cost_curve: tuple[int, ...]
    per_cause_correct: tuple[tuple[str, int, int], ...]
    confusion: tuple[tuple[str, str, int], ...]
    correct_cannot_identify: int
    missed_cannot_identify: int
    false_cannot_identify: int
    over_generalisations: int
    reused_facts: int
    downstream_queries: int
    wasted_work_avoided: int
    repeated_wasted_work: int
    false_exclusions: int
    missed_reopenings: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.episodes if self.episodes else 0.0

    def as_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "arm": self.arm,
            "episodes": self.episodes,
            "correct": self.correct,
            "accuracy": round(self.accuracy, 4),
            "probe_cost": self.probe_cost,
            "probes_bought": self.probes_bought,
            "cost_curve": list(self.cost_curve),
            "per_cause_correct": [
                {"target": t, "correct": c, "episodes": n}
                for t, c, n in self.per_cause_correct
            ],
            "confusion": [
                {"target": t, "verdict": v, "count": n} for t, v, n in self.confusion
            ],
            "correct_cannot_identify": self.correct_cannot_identify,
            "missed_cannot_identify": self.missed_cannot_identify,
            "false_cannot_identify": self.false_cannot_identify,
            "over_generalisations": self.over_generalisations,
            "reused_facts": self.reused_facts,
            "downstream_queries": self.downstream_queries,
            "wasted_work_avoided": self.wasted_work_avoided,
            "repeated_wasted_work": self.repeated_wasted_work,
            "false_exclusions": self.false_exclusions,
            "missed_reopenings": self.missed_reopenings,
        }


def run(world: DiagnosisWorld, make_arm: Callable[[], DiagnosisArm]) -> Score:
    """Play one world against one freshly constructed arm.

    Every arm sees the identical episode stream in the identical order with the
    identical probes on offer at the identical prices, and every arm's
    conclusions are filed in the identical unmodified ``failure.FailureStore``.
    The only things that vary between arms are which probes they buy and what
    they carry between episodes.
    """
    arm = make_arm()
    store = FailureStore()
    correct = 0
    cost = 0
    probes_bought = 0
    curve: list[int] = []
    confusion: dict[tuple[str, str], int] = {}
    per_cause: dict[str, list[int]] = {}
    correct_refusals = 0
    missed_refusals = 0
    false_refusals = 0
    over_generalisations = 0
    reused = 0
    downstream_queries = 0
    avoided = 0
    repeated = 0
    false_exclusions = 0
    missed_reopenings = 0

    for event in world.script:
        if isinstance(event, Episode):
            bench = event.bench()
            result = arm.diagnose(bench)
            if bench.spent != result.cost:
                raise AssertionError(
                    f"{arm.name} reported cost {result.cost} but the bench charged "
                    f"{bench.spent} on {event.case.case_id}"
                )
            cost += bench.spent
            probes_bought += len(bench.probes_run)
            curve.append(cost)
            reused += len(result.reused)

            target = event.target
            confusion[(target.name, result.verdict.name)] = (
                confusion.get((target.name, result.verdict.name), 0) + 1
            )
            slot = per_cause.setdefault(target.name, [0, 0])
            slot[1] += 1
            if result.verdict is target:
                correct += 1
                slot[0] += 1
            if target is Cause.CANNOT_IDENTIFY:
                if result.refused:
                    correct_refusals += 1
                else:
                    missed_refusals += 1
            elif result.refused:
                false_refusals += 1
            if result.verdict is Cause.EVALUATOR_DEFECT and event.checker_sound:
                over_generalisations += 1

            record_diagnosis(store, event.case, result.verdict)
        elif isinstance(event, RegimeChange):
            store.reopen(event.changed)
        else:
            downstream_queries += 1
            blocked = store.excluded(event.method, event.assumptions)
            if event.kind is QueryKind.MUST_BLOCK:
                if blocked:
                    avoided += event.work_if_attempted
                else:
                    repeated += event.work_if_attempted
            elif event.kind is QueryKind.MUST_NOT_BLOCK:
                if blocked:
                    false_exclusions += 1
            else:
                if blocked:
                    missed_reopenings += 1

    return Score(
        world_id=world.world_id,
        arm=arm.name,
        episodes=len(world.episodes),
        correct=correct,
        probe_cost=cost,
        probes_bought=probes_bought,
        cost_curve=tuple(curve),
        per_cause_correct=tuple(
            (name, per_cause[name][0], per_cause[name][1])
            for name in sorted(per_cause)
        ),
        confusion=tuple(
            (t, v, n) for (t, v), n in sorted(confusion.items())
        ),
        correct_cannot_identify=correct_refusals,
        missed_cannot_identify=missed_refusals,
        false_cannot_identify=false_refusals,
        over_generalisations=over_generalisations,
        reused_facts=reused,
        downstream_queries=downstream_queries,
        wasted_work_avoided=avoided,
        repeated_wasted_work=repeated,
        false_exclusions=false_exclusions,
        missed_reopenings=missed_reopenings,
    )


def scoreboard(
    arms: dict[str, Callable[[], DiagnosisArm]],
    worlds: Sequence[DiagnosisWorld] = WORLDS,
) -> dict[str, Score]:
    """Aggregate every arm over every world, columns summed and never combined."""
    out: dict[str, Score] = {}
    for name, factory in arms.items():
        rows = [run(world, factory) for world in worlds]
        confusion: dict[tuple[str, str], int] = {}
        per_cause: dict[str, list[int]] = {}
        curve: list[int] = []
        running = 0
        for row in rows:
            for t, v, n in row.confusion:
                confusion[(t, v)] = confusion.get((t, v), 0) + n
            for t, c, n in row.per_cause_correct:
                slot = per_cause.setdefault(t, [0, 0])
                slot[0] += c
                slot[1] += n
            for point in row.cost_curve:
                curve.append(running + point)
            running = curve[-1] if curve else running
        out[name] = Score(
            world_id="ALL",
            arm=name,
            episodes=sum(r.episodes for r in rows),
            correct=sum(r.correct for r in rows),
            probe_cost=sum(r.probe_cost for r in rows),
            probes_bought=sum(r.probes_bought for r in rows),
            cost_curve=tuple(curve),
            per_cause_correct=tuple(
                (name_, per_cause[name_][0], per_cause[name_][1])
                for name_ in sorted(per_cause)
            ),
            confusion=tuple((t, v, n) for (t, v), n in sorted(confusion.items())),
            correct_cannot_identify=sum(r.correct_cannot_identify for r in rows),
            missed_cannot_identify=sum(r.missed_cannot_identify for r in rows),
            false_cannot_identify=sum(r.false_cannot_identify for r in rows),
            over_generalisations=sum(r.over_generalisations for r in rows),
            reused_facts=sum(r.reused_facts for r in rows),
            downstream_queries=sum(r.downstream_queries for r in rows),
            wasted_work_avoided=sum(r.wasted_work_avoided for r in rows),
            repeated_wasted_work=sum(r.repeated_wasted_work for r in rows),
            false_exclusions=sum(r.false_exclusions for r in rows),
            missed_reopenings=sum(r.missed_reopenings for r in rows),
        )
    return out
