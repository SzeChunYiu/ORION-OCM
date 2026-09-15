from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import json
from typing import Iterable, Mapping, Sequence

CLAIM_CEILING = "GMI_EXACT_DEVELOPMENTAL_NATURALITY_AT_REGISTERED_FINITE_DETERMINISTIC_SCOPE"


class NaturalityError(ValueError):
    pass


@dataclass(frozen=True)
class DevSystem:
    name: str
    states: tuple[str, ...]
    experiences: tuple[str, ...]
    outputs: tuple[tuple[str, str], ...]
    updates: tuple[tuple[str, str, str], ...]

    def output_map(self) -> dict[str, str]:
        return dict(self.outputs)

    def update_map(self) -> dict[tuple[str, str], str]:
        return {(s, e): t for s, e, t in self.updates}


@dataclass(frozen=True)
class StateTransform:
    source: str
    target: str
    mapping: tuple[tuple[str, str], ...]
    evidence: tuple[str, ...]

    def map_dict(self) -> dict[str, str]:
        return dict(self.mapping)


def make_system(name: str, states: Sequence[str], experiences: Sequence[str], outputs: Mapping[str, str], updates: Mapping[tuple[str, str], str]) -> DevSystem:
    ss = tuple(states)
    es = tuple(experiences)
    if not name or not ss or not es or len(set(ss)) != len(ss) or len(set(es)) != len(es):
        raise NaturalityError("MALFORMED_SYSTEM")
    if set(outputs) != set(ss):
        raise NaturalityError("NON_TOTAL_OUTPUT_MAP")
    required = {(s, e) for s in ss for e in es}
    if set(updates) != required:
        raise NaturalityError("NON_TOTAL_UPDATE_MAP")
    if any(t not in set(ss) for t in updates.values()):
        raise NaturalityError("UPDATE_ESCAPES_CARRIER")
    return DevSystem(name, ss, es, tuple(sorted(outputs.items())), tuple(sorted((s, e, t) for (s, e), t in updates.items())))


def make_transform(source: DevSystem, target: DevSystem, mapping: Mapping[str, str], evidence: Iterable[str]) -> StateTransform:
    if source.experiences != target.experiences:
        raise NaturalityError("EXPERIENCE_ALPHABET_MISMATCH")
    if set(mapping) != set(source.states):
        raise NaturalityError("NON_TOTAL_STATE_MAP")
    if any(t not in set(target.states) for t in mapping.values()):
        raise NaturalityError("MAP_ESCAPES_TARGET_CARRIER")
    ev = tuple(sorted(set(x for x in evidence if x)))
    if not ev:
        raise NaturalityError("MISSING_EVIDENCE")
    return StateTransform(source.name, target.name, tuple(sorted(mapping.items())), ev)


def identity(system: DevSystem) -> StateTransform:
    return make_transform(system, system, {s: s for s in system.states}, (f"identity:{system.name}",))


def _check_endpoints(source: DevSystem, target: DevSystem, transform: StateTransform) -> None:
    if transform.source != source.name or transform.target != target.name:
        raise NaturalityError("TRANSFORM_ENDPOINT_MISMATCH")
    f = transform.map_dict()
    if set(f) != set(source.states):
        raise NaturalityError("NON_TOTAL_STATE_MAP")
    if any(v not in set(target.states) for v in f.values()):
        raise NaturalityError("MAP_ESCAPES_TARGET_CARRIER")


def static_behavior_preserving(source: DevSystem, target: DevSystem, transform: StateTransform) -> bool:
    _check_endpoints(source, target, transform)
    sm, tm, f = source.output_map(), target.output_map(), transform.map_dict()
    return all(sm[s] == tm[f[s]] for s in source.states)


def naturality_violations(source: DevSystem, target: DevSystem, transform: StateTransform) -> list[tuple[str, str, str, str]]:
    _check_endpoints(source, target, transform)
    if source.experiences != target.experiences:
        raise NaturalityError("EXPERIENCE_ALPHABET_MISMATCH")
    f = transform.map_dict()
    su, tu = source.update_map(), target.update_map()
    bad = []
    for s in source.states:
        for e in source.experiences:
            lhs = f[su[(s, e)]]
            rhs = tu[(f[s], e)]
            if lhs != rhs:
                bad.append((s, e, lhs, rhs))
    return bad


def exact_developmental_natural(source: DevSystem, target: DevSystem, transform: StateTransform) -> bool:
    return static_behavior_preserving(source, target, transform) and not naturality_violations(source, target, transform)


def compose_transforms(source: DevSystem, middle: DevSystem, target: DevSystem, first: StateTransform, second: StateTransform) -> StateTransform:
    if not exact_developmental_natural(source, middle, first):
        raise NaturalityError("FIRST_NOT_EXACT_DEVELOPMENTAL_NATURAL")
    if not exact_developmental_natural(middle, target, second):
        raise NaturalityError("SECOND_NOT_EXACT_DEVELOPMENTAL_NATURAL")
    f, g = first.map_dict(), second.map_dict()
    composite = make_transform(source, target, {s: g[f[s]] for s in source.states}, tuple(sorted(set(first.evidence + second.evidence))))
    if not exact_developmental_natural(source, target, composite):
        raise NaturalityError("COMPOSITION_NATURALITY_BROKEN")
    return composite


def evolve(system: DevSystem, state: str, experiences: Sequence[str]) -> str:
    if state not in set(system.states):
        raise NaturalityError("UNKNOWN_STATE")
    if any(e not in set(system.experiences) for e in experiences):
        raise NaturalityError("UNKNOWN_EXPERIENCE")
    u = system.update_map()
    cur = state
    for e in experiences:
        cur = u[(cur, e)]
    return cur


