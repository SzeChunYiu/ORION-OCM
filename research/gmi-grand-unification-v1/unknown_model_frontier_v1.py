"""Finite fixed-unknown-kernel policy vectors; exact rational arithmetic."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


@dataclass(frozen=True)
class Action:
    name: str
    cost: F
    rows: tuple  # One complete next-state probability row per fixed model.


@dataclass(frozen=True)
class Model:
    actions: tuple
    models: int
    goal: int
    abort: tuple


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, F)) or value < 0:
        raise ValueError("finite nonnegative exact rational required")
    return F(value)


def validate(model, horizon, start):
    n = len(model.actions)
    if type(horizon) is not int or horizon < 0 or type(start) is not int or not 0 <= start < n:
        raise ValueError("invalid finite horizon/start")
    if type(model.models) is not int or model.models < 1 or type(model.goal) is not int or not 0 <= model.goal < n:
        raise ValueError("invalid model register")
    if len(model.abort) != n or rational(model.abort[model.goal]) != 0 or model.actions[model.goal]:
        raise ValueError("goal must be stopped; explicit abort charges required")
    for charge in model.abort:
        rational(charge)
    for actions in model.actions:
        if len({a.name for a in actions}) != len(actions):
            raise ValueError("duplicate action name")
        for a in actions:
            rational(a.cost)
            if len(a.rows) != model.models:
                raise ValueError("kernel model dimension mismatch")
            for row in a.rows:
                if len(row) != n or sum(map(rational, row)) != 1:
                    raise ValueError("invalid complete rational kernel row")


def terminal(model, state):
    return (F(state != model.goal),)*model.models + (F(model.abort[state]),)*model.models


def pareto(points):
    return {v for v in points if not any(u != v and all(a <= b for a, b in zip(u, v)) for u in points)}


def frontier(model, horizon, start=0):
    validate(model, horizon, start)
    k, n = model.models, len(model.actions)
    count = dict(states=0, candidate_common_trees=0, weighted_coordinate_terms=0)

    @lru_cache(None)
    def visit(h, s):
        count["states"] += 1
        if s == model.goal or not h or not model.actions[s]:
            return {terminal(model, s): ("end", s)}
        candidates = {}
        for index, a in enumerate(model.actions[s]):
            successors = [t for t in range(n) if any(a.rows[j][t] for j in range(k))]
            choices = [visit(h-1, t) for t in successors]
            for children in product(*(tuple(c) for c in choices)):
                count["candidate_common_trees"] += 1
                vector = []
                for offset in (0, k):
                    for j in range(k):
                        value = F(a.cost) if offset else F(0)
                        for t, child in zip(successors, children):
                            value += a.rows[j][t]*child[offset+j]
                            count["weighted_coordinate_terms"] += 1
                        vector.append(value)
                branches = [None]*n
                for t, child, child_set in zip(successors, children, choices):
                    branches[t] = child_set[child]
                candidates.setdefault(tuple(vector), (s, index, tuple(branches)))
        return {v: candidates[v] for v in sorted(pareto(candidates))}

    return dict(points=visit(horizon, start), development=count)


def successful_costs(points, models):
    return tuple(sorted({v[models:] for v in points if all(x == 0 for x in v[:models])}))


def rectangular(model, horizon, start=0):
    """After each realized action nature chooses any candidate row anew."""
    validate(model, horizon, start)

    @lru_cache(None)
    def visit(h, s):
        if s == model.goal:
            return F(0), F(0)
        if not h or not model.actions[s]:
            return F(1), None
        failures, costs = [], []
        for a in model.actions[s]:
            children = [visit(h-1, t) for t in range(len(model.actions))]
            failures.append(max(sum(p*children[t][0] for t, p in enumerate(row)) for row in a.rows))
            if any(p and children[t][1] is None for row in a.rows for t, p in enumerate(row)):
                continue
            costs.append(F(a.cost)+max(sum(p*children[t][1] for t, p in enumerate(row) if p) for row in a.rows))
        return min(failures), min(costs) if costs else None

    failure, cost = visit(horizon, start)
    return dict(minimum_worst_failure=failure, successful_minimax_work=cost)


def posterior(prior, likelihood):
    if len(prior) != len(likelihood) or sum(map(rational, prior)) != 1:
        raise ValueError("invalid model prior")
    weights = tuple(rational(p)*rational(l) for p, l in zip(prior, likelihood))
    total = sum(weights)
    return tuple(w/total for w in weights) if total else None
