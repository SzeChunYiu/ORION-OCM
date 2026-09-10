"""DEV-CAL-1 frozen world families (#323 sec 5; DEV_CAL_1_PROTOCOL_FREEZE_V1).

2x2 relatedness design: cells A/B/C/D = {surface_same,surface_different} x
{latent_same,latent_different}.  30 worlds/cell, 3 seeds each (frozen).

World model (tiny, symbolic, exact, stdlib-only; consistent with the D19-D21
machinery and reusing the D26 frozen typed-operator vocabulary):

  A decomposition DAG over typed operators (DISTINGUISH/REFINE/REDUCE/
  VERIFY/TRANSPORT): node j consumes CHILD nodes with smaller indices; LEAF
  nodes (no children) read the world's bound input token; the ROOT is the
  unique node no other node consumes.  Executing a DAG on a world binding
  (root_slot) yields a value; a method (dag, root_slot) SOLVES the world iff
  its value equals the world goal.

  A LATENT CLASS is such a DAG, size 3-4, depth <= 4.  A WORLD is
  constructed so the class shape solves it AND (verified exhaustively at
  construction) NO strictly smaller method solves it: the class shape is a
  MINIMAL decomposition.  Surface = presentation signature (predicate names,
  arity profile, typed-literal statistics); reminting = fresh names +
  independent arity profile.

CLASS SEPARATION: latent classes are pairwise UNRELATED under the full frozen
structural relation (no isomorphic root-anchored DAG modulo relabeling, no
equal typed-operator support multiset, no homomorphism), so latent_different
cells are structurally different BY CONSTRUCTION; the fail-closed checker in
devcal1_certificates re-verifies every emitted world.

Seeded from the frozen WORLDS_V1 SEED=20260910 substreams (new prefix "DC1").
Deterministic.  Python 3.8+ stdlib only.
"""
from __future__ import annotations

import itertools
import random
from collections import Counter
from fractions import Fraction

from exact.worlds import _rng  # frozen SEED substreams

OPERATOR_TYPES = ("DISTINGUISH", "REFINE", "REDUCE", "VERIFY", "TRANSPORT")
TOKEN_TYPES = ("REL", "ATTR", "QUANT", "STRUCT")

OP_INPUT_CONTRACT = {
    "DISTINGUISH": ("STRUCT",),
    "REFINE": ("ATTR", "STRUCT"),
    "REDUCE": ("REL",),
    "VERIFY": ("QUANT", "REL", "ATTR"),
    "TRANSPORT": ("REL", "ATTR", "STRUCT"),
}
OP_SEMANTICS = {"VERIFY": lambda b: b + 1, "REFINE": lambda b: b * 2,
                "REDUCE": lambda b: b + 2, "DISTINGUISH": lambda b: b + 3,
                "TRANSPORT": lambda b: b + 5}

WORLDS_DC1_V1 = {
    "cells": ("A", "B", "C", "D"),
    "worlds_per_cell": 30,
    "seeds_per_world": 3,
    "n_latent_classes": 10,
    "decomposition_size": (3, 4),
    "arity_profile": (1, 3),
    "token_value_range": (1, 49),
    "minimality_rule": "a latent class is admissible only if some (token "
                       "type, value) exists on which NO strictly smaller dag "
                       "reproduces the class value (same-token clean pair); "
                       "world inputs are then drawn avoiding every value on "
                       "which any smaller dag binding any world token "
                       "reaches the goal (exhaustively re-verified); "
                       "latent_different cells additionally exclude source "
                       "classes that would solve the target world "
                       "(cross-solve exclusion)",
    "justify": "each world pair (source,target) crosses surface similarity "
               "against latent structural similarity; cell B (surface "
               "reminted, latent same) is the only cell in which structural, "
               "non-surface headroom can appear",
}

VALUE_LO, VALUE_HI = WORLDS_DC1_V1["token_value_range"]

