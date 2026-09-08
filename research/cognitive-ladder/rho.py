"""E7 --- the reuse-opportunity-density sweep: the world, the tasks and the certifier.

``ROOT_CAUSE_ANALYSIS_V1`` terminates nine of twelve why-chains on one deep root,
``ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE``, and names the quantity the programme
never measured::

    benefit = rho * savings_per_reuse * horizon - (discovery + maintenance + storage)

Every experiment in the lane measured the subtracted terms.  None measured
``rho``: the fraction of tasks whose solution **essentially requires** structure
acquired earlier in the same stream.  In the clause donor ``rho`` was exactly
zero by construction, because every eligible development target was a Boolean
tautology.

This module supplies the ecology for the decisive experiment that document
specifies.  One knob is varied --- ``rho`` --- and the mechanism, the parents,
the budgets, the checker and the horizon are held fixed.

What "essentially requires" means here
--------------------------------------

It is **certified, never assumed**.  A task ``t`` essentially requires acquired
structure ``M`` iff

    minimal_cost(t | M unavailable)  >  minimal_cost(t | M available)

strictly, where the minimum is taken over the *registered procedure set* below
and both sides are computed exactly by running the procedures.  A task solvable
by a bypass at equal cost does **not** count towards ``rho``, even when ``M``
happens to apply to it and even when ``M`` beats the naive procedure.

The registered procedure set, frozen before any outcome:

``P_DP``
    Exact dynamic programming over the Grundy values from the game definition.
    Always available.  This is protocol ``P0``, the task-specific conventional
    algorithm.  Its cost is ``games.Work.total`` for the actual table build.

``P_CLOSED_FORM``
    For a *prefix* move set ``S = {1..m}``, ``G(n) = n mod (m+1)``.  This is
    Bouton / Sprague--Grundy, a parent fact available to anything that knows the
    game, and it costs one predicate evaluation per heap.  A family with a
    registered closed form is a **bypass family**: an acquired periodic rule
    cannot beat arithmetic, so no task on such a family is ever essential.

``P_MEMO``
    An exact solved-instance lookup for a ``(family, position vector)`` already
    solved earlier in the same stream.  One read.  This is the classic
    persistent-memoization parent (protocol ``P1``) at the procedure level, and
    it is the load-bearing bypass: a task that merely *repeats* an earlier one is
    answerable at the acquired rule's own cost without any acquired rule, so it
    is excluded from ``rho`` however demanding it looks.

``P_RULE``
    Evaluate an acquired periodic Grundy rule (``methods.GrundyRule``), one
    predicate evaluation per heap.  Available only when a method for the family
    was **acquirable from strictly earlier tasks in the stream**.

Retrieval overheads --- index probes, object reads, store maintenance --- are
*arm bookkeeping* and are deliberately **not** part of ``minimal_cost``.
Certification is then a statement about the task and the available structure, not
about any arm's filing system, and no arm can make a task look essential by
being slow.

Why this cannot be rigged into a crossover
------------------------------------------

Publication constitution #144 §11 forbids building every environment so that
explicit reuse is optimal by construction.  Three controls are enforced, and the
first two live in this module:

1. ``rho = 0`` is in the sweep and its stream contains the same donor tasks, the
   same family set and the same horizon as every other stream.  It must
   reproduce the existing negatives.
2. The bypass task kinds are generated at every ``rho < 1`` and are certified
   *non*-essential by the same procedure that certifies the essential ones, so
   the generator cannot quietly relabel a convenient task.
3. ``rho_arms`` runs every parent on the identical stream.

The stream is a deterministic function of the pre-registration commitment
(``prereg.commit`` over :data:`RHO_PLAN`), so the protected sweep is a function
of the plan hash: editing the analysis changes the commitment and therefore
changes the draw, which makes analysis drift mechanically visible (CL-D4).

Parents: Sprague--Grundy theory and Bouton's analysis of Nim for the games and
the closed form; version-space / MDL accounting for the method language
(``methods.py``); truth-maintenance and index-cost accounting for the ledger
discipline (``scaling.py``).  No novelty is claimed for any of them.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Mapping, Sequence

from games import SubtractionGame, Work, eventual_period
from methods import (
    Admissibility,
    BitsAccounting,
    GrundyRule,
    GrundyRuleLanguage,
    data_bits,
)
from prereg import Commitment, commit
from scaling import (
    INDEX_ENTRY_BYTES,
    SHARED_SUPPORT_ID,
    CheckStatus,
    CompetenceStore,
    ResourceRecord,
    TouchLedger,
    record_from_ledger,
)

__all__ = [
    "RHO_PLAN",
    "COMMITMENT",
    "LANGUAGE",
    "PROCEDURES",
    "Task",
    "StreamTask",
    "TaskStream",
    "Acquisition",
    "closed_form_families",
    "irregular_families",
    "rejected_families",
    "build_stream",
    "grundy_table",
    "dp_cost",
    "procedure_cost",
    "minimal_cost",
    "certify_essential",
    "check_verdict",
    "solve_by_dp",
    "solve_by_closed_form",
    "acquire_method",
    "is_prefix_move_set",
    "closed_form_modulus",
]


# --------------------------------------------------------------------------
# the frozen plan
# --------------------------------------------------------------------------

#: Frozen before any outcome.  Editing any value changes the commitment and
#: therefore changes the family draw, the probe positions and the task order.
RHO_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "companion": "COGNITIVE_LADDER_SCALING_V1",
    "experiment": "E7 reuse-opportunity-density sweep",
    "answers_root": "ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE",
    "decisive_experiment": "RHO_SWEEP",
    "knob": "rho, the fraction of tasks whose solution essentially requires "
            "structure acquired earlier in the same stream",
    "rho_grid": [0.0, 0.05, 0.1, 0.15, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0],
    "stream_length": 64,
    "irregular_families": 8,
    "closed_form_moduli": [1, 2, 3, 4, 5, 6],
    "move_alphabet": 10,
    "move_set_min_size": 2,
    "move_set_max_size": 4,
    "evidence_window": 24,
    "donor_position": 23,
    "task_position_low": 200,
    "task_position_high": 400,
    "certification_bound": 400,
    "multi_heap_size": 3,
    "multi_heap_every": 3,
    "extrapolation_probes": 3,
    "extrapolation_probe_low": 24,
    "extrapolation_probe_high": 72,
    "language": {"max_preperiod": 6, "max_period": 12, "max_value": 8},
    "maintenance_per_method_per_task": 1,
    "memo_insert_work": 1,
    "index_entry_bytes": INDEX_ENTRY_BYTES,
    "discovery_cost_multipliers": [1, 4],
    "registered_procedures": ["P_DP", "P_CLOSED_FORM", "P_MEMO", "P_RULE"],
    "procedure_preference": ["P_CLOSED_FORM", "P_MEMO", "P_RULE", "P_DP"],
    "arms": [
        "persistent_arm",
        "reset_arm",
        "lazy_parent",
        "index_parent",
        "cache_parent",
        "deferred_induction_parent",
    ],
    "essential_definition": (
        "t essentially requires M iff removing M STRICTLY INCREASES the minimal "
        "solution cost of t over the registered procedure set; a task solvable "
        "by a bypass at equal cost does not count towards rho"
    ),
    "prediction_frozen_before_execution": (
        "the negatives reproduce at rho = 0; the persistent arm's cumulative "
        "cost crosses the strongest parent's at some rho* strictly between 0 "
        "and 1; and rho* rises with discovery and maintenance cost"
    ),
    "falsifier": (
        "no crossover at any rho up to and including 1.0, at matched capability "
        "and with full accounting, refutes the deep root and returns the fault "
        "to the mechanisms"
    ),
    "claim_ceiling": (
        "a hand-set reuse density says nothing about the density of any real "
        "task ecology"
    ),
}

COMMITMENT: Commitment = commit(RHO_PLAN)

LANGUAGE = GrundyRuleLanguage(
    max_preperiod=RHO_PLAN["language"]["max_preperiod"],
    max_period=RHO_PLAN["language"]["max_period"],
    max_value=RHO_PLAN["language"]["max_value"],
)

#: The registered procedure set, with the frozen tie-break preference.  An arm
#: picks the cheapest available procedure by certified cost and breaks ties in
#: this order, so no arm can manufacture a reuse event by preferring its own
#: machinery when something cheaper was available.
PROCEDURES: tuple[str, ...] = tuple(RHO_PLAN["registered_procedures"])

MAINTENANCE_PER_METHOD_PER_TASK: int = RHO_PLAN["maintenance_per_method_per_task"]
MEMO_INSERT_WORK: int = RHO_PLAN["memo_insert_work"]
EVIDENCE_WINDOW: int = RHO_PLAN["evidence_window"]
DONOR_POSITION: int = RHO_PLAN["donor_position"]
CERTIFICATION_BOUND: int = RHO_PLAN["certification_bound"]
STREAM_LENGTH: int = RHO_PLAN["stream_length"]


def _stream_rng(label: str) -> random.Random:
    """A deterministic stream derived from the pre-registration commitment."""
    return random.Random(COMMITMENT.stream(label) % (2**63))


# --------------------------------------------------------------------------
# exact game arithmetic, cached but never shortcut
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def grundy_table(moves: tuple[int, ...], limit: int) -> tuple[tuple[int, ...], int]:
    """``(table, work)`` for ``SUB(moves)`` over ``0..limit``.

    The cache stores the *result of actually running the dynamic programme*,
    including its exact ``Work.total``.  Charging that number to a ledger is
    identical to paying for the run; the cache saves wall time, never work.
    """
    work = Work()
    table = SubtractionGame(moves).grundy_upto(limit, work=work)
    return tuple(table), work.total


def is_prefix_move_set(moves: Sequence[int]) -> bool:
    """``True`` for ``S = {1..m}``, the families with a registered closed form."""
    return tuple(moves) == tuple(range(1, len(moves) + 1))


def closed_form_modulus(moves: Sequence[int]) -> int | None:
    """``m + 1`` for ``S = {1..m}``; ``None`` when no closed form is registered."""
    return len(moves) + 1 if is_prefix_move_set(moves) else None


def closed_form_grundy(modulus: int, position: int) -> int:
    """Bouton / Sprague--Grundy for a prefix subtraction game."""
    return position % modulus


# --------------------------------------------------------------------------
# the registered family pool
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def _candidate_move_sets() -> tuple[tuple[int, ...], ...]:
    """Every non-prefix move set over the registered alphabet and size range."""
    alphabet = RHO_PLAN["move_alphabet"]
    lo, hi = RHO_PLAN["move_set_min_size"], RHO_PLAN["move_set_max_size"]
    pool = tuple(range(1, alphabet + 1))
    out: list[tuple[int, ...]] = []

    def rec(start: int, acc: tuple[int, ...], size: int) -> None:
        if len(acc) == size:
            out.append(acc)
            return
        for i in range(start, len(pool)):
            rec(i + 1, acc + (pool[i],), size)

    for size in range(lo, hi + 1):
        rec(0, (), size)
    return tuple(m for m in out if not is_prefix_move_set(m))


def _family_is_admissible(moves: tuple[int, ...]) -> tuple[bool, str]:
    """Registration filter, applied before any outcome.

    A family joins the irregular pool only if the periodic rule induced from the
    donor task's own evidence window reproduces the exact Grundy value at every
    position the sweep can draw.  This is CL-D1(b) turned into a *registration*
    condition rather than a hoped-for property: it is what keeps the capability
    gate at 1.0 for the arms that reuse, so the efficiency numbers are read
    against matched capability rather than against a quietly wrong rule.

    Rejections are counted and reported; a filter whose rejections are invisible
    is a filter that can be tuned.
    """
    try:
        preperiod, period = eventual_period(moves)
    except AssertionError:
        return False, "NO_EVENTUAL_PERIOD_WITNESSED"
    if preperiod > LANGUAGE.max_preperiod or period > LANGUAGE.max_period:
        return False, "SHAPE_OUTSIDE_REGISTERED_LANGUAGE"
    table, _ = grundy_table(moves, CERTIFICATION_BOUND)
    if max(table) >= LANGUAGE.max_value:
        return False, "GRUNDY_VALUE_OUTSIDE_REGISTERED_LANGUAGE"
    evidence = tuple((n, table[n]) for n in range(EVIDENCE_WINDOW))
    rule = LANGUAGE.induce(evidence)
    if rule is None:
        return False, "NO_HYPOTHESIS_FITS_THE_EVIDENCE_WINDOW"
    if any(rule.grundy(n) != table[n] for n in range(CERTIFICATION_BOUND + 1)):
        return False, "INDUCED_RULE_DIVERGES_INSIDE_THE_TASK_BAND"
    return True, "ADMITTED"


@lru_cache(maxsize=None)
def _draw_families() -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[str, str], ...]]:
    """The commitment-derived irregular pool, with the rejection log."""
    candidates = list(_candidate_move_sets())
    rng = _stream_rng("rho-family-order-v1")
    rng.shuffle(candidates)
    admitted: list[tuple[int, ...]] = []
    rejected: list[tuple[str, str]] = []
    wanted = RHO_PLAN["irregular_families"]
    for moves in candidates:
        if len(admitted) >= wanted:
            break
        ok, reason = _family_is_admissible(moves)
        if ok:
            admitted.append(moves)
        else:
            rejected.append((SubtractionGame(moves).family_id, reason))
    if len(admitted) < wanted:  # pragma: no cover -- the pool is far larger
        raise AssertionError(
            f"only {len(admitted)} admissible irregular families; the registered "
            "pool cannot support the sweep and the experiment must be reported "
            "as unconstructible rather than run on a relaxed filter"
        )
    return tuple(admitted), tuple(rejected)


def irregular_families() -> tuple[tuple[int, ...], ...]:
    """Move sets with **no** registered closed form: the acquirable families."""
    return _draw_families()[0]


def rejected_families() -> tuple[tuple[str, str], ...]:
    """``(family_id, reason)`` for every family the registration filter dropped."""
    return _draw_families()[1]


def closed_form_families() -> tuple[tuple[int, ...], ...]:
    """Prefix move sets ``{1..m}``: the bypass families."""
    return tuple(tuple(range(1, m + 1)) for m in RHO_PLAN["closed_form_moduli"])


# --------------------------------------------------------------------------
# tasks
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Task:
    """One game task: decide whether ``positions`` is a P-position.

    ``heaps == 1`` is a ``SUB(S)`` task; ``heaps > 1`` is ``MULTI[k]SUB(S)``,
    which needs the per-heap rule *and* the combiner.  The combiner (XOR) is
    Bouton's theorem and is available to every arm without acquisition, so the
    only acquirable object in this lane is the per-heap periodic rule --- which
    is exactly ``methods.GrundyRuleLanguage``.
    """

    task_id: str
    family_id: str
    moves: tuple[int, ...]
    heaps: int
    positions: tuple[int, ...]
    intended_kind: str  # DONOR | ESSENTIAL | BYPASS_CLOSED_FORM | BYPASS_REPEAT

    @property
    def key(self) -> tuple[str, tuple[int, ...]]:
        return (self.family_id, self.positions)

    @property
    def modulus(self) -> int | None:
        return closed_form_modulus(self.moves)

    def as_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "family_id": self.family_id,
            "heaps": self.heaps,
            "positions": list(self.positions),
            "intended_kind": self.intended_kind,
        }


# --------------------------------------------------------------------------
# the registered procedures and their exact costs
# --------------------------------------------------------------------------


def _combiner_cost(heaps: int) -> int:
    """XOR over per-heap values; free on one heap, one op per heap beyond that."""
    return heaps if heaps > 1 else 0


def dp_cost(task: Task) -> int:
    """``P_DP``: exact Grundy dynamic programming, then the combiner."""
    _, work = grundy_table(task.moves, max(task.positions))
    return work + _combiner_cost(task.heaps)


def procedure_cost(task: Task, procedure: str) -> int:
    """Exact cost of one registered procedure on ``task``.

    ``P_CLOSED_FORM`` and ``P_RULE`` are both one predicate evaluation per heap:
    a periodic-rule lookup and a modular reduction are the same amount of work,
    which is precisely why a closed-form family can never yield an essential
    task however large the position is.
    """
    if procedure == "P_DP":
        return dp_cost(task)
    if procedure == "P_CLOSED_FORM":
        return task.heaps + _combiner_cost(task.heaps)
    if procedure == "P_RULE":
        return task.heaps + _combiner_cost(task.heaps)
    if procedure == "P_MEMO":
        return 1
    raise ValueError(f"unregistered procedure {procedure}")


def available_procedures(
    task: Task, *, method_available: bool, memo_available: bool
) -> tuple[str, ...]:
    """Which registered procedures can answer ``task`` in this state."""
    out = ["P_DP"]
    if task.modulus is not None:
        out.append("P_CLOSED_FORM")
    if memo_available:
        out.append("P_MEMO")
    if method_available:
        out.append("P_RULE")
    return tuple(out)


def minimal_cost(
    task: Task, *, method_available: bool, memo_available: bool
) -> tuple[int, str]:
    """``(cost, procedure)`` of the cheapest available registered procedure.

    Ties are broken by the frozen preference order, so the choice is a function
    of the plan and not of the arm.
    """
    order = {name: i for i, name in enumerate(RHO_PLAN["procedure_preference"])}
    best: tuple[int, int, str] | None = None
    for name in available_procedures(
        task, method_available=method_available, memo_available=memo_available
    ):
        candidate = (procedure_cost(task, name), order[name], name)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best[0], best[2]


def certify_essential(
    task: Task, *, method_acquirable: bool, memo_available: bool
) -> dict:
    """The load-bearing certificate.  Essentiality is computed, never assumed.

    Returns the two minimal costs, the two procedures, and the strict verdict::

        essential  iff  minimal_cost(without M)  >  minimal_cost(with M)

    A task that a bypass answers at the acquired rule's own cost is **not**
    essential even though the rule applies to it and even though the rule beats
    the naive dynamic programme by a factor of hundreds.  That exclusion is the
    whole reason ``rho`` is not a synonym for "tasks we made easy for ourselves".
    """
    without_cost, without_proc = minimal_cost(
        task, method_available=False, memo_available=memo_available
    )
    with_cost, with_proc = minimal_cost(
        task, method_available=method_acquirable, memo_available=memo_available
    )
    return {
        "essential": bool(with_cost < without_cost),
        "minimal_cost_without_method": without_cost,
        "minimal_cost_with_method": with_cost,
        "procedure_without_method": without_proc,
        "procedure_with_method": with_proc,
        "method_acquirable": bool(method_acquirable),
        "memo_available": bool(memo_available),
        "savings_per_reuse": without_cost - with_cost,
    }


# --------------------------------------------------------------------------
# the independent checker
# --------------------------------------------------------------------------


def check_verdict(task: Task, ledger: TouchLedger) -> bool:
    """Exact verdict from the independent checker (CL-D1(c)).

    Recomputes the Grundy values from the game definition and combines them with
    XOR.  It consults no store, no index and no acquired object.  Its cost lands
    in ``checker_calls`` and ``checker_expansions``; every arm pays exactly one
    call per task, including an arm that could not answer, so no arm can look
    cheap by declining to establish the truth.
    """
    table, work = grundy_table(task.moves, max(task.positions))
    ledger.checker_calls += 1
    ledger.checker_expansions += work
    acc = 0
    for p in task.positions:
        acc ^= table[p]
    return acc == 0


# --------------------------------------------------------------------------
# the method-free procedures, charged to a ledger
# --------------------------------------------------------------------------


def solve_by_dp(task: Task, ledger: TouchLedger) -> bool:
    """``P_DP``.  Returns the verdict and charges the exact dynamic-programming work."""
    table, work = grundy_table(task.moves, max(task.positions))
    ledger.search_expansions += work
    ledger.predicate_evaluations += _combiner_cost(task.heaps)
    acc = 0
    for p in task.positions:
        acc ^= table[p]
    return acc == 0


def solve_by_closed_form(task: Task, ledger: TouchLedger) -> bool:
    """``P_CLOSED_FORM``.  Bouton's arithmetic; available to every arm."""
    modulus = task.modulus
    if modulus is None:
        raise ValueError(f"{task.family_id} has no registered closed form")
    ledger.predicate_evaluations += task.heaps + _combiner_cost(task.heaps)
    acc = 0
    for p in task.positions:
        acc ^= closed_form_grundy(modulus, p)
    return acc == 0


