#!/usr/bin/env python3
"""Grammar G for gmi-833-h-family-tranche-d-v1.

One common neutral Boolean grammar over the carrier {0,1}, leaves 0,1,x0..x7,
operators NOT, XOR, AND, node-count cost, budget B=5, on the complete ecology
{0,1}^8. Enumerates exhaustively and quotients semantically on the complete
carrier-image grid. Receives no family name, no row identifier, and no
target-specific candidate menu. Structural family names are attached only
afterward by the post-hoc classifier in tranche_d_v1.py, which reads
expression trees and nothing else.

This is the shared neutral grammar of the programme (the census, tranche A
SIGMA_HA, tranche C SIGMA_TC) -- the same specification, unchanged.
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
    raise ValueError("G has no operation " + str(op))


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


_POINTS_CACHE = None


def points():
    """All 256 points of the complete ecology cube -- all channels excited.

    The cube is cached at module scope: a pure performance measure. The
    enumeration, the digest, and every denotation are unchanged.
    """
    global _POINTS_CACHE
    if _POINTS_CACHE is None:
        out = []
        for m in range(256):
            env = {}
            for i in range(8):
                env["x%d" % i] = (m >> i) & 1
            out.append(env)
        _POINTS_CACHE = out
    return _POINTS_CACHE


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


def depends_on_leaf(tree, leaf):
    """Authoritative: does the denotation change under flipping `leaf`."""
    if tree[0] == "LEAF":
        return tree[1] == leaf
    pts = points()
    flips = []
    for pt in pts:
        env2 = dict(pt)
        env2[leaf] = 1 - env2[leaf]
        flips.append(env2)
    for a, b in zip(pts, flips):
        if value(tree, a) != value(tree, b):
            return True
    return False
