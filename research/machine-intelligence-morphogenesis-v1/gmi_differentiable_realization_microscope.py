"""Differentiable-optimization DS-E1 calibration for GMI demand/response.

The objective family is a positive-definite diagonal quadratic with condition number
`kappa`. Both candidate update laws receive the same exact gradient oracle:

* VANILLA_GD: fixed step 1/L, no build cost.
* EXACT_PRECONDITIONED: pay a dense O(d^3) factorization/build cost, then apply an
  exact inverse-Hessian preconditioner at O(d^2) per task.

The cost constants are an authored calibration model. The mathematical point is
parent-owned numerical optimization: feedback availability is not the same thing as
how efficiently a realization can exploit it, and reuse horizon can amortize a
build-heavy optimizer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuadraticWorld:
    dimension: int
    condition_number: float
    objective_tolerance: float
    task_horizon: int

    def __post_init__(self) -> None:
        if self.dimension < 2:
            raise ValueError("dimension must be >= 2")
        if self.condition_number < 1.0:
            raise ValueError("condition_number must be >= 1")
        if not 0.0 < self.objective_tolerance < 0.5:
            raise ValueError("objective_tolerance must be in (0, 0.5)")
        if self.task_horizon < 1:
            raise ValueError("task_horizon must be >= 1")


@dataclass(frozen=True)
class OptimizerCost:
    name: str
    build: float
    per_task: float
    horizon: int

    @property
    def total(self) -> float:
        return self.build + self.horizon * self.per_task


def vanilla_gd_objective_after_steps(world: QuadraticWorld, steps: int) -> float:
    """Objective from x0=(1,...,1), A=diag(1,kappa,...,kappa), step=1/kappa."""

    if steps < 0:
        raise ValueError("steps must be non-negative")
    d = world.dimension
    kappa = world.condition_number
    if steps == 0:
        return 0.5 * (1.0 + (d - 1) * kappa)
    # High-curvature coordinates are zero after one exact step. The slow coordinate
    # contracts by 1 - 1/kappa each step.
    if kappa == 1.0:
        return 0.0
    contraction = 1.0 - 1.0 / kappa
    return 0.5 * (contraction ** (2 * steps))


def vanilla_gd_iterations(world: QuadraticWorld) -> int:
    steps = 0
    while vanilla_gd_objective_after_steps(world, steps) > world.objective_tolerance:
        steps += 1
        if steps > 10_000_000:
            raise RuntimeError("iteration calibration exceeded safety limit")
    return steps


def vanilla_gd_cost(world: QuadraticWorld) -> OptimizerCost:
    iterations = vanilla_gd_iterations(world)
    # One diagonal gradient/update touch per coordinate per iteration.
    per_task = float(world.dimension * iterations)
    return OptimizerCost(
        name="VANILLA_GD",
        build=0.0,
        per_task=per_task,
        horizon=world.task_horizon,
    )


def exact_preconditioned_cost(world: QuadraticWorld) -> OptimizerCost:
    d = world.dimension
    # Deliberately use a generic dense factorization/apply accounting model even
    # though the authored fixture is diagonal. This represents a build-heavy native
    # response and is not claimed as the optimal implementation for the fixture.
    return OptimizerCost(
        name="EXACT_PRECONDITIONED",
        build=float(d ** 3),
        per_task=float(d ** 2),
        horizon=world.task_horizon,
    )


def preferred_update_law(world: QuadraticWorld) -> tuple[str, ...]:
    candidates = (vanilla_gd_cost(world), exact_preconditioned_cost(world))
    best = min(c.total for c in candidates)
    return tuple(sorted(c.name for c in candidates if c.total == best))


def real_horizon_crossover(dimension: int, condition_number: float, tolerance: float) -> float | None:
    probe = QuadraticWorld(dimension, condition_number, tolerance, 1)
    gd = vanilla_gd_cost(probe)
    pre = exact_preconditioned_cost(probe)
    savings_per_task = gd.per_task - pre.per_task
    if savings_per_task <= 0:
        return None
    return pre.build / savings_per_task


def calibration_receipt() -> dict:
    one_task = QuadraticWorld(20, 100.0, 1e-3, 1)
    two_tasks = QuadraticWorld(20, 100.0, 1e-3, 2)
    low_condition = QuadraticWorld(20, 2.0, 1e-3, 2)

    def row(world: QuadraticWorld) -> dict:
        gd = vanilla_gd_cost(world)
        pre = exact_preconditioned_cost(world)
        return {
            "dimension": world.dimension,
            "condition_number": world.condition_number,
            "objective_tolerance": world.objective_tolerance,
            "task_horizon": world.task_horizon,
            "gradient_feedback_channel": "EXACT_FULL_GRADIENT",
            "vanilla_gd_iterations_per_task": vanilla_gd_iterations(world),
            "VANILLA_GD": {"build": gd.build, "per_task": gd.per_task, "total": gd.total},
            "EXACT_PRECONDITIONED": {"build": pre.build, "per_task": pre.per_task, "total": pre.total},
            "winner": preferred_update_law(world),
        }

    return {
        "schema": "GMIDifferentiableRealizationMicroscopeV1",
        "family": "strongly-convex differentiable quadratic optimization",
        "rows": {
            "KAPPA100_H1": row(one_task),
            "KAPPA100_H2": row(two_tasks),
            "KAPPA2_H2": row(low_condition),
        },
        "kappa100_real_horizon_crossover": real_horizon_crossover(20, 100.0, 1e-3),
        "demand_response_boundary": {
            "obligation_phi": "same exact full-gradient channel for both update laws",
            "native_geometry": "condition number / curvature spectrum",
            "morphology_response": "ability to exploit geometry through preconditioning versus cheap vanilla updates",
        },
        "terminal": "DIFFERENTIABLE_NATIVE_CONDITIONING_AND_AMORTIZATION_CALIBRATED",
        "claim_boundary": (
            "Numerical-optimization calibration only; not a neural architecture law. "
            "Real neural DS-E1 must compare current training-free/native predictors."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
