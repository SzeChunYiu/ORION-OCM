"""Frozen world generators for D19 (provenance/revocation) and D20 (CEGAR).

Additive to exact/worlds.py (WORLDS_V1): this module NEVER regenerates an
existing world id and NEVER reuses an existing `_rng` key prefix. New keys are
"OW4N" (provenance worlds carrying negative dependencies) and "OW5S" (concrete
transition systems with a deliberately lossy partition). Sizes/seeds are fixed
by D19_D20_PROTOCOL_V1.json; everything here is deterministic and tiny enough
that every check downstream is exhaustive, never sampled.

Python 3.8 compatible (stdlib only).
"""
from __future__ import annotations

from exact.worlds import WORLDS_V1, _rng  # frozen SEED=20260910 substreams

# --------------------------------------------------------------- specs ----
WORLDS_D19_D20_V1 = {
    "OW4N": {
        "n_worlds": 8, "nodes": (4, 7), "min_blockers_per_world": 1,
        "justify": "OW4 skeleton plus controlled NEGATIVE dependencies "
                   "(blockers). Blockers, like premises, only reference "
                   "lower-index nodes, so negation is stratified and the "
                   "well-founded model is unique and computable in one "
                   "topological pass. Tiny so every revocation subset is "
                   "enumerable and ground truth is recomputation, not algebra.",
    },
    "OW5S": {
        "n_grid": (8, 12, 16, 20, 24), "n_worlds_per_n": 6,
        "succ": (1, 2), "k_rule": "max(2, n // 4)",
        "partition_rule": "interleaved s mod k (deliberately lossy: mixes "
                          "reachable with unreachable states by construction)",
        "bad_rule": "wi even -> Bad drawn from UNREACHABLE states (concrete "
                    "verdict SAFE, every abstract counterexample is spurious); "
                    "wi odd -> Bad contains >=1 REACHABLE state (concrete "
                    "verdict UNSAFE). Stratified so both CEGAR branches are "
                    "exercised; degenerate worlds are flagged, never silently "
                    "reshaped.",
        "justify": "finite transition systems small enough that concrete BFS "
                   "is exhaustive ground truth at every n in the grid.",
    },
}


# ----------------------------------------------------------- OW4N ----
def ow4n_worlds() -> list:
    """OW4 skeleton + stratified negative dependencies.

    Edge = {id, premises, blockers, conclusion}. Semantics (ground truth):
    node n is supported iff it is a live source, or some incoming edge has
    every premise supported and NO blocker supported. Premises and blockers
    both index strictly below the conclusion, so one topological pass decides
    every node: no fixpoint iteration, no stratification ambiguity.
    """
    spec = WORLDS_D19_D20_V1["OW4N"]
    base = WORLDS_V1["OW4"]
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW4N", wi)
        n = rng.randint(*base["nodes"])
        names = ["g%d" % i for i in range(n)]
        edges, eid = [], 0
        for j in range(1, n):
            nedge = 2 if j >= n // 2 and rng.random() < 0.6 else rng.randint(0, 1)
            for _ in range(nedge):
                k = rng.randint(1, min(j, 2))
                premises = rng.sample(range(j), k)
                edges.append({"id": "s%d" % eid,
                              "premises": [names[p] for p in premises],
                              "blockers": [], "conclusion": names[j]})
                eid += 1
        # plant blockers: each candidate edge may gain exactly one blocker
        # drawn from strictly-lower-index nodes not already among its premises.
        planted = 0
        for e in edges:
            j = names.index(e["conclusion"])
            pool = [names[p] for p in range(j) if names[p] not in e["premises"]]
            if pool and rng.random() < 0.45:
                e["blockers"] = [rng.choice(sorted(pool))]
                planted += 1
        if planted < spec["min_blockers_per_world"]:
            # deterministic fallback: give the last eligible edge one blocker
            for e in reversed(edges):
                j = names.index(e["conclusion"])
                pool = [names[p] for p in range(j) if names[p] not in e["premises"]]
                if pool:
                    e["blockers"] = [sorted(pool)[0]]
                    planted += 1
                    break
        incoming = {nm: [] for nm in names}
        for e in edges:
            incoming[e["conclusion"]].append(e)
        sources = [nm for nm in names if not incoming[nm]]
        out.append({"id": "OW4N-%02d" % wi, "nodes": names, "edges": edges,
                    "sources": sources, "root": names[-1],
                    "n_blockers": planted})
    return out


def ow4_with_blocker_field() -> list:
    """The frozen OW4 worlds, each edge given an explicit empty blocker list.

    This is the CLEAN CONTROL population for every D19 negation check: same
    engine, same code path, provably zero negative dependencies.
    """
    from exact.worlds import ow4_worlds
    out = []
    for w in ow4_worlds():
        edges = [dict(e, blockers=[]) for e in w["edges"]]
        incoming = {nm: [] for nm in w["nodes"]}
        for e in edges:
            incoming[e["conclusion"]].append(e)
        out.append({"id": w["id"], "nodes": list(w["nodes"]), "edges": edges,
                    "sources": [nm for nm in w["nodes"] if not incoming[nm]],
                    "root": w["root"], "n_blockers": 0,
                    "legacy_leaves": list(w["leaves"])})
    return out


# ----------------------------------------------------------- OW5S ----
def ow5s_worlds(n_grid=None) -> list:
    """Concrete finite transition systems + deliberately lossy partitions."""
    spec = WORLDS_D19_D20_V1["OW5S"]
    grid = tuple(n_grid) if n_grid is not None else spec["n_grid"]
    out = []
    for n in grid:
        for wi in range(spec["n_worlds_per_n"]):
            rng = _rng("OW5S", n, wi)
            states = list(range(n))
            trans = {}
            for s in states:
                deg = rng.randint(*spec["succ"])
                trans[s] = sorted(rng.sample(range(n), deg))
            s0 = 0
            # concrete reachability (exhaustive; ground truth for Bad placement)
            seen, stack = {s0}, [s0]
            while stack:
                s = stack.pop()
                for t in trans[s]:
                    if t not in seen:
                        seen.add(t)
                        stack.append(t)
            reach = sorted(seen)
            unreach = sorted(set(states) - seen)
            n_bad = max(1, n // 8)
            degenerate = None
            if wi % 2 == 0:
                if len(unreach) >= n_bad:
                    bad = sorted(rng.sample(unreach, n_bad))
                else:
                    bad = sorted(rng.sample([s for s in reach if s != s0],
                                            min(n_bad, max(1, len(reach) - 1))))
                    degenerate = "DEGENERATE_NO_UNREACHABLE__FELL_BACK_TO_REACHABLE_BAD"
            else:
                pool = [s for s in reach if s != s0]
                if pool:
                    bad = sorted(rng.sample(pool, min(n_bad, len(pool))))
                else:
                    bad = [s0]
                    degenerate = "DEGENERATE_ONLY_INITIAL_REACHABLE"
            k = max(2, n // 4)
            blocks = []
            for r in range(k):
                b = tuple(s for s in states if s % k == r)
                if b:
                    blocks.append(b)
            out.append({"id": "OW5S-n%02d-%02d" % (n, wi), "n": n,
                        "states": states, "trans": trans, "init": s0,
                        "bad": bad, "start_blocks": blocks, "k": len(blocks),
                        "concrete_reachable": reach,
                        "concrete_unsafe": bool(set(bad) & seen),
                        "degenerate": degenerate})
    return out


WORLD_SETS_D19_D20 = {"OW4N": ow4n_worlds, "OW5S": ow5s_worlds}
