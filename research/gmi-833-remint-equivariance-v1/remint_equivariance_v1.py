from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from itertools import permutations
from math import inf
from typing import Iterable, Mapping, Sequence
import json

CLAIM_CEILING = "GMI_FINITE_SEMANTIC_REMINT_EQUIVARIANCE_AT_REGISTERED_SCOPE"


class RemintError(ValueError):
    pass


def F(x: int | str | Fraction) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


@dataclass(frozen=True)
class Mechanism:
    name: str
    states: tuple[str, ...]
    initial: str
    actions: tuple[str, ...]
    interventions: tuple[str, ...]
    outputs: tuple[tuple[str, str], ...]
    transitions: tuple[tuple[str, str, str], ...]
    intervention_responses: tuple[tuple[str, str, str], ...]
    developmental_edges: tuple[tuple[str, str], ...]
    resources: tuple[Fraction, ...]

    def output_map(self) -> dict[str, str]:
        return dict(self.outputs)

    def transition_map(self) -> dict[tuple[str, str], str]:
        return {(s, a): t for s, a, t in self.transitions}

    def intervention_map(self) -> dict[tuple[str, str], str]:
        return {(s, j): r for s, j, r in self.intervention_responses}


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    burden: Fraction


def make_mechanism(
    name: str,
    states: Sequence[str],
    initial: str,
    actions: Sequence[str],
    interventions: Sequence[str],
    outputs: Mapping[str, str],
    transitions: Mapping[tuple[str, str], str],
    intervention_responses: Mapping[tuple[str, str], str],
    developmental_edges: Iterable[tuple[str, str]],
    resources: Sequence[int | str | Fraction],
) -> Mechanism:
    ss = tuple(sorted(states))
    aa = tuple(sorted(actions))
    jj = tuple(sorted(interventions))
    if not name or not ss or len(set(ss)) != len(ss):
        raise RemintError("MALFORMED_STATE_CARRIER")
    if not aa or len(set(aa)) != len(aa) or len(set(jj)) != len(jj):
        raise RemintError("MALFORMED_EXTERNAL_ALPHABET")
    if initial not in set(ss):
        raise RemintError("INITIAL_OUTSIDE_CARRIER")
    if set(outputs) != set(ss):
        raise RemintError("NON_TOTAL_OUTPUT_MAP")
    req_t = {(s, a) for s in ss for a in aa}
    if set(transitions) != req_t:
        raise RemintError("NON_TOTAL_TRANSITION_MAP")
    if any(t not in set(ss) for t in transitions.values()):
        raise RemintError("TRANSITION_ESCAPES_CARRIER")
    req_i = {(s, j) for s in ss for j in jj}
    if set(intervention_responses) != req_i:
        raise RemintError("NON_TOTAL_INTERVENTION_MAP")
    dev = tuple(sorted(set(developmental_edges)))
    if any(a not in set(ss) or b not in set(ss) for a, b in dev):
        raise RemintError("DEVELOPMENT_EDGE_ESCAPES_CARRIER")
    rr = tuple(F(x) for x in resources)
    if not rr or any(x < 0 for x in rr):
        raise RemintError("MALFORMED_RESOURCES")
    return Mechanism(
        name=name,
        states=ss,
        initial=initial,
        actions=aa,
        interventions=jj,
        outputs=tuple(sorted(outputs.items())),
        transitions=tuple(sorted((s, a, t) for (s, a), t in transitions.items())),
        intervention_responses=tuple(sorted((s, j, r) for (s, j), r in intervention_responses.items())),
        developmental_edges=dev,
        resources=rr,
    )


def validate_bijection(states: Sequence[str], mapping: Mapping[str, str]) -> None:
    if set(mapping) != set(states):
        raise RemintError("NON_TOTAL_REMINT")
    vals = tuple(mapping[s] for s in states)
    if any(not v for v in vals):
        raise RemintError("EMPTY_REMINT_LABEL")
    if len(set(vals)) != len(vals):
        raise RemintError("NON_BIJECTIVE_REMINT")


