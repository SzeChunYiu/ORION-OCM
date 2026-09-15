from __future__ import annotations

from typing import Dict

CONTINUE = "CONTINUE"
RESET = "RESET"
TIE = "TIE"
NO_FINITE_BREAK_EVEN = "NO_FINITE_BREAK_EVEN"


def _nonnegative_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def lifecycle_costs(
    *,
    horizon: int,
    reset_per_task: int,
    continued_per_task: int,
    maintenance_revision: int,
) -> Dict[str, int | str]:
    _positive_int(horizon, "horizon")
    _nonnegative_int(reset_per_task, "reset_per_task")
    _nonnegative_int(continued_per_task, "continued_per_task")
    _nonnegative_int(maintenance_revision, "maintenance_revision")
    reset_cost = horizon * reset_per_task
    continued_cost = maintenance_revision + horizon * continued_per_task
    if continued_cost < reset_cost:
        verdict = CONTINUE
    elif continued_cost > reset_cost:
        verdict = RESET
    else:
        verdict = TIE
    return {
        "reset_cost": reset_cost,
        "continued_cost": continued_cost,
        "per_task_saving": reset_per_task - continued_per_task,
        "verdict": verdict,
    }


def strict_continue_break_even(
    *, reset_per_task: int, continued_per_task: int, maintenance_revision: int
) -> int | str:
    _nonnegative_int(reset_per_task, "reset_per_task")
    _nonnegative_int(continued_per_task, "continued_per_task")
    _nonnegative_int(maintenance_revision, "maintenance_revision")
    saving = reset_per_task - continued_per_task
    if saving <= 0:
        return NO_FINITE_BREAK_EVEN
    # Smallest integer H >= 1 satisfying H * saving > maintenance_revision.
    return maintenance_revision // saving + 1


def representation_future_cost(
    *, raw_distinctions: int, quotient_classes: int, representation_use_cost: int
) -> Dict[str, int | bool]:
    _positive_int(raw_distinctions, "raw_distinctions")
    _positive_int(quotient_classes, "quotient_classes")
    _nonnegative_int(representation_use_cost, "representation_use_cost")
    represented = quotient_classes + representation_use_cost
    return {
        "raw_acquisition_cost": raw_distinctions,
        "represented_acquisition_cost": represented,
        "per_task_saving": raw_distinctions - represented,
        "future_acquisition_cheaper": represented < raw_distinctions,
    }


def operator_future_search_cost(
    *, base_expansions: int, learned_expansions: int, verification_cost: int
) -> Dict[str, int | bool]:
    _nonnegative_int(base_expansions, "base_expansions")
    _nonnegative_int(learned_expansions, "learned_expansions")
    _nonnegative_int(verification_cost, "verification_cost")
    learned = learned_expansions + verification_cost
    return {
        "base_search_cost": base_expansions,
        "learned_operator_search_cost": learned,
        "per_task_saving": base_expansions - learned,
        "future_search_cheaper": learned < base_expansions,
    }


def prior_future_discovery_cost(
    *, base_rank: int, prior_rank: int, prior_inference_cost: int
) -> Dict[str, int | bool]:
    _positive_int(base_rank, "base_rank")
    _positive_int(prior_rank, "prior_rank")
    _nonnegative_int(prior_inference_cost, "prior_inference_cost")
    prior = prior_rank + prior_inference_cost
    return {
        "base_discovery_cost": base_rank,
        "prior_discovery_cost": prior,
        "per_task_saving": base_rank - prior,
        "future_discovery_cheaper": prior < base_rank,
    }


def representation_lifecycle_verdict(
    *,
    horizon: int,
    raw_distinctions: int,
    quotient_classes: int,
    representation_use_cost: int,
    maintenance_revision: int,
) -> Dict[str, int | str]:
    costs = representation_future_cost(
        raw_distinctions=raw_distinctions,
        quotient_classes=quotient_classes,
        representation_use_cost=representation_use_cost,
    )
    return lifecycle_costs(
        horizon=horizon,
        reset_per_task=int(costs["raw_acquisition_cost"]),
        continued_per_task=int(costs["represented_acquisition_cost"]),
        maintenance_revision=maintenance_revision,
    )


def operator_lifecycle_verdict(
    *,
    horizon: int,
    base_expansions: int,
    learned_expansions: int,
    verification_cost: int,
    maintenance_revision: int,
) -> Dict[str, int | str]:
    costs = operator_future_search_cost(
        base_expansions=base_expansions,
        learned_expansions=learned_expansions,
        verification_cost=verification_cost,
    )
    return lifecycle_costs(
        horizon=horizon,
        reset_per_task=int(costs["base_search_cost"]),
        continued_per_task=int(costs["learned_operator_search_cost"]),
        maintenance_revision=maintenance_revision,
    )


def prior_lifecycle_verdict(
    *,
    horizon: int,
    base_rank: int,
    prior_rank: int,
    prior_inference_cost: int,
    maintenance_revision: int,
) -> Dict[str, int | str]:
    costs = prior_future_discovery_cost(
        base_rank=base_rank,
        prior_rank=prior_rank,
        prior_inference_cost=prior_inference_cost,
    )
    return lifecycle_costs(
        horizon=horizon,
        reset_per_task=int(costs["base_discovery_cost"]),
        continued_per_task=int(costs["prior_discovery_cost"]),
        maintenance_revision=maintenance_revision,
    )
