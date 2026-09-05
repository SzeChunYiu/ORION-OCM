"""Sparse float navigation for scale (M2 §13; revival row "navigation scale").

The exact rational solver is O(n³); the dense float iteration is O(n²) per step.  This module
builds the gated matrix as sparse adjacency (per-tail lists) with the same frozen-denominator law
and runs power iteration in O(|incidences|) per step, stopping when the ℓ1 change is below ``tol``
— the KS-T05 rate (1−α)^k is the stopping certificate.  Agreement with the exact solver is asserted
on small spaces (``check_sparse_agrees_with_exact``).  No new mathematics.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Hashable, Iterable, Sequence

from .navigation import NavigationMode, _beta, _gate, fixed_point, structural_denominators
from .space import KnowledgeSpace
from .warrant import CannotCheck


@dataclass(frozen=True)
class SparseMatrix:
    ids: tuple[str, ...]
    incoming: tuple[tuple[tuple[int, float], ...], ...]   # incoming[j] = ((i, P[i][j]), ...)
    incidences: int


def sparse_navigation_matrix(ks: KnowledgeSpace, *, revoked: Iterable[Hashable] = (), relevance=None, mode: NavigationMode = NavigationMode.WARRANTED) -> SparseMatrix:
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    denom = structural_denominators(ks, relevance)
    gate = {x: float(_gate(amap[x].liveness(rv), mode)) for x in ids}
    incoming: list[list[tuple[int, float]]] = [[] for _ in ids]
    n_inc = 0
    for e in ks.hyperedges:
        mass = float(e.weight * _beta(relevance, e.relation_type))
        if mass == 0.0:
            continue
        edge_gate = float(_gate(e.liveness(rv), mode))
        tails_gate = min((gate[t] for t in e.tails), default=0.0)
        if edge_gate == 0.0 or tails_gate == 0.0:
            continue
        hw = e.normalized_head_weights()
        for t in e.tails:
            d = denom[t]
            if d == 0:
                continue
            p = mass / float(d)
            for h, w in zip(e.heads, hw, strict=True):
                g = gate[h]
                if g == 0.0:
                    continue
                incoming[idx[h]].append((idx[t], edge_gate * tails_gate * g * p * float(w)))
                n_inc += 1
    return SparseMatrix(ids, tuple(tuple(r) for r in incoming), n_inc)


def sparse_fixed_point(m: SparseMatrix, seed: Sequence[float], alpha: float, *, tol: float = 1e-12, max_iter: int = 100_000) -> tuple[list[float], int]:
    if not (0.0 < alpha <= 1.0):
        raise ValueError("alpha must be in (0,1]")
    a = [alpha * s for s in seed]
    for k in range(1, max_iter + 1):
        nxt = [alpha * seed[j] + (1 - alpha) * sum(w * a[i] for i, w in m.incoming[j]) for j in range(len(seed))]
        delta = sum(abs(u - v) for u, v in zip(nxt, a, strict=True))
        a = nxt
        if delta <= tol:
            return a, k
    raise CannotCheck(f"sparse iteration did not converge within {max_iter} steps")


def sparse_activation(ks: KnowledgeSpace, seed: Sequence[Fraction] | Sequence[float], alpha: float, *, revoked: Iterable[Hashable] = (), relevance=None, mode: NavigationMode = NavigationMode.WARRANTED, tol: float = 1e-12) -> tuple[dict[str, float], int, int]:
    """Returns (activation, iterations, incidences).  The seed is gated exactly as in the exact path."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    gated = [float(s) * float(_gate(amap[x].liveness(rv), mode)) for x, s in zip(ks.ids, seed, strict=True)]
    m = sparse_navigation_matrix(ks, revoked=rv, relevance=relevance, mode=mode)
    a, iters = sparse_fixed_point(m, gated, alpha, tol=tol)
    return dict(zip(ks.ids, a, strict=True)), iters, m.incidences


def check_sparse_agrees_with_exact(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, *, revoked: Iterable[Hashable] = (), tol: float = 1e-9) -> dict[str, Any]:
    exact = fixed_point(ks, seed, alpha, revoked=revoked)
    approx, iters, inc = sparse_activation(ks, seed, float(alpha), revoked=revoked, tol=1e-13)
    err = max(abs(approx[x] - float(exact[x])) for x in ks.ids)
    if err > tol:
        raise AssertionError(f"sparse solver disagrees with exact: max error {err}")
    return {"atoms": len(ks.ids), "incidences": inc, "iterations": iters, "max_abs_error": err}