def remint(m: Mechanism, mapping: Mapping[str, str], *, name: str | None = None) -> Mechanism:
    validate_bijection(m.states, mapping)
    out = m.output_map()
    trans = m.transition_map()
    inter = m.intervention_map()
    return make_mechanism(
        name or m.name,
        [mapping[s] for s in m.states],
        mapping[m.initial],
        m.actions,
        m.interventions,
        {mapping[s]: out[s] for s in m.states},
        {(mapping[s], a): mapping[trans[(s, a)]] for s in m.states for a in m.actions},
        {(mapping[s], j): inter[(s, j)] for s in m.states for j in m.interventions},
        {(mapping[a], mapping[b]) for a, b in m.developmental_edges},
        m.resources,
    )


def identity_remint(m: Mechanism) -> dict[str, str]:
    return {s: s for s in m.states}


def inverse_remint(mapping: Mapping[str, str]) -> dict[str, str]:
    vals = tuple(mapping.values())
    if len(set(vals)) != len(vals):
        raise RemintError("NON_BIJECTIVE_REMINT")
    return {v: k for k, v in mapping.items()}


def compose_remints(first: Mapping[str, str], second: Mapping[str, str]) -> dict[str, str]:
    if set(first.values()) != set(second.keys()):
        raise RemintError("REMINT_COMPOSITION_ENDPOINT_MISMATCH")
    return {k: second[v] for k, v in first.items()}


def _encoding_under_index(m: Mechanism, index: Mapping[str, int]) -> tuple[object, ...]:
    out = m.output_map()
    trans = m.transition_map()
    inter = m.intervention_map()
    state_order = tuple(sorted(m.states, key=lambda s: index[s]))
    outputs = tuple(out[s] for s in state_order)
    transitions = tuple(
        (index[s], a, index[trans[(s, a)]])
        for s in state_order
        for a in m.actions
    )
    interventions = tuple(
        (index[s], j, inter[(s, j)])
        for s in state_order
        for j in m.interventions
    )
    dev = tuple(sorted((index[a], index[b]) for a, b in m.developmental_edges))
    resources = tuple((x.numerator, x.denominator) for x in m.resources)
    return (
        len(m.states),
        index[m.initial],
        m.actions,
        m.interventions,
        outputs,
        transitions,
        interventions,
        dev,
        resources,
    )


def canonical_fingerprint(m: Mechanism) -> str:
    labels = tuple(range(len(m.states)))
    encodings = []
    for perm in permutations(labels):
        index = {s: perm[i] for i, s in enumerate(m.states)}
        encodings.append(_encoding_under_index(m, index))
    best = min(encodings)
    return json.dumps(best, separators=(",", ":"))


def semantic_equal_up_to_presentation(a: Mechanism, b: Mechanism) -> bool:
    return canonical_fingerprint(a) == canonical_fingerprint(b)


def audit_claimed_remint(source: Mechanism, target: Mechanism, mapping: Mapping[str, str]) -> tuple[bool, str]:
    try:
        candidate = remint(source, mapping, name=target.name)
    except RemintError as exc:
        return False, str(exc)
    # Equality is exact because constructors canonicalize order and the target name was matched.
    fields = (
        "states", "initial", "actions", "interventions", "outputs", "transitions",
        "intervention_responses", "developmental_edges", "resources",
    )
    for field in fields:
        if getattr(candidate, field) != getattr(target, field):
            return False, f"SEMANTIC_MUTATION:{field}"
    return True, "CLEAN_SEMANTIC_REMINT"


def make_edge(source: str, target: str, burden: int | str | Fraction) -> GraphEdge:
    b = F(burden)
    if b < 0:
        raise RemintError("NEGATIVE_TRANSFORM_BURDEN")
    return GraphEdge(source, target, b)


