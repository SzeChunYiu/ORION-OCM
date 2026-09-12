#!/usr/bin/env python3
import itertools
import json
from pathlib import Path


def eval_poly(coeffs, x, q):
    y = 0
    for c in reversed(coeffs):
        y = (y * x + c) % q
    return y


def minimal_poly_degree(target, q):
    for d in range(len(target)):
        for coeffs in itertools.product(range(q), repeat=d + 1):
            if all(eval_poly(coeffs, x, q) == target[x] for x in range(len(target))):
                return d
    raise AssertionError("interpolation search failed")


def coefficient_winner(target, q=5, reuse=20, state_price=10, op_price=1):
    d = minimal_poly_degree(target, q)
    coeff_cost = state_price * (d + 1) + op_price * reuse * (d + 1)
    cell_cost = state_price * len(target) + op_price * reuse
    if coeff_cost < cell_cost:
        winner = "coefficient_program"
    elif cell_cost < coeff_cost:
        winner = "indexed_cells"
    else:
        winner = "tie"
    return d, winner


def sequences_upto(length):
    yield ()
    for n in range(1, length + 1):
        yield from itertools.product((0, 1), repeat=n)


def minimum_mealy_states(task, max_length=4, max_states=2):
    tests = list(sequences_upto(max_length))
    for k in range(1, max_states + 1):
        for trans in itertools.product(range(k), repeat=2 * k):
            for outfun in itertools.product((0, 1), repeat=2 * k):
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
                    return k
    raise AssertionError("no machine found")


def routing_winner(required_sets, edge_cost=1.0, router_cost=0.5):
    union = set().union(*required_sets)
    avg = sum(map(len, required_sets)) / len(required_sets)
    static = edge_cost * len(union)
    dynamic = router_cost + edge_cost * avg
    return "input_conditioned_edges" if dynamic < static else "fixed_edges"


def permute_matrix(a, p):
    n = len(a)
    b = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            b[p[i]][p[j]] = a[i][j]
    return b


def reminted_cyclic_generator(p):
    n = len(p)
    g = [None] * n
    for i in range(n):
        g[p[i]] = p[(i + 1) % n]
    return g


def invariant_under_generator(a, g):
    n = len(a)
    return all(a[g[i]][g[j]] == a[i][j] for i in range(n) for j in range(n))


def pair_orbit_count(g):
    n = len(g)
    seen = set()
    count = 0
    for i in range(n):
        for j in range(n):
            if (i, j) in seen:
                continue
            count += 1
            x = (i, j)
            while x not in seen:
                seen.add(x)
                x = (g[x[0]], g[x[1]])
    return count


def gf2_rank(a):
    m = len(a)
    n = len(a[0])
    rows = []
    for i in range(m):
        row = 0
        for j in range(n):
            if a[i][j] & 1:
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


def permute_rows_cols(a, pr, pc):
    m = len(a)
    n = len(a[0])
    b = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            b[pr[i]][pc[j]] = a[i][j]
    return b


def main():
    receipt = {
        "artifact": "GMI_ZERO_PRIOR_REMINT_INVARIANCE_RECEIPT_V1",
        "status": "EXECUTED_EXACT_REMINT_MICROSCOPE",
        "runner": "run_gmi_zero_prior_remint_invariance_v1.py",
        "checks": {},
    }

    # 1. Affine input/output remints over GF(5).
    stable = [(2 * x + 1) % 5 for x in range(5)]
    volatile = [0, 0, 0, 0, 1]
    coefficient_cases = 0
    for a in range(1, 5):
        a_inv = pow(a, -1, 5)
        for b in range(5):
            for c in range(1, 5):
                for d in range(5):
                    for target, expected_degree, expected_winner in (
                        (stable, 1, "coefficient_program"),
                        (volatile, 4, "indexed_cells"),
                    ):
                        reminted = []
                        for xp in range(5):
                            x = (a_inv * (xp - b)) % 5
                            reminted.append((c * target[x] + d) % 5)
                        degree, winner = coefficient_winner(reminted)
                        assert degree == expected_degree
                        assert winner == expected_winner
                        coefficient_cases += 1
    receipt["coefficient_memory_affine_remints"] = {
        "cases": coefficient_cases,
        "mismatches": 0,
    }
    receipt["checks"]["coefficient_memory_winner_invariant"] = True

    # 2. Input/output bit remints for recurrent tasks.
    recurrent_cases = 0
    for input_flip, output_flip in itertools.product((0, 1), repeat=2):
        def parity_task(seq, inf=input_flip, outf=output_flip):
            p = 0
            out = []
            for observed in seq:
                p ^= observed ^ inf
                out.append(p ^ outf)
            return tuple(out)

        def current_task(seq, inf=input_flip, outf=output_flip):
            return tuple((observed ^ inf) ^ outf for observed in seq)

        assert minimum_mealy_states(parity_task) == 2
        assert minimum_mealy_states(current_task) == 1
        recurrent_cases += 2
    receipt["recurrent_label_remints"] = {"cases": recurrent_cases, "mismatches": 0}
    receipt["checks"]["recurrent_state_count_invariant"] = True

    # 3. Input and edge label permutations for routing.
    routing_cases = 0
    for ip in itertools.permutations(range(3)):
        for ep in itertools.permutations(range(3)):
            positive = [None] * 3
            for i in range(3):
                positive[ip[i]] = {ep[i]}
            negative = [{ep[0]} for _ in range(3)]
            assert routing_winner(positive) == "input_conditioned_edges"
            assert routing_winner(negative) == "fixed_edges"
            routing_cases += 2
    receipt["routing_permutation_remints"] = {"cases": routing_cases, "mismatches": 0}
    receipt["checks"]["routing_winner_invariant"] = True

    # 4. Coordinate conjugation of target and cyclic group action.
    positive_matrix = [
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
    ]
    negative_matrix = [row[:] for row in positive_matrix]
    negative_matrix[0][0] ^= 1
    symmetry_cases = 0
    for p in itertools.permutations(range(4)):
        g = reminted_cyclic_generator(p)
        assert pair_orbit_count(g) == 4
        assert invariant_under_generator(permute_matrix(positive_matrix, p), g)
        assert not invariant_under_generator(permute_matrix(negative_matrix, p), g)
        symmetry_cases += 2
    receipt["symmetry_conjugation_remints"] = {"cases": symmetry_cases, "mismatches": 0}
    receipt["checks"]["symmetry_property_invariant"] = True

    # 5. Row/column permutation remints preserve rank/winner.
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
    rank_cases = 0
    for pr in itertools.permutations(range(4)):
        for pc in itertools.permutations(range(4)):
            assert gf2_rank(permute_rows_cols(rank_one, pr, pc)) == 1
            assert gf2_rank(permute_rows_cols(full_rank, pr, pc)) == 4
            rank_cases += 2
    receipt["rank_coordinate_remints"] = {"cases": rank_cases, "mismatches": 0}
    receipt["checks"]["rank_property_invariant"] = True

    receipt["claim_ceiling"] = (
        "Exact finite remint invariance for the small hand-registered property grammar only. "
        "Does not establish broad real-family K4 closure or grammar/search neutrality."
    )
    receipt["terminal"] = "ZERO_PRIOR_EXACT_REMINT_INVARIANCE_GREEN"

    out = Path(__file__).with_name("GMI_ZERO_PRIOR_REMINT_INVARIANCE_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