# ------------------------------------------------------------ dag helpers ---
def dag_root(shape):
    """Root = the unique node no other node consumes; None if not unique."""
    consumed = set()
    for _, ch in shape:
        consumed.update(ch)
    unconsumed = [j for j in range(len(shape)) if j not in consumed]
    return unconsumed[0] if len(unconsumed) == 1 else None

def dag_connected(shape):
    """Connected iff root is unique and every node is consumed by it
    transitively (equivalently: exactly one unconsumed node exists)."""
    return dag_root(shape) is not None

def dag_depth(shape):
    root = dag_root(shape)
    if root is None:
        return None
    def dep(j):
        _, ch = shape[j]
        return 1 + max(dep(c) for c in ch) if ch else 1
    return dep(root)

def execute_dag(shape, token_type, token_value):
    """Ground-truth execution (one of three independent implementations).
    Leaves read the bound token; type violations return None."""
    root = dag_root(shape)
    if root is None:
        return None
    vals = {}
    for j in range(len(shape)):  # children < j: forward pass is topological
        op, ch = shape[j]
        if not ch:
            if token_type not in OP_INPUT_CONTRACT[op]:
                return None
            vals[j] = OP_SEMANTICS[op](token_value)
        else:
            vals[j] = OP_SEMANTICS[op](max(vals[c] for c in ch))
    return vals[root]

# ------------------------------------------------------ pairwise separation --
def _support_multiset(shape):
    return Counter(op for op, _ in shape)

def _homomorphism_exists(shape_s, shape_t):
    """Root-anchored, label-preserving homomorphism (same relation as
    certificates.cert_c, local copy so generation never imports the checker
    mid-init)."""
    rs, rt = dag_root(shape_s), dag_root(shape_t)
    if rs is None or rt is None:
        return False
    if shape_s[rs][0] != shape_t[rt][0]:
        return False
    ns, nt = len(shape_s), len(shape_t)
    for assign in itertools.product(range(nt), repeat=ns):
        if assign[rs] != rt:
            continue
        ok = True
        for j in range(ns):
            op_s, ch_s = shape_s[j]
            op_t, ch_t = shape_t[assign[j]]
            if op_s != op_t or any(assign[c] not in ch_t for c in ch_s):
                ok = False
                break
        if ok:
            return True
    return False

def _related(shape_a, shape_b):
    if not (dag_connected(shape_a) and dag_connected(shape_b)):
        return True  # malformed: never accept at generation
    if _support_multiset(shape_a) == _support_multiset(shape_b):
        return True
    return _homomorphism_exists(shape_a, shape_b) or \
        _homomorphism_exists(shape_b, shape_a)

def gen_latent_shapes(n_classes):
    rng = _rng("DC1", "shapes")
    shapes = []
    tries = 0
    while len(shapes) < n_classes and tries < 200000:
        tries += 1
        n = rng.randint(*WORLDS_DC1_V1["decomposition_size"])
        nodes = []
        for j in range(n):
            op = rng.choice(OPERATOR_TYPES)
            if j == 0:
                nodes.append((op, ()))  # node 0 can only be a leaf
                continue
            leaf = rng.random() < 0.35
            if leaf:
                nodes.append((op, ()))
            elif op == "DISTINGUISH":
                if j < 2:
                    nodes = None
                    break
                nodes.append((op, tuple(sorted(rng.sample(range(j), 2)))))
            else:
                nodes.append((op, (rng.randrange(j),)))
        if nodes is None:
            continue
        shape = tuple(nodes)
        if not dag_connected(shape):
            continue
        if (dag_depth(shape) or 0) > 4:
            continue
        if any(_related(shape, s) for s in shapes):
            continue
        if not _class_admissible(shape):
            continue
        shapes.append(shape)
    if len(shapes) < n_classes:
        raise SystemExit("DC1 shape generation underflow: %d" % len(shapes))
    return shapes

# LATENT_SHAPES is generated at the bottom of this module (after all
# helper definitions it depends on).

