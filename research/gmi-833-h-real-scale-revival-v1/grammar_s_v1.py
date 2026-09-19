"""The lower grammar G_S of gmi-833-h-real-scale-revival-v1.

Frozen by FREEZE_V1.md section 5. Stdlib only, exact rational arithmetic.

This module is written from the registered specification in FREEZE_V1.md and
imports nothing from any parent package. It receives no family name, no family
identifier, no response values and no family-specific candidate menu.
"""
from fractions import Fraction as Q
import hashlib
import itertools

UNARY_OPS = ("NEG", "ABS", "STEP", "RECIP")
BINARY_OPS = ("ADD", "MUL")

BODY_LEAVES = ("ARG", "PARAM", "C0", "C1")
HEAD_LEAVES = ("S", "BIAS", "STATE", "C0", "C1")

BODY_BUDGET = 3
HEAD_BUDGET = 4

LITERALS = {"C0": Q(0), "C1": Q(1)}

PROBE = (Q(-2), Q(-1), Q(-1, 2), Q(0), Q(1, 2), Q(1), Q(2))
AFFINE_GRID = (Q(-2), Q(-1), Q(0), Q(1), Q(2))


def nodes(tree):
    if tree[0] == "LEAF":
        return 1
    total = 1
    for kid in tree[1:]:
        total += nodes(kid)
    return total


def show(tree):
    if tree[0] == "LEAF":
        return tree[1]
    return tree[0] + "(" + ",".join(show(k) for k in tree[1:]) + ")"


def value(tree, env):
    """Exact evaluation over Fractions. Total on every environment."""
    op = tree[0]
    if op == "LEAF":
        name = tree[1]
        if name in LITERALS:
            return LITERALS[name]
        return env[name]
    if op == "NEG":
        return -value(tree[1], env)
    if op == "ABS":
        v = value(tree[1], env)
        return v if v >= 0 else -v
    if op == "STEP":
        return Q(1) if value(tree[1], env) > 0 else Q(0)
    if op == "RECIP":
        v = value(tree[1], env)
        return Q(0) if v == 0 else 1 / v
    if op == "ADD":
        return value(tree[1], env) + value(tree[2], env)
    if op == "MUL":
        return value(tree[1], env) * value(tree[2], env)
    raise ValueError("G_S has no operation " + str(op))


def to_python(tree):
    """Float source string, used only inside fitting routines."""
    op = tree[0]
    if op == "LEAF":
        name = tree[1]
        if name == "C0":
            return "0.0"
        if name == "C1":
            return "1.0"
        return name.lower()
    if op == "NEG":
        return "(-(" + to_python(tree[1]) + "))"
    if op == "ABS":
        return "(abs(" + to_python(tree[1]) + "))"
    if op == "STEP":
        return "(1.0 if (" + to_python(tree[1]) + ")>0.0 else 0.0)"
    if op == "RECIP":
        return "(_reciprocal(" + to_python(tree[1]) + "))"
    if op == "ADD":
        return "((" + to_python(tree[1]) + ")+(" + to_python(tree[2]) + "))"
    if op == "MUL":
        return "((" + to_python(tree[1]) + ")*(" + to_python(tree[2]) + "))"
    raise ValueError("G_S has no operation " + str(op))


def all_trees(budget, leaves):
    """Complete, response-independent enumeration by node count."""
    tiers = {1: [("LEAF", name) for name in leaves]}
    for n in range(2, budget + 1):
        tier = []
        for op in UNARY_OPS:
            for kid in tiers[n - 1]:
                tier.append((op, kid))
        for op in BINARY_OPS:
            for left in range(1, n - 1):
                right = n - 1 - left
                if right < 1:
                    continue
                for a in tiers[left]:
                    for b in tiers[right]:
                        tier.append((op, a, b))
        tiers[n] = tier
    out = []
    for n in range(1, budget + 1):
        out.extend(tiers[n])
    return out


_BODY_GRID = None
_HEAD_GRID = None


def body_grid():
    global _BODY_GRID
    if _BODY_GRID is None:
        _BODY_GRID = [{"ARG": a, "PARAM": p} for a in PROBE for p in PROBE]
    return _BODY_GRID


def head_grid():
    global _HEAD_GRID
    if _HEAD_GRID is None:
        _HEAD_GRID = [{"S": s, "BIAS": b, "STATE": t}
                      for s in PROBE for b in PROBE for t in PROBE]
    return _HEAD_GRID


def meaning(tree, grid):
    return tuple(value(tree, point) for point in grid)


def collapse(trees, grid):
    """One canonical representative per meaning: fewest nodes, then smallest
    rendering. Returns (representatives, meaning_by_rendering, raw, classes)."""
    pick = {}
    for tree in trees:
        key = (nodes(tree), show(tree))
        m = meaning(tree, grid)
        if m not in pick or key < pick[m][0]:
            pick[m] = (key, tree)
    reps = [pick[m][1] for m in sorted(pick, key=lambda mm: pick[mm][0])]
    return reps, dict((show(pick[m][1]), m) for m in pick), len(trees), len(pick)


