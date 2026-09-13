"""Exact finite deterministic stopping; None is infeasible, never zero cost."""

from fractions import Fraction as F


def _cost(x, positive=False):
    if not isinstance(x, F) or x < 0 or (positive and x == 0):
        raise ValueError("exact nonnegative charge required")


def validate(stops, edges, positive=False):
    if not stops or set(stops) != set(edges):
        raise ValueError("same nonempty finite state set required")
    for s, costs in stops.items():
        for c in costs:
            _cost(c)
        for e, t in edges[s]:
            _cost(e, positive)
            if t not in stops:
                raise ValueError("unknown successor")


def minimum(values):
    finite = [v for v in values if v is not None]
    return min(finite) if finite else None


def plus(e, value):
    return None if value is None else e + value


def bellman(stops, edges, values):
    return {s: minimum(list(stops[s]) + [plus(e, values[t]) for e, t in edges[s]])
            for s in stops}


def ranked_values(stops, edges, k):
    """Every cognitive transition consumes one unit of the integer allowance."""
    validate(stops, edges)
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative integer allowance required")
    values = {s: minimum(stops[s]) for s in stops}
    for _ in range(k):
        values = bellman(stops, edges, values)
    return values


def viable_states(stops, edges):
    validate(stops, edges)
    reached = {s for s in stops if stops[s]}
    while True:
        expanded = reached | {s for s in stops if any(t in reached for _, t in edges[s])}
        if expanded == reached:
            return frozenset(reached)
        reached = expanded


def positive_values(stops, edges):
    """Cycle removal leaves an optimal simple path of at most |S|-1 edges."""
    validate(stops, edges, positive=True)
    return ranked_values(stops, edges, len(stops) - 1)


def choose_stop_on_ties(stops, edges, values, state):
    """Given the certified VOC3 solution, choose with stop precedence.

    Positive edges are enforced; arbitrary supplied values are not certified here.
    """
    validate(stops, edges, positive=True)
    value = values[state]
    if value is None:
        raise ValueError("no finite terminating policy")
    for i, c in enumerate(stops[state]):
        if c == value:
            return ("stop", i)
    for i, (e, t) in enumerate(edges[state]):
        if plus(e, values[t]) == value:
            return ("cognitive", i)
    raise ValueError("values have no minimizing action")


def execute_stationary(stops, edges, policy, initial):
    """Independent trace evaluation: a cycle or dead end is infeasible."""
    state, seen, total, steps = initial, set(), F(0), 0
    while state not in seen:
        seen.add(state)
        kind, i = policy[state]
        if kind == "stop":
            return total + stops[state][i], steps
        if kind != "cognitive":
            return None, steps
        e, state = edges[state][i]
        total += e
        steps += 1
    return None, steps


def ranked_value(certified, cognitive, k, memo=None):
    """Compatibility helper: retain full state and allowance in a local cache."""
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative integer allowance required")
    for c in certified:
        _cost(c)
    for e, cs in cognitive:
        _cost(e)
        for c in cs:
            _cost(c)
    # A local cache cannot reuse another register's entries.
    cache = {}
    def solve(cs, remaining):
        key = (tuple(cs), remaining)
        if key not in cache:
            choices = list(cs)
            if remaining:
                choices += [plus(e, solve(nxt, remaining - 1)) for e, nxt in cognitive]
            cache[key] = minimum(choices)
        return cache[key]
    return solve(certified, k)
