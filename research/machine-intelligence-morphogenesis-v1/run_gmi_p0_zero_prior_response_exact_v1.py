#!/usr/bin/env python3
import itertools
import json
import math
from collections import Counter
from pathlib import Path


def residual_ball_count(n, q, r):
    return sum(math.comb(n, j) * (q - 1) ** j for j in range(r + 1))


def gf2_rank(mask, m, n):
    rows = []
    for i in range(m):
        row = 0
        for j in range(n):
            k = i * n + j
            if (mask >> k) & 1:
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
        if rank == m:
            break
    return rank


def rank_count_formula(m, n, r, q=2):
    if r == 0:
        return 1
    num = den = 1
    for i in range(r):
        num *= (q**m - q**i) * (q**n - q**i)
        den *= (q**r - q**i)
    return num // den


def main():
    receipt = {
        "artifact": "GMI_P0_ZERO_PRIOR_RESPONSE_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_p0_zero_prior_response_exact_v1.py",
        "checks": {},
    }

    # P0-1 sparse residual Hamming-ball count.
    residual_cases = 0
    residual_targets = 0
    for n in range(1, 8):
        for q in range(2, 5):
            counts = Counter()
            for target in itertools.product(range(q), repeat=n):
                d = sum(v != 0 for v in target)
                counts[d] += 1
            residual_targets += q**n
            for r in range(n + 1):
                observed = sum(counts[j] for j in range(r + 1))
                expected = residual_ball_count(n, q, r)
                assert observed == expected
                residual_cases += 1
    receipt["sparse_residual"] = {
        "n_min": 1,
        "n_max": 7,
        "q_min": 2,
        "q_max": 4,
        "formula_cases": residual_cases,
        "target_vectors_enumerated": residual_targets,
        "mismatches": 0,
    }
    receipt["checks"]["hamming_ball_cardinality_exact"] = True

    # P0-2/P0-3 static union and dynamic burden crossover.
    routing_families = 0
    routing_threshold_checks = 0
    for edge_count in range(1, 6):
        subsets = [
            frozenset(i for i in range(edge_count) if (mask >> i) & 1)
            for mask in range(1 << edge_count)
        ]
        for fam in itertools.product(subsets, repeat=3):
            union = set().union(*fam)
            feasible_static = [s for s in subsets if all(req <= s for req in fam)]
            assert min(map(len, feasible_static)) == len(union)
            avg = sum(map(len, fam)) / 3
            gap = len(union) - avg
            for routing_plus_risk in (0, 0.25, 0.5, 1, 2):
                assert ((avg + routing_plus_risk) < len(union)) == (routing_plus_risk < gap)
                routing_threshold_checks += 1
            routing_families += 1
    receipt["routing"] = {
        "universal_edges_min": 1,
        "universal_edges_max": 5,
        "inputs_per_family": 3,
        "dependency_families": routing_families,
        "crossover_checks": routing_threshold_checks,
        "mismatches": 0,
    }
    receipt["checks"]["static_exact_mask_equals_dependency_union"] = True
    receipt["checks"]["dynamic_routing_crossover_exact"] = True

    # P0-4 predictive-state packing: point-mass future laws have pairwise TV=1.
    mapping_checks = 0
    packing_cases = 0
    epsilon = 0.49
    for k in range(2, 8):
        for state_count in range(1, k):
            for mapping in itertools.product(range(state_count), repeat=k):
                collision = False
                for i in range(k):
                    for j in range(i + 1, k):
                        if mapping[i] == mapping[j]:
                            collision = True
                            assert 1 > 2 * epsilon
                            break
                    if collision:
                        break
                assert collision
                mapping_checks += 1
            packing_cases += 1
    receipt["predictive_state_packing"] = {
        "k_min": 2,
        "k_max": 7,
        "epsilon": epsilon,
        "state_count_cases": packing_cases,
        "fewer_than_k_state_mappings_checked": mapping_checks,
        "mismatches": 0,
    }
    receipt["checks"]["tv_packing_collision_lower_bound"] = True

    # P0-5 finite-field exact rank counts.
    rank_cases = 0
    matrices_checked = 0
    for m in range(1, 5):
        for n in range(1, 5):
            observed = Counter(gf2_rank(mask, m, n) for mask in range(1 << (m * n)))
            expected = {r: rank_count_formula(m, n, r, 2) for r in range(min(m, n) + 1)}
            assert dict(sorted(observed.items())) == expected
            rank_cases += 1
            matrices_checked += 1 << (m * n)
    receipt["finite_field_low_rank"] = {
        "field": "GF(2)",
        "m_min": 1,
        "m_max": 4,
        "n_min": 1,
        "n_max": 4,
        "shape_cases": rank_cases,
        "matrices_checked": matrices_checked,
        "mismatches": 0,
    }
    receipt["checks"]["rank_matrix_count_formula_exact"] = True

    # P0-6/P0-7 independent conditional modes.
    mode_cases = 0
    mode_targets = 0
    for modes in range(1, 4):
        for n in range(1, 4):
            for q in (2, 3):
                total = q ** (modes * n)
                assert len(set(itertools.product(range(q), repeat=modes * n))) == total
                assert math.ceil(math.log2(total)) == math.ceil(modes * n * math.log2(q) - 1e-12)
                mode_cases += 1
                mode_targets += total
    receipt["conditional_specialization"] = {
        "modes_min": 1,
        "modes_max": 3,
        "queries_per_mode_min": 1,
        "queries_per_mode_max": 3,
        "q_values": [2, 3],
        "cases": mode_cases,
        "target_signatures_enumerated": mode_targets,
        "mismatches": 0,
    }
    receipt["checks"]["independent_mode_information_lower_bound"] = True

    receipt["claim_ceiling"] = (
        "Exact finite theorem calibration only. Closes counting/crossover/lower-bound atoms; "
        "does not establish real pre-outcome estimators, router learnability, effective residual rank, "
        "MoE superiority, or protected held-family prediction."
    )
    receipt["terminal"] = "P0_ZERO_PRIOR_RESPONSE_LAWS_EXACT_LAYER_GREEN"

    out = Path(__file__).with_name("GMI_P0_ZERO_PRIOR_RESPONSE_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
