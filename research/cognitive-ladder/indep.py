"""E8: an independently implemented parent for the scalar-only factorization task.

Why this experiment exists
--------------------------

Two lanes in this programme reported ``PARENT_SUFFICIENT`` where the strongest
parent was *the arm's own generic algorithm holding separate state*.  Both
sessions said so plainly rather than hiding it.  The independent factorization
session's own words:

    "The adaptive parent uses the same generic algorithm with separate state:
    constructive parent sufficiency, not independent implementation/replication."

Issue #149 reports the same shape under the name
``AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION``.  ``ROOT_CAUSE_ANALYSIS_V1``
terminates both chains on ``PARENT_SHARES_THE_MECHANISM_UNDER_TEST`` and
``NEGATIVE_DISPOSITION_V1`` marks N10 ``CORRECTABLE`` with exactly one fix:
*an independently implemented parent given the same information*.

A tie against yourself is a tautology.  It is not weak evidence for the
architecture and it is not weak evidence against it; it carries no information
in either direction, because the two sides of the comparison are the same
program.  This module replaces that comparison.

``constructive_parent`` is kept, and it is kept deliberately.  It is the same
:class:`WalshLearner` class with its own state, so it *must* tie the arm
exactly, and ``test_indep.py`` asserts that it does.  Its role is not to be
beaten; its role is to make the tautology visible next to the real comparison,
so a reader can see what the earlier verdict actually measured.

The task
--------

Reconstructed from the description in the original lane's result: a learner
receives **scalar objective observations only** -- never components, never scope
masks, never the landscape object -- across twelve generations on an NK-style
landscape drawn by ``pr150_source.NK``, and must reach the exact optimum while
spending as few objective calls as possible.  Three regimes: sparse stable,
dense stable, and sparse with per-generation support replacement (drift).

The reconstruction is pinned to the original lane's reported numbers where
those numbers pin it.  ``3072`` objective calls for global enumeration over a
lifetime is ``12 * 2**8`` exactly, which fixes ``n = 8`` and twelve generations;
``2048`` bytes for a global value array is ``2**8 * 8`` exactly, which fixes the
byte rule.  ``3072`` for *everything* under drift fixes the arm's rebuild as a
full ``2**n`` transform rather than a sparse recovery.  What the reconstruction
does **not** reproduce is stated in the receipt rather than smoothed over.

What is measured, and why it is measured componentwise
------------------------------------------------------

The original lane was explicit that fewer objective calls is not whole-resource
dominance.  So the coordinates are never summed into a score:

``objective_calls``
    Distinct evaluations of the scalar objective, per lifetime.  Split by phase
    into ``discovery``, ``steady_state``, ``invalidation`` and ``search`` --
    a decomposition of one coordinate, not an aggregate over several.
``optimum_attained``
    The **capability gate**.  An arm that does not reach the exact optimum in
    every generation is inadmissible for the cost comparison, and
    :meth:`LifetimeRecord.objective_calls_if_admissible` is the only accessor
    the terminal rule may read.  Cheap and wrong is not cheap.
``fit_units`` / ``audit_units`` / ``invalidation_units`` / ``model_search_units``
    Fitting a live model, auditing it against fresh observations, discarding and
    re-deriving it after a mismatch, and searching inside it.  Invalidation is
    metered on its own coordinate rather than folded into fitting, so a machine
    that is cheap in objective calls because it rebuilds constantly cannot hide
    the rebuild.
``persistent_bytes``
    State carried *across* generations under a declared arm-independent byte
    rule.  Within-generation scratch is not persistent state.
``rebuilds``
    How often the model was invalidated, which is the coordinate drift acts on.

The decisive question and both of its answers
---------------------------------------------

Does an independently implemented parent match ``walsh_arm``'s objective-call
count?

* **Match or better** -> ``INDEPENDENT_PARENT_SUFFICIENT``.  Then
  ``PARENT_SUFFICIENT`` is informative for the first time in this programme: the
  earlier verdict was not an artifact of shared code, and the mechanism has no
  residual on this problem.
* **Strictly worse** -> ``ARM_SEPARATES_FROM_INDEPENDENT_PARENTS``.  Then the
  earlier tie proved nothing and a real comparison shows a gap, which is
  quantified -- and a gap against four hand-written parents is still not parent
  closure, because no modern AutoML or full-strength learned surrogate was run.

Both are publishable and ``terminal_for`` in ``run_indep.py`` was written before
any number was produced.

Parents: Walsh/Fourier analysis of Boolean functions (Kushilevitz--Mansour,
Goldreich--Levin) for the arm; ordinary least squares over a multilinear
monomial basis for the regression parent; tabu search (Glover) for the search
parent; successive halving / sequential halving for best-arm identification
(Karnin--Koren--Somekh, Jamieson--Talwalkar) for the bandit parent.  No novelty
is claimed for any of them, and none of them is this programme's invention.
"""

