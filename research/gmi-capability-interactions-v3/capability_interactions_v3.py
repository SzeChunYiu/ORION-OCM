"""Exact finite witnesses for issue #602 F3 capability interactions, tranche 3."""

from __future__ import annotations


def joint_threshold_success(*, capacity_a: int, capacity_b: int, threshold: int) -> bool:
    if capacity_a < 1 or capacity_b < 1 or threshold < 1:
        raise ValueError("capacities and threshold must be positive")
    return capacity_a * capacity_b >= threshold


def joint_only_emergence(*, a0: int, a1: int, b0: int, b1: int, threshold: int) -> bool:
    if min(a0, a1, b0, b1, threshold) < 1:
        raise ValueError("capacities and threshold must be positive")
    if a1 < a0 or b1 < b0:
        raise ValueError("upgrades must weakly increase their capacities")
    u00 = joint_threshold_success(capacity_a=a0, capacity_b=b0, threshold=threshold)
    u10 = joint_threshold_success(capacity_a=a1, capacity_b=b0, threshold=threshold)
    u01 = joint_threshold_success(capacity_a=a0, capacity_b=b1, threshold=threshold)
    u11 = joint_threshold_success(capacity_a=a1, capacity_b=b1, threshold=threshold)
    return (not u00) and (not u10) and (not u01) and u11


def discrete_interaction_indicator(*, a0: int, a1: int, b0: int, b1: int, threshold: int) -> int:
    """Second finite difference of the binary success indicator."""
    if min(a0, a1, b0, b1, threshold) < 1:
        raise ValueError("capacities and threshold must be positive")
    if a1 < a0 or b1 < b0:
        raise ValueError("upgrades must weakly increase their capacities")
    u00 = int(joint_threshold_success(capacity_a=a0, capacity_b=b0, threshold=threshold))
    u10 = int(joint_threshold_success(capacity_a=a1, capacity_b=b0, threshold=threshold))
    u01 = int(joint_threshold_success(capacity_a=a0, capacity_b=b1, threshold=threshold))
    u11 = int(joint_threshold_success(capacity_a=a1, capacity_b=b1, threshold=threshold))
    return u11 - u10 - u01 + u00


def capability_a_success(*, total_budget: int, required_budget: int, mandatory_other_cost: int = 0) -> bool:
    if total_budget < 0 or mandatory_other_cost < 0 or required_budget < 1:
        raise ValueError("budget/cost must be nonnegative and requirement positive")
    available = max(0, total_budget - mandatory_other_cost)
    return available >= required_budget


def interference_occurs(*, total_budget: int, required_budget: int, mandatory_other_cost: int) -> bool:
    before = capability_a_success(
        total_budget=total_budget,
        required_budget=required_budget,
        mandatory_other_cost=0,
    )
    after = capability_a_success(
        total_budget=total_budget,
        required_budget=required_budget,
        mandatory_other_cost=mandatory_other_cost,
    )
    return before and not after


def optional_extension_optimum(old_values: tuple[float, ...], new_values: tuple[float, ...]) -> float:
    """Best value after a free optional extension; the old feasible set is retained."""
    if not old_values:
        raise ValueError("old feasible set must be nonempty")
    return max(old_values + new_values)
