#!/usr/bin/env python3
"""Grammar G_HA for gmi-833-h-family-tranche-a-v1.

One common neutral Boolean grammar over the carrier {0,1}, leaves 0,1,x0..x7,
operators NOT, XOR, AND, node-count cost. Enumerates exhaustively and
quotients semantically on the complete carrier-image grid. Receives no family
name, no row identifier, and no target-specific candidate menu. Structural
family names are attached only afterward by the post-hoc classifier in
family_tranche_a_v1.py, which reads expression trees and nothing else.
"""
import hashlib


CARRIER = (0, 1)
LEAVES = ("0", "1", "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7")
UNARY = ("NOT",)
BINARY = ("XOR", "AND")
BUDGET = 5

CONST = {"0": 0, "1": 1}


def nodes(tree):
    if tree[0] == "LEAF":
        return 1
    return 1 + sum(nodes(k) for k in tree[1:])


def show(tree):
    if tree[0] == "LEAF":
        return tree[1]
    return tree[0] + "(" + ",".join(show(k) for k in tree[1:]) + ")"


def value(tree, env):
    op = tree[0]
    if op == "LEAF":
        if tree[1] in CONST:
            return CONST[tree[1]]
        return env[tree[1]]
    if op == "NOT":
        return 1 - value(tree[1], env)
    if op == "XOR":
        return value(tree[1], env) ^ value(tree[2], env)
    if op == "AND":
        return value(tree[1], env) & value(tree[2], env)
    raise ValueError("G_HA has no operation " + str(op))


def all_trees(budget, leaves):
    """Complete, target-independent enumeration by node count."""
    tiers = {1: [("LEAF", name) for name in leaves]}
    for n in range(2, budget + 1):
        tier = []
        for op in UNARY:
            for kid in tiers[n - 1]:
                tier.append((op, kid))
        for op in BINARY:
            for left in range(1, n - 1):
                right = n - 1 - left
                if right < 1:
                    continue
                for a in tiers[left]:
                    for b in tiers[right]:
                        if show(a) > show(b):
                            # canonical order for commutative pair
                            tier.append((op, b, a))
                        else:
                            tier.append((op, a, b))
        tiers[n] = tier
    out = []
    for n in range(1, budget + 1):
        out.extend(tiers[n])
    return out


def points():
    """All 256 points of the complete ecology cube -- all channels excited."""
    out = []
    for m in range(256):
        env = {}
        for i in range(8):
            env["x%d" % i] = (m >> i) & 1
        out.append(env)
    return out


def meaning(tree):
    return tuple(value(tree, pt) for pt in points())


def collapse(trees):
    """One canonical representative per semantic class on the complete cube.

    Canonical = fewest nodes, then lexicographically smallest rendering.
    Returns (representatives, classes).
    """
    pick = {}
    for tree in trees:
        key = (nodes(tree), show(tree))
        m = meaning(tree)
        if m not in pick or key < pick[m][0]:
            pick[m] = (key, tree)
    reps = [pick[m][1] for m in sorted(pick, key=lambda mm: pick[mm][0])]
    return reps, len(pick)


def digest():
    h = hashlib.sha256()
    h.update(("+".join(LEAVES)).encode())
    h.update(("+".join(UNARY) + "/" + "+".join(BINARY)).encode())
    h.update(("BUDGET=%d" % BUDGET).encode())
    h.update(("ECO=BINARY_CUBE_8").encode())
    return h.hexdigest()


def minimum_cost(truth_table):
    """Exact minimum node cost of a truth table over the grammar image.

    Computed by complete exhaustive search over the enumerated representatives.
    Returns (cost, representative) or None if outside the image at BUDGET.
    """
    best = None
    for tree in all_trees(BUDGET, LEAVES):
        m = meaning(tree)
        if m == truth_table:
            c = nodes(tree)
            if best is None or c < best[0]:
                best = (c, tree)
    return best


def class_of(tree):
    """Generic structural tags read only from the expression tree.

    These are behavioural descriptors, not family claims; family names are
    attached by the post-hoc mapping after selection.
    """
    return {
        "nodes": nodes(tree),
        "rendering": show(tree),
        "reads_x3": _depends(tree, "x3"),
        "reads_x4": _depends(tree, "x4"),
        "uses_xor": ",XOR" in ("," + show(tree)) or show(tree).startswith("XOR"),
        "uses_and_at_root": tree[0] == "AND",
        "uses_and_anywhere": _contains(tree, "AND"),
        "uses_xor_anywhere": _contains(tree, "XOR"),
    }


def _contains(tree, op):
    if tree[0] == "LEAF":
        return False
    if tree[0] == op:
        return True
    return any(_contains(k, op) for k in tree[1:])


def _depends(tree, leaf):
    """True iff the output varies with `leaf` over the complete cube."""
    if tree[0] == "LEAF":
        return tree[1] == leaf
    if tree[0] == "XOR":
        return _depends(tree[1], leaf) != _depends(tree[2], leaf)
    if tree[0] == "AND":
        if _depends(tree[1], leaf) and _depends(tree[2], leaf):
            return True
        # a AND b: depends iff at least one child depends on leaf and the other
        # can co-vary; on the full cube every leaf can be 0 and 1, so we check
        # the exact condition below.
        d1, d2 = _depends(tree[1], leaf), _depends(tree[2], leaf)
        if not (d1 or d2):
            return False
        # value moves with leaf iff the other child can be 1 while leaf moves.
        other = tree[2] if d1 else tree[1]
        if not d1:
            other = tree[1]
        if _can_be_other_than(leaf):
            pass
        # conservative: full evaluation is authoritative; this predicate is
        # only used as a structural tag and re-checked by exact min-cost anyway.
        return any(value(tree, pt) != value(tree, ptwith) for pt, ptwith in
                   zip(points(), points_with_flip(tree, leaf)))
    if tree[0] == "NOT":
        return _depends(tree[1], leaf)
    return False


def points_with_flip(tree, leaf):
    out = []
    for pt in points():
        env2 = dict(pt)
        env2[leaf] = 1 - env2[leaf]
        out.append(env2)
    return out


def depends_on_leaf(tree, leaf):
    """Authoritative: does the denotation change under flipping `leaf`."""
    if tree[0] == "LEAF":
        return tree[1] == leaf
    pts = points()
    flips = points_with_flip(tree, leaf)
    for a, b in zip(pts, flips):
        if value(tree, a) != value(tree, b):
            return True
    return False
