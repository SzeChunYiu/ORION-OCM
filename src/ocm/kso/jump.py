from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum


class JumpLevel(IntEnum):
    ACTION_PARAMETER = 0
    LOCAL_REPAIR_COMPOSITION = 1
    MODEL_HYPOTHESIS_EXPANSION = 2
    REPRESENTATION_REGIME_TRANSITION = 3
    PROBLEM_OBJECTIVE_REFORMULATION = 4
    METHOD_TOOL_INSTRUMENT_INVENTION = 5
    WORKFLOW_META_SKILL_REVISION = 6
    FRAMEWORK_REVISION = 7
    CONSTITUTION_PROPOSAL = 8


class TriggerKind(str, Enum):
    EXPRESSIVE_CEILING = "EXPRESSIVE_CEILING"
    STRUCTURAL_NONIDENTIFIABILITY = "STRUCTURAL_NONIDENTIFIABILITY"
    MODEL_FAMILY_INADEQUACY = "MODEL_FAMILY_INADEQUACY"
    GLOBAL_OBSTRUCTION = "GLOBAL_OBSTRUCTION"
    REPEATED_PROTECTED_RESIDUAL = "REPEATED_PROTECTED_RESIDUAL"
    REMOTE_DONOR_OUTSIDE_CLOSURE = "REMOTE_DONOR_OUTSIDE_CLOSURE"
    EXPLORATION_COLLAPSE = "EXPLORATION_COLLAPSE"
    STRATEGIC_RESPONSE = "STRATEGIC_RESPONSE"
    SEMANTIC_OR_SCALE_DRIFT = "SEMANTIC_OR_SCALE_DRIFT"
    POOR_SCORE = "POOR_SCORE"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    CENSORED_ROUTE = "CENSORED_ROUTE"


_STRONG_TRIGGERS = frozenset(
    {
        TriggerKind.EXPRESSIVE_CEILING,
        TriggerKind.STRUCTURAL_NONIDENTIFIABILITY,
        TriggerKind.MODEL_FAMILY_INADEQUACY,
        TriggerKind.GLOBAL_OBSTRUCTION,
        TriggerKind.REPEATED_PROTECTED_RESIDUAL,
        TriggerKind.REMOTE_DONOR_OUTSIDE_CLOSURE,
        TriggerKind.EXPLORATION_COLLAPSE,
        TriggerKind.STRATEGIC_RESPONSE,
        TriggerKind.SEMANTIC_OR_SCALE_DRIFT,
    }
)


@dataclass(frozen=True, slots=True)
class JumpTrigger:
    trigger_id: str
    kind: TriggerKind
    incumbent_level: JumpLevel
    witness_ids: tuple[str, ...]
    lower_level_dispositions: tuple[str, ...]
    route_censored: bool = False
    protected_outcome_seen: bool = False

    def __post_init__(self) -> None:
        if not self.trigger_id.strip():
            raise ValueError("trigger_id must be non-blank")
        object.__setattr__(self, "kind", TriggerKind(self.kind))
        object.__setattr__(self, "incumbent_level", JumpLevel(self.incumbent_level))
        if any(not value.strip() for value in (*self.witness_ids, *self.lower_level_dispositions)):
            raise ValueError("witnesses and dispositions may not contain blanks")

    @property
    def is_admissible(self) -> bool:
        return (
            self.kind in _STRONG_TRIGGERS
            and bool(self.witness_ids)
            and bool(self.lower_level_dispositions)
            and not self.route_censored
            and not self.protected_outcome_seen
        )


