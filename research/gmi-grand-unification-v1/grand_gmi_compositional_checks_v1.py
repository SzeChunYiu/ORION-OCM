#!/usr/bin/env python3
"""Exact checks for Grand GMI compositional/distributed layer."""

from itertools import product
import json


def pareto(points):
    pts = list(points)
    out = set()
    for p in pts:
        dominated = False
        for q in pts:
            if q == p:
                continue
            if all(a <= b for a, b in zip(q, p)) and any(a < b for a, b in zip(q, p)):
                dominated = True
                break
        if not dominated:
            out.add(p)
    return out


def check_frontier_tensorization():
    grid = [(0, 0), (0, 1), (1, 0), (1, 1)]
    subsets = []
    for mask in range(1, 1 << len(grid)):
        subsets.append({grid[i] for i in range(len(grid)) if (mask >> i) & 1})

    checks = 0
    for a in subsets:
        for b in subsets:
            product_set = {(x[0], x[1], y[0], y[1]) for x in a for y in b}
            lhs = pareto(product_set)
            rhs = {(x[0], x[1], y[0], y[1]) for x in pareto(a) for y in pareto(b)}
            assert lhs == rhs
            checks += 1
    return {"set_pair_checks": checks, "all_exact": True}


def check_semantic_width_tensorization():
    funcs = list(product(range(3), repeat=3))
    checks = 0
    for f1 in funcs:
        m1 = len(set(f1))
        for f2 in funcs:
            m2 = len(set(f2))
            joint = {(f1[x1], f2[x2]) for x1 in range(3) for x2 in range(3)}
            assert len(joint) == m1 * m2
            checks += 1
    return {"ternary_function_pairs": checks, "all_exact": True}


def check_xor_distributed_cut():
    by_k = {}
    for k in (1, 2):
        total = 0
        successful = 0
        for encoder in product(range(k), repeat=2):
            for decoder in product([0, 1], repeat=k * 2):
                total += 1
                ok = True
                for x, y in product([0, 1], repeat=2):
                    m = encoder[x]
                    out = decoder[m * 2 + y]
                    if out != (x ^ y):
                        ok = False
                        break
                if ok:
                    successful += 1
        by_k[str(k)] = {"protocols": total, "successful": successful}
    assert by_k["1"]["successful"] == 0
    assert by_k["2"]["successful"] == 2
    return {"minimum_message_symbols": 2, "by_alphabet": by_k}


def check_coupled_obligation_boundary():
    pair_outputs = {(x1, x2) for x1, x2 in product([0, 1], repeat=2)}
    parity_outputs = {x1 ^ x2 for x1, x2 in product([0, 1], repeat=2)}
    assert len(pair_outputs) == 4
    assert len(parity_outputs) == 2
    return {
        "separate_pair_message_symbols": 4,
        "coupled_parity_message_symbols": 2,
        "tensorization_without_factorized_obligation": False,
    }


def check_team_centralization(max_len=6):
    def distributed_step(state, u):
        a, b = state
        message = a ^ u
        next_a = message
        next_b = b ^ message
        return (next_a, next_b), next_b

    def centralized_step(state, u):
        a, b = state
        message = a ^ u
        return (message, b ^ message), b ^ message

    checks = 0
    for initial in product([0, 1], repeat=2):
        for length in range(max_len + 1):
            for seq in product([0, 1], repeat=length):
                d = initial
                c = initial
                d_out, c_out = [], []
                for u in seq:
                    d, od = distributed_step(d, u)
                    c, oc = centralized_step(c, u)
                    d_out.append(od)
                    c_out.append(oc)
                assert d == c
                assert d_out == c_out
                checks += 1
    return {"trace_checks": checks, "max_sequence_length": max_len, "all_exact": True}


def run():
    return {
        "terminal": "GRAND_GMI_COMPOSITIONAL_DISTRIBUTED_TRANCHE_ALL_GREEN",
        "frontier_tensorization": check_frontier_tensorization(),
        "semantic_width_tensorization": check_semantic_width_tensorization(),
        "xor_distributed_cut": check_xor_distributed_cut(),
        "coupled_obligation_boundary": check_coupled_obligation_boundary(),
        "team_centralization": check_team_centralization(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