def solve_by_rule(task: Task, rule: GrundyRule, ledger: TouchLedger) -> tuple[bool, tuple[str, ...]]:
    """``P_RULE``.  Returns the verdict and the CL-R3 execution trace.

    The trace is the actual operator sequence executed, step by step.  Presence
    in memory is not use: an endpoint may cite this method only because these
    steps happened.
    """
    trace: list[str] = []
    acc = 0
    for p in task.positions:
        slot = rule.slot(p)
        value = rule.grundy(p, work=None)
        ledger.predicate_evaluations += 1
        trace.append(f"rule.grundy(n={p}) -> slot {slot} -> G={value}")
        acc ^= value
    if task.heaps > 1:
        ledger.predicate_evaluations += task.heaps
        trace.append(f"combiner XOR over {task.heaps} heaps -> {acc}")
    trace.append(f"verdict is_P={acc == 0}")
    return acc == 0, tuple(trace)


# --------------------------------------------------------------------------
# acquisition: induction plus certification, charged as discovery
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Acquisition:
    """One acquired periodic rule, with its CL-D3 bits and CL-D1 verdict."""

    family_id: str
    rule: GrundyRule
    bits: BitsAccounting
    admissibility: Admissibility
    discovery_work: int
    extrapolation_probes: tuple[int, ...]

    @property
    def admissible(self) -> bool:
        return self.admissibility.admissible

    def as_dict(self) -> dict:
        return {
            "family_id": self.family_id,
            "preperiod": self.rule.preperiod,
            "period": self.rule.period,
            "discovery_work": self.discovery_work,
            "extrapolation_probes": list(self.extrapolation_probes),
            "bits": self.bits.as_dict(),
            "admissibility": self.admissibility.as_dict(),
        }


