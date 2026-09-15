from __future__ import annotations

from fractions import Fraction
from typing import Sequence

F = Fraction


def expectation(weights: Sequence[F], values: Sequence[F]) -> F:
    assert len(weights) == len(values) and weights
    assert sum(weights, F(0)) == 1
    return sum((w * v for w, v in zip(weights, values)), F(0))


def complementarity_gap(weights: Sequence[F], loss_a: Sequence[F], loss_b: Sequence[F]) -> F:
    ea = expectation(weights, loss_a)
    eb = expectation(weights, loss_b)
    emin = expectation(weights, [min(a, b) for a, b in zip(loss_a, loss_b)])
    gap = min(ea, eb) - emin
    assert gap >= 0
    return gap


def misrouting_penalty(weights: Sequence[F], loss_a: Sequence[F], loss_b: Sequence[F], errors: Sequence[F]) -> F:
    assert len(weights) == len(loss_a) == len(loss_b) == len(errors)
    assert all(F(0) <= e <= F(1) for e in errors)
    return expectation(weights, [e * abs(a - b) for a, b, e in zip(loss_a, loss_b, errors)])


def hybrid_cost(weights: Sequence[F], loss_a: Sequence[F], loss_b: Sequence[F], overhead: F, errors: Sequence[F] | None = None) -> F:
    assert overhead >= 0
    base = expectation(weights, [min(a, b) for a, b in zip(loss_a, loss_b)])
    penalty = F(0) if errors is None else misrouting_penalty(weights, loss_a, loss_b, errors)
    return overhead + base + penalty


def best_monolith_cost(weights: Sequence[F], loss_a: Sequence[F], loss_b: Sequence[F]) -> F:
    return min(expectation(weights, loss_a), expectation(weights, loss_b))


def hybrid_strictly_wins(weights: Sequence[F], loss_a: Sequence[F], loss_b: Sequence[F], overhead: F, errors: Sequence[F] | None = None) -> bool:
    return hybrid_cost(weights, loss_a, loss_b, overhead, errors) < best_monolith_cost(weights, loss_a, loss_b)


def registered_witness() -> dict[str, object]:
    weights = [F(1, 2), F(1, 2)]
    a = [F(0), F(4)]
    b = [F(4), F(0)]
    gap = complementarity_gap(weights, a, b)
    pos = {
        "gap": str(gap),
        "best_monolith": str(best_monolith_cost(weights, a, b)),
        "hybrid_h1": str(hybrid_cost(weights, a, b, F(1))),
        "wins_h1": hybrid_strictly_wins(weights, a, b, F(1)),
        "epsilon_below": hybrid_strictly_wins(weights, a, b, F(1), [F(1, 5), F(1, 5)]),
        "epsilon_boundary": hybrid_strictly_wins(weights, a, b, F(1), [F(1, 4), F(1, 4)]),
        "epsilon_above": hybrid_strictly_wins(weights, a, b, F(1), [F(3, 10), F(3, 10)]),
    }
    na = [F(0), F(0)]
    nb = [F(1), F(1)]
    neg = {
        "gap": str(complementarity_gap(weights, na, nb)),
        "best_monolith": str(best_monolith_cost(weights, na, nb)),
        "hybrid_h1": str(hybrid_cost(weights, na, nb, F(1))),
        "wins_h1": hybrid_strictly_wins(weights, na, nb, F(1)),
    }
    return {"positive": pos, "negative_twin": neg}


if __name__ == "__main__":
    print(registered_witness())
