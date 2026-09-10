"""Frozen tiny-world generators (WORLDS_V1). Seeded, sizes fixed, deterministic.

Every world family is tiny-exhaustive: small enough that brute-force
enumeration of all derivations/pairs/models is exact and total, so oracles
and cross-checks never sample -- they exhaust. That is the whole point of
the D17/D17 licence (P2 finite certificates, not universal proofs).
"""
from __future__ import annotations
import random
from fractions import Fraction

SEED = 20260910  # freeze date; single global seed, per-family substreams

WORLDS_V1 = {
    "OW1": {"n_worlds": 12, "nodes": (3, 8), "acyclic": 10, "cyclic": 2,
            "justify": "parsing/proof/planning-isomorphic deduction hypergraphs; tiny-exhaustive so every derivation tree is enumerable and semiring DP is cross-checkable by brute force"},
    "OW2": {"n_worlds": 8, "states": (2, 4), "actions": (2, 4),
            "justify": "ambiguity/safe-action sets; tiny so the intersection criterion is decidable by exhaustion"},
    "OW3": {"n_worlds": 10, "elems": (3, 5),
            "justify": "round-trip I/R/J relation triples with protected values; tiny so composition can be checked pair-by-pair"},
    "OW4": {"n_worlds": 8, "nodes": (4, 7),
            "justify": "provenance hypergraphs with alternative supports; tiny so revocation can be recomputed from scratch exactly"},
    "OW5": {"n_worlds": 8, "universe": 8,
            "justify": "partitions of an 8-element universe; refinement chains short enough to enumerate all strict splits"},
    "OW6": {"n_worlds": 10, "depth": (2, 4),
            "justify": "expression families with independently evaluated arithmetic semantics; tiny so e-class members can each be ground-truth evaluated"},
    "OW7": {"n_worlds": 6, "vars": 2,
            "justify": "finite logics with fully enumerated model sets; tiny so the institution satisfaction condition is checkable on every (model, sentence) pair"},
}

def _rng(*key: int) -> random.Random:
    return random.Random(f"{SEED}:{'/'.join(map(str, key))}")

def _frac(rng: random.Random, lo: int, hi: int) -> Fraction:
    return Fraction(rng.randint(lo, hi), rng.randint(hi, hi * 2))

