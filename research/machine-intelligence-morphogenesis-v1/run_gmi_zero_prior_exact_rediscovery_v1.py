#!/usr/bin/env python3
import itertools
import json
import math
from pathlib import Path


def eval_poly(coeffs, x, q):
    y = 0
    for c in reversed(coeffs):
        y = (y * x + c) % q
    return y


def minimal_poly_degree(target, q):
    n = len(target)
    checked = 0
    for d in range(n):
        for coeffs in itertools.product(range(q), repeat=d + 1):
            checked += 1
            if all(eval_poly(coeffs, x, q) == target[x] for x in range(n)):
                return d, coeffs, checked
    raise AssertionError("finite interpolation search failed")


def coefficient_vs_cells(target, q, reuse=20, state_price=10, op_price=1):
    d, coeffs, checked = minimal_poly_degree(target, q)
    coefficient_cost = state_price * (d + 1) + op_price * reuse * (d + 1)
    cell_cost = state_price * len(target) + op_price * reuse
    if coefficient_cost < cell_cost:
        winner = "coefficient_program"
    elif cell_cost < coefficient_cost:
        winner = "indexed_cells"
    else:
        winner = "tie"
    return {
        "degree": d,
        "coefficients": list(coeffs),
        "candidate_coefficients_checked": checked,
        "coefficient_cost": coefficient_cost,
        "indexed_cell_cost": cell_cost,
        "winner": winner,
    }


def sequences_upto(length):
    yield ()
    for n in range(1, length + 1):
        yield from itertools.product((0, 1), repeat=n)


def parity_trace(seq):
    p = 0
    out = []
    for b in seq:
        p ^= b
        out.append(p)
    return tuple(out)


def current_bit_trace(seq):
    return tuple(seq)


def minimum_mealy_states(task, max_length=4, max_states=3):
    tests = list(sequences_upto(max_length))
    candidates = 0
    for k in range(1, max_states + 1):
        for trans in itertools.product(range(k), repeat=2 * k):
            for outfun in itertools.product((0, 1), repeat=2 * k):
                candidates += 1
                ok = True
                for seq in tests:
                    state = 0
                    got = []
                    for bit in seq:
                        got.append(outfun[2 * state + bit])
                        state = trans[2 * state + bit]
                    if tuple(got) != task(seq):
                        ok = False
                        break
                if ok:
                    return {
                        "states": k,
                        "transition": list(trans),
                        "output": list(outfun),
                        "candidates_checked": candidates,
                    }
    raise AssertionError("no finite machine found")


def choose_routing(required_sets, edge_cost=1.0, router_cost=0.5):
    union = set().union(*required_sets)
    avg = sum(map(len, required_sets)) / len(required_sets)
    static_cost = edge_cost * len(union)
    dynamic_cost = router_cost + edge_cost * avg
    winner = "input_conditioned_edges" if dynamic_cost < static_cost else "fixed_edges"
    return {
        "union_size": len(union),
        "average_required_edges": avg,
        "static_cost": static_cost,
        "dynamic_cost": dynamic_cost,
        "winner": winner,
    }


def is_circulant(a):
    n = len(a)
    return all(a[i][j] == a[0][(j - i) % n] for i in range(n) for j in range(n))


def choose_symmetry(a):
    n = len(a)
    free_cost = n * n
    tied_cost = n if is_circulant(a) else math.inf
    return {
        "circulant": is_circulant(a),
        "tied_parameter_cost": None if math.isinf(tied_cost) else tied_cost,
        "free_parameter_cost": free_cost,
        "winner": "cyclic_orbit_tying" if tied_cost < free_cost else "free_matrix",
    }


def gf2_rank(matrix):
    m = len(matrix)
    n = len(matrix[0])
    rows = []
    for i in range(m):
        row = 0
        for j in range(n):
            if matrix[i][j] & 1:
                row |= 1 << j
        rows.append(row)
    rank = 0
    for c in range(n):
        pivot = next((i for i in range(rank, m) if (rows[i] >> c) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(m):
            if i != rank and ((rows[i] >> c) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def choose_rank_state(matrix):
    m = len(matrix)
    n = len(matrix[0])
    rank = gf2_rank(matrix)
    factor_cost = rank * (m + n)
    full_cost = m * n
    return {
        "rank": rank,
        "factor_symbol_cost": factor_cost,
        "full_symbol_cost": full_cost,
        "winner": "rank_factorization" if factor_cost < full_cost else "full_matrix",
    }


def main():
    stable = [(2 * x + 1) % 5 for x in range(5)]
    volatile = [0, 0, 0, 0, 1]
    coefficients_positive = coefficient_vs_cells(stable, 5)
    coefficients_twin = coefficient_vs_cells(volatile, 5)
    assert coefficients_positive["winner"] == "coefficient_program"
    assert coefficients_twin["winner"] == "indexed_cells"

    recurrent_positive = minimum_mealy_states(parity_trace)
    recurrent_twin = minimum_mealy_states(current_bit_trace)
    assert recurrent_positive["states"] == 2
    assert recurrent_twin["states"] == 1

    routing_positive = choose_routing([{0}, {1}, {2}])
    routing_twin = choose_routing([{0}, {0}, {0}])
    assert routing_positive["winner"] == "input_conditioned_edges"
    assert routing_twin["winner"] == "fixed_edges"

    circulant = [
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
    ]
    broken = [row[:] for row in circulant]
    broken[0][0] ^= 1
    symmetry_positive = choose_symmetry(circulant)
    symmetry_twin = choose_symmetry(broken)
    assert symmetry_positive["winner"] == "cyclic_orbit_tying"
    assert symmetry_twin["winner"] == "free_matrix"

    rank_one = [
        [1, 0, 1, 0],
        [0, 0, 0, 0],
        [1, 0, 1, 0],
        [0, 0, 0, 0],
    ]
    full_rank = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
    rank_positive = choose_rank_state(rank_one)
    rank_twin = choose_rank_state(full_rank)
    assert rank_positive["winner"] == "rank_factorization"
    assert rank_twin["winner"] == "full_matrix"

    receipt = {
        "artifact": "GMI_ZERO_PRIOR_EXACT_REDISCOVERY_RECEIPT_V1",
        "status": "EXECUTED_EXACT_MICROSCOPE",
        "runner": "run_gmi_zero_prior_exact_rediscovery_v1.py",
        "cases": {
            "shared_state_vs_indexed_cells": {"positive": coefficients_positive, "negative_twin": coefficients_twin},
            "recurrent_state": {"positive": recurrent_positive, "negative_twin": recurrent_twin},
            "dependency_routing": {"positive": routing_positive, "negative_twin": routing_twin},
            "symmetry_tying": {"positive": symmetry_positive, "negative_twin": symmetry_twin},
            "rank_residual": {"positive": rank_positive, "negative_twin": rank_twin}
        },
        "checks": {
            "coefficient_property_recovers_and_flips": True,
            "recurrent_state_count_recovers_and_flips": True,
            "dynamic_routing_recovers_and_flips": True,
            "symmetry_tying_recovers_and_flips": True,
            "low_rank_state_recovers_and_flips": True
        },
        "claim_ceiling": "Exact toy zero-prior property rediscovery only. The primitive grammar is small and hand-registered; real family names/architectures are not claimed K4-closed.",
        "terminal": "ZERO_PRIOR_EXACT_PROPERTY_REDISCOVERY_GREEN"
    }

    out = Path(__file__).with_name("GMI_ZERO_PRIOR_EXACT_REDISCOVERY_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
