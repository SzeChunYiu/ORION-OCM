"""Independent residual-resource products and complete continuation refinement.

No production imports and no product-pair shortest-path computation.
"""
from itertools import product
from random import Random


def validate(machine):
    if type(machine) not in (tuple, list) or len(machine) != 2:
        raise ValueError("machine needs observation and transition tables")
    observations, transitions = machine
    sequence = lambda value: type(value) in (tuple, list)
    natural = lambda value: type(value) is int and value >= 0
    if not sequence(observations) or not observations or not all(map(natural, observations)):
        raise ValueError("nonempty natural observations required")
    if not sequence(transitions) or len(transitions) != len(observations):
        raise ValueError("transition rows must cover states")
    if not all(sequence(row) for row in transitions):
        raise ValueError("row must be a sequence")
    width = len(transitions[0])
    for row in transitions:
        if len(row) != width:
            raise ValueError("ragged action set")
        for edge in row:
            if edge is not None and (not sequence(edge) or len(edge) != 3
                                    or not all(map(natural, edge)) or edge[2] >= len(observations)):
                raise ValueError("invalid edge")
    return tuple(observations), tuple(tuple(None if e is None else tuple(e) for e in row)
                                      for row in transitions)


def colors(values):
    representatives, result = {}, []
    for value in values:
        if value not in representatives:
            representatives[value] = len(representatives)
        result.append(representatives[value])
    return tuple(result)


def budget_partition(machine, budget, hide_cost=False):
    observations, transitions = validate(machine)
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a natural number")
    stride = budget + 1
    output, rows = [], []
    for state, observation in enumerate(observations):
        for remaining in range(stride):
            output.append(observation)
            row = []
            for edge in transitions[state]:
                if edge is None or edge[1] > remaining:
                    row.append(None)
                else:
                    label = edge[0] if hide_cost else edge[:2]
                    row.append((label, edge[2] * stride + remaining - edge[1]))
            rows.append(row)
    partition = colors(output)
    while True:
        signatures = ((observation, tuple(None if edge is None else (edge[0], partition[edge[1]])
                                         for edge in row)) for observation, row in zip(output, rows))
        updated = colors(signatures)
        if updated == partition:
            return colors(updated[state * stride + budget] for state in range(len(observations)))
        partition = updated


def response(machine, state, word, budget=None, hide_cost=False):
    observations, transitions = validate(machine)
    if type(state) is not int or not 0 <= state < len(observations):
        raise ValueError("invalid state")
    if type(word) not in (tuple, list) or any(type(a) is not int or not 0 <= a < len(transitions[0]) for a in word):
        raise ValueError("invalid action word")
    if budget is not None and (type(budget) is not int or budget < 0):
        raise ValueError("invalid budget")
    def visit(current, suffix, remaining):
        if not suffix:
            return ("END", observations[current])
        edge = transitions[current][suffix[0]]
        if edge is None or (remaining is not None and edge[1] > remaining):
            return ("ILLEGAL", observations[current])
        label = edge[0] if hide_cost else edge[:2]
        residual = None if remaining is None else remaining - edge[1]
        return ("STEP", observations[current], label, visit(edge[2], suffix[1:], residual))
    return visit(state, tuple(word), budget)


def primary_machines():
    edges = (None,) + tuple(product(range(2), range(3), range(2)))
    for observations in product(range(2), repeat=2):
        for flat in product(edges, repeat=4):
            yield observations, (flat[:2], flat[2:])


def larger_machines():
    for size in range(3, 8):
        for seed in range(8):
            random = Random(65536 * size + seed)
            observations = tuple(random.randrange(2) for _ in range(size))
            rows = tuple(tuple(None if random.randrange(5) == 0 else
                               (random.randrange(2), random.randrange(4), random.randrange(size))
                               for _ in range(2)) for _ in range(size))
            yield observations, rows


def finite_bound(machine):
    observations, transitions = validate(machine)
    maximum = max((edge[1] for row in transitions for edge in row if edge is not None), default=0)
    return (len(observations) - len(set(observations))) * maximum
