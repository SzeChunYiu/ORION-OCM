"""The successor grammar G_H of gmi-833-h-successor-constructs-v1.

Frozen by FREEZE_V1.md sections 4 and 7 and FREEZE_V1_ADDENDUM.md. Stdlib
only, exact rational arithmetic, no float anywhere.

Written from the registered specification. Imports nothing from any parent
package. Receives no family name, no family identifier, no response values and
no family-specific candidate menu.
"""
from fractions import Fraction as Q
import hashlib
import itertools

UNARY_OPS = ("NEG", "ABS", "STEP", "RECIP")
BINARY_OPS = ("ADD", "MUL")

BODY_LEAVES = ("ARG", "PARAM", "C0", "C1")
BODY2_LEAVES = ("U", "PARAM2", "C0", "C1")
HEAD_LEAVES = ("S1", "S2", "BIAS", "STATE", "RESP", "C0", "C1")
GS_HEAD_LEAVES = ("S1", "BIAS", "STATE", "C0", "C1")

BODY_BUDGET = 3
BODY2_BUDGET = 4
HEAD_BUDGET = 4

N_INDEX = 12
W_STAGE = 4
TIE_MODULI = (1, 2, 3, 4, 6, 12)
RESPONSE_SET = (Q(-6), Q(-4), Q(0), Q(4), Q(6))
COMBINERS = ("ADD", "MUL")
COMBINER_IDENTITY = {"ADD": Q(0), "MUL": Q(1)}
REDUCTIONS = ("NONE", "ARGMIN", "RSUM")

B_MAX = 10

LITERALS = {"C0": Q(0), "C1": Q(1)}
PROBE = (Q(-2), Q(-1), Q(-1, 2), Q(0), Q(1, 2), Q(1), Q(2))
AFFINE_GRID = (Q(-2), Q(-1), Q(0), Q(1), Q(2))

CLASS_PRIORITY = (
    "RESPONSE_SPACE_SEARCH",
    "MULTIPLICATIVE_ACCUMULATION",
    "NORMALISED_RATIO",
    "COUPLED_FOLDS",
    "LAYERED_NONLINEAR",
    "LAYERED_AFFINE",
    "TIED_PARAMETER",
    "PERSISTENT_STATE",
    "LIFTED_BASIS",
    "NONLINEAR_LINK",
    "AFFINE_SCORE",
)


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
    raise ValueError("G_H has no operation " + str(op))


_ZERO = Q(0)
_ONE = Q(1)


def compile_tree(tree, order):
    """Closure evaluator over a positional tuple. Exact; no float."""
    op = tree[0]
    if op == "LEAF":
        name = tree[1]
        if name in LITERALS:
            lit = LITERALS[name]
            return lambda v: lit
        idx = order.index(name)
        return lambda v: v[idx]
    if op == "NEG":
        a = compile_tree(tree[1], order)
        return lambda v: -a(v)
    if op == "ABS":
        a = compile_tree(tree[1], order)
        return lambda v: abs(a(v))
    if op == "STEP":
        a = compile_tree(tree[1], order)
        return lambda v: _ONE if a(v) > 0 else _ZERO
    if op == "RECIP":
        a = compile_tree(tree[1], order)
        return lambda v: (_ZERO if a(v) == 0 else 1 / a(v))
    if op == "ADD":
        a = compile_tree(tree[1], order)
        b = compile_tree(tree[2], order)
        return lambda v: a(v) + b(v)
    if op == "MUL":
        a = compile_tree(tree[1], order)
        b = compile_tree(tree[2], order)
        return lambda v: a(v) * b(v)
    raise ValueError("G_H has no operation " + str(op))


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


def meaning(tree, grid):
    return tuple(value(tree, point) for point in grid)


def quotient_classes(trees, grid):
    """Count distinct meanings. Reporting only: the search is over raw trees,
    so no semantically distinct program is ever dropped by a coarse grid."""
    seen = set()
    for tree in trees:
        seen.add(meaning(tree, grid))
    return len(seen)


