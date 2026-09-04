from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


class CannotCheck(RuntimeError):
    pass


Warrant = frozenset[int]
Profile = tuple[Warrant, ...]


def _canon_profile(items: Iterable[Iterable[int]]) -> Profile:
    unique = {frozenset(item) for item in items}
    minimal = [w for w in unique if not any(v < w for v in unique)]
    return tuple(sorted(minimal, key=lambda w: (len(w), tuple(sorted(w)))))


def profile_or(left: Profile, right: Profile) -> Profile:
    """Alternative warrant: either profile suffices."""
    return _canon_profile((*left, *right))


def profile_and(left: Profile, right: Profile) -> Profile:
    """Conjunctive warrant: one warrant from each profile must survive."""
    if not left or not right:
        return ()
    return _canon_profile(a | b for a in left for b in right)


def profile_live(profile: Profile, revoked: Iterable[int]) -> bool:
    rv = frozenset(revoked)
    return any(not (w & rv) for w in profile)


def powerset(items: Sequence[int]) -> list[frozenset[int]]:
    out: list[frozenset[int]] = []
    for r in range(len(items) + 1):
        out.extend(frozenset(c) for c in itertools.combinations(items, r))
    return out


def all_profiles(n: int) -> list[Profile]:
    subsets = powerset(tuple(range(n)))
    profiles: set[Profile] = set()
    for mask in range(1 << len(subsets)):
        selected = [subsets[i] for i in range(len(subsets)) if mask & (1 << i)]
        profiles.add(_canon_profile(selected))
    return sorted(profiles, key=lambda p: (len(p), tuple((len(w), tuple(sorted(w))) for w in p)))


def check_warrant_semiring(n: int = 3) -> dict[str, int]:
    ps = all_profiles(n)
    zero: Profile = ()
    one: Profile = (frozenset(),)
    pair_checks = 0
    triple_checks = 0
    for a in ps:
        assert profile_or(a, zero) == a
        assert profile_and(a, one) == a
        assert profile_and(a, zero) == zero
        assert profile_or(a, a) == a
        for b in ps:
            pair_checks += 1
            assert profile_or(a, b) == profile_or(b, a)
            assert profile_and(a, b) == profile_and(b, a)
            for c in ps:
                triple_checks += 1
                assert profile_or(profile_or(a, b), c) == profile_or(a, profile_or(b, c))
                assert profile_and(profile_and(a, b), c) == profile_and(a, profile_and(b, c))
                assert profile_and(a, profile_or(b, c)) == profile_or(profile_and(a, b), profile_and(a, c))
    return {"profiles": len(ps), "pair_checks": pair_checks, "triple_checks": triple_checks}


@dataclass(frozen=True)
class Atom:
    atom_id: str
    atom_type: str
    profile: Profile
    quarantined: bool = False


@dataclass(frozen=True)
class Hyperedge:
    edge_id: str
    tails: tuple[str, ...]
    heads: tuple[str, ...]
    relation_type: str
    weight: Fraction = Fraction(1, 1)
    head_weights: tuple[Fraction, ...] = ()
    profile: Profile = (frozenset(),)

    def normalized_head_weights(self) -> tuple[Fraction, ...]:
        if not self.heads:
            raise ValueError("hyperedge needs a head")
        weights = self.head_weights or tuple(Fraction(1, 1) for _ in self.heads)
        if len(weights) != len(self.heads) or any(w < 0 for w in weights):
            raise ValueError("bad head weights")
        total = sum(weights, Fraction(0, 1))
        if total <= 0:
            raise ValueError("head weights need positive mass")
        return tuple(w / total for w in weights)


@dataclass(frozen=True)
class KnowledgeSpace:
    atoms: tuple[Atom, ...]
    hyperedges: tuple[Hyperedge, ...]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(a.atom_id for a in self.atoms)

    def atom_map(self) -> dict[str, Atom]:
        return {a.atom_id: a for a in self.atoms}

    def validate(self) -> None:
        ids = self.ids
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate atom ids")
        amap = self.atom_map()
        edge_ids = [e.edge_id for e in self.hyperedges]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("duplicate edge ids")
        for e in self.hyperedges:
            if not e.tails or not e.heads:
                raise ValueError("hyperedges require nonempty tails and heads")
            if any(x not in amap for x in (*e.tails, *e.heads)):
                raise ValueError("hyperedge references unknown atom")
            if e.weight < 0:
                raise ValueError("negative edge weight")
            e.normalized_head_weights()


def _gate(profile: Profile, revoked: frozenset[int]) -> Fraction:
    return Fraction(1, 1) if profile_live(profile, revoked) else Fraction(0, 1)