# -------------------------------------------------------------- surface sig --
def fresh_predicate_names(rng, n):
    names, used = [], set()
    while len(names) < n:
        nm = "P" + "".join(rng.choice("abcdefghijklmnopqrstuvwxyz")
                           for _ in range(4)) + str(rng.randint(10, 99))
        if nm not in used:
            used.add(nm)
            names.append(nm)
    return names

def surface_signature_of(predicates, inputs):
    """Frozen surface signature: predicate names, arity profile, typed-literal
    statistics.  Task CONTENT (input values, goal) is NOT surface."""
    return {
        "predicate_names": tuple(sorted(p[0] for p in predicates)),
        "arity_profile": tuple(sorted(a for _, a in predicates)),
        "literal_type_histogram": tuple(sorted(
            Counter(t["type"] for t in inputs).items())),
        "n_input_literals": len(inputs),
    }

# ----------------------------------------------------------- instantiation --
def _all_dags_upto(size):
    """All connected dags with <= size operator nodes (shared frozen pool:
    construction-time minimality oracle AND the search candidate space).
    Children earlier; any node may be a leaf."""
    out = []
    for n in range(1, size + 1):
        def rec(j, nodes):
            if j == n:
                shp = tuple(nodes)
                if dag_connected(shp):
                    out.append(shp)
                return
            for op in OPERATOR_TYPES:
                nodes.append((op, ()))
                rec(j + 1, nodes)
                nodes.pop()
                if op == "DISTINGUISH":
                    if j >= 2:
                        for ch in itertools.combinations(range(j), 2):
                            nodes.append((op, tuple(sorted(ch))))
                            rec(j + 1, nodes)
                            nodes.pop()
                else:
                    for c in range(j):
                        nodes.append((op, (c,)))
                        rec(j + 1, nodes)
                        nodes.pop()
        for op0 in OPERATOR_TYPES:
            if n == 1:
                out.append(((op0, ()),))
                continue
            rec(1, [(op0, ())])
    return out

_SMALL_DAGS = {}  # size -> list, lazy

def _smaller_dags(size):
    if size - 1 not in _SMALL_DAGS:
        _SMALL_DAGS[size - 1] = _all_dags_upto(size - 1)
    return _SMALL_DAGS[size - 1]

def has_smaller_solver(shape, inputs, root_slot, goal):
    """Exhaustive: does any strictly smaller method reach the goal?
    A smaller method may bind ANY of the world's tokens: check every
    distinct (type, value) token present in the inputs."""
    smaller = _smaller_dags(len(shape))
    tokens = {(t["type"], t["value"]) for t in inputs}
    for tok in tokens:
        for shp in smaller:
            if execute_dag(shp, *tok) == goal:
                return True
    return False

# --------------------------------------------- minimality admissibility ------
def _acceptable_types(shape):
    """Token types accepted by EVERY leaf operator (leaves share the token)."""
    leaf_ops = [op for op, ch in shape if not ch]
    inter = set(OP_INPUT_CONTRACT[leaf_ops[0]])
    for op in leaf_ops[1:]:
        inter &= set(OP_INPUT_CONTRACT[op])
    return sorted(inter)

def _leaves_accept(shape, token_type):
    return all(token_type in OP_INPUT_CONTRACT[op] for op, ch in shape
               if not ch)

_CLEAN_TV_CACHE = {}

def clean_token_pairs(shape):
    """(type, value) pairs on which the class value is NOT reproduced by any
    strictly smaller dag binding that same token.  A class with no clean pair
    can never anchor a minimal world (its value function collides with a
    smaller dag for every token) and is inadmissible.  Memoized per shape."""
    if shape in _CLEAN_TV_CACHE:
        return _CLEAN_TV_CACHE[shape]
    smaller = _smaller_dags(len(shape))
    out = []
    for t in _acceptable_types(shape):
        for v in range(VALUE_LO, VALUE_HI + 1):
            goal = execute_dag(shape, t, v)
            if goal is None:
                continue
            if any(_leaves_accept(sp, t) and execute_dag(sp, t, v) == goal
                   for sp in smaller):
                continue
            out.append((t, v))
    _CLEAN_TV_CACHE[shape] = out
    return out