def quotient_distance_matrix(mechanisms: Mapping[str, Mechanism], edges: Sequence[GraphEdge]) -> dict[tuple[str, str], Fraction | float]:
    if set(mechanisms) == set():
        raise RemintError("EMPTY_MECHANISM_GRAPH")
    fingerprints = {name: canonical_fingerprint(m) for name, m in mechanisms.items()}
    qnodes = sorted(set(fingerprints.values()))
    adjacency: dict[str, list[tuple[Fraction, str]]] = {q: [] for q in qnodes}
    for edge in edges:
        if edge.source not in mechanisms or edge.target not in mechanisms:
            raise RemintError("EDGE_ENDPOINT_UNKNOWN")
        adjacency[fingerprints[edge.source]].append((edge.burden, fingerprints[edge.target]))
    result: dict[tuple[str, str], Fraction | float] = {}
    for src in qnodes:
        dist: dict[str, Fraction | float] = {q: inf for q in qnodes}
        dist[src] = F(0)
        heap: list[tuple[Fraction, str]] = [(F(0), src)]
        while heap:
            d, u = heappop(heap)
            if dist[u] != d:
                continue
            for w, v in adjacency[u]:
                nd = d + w
                if dist[v] == inf or nd < dist[v]:
                    dist[v] = nd
                    heappush(heap, (nd, v))
        for dst in qnodes:
            result[(src, dst)] = dist[dst]
    return result


def _fixture() -> tuple[Mechanism, Mechanism, Mechanism]:
    a = make_mechanism(
        "A", ("s0", "s1", "s2"), "s0", ("x", "y"), ("probe",),
        {"s0": "0", "s1": "1", "s2": "1"},
        {
            ("s0", "x"): "s1", ("s0", "y"): "s0",
            ("s1", "x"): "s2", ("s1", "y"): "s0",
            ("s2", "x"): "s2", ("s2", "y"): "s1",
        },
        {("s0", "probe"): "low", ("s1", "probe"): "high", ("s2", "probe"): "high"},
        {("s0", "s1"), ("s1", "s2")}, (1, 2, 3),
    )
    b = make_mechanism(
        "B", ("b0", "b1"), "b0", ("x", "y"), ("probe",),
        {"b0": "0", "b1": "1"},
        {("b0", "x"): "b1", ("b0", "y"): "b0", ("b1", "x"): "b1", ("b1", "y"): "b0"},
        {("b0", "probe"): "low", ("b1", "probe"): "high"},
        {("b0", "b1")}, (2, 1, 1),
    )
    c = make_mechanism(
        "C", ("c",), "c", ("x", "y"), ("probe",),
        {"c": "0"},
        {("c", "x"): "c", ("c", "y"): "c"},
        {("c", "probe"): "low"},
        set(), (1, 1, 1),
    )
    return a, b, c


