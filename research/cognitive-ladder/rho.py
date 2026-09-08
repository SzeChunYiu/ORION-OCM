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