from __future__ import annotations

import math
import pathlib
import random
import sys
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping, Protocol, Sequence

from prereg import Commitment, commit

# ``pr150_source`` is the world under audit and lives in the sibling audit lane.
# It is imported by bare name, as every module in this lane is; the path entry
# below is what makes that possible without copying or modifying the landscape.
_PR150_LANE = pathlib.Path(__file__).resolve().parent.parent / "pr150-audit"
if str(_PR150_LANE) not in sys.path:
    sys.path.insert(0, str(_PR150_LANE))

import pr150_source as SRC  # noqa: E402  (path entry must precede the import)

__all__ = [
    "N_BITS",
    "GENERATIONS",
    "REPS",
    "AUDIT_POINTS",
    "AUDIT_TOLERANCE",
    "COEFFICIENT_TOLERANCE",
    "MODEL_PARAMETER_CEILING",
    "COEFFICIENT_BYTES",
    "STATE_BYTES",
    "VALUE_BYTES",
    "MATCH_TOLERANCE",
    "DECISIVE_REGIME",
    "TERMINALS",
    "ARM_ROLES",
    "SEARCH_POLICY",
    "INDEP_PLAN",
    "COMMITMENT",
    "Regime",
    "REGIMES",
    "Objective",
    "WorkLedger",
    "PointStream",
    "CallSplit",
    "GenerationOutcome",
    "GenerationRecord",
    "LifetimeRecord",
    "Learner",
    "WalshLearner",
    "walsh_arm",
    "constructive_parent",
    "global_enumeration_parent",
    "GlobalEnumerationParent",
    "chi",
    "lifetime_landscapes",
    "point_stream",
    "run_lifetime",
    "sweep",
    "sweep_table",
    "REFERENCE_NUMBERS",
]


# --------------------------------------------------------------------------
# declared constants -- fixed before any outcome
# --------------------------------------------------------------------------

#: Bits in the assignment.  ``2**8 == 256`` and ``12 * 256 == 3072``, which is
#: the original lane's reported global-enumeration lifetime exactly.
N_BITS = 8

#: Generations in one lifetime, from the original lane's description.
GENERATIONS = 12

#: Independent lifetimes per regime.  Every arm sees the identical landscapes.
REPS = 8

#: Fresh observations spent auditing a model per generation.  One of them is
#: always the model's own predicted optimum, so a model that is wrong exactly
#: where it matters is caught by the audit rather than by luck.
AUDIT_POINTS = 4

#: A model prediction that disagrees with an observation by more than this is a
#: mismatch.  The landscapes are noiseless and the representations are exact, so
#: this separates float error from real disagreement and is not a tuned knob.
AUDIT_TOLERANCE = 1e-9

#: A fitted coefficient at or below this magnitude is a structural zero.
COEFFICIENT_TOLERANCE = 1e-9

#: A model with more free parameters than this is refused as a compression: it
#: costs more to identify than the value table it is meant to summarise.  The
#: same ceiling binds **every** model-based arm, so no arm is advantaged by it.
MODEL_PARAMETER_CEILING = 1 << (N_BITS - 1)

#: Declared byte rule.  Arm-independent by construction, so an arm cannot look
#: cheap by declaring a smaller entry.
COEFFICIENT_BYTES = 16  # one basis index plus one float
STATE_BYTES = 8  # one stored assignment
VALUE_BYTES = 8  # one stored objective value

#: Two objective-call counts "match" when they differ by at most this fraction.
#: Declared before execution; a threshold chosen after seeing numbers is not a
#: threshold.
MATCH_TOLERANCE = 0.02

#: The regime the overall terminal is read from: the one the original lane's
#: separation lived in.  The other two are reported and are not the headline.
DECISIVE_REGIME = "sparse_stable"

#: Every terminal this experiment may return, registered in advance.
TERMINALS = (
    "CONSTRUCTIVE_TIE_BROKEN",
    "ARM_NOT_CAPABLE",
    "NO_INDEPENDENT_PARENT_IS_CAPABLE",
    "INDEPENDENT_PARENT_SUFFICIENT",
    "ARM_SEPARATES_FROM_INDEPENDENT_PARENTS",
)

ARM_ROLES: Mapping[str, str] = {
    "walsh_arm": "MECHANISM_UNDER_TEST",
    "constructive_parent": "TAUTOLOGY_CONTROL",
    "regression_parent": "INDEPENDENT_PARENT",
    "tabu_parent": "INDEPENDENT_PARENT",
    "bandit_parent": "INDEPENDENT_PARENT",
    "global_enumeration_parent": "CEILING",
}

