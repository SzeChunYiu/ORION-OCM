from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class ActionValue:
    hard_gate_pass: bool
    obligation_reduction: float = 0.0
    distinguishing_power: float = 0.0
    justified_reachability_gain: float = 0.0
    scientific_value: float = 0.0
    option_value: float = 0.0
    diversity_value: float = 0.0
    cost: float = 0.0
    risk: float = 0.0
    authority_exposure: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "obligation_reduction",
            "distinguishing_power",
            "justified_reachability_gain",
            "scientific_value",
            "option_value",
            "diversity_value",
            "cost",
            "risk",
            "authority_exposure",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")

    @property
    def benefits(self) -> tuple[float, ...]:
        return (
            self.obligation_reduction,
            self.distinguishing_power,
            self.justified_reachability_gain,
            self.scientific_value,
            self.option_value,
            self.diversity_value,
        )

    @property
    def burdens(self) -> tuple[float, ...]:
        return (self.cost, self.risk, self.authority_exposure)


@dataclass(frozen=True, slots=True)
class ActionProposal:
    action_id: str
    action_family: str
    value: ActionValue
    required_authority: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.action_id, self.action_family)):
            raise ValueError("action identities must be non-blank")
        if any(not value.strip() for value in (*self.required_authority, *self.evidence_ids)):
            raise ValueError("authority/evidence identities may not be blank")


class SelectionStatus(str, Enum):
    UNIQUE = "UNIQUE"
    PARETO_SET = "PARETO_SET"
    NO_ADMISSIBLE_ACTION = "NO_ADMISSIBLE_ACTION"


@dataclass(frozen=True, slots=True)
class SelectionReceipt:
    status: SelectionStatus
    selected_action_ids: tuple[str, ...]
    rejected_gate_action_ids: tuple[str, ...]
    relation: str = "PARETO_NONCOMPENSATORY"


def dominates(left: ActionProposal, right: ActionProposal) -> bool:
    if not left.value.hard_gate_pass:
        return False
    if not right.value.hard_gate_pass:
        return True
    benefit_ge = all(a >= b for a, b in zip(left.value.benefits, right.value.benefits, strict=True))
    burden_le = all(a <= b for a, b in zip(left.value.burdens, right.value.burdens, strict=True))
    strict = left.value.benefits != right.value.benefits or left.value.burdens != right.value.burdens
    return benefit_ge and burden_le and strict


def select_actions(actions: tuple[ActionProposal, ...]) -> SelectionReceipt:
    if len({action.action_id for action in actions}) != len(actions):
        raise ValueError("action IDs must be unique")
    rejected = tuple(action.action_id for action in actions if not action.value.hard_gate_pass)
    admissible = tuple(action for action in actions if action.value.hard_gate_pass)
    if not admissible:
        return SelectionReceipt(SelectionStatus.NO_ADMISSIBLE_ACTION, (), rejected)
    frontier = tuple(
        action
        for action in admissible
        if not any(dominates(other, action) for other in admissible if other is not action)
    )
    status = SelectionStatus.UNIQUE if len(frontier) == 1 else SelectionStatus.PARETO_SET
    return SelectionReceipt(status, tuple(action.action_id for action in frontier), rejected)
