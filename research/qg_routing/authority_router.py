"""Research-only transfer of ORION-Q #908's authority-before-cost routing.

This module indexes a host-supplied catalogue. It neither proves that a summary
is sufficient nor grants execution/commit authority. Eligibility is a fresh,
snapshot-scoped host check; the real OCM constitutional boundary remains outside.
No Transformer, trained parameters, quantum backend, or runtime integration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Callable, Mapping


def _text(value: str, name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def _natural(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


class Kind(str, Enum):
    ANSWER = "ANSWER"
    REFINE = "REFINE"


class Eligibility(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class Status(str, Enum):
    SELECTED = "SELECTED"
    NO_QUERY_MATCH = "NO_QUERY_MATCH_IN_CATALOGUE"
    NO_ELIGIBLE = "NO_APPROVED_ROUTE_IN_CATALOGUE"
    UNRESOLVED = "ELIGIBILITY_UNRESOLVED"
    ENVELOPE = "NO_ROUTE_IN_ESTIMATED_ENVELOPE"
    LIMIT = "CANDIDATE_LIMIT"
    CHECK_ERROR = "ELIGIBILITY_CHECK_ERROR"


class Preflight(str, Enum):
    READY = "READY_FOR_HOST_COMMIT_CHECK"
    NO_SELECTION = "NO_SELECTION"
    STALE = "STALE_DECISION"
    CHANGED = "CATALOGUE_ROUTE_CHANGED"
    REJECTED = "ELIGIBILITY_REJECTED"
    UNKNOWN = "ELIGIBILITY_UNKNOWN"
    CHECK_ERROR = "ELIGIBILITY_CHECK_ERROR"


@dataclass(frozen=True, slots=True)
class Query:
    key: str
    context: str
    authority_kind: str
    snapshot: str  # Host identity covering field, evidence, scope and checker state.

    def __post_init__(self) -> None:
        for name in ("key", "context", "authority_kind", "snapshot"):
            _text(getattr(self, name), name)


@dataclass(frozen=True, slots=True)
class Route:
    route_id: str
    query_keys: frozenset[str]
    work_estimate: int
    active_bytes_estimate: int
    contract_ref: str  # Host-resolved contract identity, not a proof by itself.
    kind: Kind = Kind.ANSWER

    def __post_init__(self) -> None:
        _text(self.route_id, "route_id")
        _text(self.contract_ref, "contract_ref")
        if isinstance(self.query_keys, str):
            raise ValueError("query_keys must be a collection, not a string")
        keys = frozenset(self.query_keys)
        if not keys:
            raise ValueError("route needs at least one query key")
        for key in keys:
            _text(key, "query key")
        object.__setattr__(self, "query_keys", keys)
        _natural(self.work_estimate, "work_estimate")
        _natural(self.active_bytes_estimate, "active_bytes_estimate")
        if type(self.kind) is not Kind:
            raise ValueError("kind must be a Kind")


@dataclass(frozen=True, slots=True)
class Envelope:
    """Limits on supplied estimates; these do NOT enforce runtime resource use."""

    work: int
    active_bytes: int

    def __post_init__(self) -> None:
        _natural(self.work, "work envelope")
        _natural(self.active_bytes, "active bytes envelope")

    def covers(self, route: Route) -> bool:
        return (route.work_estimate <= self.work
                and route.active_bytes_estimate <= self.active_bytes)


@dataclass(frozen=True, slots=True)
class Work:
    candidates_available: int = 0
    routes_inspected: int = 0
    eligibility_calls: int = 0
    rejected: int = 0
    unknown: int = 0
    outside_envelope: int = 0
    index_probes: int = 1


@dataclass(frozen=True, slots=True)
class Selection:
    query: Query
    envelope: Envelope
    status: Status
    route: Route | None
    work: Work


# Implementations must resolve authoritative contracts and pin the requested
# snapshot. Returning strings/truthy values instead of this enum is a failure.
Check = Callable[[Route, Query], Eligibility]


@dataclass(frozen=True, slots=True)
class RouteIndex:
    routes: tuple[Route, ...]
    _by_query: Mapping[str, tuple[Route, ...]] = field(init=False, repr=False, compare=False)
    _by_id: Mapping[str, Route] = field(init=False, repr=False, compare=False)
    index_references: int = field(init=False)

    def __post_init__(self) -> None:
        routes = tuple(self.routes)
        by_id: dict[str, Route] = {}
        by_query: dict[str, list[Route]] = {}
        refs = 0
        for route in routes:
            if type(route) is not Route:
                raise ValueError("catalogue must contain Route values")
            if route.route_id in by_id:
                raise ValueError(f"duplicate route id: {route.route_id}")
            by_id[route.route_id] = route
            for key in sorted(route.query_keys):
                by_query.setdefault(key, []).append(route)
                refs += 1
        object.__setattr__(self, "routes", routes)
        object.__setattr__(self, "_by_id", MappingProxyType(by_id))
        object.__setattr__(self, "_by_query", MappingProxyType(
            {key: tuple(values) for key, values in by_query.items()}))
        object.__setattr__(self, "index_references", refs)

    def select(self, query: Query, check: Check, envelope: Envelope, *,
               priority: str = "work_first", max_candidates: int | None = None) -> Selection:
        """Choose among APPROVED routes in the exact key bucket.

        Cost ordering is an explicit policy, not an equivalence/sufficiency order.
        UNKNOWN routes are never selected. A known route can still be selected
        when another is UNKNOWN; minimality is ONLY over approved routes offered
        in this catalogue, not all possible cognition. REFINE remains a request
        for more computation, not an answer. The callback must be side-effect-free.
        """
        if priority not in ("work_first", "bytes_first"):
            raise ValueError("unknown cost priority")
        if max_candidates is not None:
            _natural(max_candidates, "max_candidates")
        candidates = self._by_query.get(query.key, ())
        total = len(candidates)
        if max_candidates is not None and total > max_candidates:
            return Selection(query, envelope, Status.LIMIT, None, Work(total))
        if not candidates:
            return Selection(query, envelope, Status.NO_QUERY_MATCH, None, Work())
        inspected = calls = rejected = unknown = outside = 0
        best: Route | None = None
        best_key: tuple[int, int, str] | None = None
        for route in candidates:
            inspected += 1
            # Estimates can exclude work; they cannot authorize a route.
            if not envelope.covers(route):
                outside += 1
                continue
            calls += 1
            try:
                eligibility = check(route, query)
            except Exception:
                return Selection(query, envelope, Status.CHECK_ERROR, None,
                                 Work(total, inspected, calls, rejected, unknown, outside))
            if type(eligibility) is not Eligibility:
                return Selection(query, envelope, Status.CHECK_ERROR, None,
                                 Work(total, inspected, calls, rejected, unknown, outside))
            if eligibility is Eligibility.REJECTED:
                rejected += 1
                continue
            if eligibility is Eligibility.UNKNOWN:
                unknown += 1
                continue
            key = ((route.work_estimate, route.active_bytes_estimate, route.route_id)
                   if priority == "work_first" else
                   (route.active_bytes_estimate, route.work_estimate, route.route_id))
            if best_key is None or key < best_key:
                best, best_key = route, key
        status = (Status.SELECTED if best is not None else Status.UNRESOLVED if unknown
                  else Status.ENVELOPE if outside == total else Status.NO_ELIGIBLE)
        return Selection(query, envelope, status, best,
                         Work(total, inspected, calls, rejected, unknown, outside))

    def preflight(self, selected: Selection, current: Query, check: Check) -> Preflight:
        """Recheck one route; READY is NOT an action/commit receipt.

        The host must atomically pin or revalidate the snapshot when it actually
        executes/commits. This function cannot close a host-side time-of-check gap.
        Global snapshot invalidation is conservative, not a local-revision result.
        """
        if selected.status is not Status.SELECTED or selected.route is None:
            return Preflight.NO_SELECTION
        if selected.query != current:
            return Preflight.STALE
        route = self._by_id.get(selected.route.route_id)
        if route != selected.route:
            return Preflight.CHANGED
        if current.key not in route.query_keys or not selected.envelope.covers(route):
            return Preflight.REJECTED
        try:
            eligibility = check(route, current)
        except Exception:
            return Preflight.CHECK_ERROR
        if type(eligibility) is not Eligibility:
            return Preflight.CHECK_ERROR
        return {Eligibility.APPROVED: Preflight.READY,
                Eligibility.REJECTED: Preflight.REJECTED,
                Eligibility.UNKNOWN: Preflight.UNKNOWN}[eligibility]