#: The search policy actually used by each arm, declared so that a parent that
#: underperforms cannot be waved away as undertuned without the reader being
#: able to check what it was given.  Every arm gets the same information (scalar
#: observations only), the same landscapes, the same per-generation point
#: stream, the same free re-query of anything it has already paid for, and the
#: same hard ceiling of ``2**n`` distinct evaluations per generation.
SEARCH_POLICY: Mapping[str, str] = {
    "shared": (
        "Every arm receives the identical landscapes, the identical "
        "per-generation deterministic point stream, and a metered objective "
        "that charges one call per DISTINCT assignment and re-serves anything "
        "already paid for at zero cost. No arm sees components, scope masks, "
        "tables or the landscape object. No arm may exceed 2**n distinct "
        "evaluations in a generation, which is the information ceiling."
    ),
    "walsh_arm": (
        "Rebuild = measure all 2**n points and take the fast Walsh-Hadamard "
        "transform; support = coefficients above COEFFICIENT_TOLERANCE. "
        "Steady state = refit exactly the held support by incremental "
        "Gauss-Jordan on freshly drawn points (one call per point, extra "
        "points drawn only to repair a rank deficiency), then audit on the "
        "model's own argmax plus AUDIT_POINTS-1 fresh points; any mismatch "
        "invalidates and rebuilds. Model search is exact (inverse transform), "
        "so the arm is not handicapped by its inner optimiser."
    ),
    "constructive_parent": (
        "Byte-identical policy to walsh_arm: the SAME WalshLearner class with "
        "its own state. This is the tautology under test, not a comparator."
    ),
    "regression_parent": (
        "Multilinear monomial basis in the 0/1 variables. Degree escalation "
        "1,2,3,... halting at the shared MODEL_PARAMETER_CEILING; at each "
        "degree an exactly-determined ordinary-least-squares fit solved by "
        "Gauss-Jordan with partial pivoting (a fresh point swapped in on a "
        "singular design), then the same audit rule and the same audit budget "
        "as the arm. Surrogate optimisation is EXHAUSTIVE over all 2**n "
        "assignments, so the parent is not handicapped by its inner optimiser. "
        "Selected features persist across generations and are refit, so the "
        "parent has the same amortization opportunity the arm has."
    ),
    "tabu_parent": (
        "No model. Best-neighbour moves with a tabu tenure of 3, restart after "
        "16 non-improving moves, stop after 8 non-improving restarts or at the "
        "2**n ceiling, whichever comes first. Carries the two best assignments "
        "across generations as restart seeds, so it has cross-generation "
        "memory. Its budget is the ceiling, which is the most any arm can be "
        "given."
    ),
    "bandit_parent": (
        "No model. Each bit is an arm; successive halving races bit flips "
        "against shared random backgrounds, doubling the context count each "
        "round, then constructs an incumbent in the surviving order and "
        "polishes it by best-improvement local search. Repeats with fresh "
        "contexts until 4 non-improving races or the 2**n ceiling. Carries the "
        "bit order and the best assignment across generations."
    ),
    "global_enumeration_parent": (
        "Measures all 2**n assignments every generation. The exact ceiling; "
        "attains the optimum by construction and cannot be undertuned."
    ),
}

#: What the original lane reported, recorded so the reconstruction can be
#: checked against it rather than asserted to match it.
REFERENCE_NUMBERS: Mapping[str, Any] = {
    "source": "research/independent-factorization-20260908/SESSION_RESULT.md (not in this tree)",
    "candidate_objective_calls_sparse_stable": 442,
    "adaptive_parent_objective_calls_sparse_stable": 442,
    "global_enumeration_objective_calls": 3072,
    "objective_calls_under_drift_all_arms": 3072,
    "candidate_persistent_bytes_sparse": 524928,
    "global_value_array_bytes": 2048,
    "what_these_pin": [
        "3072 == 12 * 2**8 pins n = 8 and twelve generations exactly",
        "2048 == 2**8 * 8 pins the value-array byte rule exactly",
        "3072 for everything under drift pins the arm's rebuild as a full 2**n "
        "transform rather than a sparse recovery",
    ],
}


# --------------------------------------------------------------------------
# regimes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Regime:
    """One registered ecology: coupling density and support drift rate."""

    name: str
    K: int
    drift: float
    description: str


REGIMES: tuple[Regime, ...] = (
    Regime(
        name="sparse_stable",
        K=2,
        drift=0.0,
        description=(
            "Sparse coupling, supports fixed for the whole lifetime, tables "
            "redrawn every generation. Structure persists and coefficients do "
            "not, which is the only regime where carrying a factorization "
            "between generations can pay for itself."
        ),
    ),
    Regime(
        name="dense_stable",
        K=5,
        drift=0.0,
        description=(
            "Dense coupling, supports fixed. The Walsh/monomial support of a "
            "K=5 landscape on eight bits nearly fills the table, so any model "
            "costs about what measuring the table costs. The registered "
            "parameter ceiling refuses the model here for every model-based "
            "arm alike."
        ),
    ),
    Regime(
        name="sparse_drift",
        K=2,
        drift=0.10,
        description=(
            "Sparse coupling with per-generation support replacement at PR "
            "#150's own drift rate. Carried structure goes stale, the audit "
            "fires, and the invalidation coordinate is where the cost lands."
        ),
    ),
)


