"""Independent complete syntax execution and leaf-output search; no DP imports."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


@lru_cache(None)
def shapes(remaining):
    trees = [None]
    for i in remaining:
        children = shapes(tuple(j for j in remaining if j != i))
        trees.extend((i, a, b) for a, b in product(children, repeat=2))
    return tuple(trees)


@lru_cache(None)
def executions(n, costs):
    rows = []
    for tree in shapes(tuple(range(n))):
        leaves, charges = [], []
        for x in range(1 << n):
            cursor, path, cost = tree, (), F(0)
            while cursor is not None:
                i, a, b = cursor
                bit = (x >> i) & 1
                cost += costs[i]
                path += (bit,)
                cursor = b if bit else a
            leaves.append(path)
            charges.append(cost)
        groups = tuple(tuple(x for x, leaf in enumerate(leaves) if leaf == path)
                       for path in sorted(set(leaves)))
        rows.append((groups, tuple(charges), tree))
    return tuple(rows)


def oracle(actions, outputs, costs):
    profiles, admitted, label_checks = set(), 0, 0
    syntax = executions(len(costs), tuple(map(F, costs)))
    for groups, work, _ in syntax:
        valid = True
        for group in groups:
            compatible_label = False
            for action in range(outputs):
                label_checks += 1
                if all(actions[x] & (1 << action) for x in group):
                    compatible_label = True
                    break
            if not compatible_label:
                valid = False
                break
        if valid:
            profiles.add(work)
            admitted += 1
    return {"profiles": frozenset(profiles), "shapes": len(syntax),
            "admitted": admitted, "leaf_label_checks": label_checks}


def execute_constructed(tree, x, costs):
    seen, cost = set(), F(0)
    while tree[0] == "ask":
        _, i, left, right = tree
        if i in seen:
            raise ValueError("constructed tree repeats a coordinate")
        seen.add(i)
        cost += costs[i]
        tree = right if (x >> i) & 1 else left
    if tree[0] != "emit":
        raise ValueError("unknown terminal instruction")
    return tree[1], cost


def pair_graph(actions):
    return tuple(bool(a & b) for a in actions for b in actions)


def equality_partition(actions):
    return tuple(a == b for a in actions for b in actions)


def graph_gamma(actions, n):
    # Generate cells by their literal lists, independently of the model's mask table.
    result = []
    for partial in product((-1, 0, 1), repeat=n):
        worlds = [x for x in range(1 << n) if all(
            bit == -1 or ((x >> i) & 1) == bit for i, bit in enumerate(partial))]
        result.append(all(actions[x] & actions[y] for x in worlds for y in worlds))
    return tuple(result)
