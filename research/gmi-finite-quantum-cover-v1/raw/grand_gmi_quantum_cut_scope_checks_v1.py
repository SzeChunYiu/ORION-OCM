#!/usr/bin/env python3
"""Exact finite counterexample to classical-chromatic quantum-dimension transport.

The verifier handles this rational projective witness, not arbitrary quantum
feasibility. No numerical tolerances, external data, or network calls are used.
"""

from fractions import Fraction as F
from itertools import combinations, product
import json


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def yu_oh_rays():
    """The 13 rays of Yu--Oh Eq. (1), modulo sign in lexicographic order."""
    return tuple(
        v for v in product((-1, 0, 1), repeat=3)
        if any(v) and next(x for x in v if x) > 0
    )


def orthogonality_edges(rays):
    return tuple(
        (i, j) for i, j in combinations(range(len(rays)), 2)
        if dot(rays[i], rays[j]) == 0
    )


def proper_coloring(colors, edges):
    return all(colors[i] != colors[j] for i, j in edges)


def check_classical_lower_certificate():
    """Exhaust all eight candidate 3-colorings after fixing the basis triangle.

    Each opposite face-diagonal pair, together with its coordinate axis,
    forms a triangle. Each pair therefore has only two possible orientations
    of the two remaining colors. In every orientation a body diagonal sees
    all three colors. This independently certifies non-3-colorability.
    """
    rays = yu_oh_rays()
    edges = orthogonality_edges(rays)
    assert len(rays) == 13 and len(edges) == 24
    axes = [rays.index(tuple(int(i == j) for j in range(3))) for i in range(3)]
    face_pairs = [
        [j for j, v in enumerate(rays) if dot(v, v) == 2 and v[i] == 0]
        for i in range(3)
    ]
    assert all(len(pair) == 2 for pair in face_pairs)
    assert len(set(axes + [j for pair in face_pairs for j in pair])) == 9
    body = [i for i, v in enumerate(rays) if dot(v, v) == 3]
    assert len(body) == 4
    certificates = []
    for orientations in product((0, 1), repeat=3):
        colors = {vertex: color for color, vertex in enumerate(axes)}
        for axis, orientation in enumerate(orientations):
            pair = face_pairs[axis]
            palette = [color for color in range(3) if color != axis]
            colors[pair[0]] = palette[orientation]
            colors[pair[1]] = palette[1 - orientation]
            triangle = [axes[axis], *pair]
            assert all(dot(rays[i], rays[j]) == 0 for i, j in combinations(triangle, 2))
        blocked = [
            i for i in body
            if {colors[j] for j in colors if dot(rays[i], rays[j]) == 0} == {0, 1, 2}
        ]
        assert blocked, "a candidate three-coloring escaped the certificate"
        certificates.append({
            "pair_orientations": list(orientations),
            "blocked_body_vertex": blocked[0],
        })

    four_coloring = (0, 0, 1, 1, 1, 1, 0, 2, 2, 0, 2, 2, 3)
    assert len(four_coloring) == len(rays)
    assert proper_coloring(four_coloring, edges)
    return {
        "vertices": len(rays),
        "edges": len(edges),
        "candidate_orientations_exhausted": len(certificates),
        "three_coloring_obstructions": certificates,
        "four_coloring": list(four_coloring),
        "chromatic_number": 4,
    }


def identity(d):
    return tuple(tuple(F(i == j) for j in range(d)) for i in range(d))


def subtract(a, b):
    return tuple(tuple(x - y for x, y in zip(r, s)) for r, s in zip(a, b))


def multiply(a, b):
    d = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(d)) for j in range(d)) for i in range(d))


def trace(a):
    return sum(a[i][i] for i in range(len(a)))


def projector(v):
    norm_squared = dot(v, v)
    if norm_squared <= 0:
        raise ValueError("a ray must be nonzero")
    return tuple(tuple(F(x * y, norm_squared) for y in v) for x in v)


def require_projector(matrix, d):
    """Hermitian idempotence certifies PSD exactly for this real witness."""
    if len(matrix) != d or any(len(row) != d for row in matrix):
        raise ValueError("wrong projector dimension")
    if any(matrix[i][j] != matrix[j][i] for i in range(d) for j in range(d)):
        raise ValueError("projector is not symmetric")
    if multiply(matrix, matrix) != matrix:
        raise ValueError("matrix is not an orthogonal projector")