def digest():
    """Stable digest of the frozen grammar definition."""
    h = hashlib.sha256()
    h.update(("+".join(UNARY_OPS) + "/" + "+".join(BINARY_OPS)).encode())
    h.update(("+".join(BODY_LEAVES) + "/" + "+".join(HEAD_LEAVES)).encode())
    h.update(("%d/%d" % (BODY_BUDGET, HEAD_BUDGET)).encode())
    h.update("+".join(str(v) for v in PROBE).encode())
    return h.hexdigest()


_DEPENDS_CACHE = {}


def depends_on(tree, leaf, others):
    """True iff the meaning moves when `leaf` moves, others held fixed."""
    key = (show(tree), leaf)
    if key in _DEPENDS_CACHE:
        return _DEPENDS_CACHE[key]
    _DEPENDS_CACHE[key] = _depends_on_uncached(tree, leaf, others)
    return _DEPENDS_CACHE[key]


def _depends_on_uncached(tree, leaf, others):
    for combo in itertools.product(PROBE, repeat=len(others)):
        env = dict(zip(others, combo))
        seen = set()
        for v in PROBE:
            env2 = dict(env)
            env2[leaf] = v
            seen.add(value(tree, env2))
        if len(seen) > 1:
            return True
    return False


_AFFINE_CACHE = {}


def affine_in(tree, leaf, leaves):
    """True iff, for every fixed assignment to the other leaves, leaf -> value
    is affine on the arithmetic sub-grid (-2,-1,0,1,2)."""
    key = (show(tree), leaf)
    if key in _AFFINE_CACHE:
        return _AFFINE_CACHE[key]
    _AFFINE_CACHE[key] = _affine_in_uncached(tree, leaf, leaves)
    return _AFFINE_CACHE[key]


def _affine_in_uncached(tree, leaf, leaves):
    others = [x for x in leaves if x != leaf]
    for combo in itertools.product(PROBE, repeat=len(others)):
        env = dict(zip(others, combo))
        ys = []
        for v in AFFINE_GRID:
            env2 = dict(env)
            env2[leaf] = v
            ys.append(value(tree, env2))
        for i in range(len(ys) - 2):
            if ys[i] - 2 * ys[i + 1] + ys[i + 2] != 0:
                return False
    return True


CLASS_PRIORITY = ("PERSISTENT_STATE", "LIFTED_BASIS", "NONLINEAR_LINK",
                  "AFFINE_SCORE")


def classify(body, head):
    """Attributes and primary structural class. Reads expression trees only.

    Priority is FREEZE_V1.md section 5, fixed before any outcome existed:
      head depends on STATE       -> PERSISTENT_STATE
      else BODY not affine in ARG -> LIFTED_BASIS
      else HEAD not affine in S   -> NONLINEAR_LINK
      else                        -> AFFINE_SCORE
    """
    if not isinstance(body, tuple) or not isinstance(head, tuple):
        raise TypeError("classify reads expression trees and nothing else")
    stateful = depends_on(head, "STATE", ["S", "BIAS"])
    body_affine = affine_in(body, "ARG", ["ARG", "PARAM"])
    head_affine = affine_in(head, "S", ["S", "BIAS", "STATE"])
    grid = body_grid()
    product_body = meaning(body, grid) == meaning(
        ("MUL", ("LEAF", "ARG"), ("LEAF", "PARAM")), grid)
    if stateful:
        name = "PERSISTENT_STATE"
    elif not body_affine:
        name = "LIFTED_BASIS"
    elif not head_affine:
        name = "NONLINEAR_LINK"
    else:
        name = "AFFINE_SCORE"
    return {"reads_state": stateful,
            "body_affine_in_arg": body_affine,
            "head_affine_in_s": head_affine,
            "body_is_arg_times_param": product_body,
            "class": name}


def program_cost(body, head, m, stateful):
    """Charged cost of the compact composed program at index-set size m."""
    ops = m * nodes(body) + m + nodes(head)
    storage = m + 1 + (1 if stateful else 0)
    return {"ops": ops, "storage": storage, "total": ops + storage}


def table_cost(m):
    """Charged cost of the tabulated alternative at index-set size m."""
    return {"ops": m, "storage": 2 ** m, "total": m + 2 ** m}


def table_crossover(body, head, stateful, m_max=64):
    """Smallest m >= 1 at which the tabulated alternative costs strictly more."""
    for m in range(1, m_max + 1):
        if table_cost(m)["total"] > program_cost(body, head, m, stateful)["total"]:
            return m
    return None


def landmark_cost(q, d):
    """Charged cost of a landmark/kernel arm with q landmarks in d dimensions."""
    ops = q * (2 * d + 1) + q
    storage = q * d + q
    return {"ops": ops, "storage": storage, "total": ops + storage}


def landmark_crossover(body, head, stateful, m, d, q_max=4096):
    """Smallest q >= 1 at which the landmark arm costs strictly more than the
    compact lifted program at index-set size m."""
    base = program_cost(body, head, m, stateful)["total"]
    for q in range(1, q_max + 1):
        if landmark_cost(q, d)["total"] > base:
            return q
    return None
