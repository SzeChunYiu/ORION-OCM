"""Revisioned registry projection with an append-only status history.

ADAPTED from ORION ``src/orion/kernel/authority_state.py`` (SzeChunYiu/ORION
commit adb97ecce7d8e1fe6effab456b98e653f401dae0). What changed:

* ``AuthorityObjectKind`` (EVALUATOR / POLICY / KEY / TRUST_ROOT) is generalised
  to ``RegistryObjectKind`` = EVIDENCE | OPERATOR | LEARNER | CHECKER |
  REPRESENTATION | COMMIT_AUTHORITY; ``AuthorityObjectStatus`` is renamed
  ``RegistryObjectStatus`` with the same four members;
* ``public_key_hex`` is dropped (it was only meaningful with ``cryptography``),
  together with the kind-conditional key rules in ``__post_init__`` and the
  key field in the commitment/revision payloads;
* ``canonical_digest`` is ``ocm.store.canonical.canonical_digest`` and the
  digest domains are ``ocm.registry-registration.v1`` / ``ocm.registry-state.v1``;
* ``SupportState`` is not here — its history layer lives in
  ``ocm.store.dependency_history``.

Everything else — registration validation, the append-only status history with
a monotone per-registration tail, the logical-time ``current_status`` that never
reads a future event, ``live_registration`` and the ``revision`` digest over the
whole registry — is verbatim.

These are immutable, logical-time projections. They contain no wall-clock
reads, no global mutable registry and no candidate-controlled promotion path.
Every relying-party decision later binds the exact registry revision it observed.

Provenance: docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .canonical import canonical_digest


_HEX = frozenset("0123456789abcdef")


def _text(value: str, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} is required")


def _sha(value: str, field: str) -> None:
    if len(value) != 64 or any(character not in _HEX for character in value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")


class RegistryObjectKind(str, Enum):
    EVIDENCE = "EVIDENCE"
    OPERATOR = "OPERATOR"
    LEARNER = "LEARNER"
    CHECKER = "CHECKER"
    REPRESENTATION = "REPRESENTATION"
    COMMIT_AUTHORITY = "COMMIT_AUTHORITY"


class RegistryObjectStatus(str, Enum):
    LIVE = "LIVE"
    STALE = "STALE"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Registration:
    registration_id: str
    kind: RegistryObjectKind
    artifact_hash: str
    epoch_id: str
    metadata_hash: str

    def __post_init__(self) -> None:
        _text(self.registration_id, "registration_id")
        _sha(self.artifact_hash, "artifact_hash")
        _text(self.epoch_id, "epoch_id")
        _sha(self.metadata_hash, "metadata_hash")

    @property
    def commitment(self) -> str:
        return canonical_digest(
            {
                "registration_id": self.registration_id,
                "kind": self.kind.value,
                "artifact_hash": self.artifact_hash,
                "epoch_id": self.epoch_id,
                "metadata_hash": self.metadata_hash,
            },
            domain="ocm.registry-registration.v1",
        )


@dataclass(frozen=True)
class RegistryStatusEvent:
    event_id: str
    registration_id: str
    status: RegistryObjectStatus
    observed_at: int
    reason: str

    def __post_init__(self) -> None:
        _text(self.event_id, "event_id")
        _text(self.registration_id, "registration_id")
        if self.observed_at < 0:
            raise ValueError("observed_at must be nonnegative")
        _text(self.reason, "reason")


def append_registry_status(
    history: tuple[RegistryStatusEvent, ...],
    event: RegistryStatusEvent,
) -> tuple[RegistryStatusEvent, ...]:
    if any(item.event_id == event.event_id for item in history):
        raise ValueError("registry status event ids must be unique")
    prior = tuple(item for item in history if item.registration_id == event.registration_id)
    if prior and event.observed_at < prior[-1].observed_at:
        raise ValueError("cannot append a registry status older than its current tail")
    return (*history, event)


@dataclass(frozen=True)
class RegistryState:
    registrations: tuple[Registration, ...]
    status_history: tuple[RegistryStatusEvent, ...]
    status_time: int

    def __post_init__(self) -> None:
        if self.status_time < 0:
            raise ValueError("status_time must be nonnegative")
        registration_ids = tuple(item.registration_id for item in self.registrations)
        if len(registration_ids) != len(set(registration_ids)):
            raise ValueError("registry registration ids must be unique")
        event_ids = tuple(item.event_id for item in self.status_history)
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("registry status event ids must be unique")
        unknown = {
            item.registration_id for item in self.status_history
        } - set(registration_ids)
        if unknown:
            raise ValueError("registry status history references unknown registrations")

    @property
    def revision(self) -> str:
        return canonical_digest(
            {
                "registrations": [
                    {
                        "registration_id": item.registration_id,
                        "kind": item.kind.value,
                        "artifact_hash": item.artifact_hash,
                        "epoch_id": item.epoch_id,
                        "metadata_hash": item.metadata_hash,
                    }
                    for item in sorted(self.registrations, key=lambda item: item.registration_id)
                ],
                "status_history": [
                    {
                        "event_id": item.event_id,
                        "registration_id": item.registration_id,
                        "status": item.status.value,
                        "observed_at": item.observed_at,
                        "reason": item.reason,
                    }
                    for item in self.status_history
                ],
                "status_time": self.status_time,
            },
            domain="ocm.registry-state.v1",
        )

    def registration(self, registration_id: str) -> Registration | None:
        return next(
            (item for item in self.registrations if item.registration_id == registration_id),
            None,
        )

    def current_status(self, registration_id: str) -> RegistryObjectStatus:
        relevant = [
            item
            for item in self.status_history
            if item.registration_id == registration_id and item.observed_at <= self.status_time
        ]
        if not relevant:
            return RegistryObjectStatus.UNKNOWN
        return max(relevant, key=lambda item: item.observed_at).status

    def live_registration(
        self,
        registration_id: str,
        *,
        kind: RegistryObjectKind | None = None,
    ) -> Registration | None:
        registration = self.registration(registration_id)
        if registration is None:
            return None
        if kind is not None and registration.kind is not kind:
            return None
        if self.current_status(registration_id) is not RegistryObjectStatus.LIVE:
            return None
        return registration


__all__ = [
    "Registration",
    "RegistryObjectKind",
    "RegistryObjectStatus",
    "RegistryState",
    "RegistryStatusEvent",
    "append_registry_status",
]