# --------------------------------------------------------------------------
# the frozen plan and the commitment-derived draw
# --------------------------------------------------------------------------

INDEP_PLAN: dict[str, Any] = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "rung": "CL-E8 independently implemented parent for scalar-only factorization",
    "negative_addressed": "N10-SCALAR-FACTORIZATION",
    "negative_verdict_being_retested": "PARENT_SUFFICIENT",
    "deep_root_addressed": "PARENT_SHARES_THE_MECHANISM_UNDER_TEST",
    "bits": N_BITS,
    "generations": GENERATIONS,
    "reps": REPS,
    "regimes": [
        {"name": r.name, "K": r.K, "drift": r.drift} for r in REGIMES
    ],
    "arms": list(ARM_ROLES),
    "arm_roles": dict(ARM_ROLES),
    "information_given_to_every_arm": "SCALAR_OBJECTIVE_OBSERVATIONS_ONLY",
    "endpoints": [
        "objective_calls per lifetime",
        "optimum_attained per generation (capability gate)",
        "persistent_bytes",
        "fit_units",
        "audit_units",
        "invalidation_units",
        "model_search_units",
        "rebuilds per lifetime",
    ],
    "resource_coordinates_are_summed": False,
    "capability_gate": "optimum attained in EVERY generation, exactly",
    "decisive_regime": DECISIVE_REGIME,
    "match_tolerance": MATCH_TOLERANCE,
    "audit_points": AUDIT_POINTS,
    "audit_tolerance": AUDIT_TOLERANCE,
    "coefficient_tolerance": COEFFICIENT_TOLERANCE,
    "model_parameter_ceiling": MODEL_PARAMETER_CEILING,
    "bytes": {
        "coefficient": COEFFICIENT_BYTES,
        "state": STATE_BYTES,
        "value": VALUE_BYTES,
    },
    "terminals": list(TERMINALS),
    "search_policy": dict(SEARCH_POLICY),
    "landscape": "pr150_source.NK, unmodified",
}

COMMITMENT: Commitment = commit(INDEP_PLAN)


def _stream_rng(label: str) -> random.Random:
    """A deterministic stream derived from the pre-registration commitment."""
    return random.Random(COMMITMENT.stream(label) % (2**63))


# --------------------------------------------------------------------------
# the meters
# --------------------------------------------------------------------------


@dataclass
class Objective:
    """The only channel between an arm and the world.

    Mutable on purpose, in the style of ``games.Work``: the frozen dataclasses
    in this module are the *records*, and a record is built from a finished
    ledger.  Nothing here reads a clock.

    One call is charged per **distinct** assignment.  Re-asking for something
    already paid for is free, uniformly, for every arm.  That rule exists so
    that no arm can look efficient merely by de-duplicating its own queries,
    and so that a rebuild which re-measures points the refit already bought
    pays only the difference.
    """

    n: int
    fitness: Any
    cache: dict[int, float] = field(default_factory=dict)
    calls: int = 0
    requests: int = 0

    def __call__(self, x: int) -> float:
        self.requests += 1
        hit = self.cache.get(x)
        if hit is not None:
            return hit
        value = self.fitness(x)
        self.cache[x] = value
        self.calls += 1
        return value

    def best_observed(self) -> int:
        """The best assignment among everything actually evaluated."""
        return max(self.cache, key=lambda x: (self.cache[x], -x))

    def top_observed(self, count: int) -> tuple[int, ...]:
        ordered = sorted(self.cache, key=lambda x: (-self.cache[x], x))
        return tuple(ordered[:count])


@dataclass
class WorkLedger:
    """Non-objective work, kept on separate coordinates and never summed.

    ``invalidation_units`` is metered apart from ``fit_units`` deliberately: an
    arm that is cheap in objective calls because it discards and re-derives its
    model every generation must not be able to book that as fitting.
    """

    fit_units: int = 0
    audit_units: int = 0
    invalidation_units: int = 0
    model_search_units: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "fit_units": self.fit_units,
            "audit_units": self.audit_units,
            "invalidation_units": self.invalidation_units,
            "model_search_units": self.model_search_units,
        }


@dataclass
class PointStream:
    """A cursor over a frozen permutation of the assignment space.

    Every arm in a generation is handed a stream built from the *same*
    permutation with its own cursor.  Common random numbers, so a difference
    between two arms is a difference between two algorithms.
    """

    points: tuple[int, ...]
    cursor: int = 0

    def next(self) -> int:
        x = self.points[self.cursor % len(self.points)]
        self.cursor += 1
        return x

    def take(self, count: int) -> list[int]:
        return [self.next() for _ in range(count)]


