"""Exact finite witnesses for issue #602 F3 capability interactions, tranche 2."""

from __future__ import annotations


def teaching_cells(*, prior_classes: int, transcript_symbols: int) -> int:
    if prior_classes < 1 or transcript_symbols < 1:
        raise ValueError("prior_classes and transcript_symbols must be positive")
    return prior_classes * transcript_symbols


def next_cultural_repertoire(*, current: int, teaching_capacity: int, novel_discoveries: int) -> int:
    if min(current, teaching_capacity, novel_discoveries) < 0:
        raise ValueError("repertoire, capacity and discoveries must be nonnegative")
    return min(current, teaching_capacity) + novel_discoveries


def cultural_growth_possible(*, current: int, teaching_capacity: int, novel_discoveries: int) -> bool:
    return next_cultural_repertoire(
        current=current,
        teaching_capacity=teaching_capacity,
        novel_discoveries=novel_discoveries,
    ) > current


def allocate_equal_cost_evc(evcs: tuple[float, ...], budget_slots: int) -> tuple[int, ...]:
    if budget_slots < 0:
        raise ValueError("budget_slots must be nonnegative")
    ranked = sorted(
        ((value, idx) for idx, value in enumerate(evcs) if value > 0),
        key=lambda pair: (-pair[0], pair[1]),
    )
    return tuple(idx for _, idx in ranked[:budget_slots])


def planning_sufficient(model_classes: tuple[int, ...], action_values: tuple[tuple[float, ...], ...]) -> bool:
    if not model_classes or len(model_classes) != len(action_values):
        raise ValueError("aligned nonempty model classes and action values are required")
    width = len(action_values[0])
    if width < 1 or any(len(row) != width for row in action_values):
        raise ValueError("action-value rows must share a positive width")

    by_class: dict[int, list[set[int]]] = {}
    for cls, values in zip(model_classes, action_values):
        best = max(values)
        argmax = {idx for idx, value in enumerate(values) if value == best}
        by_class.setdefault(cls, []).append(argmax)

    for argmax_sets in by_class.values():
        common = set.intersection(*argmax_sets)
        if not common:
            return False
    return True


def verified_route_status(
    *,
    routed: tuple[str, ...],
    correct: frozenset[str],
    accepted: frozenset[str],
    verification_budget: int,
) -> str:
    if verification_budget < 0:
        raise ValueError("verification_budget must be nonnegative")
    inspected = routed[:verification_budget]
    accepted_inspected = tuple(item for item in inspected if item in accepted)
    if any(item not in correct for item in accepted_inspected):
        return "UNSAFE_VERIFIER"
    if any(item in correct for item in accepted_inspected):
        return "SAFE_SUCCESS"
    return "NO_VERIFIED_SOLUTION"
