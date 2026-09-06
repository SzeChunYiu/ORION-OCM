from __future__ import annotations

from fractions import Fraction as F

import pytest

from ocm.kso.navigation import (
    NavigationMode,
    gated_seed,
    mutant_navigation_matrix_renormalize,
    navigation_matrix,
    restart_step,
)
from ocm.kso.navigation_matrix_free import (
    restart_iterate_matrix_free,
    restart_step_matrix_free,
    transpose_matvec,
)
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import WarrantProfile as WP


def _space() -> KnowledgeSpace:
    return KnowledgeSpace(
        (
            Atom("a", "claim"),
            Atom("b", "claim", WP.of({"ev:b"})),
            Atom("c", "claim", WP.of({"ev:c"})),
            Atom("d", "claim", WP.partial(())),
        ),
        (
            Hyperedge(
                "joint",
                ("a", "b"),
                ("c", "d"),
                "DEPENDENCE",
                weight=F(3, 2),
                head_weights=(F(1), F(3)),
                warrant=WP.of({"ev:edge"}),
            ),
            Hyperedge("support", ("a",), ("b",), "SUPPORT", weight=F(2, 3)),
            Hyperedge("tail-c", ("c",), ("d",), "SUPPORT", weight=F(5, 7)),
        ),
    )


def _dense_transpose(rows, vector):
    return [sum((rows[i][j] * vector[i] for i in range(len(vector))), F(0)) for j in range(len(vector))]


@pytest.mark.parametrize("mode", [NavigationMode.WARRANTED, NavigationMode.EXPLORATORY])
@pytest.mark.parametrize("revoked", [frozenset(), frozenset({"ev:b"}), frozenset({"ev:edge"}), frozenset({"ev:c"})])
def test_matrix_free_transpose_matvec_matches_dense_exactly(mode, revoked):
    ks = _space()
    vector = (F(2, 11), F(3, 11), F(5, 11), F(1, 11))
    relevance = {"DEPENDENCE": F(4, 3), "SUPPORT": F(7, 5)}
    dense = navigation_matrix(ks, revoked=revoked, relevance=relevance, mode=mode)

    actual, work = transpose_matvec(
        ks,
        vector,
        revoked=revoked,
        relevance=relevance,
        mode=mode,
        with_work=True,
    )

    assert actual == _dense_transpose(dense.rows, vector)
    assert work.hyperedges_examined == len(ks.hyperedges)
    assert 0 <= work.live_tail_terms <= sum(len(e.tails) for e in ks.hyperedges)
    assert 0 <= work.head_terms_examined <= sum(len(e.heads) for e in ks.hyperedges)


def test_matrix_free_restart_step_and_iteration_match_dense_operator():
    ks = _space()
    seed = (F(1), F(0), F(0), F(0))
    alpha = F(1, 3)
    revoked = frozenset({"ev:c"})
    relevance = {"DEPENDENCE": F(2), "SUPPORT": F(1, 2)}
    dense = navigation_matrix(ks, revoked=revoked, relevance=relevance)
    gated = gated_seed(ks, seed, revoked)
    current = gated[:]

    assert restart_step_matrix_free(
        ks,
        seed,
        current,
        alpha,
        revoked=revoked,
        relevance=relevance,
    ) == restart_step(dense.rows, gated, current, alpha)

    for _ in range(4):
        current = restart_step(dense.rows, gated, current, alpha)
    matrix_free, steps = restart_iterate_matrix_free(
        ks,
        seed,
        alpha,
        4,
        revoked=revoked,
        relevance=relevance,
    )
    assert steps == 4 and matrix_free == current


def test_matrix_free_preserves_frozen_denominator_instead_of_renormalizing():
    ks = KnowledgeSpace(
        (Atom("a", "claim"), Atom("b", "claim"), Atom("c", "claim", WP.of({"ev:c"}))),
        (
            Hyperedge("ab", ("a",), ("b",), "DEPENDENCE"),
            Hyperedge("ac", ("a",), ("c",), "DEPENDENCE"),
        ),
    )
    vector = (F(1), F(0), F(0))
    revoked = frozenset({"ev:c"})
    exact = navigation_matrix(ks, revoked=revoked)
    bad = mutant_navigation_matrix_renormalize(ks, revoked=revoked)

    actual = transpose_matvec(ks, vector, revoked=revoked)
    assert actual == _dense_transpose(exact.rows, vector)
    assert actual != _dense_transpose(bad.rows, vector)
    assert actual == [F(0), F(1, 2), F(0)]


def test_matrix_free_refuses_dimension_and_alpha_errors():
    ks = _space()
    with pytest.raises(ValueError):
        transpose_matvec(ks, (F(1),))
    with pytest.raises(ValueError):
        restart_step_matrix_free(ks, (F(1),), (F(1),) * 4, F(1, 2))
    with pytest.raises(ValueError):
        restart_step_matrix_free(ks, (F(1),) * 4, (F(1),) * 4, F(0))