@lru_cache(maxsize=None)
def _extrapolation_probes() -> tuple[int, ...]:
    """Frozen certification positions, strictly above the evidence window."""
    rng = _stream_rng("rho-extrapolation-probes-v1")
    lo = RHO_PLAN["extrapolation_probe_low"]
    hi = RHO_PLAN["extrapolation_probe_high"]
    return tuple(sorted(rng.sample(range(lo, hi + 1), RHO_PLAN["extrapolation_probes"])))


@lru_cache(maxsize=None)
def _acquire_uncharged(moves: tuple[int, ...]) -> tuple[Acquisition, int]:
    """Induce and certify a rule for ``moves``; returns it with its base cost.

    Deterministic and cacheable because it is a pure function of the family and
    the frozen evidence window.  The *cost* is returned so that every arm pays
    it in full every time it acquires; nothing is amortised behind the cache.
    """
    table, _ = grundy_table(moves, CERTIFICATION_BOUND)
    evidence = tuple((n, table[n]) for n in range(EVIDENCE_WINDOW))

    induce_work = Work()
    rule = LANGUAGE.induce(evidence, work=induce_work)
    if rule is None:  # pragma: no cover -- registration filter guarantees a fit
        raise AssertionError(f"no hypothesis fits {moves}")

    probes = _extrapolation_probes()
    certification_work = 0
    failures = 0
    for probe in probes:
        _, work = grundy_table(moves, probe)
        certification_work += work
        if rule.grundy(probe) != table[probe]:
            failures += 1

    bits = BitsAccounting.build(
        LANGUAGE.language_id, LANGUAGE.size(), LANGUAGE.consistent_count(evidence)
    )
    admissibility = Admissibility.build(
        bits_method=LANGUAGE.code_bits(rule),
        bits_data=data_bits(evidence, LANGUAGE.max_value),
        bits_residual=0.0,
        extrapolation_probes=len(probes),
        extrapolation_failures=failures,
        independence_ok=True,
    )
    base_cost = induce_work.total + certification_work
    return (
        Acquisition(
            family_id=SubtractionGame(moves).family_id,
            rule=rule,
            bits=bits,
            admissibility=admissibility,
            discovery_work=base_cost,
            extrapolation_probes=probes,
        ),
        base_cost,
    )