# ---------------------------------------------------------------- OW1 ----
def ow1_worlds() -> list[dict]:
    """Oblligation hypergraphs. Layered so acyclic worlds stay acyclic by
    construction; node validity is a frozen assignment; clean-world edges are
    sound by construction (premises-all-valid => conclusion-valid)."""
    spec = WORLDS_V1["OW1"]
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW1", wi)
        n = rng.randint(*spec["nodes"])
        names = [f"w{wi}n{i}" for i in range(n)]
        valid = {nm: rng.random() < 0.55 for nm in names}
        # force a couple of valid axioms (no premises) so derivations exist
        for nm in names[: max(1, n // 3)]:
            valid[nm] = True
        edges, eid = [], 0
        cyclic = wi >= spec["acyclic"]
        for j in range(1, n):
            for _ in range(rng.randint(0, 2)):
                k = rng.randint(1, min(j, 3))
                if cyclic and rng.random() < 0.35:
                    premises = [rng.randrange(n) for _ in range(k)]  # may go back
                else:
                    premises = rng.sample(range(j), k)
                concl = j
                # keep clean edges sound: if all premises valid, conclusion valid
                if not cyclic and all(valid[names[p]] for p in premises):
                    valid[names[concl]] = True
                edges.append({"id": f"e{eid}", "premises": [names[p] for p in premises],
                              "conclusion": names[concl],
                              "viterbi_w": _frac(rng, 3, 10),
                              "tropical_w": Fraction(rng.randint(1, 9), 1)})
                eid += 1
        out.append({"id": f"OW1-{wi:02d}", "nodes": names, "valid": valid,
                    "axioms": [nm for nm in names if valid[nm]],
                    "edges": edges, "cyclic": cyclic})
    return out

def ow1_unsound_variant(world: dict, rng_key=(777,)) -> dict:
    """H-T65a arm: flip exactly one clean edge to unsound (premises all valid,
    conclusion invalid). Returns modified copy + the corrupted edge id."""
    import copy
    rng = _rng(*rng_key)
    w = copy.deepcopy(world)
    cand = [e for e in w["edges"]
            if all(w["valid"][p] for p in e["premises"]) and len(e["premises"]) >= 1]
    if not cand:
        return w, None
    e = rng.choice(sorted(cand, key=lambda e: e["id"]))
    w["valid"][e["conclusion"]] = False  # breaks soundness of this rule
    return w, e["id"]

# ---------------------------------------------------------------- OW2 ----
def ow2_worlds() -> list[dict]:
    """Ambiguity + safe-action sets: possible states S, declared safe sets G(s)."""
    spec = WORLDS_V1["OW2"]
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW2", wi)
        ns, na = rng.randint(*spec["states"]), rng.randint(*spec["actions"])
        states = [f"s{i}" for i in range(ns)]
        actions = [f"a{j}" for j in range(na)]
        safe = {s: sorted(rng.sample(actions, rng.randint(1, na))) for s in states}
        if wi % 3 == 0:  # guarantee a nonempty intersection family sometimes
            safe[states[0]] = sorted(set(safe[states[0]]) | {actions[0]})
            for s in states[1:]:
                safe[s] = sorted(set(safe[s]) | {actions[0]})
        out.append({"id": f"OW2-{wi:02d}", "states": states, "actions": actions, "safe": safe})
    return out

# ---------------------------------------------------------------- OW3 ----
def ow3_worlds() -> list[dict]:
    """Round-trip triples: elements with protected values pv in {0,1,2};
    relations R1:A<->B, R2:B<->D pairs; J(y) reverse-read sets (clean coverage)."""
    spec = WORLDS_V1["OW3"]
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW3", wi)
        na, nb, nd = (rng.randint(*spec["elems"]) for _ in range(3))
        A = [f"a{i}" for i in range(na)]; B = [f"b{i}" for i in range(nb)]
        D = [f"d{i}" for i in range(nd)]
        pv = {x: rng.randrange(3) for x in A + B + D}
        # injective relations so every related pair can preserve pv consistently
        used_b, R1 = set(), []
        for x in sorted(A):
            if rng.random() < 0.8:
                free = [b for b in sorted(B) if b not in used_b]
                if free:
                    b = rng.choice(free); used_b.add(b); R1.append((x, b))
        used_d, R2 = set(), []
        for y in sorted(B):
            if rng.random() < 0.8:
                free = [d for d in sorted(D) if d not in used_d]
                if free:
                    d = rng.choice(free); used_d.add(d); R2.append((y, d))
        for x, y in R1:  # clean worlds: every related pair preserves pv
            pv[y] = pv[x]
        for y, z in R2:
            pv[z] = pv[y]
        J = {y: [x for x in A if (x, y) in R1] for y in B}  # reverse-read
        out.append({"id": f"OW3-{wi:02d}", "A": A, "B": B, "D": D, "pv": pv,
                    "R1": sorted(R1), "R2": sorted(R2), "J": J})
    return out

# ---------------------------------------------------------------- OW4 ----
def ow4_worlds() -> list[dict]:
    """Provenance hypergraphs: layered DAGs with leaf evidence variables and
    at least one node carrying TWO independent supports (alternative supports)."""
    spec = WORLDS_V1["OW4"]
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW4", wi)
        n = rng.randint(*spec["nodes"])
        names = [f"g{i}" for i in range(n)]
        edges, eid = [], 0
        for j in range(1, n):
            nedge = 2 if j >= n // 2 and rng.random() < 0.6 else rng.randint(0, 1)
            for _ in range(nedge):
                k = rng.randint(1, min(j, 2))
                premises = rng.sample(range(j), k)
                edges.append({"id": f"s{eid}", "premises": [names[p] for p in premises],
                              "conclusion": names[j]}); eid += 1
        leaves = sorted({e["premises"][0] for e in edges} | {names[0]})
        out.append({"id": f"OW4-{wi:02d}", "nodes": names, "edges": edges,
                    "leaves": leaves, "root": names[-1]})
    return out

# ---------------------------------------------------------------- OW5 ----
def ow5_worlds() -> list[dict]:
    """Partitions of an 8-element universe + strict refinement chains."""
    spec = WORLDS_V1["OW5"]
    U = list(range(spec["universe"]))
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW5", wi)
        k0 = rng.randint(1, 3)
        cut = sorted(rng.sample(range(1, len(U)), k0))
        blocks, prev = [], 0
        for c in cut + [len(U)]:
            blocks.append(tuple(range(prev, c))); prev = c
        out.append({"id": f"OW5-{wi:02d}", "universe": U, "start": blocks})
    return out

# ---------------------------------------------------------------- OW6 ----
_EXPR_OPS = ["+", "*"]
def expr_eval(t, x_val):
    """Independent ground-truth evaluator (no sharing with rewrite engine)."""
    if isinstance(t, tuple):
        op, l, r = t
        return expr_eval(l, x_val) + expr_eval(r, x_val) if op == "+" \
            else expr_eval(l, x_val) * expr_eval(r, x_val)
    return {"x": x_val, "2": 2, "3": 3, "5": 5}[t]

def ow6_worlds() -> list[dict]:
    """Expression families: ASTs over {2,3,5,x,+,*}; sound rewrites + 1 planted
    unsound rewrite id kept separate for the hostile arm."""
    spec = WORLDS_V1["OW6"]
    def gen(rng, depth):
        if depth == 0 or rng.random() < 0.3:
            return rng.choice(["2", "3", "5", "x"])
        return (rng.choice(_EXPR_OPS), gen(rng, depth - 1), gen(rng, depth - 1))
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW6", wi)
        out.append({"id": f"OW6-{wi:02d}",
                    "expr": gen(rng, rng.randint(*spec["depth"]))})
    return out

REWRITE_NAMES = ["comm+", "comm*", "assoc+"]
# distrib intentionally EXCLUDED: comm* x distrib is non-terminating on
# unbounded exprs (e-graph would grow forever); tiny worlds stay finite
# under the AC-style set above, so saturation reaches a real fixpoint.

def rewrite_apply(t, name):
    """Apply rewrite `name` at every node; returns new tree or None."""
    if not isinstance(t, tuple):
        return None
    op, l, r = t
    if name == "comm+" and op == "+":
        return (op, r, l)
    if name == "comm*" and op == "*":
        return (op, r, l)
    if name == "assoc+" and op == "+":
        if isinstance(l, tuple) and l[0] == "+":
            return ("+", l[1], ("+", l[2], r))
        return None
    if name == "distrib" and op == "*":
        if isinstance(r, tuple) and r[0] == "+":
            return ("+", ("*", l, r[1]), ("*", l, r[2]))
        return None
    if name == "unsound_swap" and op == "+":   # PLANTED UNSOUND (H-T86a)
        return ("*", l, r)
    return None

# ---------------------------------------------------------------- OW7 ----
def ow7_worlds() -> list[dict]:
    """Finite heterogeneous logics. Source I: prop. sentences over {p,q} with
    fully enumerated valuation models. Target J: same signature, own model set.
    Comorphism: alpha sentence translation (p->p', q->p'&q'), beta reduct maps
    J-models to I-models by dropping the extra coordinate."""
    spec = WORLDS_V1["OW7"]
    out = []
    for wi in range(spec["n_worlds"]):
        rng = _rng("OW7", wi)
        imodels = [(p, q) for p in (0, 1) for q in (0, 1)]
        # J models: (p', q', extra) with beta((p',q',e)) = (p', q')
        jmodels = [(p, q, e) for p in (0, 1) for q in (0, 1) for e in (0, 1)]
        if rng.random() < 0.5:
            jmodels.remove((0, 0, 1))
        out.append({"id": f"OW7-{wi:02d}", "imodels": imodels, "jmodels": jmodels})
    return out

WORLD_SETS = {"OW1": ow1_worlds, "OW2": ow2_worlds, "OW3": ow3_worlds,
              "OW4": ow4_worlds, "OW5": ow5_worlds, "OW6": ow6_worlds,
              "OW7": ow7_worlds}

def all_worlds() -> dict:
    return {k: v() for k, v in sorted(WORLD_SETS.items())}
