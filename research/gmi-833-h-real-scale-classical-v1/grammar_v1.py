"""Neutral lower grammar G_R for gmi-833-h-real-scale-classical-v1.

Frozen by FREEZE_V1.md section 5 and FREEZE_V1_ECOLOGY_ADDENDUM.md section A8.
Stdlib only. Exact rational arithmetic (fractions.Fraction) throughout.

The grammar receives no family name, no family identifier, no target values and
no family-specific candidate menu. Structural names are attached only after
selection, by classify(), which reads an expression tree and nothing else.
"""
from fractions import Fraction as F
import hashlib
import itertools

# ---------------------------------------------------------------- grammar ----

UNARY = ("NEG", "ABS", "STEP", "RECIP")
BINARY = ("ADD", "MUL")

BODY_LEAVES = ("ARG", "PARAM", "C0", "C1")
HEAD_LEAVES = ("S", "BIAS", "STATE", "C0", "C1")

BODY_MAX_NODES = 3
HEAD_MAX_NODES = 4

CONST = {"C0": F(0), "C1": F(1)}


def size(e):
    if e[0] == "L":
        return 1
    return 1 + sum(size(c) for c in e[1:])


def render(e):
    if e[0] == "L":
        return e[1]
    return e[0] + "(" + ",".join(render(c) for c in e[1:]) + ")"


def ev(e, env):
    """Exact evaluation of an expression tree over Fractions."""
    h = e[0]
    if h == "L":
        n = e[1]
        if n in CONST:
            return CONST[n]
        return env[n]
    if h == "NEG":
        return -ev(e[1], env)
    if h == "ABS":
        v = ev(e[1], env)
        return v if v >= 0 else -v
    if h == "STEP":
        return F(1) if ev(e[1], env) > 0 else F(0)
    if h == "RECIP":
        v = ev(e[1], env)
        return F(0) if v == 0 else 1 / v
    if h == "ADD":
        return ev(e[1], env) + ev(e[2], env)
    if h == "MUL":
        return ev(e[1], env) * ev(e[2], env)
    raise ValueError("unknown op " + str(h))


def codegen(e):
    """Compile an expression tree to a Python source string over floats.

    Used only inside fitting/search routines. Every claim is recomputed with
    ev() over Fractions.
    """
    h = e[0]
    if h == "L":
        n = e[1]
        if n == "C0":
            return "0.0"
        if n == "C1":
            return "1.0"
        return n.lower()
    if h == "NEG":
        return "(-(" + codegen(e[1]) + "))"
    if h == "ABS":
        return "(abs(" + codegen(e[1]) + "))"
    if h == "STEP":
        return "(1.0 if (" + codegen(e[1]) + ")>0.0 else 0.0)"
    if h == "RECIP":
        return "(_rec(" + codegen(e[1]) + "))"
    if h == "ADD":
        return "((" + codegen(e[1]) + ")+(" + codegen(e[2]) + "))"
    if h == "MUL":
        return "((" + codegen(e[1]) + ")*(" + codegen(e[2]) + "))"
    raise ValueError("unknown op " + str(h))


def enumerate_exprs(max_nodes, leaves):
    """Complete, target-independent enumeration by node count."""
    by_size = {1: [("L", n) for n in leaves]}
    for n in range(2, max_nodes + 1):
        out = []
        for op in UNARY:
            for c in by_size[n - 1]:
                out.append((op, c))
        for op in BINARY:
            for a in range(1, n - 1):
                b = n - 1 - a
                if b < 1:
                    continue
                for x in by_size[a]:
                    for y in by_size[b]:
                        out.append((op, x, y))
        by_size[n] = out
    all_e = []
    for n in range(1, max_nodes + 1):
        all_e.extend(by_size[n])
    return all_e


# ------------------------------------------------------------ probe grids ----

PROBE_1D = (F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2))


def body_probe_points():
    return [{"ARG": a, "PARAM": p} for a in PROBE_1D for p in PROBE_1D]


def head_probe_points():
    return [
        {"S": s, "BIAS": b, "STATE": t}
        for s in PROBE_1D
        for b in PROBE_1D
        for t in PROBE_1D
    ]


def denotation(e, points):
    return tuple(ev(e, pt) for pt in points)