def acquire_method(
    moves: tuple[int, ...], ledger: TouchLedger, *, discovery_multiplier: int = 1
) -> Acquisition:
    """Acquire a periodic rule and charge the whole discovery bill.

    Discovery is induction over the registered language plus the CL-D1(b)
    extrapolation certification against the independent checker.  Both land in
    ``index_build_work``, which is this lane's ``discovery`` coordinate: the term
    the amortization inequality subtracts and the term every previous experiment
    in the programme measured.
    """
    acquisition, base_cost = _acquire_uncharged(moves)
    ledger.index_build_work += base_cost * discovery_multiplier
    return acquisition


# --------------------------------------------------------------------------
# the task stream: one knob, everything else frozen
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class StreamTask:
    """One task in position, with its certificate computed in stream order."""

    index: int
    task: Task
    certified_essential: bool
    minimal_cost_without_method: int
    minimal_cost_with_method: int
    procedure_without_method: str
    procedure_with_method: str
    method_acquirable: bool
    memo_available: bool

    @property
    def savings_per_reuse(self) -> int:
        return self.minimal_cost_without_method - self.minimal_cost_with_method

    def as_dict(self) -> dict:
        out = self.task.as_dict()
        out.update(
            {
                "index": self.index,
                "certified_essential": self.certified_essential,
                "minimal_cost_without_method": self.minimal_cost_without_method,
                "minimal_cost_with_method": self.minimal_cost_with_method,
                "procedure_without_method": self.procedure_without_method,
                "procedure_with_method": self.procedure_with_method,
                "method_acquirable": self.method_acquirable,
                "memo_available": self.memo_available,
                "savings_per_reuse": self.savings_per_reuse,
            }
        )
        return out


