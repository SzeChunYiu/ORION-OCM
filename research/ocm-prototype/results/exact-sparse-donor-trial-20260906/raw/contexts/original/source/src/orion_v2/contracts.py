from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ObligationStatus(str, Enum):
    OPEN = "OPEN"
    SATISFIED = "SATISFIED"
    DEFEATED = "DEFEATED"
    CENSORED = "CENSORED"
    NONIDENTIFIABLE = "NONIDENTIFIABLE"
    AUTHORITY_BLOCKED = "AUTHORITY_BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


class Terminal(str, Enum):
    JUSTIFIED_SOLUTION = "JUSTIFIED_SOLUTION"
    JUSTIFIED_PARTIAL_RESULT = "JUSTIFIED_PARTIAL_RESULT"
    MULTIPLE_JUSTIFIED_ALTERNATIVES = "MULTIPLE_JUSTIFIED_ALTERNATIVES"
    OBSERVATIONALLY_INDETERMINATE = "OBSERVATIONALLY_INDETERMINATE"
    STRUCTURALLY_NONIDENTIFIABLE = "STRUCTURALLY_NONIDENTIFIABLE"
    REPRESENTATION_INSUFFICIENT = "REPRESENTATION_INSUFFICIENT"
    METHOD_FAMILY_INSUFFICIENT = "METHOD_FAMILY_INSUFFICIENT"
    COVERAGE_INCOMPLETE = "COVERAGE_INCOMPLETE"
    SEARCH_ROUTE_CENSORED = "SEARCH_ROUTE_CENSORED"
    RESOURCE_BOUND = "RESOURCE_BOUND"
    AUTHORITY_REQUIRED = "AUTHORITY_REQUIRED"
    CONTRADICTION_OR_OBSTRUCTION = "CONTRADICTION_OR_OBSTRUCTION"
    FRAMEWORK_REVISION_CANDIDATE = "FRAMEWORK_REVISION_CANDIDATE"
    REFUTED = "REFUTED"
    CANNOT_CHECK = "CANNOT_CHECK"


def _nonblank(name: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must be non-blank")
    return normalized


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    evidence_id: str
    source_uri: str
    content_digest: str = ""
    epoch: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", _nonblank("evidence_id", self.evidence_id))
        object.__setattr__(self, "source_uri", _nonblank("source_uri", self.source_uri))
        if self.content_digest and not self.content_digest.strip():
            raise ValueError("content_digest cannot be whitespace")


@dataclass(frozen=True, slots=True)
class Obligation:
    obligation_id: str
    description: str
    status: ObligationStatus = ObligationStatus.OPEN
    hard: bool = True
    support_ids: tuple[str, ...] = ()
    blocker_ids: tuple[str, ...] = ()
    reopen_condition: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "obligation_id", _nonblank("obligation_id", self.obligation_id))
        object.__setattr__(self, "description", _nonblank("description", self.description))
        object.__setattr__(self, "status", ObligationStatus(self.status))
        if any(not item.strip() for item in (*self.support_ids, *self.blocker_ids)):
            raise ValueError("support_ids and blocker_ids may not contain blanks")
        if len(set(self.support_ids)) != len(self.support_ids):
            raise ValueError("support_ids must be unique")
        if len(set(self.blocker_ids)) != len(self.blocker_ids):
            raise ValueError("blocker_ids must be unique")
        if self.status is ObligationStatus.SATISFIED and self.blocker_ids:
            raise ValueError("a satisfied obligation cannot retain active blockers")

    @property
    def is_closed(self) -> bool:
        return self.status is not ObligationStatus.OPEN

    @property
    def is_successfully_discharged(self) -> bool:
        return self.status is ObligationStatus.SATISFIED


@dataclass(frozen=True, slots=True)
class ProblemContract:
    problem_id: str
    target: str
    decision_class: str
    scope: tuple[str, ...]
    exclusions: tuple[str, ...] = ()
    admissible_evidence_classes: tuple[str, ...] = ()
    admissible_intervention_classes: tuple[str, ...] = ()
    protected_constraints: tuple[str, ...] = ()
    authority_requirements: tuple[str, ...] = ()
    resource_budget: float = 0.0
    information_budget: float = 0.0
    epoch: str = ""
    replay_required: bool = True
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in ("problem_id", "target", "decision_class"):
            object.__setattr__(self, name, _nonblank(name, getattr(self, name)))
        if not self.scope or any(not item.strip() for item in self.scope):
            raise ValueError("scope must contain at least one non-blank item")
        for name in (
            "exclusions",
            "admissible_evidence_classes",
            "admissible_intervention_classes",
            "protected_constraints",
            "authority_requirements",
        ):
            values = getattr(self, name)
            if any(not item.strip() for item in values):
                raise ValueError(f"{name} may not contain blanks")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must contain unique values")
        if self.resource_budget < 0 or self.information_budget < 0:
            raise ValueError("budgets must be non-negative")
        keys = [key for key, _ in self.metadata]
        if any(not key.strip() for key in keys) or len(set(keys)) != len(keys):
            raise ValueError("metadata keys must be unique and non-blank")

    def requires_authority(self) -> bool:
        return bool(self.authority_requirements)