@dataclass(frozen=True, slots=True)
class JumpProposal:
    proposal_id: str
    trigger: JumpTrigger
    level: JumpLevel
    transformation_family: str
    parent_ids: tuple[str, ...]
    correspondence_ids: tuple[str, ...]
    preservation_obligation_ids: tuple[str, ...]
    predicted_contract_ids: tuple[str, ...]
    falsifier_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.proposal_id, self.transformation_family)):
            raise ValueError("proposal identities must be non-blank")
        object.__setattr__(self, "level", JumpLevel(self.level))
        for name in (
            "parent_ids",
            "correspondence_ids",
            "preservation_obligation_ids",
            "predicted_contract_ids",
            "falsifier_ids",
        ):
            values = getattr(self, name)
            if not values or any(not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-blank identities")
        if self.level <= self.trigger.incumbent_level:
            raise ValueError("a jump proposal must change a level above the incumbent level")

    @property
    def is_formally_complete(self) -> bool:
        return self.trigger.is_admissible and all(
            (
                self.parent_ids,
                self.correspondence_ids,
                self.preservation_obligation_ids,
                self.predicted_contract_ids,
                self.falsifier_ids,
            )
        )


class JumpAssessment(str, Enum):
    INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED = "INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED"
    NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT = "NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT"
    DONOR_SUBSUMES_JUMP = "DONOR_SUBSUMES_JUMP"
    JUMP_PROPOSAL_INCOMPLETE = "JUMP_PROPOSAL_INCOMPLETE"
    CANDIDATE_FOR_PROTECTED_EVALUATION = "CANDIDATE_FOR_PROTECTED_EVALUATION"


def assess_jump(
    proposal: JumpProposal,
    *,
    lower_level_sufficient: bool,
    donor_product_ties: bool,
) -> JumpAssessment:
    if not proposal.trigger.is_admissible:
        return JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    if lower_level_sufficient:
        return JumpAssessment.NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT
    if donor_product_ties:
        return JumpAssessment.DONOR_SUBSUMES_JUMP
    if not proposal.is_formally_complete:
        return JumpAssessment.JUMP_PROPOSAL_INCOMPLETE
    return JumpAssessment.CANDIDATE_FOR_PROTECTED_EVALUATION


def minimum_level(proposals: tuple[JumpProposal, ...]) -> JumpProposal:
    admissible = [proposal for proposal in proposals if proposal.is_formally_complete]
    if not admissible:
        raise ValueError("no complete admissible jump proposal")
    return min(admissible, key=lambda proposal: int(proposal.level))


def assess_jump_from_evidence(proposal: JumpProposal, *, minimum_sufficient_local: bool | None, certificate_valid: bool, donor_product_ties: bool) -> JumpAssessment:
    """Batch 6 (F3/F4) tightening of `assess_jump`: `lower_level_sufficient` is not a caller flag but
    is derived from the diagnosis — the minimum-sufficient layer computed from ablation evidence is
    local (D0–D2/D5/D6) ⇒ no Jump; UNKNOWN (no restoring ablation) ⇒ insufficiency not identified;
    non-local without a valid obstruction certificate ⇒ insufficiency not identified either."""
    if minimum_sufficient_local is None or not proposal.trigger.is_admissible:
        return JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    if minimum_sufficient_local:
        return JumpAssessment.NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT
    if not certificate_valid:
        return JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    if donor_product_ties:
        return JumpAssessment.DONOR_SUBSUMES_JUMP
    if not proposal.is_formally_complete:
        return JumpAssessment.JUMP_PROPOSAL_INCOMPLETE
    return JumpAssessment.CANDIDATE_FOR_PROTECTED_EVALUATION


def minimum_sufficient_proposal(proposals: tuple[JumpProposal, ...], minimum_sufficient_level: int) -> JumpProposal:
    """The lowest complete proposal at or above the *minimum sufficient* level established by
    evidence — not merely the lowest admissible proposal (batch 6 consequence 7)."""
    admissible = [p for p in proposals if p.is_formally_complete and int(p.level) >= minimum_sufficient_level]
    if not admissible:
        raise ValueError("no complete admissible jump proposal at or above the minimum sufficient level")
    return min(admissible, key=lambda p: int(p.level))