@dataclass(frozen=True)
class TaskStream:
    """A frozen stream at one requested ``rho``.

    ``requested_rho`` is the knob.  ``realised_rho`` is what the certifier found,
    and the two differ because the donor tasks that make any structure acquirable
    at all can never themselves be essential.  Reporting only the requested value
    would hide exactly that.
    """

    requested_rho: float
    tasks: tuple[StreamTask, ...]

    @property
    def realised_rho(self) -> float:
        if not self.tasks:
            return 0.0
        return sum(1 for t in self.tasks if t.certified_essential) / len(self.tasks)

    @property
    def essential_count(self) -> int:
        return sum(1 for t in self.tasks if t.certified_essential)

    def kind_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for st in self.tasks:
            out[st.task.intended_kind] = out.get(st.task.intended_kind, 0) + 1
        return out

    @property
    def total_certified_savings(self) -> int:
        return sum(st.savings_per_reuse for st in self.tasks if st.certified_essential)


def _heaps_for(slot: int) -> int:
    every = RHO_PLAN["multi_heap_every"]
    return RHO_PLAN["multi_heap_size"] if slot % every == every - 1 else 1


def build_stream(requested_rho: float) -> TaskStream:
    """The frozen stream at one ``rho``, with every certificate asserted.

    The shape held fixed across the whole sweep: the same eight irregular donor
    tasks at the same donor position, the same family pool, the same horizon of
    ``stream_length`` tasks, the same position band.  The **only** thing ``rho``
    changes is how many of the non-donor slots are essential rather than
    bypassable.  Discovery cost is therefore identical at every ``rho``, which is
    what makes this a one-knob sweep rather than a change of ecology.

    Essential slots are spread evenly through the stream rather than clustered,
    so no arm benefits from an ordering effect (protocol attack A6/A7).

    The two assertions at the end are the anti-rigging guarantee: every task the
    generator *intended* to be essential is certified essential, and every task
    it intended to be bypassable is certified non-essential.  If the domain could
    not produce certified-essential tasks the generator would raise here, and the
    honest report would be that the experiment is unconstructible.
    """
    if not 0.0 <= requested_rho <= 1.0:
        raise ValueError("rho must lie in [0, 1]")

    irregular = irregular_families()
    closed = closed_form_families()
    rng = _stream_rng(f"rho-stream-v1:{requested_rho:.4f}")

    tasks: list[Task] = []
    for moves in irregular:
        family_id = SubtractionGame(moves).family_id
        tasks.append(
            Task(
                task_id=f"T{len(tasks):03d}",
                family_id=family_id,
                moves=moves,
                heaps=1,
                positions=(DONOR_POSITION,),
                intended_kind="DONOR",
            )
        )

    n_slots = STREAM_LENGTH - len(tasks)
    n_essential = min(n_slots, int(requested_rho * STREAM_LENGTH + 0.5))

    lo, hi = RHO_PLAN["task_position_low"], RHO_PLAN["task_position_high"]
    used: set[tuple[str, tuple[int, ...]]] = {t.key for t in tasks}

    def fresh_positions(family_id: str, heaps: int) -> tuple[int, ...]:
        for _ in range(4096):
            positions = tuple(sorted(rng.sample(range(lo, hi + 1), heaps)))
            if (family_id, positions) not in used:
                used.add((family_id, positions))
                return positions
        raise AssertionError("position band exhausted")  # pragma: no cover

    essential_seen = 0
    closed_seen = 0
    for slot in range(n_slots):
        # even spread: the slot is essential when the running quota advances
        take = (slot + 1) * n_essential // n_slots > slot * n_essential // n_slots
        heaps = _heaps_for(slot)
        task_id = f"T{len(tasks):03d}"
        if take:
            moves = irregular[essential_seen % len(irregular)]
            essential_seen += 1
            family_id = SubtractionGame(moves).family_id
            tasks.append(
                Task(
                    task_id=task_id,
                    family_id=family_id,
                    moves=moves,
                    heaps=heaps,
                    positions=fresh_positions(family_id, heaps),
                    intended_kind="ESSENTIAL",
                )
            )
        elif slot % 2 == 0:
            moves = closed[closed_seen % len(closed)]
            closed_seen += 1
            family_id = SubtractionGame(moves).family_id
            tasks.append(
                Task(
                    task_id=task_id,
                    family_id=family_id,
                    moves=moves,
                    heaps=heaps,
                    positions=fresh_positions(family_id, heaps),
                    intended_kind="BYPASS_CLOSED_FORM",
                )
            )
        else:
            source = _repeat_source(tasks)
            tasks.append(
                Task(
                    task_id=task_id,
                    family_id=source.family_id,
                    moves=source.moves,
                    heaps=source.heaps,
                    positions=source.positions,
                    intended_kind="BYPASS_REPEAT",
                )
            )

    stream = _certify_stream(requested_rho, tuple(tasks))

    for st in stream.tasks:
        if st.task.intended_kind == "ESSENTIAL" and not st.certified_essential:
            raise AssertionError(
                f"{st.task.task_id} was generated as essential but certification "
                "found an equal-cost bypass; the generator must not count it"
            )
        if st.task.intended_kind != "ESSENTIAL" and st.certified_essential:
            raise AssertionError(
                f"{st.task.task_id} was generated as bypassable but certification "
                "found it essential; the stream shape is not what the plan says"
            )
    return stream


