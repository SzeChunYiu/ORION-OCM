#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path


def conjugate_by_cyclic_shift(a, n, k):
    return [[a[(i + k) % n][(j + k) % n] for j in range(n)] for i in range(n)]


def gf2_rank(mask, m, n):
    rows = []
    for i in range(m):
        row = 0
        for j in range(n):
            if (mask >> (i * n + j)) & 1:
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
        den *= q**r - q**i
    return num // den


def main():
    receipt = {
        "artifact": "GMI_SYMMETRY_SPECIALIZATION_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "runner": "run_gmi_symmetry_specialization_exact_v1.py",
        "checks": {},
    }

    # Exact cyclic group-average projection checks on every binary matrix through n=4.
    matrices = 0
    for n in range(1, 5):
        for mask in range(1 << (n * n)):
            a = [[(mask >> (i * n + j)) & 1 for j in range(n)] for i in range(n)]
            s = [[0] * n for _ in range(n)]
            for k in range(n):
                c = conjugate_by_cyclic_shift(a, n, k)
                for i in range(n):
                    for j in range(n):
                        s[i][j] += c[i][j]
            # Group average s/n is circulant.
            for i in range(n):
                for j in range(n):
                    assert s[i][j] == s[0][(j - i) % n]
            # Exact scaled Pythagorean identity for orthogonal projection.
            lhs = n * n * sum(a[i][j] ** 2 for i in range(n) for j in range(n))
            projected = sum(s[i][j] ** 2 for i in range(n) for j in range(n))
            residual = sum((n * a[i][j] - s[i][j]) ** 2 for i in range(n) for j in range(n))
            assert lhs == projected + residual
            matrices += 1

    receipt["cyclic_symmetry_projection"] = {
        "n_min": 1,
        "n_max": 4,
        "binary_matrices_checked": matrices,
        "mismatches": 0,
    }
    receipt["checks"]["group_average_is_circulant_projection"] = True
    receipt["checks"]["projection_pythagorean_identity_exact"] = True

    # Exact GF(2) mode-span rank distributions through 4x4.
    shapes = 0
    mode_matrices = 0
    for m in range(1, 5):
        for p in range(1, 5):
            observed = Counter(gf2_rank(mask, m, p) for mask in range(1 << (m * p)))
            expected = {r: rank_count_formula(m, p, r, 2) for r in range(min(m, p) + 1)}
            assert dict(sorted(observed.items())) == expected
            shapes += 1
            mode_matrices += 1 << (m * p)

    receipt["mode_span_rank"] = {
        "field": "GF(2)",
        "modes_min": 1,
        "modes_max": 4,
        "parameter_dimension_min": 1,
        "parameter_dimension_max": 4,
        "shape_cases": shapes,
        "matrices_checked": mode_matrices,
        "mismatches": 0,
    }
    receipt["checks"]["finite_field_rank_count_exact"] = True

    receipt["claim_ceiling"] = (
        "Exact finite validation of linear cyclic-symmetry projection and finite-field mode-rank laws only; "
        "does not establish nonlinear real-task symmetry estimators or MoE superiority."
    )
    receipt["terminal"] = "SYMMETRY_SPECIALIZATION_EXACT_LAYER_GREEN"

    out = Path(__file__).with_name("GMI_SYMMETRY_SPECIALIZATION_EXACT_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
