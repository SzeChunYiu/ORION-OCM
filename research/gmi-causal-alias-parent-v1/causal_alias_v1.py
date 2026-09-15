from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Mapping, Sequence, Tuple

Model = Mapping[str, object]


def validate_model(model: Model) -> None:
    required = {"id", "passive_observation", "required_action", "interventions"}
    if set(model) != required:
        raise ValueError("causal model must contain exactly the registered fields")
    if not isinstance(model["id"], str) or not model["id"]:
        raise ValueError("model id must be a nonempty string")
    passive = model["passive_observation"]
    if not isinstance(passive, tuple):
        raise ValueError("passive_observation must be a tuple")
    action = model["required_action"]
    if not isinstance(action, str) or not action:
        raise ValueError("required_action must be a nonempty string")
    interventions = model["interventions"]
    if not isinstance(interventions, Mapping) or not interventions:
        raise ValueError("interventions must be a nonempty mapping")
    for name, outcome in interventions.items():
        if not isinstance(name, str) or not name:
            raise ValueError("intervention names must be nonempty strings")
        if not isinstance(outcome, tuple):
            raise ValueError("intervention outcomes must be tuples")


def observational_classes(models: Iterable[Model]) -> Dict[Tuple[object, ...], Tuple[str, ...]]:
    groups: Dict[Tuple[object, ...], list[str]] = defaultdict(list)
    for model in models:
        validate_model(model)
        groups[model["passive_observation"]].append(model["id"])
    return {obs: tuple(sorted(ids)) for obs, ids in groups.items()}


def observational_only_exact_possible(models: Sequence[Model]) -> bool:
    """Exact causal-state decision is possible iff action is constant on each passive-observation class."""
    groups: Dict[Tuple[object, ...], set[str]] = defaultdict(set)
    for model in models:
        validate_model(model)
        groups[model["passive_observation"]].add(model["required_action"])
    return all(len(actions) == 1 for actions in groups.values())


def aliases_causal_states(left: Model, right: Model) -> bool:
    validate_model(left)
    validate_model(right)
    if left["passive_observation"] != right["passive_observation"]:
        return False
    return any(
        name in right["interventions"]
        and left["interventions"][name] != right["interventions"][name]
        for name in left["interventions"]
    )


def separating_interventions(models: Sequence[Model]) -> Tuple[str, ...]:
    if not models:
        raise ValueError("at least one model is required")
    for model in models:
        validate_model(model)
    common = set(models[0]["interventions"])
    for model in models[1:]:
        common.intersection_update(model["interventions"])
    separating = []
    for intervention in sorted(common):
        outcomes = {model["interventions"][intervention] for model in models}
        if len(outcomes) == len(models):
            separating.append(intervention)
    return tuple(separating)


def intervention_partition(models: Sequence[Model], intervention: str) -> Dict[Tuple[object, ...], Tuple[str, ...]]:
    groups: Dict[Tuple[object, ...], list[str]] = defaultdict(list)
    for model in models:
        validate_model(model)
        if intervention not in model["interventions"]:
            raise ValueError("intervention unavailable in one or more models")
        groups[model["interventions"][intervention]].append(model["id"])
    return {outcome: tuple(sorted(ids)) for outcome, ids in groups.items()}


def ambiguity_pairs(partition: Mapping[object, Sequence[str]]) -> int:
    """Number of unordered model pairs that remain observationally indistinguishable."""
    total = 0
    for ids in partition.values():
        n = len(ids)
        total += n * (n - 1) // 2
    return total


def ambiguity_reduction_per_cost(
    models: Sequence[Model], intervention: str, *, cost: int
) -> Tuple[int, int]:
    if isinstance(cost, bool) or not isinstance(cost, int) or cost <= 0:
        raise ValueError("cost must be a positive integer")
    passive = observational_classes(models)
    post = intervention_partition(models, intervention)
    reduction = ambiguity_pairs(passive) - ambiguity_pairs(post)
    return reduction, cost


def choose_intervention_by_ambiguity_per_cost(
    models: Sequence[Model], costs: Mapping[str, int]
) -> str:
    candidates = []
    for intervention, cost in costs.items():
        reduction, denom = ambiguity_reduction_per_cost(models, intervention, cost=cost)
        candidates.append((reduction * 1_000_000 // denom, reduction, -cost, intervention))
    if not candidates:
        raise ValueError("at least one intervention cost is required")
    return max(candidates)[-1]


def canonical_alias_witness() -> Tuple[Dict[str, object], Dict[str, object]]:
    """Two finite SCM-style states with identical passive observation and different do(X=1) response.

    Forward state: X:=0; Y:=X.
    Reverse state: Y:=0; X:=Y.
    Both passively yield (X,Y)=(0,0).
    Under do(X=1), forward gives (1,1), reverse gives (1,0).
    """
    forward = {
        "id": "C0",
        "passive_observation": (0, 0),
        "required_action": "ACT_FORWARD",
        "interventions": {"do_X_1": (1, 1), "do_Y_1": (0, 1)},
    }
    reverse = {
        "id": "C1",
        "passive_observation": (0, 0),
        "required_action": "ACT_REVERSE",
        "interventions": {"do_X_1": (1, 0), "do_Y_1": (1, 1)},
    }
    return forward, reverse
