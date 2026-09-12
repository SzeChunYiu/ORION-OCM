#!/usr/bin/env python3
from itertools import product
import json


def partition_from_matrix(matrix, obs_subset):
    sig_to_block = {}
    for h, row in enumerate(matrix):
        sig = tuple(row[q] for q in obs_subset)
        sig_to_block.setdefault(sig, []).append(h)
    blocks = tuple(sorted((tuple(v) for v in sig_to_block.values()), key=lambda b: b[0]))
    cls = {}
    for i, block in enumerate(blocks):
        for h in block:
            cls[h] = i
    return blocks, cls


def partition_checks():
    H = 4
    Q = 3
    nested = []
    for mask2 in range(1 << Q):
        for mask1 in range(1 << Q):
            if mask1 & ~mask2 == 0:
                o1 = tuple(i for i in range(Q) if mask1 >> i & 1)
                o2 = tuple(i for i in range(Q) if mask2 >> i & 1)
                nested.append((o1, o2))
    checks = 0
    strict = 0
    for bits in product((0, 1), repeat=H * Q):
        matrix = [bits[h * Q : (h + 1) * Q] for h in range(H)]
        for o1, o2 in nested:
            b1, c1 = partition_from_matrix(matrix, o1)
            b2, c2 = partition_from_matrix(matrix, o2)
            for i in range(H):
                for j in range(H):
                    if c2[i] == c2[j] and c1[i] != c1[j]:
                        raise AssertionError("refinement violation")
            mapping = {}
            for fi, block in enumerate(b2):
                ids = {c1[h] for h in block}
                if len(ids) != 1:
                    raise AssertionError("quotient map not well-defined")
                mapping[fi] = next(iter(ids))
            if set(mapping.values()) != set(range(len(b1))):
                raise AssertionError("quotient map not surjective")
            if len(b2) < len(b1):
                raise AssertionError("semantic cardinality decreased")
            strict += int(len(b2) > len(b1))
            checks += 1
    return {
        "matrices": 2 ** (H * Q),
        "nested_pairs_per_matrix": len(nested),
        "checks": checks,
        "strict_refinements": strict,
    }


def quotient_compatibility():
    classes = {"p0": "X", "p1": "X", "q0": "Y", "r0": "Z"}
    good = {"p0": "q0", "p1": "q0", "q0": "q0", "r0": "r0"}
    bad = {"p0": "q0", "p1": "r0", "q0": "q0", "r0": "r0"}

    def descends(transition):
        by_class = {}
        for state, cls in classes.items():
            by_class.setdefault(cls, set()).add(classes[transition[state]])
        return all(len(v) == 1 for v in by_class.values()), {
            k: sorted(v) for k, v in sorted(by_class.items())
        }

    return {"compatible": descends(good), "syntax_sensitive": descends(bad)}


def reachable_by_sequences(actions, delta, start, budget):
    reached = {start}
    for length in range(1, budget + 1):
        for seq in product(actions, repeat=length):
            state = start
            for action in seq:
                state = delta(state, action)
            reached.add(state)
    return reached


def reachable_bfs(actions, delta, start, budget):
    reached = {start}
    frontier = {start}
    for _ in range(budget):
        nxt = {delta(state, action) for state in frontier for action in actions}
        reached |= nxt
        frontier = nxt
    return reached


def reachability_checks():
    actions0 = ("stay", "inc1", "inc2")

    def delta0(state, action):
        if action == "stay":
            return state
        return min(3, state + (1 if action == "inc1" else 2))

    base = []
    for budget in range(5):
        seq = reachable_by_sequences(actions0, delta0, 0, budget)
        bfs = reachable_bfs(actions0, delta0, 0, budget)
        if seq != bfs:
            raise AssertionError("base reachability mismatch")
        base.append({"budget": budget, "reachable": sorted(seq)})

    actions1 = ("apply", "switch")

    def delta1(state, action):
        morphology, rule = state
        if action == "switch":
            return (morphology, "fast" if rule == "slow" else "slow")
        return (min(3, morphology + (1 if rule == "slow" else 2)), rule)

    lifted = []
    for budget in range(5):
        seq = reachable_by_sequences(actions1, delta1, (0, "slow"), budget)
        bfs = reachable_bfs(actions1, delta1, (0, "slow"), budget)
        if seq != bfs:
            raise AssertionError("lifted reachability mismatch")
        lifted.append(
            {
                "budget": budget,
                "reachable_count": len(seq),
                "reaches_target": any(m == 3 for m, _ in seq),
            }
        )
    return {"base": base, "lifted": lifted}


def run():
    return {
        "terminal": "GRAND_GMI_RECURSIVE_MORPHOGENESIS_TRANCHE_ALL_GREEN",
        "determinism": "exhaustive/no-rng",
        "semantic_state_refinement": partition_checks(),
        "quotient_compatibility": quotient_compatibility(),
        "reachability": reachability_checks(),
    }


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
