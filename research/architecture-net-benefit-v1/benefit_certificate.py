"""Exact finite-model lifetime cost certificates; not software qualification.

Apply ordinary difference constraints to a *paired* lifecycle transition graph.
Costs must already include all work in both arms. The caller must separately
prove that this graph covers the real implementations and their legal inputs.
No probability model, oracle features, learning, or third-party solver is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
import json
from typing import Iterable, Mapping


class InvalidModel(ValueError):
    pass


def rational(value: object) -> F:
    if type(value) not in (int, str, F):
        raise InvalidModel("use exact int, rational string, or Fraction; no bool/float")
    try:
        return F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise InvalidModel("invalid finite rational") from exc


def vector(values: Iterable[object]) -> tuple[F, ...]:
    result = tuple(rational(x) for x in values)
    if not result or any(x < 0 for x in result):
        raise InvalidModel("costs/prices must be nonempty and nonnegative")
    return result


@dataclass(frozen=True)
class Edge:
    name: str
    source: str
    target: str
    parent_cost: tuple[F, ...]
    architecture_cost: tuple[F, ...]
    demands: int = 1

    def __post_init__(self) -> None:
        if any(type(x) is not str or not x for x in (self.name, self.source, self.target)):
            raise InvalidModel("edge identities must be nonempty strings")
        object.__setattr__(self, "parent_cost", vector(self.parent_cost))
        object.__setattr__(self, "architecture_cost", vector(self.architecture_cost))
        if type(self.demands) is not int or self.demands < 0:
            raise InvalidModel("demands must be a nonnegative integer")


@dataclass(frozen=True)
class Model:
    start: str
    states: tuple[str, ...]
    coordinates: tuple[str, ...]
    edges: tuple[Edge, ...]
    binding: str

    def __post_init__(self) -> None:
        for name in ("states", "coordinates", "edges"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        for names in (self.states, self.coordinates):
            if not names or any(type(x) is not str or not x for x in names) or len(set(names)) != len(names):
                raise InvalidModel("state/coordinate names must be unique nonempty strings")
        if self.start not in self.states or type(self.binding) is not str or not self.binding:
            raise InvalidModel("unknown start or absent source/model binding")
        if any(type(e) is not Edge for e in self.edges):
            raise InvalidModel("edges must be Edge values")
        if len({e.name for e in self.edges}) != len(self.edges):
            raise InvalidModel("duplicate edge name")
        for e in self.edges:
            if e.source not in self.states or e.target not in self.states:
                raise InvalidModel("unknown endpoint")
            if len(e.parent_cost) != len(self.coordinates) or len(e.architecture_cost) != len(self.coordinates):
                raise InvalidModel("resource dimension mismatch")

    def fingerprint(self) -> str:
        body = {"start": self.start, "states": self.states, "coordinates": self.coordinates,
                "binding": self.binding, "edges": [
                    [e.name, e.source, e.target, list(map(str, e.parent_cost)),
                     list(map(str, e.architecture_cost)), e.demands] for e in self.edges]}
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def reachable(self) -> tuple[str, ...]:
        seen = {self.start}
        while True:
            expanded = seen | {e.target for e in self.edges if e.source in seen}
            if expanded == seen:
                return tuple(s for s in self.states if s in seen)
            seen = expanded


def checked_prices(model: Model, prices: Iterable[object]) -> tuple[F, ...]:
    p = vector(prices)
    if len(p) != len(model.coordinates) or not any(p):
        raise InvalidModel("nonzero prices of matching dimension required")
    return p


def gain(edge: Edge, prices: tuple[F, ...]) -> F:
    if len(prices) != len(edge.parent_cost):
        raise InvalidModel("price dimension mismatch")
    return sum((w * (p - a) for w, p, a in zip(prices, edge.parent_cost, edge.architecture_cost, strict=True)), F(0))


@dataclass(frozen=True)
class Certificate:
    model_sha256: str
    prices: tuple[F, ...]
    rate: F
    potentials: tuple[tuple[str, F], ...]


@dataclass(frozen=True)
class Countercycle:
    model_sha256: str
    prices: tuple[F, ...]
    rate: F
    edges: tuple[str, ...]


def verify(model: Model, cert: Certificate, *, fixed_overhead: object = 0) -> dict:
    """O(V+E) arithmetic certificate check after reachability; exact, model-only.

    Reachability in this simple implementation scans edges iteratively. No
    complexity claim here includes integer bit complexity or source validation.
    fixed_overhead is a scalar upper bound in the registered priced units.
    """
    p = checked_prices(model, cert.prices)
    rate = rational(cert.rate)
    overhead = rational(fixed_overhead)
    if overhead < 0 or cert.model_sha256 != model.fingerprint():
        raise InvalidModel("negative overhead or stale model certificate")
    pairs = tuple(cert.potentials)
    if len({s for s, _ in pairs}) != len(pairs):
        raise InvalidModel("duplicate potential state")
    phi = {s: rational(v) for s, v in pairs}
    reachable = set(model.reachable())
    if set(phi) != reachable:
        raise InvalidModel("potential must cover exactly every reachable state")
    for e in model.edges:
        if e.source in reachable and gain(e, p) - rate * e.demands < phi[e.target] - phi[e.source]:
            raise InvalidModel(f"failed edge inequality: {e.name}")
    debt = overhead + phi[model.start] - min(phi.values())
    return {"terminal": "FINITE_MODEL_COST_BOUND_VERIFIED", "model_sha256": model.fingerprint(),
            "rate": str(rate), "debt": str(debt),
            "first_guaranteed_strict_benefit_demand_count": int(debt // rate) + 1 if rate > 0 else None,
            "bound": "C_parent(H)-C_architecture(H) >= rate*H-debt",
            "software_correspondence_verified": False, "architecture_net_benefit_established": False}


def verify_countercycle(model: Model, witness: Countercycle) -> dict:
    p = checked_prices(model, witness.prices)
    rate = rational(witness.rate)
    if witness.model_sha256 != model.fingerprint() or not witness.edges:
        raise InvalidModel("stale or empty countercycle")
    by_name = {e.name: e for e in model.edges}
    try:
        cycle = tuple(by_name[name] for name in witness.edges)
    except KeyError as exc:
        raise InvalidModel("unknown countercycle edge") from exc
    if cycle[0].source not in set(model.reachable()):
        raise InvalidModel("countercycle is unreachable")
    if any(a.target != b.source for a, b in zip(cycle, cycle[1:] + cycle[:1], strict=True)):
        raise InvalidModel("countercycle is not closed and contiguous")
    total_gain = sum((gain(e, p) for e in cycle), F(0))
    demands = sum(e.demands for e in cycle)
    if total_gain - rate * demands >= 0:
        raise InvalidModel("cycle does not refute requested rate")
    return {"terminal": "REQUESTED_UNIFORM_RATE_REFUTED_IN_MODEL", "cycle": list(witness.edges),
            "cycle_gain": str(total_gain), "cycle_demands": demands, "requested_rate": str(rate),
            "architecture_net_benefit_established": False}


def synthesize(model: Model, prices: Iterable[object], rate: object = 0) -> Certificate | Countercycle:
    """Bellman-Ford difference constraints, or an independently checkable cycle.

    A synthetic zero-cost super-source reaches every actually reachable vertex.
    The super-source only constructs potentials; it is not a runtime action.
    """
    p = checked_prices(model, prices)
    delta = rational(rate)
    states = model.reachable()
    edges = tuple(e for e in model.edges if e.source in set(states))
    distance = {s: F(0) for s in states}
    predecessor: dict[str, Edge] = {}
    changed = None
    for _ in range(len(states)):
        changed = None
        for e in edges:
            candidate = distance[e.source] + gain(e, p) - delta * e.demands
            if candidate < distance[e.target]:
                distance[e.target] = candidate
                predecessor[e.target] = e
                changed = e.target
        if changed is None:
            offset = distance[model.start]
            cert = Certificate(model.fingerprint(), p, delta,
                               tuple((s, distance[s] - offset) for s in states))
            verify(model, cert)
            return cert
    if changed is None:
        raise AssertionError("unreachable synthesis branch")
    cursor = changed
    for _ in states:
        cursor = predecessor[cursor].source
    end = cursor
    backwards = []
    while True:
        e = predecessor[cursor]
        backwards.append(e.name)
        cursor = e.source
        if cursor == end:
            break
        if len(backwards) > len(states):
            raise AssertionError("countercycle extraction exceeded state bound")
    witness = Countercycle(model.fingerprint(), p, delta, tuple(reversed(backwards)))
    verify_countercycle(model, witness)
    return witness


def path_bound(model: Model, cert: Certificate, names: Iterable[str], *, fixed_overhead: object = 0) -> dict:
    """Check one observed model path against its all-path certificate."""
    bound = verify(model, cert, fixed_overhead=fixed_overhead)
    prices = checked_prices(model, cert.prices)
    rate = rational(cert.rate)
    edges = {e.name: e for e in model.edges}
    cursor, total, demands = model.start, -rational(fixed_overhead), 0
    for name in names:
        if name not in edges or edges[name].source != cursor:
            raise InvalidModel("unknown edge or non-contiguous path")
        e = edges[name]
        total += gain(e, prices)
        demands += e.demands
        cursor = e.target
    floor = rate * demands - F(bound["debt"])
    if total < floor:
        raise AssertionError("valid certificate failed path bound")
    return {"gain": str(total), "demands": demands, "lower_bound": str(floor)}
