from __future__ import annotations

from typing import Dict, Mapping, Tuple

EXPAND = "EXPAND"
KEEP = "KEEP"
PRUNE = "PRUNE"
COMPILE = "COMPILE"
INTERPRET = "INTERPRET"
LOCAL = "LOCAL"
GLOBAL = "GLOBAL"
TIE = "TIE"


def _nonnegative(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _positive(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _verdict(lower_name: str, upper_name: str, lower_cost: int, upper_cost: int) -> str:
    if lower_cost < upper_cost:
        return lower_name
    if lower_cost > upper_cost:
        return upper_name
    return TIE


def expansion_verdict(
    *,
    horizon: int,
    current_loss_per_task: int,
    expanded_loss_per_task: int,
    expansion_cost: int,
    expanded_maintenance_per_task: int,
) -> Dict[str, int | str]:
    """Compare retaining current morphology with an architecture expansion."""
    _positive(horizon, "horizon")
    for value, name in (
        (current_loss_per_task, "current_loss_per_task"),
        (expanded_loss_per_task, "expanded_loss_per_task"),
        (expansion_cost, "expansion_cost"),
        (expanded_maintenance_per_task, "expanded_maintenance_per_task"),
    ):
        _nonnegative(value, name)
    keep_cost = horizon * current_loss_per_task
    expand_cost = expansion_cost + horizon * (
        expanded_loss_per_task + expanded_maintenance_per_task
    )
    return {
        "keep_cost": keep_cost,
        "expand_cost": expand_cost,
        "verdict": _verdict(EXPAND, KEEP, expand_cost, keep_cost),
    }


def pruning_verdict(
    *,
    horizon: int,
    maintenance_per_task: int,
    keep_loss_per_task: int,
    post_prune_loss_per_task: int,
    prune_cost: int,
) -> Dict[str, int | str]:
    """Compare keeping old structure with pruning it."""
    _positive(horizon, "horizon")
    for value, name in (
        (maintenance_per_task, "maintenance_per_task"),
        (keep_loss_per_task, "keep_loss_per_task"),
        (post_prune_loss_per_task, "post_prune_loss_per_task"),
        (prune_cost, "prune_cost"),
    ):
        _nonnegative(value, name)
    keep_cost = horizon * (maintenance_per_task + keep_loss_per_task)
    prune_total = prune_cost + horizon * post_prune_loss_per_task
    return {
        "keep_cost": keep_cost,
        "prune_cost": prune_total,
        "verdict": _verdict(PRUNE, KEEP, prune_total, keep_cost),
    }


def self_compilation_verdict(
    *,
    reuse: int,
    interpreted_cost_per_use: int,
    compiled_cost_per_use: int,
    compile_cost: int,
    verification_cost_per_use: int,
) -> Dict[str, int | str]:
    _positive(reuse, "reuse")
    for value, name in (
        (interpreted_cost_per_use, "interpreted_cost_per_use"),
        (compiled_cost_per_use, "compiled_cost_per_use"),
        (compile_cost, "compile_cost"),
        (verification_cost_per_use, "verification_cost_per_use"),
    ):
        _nonnegative(value, name)
    interpret_total = reuse * interpreted_cost_per_use
    compile_total = compile_cost + reuse * (
        compiled_cost_per_use + verification_cost_per_use
    )
    return {
        "interpret_total": interpret_total,
        "compile_total": compile_total,
        "verdict": _verdict(COMPILE, INTERPRET, compile_total, interpret_total),
    }


def local_morphogenesis_verdict(
    *,
    horizon: int,
    global_rebuild_cost: int,
    local_patch_cost: int,
    local_verification_cost: int,
    local_residual_loss_per_task: int,
    local_obligation_sufficient: bool,
) -> Dict[str, int | str | bool]:
    _positive(horizon, "horizon")
    for value, name in (
        (global_rebuild_cost, "global_rebuild_cost"),
        (local_patch_cost, "local_patch_cost"),
        (local_verification_cost, "local_verification_cost"),
        (local_residual_loss_per_task, "local_residual_loss_per_task"),
    ):
        _nonnegative(value, name)
    if not isinstance(local_obligation_sufficient, bool):
        raise ValueError("local_obligation_sufficient must be boolean")
    local_total = local_patch_cost + local_verification_cost + horizon * local_residual_loss_per_task
    if not local_obligation_sufficient:
        verdict = GLOBAL
    else:
        verdict = _verdict(LOCAL, GLOBAL, local_total, global_rebuild_cost)
    return {
        "local_total": local_total,
        "global_total": global_rebuild_cost,
        "local_obligation_sufficient": local_obligation_sufficient,
        "verdict": verdict,
    }


def generation_burden_trajectory(
    *,
    initial_burden: int,
    inherited_reduction: int,
    maintenance: int,
    generations: int,
) -> Tuple[int, ...]:
    """Exact bounded recurrence b[g+1] = max(0,b[g]-s) + m."""
    _nonnegative(initial_burden, "initial_burden")
    _nonnegative(inherited_reduction, "inherited_reduction")
    _nonnegative(maintenance, "maintenance")
    _nonnegative(generations, "generations")
    values = [initial_burden]
    for _ in range(generations):
        values.append(max(0, values[-1] - inherited_reduction) + maintenance)
    return tuple(values)


def finite_state_cycle_certificate(
    transition: Mapping[str, str], start: str
) -> Dict[str, object]:
    """Pigeonhole certificate for deterministic finite developmental dynamics."""
    if not transition:
        raise ValueError("transition map must be nonempty")
    states = set(transition)
    if start not in states:
        raise ValueError("unknown start state")
    if any(dst not in states for dst in transition.values()):
        raise ValueError("transition map must be closed on its registered state set")
    seen: Dict[str, int] = {}
    trajectory = []
    current = start
    while current not in seen:
        seen[current] = len(trajectory)
        trajectory.append(current)
        if len(trajectory) > len(states):
            raise AssertionError("finite deterministic trajectory exceeded state count without repeat")
        current = transition[current]
    cycle_start = seen[current]
    cycle = trajectory[cycle_start:]
    return {
        "state_count": len(states),
        "distinct_before_repeat": len(trajectory),
        "repeat_state": current,
        "prefix_length": cycle_start,
        "cycle_length": len(cycle),
        "trajectory_before_repeat": tuple(trajectory),
        "cycle": tuple(cycle),
        "open_ended_distinct_state_growth_possible": False,
    }
