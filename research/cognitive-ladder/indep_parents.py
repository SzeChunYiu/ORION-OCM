"""The four independently implemented parents.  These are the point of E8.

Every parent here was written from the standard description of its own method
and reaches the objective by a genuinely different route.  None of them imports,
calls, subclasses or reads any part of the arm's fitting, auditing or
model-search machinery; the only things they share with the arm are the
landscape and the scalar objective call, which is what "same information" means.
``test_indep.py`` enforces that structurally, by inspecting this module's source
and its import graph rather than by taking this paragraph's word for it.

The four
--------

``regression_parent``
    A sparse linear-plus-interaction surrogate over the **multilinear monomial**
    basis in the 0/1 variables -- ``1``, ``x_i``, ``x_i x_j``, ``x_i x_j x_k``,
    and so on -- fitted by ordinary least squares over observed assignments, then
    optimised.  Different representation (monomials, not characters), different
    identification procedure (an exactly-determined batch solve with degree
    escalation, not a transform of the whole table), different discovery cost.
    It keeps its selected features across generations and refits them, so it has
    exactly the amortization opportunity the arm has.  It optimises its
    surrogate **exhaustively**, so nothing it fails to find can be blamed on a
    weak inner optimiser.

``tabu_parent``
    No model at all: memory-based local search.  Best-neighbour moves under a
    tabu tenure, restarts on stagnation, and the two best assignments carried
    across generations as restart seeds.  Its budget is the full information
    ceiling of ``2**n`` distinct evaluations, which is the most any arm can be
    given, so it cannot have been starved.

``bandit_parent``
    Treats each bit as an arm and identifies good bit flips by **successive
    halving** against shared random backgrounds -- the standard best-arm
    identification race, doubling the context count as the field halves -- then
    constructs an incumbent in the surviving order and polishes it.  It carries
    the bit order and the incumbent across generations.  Also budgeted to the
    ceiling.

``global_enumeration_parent``
    Lives in ``indep`` beside the meters because it *is* a meter: the exact
    ``2**n`` ceiling, attaining the optimum by construction.

On not tuning a parent down
---------------------------

A parent that loses because it was given a smaller budget or a worse
hyperparameter policy than the arm produces ``PARENT_UNDERTUNED``, and a
comparison in that state is inadmissible regardless of which way it points.  So
the policies are declared in ``indep.SEARCH_POLICY``, they are the standard ones
for each method, every parent gets the ceiling as its budget, every parent gets
the same audit budget and the same model-parameter ceiling the arm gets, and the
model-based parent gets an exhaustive inner optimiser.  Where a parent still
loses, the loss is the method's and the receipt says which coordinate it is on.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from indep import (
    AUDIT_POINTS,
    AUDIT_TOLERANCE,
    COEFFICIENT_BYTES,
    COEFFICIENT_TOLERANCE,
    MODEL_PARAMETER_CEILING,
    N_BITS,
    STATE_BYTES,
    CallSplit,
    GenerationOutcome,
    Objective,
    PointStream,
    WorkLedger,
)

__all__ = [
    "RegressionParent",
    "TabuParent",
    "BanditParent",
    "regression_parent",
    "tabu_parent",
    "bandit_parent",
    "TABU_TENURE",
    "TABU_STALL",
    "TABU_PATIENCE",
    "TABU_ELITES",
    "BANDIT_BASE_CONTEXTS",
    "BANDIT_PATIENCE",
    "REGRESSION_DESIGN_GROWTH",
    "REGRESSION_DESIGN_SLACK",
    "monomial",
    "features_up_to_degree",
]


# --------------------------------------------------------------------------
# declared hyperparameters, all standard for their methods
# --------------------------------------------------------------------------

#: How many moves a flipped bit stays forbidden.  The textbook small tenure.
TABU_TENURE = 3
#: Non-improving moves tolerated before a restart.
TABU_STALL = 16
#: Non-improving restarts tolerated before the generation ends.
TABU_PATIENCE = 8
#: Best assignments carried between generations as restart seeds.
TABU_ELITES = 2

#: Backgrounds sampled per bit in the first round of the race; doubled each
#: time the field halves, which is what successive halving prescribes.
BANDIT_BASE_CONTEXTS = 2
#: Non-improving races tolerated before the generation ends.
BANDIT_PATIENCE = 4

#: The design may grow to this multiple of the feature count (plus the constant
#: below) while it fails to determine the coefficients, after which the fit is
#: abandoned and the surrogate is rediscovered.  This is deliberately the SAME
#: allowance the arm gives its own refit, so neither can be said to have been
#: given a more forgiving repair budget than the other.
REGRESSION_DESIGN_GROWTH = 3
REGRESSION_DESIGN_SLACK = 8


# --------------------------------------------------------------------------
# the monomial basis
# --------------------------------------------------------------------------


def monomial(mask: int, x: int) -> float:
    """The product of the variables in ``mask``: 1 when all of them are set."""
    return 1.0 if (x & mask) == mask else 0.0


@lru_cache(maxsize=None)
def features_up_to_degree(n: int, degree: int) -> tuple[int, ...]:
    """Every monomial of degree at most ``degree``, low degree first."""
    return tuple(
        sorted(
            (m for m in range(1 << n) if bin(m).count("1") <= degree),
            key=lambda m: (bin(m).count("1"), m),
        )
    )


def _solve_design(
    design: Sequence[Sequence[float]], rhs: Sequence[float], p: int
) -> tuple[list[float] | None, int]:
    """Batch rank-revealing Gaussian elimination over the whole design.

    The design may be square or taller than it is wide; the pivot for each
    column is searched over every remaining row rather than only the diagonal,
    which is both the numerically sound choice and what lets an extra
    observation rescue a design that a monomial basis left rank deficient.
    ``None`` means the design still does not determine the coefficients, so the
    caller can buy another observation rather than be handed a least-norm answer
    it did not ask for.
    """
    rows = [list(r) + [v] for r, v in zip(design, rhs)]
    ops = 0
    used = 0
    for col in range(p):
        pivot, best = None, 1e-9
        for r in range(used, len(rows)):
            magnitude = abs(rows[r][col])
            if magnitude > best:
                best, pivot = magnitude, r
        if pivot is None:
            return None, ops
        rows[used], rows[pivot] = rows[pivot], rows[used]
        base = rows[used]
        inv = 1.0 / base[col]
        for r in range(used + 1, len(rows)):
            target = rows[r]
            factor = target[col] * inv
            if factor == 0.0:
                continue
            for c in range(col, p + 1):
                target[c] -= factor * base[c]
            ops += p + 1 - col
        used += 1
    solution = [0.0] * p
    for col in reversed(range(p)):
        row = rows[col]
        acc = row[p] - math.fsum(row[c] * solution[c] for c in range(col + 1, p))
        solution[col] = acc / row[col]
        ops += p - col
    return solution, ops


# --------------------------------------------------------------------------
# regression_parent
# --------------------------------------------------------------------------


@dataclass
class RegressionParent:
    """Sparse linear-plus-interaction surrogate, ordinary least squares.

    Route: pick the smallest interaction degree whose monomial model survives a
    confrontation with fresh observations, fit it by least squares on an
    exactly-determined design, prune the structural zeros, carry the surviving
    feature set forward, and refit it each generation.  Optimise by scanning the
    surrogate over the whole assignment space.

    Nothing about the arm's representation, transform, threshold rule, refit or
    audit routine is reachable from here.
    """

    n: int
    features: tuple[int, ...] | None = None
    weights: tuple[float, ...] | None = None
    refused: bool = False
    elite: int | None = None

    # -- state ------------------------------------------------------------

    def persistent_bytes(self) -> int:
        held = 0 if self.features is None else len(self.features) * COEFFICIENT_BYTES
        return held + (STATE_BYTES if self.elite is not None else 0)

    # -- surrogate --------------------------------------------------------

    def _predict(self, x: int) -> float:
        return math.fsum(
            w for m, w in zip(self.features, self.weights) if (x & m) == m
        )

    def _surrogate_optimum(self, work: WorkLedger) -> int:
        """Exhaustive scan of the surrogate.  No inner-optimiser handicap."""
        size = 1 << self.n
        work.model_search_units += size * max(1, len(self.features))
        best_x, best_v = 0, -math.inf
        for x in range(size):
            v = self._predict(x)
            if v > best_v:
                best_x, best_v = x, v
        return best_x

    def _least_squares(
        self,
        objective: Objective,
        features: Sequence[int],
        stream: PointStream,
        work: WorkLedger,
        invalidating: bool = False,
    ) -> tuple[float, ...] | None:
        """OLS over observed assignments, starting from an exactly-determined design.

        The design begins with as many observations as there are features and
        grows by one observation at a time while it fails to determine the
        coefficients -- a monomial column can be all-zero on a small sample in a
        way a character column cannot, and paying for the extra observation is
        the honest fix.  So the parent's objective cost is ``|features|`` plus
        exactly what a rank deficiency actually costs, never a fixed slack
        allowance chosen to be safe.

        ``invalidating`` books the arithmetic on the invalidation coordinate
        instead of the fitting one, so re-deriving a discarded model is never
        booked as ordinary fitting.
        """
        p = len(features)
        if p == 0:
            return ()
        limit = min(
            1 << objective.n, REGRESSION_DESIGN_GROWTH * p + REGRESSION_DESIGN_SLACK
        )
        # Reuse observations already paid for this generation before buying new
        # ones.  Degree escalation would otherwise re-buy the whole design at
        # every degree, and a parent that throws away its own data is a parent
        # that was tuned down.
        points = list(objective.cache)[:p]
        while len(points) < p:
            points.append(stream.next())
        while True:
            design = [[monomial(m, x) for m in features] for x in points]
            rhs = [objective(x) for x in points]
            solution, ops = _solve_design(design, rhs, p)
            if invalidating:
                work.invalidation_units += ops
            else:
                work.fit_units += ops
            if solution is not None:
                return tuple(solution)
            if len(points) >= limit:
                return None
            points = points + [stream.next()]

    def _confront(
        self,
        objective: Objective,
        stream: PointStream,
        candidate: int,
        work: WorkLedger,
    ) -> bool:
        """Fresh observations against the surrogate, its own argmax included."""
        for x in [candidate] + stream.take(AUDIT_POINTS - 1):
            work.audit_units += len(self.features) + 1
            if abs(self._predict(x) - objective(x)) > AUDIT_TOLERANCE:
                return False
        return True

    # -- one generation ---------------------------------------------------

    def generation(
        self, objective: Objective, stream: PointStream, work: WorkLedger
    ) -> GenerationOutcome:
        size = 1 << self.n
        if self.refused:
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
        if self.features is not None:
            before = objective.calls
            fitted = self._least_squares(objective, self.features, stream, work)
            if fitted is not None:
                self.weights = fitted
                candidate = self._surrogate_optimum(work)
                if self._confront(objective, stream, candidate, work):
                    self.elite = objective.best_observed()
                    return GenerationOutcome(
                        best_x=self.elite,
                        rebuilt=False,
                        model_parameters=len(self.features),
                        model_refused=False,
                        calls=CallSplit(steady_state=objective.calls - before),
                    )
            steady = objective.calls - before

        first_build = self.features is None
        before = objective.calls
        held = self._rediscover(objective, stream, work, first_build)
        spent = objective.calls - before
        split = (
            CallSplit(discovery=spent, steady_state=steady)
            if first_build
            else CallSplit(invalidation=spent, steady_state=steady)
        )
        return GenerationOutcome(
            best_x=self.elite,
            rebuilt=True,
            model_parameters=held,
            model_refused=self.refused,
            calls=split,
        )

    def _rediscover(
        self,
        objective: Objective,
        stream: PointStream,
        work: WorkLedger,
        first_build: bool,
    ) -> int:
        """Escalate the interaction degree until the surrogate survives, or refuse."""
        for degree in range(1, self.n + 1):
            features = features_up_to_degree(self.n, degree)
            if len(features) > MODEL_PARAMETER_CEILING:
                break
            self.features = features
            fitted = self._least_squares(
                objective, features, stream, work, invalidating=not first_build
            )
            if fitted is None:
                continue
            self.weights = fitted
            candidate = self._surrogate_optimum(work)
            if self._confront(objective, stream, candidate, work):
                kept = tuple(
                    (m, w)
                    for m, w in zip(features, fitted)
                    if abs(w) > COEFFICIENT_TOLERANCE
                )
                self.features = tuple(m for m, _ in kept)
                self.weights = tuple(w for _, w in kept)
                self.elite = objective.best_observed()
                return len(self.features)
        # No admissible surrogate under the shared parameter ceiling.
        self.features = None
        self.weights = None
        self.refused = True
        size = 1 << self.n
        for x in range(size):
            objective(x)
        work.model_search_units += size
        self.elite = objective.best_observed()
        return 0


def regression_parent(n: int = N_BITS) -> RegressionParent:
    return RegressionParent(n=n)


# --------------------------------------------------------------------------
# tabu_parent
# --------------------------------------------------------------------------


@dataclass
class TabuParent:
    """Memory-based local search.  No model, no fitting, no audit.

    The only thing it remembers between generations is where the good
    assignments were, which is the weakest form of carried structure available
    and therefore the right control for a mechanism whose whole claim is that
    carrying structure pays.
    """

    n: int
    elites: tuple[int, ...] = ()

    def persistent_bytes(self) -> int:
        return len(self.elites) * STATE_BYTES

    def _descend(
        self,
        objective: Objective,
        work: WorkLedger,
        start: int,
        ceiling: int,
    ) -> tuple[int, float]:
        x = start
        fx = objective(x)
        best_x, best_v = x, fx
        tabu: dict[int, int] = {}
        step = 0
        stall = 0
        while stall < TABU_STALL and objective.calls < ceiling:
            step += 1
            move_bit, move_x, move_v = None, None, -math.inf
            for bit in range(self.n):
                if tabu.get(bit, -1) > step:
                    continue
                y = x ^ (1 << bit)
                vy = objective(y)
                work.model_search_units += 1
                if vy > move_v:
                    move_bit, move_x, move_v = bit, y, vy
            if move_bit is None:
                break
            x, fx = move_x, move_v
            tabu[move_bit] = step + TABU_TENURE
            if fx > best_v + 1e-15:
                best_x, best_v, stall = x, fx, 0
            else:
                stall += 1
        return best_x, best_v

    def generation(
        self, objective: Objective, stream: PointStream, work: WorkLedger
    ) -> GenerationOutcome:
        ceiling = 1 << self.n
        before = objective.calls
        seeds = list(self.elites)
        best_v = -math.inf
        stall = 0
        while objective.calls < ceiling:
            start = seeds.pop(0) if seeds else stream.next()
            _, value = self._descend(objective, work, start, ceiling)
            if value > best_v + 1e-15:
                best_v, stall = value, 0
            else:
                stall += 1
            if not seeds and stall >= TABU_PATIENCE:
                break
        self.elites = objective.top_observed(TABU_ELITES)
        return GenerationOutcome(
            best_x=objective.best_observed(),
            rebuilt=False,
            model_parameters=0,
            model_refused=False,
            calls=CallSplit(search=objective.calls - before),
        )


def tabu_parent(n: int = N_BITS) -> TabuParent:
    return TabuParent(n=n)


# --------------------------------------------------------------------------
# bandit_parent
# --------------------------------------------------------------------------


@dataclass
class BanditParent:
    """Each bit is an arm; successive halving races bit flips.

    A round evaluates every surviving bit's flip against the same freshly drawn
    backgrounds, scores each bit by its mean flip gain, discards the weaker half
    and doubles the number of backgrounds -- the standard sequential-halving
    budget allocation.  The surviving order is then used to construct an
    incumbent greedily and polish it.  There is no model of the objective
    anywhere in this class.
    """

    n: int
    order: tuple[int, ...] = ()
    elite: int | None = None

    def persistent_bytes(self) -> int:
        return len(self.order) * STATE_BYTES + (
            STATE_BYTES if self.elite is not None else 0
        )

    def _race(
        self,
        objective: Objective,
        stream: PointStream,
        work: WorkLedger,
        ceiling: int,
    ) -> list[int]:
        active = list(range(self.n))
        contexts = BANDIT_BASE_CONTEXTS
        eliminated: list[int] = []
        while len(active) > 1 and objective.calls < ceiling:
            score = {bit: 0.0 for bit in active}
            for _ in range(contexts):
                if objective.calls >= ceiling:
                    break
                x = stream.next()
                fx = objective(x)
                for bit in active:
                    score[bit] += objective(x ^ (1 << bit)) - fx
                work.model_search_units += len(active)
            active.sort(key=lambda bit: (score[bit], -bit))
            cut = len(active) // 2
            eliminated.extend(active[:cut])
            active = active[cut:]
            contexts *= 2
        eliminated.extend(active)
        return list(reversed(eliminated))

    def _construct(
        self,
        objective: Objective,
        work: WorkLedger,
        order: Sequence[int],
        start: int,
        ceiling: int,
    ) -> int:
        x = start
        fx = objective(x)
        for bit in order:
            if objective.calls >= ceiling:
                break
            y = x ^ (1 << bit)
            fy = objective(y)
            work.model_search_units += 1
            if fy > fx + 1e-15:
                x, fx = y, fy
        return x

    def _polish(
        self, objective: Objective, work: WorkLedger, start: int, ceiling: int
    ) -> tuple[int, float]:
        x = start
        fx = objective(x)
        improved = True
        while improved and objective.calls < ceiling:
            improved = False
            for bit in range(self.n):
                y = x ^ (1 << bit)
                fy = objective(y)
                work.model_search_units += 1
                if fy > fx + 1e-15:
                    x, fx, improved = y, fy, True
        return x, fx

    def generation(
        self, objective: Objective, stream: PointStream, work: WorkLedger
    ) -> GenerationOutcome:
        ceiling = 1 << self.n
        before = objective.calls
        best_v = -math.inf
        stall = 0
        seeded = self.elite
        while objective.calls < ceiling and stall < BANDIT_PATIENCE:
            order = self._race(objective, stream, work, ceiling)
            self.order = tuple(order)
            start = seeded if seeded is not None else stream.next()
            seeded = None
            incumbent = self._construct(objective, work, order, start, ceiling)
            _, value = self._polish(objective, work, incumbent, ceiling)
            if value > best_v + 1e-15:
                best_v, stall = value, 0
            else:
                stall += 1
        self.elite = objective.best_observed()
        return GenerationOutcome(
            best_x=self.elite,
            rebuilt=False,
            model_parameters=0,
            model_refused=False,
            calls=CallSplit(search=objective.calls - before),
        )


def bandit_parent(n: int = N_BITS) -> BanditParent:
    return BanditParent(n=n)
