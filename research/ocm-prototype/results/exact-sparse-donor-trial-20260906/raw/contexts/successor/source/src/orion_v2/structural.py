from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Hashable, Mapping, Sequence


class RelationType(str, Enum):
    ISOMORPHIC = "ISOMORPHIC"
    ROLE_EQUIVALENT = "ROLE_EQUIVALENT"
    BEHAVIORALLY_EQUIVALENT = "BEHAVIORALLY_EQUIVALENT"
    OBSERVATIONALLY_INDISTINGUISHABLE = "OBSERVATIONALLY_INDISTINGUISHABLE"
    PREDICTIVELY_EQUIVALENT = "PREDICTIVELY_EQUIVALENT"
    DECISION_DOMINATES = "DECISION_DOMINATES"
    SAFE_QUOTIENT = "SAFE_QUOTIENT"
    APPROXIMATELY_EQUIVALENT = "APPROXIMATELY_EQUIVALENT"
    INCOMPARABLE = "INCOMPARABLE"
    DISTINGUISHED_BY = "DISTINGUISHED_BY"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class ContextProbe:
    context_id: str
    queries: tuple[str, ...] = ()
    interventions: tuple[str, ...] = ()
    decision_class: str = ""
    target: str = ""
    resource_budget: float = 0.0
    tolerance: float = 0.0
    epoch: str = ""

    def __post_init__(self) -> None:
        if not self.context_id.strip():
            raise ValueError("context_id must be non-blank")
        if self.resource_budget < 0 or self.tolerance < 0:
            raise ValueError("resource_budget and tolerance must be non-negative")
        if any(not value.strip() for value in (*self.queries, *self.interventions)):
            raise ValueError("queries and interventions may not contain blanks")


State = Hashable
Action = str


@dataclass(frozen=True, slots=True)
class FiniteTransitionSystem:
    system_id: str
    states: frozenset[State]
    initial_state: State
    transitions: Mapping[tuple[State, Action], frozenset[State]]
    observations: Mapping[State, Hashable]

    def __post_init__(self) -> None:
        if not self.system_id.strip():
            raise ValueError("system_id must be non-blank")
        if not self.states:
            raise ValueError("states must be non-empty")
        if self.initial_state not in self.states:
            raise ValueError("initial_state must belong to states")
        if set(self.observations) != set(self.states):
            raise ValueError("observations must be defined for every state exactly once")
        for (source, action), destinations in self.transitions.items():
            if source not in self.states:
                raise ValueError("transition source is outside the state set")
            if not action.strip():
                raise ValueError("transition actions must be non-blank")
            if not destinations or not set(destinations) <= set(self.states):
                raise ValueError("transition destinations must be non-empty in-system states")

    def actions_from(self, state: State) -> frozenset[Action]:
        return frozenset(action for source, action in self.transitions if source == state)

    def successors(self, state: State, action: Action) -> frozenset[State]:
        return self.transitions.get((state, action), frozenset())


def _matches_successors(
    left: FiniteTransitionSystem,
    right: FiniteTransitionSystem,
    left_state: State,
    right_state: State,
    relation: set[tuple[State, State]],
) -> bool:
    actions = left.actions_from(left_state) | right.actions_from(right_state)
    for action in actions:
        left_successors = left.successors(left_state, action)
        right_successors = right.successors(right_state, action)
        if bool(left_successors) != bool(right_successors):
            return False
        for successor in left_successors:
            if not any((successor, candidate) in relation for candidate in right_successors):
                return False
        for successor in right_successors:
            if not any((candidate, successor) in relation for candidate in left_successors):
                return False
    return True


def bisimulation_relation(
    left: FiniteTransitionSystem,
    right: FiniteTransitionSystem,
) -> frozenset[tuple[State, State]]:
    """Compute the greatest strong bisimulation for two finite labelled systems."""

    relation = {
        (left_state, right_state)
        for left_state in left.states
        for right_state in right.states
        if left.observations[left_state] == right.observations[right_state]
    }
    changed = True
    while changed:
        changed = False
        for pair in tuple(relation):
            if not _matches_successors(left, right, pair[0], pair[1], relation):
                relation.remove(pair)
                changed = True
    return frozenset(relation)


def are_bisimilar(left: FiniteTransitionSystem, right: FiniteTransitionSystem) -> bool:
    return (left.initial_state, right.initial_state) in bisimulation_relation(left, right)


def indiscernibility_classes(
    information_table: Mapping[Hashable, Mapping[str, Hashable]],
    attributes: Sequence[str],
) -> tuple[frozenset[Hashable], ...]:
    """Return Pawlak-style equivalence classes under selected attributes."""

    if not attributes or any(not attribute.strip() for attribute in attributes):
        raise ValueError("attributes must contain non-blank names")
    classes: dict[tuple[Hashable, ...], set[Hashable]] = {}
    for object_id, row in information_table.items():
        try:
            key = tuple(row[attribute] for attribute in attributes)
        except KeyError as exc:
            raise ValueError(f"missing selected attribute: {exc.args[0]}") from exc
        classes.setdefault(key, set()).add(object_id)
    return tuple(
        sorted(
            (frozenset(values) for values in classes.values()),
            key=lambda values: tuple(sorted(map(repr, values))),
        )
    )


@dataclass(frozen=True, slots=True)
class StructuralRelationReceipt:
    relation: RelationType
    context_id: str
    left_id: str
    right_id: str
    witness: tuple[str, ...] = ()
    lost_information: tuple[str, ...] = ()
    counter_probe: str = ""
    exact: bool = True
    authorized_scientific_identity: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "relation", RelationType(self.relation))
        if any(not value.strip() for value in (self.context_id, self.left_id, self.right_id)):
            raise ValueError("receipt identities must be non-blank")
        if self.authorized_scientific_identity:
            raise ValueError("reference relation receipts cannot self-authorize scientific identity")


def safe_quotient(
    classes: Sequence[Sequence[Hashable]],
    protected_outputs: Mapping[Hashable, Hashable],
    *,
    context_id: str,
    left_id: str,
    right_id: str,
) -> StructuralRelationReceipt:
    """Certify a quotient only if every class preserves the protected output.

    The function deliberately checks one declared target.  It never implies that
    the quotient is safe for future or unregistered queries.
    """

    lost: list[str] = []
    for group in classes:
        values = {protected_outputs[item] for item in group}
        if len(values) > 1:
            lost.append(
                "class " + repr(tuple(group)) + " merges distinct protected outputs " + repr(values)
            )
    if lost:
        return StructuralRelationReceipt(
            relation=RelationType.DISTINGUISHED_BY,
            context_id=context_id,
            left_id=left_id,
            right_id=right_id,
            lost_information=tuple(lost),
            counter_probe="protected_output",
            exact=True,
        )
    return StructuralRelationReceipt(
        relation=RelationType.SAFE_QUOTIENT,
        context_id=context_id,
        left_id=left_id,
        right_id=right_id,
        witness=("protected output is constant on every quotient class",),
        exact=True,
    )