def finite_certificate() -> dict[str, object]:
    a, b, c = _fixture()
    r1 = {"s0": "alpha", "s1": "beta", "s2": "gamma"}
    r2 = {"alpha": "u", "beta": "v", "gamma": "w"}
    ar1 = remint(a, r1, name="A1")
    ar2 = remint(ar1, r2, name="A2")
    composed = compose_remints(r1, r2)
    ar_comp = remint(a, composed, name="A2")
    assert ar2 == ar_comp
    inv = inverse_remint(r1)
    assert remint(ar1, inv, name="A") == a
    assert remint(a, identity_remint(a), name="A") == a

    base_fp = canonical_fingerprint(a)
    remint_fingerprints = set()
    state_names = ("p", "q", "r")
    for perm in permutations(state_names):
        rm = dict(zip(a.states, perm, strict=True))
        x = remint(a, rm, name="A_perm")
        remint_fingerprints.add(canonical_fingerprint(x))
    assert remint_fingerprints == {base_fp}

    base_mechs = {"A": a, "B": b, "C": c}
    base_edges = (make_edge("A", "B", 2), make_edge("B", "C", 3), make_edge("A", "C", 8), make_edge("C", "A", 11))
    base_d = quotient_distance_matrix(base_mechs, base_edges)
    a_m = remint(a, {"s0": "A-9", "s1": "A-2", "s2": "A-7"}, name="A_m")
    b_m = remint(b, {"b0": "left", "b1": "right"}, name="B_m")
    c_m = remint(c, {"c": "singleton"}, name="C_m")
    rem_mechs = {"A_m": a_m, "B_m": b_m, "C_m": c_m}
    rem_edges = (make_edge("A_m", "B_m", 2), make_edge("B_m", "C_m", 3), make_edge("A_m", "C_m", 8), make_edge("C_m", "A_m", 11))
    rem_d = quotient_distance_matrix(rem_mechs, rem_edges)
    assert base_d == rem_d

    hostiles: dict[str, bool] = {}
    try:
        remint(a, {"s0": "z", "s1": "z", "s2": "w"})
    except RemintError:
        hostiles["non_bijective"] = True
    else:
        hostiles["non_bijective"] = False

    clean_target = remint(a, r1, name="TARGET")
    ok, why = audit_claimed_remint(a, clean_target, r1)
    assert ok and why == "CLEAN_SEMANTIC_REMINT"

    def mutated_target(kind: str) -> Mechanism:
        m = clean_target
        outputs = m.output_map()
        transitions = m.transition_map()
        interventions = m.intervention_map()
        dev = set(m.developmental_edges)
        resources = list(m.resources)
        if kind == "output":
            outputs["alpha"] = "mutated"
        elif kind == "transition":
            transitions[("alpha", "x")] = "alpha"
        elif kind == "intervention":
            interventions[("alpha", "probe")] = "mutated"
        elif kind == "development":
            dev.add(("gamma", "alpha"))
        elif kind == "resources":
            resources[0] += 1
        else:
            raise AssertionError(kind)
        return make_mechanism(
            "TARGET", m.states, m.initial, m.actions, m.interventions,
            outputs, transitions, interventions, dev, resources,
        )

    for kind in ("output", "transition", "intervention", "development", "resources"):
        ok, reason = audit_claimed_remint(a, mutated_target(kind), r1)
        hostiles[f"semantic_{kind}_mutation"] = (not ok and reason.startswith("SEMANTIC_MUTATION:"))
    assert all(hostiles.values())

    # Explicit boundary: remint invariance says nothing about search order.
    candidates = ("same_semantics_long_encoding", "same_semantics_short_encoding")
    forward_budget_one = candidates[0]
    reverse_budget_one = tuple(reversed(candidates))[0]
    search_order_sensitive = forward_budget_one != reverse_budget_one
    assert search_order_sensitive

    return {
        "schema": "GMI_833_REMINT_EQUIVARIANCE_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": {
            "identity_remint": True,
            "inverse_remint": True,
            "composition_remint": True,
            "canonical_fingerprint_invariant": True,
            "all_six_three_state_remints_same_fingerprint": len(remint_fingerprints) == 1,
            "quotient_transform_geometry_invariant": base_d == rem_d,
            "semantic_mutation_hostiles_detected": all(hostiles.values()),
            "search_invariance_not_inferred": search_order_sensitive,
        },
        "counts": {
            "three_state_remints_exhausted": 6,
            "semantic_hostile_cases": len(hostiles),
            "base_quotient_pairs": len(base_d),
        },
        "witnesses": {
            "canonical_fingerprint": base_fp,
            "hostiles": hostiles,
            "search_order_forward_winner": forward_budget_one,
            "search_order_reverse_winner": reverse_budget_one,
        },
        "forbidden_promotions": [
            "UNIVERSAL_GRAMMAR_NEUTRALITY_PROVED",
            "SEARCH_PRIOR_INVARIANCE_PROVED",
            "REACHABILITY_INVARIANCE_PROVED",
            "P3_KNOWN_FORM_RECOVERY_COMPLETE",
            "UNRESTRICTED_TOPOLOGY_INVARIANCE_PROVED",
            "COMPLETE_GMI",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))