def point_stream(regime: str, rep: int, generation: int) -> tuple[int, ...]:
    """The frozen point order for one generation, from the commitment."""
    rng = _stream_rng(f"indep-points|{regime}|{rep}|{generation}")
    points = list(range(1 << N_BITS))
    rng.shuffle(points)
    return tuple(points)


# --------------------------------------------------------------------------
# per-generation and per-lifetime records
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CallSplit:
    """A decomposition of ONE coordinate by phase, not an aggregate over many.

    ``discovery`` is the first build of a model from nothing; ``invalidation``
    is a rebuild the audit forced; ``steady_state`` is refit-and-audit against a
    model already held; ``search`` is everything a model-free arm spends.
    """

    discovery: int = 0
    steady_state: int = 0
    invalidation: int = 0
    search: int = 0

    @property
    def total(self) -> int:
        return self.discovery + self.steady_state + self.invalidation + self.search

    def plus(self, other: "CallSplit") -> "CallSplit":
        return CallSplit(
            discovery=self.discovery + other.discovery,
            steady_state=self.steady_state + other.steady_state,
            invalidation=self.invalidation + other.invalidation,
            search=self.search + other.search,
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "discovery": self.discovery,
            "steady_state": self.steady_state,
            "invalidation": self.invalidation,
            "search": self.search,
        }


@dataclass(frozen=True)
class GenerationOutcome:
    """What a learner hands back after one generation."""

    best_x: int
    rebuilt: bool
    model_parameters: int
    model_refused: bool
    calls: CallSplit


@dataclass(frozen=True)
class GenerationRecord:
    """One generation of one lifetime for one arm, scored against the oracle."""

    regime: str
    arm: str
    rep: int
    generation: int
    objective_calls: int
    optimum: float
    attained_value: float
    attained: bool
    rebuilt: bool
    model_parameters: int
    model_refused: bool
    calls: CallSplit


@dataclass(frozen=True)
class LifetimeRecord:
    """One arm's whole lifetime in one regime, averaged over repetitions.

    The capability gate is enforced structurally.  ``objective_calls`` is
    reported unconditionally, because a cost that is hidden cannot be checked,
    but the only accessor the terminal rule is permitted to read is
    :meth:`objective_calls_if_admissible`, which returns ``None`` unless the arm
    attained the exact optimum in every generation of every repetition.
    """

    regime: str
    arm: str
    arm_role: str
    generations: int
    reps: int
    objective_calls: float
    call_split: Mapping[str, float]
    optimum_attained_generations: float
    optimum_attained_fraction: float
    mean_quality_over_optimum: float
    fit_units: float
    audit_units: float
    invalidation_units: float
    model_search_units: float
    persistent_bytes: float
    rebuilds: float
    model_parameters: float
    model_refused_fraction: float

    @property
    def capability_ok(self) -> bool:
        return self.optimum_attained_fraction == 1.0

    @property
    def admissible(self) -> bool:
        """Capability first.  An arm that misses the optimum has no cost to read."""
        return self.capability_ok

    def objective_calls_if_admissible(self) -> float | None:
        """The ONLY cost accessor the terminal rule may use."""
        if not self.admissible:
            return None
        return self.objective_calls

    def resource_coordinates(self) -> dict[str, float]:
        """The separately reported coordinates.  Never summed into a score."""
        return {
            "objective_calls": self.objective_calls,
            "fit_units": self.fit_units,
            "audit_units": self.audit_units,
            "invalidation_units": self.invalidation_units,
            "model_search_units": self.model_search_units,
            "persistent_bytes": self.persistent_bytes,
        }

    def as_row(self) -> dict[str, Any]:
        row = {
            "regime": self.regime,
            "arm": self.arm,
            "arm_role": self.arm_role,
            "generations": self.generations,
            "reps": self.reps,
            "optimum_attained_generations": self.optimum_attained_generations,
            "optimum_attained_fraction": self.optimum_attained_fraction,
            "mean_quality_over_optimum": self.mean_quality_over_optimum,
            "capability_ok": self.capability_ok,
            "admissible": self.admissible,
            "objective_calls_if_admissible": self.objective_calls_if_admissible(),
            "call_split": dict(self.call_split),
            "rebuilds": self.rebuilds,
            "model_parameters": self.model_parameters,
            "model_refused_fraction": self.model_refused_fraction,
        }
        row.update(self.resource_coordinates())
        return row


# --------------------------------------------------------------------------
# the learner protocol
# --------------------------------------------------------------------------


class Learner(Protocol):
    """What the harness requires of an arm.  Nothing about how it works."""

    def generation(
        self, objective: Objective, stream: PointStream, work: WorkLedger
    ) -> GenerationOutcome: ...

    def persistent_bytes(self) -> int: ...


