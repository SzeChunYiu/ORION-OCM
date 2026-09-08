"""Incremental liveness for a frozen snapshot of canonical warrant intervals.

This is an optional index, not an admission authority or a replacement KSO core.
Its answers equal WarrantProfile.liveness at the supplied field epoch. Changing a
profile, operator, scope, or authority requires a new externally bound epoch and
rebuilding the index. No runtime call site is switched to this index here.

The conditional proof and accounting model are in
``docs/spec/OCM_FOUNDATIONS_CLOSURE_V1.md`` (FC-T2). Both interval bounds are indexed:
``WarrantProfile.evidence`` alone is insufficient because it exposes only lower
support. A mixed revoke/reinstate batch is evaluated by its final state, never by
intermediate, externally visible liveness changes.

Work counts cover incidence operations, not CPU, allocation, persistence, or
canonical-profile discovery. Calls must be serialized by the owning transaction;
this object does not supply a durable commit protocol. Evidence identifiers must
have stable, side-effect-free Python hash/equality semantics, as in warrant.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Hashable, Iterable, Mapping

from .warrant import CannotCheck, Liveness, WarrantProfile


@dataclass(frozen=True, slots=True)
class IndexSize:
    initial_revocation_items: int
    profiles: int
    distinct_clauses: int
    evidence_clause_links: int
    clause_bound_links: int


@dataclass(frozen=True, slots=True)
class IndexWork:
    input_evidence_items: int
    requested_evidence: int
    changed_evidence: int
    evidence_clause_visits: int
    changed_clauses: int
    clause_bound_visits: int
    touched_profiles: int
    changed_liveness: int


@dataclass(frozen=True, slots=True)
class IndexDelta:
    """Diagnostic data only; not a warrant or an externally authorized receipt.

    Iteration order of changes is unspecified. Canonical serialization, should a
    caller require it, is additional work rather than free work inside apply().
    """

    changes: Mapping[str, tuple[Liveness, Liveness]]
    work: IndexWork


def _identities(values: Iterable[Hashable]) -> tuple[frozenset[Hashable], int]:
    """Count input consumption as well as distinct identities; inputs must be finite."""
    unique: set[Hashable] = set()
    count = 0
    for value in values:
        unique.add(value)
        count += 1
    return frozenset(unique), count


def _liveness(counts: tuple[int, int]) -> Liveness:
    lower, upper = counts
    if lower:
        return Liveness.LIVE
    return Liveness.UNKNOWN if upper else Liveness.DEAD


class WarrantLivenessIndex:
    """Snapshot index with O(1) liveness lookup in the dictionary-access model.

    The caller owns the epoch-to-state binding. Repeating an old epoch token for
    changed runtime state violates the contract; the index cannot discover that
    lie. The retained snapshot and the original profiles remain unmodified.
    """

    def __init__(
        self,
        profiles: Mapping[str, WarrantProfile],
        *,
        epoch: str,
        revoked: Iterable[Hashable] = (),
    ) -> None:
        if type(epoch) is not str or not epoch:
            raise ValueError("epoch must be a nonempty externally bound string")
        snapshot = dict(profiles)
        if any(type(key) is not str or not key for key in snapshot):
            raise ValueError("object identities must be nonempty strings")
        if any(type(profile) is not WarrantProfile for profile in snapshot.values()):
            raise TypeError("profiles must be canonical WarrantProfile instances")
        self._epoch = epoch
        initial_revoked, initial_items = _identities(revoked)
        self._revoked = set(initial_revoked)
        self._counts: dict[str, tuple[int, int]] = {}
        self._limits: dict[str, tuple[int, int]] = {}
        self._blocked: list[int] = []
        self._clause_lengths: list[int] = []
        self._consumers: list[list[tuple[str, int]]] = []
        self._incidence: dict[Hashable, list[int]] = {}
        clause_ids: dict[frozenset, int] = {}
        evidence_links = bound_links = 0
        for object_id, profile in snapshot.items():
            counts = [0, 0]
            self._limits[object_id] = (len(profile.lower), len(profile.upper))
            for bound, support in enumerate((profile.lower, profile.upper)):
                for clause in support:
                    if clause not in clause_ids:
                        clause_id = len(clause_ids)
                        clause_ids[clause] = clause_id
                        self._blocked.append(sum(e in self._revoked for e in clause))
                        self._clause_lengths.append(len(clause))
                        self._consumers.append([])
                        for evidence in clause:
                            self._incidence.setdefault(evidence, []).append(clause_id)
                            evidence_links += 1
                    clause_id = clause_ids[clause]
                    self._consumers[clause_id].append((object_id, bound))
                    bound_links += 1
                    counts[bound] += int(self._blocked[clause_id] == 0)
            self._counts[object_id] = (counts[0], counts[1])
        self.size = IndexSize(initial_items, len(snapshot), len(clause_ids), evidence_links, bound_links)

    def _check_epoch(self, epoch: str) -> None:
        if type(epoch) is not str or epoch != self._epoch:
            raise CannotCheck("CANNOT_CHECK_STALE_WARRANT_INDEX_EPOCH")

    def liveness(self, object_id: str, *, epoch: str) -> Liveness:
        self._check_epoch(epoch)
        if object_id not in self._counts:
            raise CannotCheck("CANNOT_CHECK_UNKNOWN_OBJECT_IDENTITY")
        return _liveness(self._counts[object_id])

    def snapshot(self, *, epoch: str) -> Mapping[str, Liveness]:
        """Copy all answers; explicitly O(number of profiles), not an O(1) view."""
        self._check_epoch(epoch)
        return MappingProxyType({key: _liveness(value) for key, value in self._counts.items()})

    def revoked_snapshot(self, *, epoch: str) -> frozenset[Hashable]:
        """Copy revocations; explicitly O(number of revoked identities)."""
        self._check_epoch(epoch)
        return frozenset(self._revoked)

    def apply(
        self,
        *,
        epoch: str,
        revoke: Iterable[Hashable] = (),
        reinstate: Iterable[Hashable] = (),
    ) -> IndexDelta:
        """Apply one final-state batch, rejecting overlap before any mutation.

        Idempotent requests and absent-evidence identities are legal. Both remain
        accounted for; absent evidence is retained in the revocation snapshot.
        All validation and counter planning precede mutation. This is not a claim
        of crash atomicity or recovery from process failure / MemoryError.
        """
        self._check_epoch(epoch)
        requested_dead, dead_items = _identities(revoke)
        requested_live, live_items = _identities(reinstate)
        if requested_dead & requested_live:
            raise ValueError("one batch cannot both revoke and reinstate an identity")
        added = requested_dead - self._revoked
        removed = requested_live & self._revoked
        clause_deltas: dict[int, int] = {}
        evidence_visits = 0
        for identities, direction in ((added, 1), (removed, -1)):
            for evidence in identities:
                for clause_id in self._incidence.get(evidence, ()):
                    evidence_visits += 1
                    clause_deltas[clause_id] = clause_deltas.get(clause_id, 0) + direction

        planned_clauses: dict[int, int] = {}
        bound_deltas: dict[str, list[int]] = {}
        changed_clauses = bound_visits = 0
        for clause_id, delta in clause_deltas.items():
            old = self._blocked[clause_id]
            new = old + delta
            if not 0 <= new <= self._clause_lengths[clause_id]:
                raise CannotCheck("CANNOT_CHECK_CLAUSE_COUNTER_INVARIANT")
            planned_clauses[clause_id] = new
            if (old == 0) == (new == 0):
                continue
            changed_clauses += 1
            direction = 1 if new == 0 else -1
            for object_id, bound in self._consumers[clause_id]:
                bound_visits += 1
                bound_deltas.setdefault(object_id, [0, 0])[bound] += direction

        planned_counts: dict[str, tuple[int, int]] = {}
        changes: dict[str, tuple[Liveness, Liveness]] = {}
        for object_id, delta in bound_deltas.items():
            old = self._counts[object_id]
            new = (old[0] + delta[0], old[1] + delta[1])
            limits = self._limits[object_id]
            if any(not 0 <= new[i] <= limits[i] for i in (0, 1)) or (new[0] and not new[1]):
                raise CannotCheck("CANNOT_CHECK_INTERVAL_COUNTER_INVARIANT")
            planned_counts[object_id] = new
            before, after = _liveness(old), _liveness(new)
            if before is not after:
                changes[object_id] = (before, after)

        result = IndexDelta(
            MappingProxyType(changes),
            IndexWork(
                dead_items + live_items,
                len(requested_dead) + len(requested_live),
                len(added) + len(removed),
                evidence_visits,
                changed_clauses,
                bound_visits,
                len(bound_deltas),
                len(changes),
            ),
        )
        # The owner serializes this small mutation phase with its transaction.
        for clause_id, count in planned_clauses.items():
            self._blocked[clause_id] = count
        self._counts.update(planned_counts)
        self._revoked.difference_update(removed)
        self._revoked.update(added)
        return result
