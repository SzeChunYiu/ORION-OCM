#!/usr/bin/env python3
"""Route B: source-separated oracle for gmi-833-h-family-tranche-d-v1.

R10 independent search: a second implementation, source-separated from the
primary executor, re-derives the family-blind selections WITHOUT importing
this package (enforced by the checker's ast scan and by `import none of
grammar_td_v1 / tranche_d_v1`). It writes ORACLE_RESULT_V1.json with its own
tuple-truth-table semantics, its own evaluator, and its own exhaustive
minimum-cost search over the SAME frozen grammar specification.

    python3 -I -B independent_oracle_v1.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ORACLE_RESULT_V1.json")

BUDGET = 5
LEAVES = ("0", "1", "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7")
CONST = {"0": 0, "1": 1}


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


ALL_TREES = oracle_build(BUDGET)
MEANING_CACHE = {}


def oracle_meaning(tree):
    key = oracle_render(tree)
    if key in MEANING_CACHE:
        return MEANING_CACHE[key]
    vals = []
    for m in range(256):
        env = {}
        for i in range(8):
            env["x%d" % i] = (m >> i) & 1
        vals.append(oracle_value(tree, env))
    MEANING_CACHE[key] = tuple(vals)
    return MEANING_CACHE[key]


def oracle_render(tree):
    if tree[0] == "LEAF":
        return tree[1]
    return tree[0] + "(" + ",".join(oracle_render(k) for k in tree[1:]) + ")"


def oracle_nodes(tree):
    if tree[0] == "LEAF":
        return 1
    return 1 + sum(oracle_nodes(k) for k in tree[1:])


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
    """Exact: does the truth table move when `leaf` flips (full-cube eval)."""
    for m in range(256):
        env = {}
        for i in range(8):
            env["x%d" % i] = (m >> i) & 1
        env2 = dict(env)
        env2[leaf] = 1 - env2[leaf]
        if oracle_value(tree, env) != oracle_value(tree, env2):
            return True
    return False


def _triple_shape(tree, op):
    if tree[0] != op or len(tree) != 3:
        return False
    ops = [k for k in tree[1:] if k[0] == op]
    leaves = [k for k in tree[1:] if k[0] == "LEAF" and k[1] not in ("0", "1")]
    if len(ops) != 1 or len(leaves) != 1:
        return False
    inner = ops[0]
    if inner[0] != op or len(inner) != 3:
        return False
    il = [k for k in inner[1:] if k[0] == "LEAF" and k[1] not in ("0", "1")]
    if len(il) != 2:
        return False
    return len({leaves[0][1], il[0][1], il[1][1]}) == 3


def structural_class(tree):
    """Own post-hoc classifier with the frozen priority order."""
    if depends_exact(tree, "x5"):
        return "STOCHASTIC_SOURCE_CHANNEL"
    if depends_exact(tree, "x6"):
        return "UPDATE_FEEDBACK_CHANNEL"
    if depends_exact(tree, "x7"):
        return "EXTERNAL_PEER_TOOL_CHANNEL"
    if depends_exact(tree, "x4"):
        return "PERSISTENT_STATE_READ"
    if depends_exact(tree, "x3"):
        return "ADDRESSABLE_CONTEXT_READ"
    if _triple_shape(tree, "XOR"):
        return "TRIPLE_PARITY"
    if _triple_shape(tree, "AND"):
        return "CONJUNCTIVE_SIEVE"
    if tree[0] == "LEAF" and tree[1] not in ("0", "1"):
        return "DIRECT_COORDINATE_READ"
    if tree[0] == "AND":
        return "CONJUNCTIVE_SIEVE"
    if tree[0] == "XOR":
        return "PARITY_SIEVE"
    return "BOOLEAN_COMPOSITION"


def contract_tables():
    em = list(range(256))
    def tt(bit):
        return tuple((m >> bit) & 1 for m in em)
    return {
        "XOR(x0,x5)": tuple(((m & 1) ^ ((m >> 5) & 1)) for m in em),
        "AND(x0,x7)": tuple(((m & 1) & ((m >> 7) & 1)) for m in em),
        "AND(x2,x7)": tuple((((m >> 2) & 1) & ((m >> 7) & 1)) for m in em),
        "XOR(x1,x7)": tuple((((m >> 1) & 1) ^ ((m >> 7) & 1)) for m in em),
        "XOR(XOR(x0,x1),x2)": tuple((((m & 1) ^ ((m >> 1) & 1)) ^ ((m >> 2) & 1)) for m in em),
        "AND(AND(x0,x1),x2)": tuple((((m & 1) & ((m >> 1) & 1)) & ((m >> 2) & 1)) for m in em),
        "AND(x0,x6)": tuple(((m & 1) & ((m >> 6) & 1)) for m in em),
        "XOR(x0,x6)": tuple(((m & 1) ^ ((m >> 6) & 1)) for m in em),
        "AND(x1,x6)": tuple((((m >> 1) & 1) & ((m >> 6) & 1)) for m in em),
        "XOR(x0,x7)": tuple(((m & 1) ^ ((m >> 7) & 1)) for m in em),
        "XOR(x0,x1)": tuple(((m & 1) ^ ((m >> 1) & 1)) for m in em),
        "AND(x0,x1)": tuple(((m & 1) & ((m >> 1) & 1)) for m in em),
        "x4": tt(4),
    }


ROWS = {
    "H35": ("XOR(x0,x5)", "STOCHASTIC_SOURCE_CHANNEL"),
    "H36": ("AND(x0,x7)", "EXTERNAL_PEER_TOOL_CHANNEL"),
    "H37": ("AND(x2,x7)", "EXTERNAL_PEER_TOOL_CHANNEL"),
    "H38": ("XOR(x1,x7)", "EXTERNAL_PEER_TOOL_CHANNEL"),
    "H39": ("XOR(XOR(x0,x1),x2)", "TRIPLE_PARITY"),
    "H40": ("AND(x0,x6)", "UPDATE_FEEDBACK_CHANNEL"),
    "H41": ("XOR(x0,x6)", "UPDATE_FEEDBACK_CHANNEL"),
    "H42": ("AND(x1,x6)", "UPDATE_FEEDBACK_CHANNEL"),
    "H43": ("XOR(x0,x7)", "EXTERNAL_PEER_TOOL_CHANNEL"),
}

# Matched negative control contracts (rejected as the predicted class).
TWINS = {
    "H35": "XOR(x0,x1)", "H36": "AND(x0,x1)", "H37": "AND(x0,x1)",
    "H38": "XOR(x0,x1)", "H39": "AND(AND(x0,x1),x2)", "H40": "AND(x0,x1)",
    "H41": "XOR(x0,x1)", "H42": "x4", "H43": "AND(x0,x1)",
}


def main():
    tables = contract_tables()
    selections = {}
    for hid, (contract, pred) in ROWS.items():
        best = minimum_exact(tables[contract])
        cls = structural_class(best[1]) if best else None
        twin = minimum_exact(tables[TWINS[hid]])
        twin_cls = structural_class(twin[1]) if twin else None
        selections[hid] = {
            "contract": contract,
            "cost": best[0][0] if best else None,
            "tree": best[0][1] if best else None,
            "class": cls,
            "correct_class": cls == pred,
            "twin_class": twin_cls,
            "twin_rejected": twin_cls != cls,
        }

    result = {
        "schema": "GMI833HFAMILY_TRANCHE_D_ORACLE_V1",
        "sigma": "SIGMA_TD01..SIGMA_TD09",
        "budget": BUDGET,
        "selections": selections,
        "all_classes_match": all(s["correct_class"] for s in selections.values()),
        "all_twins_rejected": all(s["twin_rejected"] for s in selections.values()),
        "note": "source-separated re-derivation; imports nothing from this "
                "package (enforced by the checker's ast scan)",
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print("ORACLE_RESULT_V1.json written: %d selections, all classes match=%s, "
          "all twins rejected=%s" %
          (len(selections), result["all_classes_match"], result["all_twins_rejected"]))


if __name__ == "__main__":
    main()
