"""The registered failure worlds over the subtraction and Nim families.

Seven worlds: two that a competent failure memory must simply get right, and
five hostiles built to break a specific wrong way of remembering.  Every world's
verdicts are true **by construction**, not by adjudication.  The construction is
always the same: pick two rules from ``games.py`` and ``methods.py`` whose exact
agreement set is computable, then place the boundary of that agreement set
between the failure and the query.  The disagreement sets are computed at import
time and exported as :data:`GROUND_TRUTH`, so a reviewer can recheck the label
of every query with three lines of arithmetic and never has to trust this file.

The two rule pairs carrying all seven worlds:

``grundy_mod3`` versus ``grundy_mod4``
    ``SUB(1,2)`` has Grundy sequence ``0,1,2,0,1,2,…`` and ``SUB(1,2,3)`` has
    ``0,1,2,3,0,1,2,3,…``.  So ``n mod 3 == 0`` is *exactly* the P-position rule
    of ``SUB(1,2)`` and *exactly wrong* infinitely often on ``SUB(1,2,3)``, and
    ``n mod 4 == 0`` is the mirror image.  A method that is right in one regime
    and demonstrably wrong in the other is what a scope-keyed exclusion is for.

``xor_combiner`` versus ``sum_mod_2_combiner``
    ``methods.py`` registers ``SUM_MOD_2`` in ``XOR_LOOKALIKES_ON_BINARY_VALUES``,
    the combiners that agree with ``XOR`` whenever every per-heap Grundy value
    lies in ``{0, 1}``.  So on ``NIM(2)`` with heaps drawn from ``{0, 1}`` the two
    are extensionally identical, and ``(1, 3)`` separates them.  That gives a
    probe set which *provably* cannot discriminate, which is what the
    non-identifying-experiment hostile needs and what an ordinary timeout cannot
    supply.

What each world is testing:

``FW1`` a genuine refutation in one regime must transfer to a *fresh* task in the
        same regime.  A task-keyed memory cannot make this transfer, which is
        attack A10 taken from the front.
``FW2`` the regime changes back and the excluded method must be reopened and
        must succeed.  This is CL-R4 ``scope_recovery``: a failure is a lease.
``FW3`` **hostile.** Two failures under the identical surface label "no solution
        found", one a checker refutation and one a spent budget.  Only the first
        may exclude.  If a policy reads labels rather than causes it cannot pass.
``FW4`` **hostile.** Same method, changed assumptions.  A refutation obtained
        with heaps up to four says nothing about heaps in ``{0, 1}``, where the
        method is provably correct.
``FW5`` **hostile.** A probe set on which the rival hypotheses provably agree.
        Failing to discriminate there is a fact about the probes; excluding
        ``XOR`` -- the true rule -- on that basis is the worst error available.
``FW6`` **hostile.** A defective checker reports "refuted by checker" against a
        method that is exactly correct.  The label is identical to FW1's; only
        the diagnosed cause differs.
``FW7`` **hostile, "broken shut".** Exclude, reopen, re-earn the exclusion,
        reopen again.  A method excluded once must never become permanently
        unreachable.  A policy that treats exclusion as deletion passes the
        first half and fails the second.

Scoring is deliberately four-dimensional and is never collapsed to a scalar.
Avoiding repeated work and avoiding false exclusions trade against each other,
and a single number would let a policy buy one with the other -- which is
exactly the trade the whole exercise is trying to make visible.  ``no_memory``
scores a perfect zero on all three error columns while avoiding no work at all;
it is safe and useless, and any scalar score that ranked it well would be the
wrong score.

Registered before any protected outcome; the draw derives from the
pre-registration commitment in ``prereg.py``.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

from failure import (
    Assumption,
    FailureCause,
    FailureKnowledge,
    Observation,
    ResourceBound,
    Success,
)
from games import MultiHeapGame, SubtractionGame, Work
from methods import COMBINERS, XOR_LOOKALIKES_ON_BINARY_VALUES

__all__ = [
    "QueryKind",
    "Attempt",
    "RegimeChange",
    "Query",
    "FailureWorld",
    "Policy",
    "Score",
    "run",
    "scoreboard",
    "WORLDS",
    "world_by_id",
    "GROUND_TRUTH",
]


# --------------------------------------------------------------------------
# ground truth, computed rather than asserted
# --------------------------------------------------------------------------

HORIZON = 40

SUB12 = SubtractionGame((1, 2))
SUB123 = SubtractionGame((1, 2, 3))
NIM2 = MultiHeapGame.nim(2, 4)

_SUB12_TABLE = SUB12.grundy_upto(HORIZON)
_SUB123_TABLE = SUB123.grundy_upto(HORIZON)


def _mod3_says_p(n: int) -> bool:
    return n % 3 == 0


def _mod4_says_p(n: int) -> bool:
    return n % 4 == 0


def _disagreements(rule, table) -> tuple[int, ...]:
    return tuple(n for n in range(HORIZON + 1) if rule(n) != (table[n] == 0))


MOD3_WRONG_ON_SUB123 = _disagreements(_mod3_says_p, _SUB123_TABLE)
MOD3_WRONG_ON_SUB12 = _disagreements(_mod3_says_p, _SUB12_TABLE)
MOD4_WRONG_ON_SUB123 = _disagreements(_mod4_says_p, _SUB123_TABLE)
MOD4_WRONG_ON_SUB12 = _disagreements(_mod4_says_p, _SUB12_TABLE)

_NIM_WIDE_POSITIONS = tuple((a, b) for a in range(5) for b in range(5))
_NIM_BINARY_POSITIONS = tuple((a, b) for a in range(2) for b in range(2))

_XOR = COMBINERS["XOR"]
_SUM_MOD_2 = COMBINERS["SUM_MOD_2"]


def _combiner_disagreements(positions) -> tuple[tuple[int, ...], ...]:
    return tuple(p for p in positions if (_XOR(p) == 0) != (_SUM_MOD_2(p) == 0))


SUM_MOD_2_WRONG_WIDE = _combiner_disagreements(_NIM_WIDE_POSITIONS)
SUM_MOD_2_WRONG_BINARY = _combiner_disagreements(_NIM_BINARY_POSITIONS)


def _require(condition: bool, message: str) -> None:
    """Fail loudly at import if a world's premise is not actually true.

    Used instead of a bare ``assert`` so the checks survive ``python -O``.  A
    world whose ground truth stopped holding must not quietly become a world
    that tests nothing.
    """
    if not condition:
        raise AssertionError("failure-world ground truth violated: " + message)


_require(MOD3_WRONG_ON_SUB12 == (), "n mod 3 must be exactly the P-rule of SUB(1,2)")
_require(MOD3_WRONG_ON_SUB123 != (), "n mod 3 must be refutable on SUB(1,2,3)")
_require(MOD4_WRONG_ON_SUB123 == (), "n mod 4 must be exactly the P-rule of SUB(1,2,3)")
_require(MOD4_WRONG_ON_SUB12 != (), "n mod 4 must be refutable on SUB(1,2)")
_require(SUM_MOD_2_WRONG_BINARY == (), "SUM_MOD_2 must equal XOR on heaps in {0,1}")
_require((1, 3) in SUM_MOD_2_WRONG_WIDE, "(1,3) must separate SUM_MOD_2 from XOR")
_require(
    "SUM_MOD_2" in XOR_LOOKALIKES_ON_BINARY_VALUES,
    "methods.py must still register SUM_MOD_2 as a XOR lookalike on binary values",
)
_require(
    all(
        (COMBINERS[name](p) == 0) == (_XOR(p) == 0)
        for name in XOR_LOOKALIKES_ON_BINARY_VALUES
        for p in _NIM_BINARY_POSITIONS
    ),
    "every registered lookalike must in fact agree with XOR on heaps in {0,1}",
)

#: Exported so the tests can restate every world's premise independently of the
#: world objects, and so a reader can check the claims without running anything.
GROUND_TRUTH = {
    "sub12_grundy_prefix": tuple(_SUB12_TABLE[:12]),
    "sub123_grundy_prefix": tuple(_SUB123_TABLE[:12]),
    "mod3_wrong_on_sub123": MOD3_WRONG_ON_SUB123,
    "mod3_wrong_on_sub12": MOD3_WRONG_ON_SUB12,
    "mod4_wrong_on_sub123": MOD4_WRONG_ON_SUB123,
    "mod4_wrong_on_sub12": MOD4_WRONG_ON_SUB12,
    "sum_mod_2_wrong_wide": SUM_MOD_2_WRONG_WIDE,
    "sum_mod_2_wrong_binary": SUM_MOD_2_WRONG_BINARY,
}


# ---- exact work counters, so "wasted work" is counted and not invented ----


def _sub_work(game: SubtractionGame, n: int) -> int:
    work = Work()
    game.grundy_upto(n, work=work)
    return work.total


def _nim_work(game: MultiHeapGame, position: Sequence[int]) -> int:
    work = Work()
    game.is_p_position(position, work=work)
    return work.total


# --------------------------------------------------------------------------
# assumption contexts
# --------------------------------------------------------------------------

EXACT_CHECKER = Assumption("checker", "grundy_dp_exact")
DEFECTIVE_CHECKER = Assumption("checker", "sub12_table_misapplied")
SG_CHECKER = Assumption("checker", "sprague_grundy_exact")

#: the ``SUB(1,2)`` regime
A_S1 = (Assumption("move_set", "1,2"), Assumption("play", "normal"), EXACT_CHECKER)
#: the ``SUB(1,2,3)`` regime
A_S2 = (Assumption("move_set", "1,2,3"), Assumption("play", "normal"), EXACT_CHECKER)
#: the ``SUB(1,2,3)`` regime as seen through a broken checker
A_S2_BAD_CHECKER = (
    Assumption("move_set", "1,2,3"),
    Assumption("play", "normal"),
    DEFECTIVE_CHECKER,
)
#: ``NIM(2)`` with heaps up to four -- ``XOR`` and ``SUM_MOD_2`` separate here
A_NIM_WIDE = (
    Assumption("family", "NIM(2)"),
    Assumption("heap_values", "0..4"),
    SG_CHECKER,
)
#: ``NIM(2)`` with heaps in ``{0,1}`` -- the two combiners provably agree here
A_NIM_BINARY = (
    Assumption("family", "NIM(2)"),
    Assumption("heap_values", "0..1"),
    SG_CHECKER,
)

NO_BUDGET_PRESSURE = ResourceBound(
    expansions=4096, checker_calls=4096, spent_expansions=64, spent_checker_calls=8
)


# --------------------------------------------------------------------------
# world scripts
# --------------------------------------------------------------------------


class QueryKind(enum.Enum):
    """What the ground truth says the policy should answer, and why it matters.

    Each kind names the specific error a wrong answer is, so the score columns
    are not a matter of interpretation after the fact.
    """

    #: the method is genuinely wrong here; not blocking repeats known-wasted work
    MUST_BLOCK = "MUST_BLOCK"
    #: the method is live here; blocking it is a false exclusion
    MUST_NOT_BLOCK = "MUST_NOT_BLOCK"
    #: the method was excluded and its reopen condition has since fired; blocking
    #: it is a missed reopening, and leaves it unreachable
    MUST_REOPEN = "MUST_REOPEN"


@dataclass(frozen=True)
class Attempt:
    """One failed attempt presented to the policy, with its diagnosis attached.

    The diagnosis is part of the world, not part of the policy: every policy
    receives the identical, correctly diagnosed record.  This is on purpose.
    The question under test is what a policy *does* with a correct diagnosis,
    not whether it can produce one -- charging the parents for a diagnosis they
    never claimed to make would be a strawman.
    """

    knowledge: FailureKnowledge
    note: str = ""


@dataclass(frozen=True)
class RegimeChange:
    """An assumption changed value between episodes.

    Announced to every policy identically.  A policy is free to ignore it; that
    is what a task-ID blacklist does, and the score records the consequence.
    """

    changed: str
    to_value: str
    note: str = ""


@dataclass(frozen=True)
class Query:
    """Would the policy attempt this method on this task, under these assumptions?

    ``work_if_attempted`` is the exact ``games.Work`` total the attempt would
    burn, counted by running the real procedure at import time.  It is the
    quantity a correct exclusion saves and a false exclusion is spending its
    credibility to save.
    """

    method: str
    task: str
    assumptions: tuple[Assumption, ...]
    kind: QueryKind
    work_if_attempted: int
    ground_truth: str


Event = Attempt | RegimeChange | Query


@dataclass(frozen=True)
class FailureWorld:
    """One registered world: a script of episodes with by-construction verdicts."""

    world_id: str
    hostile: bool
    script: tuple[Event, ...]
    tests: str
    notes: str = ""

    @property
    def queries(self) -> tuple[Query, ...]:
        return tuple(e for e in self.script if isinstance(e, Query))

    @property
    def available_work_saving(self) -> int:
        """Total work a policy could avoid here by blocking exactly what it should."""
        return sum(q.work_if_attempted for q in self.queries if q.kind is QueryKind.MUST_BLOCK)


class Policy(Protocol):
    """The interface every arm implements, governed and parent alike.

    Note what ``blocked`` is given: a method, an assumption context and a task.
    The governed store ignores the task because its key cannot express one; the
    transcript parent uses nothing else.  Handing both the same three arguments
    is what makes the comparison fair -- neither arm is starved of information
    the other has.
    """

    name: str

    def record(self, knowledge: FailureKnowledge) -> None: ...

    def blocked(
        self, method: str, assumptions: Sequence[Assumption], task: str
    ) -> bool: ...

    def regime_change(self, changed: str) -> set[str]: ...


# --------------------------------------------------------------------------
# helpers for building the records
# --------------------------------------------------------------------------


def _sub_observation(n: int, method_says: bool, table: Sequence[int]) -> Observation:
    return Observation(
        position=f"n={n}", method_says=method_says, checker_says=table[n] == 0
    )


def _nim_observation(position: tuple[int, ...], method_says: bool) -> Observation:
    return Observation(
        position=str(position), method_says=method_says, checker_says=_XOR(position) == 0
    )


# --------------------------------------------------------------------------
# FW1: a scoped refutation must transfer to a fresh task in the same regime
# --------------------------------------------------------------------------

_FW1_WITNESS = MOD3_WRONG_ON_SUB123[0]          # 3
_FW1_FRESH = MOD3_WRONG_ON_SUB123[4]            # a different heap, same regime

FW1 = FailureWorld(
    world_id="FW1_SCOPED_REFUTATION_TRANSFERS",
    hostile=False,
    tests=(
        "a genuine refutation of grundy_mod3 in the SUB(1,2,3) regime must block "
        "a fresh, unseen task in that same regime, and must leave grundy_mod4 alone"
    ),
    script=(
        Attempt(
            FailureKnowledge.build(
                attempted_method="grundy_mod3",
                task=f"T[n={_FW1_WITNESS}]",
                representation="heap_size",
                assumptions=A_S2,
                evidence=(
                    _sub_observation(
                        _FW1_WITNESS, _mod3_says_p(_FW1_WITNESS), _SUB123_TABLE
                    ),
                ),
                resource_bound=NO_BUDGET_PRESSURE,
                observed_failure="no solution found",
                diagnosed_responsibility=FailureCause.REFUTED_BY_CHECKER,
                still_live_alternatives=("grundy_mod4", "grundy_dp_exhaustive"),
                preserved_successes=(
                    Success(
                        method="grundy_mod3",
                        assumptions=A_S1,
                        task="T[n=9]",
                        note="the rule was learned here and is exactly right here",
                    ),
                ),
                scope="SUB(1,2,3), one heap, n <= 40",
                reopen_conditions=("move_set changes", "play convention changes"),
            ),
            note="the checker exhibits a position where the rule's verdict is wrong",
        ),
        Query(
            method="grundy_mod3",
            task=f"T[n={_FW1_WITNESS}]",
            assumptions=A_S2,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_sub_work(SUB123, _FW1_WITNESS),
            ground_truth="the same task that was just refuted; retrying is pure waste",
        ),
        Query(
            method="grundy_mod3",
            task=f"T[n={_FW1_FRESH}]",
            assumptions=A_S2,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_sub_work(SUB123, _FW1_FRESH),
            ground_truth=(
                f"n={_FW1_FRESH} is in the computed disagreement set, so the rule is "
                "wrong here too; this task was never attempted, which is the whole point"
            ),
        ),
        Query(
            method="grundy_mod4",
            task=f"T[n={_FW1_FRESH}]",
            assumptions=A_S2,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_sub_work(SUB123, _FW1_FRESH),
            ground_truth="n mod 4 is exactly the P-rule of SUB(1,2,3); it is the answer",
        ),
    ),
    notes=(
        "the discriminating query is the second one: it is a task no attempt has "
        "ever touched, so only a memory keyed on something other than task identity "
        "can reach it"
    ),
)


# --------------------------------------------------------------------------
# FW2: the regime changes back and the exclusion must be reopened
# --------------------------------------------------------------------------

_FW2_TASK = "T[n=9]"                             # 9 mod 3 == 0, and SUB(1,2) agrees
_require(
    9 in MOD3_WRONG_ON_SUB123 and 9 not in MOD3_WRONG_ON_SUB12,
    "T[n=9] must be refuting under SUB(1,2,3) and correct under SUB(1,2)",
)

FW2 = FailureWorld(
    world_id="FW2_REGIME_RESTORED_MUST_REOPEN",
    hostile=False,
    tests=(
        "after the move set reverts to SUB(1,2) the excluded rule must be reachable "
        "again and must succeed; this is CL-R4 scope_recovery and protocol attack A10"
    ),
    script=(
        Attempt(
            FailureKnowledge.build(
                attempted_method="grundy_mod3",
                task=_FW2_TASK,
                representation="heap_size",
                assumptions=A_S2,
                evidence=(_sub_observation(9, _mod3_says_p(9), _SUB123_TABLE),),
                resource_bound=NO_BUDGET_PRESSURE,
                observed_failure="no solution found",
                diagnosed_responsibility=FailureCause.REFUTED_BY_CHECKER,
                still_live_alternatives=("grundy_mod4",),
                scope="SUB(1,2,3), one heap, n <= 40",
                reopen_conditions=("move_set changes",),
            )
        ),
        Query(
            method="grundy_mod3",
            task=_FW2_TASK,
            assumptions=A_S2,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_sub_work(SUB123, 9),
            ground_truth="still the refuted regime",
        ),
        RegimeChange(
            changed="move_set",
            to_value="1,2",
            note="the family reverts; every exclusion resting on the move set loses its warrant",
        ),
        Query(
            method="grundy_mod3",
            task=_FW2_TASK,
            assumptions=A_S1,
            kind=QueryKind.MUST_REOPEN,
            work_if_attempted=_sub_work(SUB12, 9),
            ground_truth=(
                "n mod 3 has no disagreement with SUB(1,2) anywhere in scope; the rule "
                "is exactly correct and blocking it forfeits the answer"
            ),
        ),
    ),
    notes=(
        "the task identity is deliberately held fixed across the regime change, so a "
        "task-keyed memory blocks precisely the episode the protocol requires to succeed.  "
        "Note what the MUST_REOPEN query alone does *not* establish: for any policy that "
        "keys on the assumption set, the query is already unblocked because the key "
        "differs, whether or not the policy retired anything.  The retirement itself is "
        "a separate obligation and is asserted directly against the store in "
        "test_failure.py rather than inferred from this score"
    ),
)


# --------------------------------------------------------------------------
# FW3 (hostile): one failure label, two root causes
# --------------------------------------------------------------------------

_FW3_DP_TARGET = 40
_FW3_TRUE_COST = _sub_work(SUB123, _FW3_DP_TARGET)
_FW3_BUDGET = 8
_require(
    _FW3_TRUE_COST > _FW3_BUDGET,
    "the exhaustive DP must genuinely cost more than the budget it was given",
)

FW3 = FailureWorld(
    world_id="FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE",
    hostile=True,
    tests=(
        "two failures reported under the identical string 'no solution found': one is "
        "a checker refutation and may exclude, one is a spent budget and may not"
    ),
    script=(
        Attempt(
            FailureKnowledge.build(
                attempted_method="grundy_mod3",
                task="T[n=4]",
                representation="heap_size",
                assumptions=A_S2,
                evidence=(_sub_observation(4, _mod3_says_p(4), _SUB123_TABLE),),
                resource_bound=NO_BUDGET_PRESSURE,
                observed_failure="no solution found",
                diagnosed_responsibility=FailureCause.REFUTED_BY_CHECKER,
                still_live_alternatives=("grundy_mod4", "grundy_dp_exhaustive"),
                scope="SUB(1,2,3), one heap, n <= 40",
                reopen_conditions=("move_set changes",),
            ),
            note="genuinely wrong: n=4 is a P-position of SUB(1,2,3) and 4 mod 3 != 0",
        ),
        Attempt(
            FailureKnowledge.build(
                attempted_method="grundy_dp_exhaustive",
                task=f"T[n={_FW3_DP_TARGET}]",
                representation="heap_size",
                assumptions=A_S2,
                evidence=(),
                resource_bound=ResourceBound(
                    expansions=_FW3_BUDGET,
                    checker_calls=64,
                    spent_expansions=_FW3_BUDGET,
                    spent_checker_calls=0,
                ),
                observed_failure="no solution found",
                diagnosed_responsibility=FailureCause.BUDGET_EXHAUSTED,
                still_live_alternatives=("grundy_dp_exhaustive", "grundy_mod4"),
                scope="SUB(1,2,3), one heap, n <= 40",
                reopen_conditions=("budget increases",),
            ),
            note=(
                f"the exact DP needs {_FW3_TRUE_COST} counted units and was given "
                f"{_FW3_BUDGET}; nothing whatever was learned about its correctness"
            ),
        ),
        Query(
            method="grundy_mod3",
            task="T[n=16]",
            assumptions=A_S2,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_sub_work(SUB123, 16),
            ground_truth="16 is in the computed disagreement set of n mod 3 with SUB(1,2,3)",
        ),
        Query(
            method="grundy_dp_exhaustive",
            task="T[n=16]",
            assumptions=A_S2,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_sub_work(SUB123, 16),
            ground_truth=(
                "the exhaustive DP is games.py's own exact procedure; it is correct on "
                "every position and the only thing wrong with the earlier attempt was "
                "the number it was allowed to spend"
            ),
        ),
    ),
    notes=(
        "a policy that keys on the reported failure string cannot separate these two "
        "records at all; a policy that keys on the diagnosed cause separates them "
        "without looking at anything else"
    ),
)


# --------------------------------------------------------------------------
# FW4 (hostile): same method, changed assumptions
# --------------------------------------------------------------------------

FW4 = FailureWorld(
    world_id="FW4_HOSTILE_CHANGED_ASSUMPTIONS",
    hostile=True,
    tests=(
        "sum_mod_2_combiner is refuted with heaps up to four and is provably identical "
        "to XOR with heaps in {0,1}; the exclusion must not follow it into the second context"
    ),
    script=(
        Attempt(
            FailureKnowledge.build(
                attempted_method="sum_mod_2_combiner",
                task="T[(1,3)]",
                representation="heap_tuple",
                assumptions=A_NIM_WIDE,
                evidence=(_nim_observation((1, 3), _SUM_MOD_2((1, 3)) == 0),),
                resource_bound=NO_BUDGET_PRESSURE,
                observed_failure="refuted by checker at (1,3)",
                diagnosed_responsibility=FailureCause.REFUTED_BY_CHECKER,
                still_live_alternatives=("xor_combiner",),
                scope="NIM(2), heaps in 0..4",
                reopen_conditions=("heap_values changes", "family changes"),
            ),
            note="(1,3) is in the computed separation set of SUM_MOD_2 from XOR",
        ),
        Query(
            method="sum_mod_2_combiner",
            task="T[(2,4)]",
            assumptions=A_NIM_WIDE,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_nim_work(NIM2, (2, 4)),
            ground_truth="(2,4) is also in the separation set; the rule is wrong here too",
        ),
        Query(
            method="sum_mod_2_combiner",
            task="T[(1,1)]",
            assumptions=A_NIM_BINARY,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_nim_work(NIM2, (1, 1)),
            ground_truth=(
                "methods.py registers SUM_MOD_2 as a XOR lookalike on values in {0,1}; "
                "the computed disagreement set over those positions is empty, so the "
                "method is exactly correct in this assumption context"
            ),
        ),
        Query(
            method="xor_combiner",
            task="T[(2,4)]",
            assumptions=A_NIM_WIDE,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_nim_work(NIM2, (2, 4)),
            ground_truth="XOR is the Sprague-Grundy answer and was never the method that failed",
        ),
    ),
    notes=(
        "no regime-change event occurs here: the second context is simply a different "
        "assumption set, so this world tests the exclusion *key* rather than the "
        "reopening mechanism"
    ),
)


# --------------------------------------------------------------------------
# FW5 (hostile): a non-identifying experiment mistaken for a refutation
# --------------------------------------------------------------------------

_FW5_EVIDENCE = tuple(
    _nim_observation(p, _XOR(p) == 0) for p in _NIM_BINARY_POSITIONS
)
_require(
    not any(o.refutes for o in _FW5_EVIDENCE),
    "the non-identifying probe set must contain no refuting observation",
)

FW5 = FailureWorld(
    world_id="FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT",
    hostile=True,
    tests=(
        "the probe set was confined to positions where XOR and its registered "
        "lookalikes provably agree; failing to identify there is a fact about the "
        "probes and must exclude nothing"
    ),
    script=(
        Attempt(
            FailureKnowledge.build(
                attempted_method="xor_combiner",
                task="T[binary-probe-set]",
                representation="heap_tuple",
                assumptions=A_NIM_BINARY,
                evidence=_FW5_EVIDENCE,
                resource_bound=NO_BUDGET_PRESSURE,
                observed_failure="no solution found",
                diagnosed_responsibility=FailureCause.NON_IDENTIFYING_EXPERIMENT,
                still_live_alternatives=("xor_combiner", "sum_mod_2_combiner"),
                scope="NIM(2), heaps in 0..1",
                reopen_conditions=("heap_values changes",),
            ),
            note=(
                "the version space did not collapse and could not have: every probe in "
                "the set lies inside the agreement region of XOR and every one of its "
                "registered lookalikes"
            ),
        ),
        Query(
            method="xor_combiner",
            task="T[binary-probe-set]",
            assumptions=A_NIM_BINARY,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_nim_work(NIM2, (1, 1)),
            ground_truth=(
                "XOR is the true rule of NIM(2) everywhere; excluding it on the strength "
                "of a probe set that cannot discriminate is the most expensive error in "
                "the module"
            ),
        ),
        Query(
            method="sum_mod_2_combiner",
            task="T[binary-probe-set]",
            assumptions=A_NIM_BINARY,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_nim_work(NIM2, (1, 1)),
            ground_truth=(
                "the rival is also correct in this context, which is exactly why the "
                "experiment could not discriminate"
            ),
        ),
        Query(
            method="xor_combiner",
            task="T[(1,3)]",
            assumptions=A_NIM_WIDE,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_nim_work(NIM2, (1, 3)),
            ground_truth="the widened context is where the experiment should have been run",
        ),
    ),
    notes=(
        "the honest response to this failure is to widen the probe set, which is the "
        "L2_MORE_EVIDENCE reading in escalation.py; the wrong response is to conclude "
        "anything at all about the methods"
    ),
)


# --------------------------------------------------------------------------
# FW6 (hostile): an evaluator defect mistaken for a scientific failure
# --------------------------------------------------------------------------

_FW6_DEFECTIVE_VERDICT = _SUB12_TABLE[4] == 0    # the wrong table was consulted
_require(
    _FW6_DEFECTIVE_VERDICT != (_SUB123_TABLE[4] == 0),
    "the defective checker must actually disagree with the exact one at n=4",
)

FW6 = FailureWorld(
    world_id="FW6_HOSTILE_EVALUATOR_DEFECT",
    hostile=True,
    tests=(
        "the checker consulted the SUB(1,2) table while judging a SUB(1,2,3) position "
        "and reported 'refuted by checker' against grundy_mod4, which is the exact "
        "P-rule of SUB(1,2,3); the label matches FW1's and the cause does not"
    ),
    script=(
        Attempt(
            FailureKnowledge.build(
                attempted_method="grundy_mod4",
                task="T[n=4]",
                representation="heap_size",
                assumptions=A_S2_BAD_CHECKER,
                evidence=(
                    Observation(
                        position="n=4",
                        method_says=_mod4_says_p(4),
                        checker_says=_FW6_DEFECTIVE_VERDICT,
                    ),
                ),
                resource_bound=NO_BUDGET_PRESSURE,
                observed_failure="refuted by checker at n=4",
                diagnosed_responsibility=FailureCause.EVALUATOR_DEFECT,
                still_live_alternatives=("grundy_mod4",),
                scope="SUB(1,2,3), one heap, n <= 40",
                reopen_conditions=("checker changes",),
            ),
            note=(
                "the disagreement is real and the checker is the party that is wrong; "
                "the independence requirement of CL-D1(c) is what this violates"
            ),
        ),
        Query(
            method="grundy_mod4",
            task="T[n=4]",
            assumptions=A_S2_BAD_CHECKER,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_sub_work(SUB123, 4),
            ground_truth=(
                "the computed disagreement set of n mod 4 with SUB(1,2,3) is empty; the "
                "method is exactly correct and it is the checker that must be retired"
            ),
        ),
        Query(
            method="grundy_mod4",
            task="T[n=20]",
            assumptions=A_S2_BAD_CHECKER,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_sub_work(SUB123, 20),
            ground_truth="same rule, fresh task, still exactly correct",
        ),
        RegimeChange(
            changed="checker",
            to_value="grundy_dp_exact",
            note="the defect is repaired; any exclusion resting on the old checker loses its warrant",
        ),
        Query(
            method="grundy_mod4",
            task="T[n=20]",
            assumptions=A_S2,
            kind=QueryKind.MUST_NOT_BLOCK,
            work_if_attempted=_sub_work(SUB123, 20),
            ground_truth="with the checker repaired the rule verifies on every position in scope",
        ),
    ),
    notes=(
        "the two queries before the repair are the ones that discriminate: a policy that "
        "excludes on the checker's say-so has already destroyed the answer by then, and "
        "repairing the checker afterwards only limits the damage"
    ),
)


# --------------------------------------------------------------------------
# FW7 (hostile): broken shut
# --------------------------------------------------------------------------


def _mod3_refutation(task: str) -> FailureKnowledge:
    return FailureKnowledge.build(
        attempted_method="grundy_mod3",
        task=task,
        representation="heap_size",
        assumptions=A_S2,
        evidence=(_sub_observation(9, _mod3_says_p(9), _SUB123_TABLE),),
        resource_bound=NO_BUDGET_PRESSURE,
        observed_failure="no solution found",
        diagnosed_responsibility=FailureCause.REFUTED_BY_CHECKER,
        still_live_alternatives=("grundy_mod4",),
        scope="SUB(1,2,3), one heap, n <= 40",
        reopen_conditions=("move_set changes",),
    )


FW7 = FailureWorld(
    world_id="FW7_HOSTILE_BROKEN_SHUT",
    hostile=True,
    tests=(
        "exclude, reopen, re-earn the exclusion, reopen again; a method excluded once "
        "must never become permanently unreachable, and re-excluding it must still work"
    ),
    script=(
        Attempt(_mod3_refutation("T[n=9]")),
        Query(
            method="grundy_mod3",
            task="T[n=9]",
            assumptions=A_S2,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_sub_work(SUB123, 9),
            ground_truth="first exclusion, correctly earned",
        ),
        RegimeChange(changed="move_set", to_value="1,2"),
        Query(
            method="grundy_mod3",
            task="T[n=9]",
            assumptions=A_S1,
            kind=QueryKind.MUST_REOPEN,
            work_if_attempted=_sub_work(SUB12, 9),
            ground_truth="n mod 3 is exactly the P-rule of SUB(1,2); the door must open",
        ),
        RegimeChange(changed="move_set", to_value="1,2,3"),
        Attempt(
            _mod3_refutation("T[n=21]"),
            note="the exclusion is re-earned by a fresh refutation, not remembered",
        ),
        Query(
            method="grundy_mod3",
            task="T[n=33]",
            assumptions=A_S2,
            kind=QueryKind.MUST_BLOCK,
            work_if_attempted=_sub_work(SUB123, 33),
            ground_truth=(
                "33 is in the computed disagreement set; re-exclusion must transfer to "
                "fresh tasks exactly as the first one did"
            ),
        ),
        RegimeChange(changed="move_set", to_value="1,2"),
        Query(
            method="grundy_mod3",
            task="T[n=33]",
            assumptions=A_S1,
            kind=QueryKind.MUST_REOPEN,
            work_if_attempted=_sub_work(SUB12, 33),
            ground_truth="the second reopening; one-way doors would have shut here",
        ),
    ),
    notes=(
        "the cycle is the test.  A policy that scores well by deleting exclusions on "
        "any regime change fails the MUST_BLOCK query in the middle; a policy that "
        "scores well by never deleting them fails both MUST_REOPEN queries.  Only a "
        "lease with a stated expiry passes all four"
    ),
)


WORLDS: tuple[FailureWorld, ...] = (FW1, FW2, FW3, FW4, FW5, FW6, FW7)


def world_by_id(world_id: str) -> FailureWorld:
    for world in WORLDS:
        if world.world_id == world_id:
            return world
    raise KeyError(world_id)


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Score:
    """Four error columns and one benefit column.  Never summed into a scalar.

    ``wasted_work_avoided`` is a counted ``games.Work`` total, not a count of
    decisions, so a policy gets credit proportional to the work its correct
    exclusions actually saved.  The three error columns are counts, because a
    false exclusion's cost is the answer it forfeited and that is not
    commensurable with expansions.  Reporting them together and refusing to
    combine them is the point: the interesting policies differ by trading one
    column against another, and a scalar would hide precisely that.
    """

    world_id: str
    policy: str
    queries: int
    wasted_work_avoided: int
    repeated_wasted_work: int
    false_exclusions: int
    missed_reopenings: int
    broken_shut: int

    def as_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "policy": self.policy,
            "queries": self.queries,
            "wasted_work_avoided": self.wasted_work_avoided,
            "repeated_wasted_work": self.repeated_wasted_work,
            "false_exclusions": self.false_exclusions,
            "missed_reopenings": self.missed_reopenings,
            "broken_shut": self.broken_shut,
        }

    @property
    def error_columns(self) -> tuple[int, int, int]:
        """The three ways to be wrong, as a comparable triple."""
        return (self.false_exclusions, self.missed_reopenings, self.broken_shut)


def run(world: FailureWorld, make_policy: Callable[[], "Policy"]) -> Score:
    """Play one world against one freshly constructed policy.

    Every policy sees the identical event stream in the identical order, with
    the identical diagnoses attached.  Nothing about the world consults the
    policy's internals, and nothing about the scoring consults anything the
    policy could not have seen.
    """
    policy = make_policy()
    avoided = 0
    repeated = 0
    false_exclusions = 0
    missed = 0
    shut: set[str] = set()
    queries = 0

    for event in world.script:
        if isinstance(event, Attempt):
            policy.record(event.knowledge)
        elif isinstance(event, RegimeChange):
            policy.regime_change(event.changed)
        else:
            queries += 1
            blocked = policy.blocked(event.method, event.assumptions, event.task)
            if event.kind is QueryKind.MUST_BLOCK:
                if blocked:
                    avoided += event.work_if_attempted
                else:
                    repeated += event.work_if_attempted
            elif event.kind is QueryKind.MUST_NOT_BLOCK:
                if blocked:
                    false_exclusions += 1
            else:  # MUST_REOPEN
                if blocked:
                    missed += 1
                    shut.add(event.method)

    return Score(
        world_id=world.world_id,
        policy=policy.name,
        queries=queries,
        wasted_work_avoided=avoided,
        repeated_wasted_work=repeated,
        false_exclusions=false_exclusions,
        missed_reopenings=missed,
        broken_shut=len(shut),
    )


def scoreboard(
    policies: dict[str, Callable[[], "Policy"]],
    worlds: Sequence[FailureWorld] = WORLDS,
) -> dict[str, Score]:
    """Aggregate every policy over every world into one row each.

    The aggregate hides which world produced which error, so the per-world
    scores are what a report should actually print; this exists so a single
    table can be shown next to it without recomputing.
    """
    out: dict[str, Score] = {}
    for name, make in policies.items():
        totals = [run(world, make) for world in worlds]
        out[name] = Score(
            world_id="ALL",
            policy=name,
            queries=sum(s.queries for s in totals),
            wasted_work_avoided=sum(s.wasted_work_avoided for s in totals),
            repeated_wasted_work=sum(s.repeated_wasted_work for s in totals),
            false_exclusions=sum(s.false_exclusions for s in totals),
            missed_reopenings=sum(s.missed_reopenings for s in totals),
            broken_shut=sum(s.broken_shut for s in totals),
        )
    return out
