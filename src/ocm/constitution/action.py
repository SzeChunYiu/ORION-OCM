"""ActionIntent / ActionReceipt and the external commit authority (M2 §9; MEG-04).

The constitution 𝔠 = (Check, Authority, Meter, Commit) is external to the machine.  Inside the
runtime that is realised by **capability non-distribution**: the runtime never holds an object
that can grant commit authority; a ``CommitAuthority`` is injected by the host and consulted, and
an atom produced by any internal operator has ``commit = 0`` in its authority lattice (undeclared
coordinates are bottom, `types.Authority.meet`), so no internal composition ever reaches Commit.
The only source of a commit-bearing record is an ``ActionReceipt`` returned from the boundary.
Parents: object capabilities (Dennis & Van Horn 1966; Miller 2006), reference monitor
(Saltzer & Schroeder 1975), Biba low-water-mark (authority meet) — all verified in
KSO_CORE_PARENTS_V1.  ORION `protected_flow.ProtectedTransitionCoordinator` supplied the shape
(one fixed sequence, no public method that skips a step); it is not vendored (signature stack).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

from ocm.kso.ids import content_hash
from ocm.kso.resources import ResourceVector
from ocm.kso.types import Authority, Scope

COMMIT_COORDINATE = "commit"


@dataclass(frozen=True, slots=True)
class ActionIntent:
    intent_id: str
    requested_effect: str
    arguments: Mapping[str, Any]
    scope: Scope
    required_authority: Authority
    supporting_object_ids: tuple[str, ...]
    expected_outcome: str
    risk_estimate: str
    resource_estimate: ResourceVector = field(default_factory=ResourceVector)

    def __post_init__(self) -> None:
        if not self.intent_id.strip() or not self.requested_effect.strip():
            raise ValueError("intent needs an id and an effect")
        if not self.supporting_object_ids:
            raise ValueError("an intent must name the objects that support it")

    @property
    def fingerprint(self) -> str:
        return content_hash({"id": self.intent_id, "effect": self.requested_effect, "args": self.arguments, "support": list(self.supporting_object_ids), "scope": self.scope.as_dict(), "authority": self.required_authority.as_dict()})

    def as_dict(self) -> dict[str, Any]:
        return {"intent_id": self.intent_id, "requested_effect": self.requested_effect, "arguments": dict(self.arguments), "scope": self.scope.as_dict(), "required_authority": self.required_authority.as_dict(), "supporting_object_ids": list(self.supporting_object_ids), "expected_outcome": self.expected_outcome, "risk_estimate": self.risk_estimate, "resource_estimate": self.resource_estimate.as_dict(), "fingerprint": self.fingerprint}


class ActionStatus(str, Enum):
    EXECUTED = "EXECUTED"
    REFUSED = "REFUSED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class ActionReceipt:
    receipt_id: str
    intent_id: str
    intent_fingerprint: str
    status: ActionStatus
    actual_effect: str
    authoritative_source: str
    observed_resources: ResourceVector
    gate_state: str                     # HardGateState value: PASS | FAIL | CANNOT_CHECK
    gate_reasons: tuple[str, ...]
    warrant_liveness: str               # LIVE | DEAD | UNKNOWN
    authority_granted: bool
    evidence_ids: tuple[str, ...]
    refusal_code: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"receipt_id": self.receipt_id, "intent_id": self.intent_id, "intent_fingerprint": self.intent_fingerprint, "status": self.status.value, "actual_effect": self.actual_effect, "authoritative_source": self.authoritative_source, "observed_resources": self.observed_resources.as_dict(), "gate_state": self.gate_state, "gate_reasons": list(self.gate_reasons), "warrant_liveness": self.warrant_liveness, "authority_granted": self.authority_granted, "evidence_ids": list(self.evidence_ids), "refusal_code": self.refusal_code}


@dataclass(frozen=True, slots=True)
class CommitDecision:
    granted: bool
    authority: Authority
    reason: str
    source: str


class CommitAuthority(Protocol):
    """Host-installed.  Never constructed by the runtime; never reachable from operators."""

    def decide(self, intent: ActionIntent, *, gate_state: str, warrant_liveness: str) -> CommitDecision: ...


@dataclass(frozen=True)
class StaticCommitAuthority:
    """A host authority with a fixed grant lattice (test/demo).  Refuses whenever the gate is not
    PASS or the warrant is not LIVE, regardless of its own rank — the constitution cannot be talked
    past by the machine's confidence."""

    grant: Authority
    source: str = "host:static"

    def decide(self, intent: ActionIntent, *, gate_state: str, warrant_liveness: str) -> CommitDecision:
        if gate_state != "PASS":
            return CommitDecision(False, Authority(), f"GATE_{gate_state}", self.source)
        if warrant_liveness != "LIVE":
            return CommitDecision(False, Authority(), f"WARRANT_{warrant_liveness}", self.source)
        if not (intent.required_authority <= self.grant):
            return CommitDecision(False, Authority(), "AUTHORITY_INSUFFICIENT", self.source)
        return CommitDecision(True, self.grant, "GRANTED", self.source)


def internal_authority_has_no_commit(a: Authority) -> bool:
    """MEG-04: any internally produced authority has commit = 0."""
    return a.rank(COMMIT_COORDINATE) == 0


def mutant_self_granting_authority(intent: ActionIntent) -> CommitDecision:
    """Planted: the runtime constructs its own grant from the intent's requirement."""
    return CommitDecision(True, intent.required_authority, "SELF_GRANTED", "runtime")