def _repeat_source(tasks: Sequence[Task]) -> Task:
    """The earlier task a ``BYPASS_REPEAT`` slot repeats exactly.

    An essential task is preferred, because repeating one is the sharpest
    demonstration the certifier can be given: the repeat sits on an irregular
    family at a position hundreds of steps beyond the training support, where the
    dynamic programme costs thousands of units and the acquired rule costs one,
    and it is *still* not essential, because a solved-instance store answers it
    for the same one unit.
    """
    for kind in ("ESSENTIAL", "BYPASS_CLOSED_FORM", "DONOR"):
        for task in reversed(tasks):
            if task.intended_kind == kind:
                return task
    raise AssertionError("no earlier task to repeat")  # pragma: no cover


def _certify_stream(requested_rho: float, tasks: Sequence[Task]) -> TaskStream:
    """Walk the stream in order and certify each task against what came before.

    ``method_acquirable`` is true only when an **earlier** task on the same family
    was answered by the dynamic programme, because that is the only thing in this
    ecology that produces the Grundy evidence a rule is induced from.  Structure
    that could not have been acquired earlier cannot make a later task essential,
    which is what ties ``rho`` to accumulation rather than to mere applicability.
    """
    solved: set[tuple[str, tuple[int, ...]]] = set()
    acquirable: set[str] = set()
    out: list[StreamTask] = []
    for index, task in enumerate(tasks):
        memo_available = task.key in solved
        method_acquirable = task.family_id in acquirable
        cert = certify_essential(
            task, method_acquirable=method_acquirable, memo_available=memo_available
        )
        out.append(
            StreamTask(
                index=index,
                task=task,
                certified_essential=cert["essential"],
                minimal_cost_without_method=cert["minimal_cost_without_method"],
                minimal_cost_with_method=cert["minimal_cost_with_method"],
                procedure_without_method=cert["procedure_without_method"],
                procedure_with_method=cert["procedure_with_method"],
                method_acquirable=method_acquirable,
                memo_available=memo_available,
            )
        )
        if cert["procedure_without_method"] == "P_DP" and task.modulus is None:
            acquirable.add(task.family_id)
        solved.add(task.key)
    return TaskStream(requested_rho=requested_rho, tasks=tuple(out))