_FORBIDDEN_CACHE = {}

def forbidden_values(size, goal, token_type):
    """Token values on which SOME dag of size < `size` (leaf-accepted on
    `token_type`) reaches `goal` -- values a world input of that type must
    avoid.  Memoized by (size, goal, type)."""
    key = (size, goal, token_type)
    if key in _FORBIDDEN_CACHE:
        return _FORBIDDEN_CACHE[key]
    smaller = _smaller_dags(size)
    bad = set()
    for v in range(VALUE_LO, VALUE_HI + 1):
        if any(_leaves_accept(sp, token_type) and
               execute_dag(sp, token_type, v) == goal for sp in smaller):
            bad.add(v)
    _FORBIDDEN_CACHE[key] = bad
    return bad

def _class_admissible(shape):
    """Generation gate: acceptable types exist AND a same-token-clean pair
    exists (necessary for the class to anchor ANY minimal world)."""
    return bool(_acceptable_types(shape)) and bool(clean_token_pairs(shape))

def cross_solves(shape, world):
    """Does `shape` solve `world` on ANY of its input tokens?  Used to keep
    latent_different source classes from functionally solving the target."""
    for tok in world["inputs"]:
        val = execute_dag(shape, tok["type"], tok["value"])
        if val is not None and val == world["goal"]:
            return True
    return False

def instantiate(shape_idx, surface_names, seed_key, forced_types=None,
                forced_predicates=None):
    """Instantiate latent class `shape_idx` presented with `surface_names`.

    The class-anchoring token is drawn from the class's same-token-clean
    (type, value) pairs (no strictly smaller dag reproduces the class value
    on that token); every other input avoids all values on which a smaller
    dag binding a token of that type would reach the goal.  A final
    exhaustive assert re-checks the whole world (any token, any smaller
    dag).  Fail-closed SystemExit if a clean world cannot be built."""
    rng = _rng("DC1", "inst", shape_idx, *seed_key)
    shape = LATENT_SHAPES[shape_idx]
    clean = clean_token_pairs(shape)
    if not clean:
        raise SystemExit("DC1 inadmissible class reached instantiate: %d"
                         % shape_idx)
    for attempt in range(500):
        if forced_types is None:
            n_slots = rng.randint(3, 6)
            i0 = rng.randrange(n_slots)
            t0, v0 = rng.choice(clean)
            types = [rng.choice(TOKEN_TYPES) for _ in range(n_slots)]
            types[i0] = t0
        else:
            n_slots = len(forced_types)
            by_type = {}
            for t, v in clean:
                by_type.setdefault(t, []).append(v)
            slots_ok = [i for i, t in enumerate(forced_types) if t in by_type]
            if not slots_ok:
                raise SystemExit("DC1 forced types admit no clean pair: %d"
                                 % shape_idx)
            i0 = rng.choice(slots_ok)
            t0 = forced_types[i0]
            v0 = rng.choice(by_type[t0])
            types = list(forced_types)
        goal = execute_dag(shape, t0, v0)
        inputs = []
        ok = True
        for i in range(n_slots):
            if i == i0:
                inputs.append({"slot": i, "type": t0, "value": v0})
                continue
            bad = forbidden_values(len(shape), goal, types[i])
            choices = [v for v in range(VALUE_LO, VALUE_HI + 1)
                       if v not in bad]
            if not choices:
                ok = False
                break
            inputs.append({"slot": i, "type": types[i],
                           "value": rng.choice(choices)})
        if not ok:
            continue
        if not has_smaller_solver(shape, inputs, i0, goal):
            break
    else:
        raise SystemExit("DC1 minimality construction failed: shape %d"
                         % shape_idx)
    if forced_predicates is not None:
        predicates = list(forced_predicates)
    else:
        arities = [rng.randint(*WORLDS_DC1_V1["arity_profile"])
                   for _ in surface_names]
        predicates = [(nm, ar) for nm, ar in zip(surface_names, arities)]
    return {
        "shape_idx": shape_idx, "shape": shape,
        "inputs": inputs, "root_slot": i0, "goal": goal,
        "predicates": predicates,
        "minimality_redraws": attempt,
    }

