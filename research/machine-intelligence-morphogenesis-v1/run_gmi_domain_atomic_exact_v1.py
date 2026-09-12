#!/usr/bin/env python3
"""Deterministic exact microscope for atomic GMI domain theorems.

Checks:
1. Arbitrary graph XOR constraints: consistency iff all fundamental-cycle
   syndromes vanish; consistent systems have exactly 2^c solutions; syndrome
   space size is 2^beta1.
2. Explicit constructor DAGs: iterative closure equals reachability closure and
   earliest synchronous construction rounds equal shortest prerequisite path
   depth for the one-prerequisite edge-rule subfamily.

No ML dependencies. Exact finite calibration only.
"""

from itertools import combinations, product
import json
from math import factorial


def component_count(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    c = 0
    for s in range(n):
        if seen[s]:
            continue
        c += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return c


def brute_solution_count(n, edges, labels):
    count = 0
    for x in product((0, 1), repeat=n):
        if all((x[u] ^ x[v]) == b for (u, v), b in zip(edges, labels)):
            count += 1
    return count


def fundamental_cycle_syndrome(n, edges, labels):
    parent = list(range(n))
    rank = [0] * n

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    tree = []
    non_tree = []
    for idx, (u, v) in enumerate(edges):
        if union(u, v):
            tree.append((idx, u, v))
        else:
            non_tree.append((idx, u, v))

    adj = [[] for _ in range(n)]
    for idx, u, v in tree:
        b = labels[idx]
        adj[u].append((v, b))
        adj[v].append((u, b))

    potential = [None] * n
    for s in range(n):
        if potential[s] is not None:
            continue
        potential[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for v, b in adj[u]:
                if potential[v] is None:
                    potential[v] = potential[u] ^ b
                    stack.append(v)

    return tuple(
        potential[u] ^ potential[v] ^ labels[idx]
        for idx, u, v in non_tree
    )


def check_relational_graphs(max_n=5):
    topology_count = 0
    labeled_instances = 0
    assignment_checks = 0
    consistent_instances = 0
    inconsistent_instances = 0
    max_beta1 = 0
    mismatches = 0

    per_n = {}
    for n in range(1, max_n + 1):
        possible_edges = list(combinations(range(n), 2))
        top_n = lab_n = chk_n = con_n = inc_n = 0

        for mask in range(1 << len(possible_edges)):
            edges = [
                possible_edges[i]
                for i in range(len(possible_edges))
                if (mask >> i) & 1
            ]
            m = len(edges)
            c = component_count(n, edges)
            beta1 = m - n + c
            max_beta1 = max(max_beta1, beta1)
            top_n += 1

            syndromes_seen = set()
            for labels in product((0, 1), repeat=m):
                syndrome = fundamental_cycle_syndrome(n, edges, labels)
                syndromes_seen.add(syndrome)
                solutions = brute_solution_count(n, edges, labels)
                expected_consistent = all(bit == 0 for bit in syndrome)

                if (solutions > 0) != expected_consistent:
                    mismatches += 1
                if solutions > 0 and solutions != 2 ** c:
                    mismatches += 1

                if solutions > 0:
                    con_n += 1
                else:
                    inc_n += 1
                lab_n += 1
                chk_n += 2 ** n

            if len(syndromes_seen) != 2 ** beta1:
                mismatches += 1

        topology_count += top_n
        labeled_instances += lab_n
        assignment_checks += chk_n
        consistent_instances += con_n
        inconsistent_instances += inc_n
        per_n[str(n)] = {
            "topologies": top_n,
            "labeled_instances": lab_n,
            "assignment_checks": chk_n,
            "consistent": con_n,
            "inconsistent": inc_n,
        }

    return {
        "n_min": 1,
        "n_max": max_n,
        "topologies": topology_count,
        "labeled_instances": labeled_instances,
        "assignment_checks": assignment_checks,
        "consistent_instances": consistent_instances,
        "inconsistent_instances": inconsistent_instances,
        "max_beta1": max_beta1,
        "mismatches": mismatches,
        "per_n": per_n,
    }


def closure_by_rounds(n, edges):
    available = {0}
    earliest = {0: 0}
    round_id = 0
    while True:
        new = {
            v for u, v in edges
            if u in available and v not in available
        }
        if not new:
            break
        round_id += 1
        for v in sorted(new):
            if v not in available:
                available.add(v)
                earliest[v] = round_id
    return available, tuple(earliest.get(i) for i in range(n))


def shortest_edge_depths(n, edges):
    # Edges are generated only with u < v, so the graph is a DAG.
    inf = None
    depth = [inf] * n
    depth[0] = 0
    for u in range(n):
        if depth[u] is None:
            continue
        for a, b in edges:
            if a == u:
                cand = depth[u] + 1
                if depth[b] is None or cand < depth[b]:
                    depth[b] = cand
    return tuple(depth)


def check_constructor_dags(max_n=6):
    systems = 0
    mismatches = 0
    per_n = {}
    largest_closure = 0
    largest_deadline = 0

    for n in range(1, max_n + 1):
        possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        count_n = 0
        for mask in range(1 << len(possible)):
            edges = [
                possible[i]
                for i in range(len(possible))
                if (mask >> i) & 1
            ]
            closure, rounds = closure_by_rounds(n, edges)
            depths = shortest_edge_depths(n, edges)
            depth_closure = {i for i, d in enumerate(depths) if d is not None}
            if closure != depth_closure or rounds != depths:
                mismatches += 1
            largest_closure = max(largest_closure, len(closure))
            finite_depths = [d for d in depths if d is not None]
            if finite_depths:
                largest_deadline = max(largest_deadline, max(finite_depths))
            count_n += 1
            systems += 1
        per_n[str(n)] = count_n

    return {
        "n_min": 1,
        "n_max": max_n,
        "dag_systems": systems,
        "largest_closure": largest_closure,
        "largest_earliest_round": largest_deadline,
        "mismatches": mismatches,
        "per_n": per_n,
    }


def main():
    relational = check_relational_graphs()
    constructive = check_constructor_dags()

    receipt = {
        "artifact": "GMI_DOMAIN_ATOMIC_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_domain_atomic_exact_v1.py",
        "relational_graph_xor": relational,
        "constructive_edge_rule_dags": constructive,
        "checks": {
            "cycle_syndrome_zero_iff_consistent": relational["mismatches"] == 0,
            "consistent_solution_count_is_2_pow_components": relational["mismatches"] == 0,
            "syndrome_count_is_2_pow_beta1": relational["mismatches"] == 0,
            "constructor_closure_equals_reachability": constructive["mismatches"] == 0,
            "earliest_round_equals_shortest_rule_depth": constructive["mismatches"] == 0,
        },
        "claim_ceiling": (
            "Exact finite theorem calibration only. Confirms generalized state/"
            "obstruction/deadline laws on registered finite families. It does not "
            "establish a new domain because matching symbolic reductions exist."
        ),
        "terminal": "DOMAIN_ATOMIC_EXACT_FINITE_GREEN",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
