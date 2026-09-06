"""Exact matrix-free navigation primitives for issue #115 FK-2.

This module is deliberately additive.  The incumbent dense rational navigation
implementation remains the authority/reference.  The functions here evaluate
that same registered operator directly from hyperedge incidence without
materialising the dense ``N x N`` transition matrix.

The factorisation is only an execution change:

    y = P^T x

where ``P`` is exactly the matrix produced by ``navigation.navigation_matrix``.
Frozen structural denominators, conjunctive-tail gating, edge liveness,
per-head liveness and normalized head weights are preserved verbatim.

No local-subgraph truncation, approximate retrieval, renormalisation or new
navigation semantics are introduced here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Hashable, Iterable, Sequence

from .navigation import NavigationMode, Relevance, _beta, _gate, gated_seed, structural_denominators
from .space import KnowledgeSpace
from .warrant import CannotCheck


@dataclass(frozen=True, slots=True)
class MatrixFreeWork:
    """Structural work counters for one matrix-free ``P^T x`` application.

    These are logical operation counts, not wall-time, RSS, CPU or a claim that
    the whole query is sparse.  ``hyperedges_examined`` still exposes any global
    preparation that remains in this first exact implementation.
    """

    hyperedges_examined: int
    live_tail_terms: int
    head_terms_examined: int


@dataclass(frozen=True, slots=True)
class MatrixFreeConvergence:
    """Exact a-posteriori certificate for matrix-free restart iteration.

    For the registered non-negative, row-substochastic navigation operator,
    ``T(x) = alpha*s + (1-alpha) P^T x`` is an l1 contraction with factor at most
    ``1-alpha``.  Therefore ``||x-x*||_1 <= ||T(x)-x||_1 / alpha``.  We compute
    that residual exactly over ``Fraction``; no float threshold grants success.
    """

    activation: tuple[Fraction, ...]
    iterations: int
    residual_l1: Fraction
    error_bound_l1: Fraction
    matvec_calls: int


def transpose_matvec(
    ks: KnowledgeSpace,
    vector: Sequence[Fraction],
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
    mode: NavigationMode = NavigationMode.WARRANTED,
    with_work: bool = False,
) -> list[Fraction] | tuple[list[Fraction], MatrixFreeWork]:
    """Return ``P^T vector`` without materialising ``P``.

    ``P`` is the exact query/revocation-conditioned transition matrix defined by
    :func:`ocm.kso.navigation.navigation_matrix`.  The implementation factors the
    repeated per-tail/per-head contribution of a hyperedge, but does not alter
    its conjunctive enabling rule.
    """

    ids = ks.ids
    if len(vector) != len(ids):
        raise ValueError("vector must match KnowledgeSpace dimensions")

    rv = frozenset(revoked)
    idx = {atom_id: i for i, atom_id in enumerate(ids)}
    amap = ks.atom_view
    denominators = structural_denominators(ks, relevance)
    out = [Fraction(0, 1) for _ in ids]

    edges_examined = tail_terms = head_terms = 0
    for edge in ks.hyperedges:
        edges_examined += 1
        structural_mass = edge.weight * _beta(relevance, edge.relation_type)
        if structural_mass == 0:
            continue

        edge_gate = _gate(edge.liveness(rv), mode)
        tails_gate = min((_gate(amap[t].liveness(rv), mode) for t in edge.tails), default=Fraction(0, 1))
        if edge_gate == 0 or tails_gate == 0:
            continue

        # For this hyperedge, P[tail, head] factors into a common edge/tail
        # gate, one structural mass / frozen tail denominator, and a per-head
        # weight/gate.  Summing the source-vector contribution first therefore
        # gives the same P^T x without creating pairwise edge semantics.
        source_mass = Fraction(0, 1)
        for tail in edge.tails:
            denom = denominators[tail]
            if denom == 0:
                continue
            tail_terms += 1
            source_mass += Fraction(vector[idx[tail]]) / denom
        if source_mass == 0:
            continue

        common = edge_gate * tails_gate * structural_mass * source_mass
        for head, head_weight in zip(edge.heads, edge.normalized_head_weights(), strict=True):
            head_terms += 1
            dst_gate = _gate(amap[head].liveness(rv), mode)
            if dst_gate:
                out[idx[head]] += common * dst_gate * head_weight

    if with_work:
        return out, MatrixFreeWork(edges_examined, tail_terms, head_terms)
    return out


def restart_step_matrix_free(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    vector: Sequence[Fraction],
    alpha: Fraction,
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> list[Fraction]:
    """One exact restart step using the matrix-free transition application."""

    alpha = Fraction(alpha)
    if not (Fraction(0, 1) < alpha <= Fraction(1, 1)):
        raise ValueError("alpha must be in (0,1]")
    if len(seed) != len(ks.ids) or len(vector) != len(ks.ids):
        raise ValueError("seed and vector must match KnowledgeSpace dimensions")

    rv = frozenset(revoked)
    gated = gated_seed(ks, seed, rv, mode)
    transition = transpose_matvec(ks, vector, revoked=rv, relevance=relevance, mode=mode)
    return [alpha * gated[i] + (1 - alpha) * transition[i] for i in range(len(gated))]


def restart_iterate_matrix_free(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    alpha: Fraction,
    steps: int,
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> tuple[list[Fraction], int]:
    """Run a fixed number of exact matrix-free restart iterations from the gated seed."""

    if not isinstance(steps, int) or steps < 0:
        raise ValueError("steps must be a non-negative integer")
    rv = frozenset(revoked)
    current = gated_seed(ks, seed, rv, mode)
    for _ in range(steps):
        current = restart_step_matrix_free(
            ks,
            seed,
            current,
            alpha,
            revoked=rv,
            relevance=relevance,
            mode=mode,
        )
    return current, steps


def _certifiable_nonnegative_operator(ks: KnowledgeSpace, relevance: Relevance) -> bool:
    """Check the extra assumptions used only by the convergence certificate.

    The incumbent dense reference permits arbitrary caller relevance functions.
    Matrix-free operator parity does too.  The simple l1 contraction certificate,
    however, is justified only when every structural multiplier is non-negative.
    """

    return all(_beta(relevance, edge.relation_type) >= 0 for edge in ks.hyperedges)


def fixed_point_matrix_free_certified(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    alpha: Fraction,
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
    mode: NavigationMode = NavigationMode.WARRANTED,
    tol: Fraction = Fraction(1, 10**12),
    max_iter: int = 100_000,
) -> MatrixFreeConvergence:
    """Iterate to an exactly certified l1 error bound without a dense matrix.

    The returned ``error_bound_l1`` is an upper bound on distance to the exact
    fixed point of the *same* registered navigation operator.  This is a serving
    alternative, not a replacement for exact dense receipts.  If the simple
    contraction proof does not apply or the budget is exhausted, fail closed.
    """

    alpha = Fraction(alpha)
    tol = Fraction(tol)
    if not (Fraction(0, 1) < alpha <= Fraction(1, 1)):
        raise ValueError("alpha must be in (0,1]")
    if tol <= 0 or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("tol and max_iter must be positive")
    if len(seed) != len(ks.ids):
        raise ValueError("seed must match KnowledgeSpace dimensions")
    seed = tuple(Fraction(value) for value in seed)
    if any(value < 0 for value in seed) or sum(seed, Fraction(0, 1)) > 1:
        raise ValueError("seed must be a non-negative sub-probability vector")
    if not _certifiable_nonnegative_operator(ks, relevance):
        raise CannotCheck("matrix-free l1 certificate requires non-negative relevance weights")

    rv = frozenset(revoked)
    gated = tuple(gated_seed(ks, seed, rv, mode))
    current = gated
    matvec_calls = 0

    for iteration in range(1, max_iter + 1):
        transition = transpose_matvec(ks, current, revoked=rv, relevance=relevance, mode=mode)
        matvec_calls += 1
        current = tuple(alpha * gated[i] + (1 - alpha) * transition[i] for i in range(len(gated)))

        # Exact a-posteriori residual at the candidate being returned.
        transition_next = transpose_matvec(ks, current, revoked=rv, relevance=relevance, mode=mode)
        matvec_calls += 1
        next_state = tuple(alpha * gated[i] + (1 - alpha) * transition_next[i] for i in range(len(gated)))
        residual = sum((abs(next_state[i] - current[i]) for i in range(len(gated))), Fraction(0, 1))
        error_bound = residual / alpha
        if error_bound <= tol:
            return MatrixFreeConvergence(current, iteration, residual, error_bound, matvec_calls)

    raise CannotCheck(f"matrix-free iteration did not certify tolerance within {max_iter} steps")
