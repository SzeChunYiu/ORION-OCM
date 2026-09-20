#!/usr/bin/env python3
"""Exact finite verification; paper/Lean proofs carry universal claims."""
from fractions import Fraction as F
from itertools import permutations, product
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def need(x, msg):
    if not x:
        raise RuntimeError(msg)

def distances(n, edges):
    if any(w < 0 for w in edges.values()):
        raise ValueError('NONNEGATIVE_COST_REQUIRED')
    d = [[None for _ in range(n)] for _ in range(n)]
    for a in range(n):
        d[a][a] = 0
    for (a, b), w in edges.items():
        d[a][b] = w if d[a][b] is None else min(d[a][b], w)
    for k in range(n):
        for a in range(n):
            for b in range(n):
                if d[a][k] is not None and d[k][b] is not None:
                    v = d[a][k] + d[k][b]
                    d[a][b] = v if d[a][b] is None else min(d[a][b], v)
    return d

def path_oracle(n, edges, a, b):
    # Independent route: all distinct-vertex paths; nonnegative cycles removable.
    if a == b:
        return 0
    costs = []
    middle = [v for v in range(n) if v not in (a, b)]
    for k in range(len(middle) + 1):
        for p in permutations(middle, k):
            nodes = (a,) + p + (b,)
            pairs = list(zip(nodes, nodes[1:]))
            if all(edge in edges for edge in pairs):
                costs.append(sum(edges[edge] for edge in pairs))
    return min(costs) if costs else None

def frontier(vectors):
    v = set(vectors)
    return {x for x in v if not any(y != x and all(a <= b for a, b in zip(y, x)) for y in v)}

def graph_census():
    pairs = [(a, b) for a in range(3) for b in range(3) if a != b]
    count = 0
    for values in product((None, 0, 1, 2), repeat=6):
        edges = {p: v for p, v in zip(pairs, values) if v is not None}
        d = distances(3, edges)
        for a, b in product(range(3), repeat=2):
            need(d[a][b] == path_oracle(3, edges, a, b), 'PATH_DISAGREEMENT')
        for a, b, c in product(range(3), repeat=3):
            if d[a][b] is not None and d[b][c] is not None:
                need(d[a][c] is not None and d[a][c] <= d[a][b] + d[b][c], 'TRIANGLE')
        # A true relabeling, including edges; not a second copy of the same cost list.
        perm = (2, 0, 1)
        renamed = {(perm[a], perm[b]): w for (a, b), w in edges.items()}
        dr = distances(3, renamed)
        for a, b in product(range(3), repeat=2):
            need(dr[perm[a]][perm[b]] == d[a][b], 'RELABEL')
        count += 1
    return count

def hostiles():
    caught = []
    try:
        distances(2, {(0, 1): -1})
    except ValueError:
        caught.append('negative_cost_rejected')
    e = {(0, 1): 1, (1, 2): 2, (0, 2): 9}
    d = distances(3, e)
    need(d[0][2] == 3 and d[2][0] is None, 'DIRECTION_AND_COMPOSITION')
    need(e[(0, 2)] > d[0][2], 'DIRECT_ONLY_MUTANT_NOT_DETECTED')
    caught.append('direct_edge_is_not_shortest_path')
    need(distances(3, {**e, (0, 2): 0})[0][2] != d[0][2], 'COST_MUTANT')
    caught.append('cost_changed_relabel_rejected')
    need(d[2][0] != d[0][2], 'SYMMETRY_MUTANT')
    caught.append('symmetry_rejected')
    # Positive coordinate swap/scaling is an order isomorphism on the image.
    v = {(1, 4), (2, 2), (4, 1), (4, 4)}
    phi = lambda x: (3 * x[1], 2 * x[0])
    need(frontier({phi(x) for x in v}) == {phi(x) for x in frontier(v)}, 'PARETO_TRANSPORT')
    pair = {(0, 1), (1, 0)}
    proj = lambda x: (x[0],)
    need(frontier({proj(x) for x in pair}) != {proj(x) for x in frontier(pair)}, 'ORDER_REFLECTION')
    caught.append('monotone_projection_not_order_isomorphism')
    # Strictly dominated cost can tie for a nonnegative but nonpositive weight.
    need(frontier({(0, 0), (0, 1)}) == {(0, 0)}, 'ZERO_WEIGHT_CONTROL')
    weight = (1, 0)
    scores = [sum(a*b for a, b in zip(weight, x)) for x in ((0, 0), (0, 1))]
    need(scores == [0, 0], 'ZERO_WEIGHT_TIE')
    caught.append('nonnegative_scalarization_can_tie_dominated')
    # Exact finite instances are witnesses only; infinite nonattainment is G3.
    for n in range(1, 101):
        need(F(1, n + 1) < F(1, n), 'STRICT_DESCENT')
    caught.append('positive_cost_does_not_imply_attained_infimum')
    need(len(caught) == 7, 'HOSTILE_COVERAGE')
    return caught

def main():
    out = {'schema': 'R5_GEOMETRY_REPAIR_V2', 'round_closure': 'OPEN',
           'claim': 'CONDITIONAL_RESOURCE_GEOMETRY_WITH_EXACT_FINITE_CHECKS',
           'graphs': graph_census(), 'ordered_pairs_per_graph': 9,
           'hostiles': hostiles(), 'proof_scope': {'Lean': 'natural_cost_minimizer_identity_triangle_and_order_transport',
                                                'paper': 'real_infimum_and_Pareto_existence_conditions'},
           'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(ROOT.iterdir()) if p.suffix in ('.py', '.lean', '.md')}}
    print(json.dumps(out, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