# --------------------------------------------------------------------------
# the mechanism under test: a Walsh/Fourier factorization learner
# --------------------------------------------------------------------------


def chi(subset: int, x: int) -> float:
    """The Walsh character of ``subset`` at ``x``: ``(-1)**|subset & x|``."""
    return -1.0 if bin(subset & x).count("1") & 1 else 1.0


def _walsh_hadamard(vector: Sequence[float]) -> tuple[list[float], int]:
    """In-place fast Walsh-Hadamard transform.  Returns the butterfly count.

    Self-inverse up to a factor of ``len(vector)``, so the same routine both
    analyses a measured table into coefficients and synthesises a table from
    coefficients.
    """
    a = list(vector)
    size = len(a)
    ops = 0
    h = 1
    while h < size:
        for i in range(0, size, h << 1):
            for j in range(i, i + h):
                u, v = a[j], a[j + h]
                a[j], a[j + h] = u + v, u - v
        ops += size
        h <<= 1
    return a, ops


def _walsh_full_transform(objective: Objective, n: int) -> tuple[tuple[float, ...], int]:
    """Measure the whole table and analyse it.  ``2**n`` objective calls."""
    size = 1 << n
    values = [objective(x) for x in range(size)]
    spectrum, ops = _walsh_hadamard(values)
    return tuple(c / size for c in spectrum), ops + size


def _walsh_threshold(coefficients: Sequence[float]) -> tuple[int, ...]:
    """The support: the basis indices this landscape actually puts weight on."""
    return tuple(
        s for s, c in enumerate(coefficients) if abs(c) > COEFFICIENT_TOLERANCE
    )


def _walsh_refit(
    objective: Objective,
    support: Sequence[int],
    stream: PointStream,
    work: WorkLedger,
) -> tuple[float, ...] | None:
    """Re-identify coefficients on a support already held.

    Incremental Gauss-Jordan: each fresh point contributes one row, the row is
    reduced against the basis already accumulated, and a point whose row adds no
    rank is discarded and another drawn.  So the objective cost is ``|support|``
    plus whatever a rank deficiency actually costs to repair, and never a fixed
    slack allowance chosen to be safe.
    """
    p = len(support)
    if p == 0:
        return ()
    limit = min(1 << objective.n, 3 * p + 8)
    pivots: list[int] = []
    rows: list[list[float]] = []
    vals: list[float] = []
    taken = 0
    while len(pivots) < p and taken < limit:
        x = stream.next()
        taken += 1
        row = [chi(s, x) for s in support]
        val = objective(x)
        for pc, brow, bval in zip(pivots, rows, vals):
            factor = row[pc]
            if factor:
                for c in range(p):
                    row[c] -= factor * brow[c]
                val -= factor * bval
                work.fit_units += p + 1
        pivot = None
        for c in range(p):
            if abs(row[c]) > 1e-9:
                pivot = c
                break
        if pivot is None:
            continue
        inv = 1.0 / row[pivot]
        row = [a * inv for a in row]
        val *= inv
        work.fit_units += p + 1
        for i in range(len(rows)):
            factor = rows[i][pivot]
            if factor:
                target = rows[i]
                for c in range(p):
                    target[c] -= factor * row[c]
                vals[i] -= factor * val
                work.fit_units += p + 1
        pivots.append(pivot)
        rows.append(row)
        vals.append(val)
    if len(pivots) < p:
        return None
    solution = [0.0] * p
    for pc, val in zip(pivots, vals):
        solution[pc] = val
    return tuple(solution)


def _walsh_argmax(
    support: Sequence[int], coefficients: Sequence[float], n: int, work: WorkLedger
) -> int:
    """The model's own optimum, exactly, by synthesising the model's table."""
    size = 1 << n
    vector = [0.0] * size
    for s, c in zip(support, coefficients):
        vector[s] = c
    values, ops = _walsh_hadamard(vector)
    work.model_search_units += ops + size
    return max(range(size), key=lambda x: (values[x], -x))


def _walsh_predict(
    support: Sequence[int], coefficients: Sequence[float], x: int
) -> float:
    return math.fsum(c * chi(s, x) for s, c in zip(support, coefficients))


def _walsh_audit(
    support: Sequence[int],
    coefficients: Sequence[float],
    objective: Objective,
    stream: PointStream,
    candidate: int,
    work: WorkLedger,
) -> bool:
    """Confront the model with fresh observations, its own argmax included."""
    points = [candidate] + stream.take(AUDIT_POINTS - 1)
    for x in points:
        predicted = _walsh_predict(support, coefficients, x)
        work.audit_units += len(support) + 1
        if abs(predicted - objective(x)) > AUDIT_TOLERANCE:
            return False
    return True


