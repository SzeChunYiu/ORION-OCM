"""Sparse float navigation for scale (M2 §13; revival row "navigation scale").

The exact rational solver is O(n³); the dense float iteration is O(n²) per step.  This module
builds the gated matrix as sparse adjacency (per-tail lists) with the same frozen-denominator law
and runs power iteration in O(|incidences|) per step. An exact rational residual bounds the error
to the represented float matrix/seed/alpha; conversion error from the original rational KSO is
outside that certificate. Agreement with the exact solver is asserted
on small spaces (``check_sparse_agrees_with_exact``).  No new mathematics.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any, Hashable, Iterable, Sequence

from .navigation import NavigationMode, _beta, _gate, fixed_point, structural_denominators
from .space import KnowledgeSpace
from .warrant import CannotCheck


@dataclass(frozen=True)
class SparseMatrix:
    ids: tuple[str, ...]
    incoming: tuple[tuple[tuple[int, float], ...], ...]   # incoming[j] = ((i, P[i][j]), ...)
    incidences: int

    def __post_init__(self):
        # Validation, iteration and exact certification must see the same matrix.
        # Materialize nested one-shot rows and sever mutable sequence aliases.
        object.__setattr__(self, "ids", tuple(self.ids))
        object.__setattr__(self, "incoming", tuple(tuple((i, weight) for i, weight in row) for row in self.incoming))


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
        mass = e.weight * _beta(relevance, e.relation_type)
        if mass == 0:
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
            # Normalize exact structural mass before float conversion: a common
            # scale of 10**400 or 10**-400 must neither overflow nor erase a row.
            p = mass / d
            for h, w in zip(e.heads, hw, strict=True):
                g = gate[h]
                if g == 0.0:
                    continue
                incoming[idx[h]].append((idx[t], edge_gate * tails_gate * g * float(p * w)))
                n_inc += 1
    return SparseMatrix(ids, tuple(tuple(r) for r in incoming), n_inc)


@dataclass(frozen=True)
class SparseConvergence:
    """A posteriori bound for the exact system represented by the float inputs.

    The certificate does not bound conversion error from an original rational matrix,
    seed or alpha. Exact KSO receipts still use the rational solver. Fractions here make
    the residual check independent of floating-point stagnation and summation error.
    """

    activation: tuple[float, ...]
    iterations: int
    residual_l1: Fraction
    contraction: Fraction
    error_bound_l1: Fraction


def _dyadic_parts(value) -> tuple[int, int]:
    """Exact numerator and binary denominator exponent, without Fraction products."""
    if isinstance(value, (int, float)):
        numerator, denominator = value.as_integer_ratio()
    else:
        rational = Fraction(value)
        numerator, denominator = rational.numerator, rational.denominator
    if denominator & (denominator - 1):
        raise ValueError("non-dyadic input")
    return numerator, denominator.bit_length() - 1


def _dyadic_vector(values) -> tuple[list[int], int]:
    parts = [_dyadic_parts(value) for value in values]
    exponent = max((power for _, power in parts), default=0)
    return [numerator << (exponent - power) for numerator, power in parts], exponent


class _DyadicSystem:
    """The same exact residual using integers with common power-of-two scales.

    IEEE finite floats are dyadic rationals. Integer additions/multiplications
    therefore retain every represented bit while avoiding a gcd at each sparse
    incidence. No floating-point error estimate decides acceptance.
    """

    def __init__(self, m, seed, alpha):
        self.alpha, self.alpha_exp = _dyadic_parts(alpha)
        self.q = (1 << self.alpha_exp) - self.alpha
        self.seed, self.seed_exp = _dyadic_vector(seed)
        weights, self.weight_exp = _dyadic_vector(weight for row in m.incoming for _, weight in row)
        weight_iter = iter(weights)
        self.incoming = tuple(tuple((i, next(weight_iter)) for i, _ in row) for row in m.incoming)
        row_mass = [0] * len(seed)
        for row in self.incoming:
            for i, weight in row:
                row_mass[i] += weight
        self.contraction = Fraction(self.q * max(row_mass, default=0), 1 << (self.alpha_exp + self.weight_exp))

    def residual(self, activation):
        a, a_exp = _dyadic_vector(activation)
        restart_exp = self.alpha_exp + self.seed_exp
        transition_exp = self.alpha_exp + self.weight_exp + a_exp
        exponent = max(restart_exp, transition_exp, a_exp)
        total = 0
        for j, incoming in enumerate(self.incoming):
            restart = (self.alpha * self.seed[j]) << (exponent - restart_exp)
            transition = (self.q * sum(weight * a[i] for i, weight in incoming)) << (exponent - transition_exp)
            total += abs(restart + transition - (a[j] << (exponent - a_exp)))
        return Fraction(total, 1 << exponent)


class _FractionSystem:
    """Compatibility for direct rational inputs that do not have binary denominators."""

    def __init__(self, m, seed, alpha):
        row_mass = [Fraction(0)] * len(seed)
        self.incoming = tuple(tuple((i, Fraction(weight)) for i, weight in row) for row in m.incoming)
        for row in self.incoming:
            for i, weight in row:
                row_mass[i] += weight
        self.q = 1 - Fraction(alpha)
        self.restart = [Fraction(alpha) * Fraction(s) for s in seed]
        self.contraction = self.q * max(row_mass, default=Fraction(0))

    def residual(self, activation):
        a = list(map(Fraction, activation))
        return sum((abs(self.restart[j] + self.q * sum((weight * a[i] for i, weight in row), Fraction(0)) - a[j])
                    for j, row in enumerate(self.incoming)), Fraction(0))


def sparse_fixed_point_certified(m: SparseMatrix, seed: Sequence[float], alpha: float, *, tol: float = 1e-12, max_iter: int = 100_000) -> SparseConvergence:
    if not math.isfinite(alpha) or not (0.0 < alpha <= 1.0):
        raise ValueError("alpha must be in (0,1]")
    if not math.isfinite(tol) or tol <= 0 or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("tol and max_iter must be positive and finite")
    if len(seed) != len(m.ids) or len(m.incoming) != len(m.ids) or any(not math.isfinite(s) or s < 0 for s in seed):
        raise ValueError("seed must be finite, non-negative and match matrix dimensions")
    n = len(seed)
    for incoming in m.incoming:
        for i, weight in incoming:
            if not isinstance(i, int) or not 0 <= i < n or not math.isfinite(weight) or weight < 0:
                raise ValueError("matrix entries must have valid indices and finite non-negative weights")
    try:
        exact_system = _DyadicSystem(m, seed, alpha)
    except ValueError:
        exact_system = _FractionSystem(m, seed, alpha)
    contraction = exact_system.contraction
    if contraction >= 1:
        raise CannotCheck("represented sparse operator has no certified contraction")
    target = Fraction(tol)
    a = [alpha * s for s in seed]
    for k in range(1, max_iter + 1):
        nxt = [alpha * seed[j] + (1 - alpha) * sum(w * a[i] for i, w in m.incoming[j]) for j in range(len(seed))]
        if any(not math.isfinite(x) for x in nxt):
            raise CannotCheck("sparse floating-point iteration overflowed")
        delta = sum(abs(u - v) for u, v in zip(nxt, a, strict=True))
        a = nxt
        # The old delta <= tol test can underestimate error by roughly 1/alpha.
        # This only chooses when to check; the exact residual decides convergence.
        if delta <= tol * alpha or k == max_iter:
            residual = exact_system.residual(a)
            error_bound = residual / (1 - contraction)
            if error_bound <= target:
                return SparseConvergence(tuple(a), k, residual, contraction, error_bound)
            if delta == 0:
                raise CannotCheck("floating-point precision cannot certify the requested sparse error tolerance")
    raise CannotCheck(f"sparse iteration did not converge within {max_iter} steps")


def sparse_fixed_point(m: SparseMatrix, seed: Sequence[float], alpha: float, *, tol: float = 1e-12, max_iter: int = 100_000) -> tuple[list[float], int]:
    """Compatibility tuple API; use ``sparse_fixed_point_certified`` for the explicit bound."""
    result = sparse_fixed_point_certified(m, seed, alpha, tol=tol, max_iter=max_iter)
    return list(result.activation), result.iterations


def sparse_activation(ks: KnowledgeSpace, seed: Sequence[Fraction] | Sequence[float], alpha: float, *, revoked: Iterable[Hashable] = (), relevance=None, mode: NavigationMode = NavigationMode.WARRANTED, tol: float = 1e-12) -> tuple[dict[str, float], int, int]:
    """Returns (activation, iterations, incidences).  The seed is gated exactly as in the exact path."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    gated = [float(s) * float(_gate(amap[x].liveness(rv), mode)) for x, s in zip(ks.ids, seed, strict=True)]
    m = sparse_navigation_matrix(ks, revoked=rv, relevance=relevance, mode=mode)
    a, iters = sparse_fixed_point(m, gated, alpha, tol=tol)
    return dict(zip(ks.ids, a, strict=True)), iters, m.incidences


def check_sparse_agrees_with_exact(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, *, revoked: Iterable[Hashable] = (), tol: float = 1e-9) -> dict[str, Any]:
    rv = frozenset(revoked)
    exact = fixed_point(ks, seed, alpha, revoked=rv)
    approx, iters, inc = sparse_activation(ks, seed, float(alpha), revoked=rv, tol=1e-13)
    err = max(abs(approx[x] - float(exact[x])) for x in ks.ids)
    if err > tol:
        raise AssertionError(f"sparse solver disagrees with exact: max error {err}")
    return {"atoms": len(ks.ids), "incidences": inc, "iterations": iters, "max_abs_error": err}
