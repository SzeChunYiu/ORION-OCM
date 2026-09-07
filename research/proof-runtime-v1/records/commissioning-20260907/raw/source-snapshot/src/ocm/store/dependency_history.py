"""Append-only dependency status history at logical time.

ADAPTED from ORION ``src/orion/kernel/support.py`` (SzeChunYiu/ORION commit
adb97ecce7d8e1fe6effab456b98e653f401dae0). Kept verbatim: ``DependencyStatus``
(LIVE / STALE / REVOKED / UNKNOWN), ``SupportVerdict`` (PASS / FAIL /
CANNOT_CHECK), ``DependencyStatusEvent``, ``append_dependency_status`` and the
logical-time ``_statuses_at`` resolution. Dropped: ``SupportSet``,
``SupportReason``, ``SupportReasonCode``, ``SupportEvaluation`` and the DNF
``evaluate_support`` — OCM's warrant algebra (``ocm.kso.warrant``) supersedes
the disjunction-of-conjunctions evaluator. Its refusal semantics survive as the
thin ``status_verdict`` helper: a conjunction of dependencies PASSes only when
every one is LIVE, FAILs only when one is demonstrably REVOKED, and is otherwise
CANNOT_CHECK — STALE, UNKNOWN and not-yet-observed never collapse into FAIL.

Nothing here reads a wall clock; ``observed_at`` and ``status_time`` are
logical coordinates supplied by the caller.

Provenance: docs/provenance/VENDORED_SOURCE_MANIFEST_V1.json.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum

from .canonical import canonical_digest


class DependencyStatus(str, Enum):
    """Freshness state of one exact, versioned dependency."""

    LIVE = "LIVE"
    STALE = "STALE"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class SupportVerdict(str, Enum):
    """Verdict licensed by a conjunction of dependency statuses."""

    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


def _require_identifier(value: str, field_name: str) -> None:
    if not value or value.isspace():
        raise ValueError(f"{field_name} must be nonblank")


@dataclass(frozen=True)
class DependencyStatusEvent:
    """One immutable observation in a dependency's append-only history."""

    event_id: str
    dependency_id: str
    status: DependencyStatus
    observed_at: int
    reason: str

    def __post_init__(self) -> None:
        _require_identifier(self.event_id, "event_id")
        _require_identifier(self.dependency_id, "dependency_id")
        if self.observed_at < 0:
            raise ValueError("observed_at must be nonnegative")
        _require_identifier(self.reason, "reason")


def append_dependency_status(
    history: Sequence[DependencyStatusEvent], event: DependencyStatusEvent
) -> tuple[DependencyStatusEvent, ...]:
    """Return history with one event appended; prior observations are retained."""

    if any(item.event_id == event.event_id for item in history):
        raise ValueError(f"event_id {event.event_id!r} already exists")
    same_dependency = tuple(
        item for item in history if item.dependency_id == event.dependency_id
    )
    if same_dependency and event.observed_at < same_dependency[-1].observed_at:
        raise ValueError("cannot append a dependency status older than its current tail")
    return (*history, event)


def _statuses_at(
    events: Sequence[DependencyStatusEvent], status_time: int
) -> dict[str, DependencyStatus]:
    statuses: dict[str, DependencyStatus] = {}
    timestamps: dict[str, int] = {}
    for event in events:
        if event.observed_at > status_time:
            continue
        previous = timestamps.get(event.dependency_id)
        if previous is None or event.observed_at >= previous:
            statuses[event.dependency_id] = event.status
            timestamps[event.dependency_id] = event.observed_at
    return statuses


def statuses_at(
    events: Sequence[DependencyStatusEvent], status_time: int
) -> dict[str, DependencyStatus]:
    """Resolve every dependency's status as of an explicit logical time.

    Events observed after ``status_time`` are invisible; a dependency with no
    visible observation is absent from the result (callers treat absence as
    UNKNOWN, never as LIVE).
    """

    if status_time < 0:
        raise ValueError("status_time must be nonnegative")
    event_ids = tuple(item.event_id for item in events)
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("event_id values must be unique")
    return _statuses_at(events, status_time)


def status_verdict(statuses: Iterable[DependencyStatus]) -> SupportVerdict:
    """Verdict for one conjunction of dependency statuses, failing closed.

    Mirrors the single-support-set case of ORION's ``evaluate_support``: all
    LIVE → PASS; any REVOKED → FAIL (the conjunction is demonstrably broken);
    anything else (STALE, UNKNOWN, or an empty conjunction) → CANNOT_CHECK.
    """

    observed = tuple(statuses)
    if not observed:
        return SupportVerdict.CANNOT_CHECK
    if all(status is DependencyStatus.LIVE for status in observed):
        return SupportVerdict.PASS
    if any(status is DependencyStatus.REVOKED for status in observed):
        return SupportVerdict.FAIL
    return SupportVerdict.CANNOT_CHECK


@dataclass(frozen=True)
class DependencyHistoryState:
    """Revisioned, logical-time projection of one dependency history.

    The analogue of ORION's ``SupportState`` without support sets: it carries
    the history and the status time, and its ``revision`` digest changes
    whenever either does, so a relying decision can bind the exact history it
    observed.
    """

    dependency_history: tuple[DependencyStatusEvent, ...]
    status_time: int

    def __post_init__(self) -> None:
        if self.status_time < 0:
            raise ValueError("status_time must be nonnegative")
        event_ids = tuple(item.event_id for item in self.dependency_history)
        if len(set(event_ids)) != len(event_ids):
            raise ValueError("dependency status event ids must be unique")

    @property
    def revision(self) -> str:
        return canonical_digest(
            {
                "dependency_history": [
                    {
                        "event_id": item.event_id,
                        "dependency_id": item.dependency_id,
                        "status": item.status.value,
                        "observed_at": item.observed_at,
                        "reason": item.reason,
                    }
                    for item in self.dependency_history
                ],
                "status_time": self.status_time,
            },
            domain="ocm.dependency-history-state.v1",
        )

    @property
    def statuses(self) -> dict[str, DependencyStatus]:
        return _statuses_at(self.dependency_history, self.status_time)

    def status_of(self, dependency_id: str) -> DependencyStatus:
        return self.statuses.get(dependency_id, DependencyStatus.UNKNOWN)

    def verdict(self, dependency_ids: Sequence[str]) -> SupportVerdict:
        """Verdict for the conjunction of the named dependencies at status time."""

        if not dependency_ids:
            return SupportVerdict.CANNOT_CHECK
        if len(set(dependency_ids)) != len(dependency_ids):
            raise ValueError("dependency_ids must be unique within a conjunction")
        return status_verdict(self.status_of(item) for item in dependency_ids)


__all__ = [
    "DependencyHistoryState",
    "DependencyStatus",
    "DependencyStatusEvent",
    "SupportVerdict",
    "append_dependency_status",
    "status_verdict",
    "statuses_at",
]