@dataclass
class WalshLearner:
    """The mechanism under test, and -- with its own state -- the tautology control.

    Learn a Walsh representation of the scalar objective, refit its coefficients
    across generations, audit it against fresh observations, and rebuild on
    mismatch.  Nothing here sees a component, a scope or a table.
    """

    n: int
    support: tuple[int, ...] | None = None
    coefficients: tuple[float, ...] | None = None
    refused: bool = False
    elite: int | None = None

    def persistent_bytes(self) -> int:
        held = 0 if self.support is None else len(self.support) * COEFFICIENT_BYTES
        return held + (STATE_BYTES if self.elite is not None else 0)

    def generation(
        self, objective: Objective, stream: PointStream, work: WorkLedger
    ) -> GenerationOutcome:
        size = 1 << self.n
        if self.refused:
            # The parameter ceiling refused the model; measure the table.
            before = objective.calls
            for x in range(size):
                objective(x)
            work.model_search_units += size
            self.elite = objective.best_observed()
            return GenerationOutcome(
                best_x=self.elite,
                rebuilt=False,
                model_parameters=0,
                model_refused=True,
                calls=CallSplit(search=objective.calls - before),
            )

        steady = 0
        if self.support is not None:
            before = objective.calls
            fitted = _walsh_refit(objective, self.support, stream, work)
            if fitted is not None:
                candidate = _walsh_argmax(self.support, fitted, self.n, work)
                if _walsh_audit(
                    self.support, fitted, objective, stream, candidate, work
                ):
                    self.coefficients = fitted
                    self.elite = objective.best_observed()
                    return GenerationOutcome(
                        best_x=self.elite,
                        rebuilt=False,
                        model_parameters=len(self.support),
                        model_refused=False,
                        calls=CallSplit(steady_state=objective.calls - before),
                    )
            steady = objective.calls - before

        first_build = self.support is None
        before = objective.calls
        coefficients, ops = _walsh_full_transform(objective, self.n)
        if first_build:
            work.fit_units += ops
        else:
            work.invalidation_units += ops
        support = _walsh_threshold(coefficients)
        if len(support) > MODEL_PARAMETER_CEILING:
            self.support = None
            self.coefficients = None
            self.refused = True
            parameters = 0
        else:
            self.support = support
            self.coefficients = tuple(coefficients[s] for s in support)
            parameters = len(support)
        self.elite = objective.best_observed()
        spent = objective.calls - before
        split = (
            CallSplit(discovery=spent, steady_state=steady)
            if first_build
            else CallSplit(invalidation=spent, steady_state=steady)
        )
        return GenerationOutcome(
            best_x=self.elite,
            rebuilt=True,
            model_parameters=parameters,
            model_refused=self.refused,
            calls=split,
        )


def walsh_arm(n: int = N_BITS) -> WalshLearner:
    """The mechanism under test."""
    return WalshLearner(n=n)


def constructive_parent(n: int = N_BITS) -> WalshLearner:
    """The SAME algorithm with separate state.  It must tie, and that is the point.

    This is what both earlier lanes actually compared against.  It is kept here
    so that the tautology is visible beside the real comparison rather than
    argued about: ``test_indep.py`` asserts an exact tie on every coordinate,
    and an exact tie between a program and itself is not evidence.
    """
    return WalshLearner(n=n)


# --------------------------------------------------------------------------
# the exact ceiling
# --------------------------------------------------------------------------


@dataclass
class GlobalEnumerationParent:
    """Measure everything, every generation.  ``2**n`` calls; optimum by construction."""

    n: int
    elite: int | None = None

    def persistent_bytes(self) -> int:
        return (1 << self.n) * VALUE_BYTES

    def generation(
        self, objective: Objective, stream: PointStream, work: WorkLedger
    ) -> GenerationOutcome:
        before = objective.calls
        size = 1 << self.n
        for x in range(size):
            objective(x)
        work.model_search_units += size
        self.elite = objective.best_observed()
        return GenerationOutcome(
            best_x=self.elite,
            rebuilt=False,
            model_parameters=0,
            model_refused=False,
            calls=CallSplit(search=objective.calls - before),
        )


def global_enumeration_parent(n: int = N_BITS) -> GlobalEnumerationParent:
    return GlobalEnumerationParent(n=n)


# --------------------------------------------------------------------------
# the world
# --------------------------------------------------------------------------


def lifetime_landscapes(regime: Regime, rep: int) -> list[Any]:
    """Twelve landscapes for one lifetime, drawn exactly as PR #150 draws them.

    Supports persist across generations (drifting when the regime drifts) while
    the value tables are redrawn every generation.  That is what makes carried
    structure worth anything at all: the *shape* recurs, the *numbers* do not.
    """
    rng = _stream_rng(f"indep-world|{regime.name}|{rep}")
    scopes = None
    landscapes = []
    for _ in range(GENERATIONS):
        if scopes is not None and regime.drift:
            scopes = SRC.drift_scopes(scopes, N_BITS, regime.K, rng, regime.drift)
        land = SRC.NK(N_BITS, regime.K, rng, scopes=scopes)
        scopes = land.scopes
        landscapes.append(land)
    return landscapes


