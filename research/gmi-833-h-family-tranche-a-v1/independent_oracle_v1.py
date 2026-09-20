#!/usr/bin/env python3
"""Route B: source-separated oracle for gmi-833-h-family-tranche-a-v1.

R10 independent search: a second implementation, source-separated from the
primary executor, re-derives the family-blind selections WITHOUT importing
this package. It writes ORACLE_RESULT_V1.json with its own tuple-truth-table
semantics, its own evaluator, and its own exhaustive minimum-cost search over
the SAME grammar specification frozen in FREEZE_V1.md.

    python3 -I -B independent_oracle_v1.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ORACLE_RESULT_V1.json")

SIGMA = "SIGMA_HA"
BUDGET = 5
LEAVES = ("0", "1", "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7")
CONST = {"0": 0, "1": 1}


# ---- independent grammar and evaluator ----
def oracle_value(tree, env):
    op = tree[0]
    if op == "LEAF":
        if tree[1] in CONST:
            return CONST[tree[1]]
        return env[tree[1]]
    if op == "NOT":
        return 1 - oracle_value(tree[1], env)
    if op == "XOR":
        return oracle_value(tree[1], env) ^ oracle_value(tree[2], env)
    if op == "AND":
        return oracle_value(tree[1], env) & oracle_value(tree[2], env)
    raise ValueError("oracle op " + str(op))


def oracle_build(budget):
    """Enumerate expression trees up to `budget` nodes (own ordering)."""
    tiers = {1: [("LEAF", n) for n in LEAVES]}
    for n in range(2, budget + 1):
        tier = []
        for kid in tiers[n - 1]:
            tier.append(("NOT", kid))
        for left in range(1, n - 1):
            right = n - 1 - left
            if right < 1:
                continue
            for a in tiers[left]:
                for b in tiers[right]:
                    tier.append(("XOR", a, b))
                    tier.append(("AND", a, b))
        tiers[n] = tier
    out = []
    for n in range(1, budget + 1):
        out.extend(tiers[n])
    return out


def oracle_meaning(tree):
    """Truth tuple over the complete cube in index order 0..255."""
    vals = []
    for m in range(256):
        env = {}
        for i in range(8):
            env["x%d" % i] = (m >> i) & 1
        vals.append(oracle_value(tree, env))
    return tuple(vals)


def oracle_render(tree):
    if tree[0] == "LEAF":
        return tree[1]
    return tree[0] + "(" + ",".join(oracle_render(k) for k in tree[1:]) + ")"


def oracle_nodes(tree):
    if tree[0] == "LEAF":
        return 1
    return 1 + sum(oracle_nodes(k) for k in tree[1:])


ALL_TREES = oracle_build(BUDGET)


def contract_tables():
    """Frozen contract truth tables, computed independently."""
    em = list(range(256))
    tables = {
        "x3": tuple((m >> 3) & 1 for m in em),
        "x4": tuple((m >> 4) & 1 for m in em),
        "AND3": tuple(((m & 1) & ((m >> 1) & 1) & ((m >> 2) & 1)) for m in em),
        "XOR3": tuple(((m & 1) ^ ((m >> 1) & 1) ^ ((m >> 2) & 1)) for m in em),
        "0": tuple(0 for m in em),
    }
    return tables


def minimum_exact(tt):
    best = None
    for tree in ALL_TREES:
        if oracle_meaning(tree) == tt:
            c = oracle_nodes(tree)
            key = (c, oracle_render(tree))
            if best is None or key < best[0]:
                best = (key, tree)
    return best


def depends_exact(tree, leaf):
    """Exact: does the truth table move when `leaf` flips."""
    if tree[0] == "LEAF":
        return tree[1] == leaf
    if tree[0] == "NOT":
        return depends_exact(tree[1], leaf)
    if tree[0] == "XOR":
        return depends_exact(tree[1], leaf) or depends_exact(tree[2], leaf)
    # AND
    return _and_depends(tree[1], tree[2], leaf)


def _and_depends(a, b, leaf):
    """a AND b depends on leaf iff (a depends-and-b-can-be-1) or reversed.

    On the complete cube every leaf can be 0 and 1 with any assignment to the
    other coordinates, so we implement the modification directly: the output
    changes under the flip iff either child changes while the other evaluates
    to 1 somewhere on a flipped pair.
    """
    if not (depends_exact(a, leaf) or depends_exact(b, leaf)):
        return False
    # quick structural: leaf can be selected to make the non-varying child 1
    a_dep, b_dep = depends_exact(a, leaf), depends_exact(b, leaf)
    if a_dep and b_dep:
        return True
    fixed = a if not a_dep else b
    if _may_be_one(fixed, leaf):
        return True
    return False


def _may_be_one(tree, leaf):
    """Can the tree evaluate to 1 for some assignment where `leaf`=1 and
    where `leaf`=0 (within the complete cube)?"""
    for m in range(256):
        for flip in (0, 1):
            env = {}
            for i in range(8):
                env["x%d" % i] = (m >> i) & 1
            env[leaf] = flip
            if oracle_value(tree, env) == 1:
                return True
    return False


def structural_class(tree):
    """Own post-hoc classifier consistent with the frozen priority:

    depends on x4  -> PERSISTENT_STATE_READ
    else depends on x3 -> ADDRESSABLE_CONTEXT_READ
    else a single coordinate leaf (not 0/1) -> ADDRESSABLE_CONTEXT_READ
    else root AND -> THRESHOLD_CONJUNCTION
    else -> BOOLEAN_COMPOSITION
    """
    if depends_exact(tree, "x4"):
        return "PERSISTENT_STATE_READ"
    if depends_exact(tree, "x3"):
        return "ADDRESSABLE_CONTEXT_READ"
    if tree[0] == "LEAF" and tree[1] not in ("0", "1"):
        return "ADDRESSABLE_CONTEXT_READ"
    if tree[0] == "AND":
        return "THRESHOLD_CONJUNCTION"
    return "BOOLEAN_COMPOSITION"


def main():
    tables = contract_tables()
    rows = {
        "H05": ("x3", "ADDRESSABLE_CONTEXT_READ"),
        "H06": ("x3", "ADDRESSABLE_CONTEXT_READ"),
        "H08": ("AND3", "THRESHOLD_CONJUNCTION"),
        "H10": ("AND3", "THRESHOLD_CONJUNCTION"),
        "H11": ("x3", "ADDRESSABLE_CONTEXT_READ"),
        "H12": ("AND3", "THRESHOLD_CONJUNCTION"),
        "H13": ("AND3", "THRESHOLD_CONJUNCTION"),
        "H14": ("x4", "PERSISTENT_STATE_READ"),
    }
    selections = {}
    for hid, (contract, pred) in rows.items():
        tt = tables[contract]
        best = minimum_exact(tt)
        cls = structural_class(best[1]) if best else None
        selections[hid] = {
            "contract": contract,
            "cost": best[0][0] if best else None,
            "tree": best[0][1] if best else None,
            "class": cls,
            "correct_class": cls == pred,
            "reads_x4": depends_exact(best[1], "x4") if best else None,
            "reads_x3": depends_exact(best[1], "x3") if best else None,
        }

    result = {
        "schema": "GMI833HFAMILY_TRANCHE_A_ORACLE_V1",
        "sigma": SIGMA,
        "budget": BUDGET,
        "selections": selections,
        "all_classes_match": all(s["correct_class"] for s in selections.values()),
        "note": "source-separated re-derivation; imports nothing from this "
                "package (enforced by the checker's ast scan)",
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print("ORACLE_RESULT_V1.json written: %d selections, all classes match=%s" %
          (len(selections), result["all_classes_match"]))


if __name__ == "__main__":
    main()