def navigation_matrix(
    ks: KnowledgeSpace,
    *,
    revoked: Iterable[int] = (),
    relation_weights: dict[str, Fraction] | None = None,
) -> list[list[Fraction]]:
    """Base-denominator, substochastic navigation.

    Structural outgoing mass is normalised before warrant gating. Revocation therefore
    removes exactly the dead path's share rather than redistributing it to surviving edges.
    Missing mass is implicit dissipation/restart mass.
    """
    ks.validate()
    relation_weights = relation_weights or {}
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    n = len(ids)
    out = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]

    denom: dict[str, Fraction] = {x: Fraction(0, 1) for x in ids}
    for e in ks.hyperedges:
        rw = relation_weights.get(e.relation_type, Fraction(1, 1))
        mass = e.weight * rw
        for tail in e.tails:
            denom[tail] += mass

    for e in ks.hyperedges:
        rw = relation_weights.get(e.relation_type, Fraction(1, 1))
        structural_mass = e.weight * rw
        edge_gate = _gate(e.profile, rv)
        tails_gate = min((_gate(amap[t].profile, rv) for t in e.tails), default=Fraction(0, 1))
        if edge_gate == 0 or tails_gate == 0:
            continue
        hweights = e.normalized_head_weights()
        for tail in e.tails:
            src_gate = _gate(amap[tail].profile, rv)
            if src_gate == 0 or denom[tail] == 0:
                continue
            edge_prob = structural_mass / denom[tail]
            for head, hw in zip(e.heads, hweights, strict=True):
                dst_gate = _gate(amap[head].profile, rv)
                out[idx[tail]][idx[head]] += src_gate * edge_gate * tails_gate * dst_gate * edge_prob * hw
    assert all(sum(row, Fraction(0, 1)) <= 1 for row in out)
    return out


def navigation_matrix_independent_prune(
    ks: KnowledgeSpace,
    *,
    revoked: Iterable[int] = (),
    relation_weights: dict[str, Fraction] | None = None,
) -> list[list[Fraction]]:
    """Independent implementation of exact-share pruning with original denominators."""
    ks.validate()
    relation_weights = relation_weights or {}
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    n = len(ids)
    out = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]
    structural: dict[str, list[tuple[Hyperedge, Fraction]]] = {x: [] for x in ids}
    for e in ks.hyperedges:
        m = e.weight * relation_weights.get(e.relation_type, Fraction(1, 1))
        for t in e.tails:
            structural[t].append((e, m))
    totals = {t: sum((m for _, m in rows), Fraction(0, 1)) for t, rows in structural.items()}
    live_atom = {x: profile_live(amap[x].profile, rv) for x in ids}
    live_edge = {e.edge_id: profile_live(e.profile, rv) and all(live_atom[t] for t in e.tails) for e in ks.hyperedges}
    for tail, rows in structural.items():
        if not live_atom[tail] or totals[tail] == 0:
            continue
        for e, m in rows:
            if not live_edge[e.edge_id]:
                continue
            for head, hw in zip(e.heads, e.normalized_head_weights(), strict=True):
                if live_atom[head]:
                    out[idx[tail]][idx[head]] += (m / totals[tail]) * hw
    return out


def navigation_matrix_bad_renormalize(
    ks: KnowledgeSpace,
    *,
    revoked: Iterable[int] = (),
) -> list[list[Fraction]]:
    """Planted bad implementation: redistributes dead-edge mass onto survivors."""
    ks.validate()
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    out = [[Fraction(0, 1) for _ in ids] for _ in ids]
    for tail in ids:
        if not profile_live(amap[tail].profile, rv):
            continue
        live_rows: list[Hyperedge] = []
        for e in ks.hyperedges:
            if tail not in e.tails:
                continue
            if profile_live(e.profile, rv) and all(profile_live(amap[t].profile, rv) for t in e.tails) and all(profile_live(amap[h].profile, rv) for h in e.heads):
                live_rows.append(e)
        total = sum((e.weight for e in live_rows), Fraction(0, 1))
        for e in live_rows:
            if total == 0:
                continue
            for head, hw in zip(e.heads, e.normalized_head_weights(), strict=True):
                if profile_live(amap[head].profile, rv):
                    out[idx[tail]][idx[head]] += (e.weight / total) * hw
    return out


def _transpose(m: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(col) for col in zip(*m, strict=True)]


