#!/usr/bin/env python3
"""Exact finite-dimensional witnesses for the Grand GMI quantum instantiation.

All arithmetic used for verdicts is rational. This is not a quantum simulator; it pins
small operational identities and boundary counterexamples used by the theorem note.
"""

from fractions import Fraction as F
from math import ceil, log2
import json


def mat_trace_product(a, b):
    n = len(a)
    return sum(a[i][j] * b[j][i] for i in range(n) for j in range(n))


def check_probe_refinement():
    h = F(1, 2)
    rho_plus = [[h, h], [h, h]]
    rho_minus = [[h, -h], [-h, h]]
    z0 = [[F(1), F(0)], [F(0), F(0)]]
    z1 = [[F(0), F(0)], [F(0), F(1)]]
    xp = [[h, h], [h, h]]
    xm = [[h, -h], [-h, h]]

    z_plus = [mat_trace_product(z0, rho_plus), mat_trace_product(z1, rho_plus)]
    z_minus = [mat_trace_product(z0, rho_minus), mat_trace_product(z1, rho_minus)]
    x_plus = [mat_trace_product(xp, rho_plus), mat_trace_product(xm, rho_plus)]
    x_minus = [mat_trace_product(xp, rho_minus), mat_trace_product(xm, rho_minus)]

    assert z_plus == z_minus == [h, h]
    assert x_plus == [F(1), F(0)]
    assert x_minus == [F(0), F(1)]
    return {
        "z_only_response_plus": ["1/2", "1/2"],
        "z_only_response_minus": ["1/2", "1/2"],
        "x_response_plus": ["1", "0"],
        "x_response_minus": ["0", "1"],
        "z_only_equivalent": True,
        "z_plus_x_refines": True,
    }


def check_quantum_cut_capacities():
    rows = []
    for q in range(0, 5):
        d = 2 ** q
        rows.append({
            "transmitted_qubits": q,
            "dimension": d,
            "bare_zero_error_messages": d,
            "dense_coding_messages_with_declared_max_entanglement": d * d,
        })

    thresholds = []
    for m in range(1, 257):
        bare_q = 0
        while 2 ** bare_q < m:
            bare_q += 1
        ea_q = 0
        while 4 ** ea_q < m:
            ea_q += 1
        assert 2 ** bare_q >= m
        assert 4 ** ea_q >= m
        thresholds.append((m, bare_q, ea_q))

    assert thresholds[-1] == (256, 8, 4)
    return {
        "capacity_rows": rows,
        "message_thresholds_checked": len(thresholds),
        "m_256_bare_qubits": 8,
        "m_256_dense_coding_transmitted_qubits": 4,
        "free_entanglement_changes_cut_capacity": True,
    }


def check_no_cloning_witness():
    # |0> and |+> have fidelity |<0|+>|^2 = 1/2.
    # Two perfect copies would have fidelity (1/2)^2 = 1/4, while an isometry
    # must preserve fidelity of pure inputs. Contradiction.
    f_in = F(1, 2)
    f_two_copies = f_in * f_in
    assert f_in != f_two_copies
    return {
        "input_fidelity": "1/2",
        "perfect_two_copy_fidelity": "1/4",
        "isometric_fidelity_required": "1/2",
        "universal_perfect_cloner_possible": False,
    }


def check_classical_diagonal_sector():
    probs = [F(0), F(1, 4), F(1, 2), F(3, 4), F(1)]
    checks = []
    z0 = [[F(1), F(0)], [F(0), F(0)]]
    z1 = [[F(0), F(0)], [F(0), F(1)]]
    for p1 in probs:
        rho = [[1 - p1, F(0)], [F(0), p1]]
        obs = [mat_trace_product(z0, rho), mat_trace_product(z1, rho)]
        assert obs == [1 - p1, p1]
        checks.append({"p1": str(p1), "z_distribution": [str(obs[0]), str(obs[1])]})
    return {"rational_distributions_checked": len(checks), "rows": checks, "all_exact": True}


def rank_fraction(rows):
    a = [list(map(F, row)) for row in rows]
    r = 0
    c = 0
    while r < len(a) and c < len(a[0]):
        pivot = next((i for i in range(r, len(a)) if a[i][c] != 0), None)
        if pivot is None:
            c += 1
            continue
        a[r], a[pivot] = a[pivot], a[r]
        p = a[r][c]
        a[r] = [x / p for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        r += 1
        c += 1
    return r


def check_effect_span_refinement():
    # Coordinates in the Pauli basis (I, X, Y, Z), overall 1/2 factors omitted.
    z = [(1, 0, 0, 1), (1, 0, 0, -1)]
    zx = z + [(1, 1, 0, 0), (1, -1, 0, 0)]
    zxy = zx + [(1, 0, 1, 0), (1, 0, -1, 0)]
    ranks = [rank_fraction(z), rank_fraction(zx), rank_fraction(zxy)]
    assert ranks == [2, 3, 4]
    return {"effect_span_ranks_Z_ZX_ZXY": ranks, "tomographic_full_qubit_rank": 4}


def run():
    return {
        "terminal": "GRAND_GMI_QUANTUM_PROCESS_INSTANTIATION_TRANCHE_ALL_GREEN",
        "probe_refinement": check_probe_refinement(),
        "quantum_cut_capacity": check_quantum_cut_capacities(),
        "no_cloning": check_no_cloning_witness(),
        "classical_diagonal_sector": check_classical_diagonal_sector(),
        "effect_span": check_effect_span_refinement(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
