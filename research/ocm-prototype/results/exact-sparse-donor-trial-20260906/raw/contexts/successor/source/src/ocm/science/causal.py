"""Controlled causal worlds with a known structural causal model (M10 §5): confounding, mediator,
collider, transport across environments; observation vs intervention; exact oracle effects.

Linear-Gaussian SCMs with fixed seeds.  `observe(n)` samples the observational distribution;
`intervene(var, value, n)` samples do(var = value).  The oracle total effect of X on Y is the
sum over directed paths of edge products.  Estimators: naive regression slope (observational),
back-door adjusted slope, interventional contrast.  Identification: the registered assumption set
that licenses a causal claim (`randomised`, `backdoor:{Z}`), checked against the world's structure
by the checker only.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class SCM:
    world_id: str
    variables: tuple[str, ...]
    parents: Mapping[str, tuple[tuple[str, float], ...]]     # var → ((parent, coefficient), …)
    noise: float = 1.0
    seed: str = "OCM-M10-SCM"

    def order(self) -> list[str]:
        out, seen = [], set()

        def visit(v):
            if v in seen:
                return
            for p, _ in self.parents.get(v, ()):
                visit(p)
            seen.add(v)
            out.append(v)
        for v in self.variables:
            visit(v)
        return out

    def sample(self, n: int, do: Mapping[str, float] | None = None, *, env_shift: Mapping[str, float] | None = None, tag: str = "") -> list[dict[str, float]]:
        rng = random.Random(f"{self.seed}|{self.world_id}|{n}|{sorted((do or {}).items())}|{tag}")
        rows = []
        for _ in range(n):
            row: dict[str, float] = {}
            for v in self.order():
                if do and v in do:
                    row[v] = float(do[v])
                    continue
                val = sum(c * row[p] for p, c in self.parents.get(v, ())) + rng.gauss(0.0, self.noise) + (env_shift or {}).get(v, 0.0)
                row[v] = val
            rows.append(row)
        return rows

    def total_effect(self, x: str, y: str) -> float:
        """Sum over directed paths x → … → y of the product of coefficients."""
        def paths(v: str) -> float:
            if v == x:
                return 1.0
            return sum(c * paths(p) for p, c in self.parents.get(v, ()))
        return paths(y) if y != x else 1.0

    def backdoor_set(self, x: str, y: str) -> frozenset[str]:
        """For these small worlds: the parents of x that are not descendants of x (sufficient here)."""
        return frozenset(p for p, _ in self.parents.get(x, ()))


def slope(rows: Sequence[Mapping[str, float]], x: str, y: str, adjust: Sequence[str] = ()) -> float:
    """OLS slope of y on x (with optional adjustment covariates) by normal equations."""
    cols = [x, *adjust]
    n = len(rows)
    X = [[1.0] + [r[c] for c in cols] for r in rows]
    Y = [r[y] for r in rows]
    k = len(cols) + 1
    # X^T X and X^T Y
    xtx = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    xty = [sum(X[i][a] * Y[i] for i in range(n)) for a in range(k)]
    # solve by Gaussian elimination
    M = [row[:] + [xty[i]] for i, row in enumerate(xtx)]
    for c in range(k):
        piv = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        for r in range(k):
            if r != c and M[c][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(k + 1)]
    beta = [M[i][k] / M[i][i] if M[i][i] else 0.0 for i in range(k)]
    return beta[1]


def interventional_contrast(scm: SCM, x: str, y: str, n: int = 400) -> float:
    a = scm.sample(n, do={x: 1.0}, tag="do1")
    b = scm.sample(n, do={x: 0.0}, tag="do0")
    return sum(r[y] for r in a) / n - sum(r[y] for r in b) / n


WORLDS: dict[str, SCM] = {
    "confounded": SCM("confounded", ("Z", "X", "Y"), {"X": (("Z", 1.0),), "Y": (("Z", 1.5), ("X", 0.5))}),
    "mediator": SCM("mediator", ("X", "M", "Y"), {"M": (("X", 1.0),), "Y": (("M", 0.8),)}),
    "collider": SCM("collider", ("X", "Y", "C"), {"C": (("X", 1.0), ("Y", 1.0))}),
    "no_effect_confounded": SCM("no_effect_confounded", ("Z", "X", "Y"), {"X": (("Z", 1.0),), "Y": (("Z", 1.0),)}),
    "chain_transport": SCM("chain_transport", ("X", "M", "Y"), {"M": (("X", 0.7),), "Y": (("M", 1.0),)}),
}


@dataclass(frozen=True)
class CausalEstimate:
    method: str
    value: float
    assumptions: tuple[str, ...]
    identified: bool


def estimate(scm: SCM, x: str, y: str, method: str, n: int = 400) -> CausalEstimate:
    if method == "naive":
        return CausalEstimate("naive_regression", slope(scm.sample(n, tag="obs"), x, y), (), False)
    if method == "backdoor":
        z = sorted(scm.backdoor_set(x, y))
        return CausalEstimate("backdoor_adjusted", slope(scm.sample(n, tag="obs"), x, y, z), (f"backdoor:{','.join(z)}",), True)
    if method == "intervention":
        return CausalEstimate("randomised_intervention", interventional_contrast(scm, x, y, n), ("randomised",), True)
    if method == "collider_adjusted":
        return CausalEstimate("adjusted_on_collider", slope(scm.sample(n, tag="obs"), x, y, ["C"]), ("backdoor:C",), False)
    raise ValueError(method)