# --------------------------------------------------------------------------
# the sweep
# --------------------------------------------------------------------------


def _arm_factories() -> dict[str, Any]:
    """Built here so that the parents module is imported, not depended on."""
    import indep_parents

    return {
        "walsh_arm": walsh_arm,
        "constructive_parent": constructive_parent,
        "regression_parent": indep_parents.regression_parent,
        "tabu_parent": indep_parents.tabu_parent,
        "bandit_parent": indep_parents.bandit_parent,
        "global_enumeration_parent": global_enumeration_parent,
    }


def run_lifetime(
    arm: str, factory: Any, regime: Regime, rep: int, landscapes: Sequence[Any],
    optima: Sequence[float],
) -> tuple[list[GenerationRecord], WorkLedger, int]:
    """One arm, one lifetime.  Returns records, its work ledger and its bytes."""
    learner = factory(N_BITS)
    work = WorkLedger()
    records: list[GenerationRecord] = []
    for generation, (land, optimum) in enumerate(zip(landscapes, optima)):
        objective = Objective(n=N_BITS, fitness=land.fitness)
        stream = PointStream(point_stream(regime.name, rep, generation))
        outcome = learner.generation(objective, stream, work)
        value = land.fitness(outcome.best_x)  # the scorer's own read, not charged
        records.append(
            GenerationRecord(
                regime=regime.name,
                arm=arm,
                rep=rep,
                generation=generation,
                objective_calls=objective.calls,
                optimum=optimum,
                attained_value=value,
                attained=abs(value - optimum) <= 1e-12,
                rebuilt=outcome.rebuilt,
                model_parameters=outcome.model_parameters,
                model_refused=outcome.model_refused,
                calls=outcome.calls,
            )
        )
    return records, work, learner.persistent_bytes()


def sweep() -> dict[str, list[LifetimeRecord]]:
    """Every arm, every regime, every repetition, on identical landscapes."""
    factories = _arm_factories()
    out: dict[str, list[LifetimeRecord]] = {}
    for regime in REGIMES:
        worlds = [lifetime_landscapes(regime, rep) for rep in range(REPS)]
        optima = [[land.optimum() for land in w] for w in worlds]
        rows: list[LifetimeRecord] = []
        for arm, factory in factories.items():
            per_rep: list[tuple[list[GenerationRecord], WorkLedger, int]] = []
            for rep in range(REPS):
                per_rep.append(
                    run_lifetime(arm, factory, regime, rep, worlds[rep], optima[rep])
                )
            rows.append(_summarise(regime, arm, per_rep))
        out[regime.name] = rows
    return out


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _summarise(
    regime: Regime,
    arm: str,
    per_rep: Sequence[tuple[list[GenerationRecord], WorkLedger, int]],
) -> LifetimeRecord:
    lifetimes = [sum(r.objective_calls for r in recs) for recs, _, _ in per_rep]
    splits = []
    for recs, _, _ in per_rep:
        total = CallSplit()
        for r in recs:
            total = total.plus(r.calls)
        splits.append(total)
    attained = [sum(1 for r in recs if r.attained) for recs, _, _ in per_rep]
    all_records = [r for recs, _, _ in per_rep for r in recs]
    return LifetimeRecord(
        regime=regime.name,
        arm=arm,
        arm_role=ARM_ROLES[arm],
        generations=GENERATIONS,
        reps=len(per_rep),
        objective_calls=_mean(lifetimes),
        call_split={
            key: _mean([s.as_dict()[key] for s in splits])
            for key in ("discovery", "steady_state", "invalidation", "search")
        },
        optimum_attained_generations=_mean(attained),
        optimum_attained_fraction=sum(attained) / (len(per_rep) * GENERATIONS),
        mean_quality_over_optimum=_mean(
            [r.attained_value / r.optimum for r in all_records]
        ),
        fit_units=_mean([w.fit_units for _, w, _ in per_rep]),
        audit_units=_mean([w.audit_units for _, w, _ in per_rep]),
        invalidation_units=_mean([w.invalidation_units for _, w, _ in per_rep]),
        model_search_units=_mean([w.model_search_units for _, w, _ in per_rep]),
        persistent_bytes=_mean([b for _, _, b in per_rep]),
        rebuilds=_mean([sum(1 for r in recs if r.rebuilt) for recs, _, _ in per_rep]),
        model_parameters=_mean([r.model_parameters for r in all_records]),
        model_refused_fraction=(
            sum(1 for r in all_records if r.model_refused) / len(all_records)
        ),
    )


def sweep_table(results: Mapping[str, Sequence[LifetimeRecord]]) -> list[dict[str, Any]]:
    return [row.as_row() for regime in REGIMES for row in results[regime.name]]