def body_grid():
    return [{"ARG": a, "PARAM": p} for a in PROBE for p in PROBE]


def body2_grid():
    return [{"U": a, "PARAM2": p} for a in PROBE for p in PROBE]


def head_grid_small():
    """Head probe grid for the quotient count only (3-point sub-grid)."""
    sub = (Q(-1), Q(1, 2), Q(2))
    out = []
    for s1 in sub:
        for s2 in sub:
            for b in sub:
                for t in sub:
                    for r in sub:
                        out.append({"S1": s1, "S2": s2, "BIAS": b,
                                    "STATE": t, "RESP": r})
    return out


_DEPENDS = {}
_AFFINE = {}


def depends_on(tree, leaf, others):
    key = (show(tree), leaf, tuple(others))
    hit = _DEPENDS.get(key)
    if hit is not None:
        return hit
    out = False
    for combo in itertools.product(PROBE, repeat=len(others)):
        env = dict(zip(others, combo))
        seen = set()
        for v in PROBE:
            env[leaf] = v
            seen.add(value(tree, env))
        if len(seen) > 1:
            out = True
            break
    _DEPENDS[key] = out
    return out


def affine_in(tree, leaf, leaves):
    key = (show(tree), leaf, tuple(leaves))
    hit = _AFFINE.get(key)
    if hit is not None:
        return hit
    others = [x for x in leaves if x != leaf]
    out = True
    for combo in itertools.product(PROBE, repeat=len(others)):
        env = dict(zip(others, combo))
        ys = []
        for v in AFFINE_GRID:
            env[leaf] = v
            ys.append(value(tree, env))
        bad = False
        for i in range(len(ys) - 2):
            if ys[i] - 2 * ys[i + 1] + ys[i + 2] != 0:
                bad = True
                break
        if bad:
            out = False
            break
    _AFFINE[key] = out
    return out


def head_signature(head):
    """Tree-only predicates of a head. Never reads a family label."""
    lv = list(HEAD_LEAVES[:5])
    return {
        "dep_S1": depends_on(head, "S1", [x for x in lv if x != "S1"]),
        "dep_S2": depends_on(head, "S2", [x for x in lv if x != "S2"]),
        "dep_STATE": depends_on(head, "STATE", [x for x in lv if x != "STATE"]),
        "dep_RESP": depends_on(head, "RESP", [x for x in lv if x != "RESP"]),
        "aff_S1": affine_in(head, "S1", lv),
        "aff_S2": affine_in(head, "S2", lv),
    }


def body_signature(body):
    return {"aff_ARG": affine_in(body, "ARG", ["ARG", "PARAM"])}


def body2_signature(body2):
    return {"aff_U": affine_in(body2, "U", ["U", "PARAM2"])}


def classify(flags, head_sig, body_sig, body2_sig):
    """Post-hoc structural class. Reads trees and structural flags only.

    Priority is FREEZE_V1.md section 4.10, fixed before any outcome existed.
    """
    if not isinstance(flags, dict) or not isinstance(head_sig, dict):
        raise TypeError("classify reads structural flags and tree signatures")
    for key in flags:
        if key not in ("r", "L", "p", "kind", "ops"):
            raise TypeError("classify was handed a non-structural field: " + str(key))
    r = flags["r"]
    L = flags["L"]
    p = flags["p"]
    kind = flags["kind"]
    ops = flags["ops"]
    if kind != "NONE" and head_sig["dep_RESP"]:
        return "RESPONSE_SPACE_SEARCH"
    if "MUL" in ops:
        return "MULTIPLICATIVE_ACCUMULATION"
    if r == 2 and head_sig["dep_S1"] and head_sig["dep_S2"]:
        if (not head_sig["aff_S1"]) or (not head_sig["aff_S2"]):
            return "NORMALISED_RATIO"
        return "COUPLED_FOLDS"
    if L == 2:
        if body2_sig is not None and not body2_sig["aff_U"]:
            return "LAYERED_NONLINEAR"
        return "LAYERED_AFFINE"
    if p != N_INDEX:
        return "TIED_PARAMETER"
    if head_sig["dep_STATE"]:
        return "PERSISTENT_STATE"
    if body_sig is not None and not body_sig["aff_ARG"]:
        return "LIFTED_BASIS"
    if not head_sig["aff_S1"]:
        return "NONLINEAR_LINK"
    return "AFFINE_SCORE"


