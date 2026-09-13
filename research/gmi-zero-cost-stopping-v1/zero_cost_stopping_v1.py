"""Exact finite deterministic proper stopping; None denotes infeasibility."""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Graph:
    terminals: tuple[tuple[Fraction, ...], ...]
    edges: tuple[tuple[tuple[int, Fraction], ...], ...]


def _cost(value):
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)) or value < 0:
        raise ValueError("costs must be exact nonnegative rational numbers")
    return Fraction(value)


def validate(graph):
    size = len(graph.terminals)
    if size == 0 or len(graph.edges) != size:
        raise ValueError("finite nonempty common state register required")
    for row in graph.terminals:
        for cost in row:
            _cost(cost)
    for row in graph.edges:
        for target, cost in row:
            if type(target) is not int or not 0 <= target < size:
                raise ValueError("edge target outside state register")
            _cost(cost)


def solve(graph):
    """Return (cost, remaining edges) labels and proper indexed actions.

    Actions are ("stop", terminal_index), ("edge", edge_index), or None.
    None is never an uncharged successful terminal action.
    """
    validate(graph)
    labels = [min(((_cost(c), 0) for c in row), default=None)
              for row in graph.terminals]
    for _ in range(len(labels) - 1):
        previous = labels
        labels = previous.copy()
        for state, row in enumerate(graph.edges):
            for target, cost in row:
                if previous[target] is None:
                    continue
                value, length = previous[target]
                candidate = (_cost(cost) + value, length + 1)
                if labels[state] is None or candidate < labels[state]:
                    labels[state] = candidate
    policy = []
    for state, label in enumerate(labels):
        if label is None:
            policy.append(None)
            continue
        chosen = None
        for index, cost in enumerate(graph.terminals[state]):
            if (_cost(cost), 0) == label:
                chosen = ("stop", index)
                break
        if chosen is None:
            for index, (target, cost) in enumerate(graph.edges[state]):
                suffix = labels[target]
                if suffix is not None and (_cost(cost) + suffix[0], 1 + suffix[1]) == label:
                    chosen = ("edge", index)
                    break
        if chosen is None:
            raise RuntimeError("constructed label has no exact progress witness")
        policy.append(chosen)
    return tuple(labels), tuple(policy)
