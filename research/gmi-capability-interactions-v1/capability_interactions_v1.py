"""Exact finite witnesses for issue #602 F3 capability interactions, tranche 1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryPlanningInstance:
    cue_classes: int
    memory_states: int
    required_horizon: int
    planning_horizon: int

    def validate(self) -> None:
        if min(self.cue_classes, self.memory_states, self.required_horizon, self.planning_horizon) < 1:
            raise ValueError("all cardinalities/horizons must be positive")

    def exact_success_possible(self) -> bool:
        self.validate()
        return self.memory_states >= self.cue_classes and self.planning_horizon >= self.required_horizon


def abstraction_required_states(raw_to_class: tuple[int, ...], obligations: tuple[int, ...]) -> int | None:
    """Return exact quotient size when abstraction preserves obligations, else None.

    Every raw item in one abstraction class must have the same obligation.  Empty
    class labels are harmless; only represented classes count.
    """
    if not raw_to_class or len(raw_to_class) != len(obligations):
        raise ValueError("nonempty aligned raw_to_class and obligations are required")
    class_to_obligation: dict[int, int] = {}
    for cls, obligation in zip(raw_to_class, obligations):
        if cls in class_to_obligation and class_to_obligation[cls] != obligation:
            return None
        class_to_obligation[cls] = obligation
    return len(class_to_obligation)


def heuristic_net_saving(*, baseline_cost: int, heuristic_cost: int, learn_cost: int, reuse: int) -> int:
    """Positive means the learned heuristic is cheaper over ``reuse`` uses."""
    if min(baseline_cost, heuristic_cost, learn_cost, reuse) < 0:
        raise ValueError("costs and reuse must be nonnegative")
    if heuristic_cost > baseline_cost:
        # The algebra still works, but this helper is deliberately scoped to a
        # heuristic that weakly reduces verified search burden.
        raise ValueError("heuristic_cost must not exceed baseline_cost in this theorem scope")
    return reuse * (baseline_cost - heuristic_cost) - learn_cost


def heuristic_verdict(*, baseline_cost: int, heuristic_cost: int, learn_cost: int, reuse: int) -> str:
    delta = heuristic_net_saving(
        baseline_cost=baseline_cost,
        heuristic_cost=heuristic_cost,
        learn_cost=learn_cost,
        reuse=reuse,
    )
    if delta > 0:
        return "RETAIN_HEURISTIC"
    if delta < 0:
        return "SEARCH_PLAIN"
    return "TIE"


def social_communication_cells(*, social_states: int, message_symbols: int) -> int:
    if social_states < 1 or message_symbols < 1:
        raise ValueError("social_states and message_symbols must be positive")
    return social_states * message_symbols


def social_communication_exact_possible(*, social_states: int, message_symbols: int, obligation_cells: int) -> bool:
    if obligation_cells < 1:
        raise ValueError("obligation_cells must be positive")
    return obligation_cells <= social_communication_cells(
        social_states=social_states,
        message_symbols=message_symbols,
    )


def memory_planning_truth_table(max_cues: int = 4, max_horizon: int = 4) -> tuple[tuple[int, int, int, int, bool], ...]:
    rows = []
    for n in range(1, max_cues + 1):
        for k in range(1, max_cues + 1):
            for h in range(1, max_horizon + 1):
                for d in range(1, max_horizon + 1):
                    inst = MemoryPlanningInstance(n, k, h, d)
                    rows.append((n, k, h, d, inst.exact_success_possible()))
    return tuple(rows)