def charged_cost(flags, bodies, body2, head):
    """FREEZE_V1.md section 4.7. Integers only."""
    total = 0
    for b in bodies:
        total += nodes(b)
    if flags["L"] == 2:
        total += nodes(body2)
    total += nodes(head)
    if flags["r"] == 2:
        total += 1
    if flags["L"] == 2:
        total += 1
    if flags["p"] != N_INDEX:
        total += 1
    if flags["kind"] != "NONE":
        total += 1
    return total


def render(flags, bodies, body2, head):
    parts = ["r=%d" % flags["r"], "L=%d" % flags["L"], "p=%d" % flags["p"],
             "kind=" + flags["kind"], "ops=" + "+".join(flags["ops"])]
    parts.append("bodies=" + "|".join(show(b) for b in bodies))
    parts.append("body2=" + (show(body2) if body2 is not None else "-"))
    parts.append("head=" + show(head))
    return ";".join(parts)


def serve_cost(flags, bodies, body2, head, n_index, w_stage, y_size):
    """Charged serve cost at deployment size. Integers only.

    ops   = per-index body evaluations + per-index combines + head evaluations
    store = parameter slots + fold accumulators + output

    The parameter-slot count is the deployment size `n_index` when the tying
    map is the identity — that is, when `p` equals the registered index-set
    size `N_INDEX` — and `p` otherwise. Comparing `p` against the varying
    `n_index` instead would charge an untied program a constant `p` slots at
    every deployment size; route B caught exactly that and it is fixed here.
    """
    ops = 0
    store = 0
    if flags["L"] == 2:
        ops += n_index * w_stage * nodes(bodies[0]) + n_index * w_stage
        ops += w_stage * nodes(body2) + w_stage
        store += (n_index if flags["p"] == N_INDEX else flags["p"]) * w_stage
        store += w_stage + 1
    else:
        for b in bodies:
            ops += n_index * nodes(b) + n_index
        store += (n_index if flags["p"] == N_INDEX else flags["p"])
        store += flags["r"]
    reps = y_size if flags["kind"] != "NONE" else 1
    ops += reps * nodes(head)
    store += 1
    return {"ops": ops, "storage": store, "total": ops + store}


def table_cost(m):
    """Charged cost of the tabulated alternative at index-set size m."""
    return {"ops": m, "storage": 2 ** m, "total": m + 2 ** m}


def table_crossover(flags, bodies, body2, head, w_stage, y_size, m_max=64):
    """Smallest m >= 1 at which the tabulated alternative costs strictly more."""
    for m in range(1, m_max + 1):
        prog = serve_cost(flags, bodies, body2, head, m, w_stage, y_size)
        if table_cost(m)["total"] > prog["total"]:
            return m
    return None


def untied_storage(m):
    return m


def tied_storage(p):
    return p


def tie_crossover(p, m_max=64):
    """Smallest index-set size m at which untied parameter storage strictly
    exceeds tied storage at modulus p."""
    for m in range(1, m_max + 1):
        if untied_storage(m) > tied_storage(p):
            return m
    return None


def stage_crossover(w, m_max=64):
    """Smallest index-set size m at which the tabulated alternative's storage
    strictly exceeds a two-stage program's parameter storage m*w + w."""
    for m in range(1, m_max + 1):
        if 2 ** m > m * w + w:
            return m
    return None


