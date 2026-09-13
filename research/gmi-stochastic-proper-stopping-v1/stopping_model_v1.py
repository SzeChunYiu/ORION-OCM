"""Exact known finite MDP register; no sampling or native task execution."""
from dataclasses import dataclass
from fractions import Fraction as F


def rational(value):
    if type(value) not in (int, F):
        raise ValueError("exact int or Fraction required")
    return F(value)


@dataclass(frozen=True)
class Action:
    cost: F
    probability: tuple


@dataclass(frozen=True)
class Model:
    rows: tuple

    def __post_init__(self):
        n = len(self.rows)
        normalized = []
        for actions in self.rows:
            clean = []
            for a in actions:
                cost = rational(a.cost)
                p = tuple(rational(x) for x in a.probability)
                if cost < 0 or len(p) != n + 1:
                    raise ValueError("nonnegative cost and n+1 successors required")
                if any(x < 0 for x in p) or sum(p) != 1:
                    raise ValueError("probabilities must be nonnegative and sum to one")
                clean.append(Action(cost, p))
            normalized.append(tuple(clean))
        object.__setattr__(self, "rows", tuple(normalized))

    @property
    def goal(self):
        return len(self.rows)


def action(cost, *probabilities):
    return Action(cost, probabilities)


def safe_actions(model, domain):
    allowed = set(domain) | {model.goal}
    return {
        s: tuple(i for i, a in enumerate(model.rows[s])
                 if all(not p or y in allowed
                        for y, p in enumerate(a.probability)))
        for s in sorted(domain)
    }


def goal_ancestors(model, choices):
    reached = {model.goal}
    while True:
        grown = reached | {
            s for s, indices in choices.items()
            if any(any(p and y in reached for y, p in
                       enumerate(model.rows[s][i].probability)) for i in indices)
        }
        if grown == reached:
            return reached - {model.goal}
        reached = grown


def viable_domain(model):
    domain = set(range(model.goal))
    while True:
        revised = goal_ancestors(model, safe_actions(model, domain))
        if revised == domain:
            return tuple(sorted(domain))
        domain = revised


def solve_linear(matrix, rhs):
    """Gauss-Jordan with exact rationals; rhs is a vector."""
    n = len(matrix)
    rows = [[F(x) for x in row] + [F(rhs[i])]
            for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            raise ValueError("singular linear system")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [x - scale*y for x, y in zip(rows[i], rows[col])]
    return tuple(row[-1] for row in rows)