def _solve_fraction(a: list[list[Fraction]], b: list[Fraction]) -> list[Fraction]:
    n = len(a)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b, strict=True)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot is None:
            raise CannotCheck("singular exact system")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [x / p for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            f = aug[r][col]
            if f:
                aug[r] = [x - f * y for x, y in zip(aug[r], aug[col], strict=True)]
    return [row[-1] for row in aug]


def restart_fixed_point(p: list[list[Fraction]], seed: list[Fraction], alpha: Fraction) -> list[Fraction]:
    if not (Fraction(0, 1) < alpha <= Fraction(1, 1)):
        raise ValueError("alpha must be in (0,1]")
    n = len(p)
    if len(seed) != n or sum(seed, Fraction(0, 1)) != 1 or any(x < 0 for x in seed):
        raise ValueError("seed must be a probability vector")
    pt = _transpose(p)
    a = [[Fraction(int(i == j), 1) - (1 - alpha) * pt[i][j] for j in range(n)] for i in range(n)]
    b = [alpha * x for x in seed]
    return _solve_fraction(a, b)


def restart_step(p: list[list[Fraction]], seed: list[Fraction], x: list[Fraction], alpha: Fraction) -> list[Fraction]:
    pt = _transpose(p)
    return [alpha * seed[i] + (1 - alpha) * sum((pt[i][j] * x[j] for j in range(len(x))), Fraction(0, 1)) for i in range(len(x))]


def l1(x: Sequence[Fraction]) -> Fraction:
    return sum((abs(v) for v in x), Fraction(0, 1))


def reaction_surprise(query: Fraction, background: Fraction, eps: float = 1e-12) -> float:
    q = float(query)
    b = float(background)
    if q <= 0:
        return 0.0
    return max(0.0, q * math.log((q + eps) / (b + eps)))


def enabled_hyperedges(ks: KnowledgeSpace, activation: dict[str, Fraction], threshold: Fraction, revoked: Iterable[int] = ()) -> tuple[str, ...]:
    rv = frozenset(revoked)
    amap = ks.atom_map()
    enabled: list[str] = []
    for e in ks.hyperedges:
        if not profile_live(e.profile, rv):
            continue
        if all(profile_live(amap[t].profile, rv) and activation.get(t, Fraction(0, 1)) >= threshold for t in e.tails):
            enabled.append(e.edge_id)
    return tuple(sorted(enabled))


Partition = tuple[tuple[int, ...], ...]


def is_lumpable(p: list[list[Fraction]], blocks: Partition) -> bool:
    universe = sorted(i for block in blocks for i in block)
    if universe != list(range(len(p))) or len(universe) != len(set(universe)):
        raise ValueError("blocks must partition all states")
    for block in blocks:
        for target in blocks:
            vals = {sum((p[i][j] for j in target), Fraction(0, 1)) for i in block}
            if len(vals) > 1:
                return False
    return True


def lump_matrix(p: list[list[Fraction]], blocks: Partition) -> list[list[Fraction]]:
    if not is_lumpable(p, blocks):
        raise ValueError("not lumpable")
    return [[sum((p[block[0]][j] for j in target), Fraction(0, 1)) for target in blocks] for block in blocks]


def pushforward(x: Sequence[Fraction], blocks: Partition) -> list[Fraction]:
    return [sum((x[i] for i in block), Fraction(0, 1)) for block in blocks]


def row_vector_step(x: Sequence[Fraction], p: list[list[Fraction]]) -> list[Fraction]:
    return [sum((x[i] * p[i][j] for i in range(len(x))), Fraction(0, 1)) for j in range(len(x))]


def semantically_connected(ks: KnowledgeSpace, atom_id: str, revoked: Iterable[int] = ()) -> bool:
    amap = ks.atom_map()
    atom = amap[atom_id]
    if atom.quarantined:
        return True
    rv = frozenset(revoked)
    if not profile_live(atom.profile, rv):
        return True
    for e in ks.hyperedges:
        if atom_id not in (*e.tails, *e.heads) or not profile_live(e.profile, rv):
            continue
        peers = set((*e.tails, *e.heads)) - {atom_id}
        if any(profile_live(amap[p].profile, rv) for p in peers):
            return True
    return False


def dependency_impact_cone(ks: KnowledgeSpace, changed: Iterable[str], dependency_types: frozenset[str]) -> frozenset[str]:
    impacted = set(changed)
    grew = True
    while grew:
        grew = False
        for e in ks.hyperedges:
            if e.relation_type not in dependency_types:
                continue
            if any(t in impacted for t in e.tails):
                for h in e.heads:
                    if h not in impacted:
                        impacted.add(h)
                        grew = True
    return frozenset(impacted)


def check_navigation_theorems() -> dict[str, int]:
    one = (frozenset(),)
    a = Atom("a", "claim", one)
    b = Atom("b", "claim", (frozenset({0}),))
    c = Atom("c", "claim", one)
    d = Atom("d", "claim", one)
    e1 = Hyperedge("ab", ("a",), ("b",), "support", Fraction(1, 1), profile=one)
    e2 = Hyperedge("ac", ("a",), ("c",), "support", Fraction(1, 1), profile=one)
    e3 = Hyperedge("bcd", ("b", "c"), ("d",), "compose", Fraction(1, 1), profile=one)
    ks = KnowledgeSpace((a, b, c, d), (e1, e2, e3))

    p0 = navigation_matrix(ks)
    p0b = navigation_matrix_independent_prune(ks)
    assert p0 == p0b
    p1 = navigation_matrix(ks, revoked={0})
    p1b = navigation_matrix_independent_prune(ks, revoked={0})
    assert p1 == p1b
    assert p1 != navigation_matrix_bad_renormalize(ks, revoked={0})

    seed = [Fraction(1, 1), Fraction(0), Fraction(0), Fraction(0)]
    alpha = Fraction(1, 3)
    fixed = restart_fixed_point(p0, seed, alpha)
    assert restart_step(p0, seed, fixed, alpha) == fixed

    rng = random.Random(20260904)
    contraction_checks = 0
    for _ in range(200):
        x = [Fraction(rng.randint(-5, 5), 7) for _ in range(4)]
        y = [Fraction(rng.randint(-5, 5), 7) for _ in range(4)]
        fx = restart_step(p0, seed, x, alpha)
        fy = restart_step(p0, seed, y, alpha)
        assert l1([u - v for u, v in zip(fx, fy, strict=True)]) <= (1 - alpha) * l1([u - v for u, v in zip(x, y, strict=True)])
        contraction_checks += 1

    activation = {"a": Fraction(1), "b": Fraction(1), "c": Fraction(1), "d": Fraction(0)}
    assert "bcd" in enabled_hyperedges(ks, activation, Fraction(1, 2))
    assert "bcd" not in enabled_hyperedges(ks, activation, Fraction(1, 2), revoked={0})
    assert reaction_surprise(Fraction(1, 3), Fraction(1, 3)) == 0.0
    assert reaction_surprise(Fraction(1, 2), Fraction(1, 10)) > 0.0
    return {"matrix_equalities": 2, "planted_renormalization_detected": 1, "fixed_point_checks": 1, "contraction_checks": contraction_checks, "firing_revocation_checks": 2}


def check_lumpability() -> dict[str, int]:
    p = [
        [Fraction(1, 2), Fraction(0), Fraction(1, 2), Fraction(0)],
        [Fraction(0), Fraction(1, 2), Fraction(0), Fraction(1, 2)],
        [Fraction(1, 4), Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)],
        [Fraction(1, 4), Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)],
    ]
    blocks: Partition = ((0, 1), (2, 3))
    assert is_lumpable(p, blocks)
    lp = lump_matrix(p, blocks)
    checks = 0
    for numerators in itertools.product(range(3), repeat=4):
        total = sum(numerators)
        if total == 0:
            continue
        x = [Fraction(v, total) for v in numerators]
        lhs = pushforward(row_vector_step(x, p), blocks)
        rhs = row_vector_step(pushforward(x, blocks), lp)
        assert lhs == rhs
        checks += 1
    bad = [row[:] for row in p]
    bad[1][0] += Fraction(1, 4)
    bad[1][3] -= Fraction(1, 4)
    assert not is_lumpable(bad, blocks)
    return {"pushforward_commutation_checks": checks, "nonlumpable_control": 1}