def commutative_nf(tree):
    """Canonical form under commutativity of ADD and MUL. Reporting only: the
    search never uses it, so it cannot change which programs are found."""
    if tree[0] == "LEAF":
        return tree
    if len(tree) == 2:
        return (tree[0], commutative_nf(tree[1]))
    a = commutative_nf(tree[1])
    b = commutative_nf(tree[2])
    if tree[0] in ("ADD", "MUL") and show(b) < show(a):
        a, b = b, a
    return (tree[0], a, b)


def swap_s1_s2(tree):
    if tree[0] == "LEAF":
        if tree[1] == "S1":
            return ("LEAF", "S2")
        if tree[1] == "S2":
            return ("LEAF", "S1")
        return tree
    return tuple([tree[0]] + [swap_s1_s2(k) for k in tree[1:]])


def equivalence_key(flags, bodies, body2, head):
    """A program's identity up to commutativity of ADD and MUL and, at r = 2,
    up to exchanging the two fold banks together with S1 and S2."""
    def render_with(bs, ops, hd):
        return ";".join([
            "r=%d" % flags["r"], "L=%d" % flags["L"], "p=%d" % flags["p"],
            "kind=" + flags["kind"], "ops=" + "+".join(ops),
            "bodies=" + "|".join(show(commutative_nf(b)) for b in bs),
            "body2=" + (show(commutative_nf(body2))
                        if body2 is not None else "-"),
            "head=" + show(commutative_nf(hd))])
    keys = [render_with(bodies, flags["ops"], head)]
    if flags["r"] == 2:
        keys.append(render_with([bodies[1], bodies[0]],
                                (flags["ops"][1], flags["ops"][0]),
                                swap_s1_s2(head)))
    return min(keys)


def digest():
    """Stable digest of the frozen grammar definition."""
    h = hashlib.sha256()
    h.update(("+".join(UNARY_OPS) + "/" + "+".join(BINARY_OPS)).encode())
    h.update(("+".join(BODY_LEAVES) + "/" + "+".join(BODY2_LEAVES) + "/"
              + "+".join(HEAD_LEAVES)).encode())
    h.update(("%d/%d/%d" % (BODY_BUDGET, BODY2_BUDGET, HEAD_BUDGET)).encode())
    h.update(("%d/%d/%d" % (N_INDEX, W_STAGE, B_MAX)).encode())
    h.update(("+".join(str(v) for v in PROBE)).encode())
    h.update(("+".join(str(v) for v in RESPONSE_SET)).encode())
    h.update(("+".join(str(v) for v in TIE_MODULI)).encode())
    h.update(("+".join(COMBINERS) + "/" + "+".join(REDUCTIONS)).encode())
    h.update(("+".join(CLASS_PRIORITY)).encode())
    return h.hexdigest()


FAMILY_TOKENS = (
    "bayes", "belief", "neural", "network", "conv", "cnn", "equivar",
    "flow", "transport", "energy", "ebm", "softmax", "attention",
    "kernel", "regress", "classifier", "glm", "automat", "family",
    "gaussian", "boltzmann", "jacobian", "posterior", "layer",
)


def macro_audit():
    """R03: the serialized grammar carries no family-named operation or leaf."""
    surface = []
    surface.extend(UNARY_OPS)
    surface.extend(BINARY_OPS)
    surface.extend(BODY_LEAVES)
    surface.extend(BODY2_LEAVES)
    surface.extend(HEAD_LEAVES)
    surface.extend(COMBINERS)
    surface.extend(REDUCTIONS)
    hits = []
    for name in surface:
        low = name.lower()
        for tok in FAMILY_TOKENS:
            if tok in low:
                hits.append((name, tok))
    return {"surface": tuple(surface), "hits": tuple(hits),
            "clean": len(hits) == 0}


def provenance_closed(trees):
    """Every operation in every enumerated tree is a registered primitive."""
    allowed = set(UNARY_OPS) | set(BINARY_OPS) | set(["LEAF"])
    stack = list(trees)
    while stack:
        t = stack.pop()
        if t[0] not in allowed:
            return False
        if t[0] != "LEAF":
            stack.extend(t[1:])
    return True