def surface_of(world):
    return surface_signature_of(world["predicates"], world["inputs"])

# ------------------------------------------------------------ cell builder --
def _class_fits_forced(shape, forced_types):
    """A class can share the target's surface type multiset iff it has a
    same-token-clean (type, value) pair on one of the forced types (it must
    anchor a minimal world on those types)."""
    forced = set(forced_types)
    return any(t in forced for t, _ in clean_token_pairs(shape))

def build_cell(cell, world_index):
    """A: same class, SAME surface.  B: same class, REMINTED surface.
       C: different classes, SAME surface.  D: different classes, reminted."""
    spec = WORLDS_DC1_V1
    rng = _rng("DC1", cell, world_index)
    shape_t = world_index % spec["n_latent_classes"]
    if cell in ("A", "B"):
        shape_s = shape_t
    else:
        n_pred_t = rng.randint(2, 4)
        names_t = fresh_predicate_names(rng, n_pred_t)
        target = instantiate(shape_t, names_t, ("T", cell, world_index))
        forced_types = [t["type"] for t in target["inputs"]]
        eligible = [i for i, s in enumerate(LATENT_SHAPES)
                    if i != shape_t and _class_fits_forced(s, forced_types)
                    and not cross_solves(s, target)]
        if not eligible:
            raise SystemExit("no eligible distinct source class for "
                             "%s-%02d" % (cell, world_index))
        shape_s = eligible[rng.randrange(len(eligible))]
        return _finish_cell(cell, world_index, shape_t, shape_s,
                            target, names_t, rng)

    n_pred_t = rng.randint(2, 4)
    names_t = fresh_predicate_names(rng, n_pred_t)
    target = instantiate(shape_t, names_t, ("T", cell, world_index))
    return _finish_cell(cell, world_index, shape_t, shape_s,
                        target, names_t, rng)

def _finish_cell(cell, world_index, shape_t, shape_s, target, names_t, rng):
    spec = WORLDS_DC1_V1
    if cell in ("A", "C"):
        forced_types = [t["type"] for t in target["inputs"]]
        source = instantiate(shape_s, list(names_t), ("S", cell, world_index),
                             forced_types=forced_types,
                             forced_predicates=list(target["predicates"]))
    else:
        n_pred_s = rng.randint(2, 4)
        names_s = fresh_predicate_names(rng, n_pred_s)
        source = instantiate(shape_s, names_s, ("S", cell, world_index))

    sig_t, sig_s = surface_of(target), surface_of(source)
    if cell in ("A", "C") and sig_t != sig_s:
        raise SystemExit("surface_same construction failed for %s-%02d"
                         % (cell, world_index))
    if cell in ("B", "D") and sig_t == sig_s:
        raise SystemExit("surface reminting failed for %s-%02d"
                         % (cell, world_index))

    return {
        "cell": cell, "world_index": world_index,
        "source": source, "target": target,
        "sig_source": sig_s, "sig_target": sig_t,
        "declared_surface_same": cell in ("A", "C"),
        "declared_latent_same": cell in ("A", "B"),
        "ecology_axes": {
            "rho": Fraction(1, 2),
            "sigma": Fraction(1, 1) if cell in ("A", "B") else Fraction(0, 1),
            "d": dag_depth(LATENT_SHAPES[shape_t]),
            "delta": 0,
        },
    }

def all_worlds():
    out = []
    for cell in WORLDS_DC1_V1["cells"]:
        for wi in range(WORLDS_DC1_V1["worlds_per_cell"]):
            out.append(build_cell(cell, wi))
    return out

# frozen latent classes (module-level, generated once, deterministic)
LATENT_SHAPES = gen_latent_shapes(WORLDS_DC1_V1["n_latent_classes"])