def check_connectivity_and_impact() -> dict[str, int]:
    one = (frozenset(),)
    atoms = (
        Atom("a", "claim", one),
        Atom("b", "claim", one),
        Atom("c", "procedure", one),
        Atom("q", "claim", one, quarantined=True),
        Atom("z", "claim", one),
    )
    edges = (
        Hyperedge("e1", ("a",), ("b",), "depends", profile=one),
        Hyperedge("e2", ("b",), ("c",), "depends", profile=one),
    )
    ks = KnowledgeSpace(atoms, edges)
    assert semantically_connected(ks, "a")
    assert semantically_connected(ks, "b")
    assert semantically_connected(ks, "c")
    assert semantically_connected(ks, "q")
    assert not semantically_connected(ks, "z")
    assert dependency_impact_cone(ks, {"a"}, frozenset({"depends"})) == frozenset({"a", "b", "c"})
    return {"connectivity_checks": 5, "impact_cone_checks": 1}


def run_all() -> dict[str, object]:
    result = {
        "contract": "KnowledgeSpace.v1-M0",
        "warrant_semiring": check_warrant_semiring(),
        "navigation": check_navigation_theorems(),
        "lumpability": check_lumpability(),
        "connectivity_rewrite": check_connectivity_and_impact(),
        "terminals": {
            "M0_FINITE_MATH_CORE": "GREEN",
            "GENERAL_NOVELTY": "NOT_ESTABLISHED",
            "M1_KSO_INSTANCE": "NOT_RUN",
            "M2_SOLVE_LOOP": "NOT_RUN",
            "M3_GAP_LEARNING": "NOT_RUN",
            "M4_JUMP_LOOP": "NOT_RUN",
            "M5_CHAT": "NOT_RUN",
            "M6_FRONTIER_MATH": "NOT_RUN",
        },
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_all()
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    if args.json or args.self_test:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