def trajectory_preserved(source: DevSystem, target: DevSystem, transform: StateTransform, start: str, experiences: Sequence[str]) -> bool:
    if not exact_developmental_natural(source, target, transform):
        return False
    f = transform.map_dict()
    return f[evolve(source, start, experiences)] == evolve(target, f[start], experiences)


def exhaustive_trajectory_check(source: DevSystem, target: DevSystem, transform: StateTransform, max_length: int) -> int:
    if max_length < 0:
        raise NaturalityError("NEGATIVE_MAX_LENGTH")
    checked = 0
    for start in source.states:
        for length in range(max_length + 1):
            for seq in product(source.experiences, repeat=length):
                assert trajectory_preserved(source, target, transform, start, seq)
                checked += 1
    return checked


def finite_certificate() -> dict[str, object]:
    m = make_system("M", ("m0", "m1"), ("x", "y"), {"m0": "0", "m1": "1"}, {("m0", "x"): "m1", ("m1", "x"): "m0", ("m0", "y"): "m0", ("m1", "y"): "m1"})
    n = make_system("N", ("nA", "nB"), ("x", "y"), {"nA": "0", "nB": "1"}, {("nA", "x"): "nB", ("nB", "x"): "nA", ("nA", "y"): "nA", ("nB", "y"): "nB"})
    p = make_system("P", ("pL", "pR"), ("x", "y"), {"pL": "0", "pR": "1"}, {("pL", "x"): "pR", ("pR", "x"): "pL", ("pL", "y"): "pL", ("pR", "y"): "pR"})
    f = make_transform(m, n, {"m0": "nA", "m1": "nB"}, ("e_mn",))
    g = make_transform(n, p, {"nA": "pL", "nB": "pR"}, ("e_np",))
    assert exact_developmental_natural(m, n, f)
    assert exact_developmental_natural(n, p, g)
    assert exact_developmental_natural(m, m, identity(m))
    gf = compose_transforms(m, n, p, f, g)
    assert exact_developmental_natural(m, p, gf)
    trajectory_checks = exhaustive_trajectory_check(m, p, gf, 5)

    n_bad = make_system("N_BAD", ("bA", "bB"), ("x", "y"), {"bA": "0", "bB": "1"}, {("bA", "x"): "bA", ("bB", "x"): "bB", ("bA", "y"): "bA", ("bB", "y"): "bB"})
    bad = make_transform(m, n_bad, {"m0": "bA", "m1": "bB"}, ("e_static",))
    assert static_behavior_preserving(m, n_bad, bad)
    bad_violations = naturality_violations(m, n_bad, bad)
    assert bad_violations and not exact_developmental_natural(m, n_bad, bad)

    hostiles: dict[str, bool] = {}
    try:
        q = make_system("Q", ("q0",), ("z",), {"q0": "0"}, {("q0", "z"): "q0"})
        make_transform(m, q, {"m0": "q0", "m1": "q0"}, ("e",))
    except NaturalityError:
        hostiles["experience_mismatch"] = True
    else:
        hostiles["experience_mismatch"] = False
    for name, thunk in {
        "non_total_map": lambda: make_transform(m, n, {"m0": "nA"}, ("e",)),
        "map_escape": lambda: make_transform(m, n, {"m0": "nA", "m1": "ghost"}, ("e",)),
        "missing_evidence": lambda: make_transform(m, n, {"m0": "nA", "m1": "nB"}, ()),
        "update_escape": lambda: make_system("ESC", ("s",), ("x",), {"s": "0"}, {("s", "x"): "ghost"}),
    }.items():
        try:
            thunk()
        except NaturalityError:
            hostiles[name] = True
        else:
            hostiles[name] = False
    label_bad = make_system("N_LABEL_BAD", ("nA", "nB"), ("x", "y"), {"nA": "1", "nB": "0"}, {("nA", "x"): "nB", ("nB", "x"): "nA", ("nA", "y"): "nA", ("nB", "y"): "nB"})
    label_t = make_transform(m, label_bad, {"m0": "nA", "m1": "nB"}, ("e",))
    hostiles["behavior_mismatch"] = naturality_violations(m, label_bad, label_t) == [] and not exact_developmental_natural(m, label_bad, label_t)
    assert all(hostiles.values())

    return {
        "schema": "GMI_833_DEVELOPMENTAL_NATURALITY_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": {"identity_natural": True, "composition_natural": True, "finite_trajectory_preservation": True, "static_only_hostile_detected": True, "behavior_separate_from_naturality": True, "fail_closed_hostiles": all(hostiles.values())},
        "counts": {"state_experience_commuting_cells_per_good_map": len(m.states) * len(m.experiences), "trajectory_checks_through_length_5": trajectory_checks, "static_only_naturality_violations": len(bad_violations), "hostile_cases": len(hostiles)},
        "witnesses": {"static_hostile_first_violation": list(bad_violations[0]), "composite_mapping": [list(x) for x in gf.mapping], "hostiles": hostiles},
        "forbidden_promotions": ["APPROXIMATE_NATURALITY_PROVED", "STOCHASTIC_DEVELOPMENTAL_NATURALITY_PROVED", "OPTIMIZER_EQUIVALENCE_PROVED", "GRAMMAR_REMINT_INVARIANCE_PROVED", "KNOWN_FORM_RECOVERY_COMPLETE", "COMPLETE_GMI"],
    }


if __name__ == "__main__":
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))
