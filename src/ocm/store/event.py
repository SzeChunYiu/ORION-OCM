"""The canonical OCM event (M2 §2) — one schema unifying the M0 ``EventStore`` line, ORION's
``LedgerEntry`` and the ``TransitionTransaction`` envelope.

Every consequential runtime transition is one immutable ``OCMEvent``:
  chain          schema/runtime version, monotonic sequence, prev_hash, event_hash (over every
                 field except itself), event_id (content-derived, NOT its own input);
  classification event_type (families below), status PASS | FAIL | CANNOT_CHECK | PROPOSAL;
  object graph   input_object_ids, output_object_ids, evidence_ids;
  provenance     operator_fingerprint, seed, observed_at (LOGICAL time, never wall clock);
  accounting     resource_delta — structurally non-optional (S7 over the log);
  expectation    the CAS tuple (log_head, kso_state_hash, registry_revision, evidence_epoch) the
                 writer observed — each coordinate is checked under the writer lock and each
                 mismatch is a distinct typed error, so a stale commit is refused, never re-served;
  payload        family-specific body, canonicalised.

Events are sufficient to reproduce the epistemically relevant state from a snapshot + log.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping

from ocm.kso.resources import ResourceVector

from .canonical import canonical_bytes

SCHEMA_VERSION = "ocm.event.v1"
GENESIS_HASH = "0" * 64


class EventType(str, Enum):
    EVIDENCE_ADMITTED = "EVIDENCE_ADMITTED"
    EVIDENCE_REVOKED = "EVIDENCE_REVOKED"
    EVIDENCE_REINSTATED = "EVIDENCE_REINSTATED"
    OBJECT_ADMITTED = "OBJECT_ADMITTED"
    OBJECT_QUARANTINED = "OBJECT_QUARANTINED"
    OBJECT_REOPENED = "OBJECT_REOPENED"
    RELATION_ADMITTED = "RELATION_ADMITTED"
    QUERY_OPENED = "QUERY_OPENED"
    NAVIGATION = "NAVIGATION"
    EXTRACTION = "EXTRACTION"
    CANDIDATE_COMPOSED = "CANDIDATE_COMPOSED"
    CHECKER_RESULT = "CHECKER_RESULT"
    LEARNER_UPDATE = "LEARNER_UPDATE"
    SKILL_PROMOTED = "SKILL_PROMOTED"
    SKILL_QUARANTINED = "SKILL_QUARANTINED"
    REPRESENTATION_PROPOSAL = "REPRESENTATION_PROPOSAL"
    OPERATOR_REGISTERED = "OPERATOR_REGISTERED"
    JUMP_PROPOSED = "JUMP_PROPOSED"
    JUMP_ADOPTED = "JUMP_ADOPTED"
    JUMP_REJECTED = "JUMP_REJECTED"
    ACTION_INTENT = "ACTION_INTENT"
    ACTION_RECEIPT = "ACTION_RECEIPT"
    SNAPSHOT_WRITTEN = "SNAPSHOT_WRITTEN"


class EventStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"
    PROPOSAL = "PROPOSAL"


class ExpectationMismatch(RuntimeError):
    """Base of the four distinct CAS errors (each coordinate has its own subclass)."""

    def __init__(self, coordinate: str, expected: str | None, actual: str | None) -> None:
        super().__init__(f"{coordinate}: expected {expected!r}, actual {actual!r}")
        self.coordinate, self.expected, self.actual = coordinate, expected, actual


class StaleLogHead(ExpectationMismatch):
    pass


class StaleStateHash(ExpectationMismatch):
    pass


class StaleRegistryRevision(ExpectationMismatch):
    pass


class StaleEvidenceEpoch(ExpectationMismatch):
    pass


@dataclass(frozen=True, slots=True)
class EventExpectation:
    log_head: str | None
    kso_state_hash: str
    registry_revision: str
    evidence_epoch: str

    def as_dict(self) -> dict[str, Any]:
        return {"log_head": self.log_head, "kso_state_hash": self.kso_state_hash, "registry_revision": self.registry_revision, "evidence_epoch": self.evidence_epoch}

    def check(self, *, log_head: str | None, kso_state_hash: str, registry_revision: str, evidence_epoch: str) -> None:
        if self.log_head != log_head:
            raise StaleLogHead("log_head", self.log_head, log_head)
        if self.kso_state_hash != kso_state_hash:
            raise StaleStateHash("kso_state_hash", self.kso_state_hash, kso_state_hash)
        if self.registry_revision != registry_revision:
            raise StaleRegistryRevision("registry_revision", self.registry_revision, registry_revision)
        if self.evidence_epoch != evidence_epoch:
            raise StaleEvidenceEpoch("evidence_epoch", self.evidence_epoch, evidence_epoch)


def _hash(body: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


@dataclass(frozen=True, slots=True)
class OCMEvent:
    schema_version: str
    runtime_version: str
    sequence: int
    prev_hash: str
    event_type: EventType
    status: EventStatus
    input_object_ids: tuple[str, ...]
    output_object_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    operator_fingerprint: str
    seed: str | None
    observed_at: int
    resource_delta: Mapping[str, int]
    expectation: EventExpectation
    payload: Mapping[str, Any]
    event_hash: str = ""
    event_id: str = ""

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError("sequence is 1-based")
        if self.observed_at < 0:
            raise ValueError("observed_at is a logical time ≥ 0")
        if set(self.resource_delta) - set(ResourceVector().as_dict()):
            raise ValueError("resource_delta has an unregistered coordinate")
        if any(v < 0 for v in self.resource_delta.values()):
            raise ValueError("resource_delta coordinates are non-negative")
        if not self.operator_fingerprint and self.event_type is not EventType.SNAPSHOT_WRITTEN:
            raise ValueError("operator_fingerprint is required on every non-snapshot event")
        body = self.hash_body()
        h = _hash(body)
        eid = "evt:" + hashlib.sha256(canonical_bytes({"schema": self.schema_version, "sequence": self.sequence, "event_hash": h})).hexdigest()[:24]
        if self.event_hash and self.event_hash != h:
            raise ValueError("event_hash does not match the event body")
        if self.event_id and self.event_id != eid:
            raise ValueError("event_id does not match the event")
        object.__setattr__(self, "event_hash", h)
        object.__setattr__(self, "event_id", eid)

    def hash_body(self) -> dict[str, Any]:
        """Every field except event_hash and event_id (the id is never its own input)."""
        return {
            "schema_version": self.schema_version,
            "runtime_version": self.runtime_version,
            "sequence": self.sequence,
            "prev_hash": self.prev_hash,
            "event_type": self.event_type.value,
            "status": self.status.value,
            "input_object_ids": list(self.input_object_ids),
            "output_object_ids": list(self.output_object_ids),
            "evidence_ids": list(self.evidence_ids),
            "operator_fingerprint": self.operator_fingerprint,
            "seed": self.seed,
            "observed_at": self.observed_at,
            "resource_delta": dict(sorted(self.resource_delta.items())),
            "expectation": self.expectation.as_dict(),
            "payload": self.payload,
        }

    def as_dict(self) -> dict[str, Any]:
        d = self.hash_body()
        d["event_hash"] = self.event_hash
        d["event_id"] = self.event_id
        return d

    @property
    def resources(self) -> ResourceVector:
        return ResourceVector(**self.resource_delta)

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> "OCMEvent":
        if d.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"unsupported event schema {d.get('schema_version')!r}")
        exp = d["expectation"]
        ev = OCMEvent(
            schema_version=d["schema_version"],
            runtime_version=d["runtime_version"],
            sequence=int(d["sequence"]),
            prev_hash=d["prev_hash"],
            event_type=EventType(d["event_type"]),
            status=EventStatus(d["status"]),
            input_object_ids=tuple(d["input_object_ids"]),
            output_object_ids=tuple(d["output_object_ids"]),
            evidence_ids=tuple(d["evidence_ids"]),
            operator_fingerprint=d["operator_fingerprint"],
            seed=d.get("seed"),
            observed_at=int(d["observed_at"]),
            resource_delta=dict(d["resource_delta"]),
            expectation=EventExpectation(exp["log_head"], exp["kso_state_hash"], exp["registry_revision"], exp["evidence_epoch"]),
            payload=d["payload"],
            event_hash=d.get("event_hash", ""),
            event_id=d.get("event_id", ""),
        )
        return ev


def next_event(prev: OCMEvent | None, **fields: Any) -> OCMEvent:
    """Build the successor of ``prev`` (or the genesis event) with the chain fields filled in."""
    sequence = 1 if prev is None else prev.sequence + 1
    prev_hash = GENESIS_HASH if prev is None else prev.event_hash
    fields.setdefault("schema_version", SCHEMA_VERSION)
    fields.setdefault("seed", None)
    fields.setdefault("resource_delta", {})
    return OCMEvent(sequence=sequence, prev_hash=prev_hash, **fields)


def verify_chain(events: list[OCMEvent]) -> dict[str, Any]:
    """Replay check: sequence contiguous from 1, prev_hash continuity, recomputed hashes, and the
    summed resource delta (S7 over the log)."""
    prev = GENESIS_HASH
    total = ResourceVector()
    for i, e in enumerate(events, start=1):
        if e.sequence != i:
            raise ValueError(f"event sequence gap at position {i}")
        if e.prev_hash != prev:
            raise ValueError(f"event hash chain broken at sequence {i}")
        recomputed = _hash(e.hash_body())
        if recomputed != e.event_hash:
            raise ValueError(f"event content hash mismatch at sequence {i}")
        prev = e.event_hash
        total = total + e.resources
    return {"events": len(events), "head": prev, "resource_total": total.as_dict()}


def mutant_reorder(events: list[OCMEvent]) -> list[OCMEvent]:
    """Planted: swap two events (order corruption) — verify_chain must refuse."""
    if len(events) < 2:
        return list(events)
    out = list(events)
    out[0], out[1] = out[1], out[0]
    return out


def mutant_drop_resource_delta(e: OCMEvent) -> OCMEvent:
    """Planted: strip the resource delta from a committed event (the S7 hostile) — the hash breaks."""
    return replace(e, resource_delta={}, event_hash=e.event_hash)
