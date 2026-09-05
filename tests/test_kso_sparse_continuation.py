"""Independent represented-system checks and normalization/lifetime boundaries."""
from dataclasses import replace
from fractions import Fraction
import gc
import random
import weakref

import pytest

from ocm.kso.navigation import fixed_point, navigation_matrix, restart_fixed_point_exact
from ocm.kso.navigation_sparse import (
    SparseMatrix, check_sparse_agrees_with_exact, sparse_fixed_point_certified, sparse_navigation_matrix,
)
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile


@pytest.mark.parametrize("scale", [Fraction(1, 10**400), Fraction(10**400)])
def test_sparse_normalization_survives_extreme_common_weight_scale(scale):
    atoms = tuple(Atom(x, "claim") for x in ("a", "b", "c", "d"))
    ks = KnowledgeSpace(atoms, (
        Hyperedge("joint", ("a", "b"), ("c", "d"), "SUPPORT", weight=scale,
                  head_weights=(Fraction(1), Fraction(3))),
        Hyperedge("other", ("a",), ("d",), "SUPPORT", weight=3 * scale),
    ))
    sparse = sparse_navigation_matrix(ks)
    exact = navigation_matrix(ks)
    for j, incoming in enumerate(sparse.incoming):
        for i in range(len(atoms)):
            assert sum(weight for source, weight in incoming if source == i) == float(exact.rows[i][j])


@pytest.mark.parametrize("seed_number", range(12))
def test_certificate_matches_independent_fraction_residual_and_exact_solution(seed_number):
    rng = random.Random(seed_number)
    n = rng.randint(2, 7)
    # Duplicate entries are deliberately retained: the matrix constructor permits them.
    incoming = [[] for _ in range(n)]
    for source in range(n):
        for _ in range(4):
            incoming[rng.randrange(n)].append((source, rng.choice((0.0, .025, .125))))
    matrix = SparseMatrix(tuple(map(str, range(n))), tuple(tuple(row) for row in incoming), 4 * n)
    seed = [rng.choice((0.0, .1, .25)) for _ in range(n)]
    # Exact solver requires a sub-probability seed.
    seed = [value / max(1.0, sum(seed)) for value in seed]
    alpha = rng.choice((.01, .2, .5, 1.0))
    result = sparse_fixed_point_certified(matrix, seed, alpha)
    p = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for target, row in enumerate(matrix.incoming):
        for source, weight in row:
            p[source][target] += Fraction(weight)
    qa = Fraction(alpha)
    a = list(map(Fraction, result.activation))
    residual = sum(abs(qa * Fraction(seed[j]) + (1 - qa) * sum(p[i][j] * a[i] for i in range(n)) - a[j]) for j in range(n))
    contraction = (1 - qa) * max(map(sum, p))
    exact = restart_fixed_point_exact(p, list(map(Fraction, seed)), qa)
    assert result.residual_l1 == residual
    assert result.contraction == contraction
    assert result.error_bound_l1 == residual / (1 - contraction)
    assert sum(abs(x - y) for x, y in zip(a, exact, strict=True)) <= result.error_bound_l1 <= Fraction(1e-12)


@pytest.mark.parametrize("weight,seed,alpha", [
    (float.fromhex("0x0.0000000000001p-1022"), 1.0, .5),
    (.125, float.fromhex("0x0.0000000000001p-1022"), .5),
    (Fraction(1, 3), Fraction(1, 7), Fraction(1, 5)),
])
def test_certificate_handles_subnormals_and_nondyadic_direct_inputs(weight, seed, alpha):
    matrix = SparseMatrix(("x",), (((0, weight),),), 1)
    result = sparse_fixed_point_certified(matrix, [seed], alpha)
    a = Fraction(result.activation[0])
    residual = abs(Fraction(alpha) * Fraction(seed) + (1 - Fraction(alpha)) * Fraction(weight) * a - a)
    assert result.residual_l1 == residual
    assert result.error_bound_l1 == residual / (1 - (1 - Fraction(alpha)) * Fraction(weight))


def test_warm_indexes_are_owned_by_their_generation_and_collectable():
    ks = KnowledgeSpace((Atom("a", "claim"), Atom("b", "claim")),
                        (Hyperedge("e", ("a",), ("b",), "SUPPORT"),))
    ks.atom_map(); ks.edge_map(); ks.incident_edges("a"); ks.outgoing_edges("a")
    old = weakref.ref(ks)
    successor = ks.replace_atom(replace(ks.atom("b"), warrant=WarrantProfile.zero()))
    assert set(successor.__dict__) == {"atoms", "hyperedges", "registry", "ids"}
    assert successor.atom("b").warrant.is_live(()) is False
    assert successor.outgoing_edges("a") == ks.outgoing_edges("a")
    del ks
    gc.collect()
    assert old() is None  # no global cache holds the preceding graph alive


def test_exact_seed_and_sparse_comparison_share_one_revocation_snapshot():
    ks = KnowledgeSpace((Atom("a", "claim", WarrantProfile.of({"revoked"})), Atom("b", "claim")),
                        (Hyperedge("e", ("a",), ("b",), "SUPPORT"),))
    seed = [Fraction(1), Fraction(0)]
    expected = fixed_point(ks, seed, Fraction(1, 3), revoked={"revoked"})
    assert expected == {"a": 0, "b": 0}
    assert fixed_point(ks, seed, Fraction(1, 3), revoked=iter(("revoked",))) == expected
    assert check_sparse_agrees_with_exact(ks, seed, Fraction(1, 3), revoked=iter(("revoked",)))["max_abs_error"] == 0


def test_sparse_matrix_materializes_nested_iterators_and_input_aliases():
    row = [[0, 1.0]]
    matrix = SparseMatrix(["x"], (iter(row),), 1)
    row[0][1] = 0.0
    first = sparse_fixed_point_certified(matrix, [1.0], .5)
    second = sparse_fixed_point_certified(matrix, [1.0], .5)
    assert first == second
    assert abs(first.activation[0] - 1.0) <= float(first.error_bound_l1)