def edge_measurements(states, edges):
    unit = identity(len(states[0]))
    return {edge: (states[edge[0]], subtract(unit, states[edge[0]])) for edge in edges}


def verify_edge_protocol(states, measurements, edges):
    """Verify all promised endpoints for the finite projective encoding.

    The outputs 0 and 1 identify respectively the smaller and larger endpoint
    in y=(i,j). This verifies a supplied protocol and rejects corrupt witnesses.
    """
    if not states:
        raise ValueError("no encoded input states")
    d = len(states[0])
    for state in states:
        require_projector(state, d)
        if trace(state) != 1:
            raise ValueError("state is not trace one")
    if set(measurements) != set(edges):
        raise ValueError("measurement contexts do not match the promise")
    unit = identity(d)
    checked = 0
    for i, j in edges:
        effects = measurements[i, j]
        if len(effects) != 2:
            raise ValueError("a promised edge needs two output effects")
        for effect in effects:
            require_projector(effect, d)
        if effects[1] != subtract(unit, effects[0]):
            raise ValueError("effects do not sum to identity")
        for x, expected in ((i, (F(1), F(0))), (j, (F(0), F(1)))):
            probabilities = tuple(trace(multiply(states[x], effect)) for effect in effects)
            if probabilities != expected:
                raise ValueError("nonzero error on a promised endpoint")
            checked += 1
    return checked


def witness_data():
    rays = tuple(v + (0,) for v in yu_oh_rays()) + ((0, 0, 0, 1),)
    edges = orthogonality_edges(rays)
    states = tuple(projector(v) for v in rays)
    return rays, edges, states, edge_measurements(states, edges)


def check_quantum_separation():
    base = check_classical_lower_certificate()
    rays, edges, states, measurements = witness_data()
    assert len(rays) == 14 and len(edges) == 37
    base_edges = set(orthogonality_edges(yu_oh_rays()))
    assert set(edges) == base_edges | {(i, 13) for i in range(13)}
    five_coloring = tuple(base["four_coloring"]) + (4,)
    assert proper_coloring(five_coloring, edges)
    # The universal vertex requires a color absent from all G13 vertices.
    classical_alphabet = base["chromatic_number"] + 1
    clique = (0, 2, 8, 13)
    assert all((i, j) in edges for i, j in combinations(clique, 2))
    d = len(rays[0])
    # A K4 forces four mutually orthogonal nonzero supports; the displayed
    # orthogonal representation and verified decoder attain dimension four.
    assert len(clique) == d == 4
    checked = verify_edge_protocol(states, measurements, edges)
    assert checked == 74
    classical_bits = (classical_alphabet - 1).bit_length()
    quantum_qubits = (d - 1).bit_length()
    assert classical_alphabet > d and classical_bits > quantum_qubits
    # Genuine global identity-channel code: coordinate states are distinguished
    # together by one basis measurement. The side-information task has no such
    # full-input decoder; rays 0 and 1 have nonzero squared overlap 1/2.
    identity_checks = 0
    for i in clique:
        for j in clique:
            assert trace(multiply(states[i], states[j])) == F(i == j)
            identity_checks += 1
    overlap = trace(multiply(states[0], states[1]))
    assert overlap == F(1, 2)
    return {
        "rays": [list(v) for v in rays],
        "edges": [list(edge) for edge in edges],
        "classical_lower_certificate": base,
        "classical_five_coloring": list(five_coloring),
        "classical_minimum_alphabet": classical_alphabet,
        "classical_fixed_length_bits": classical_bits,
        "orthogonal_clique": list(clique),
        "quantum_minimum_dimension": d,
        "quantum_qubits": quantum_qubits,
        "rational_density_matrices_checked": len(states),
        "promised_input_context_checks": checked,
        "global_four_message_identity_checks": identity_checks,
        "nonorthogonal_input_pair_overlap": str(overlap),
        "unqualified_chromatic_dimension_transport_refuted": True,
        "global_identity_capacity_theorem_preserved": True,
    }


def run():
    return {
        "terminal": "GRAND_GMI_QUANTUM_CUT_SCOPE_V1_CHECKED",
        "scope": {
            "inputs": "finite classical edge-promise exact function",
            "communication": "one unassisted noiseless quantum message",
            "preshared_entanglement": False,
            "side_information": "edge known only to receiver",
            "arithmetic": "integers and exact rational Born probabilities",
            "evidence_boundary": "finite counterexample and identity-code control; not universal theory closure",
        },
        "separation": check_quantum_separation(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
