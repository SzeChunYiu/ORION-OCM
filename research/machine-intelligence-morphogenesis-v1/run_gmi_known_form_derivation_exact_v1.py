#!/usr/bin/env python3
"""Deterministic finite checks for GMI_KNOWN_FORM_DERIVATION_THEOREMS_V1.

No ML dependencies. This calibrates exact algebraic statements only; it is not
empirical evidence that historical architectures are frontier-optimal.
"""

from fractions import Fraction
from itertools import product
import json
import math


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def mat_vec(X, th):
    return [dot(row, th) for row in X]


def transpose(X):
    return list(map(list, zip(*X)))


def matmul(A, B):
    BT = transpose(B)
    return [[dot(row, col) for col in BT] for row in A]


def check_linear_sufficient_statistics():
    cases = 0
    mismatches = 0
    for vals in product((-1, 0, 1), repeat=6):
        X = [list(vals[0:2]), list(vals[2:4]), list(vals[4:6])]
        XT = transpose(X)
        XTX = matmul(XT, X)
        for y in product((-1, 0, 1), repeat=3):
            XTy = [dot(col, y) for col in XT]
            yTy = dot(y, y)
            for th in product((-1, 0, 1), repeat=2):
                pred = mat_vec(X, th)
                sse = sum((yy - pp) ** 2 for yy, pp in zip(y, pred))
                quad = yTy - 2 * dot(th, XTy)
                quad += sum(th[i] * XTX[i][j] * th[j] for i in range(2) for j in range(2))
                cases += 1
                if sse != quad:
                    mismatches += 1
    return {"cases": cases, "mismatches": mismatches}


def check_posterior_separation():
    den = 5
    grid = []
    for a in range(den + 1):
        for b in range(den + 1 - a):
            c = den - a - b
            grid.append((Fraction(a, den), Fraction(b, den), Fraction(c, den)))
    pairs = 0
    failures = 0
    for i, p in enumerate(grid):
        for q in grid[i + 1:]:
            v = tuple(pp - qq for pp, qq in zip(p, q))
            pv = dot(p, v)
            qv = dot(q, v)
            c = (pv + qv) / 2
            up = pv - c
            uq = qv - c
            pairs += 1
            if not (up > 0 and uq < 0):
                failures += 1
    return {"posterior_states": len(grid), "pairs": pairs, "failures": failures}


def matmul_mod2(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) % 2 for j in range(n)] for i in range(n)]


def check_translation_equivariance():
    per_n = {}
    for n in range(2, 5):
        P = [[0] * n for _ in range(n)]
        for i in range(n):
            P[(i + 1) % n][i] = 1
        count = 0
        total = 1 << (n * n)
        for bits in range(total):
            A = [[(bits >> (i * n + j)) & 1 for j in range(n)] for i in range(n)]
            if matmul_mod2(A, P) == matmul_mod2(P, A):
                count += 1
        per_n[str(n)] = {
            "all_binary_linear_maps": total,
            "translation_equivariant_maps": count,
            "expected_circulant_maps": 1 << n,
            "match": count == (1 << n),
        }
    return per_n


def popcount(x):
    return x.bit_count()


def check_dynamic_routing_union():
    cases = 0
    violations = 0
    positive_gap = 0
    for a in range(16):
        for b in range(16):
            for c in range(16):
                u = a | b | c
                avg = Fraction(popcount(a) + popcount(b) + popcount(c), 3)
                delta = Fraction(popcount(u), 1) - avg
                cases += 1
                if delta < 0:
                    violations += 1
                if delta > 0:
                    positive_gap += 1
    return {"cases": cases, "violations": violations, "positive_gap_cases": positive_gap}


def check_ensemble_variance():
    cases = 0
    failures = 0
    for m in range(1, 17):
        rhos = [Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)]
        if m > 1:
            rhos.append(Fraction(-1, m - 1))
        for rho in rhos:
            # variance of the equal-weight average from an equicorrelation covariance matrix
            exact = Fraction(m, m * m) + Fraction(m * (m - 1), m * m) * rho
            formula = rho + (1 - rho) / m
            cases += 1
            if exact != formula:
                failures += 1
    return {"cases": cases, "failures": failures}


def check_compile_threshold():
    cases = 0
    failures = 0
    for C in range(1, 21):
        for c_search in range(2, 11):
            for c_compiled in range(c_search):
                for R in range(1, 31):
                    actual = C + R * c_compiled < R * c_search
                    theorem = Fraction(R, 1) > Fraction(C, c_search - c_compiled)
                    cases += 1
                    if actual != theorem:
                        failures += 1
    return {"cases": cases, "failures": failures}


def memory_counting_calibration():
    cases = []
    for N in range(1, 9):
        for q in range(2, 6):
            states = q ** N
            cases.append({
                "N": N,
                "q": q,
                "possible_maps": states,
                "information_bits": math.log2(states),
                "formula_bits": N * math.log2(q),
            })
    return {"cases": len(cases), "largest_possible_maps": max(x["possible_maps"] for x in cases)}


def main():
    receipt = {
        "artifact": "GMI_KNOWN_FORM_DERIVATION_EXACT_RECEIPT_V1",
        "status": "EXACT_FINITE_CALIBRATION",
        "linear_sufficient_statistics": check_linear_sufficient_statistics(),
        "posterior_decision_separation": check_posterior_separation(),
        "translation_equivariance_gf2": check_translation_equivariance(),
        "dynamic_routing_union": check_dynamic_routing_union(),
        "ensemble_variance": check_ensemble_variance(),
        "compile_search_threshold": check_compile_threshold(),
        "memory_counting": memory_counting_calibration(),
    }
    checks = [
        receipt["linear_sufficient_statistics"]["mismatches"] == 0,
        receipt["posterior_decision_separation"]["failures"] == 0,
        all(v["match"] for v in receipt["translation_equivariance_gf2"].values()),
        receipt["dynamic_routing_union"]["violations"] == 0,
        receipt["ensemble_variance"]["failures"] == 0,
        receipt["compile_search_threshold"]["failures"] == 0,
    ]
    receipt["all_checks_green"] = all(checks)
    receipt["claim_ceiling"] = (
        "Exact finite calibration of theorem identities only. Does not establish practical optimization, "
        "generalization, architecture uniqueness, or protected neutral rediscovery."
    )
    receipt["terminal"] = "KNOWN_FORM_DERIVATION_EXACT_FINITE_GREEN" if all(checks) else "KNOWN_FORM_DERIVATION_EXACT_FINITE_RED"
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