def quotient(exprs, points):
    """Semantic quotient: one canonical representative per denotation.

    Canonical = fewest nodes, then lexicographically smallest rendering.
    Returns (reps, denot_of_rep, n_raw, n_classes).
    """
    best = {}
    for e in exprs:
        d = denotation(e, points)
        key = (size(e), render(e))
        if d not in best or key < best[d][0]:
            best[d] = (key, e)
    reps = [best[d][1] for d in sorted(best, key=lambda dd: best[dd][0])]
    return reps, {render(best[d][1]): d for d in best}, len(exprs), len(best)


def grammar_digest():
    """Stable digest of the frozen grammar definition."""
    h = hashlib.sha256()
    h.update(("|".join(UNARY) + "#" + "|".join(BINARY)).encode())
    h.update(("|".join(BODY_LEAVES) + "#" + "|".join(HEAD_LEAVES)).encode())
    h.update(("%d#%d" % (BODY_MAX_NODES, HEAD_MAX_NODES)).encode())
    h.update("|".join(str(v) for v in PROBE_1D).encode())
    return h.hexdigest()


# --------------------------------------------------- post-hoc classifier -----
# Reads only the expression trees. Never receives a family name or a target.

def _depends_on(e, leaf, points, other_leaves):
    """True iff the denotation varies when `leaf` varies, others held fixed."""
    for combo in itertools.product(PROBE_1D, repeat=len(other_leaves)):
        env = dict(zip(other_leaves, combo))
        vals = set()
        for v in PROBE_1D:
            env2 = dict(env)
            env2[leaf] = v
            vals.add(ev(e, env2))
        if len(vals) > 1:
            return True
    return False


def _affine_in(e, leaf, points_leaves):
    """True iff, for every fixed assignment to the other leaves, the map
    leaf -> value is affine on the arithmetic sub-grid (-2,-1,0,1,2)."""
    grid = (F(-2), F(-1), F(0), F(1), F(2))
    others = [l for l in points_leaves if l != leaf]
    for combo in itertools.product(PROBE_1D, repeat=len(others)):
        env = dict(zip(others, combo))
        ys = []
        for v in grid:
            env2 = dict(env)
            env2[leaf] = v
            ys.append(ev(e, env2))
        for i in range(len(ys) - 2):
            if ys[i] - 2 * ys[i + 1] + ys[i + 2] != 0:
                return False
    return True


def classify(body, head):
    """Attribute vector and primary structural class of a candidate.

    Priority (fixed here, before any outcome exists):
      reads_state          -> PERSISTENT_STATE
      else body_nonaffine  -> LIFTED_BASIS
      else head_nonaffine  -> NONLINEAR_LINK
      else                 -> AFFINE_SCORE
    """
    reads_state = _depends_on(head, "STATE", None, ["S", "BIAS"])
    body_affine = _affine_in(body, "ARG", ["ARG", "PARAM"])
    head_affine = _affine_in(head, "S", ["S", "BIAS", "STATE"])
    body_mult = denotation(body, body_probe_points()) == denotation(
        ("MUL", ("L", "ARG"), ("L", "PARAM")), body_probe_points()
    )
    if reads_state:
        cls = "PERSISTENT_STATE"
    elif not body_affine:
        cls = "LIFTED_BASIS"
    elif not head_affine:
        cls = "NONLINEAR_LINK"
    else:
        cls = "AFFINE_SCORE"
    return {
        "reads_state": reads_state,
        "body_affine_in_arg": body_affine,
        "head_affine_in_s": head_affine,
        "body_is_arg_times_param": body_mult,
        "class": cls,
    }


# ------------------------------------------------------------ cost model -----
# FREEZE_V1_ECOLOGY_ADDENDUM.md section A5. Exact integers only.

def program_cost(body, head, m, reads_state):
    ops = m * size(body) + m + size(head)
    storage = m + 1 + (1 if reads_state else 0)
    return {"ops": ops, "storage": storage, "total": ops + storage}


def table_cost(m):
    ops = m
    storage = 2 ** m
    return {"ops": ops, "storage": storage, "total": ops + storage}


def table_crossover(body, head, reads_state, m_max=64):
    """Smallest m >= 1 at which the tabulated alternative costs strictly more."""
    for m in range(1, m_max + 1):
        if table_cost(m)["total"] > program_cost(body, head, m, reads_state)["total"]:
            return m
    return None
