"""Declared task interfaces and source-faithful total-relation composition."""
from dataclasses import dataclass
from core_v27 import index, nat, need, stochastic, tup


def interface(ambient, values):
    nat(ambient)
    tup(values)
    for value in values:
        index(value, ambient)
    need(len(set(values)) == len(values), "duplicate interface label")
    return tuple(sorted(values))


def pairs(ambient, values):
    nat(ambient)
    tup(values)
    for pair in values:
        need(type(pair) is tuple and len(pair) == 2, "relation pair required")
        for value in pair:
            index(value, ambient)
    need(len(set(values)) == len(values), "duplicate relation pair")
    return tuple(sorted(values))


@dataclass(frozen=True)
class Task:
    ambient: int
    source: tuple
    target: tuple
    pairs: tuple

    def __post_init__(self):
        source = interface(self.ambient, self.source)
        target = interface(self.ambient, self.target)
        relation = pairs(self.ambient, self.pairs)
        need(all(x in source and y in target for x, y in relation), "pair outside interfaces")
        need(all(any(x == s for x, _ in relation) for s in source), "task not total on inputs")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "pairs", relation)


def checked(task):
    need(type(task) is Task, "actual Task required")
    return task


def from_relation(ambient, relation):
    relation = pairs(ambient, relation)
    return Task(ambient, tuple(sorted({x for x, _ in relation})),
                tuple(sorted({y for _, y in relation})), relation)


def as_relation(task):
    checked(task)
    targets = {value: i for i, value in enumerate(task.target)}
    return stochastic.Relation(len(task.source), len(task.target), tuple(
        frozenset(targets[y] for x, y in task.pairs if x == source) for source in task.source))


def decode(task):
    checked(task)
    return task.pairs


def identity_task(ambient, values):
    values = interface(ambient, values)
    return Task(ambient, values, values, tuple((x, x) for x in values))


def typed_compose(first, second):
    checked(first)
    checked(second)
    need(first.ambient == second.ambient and first.target == second.source,
         "typed task interfaces mismatch")
    result = stochastic.compose_relation(as_relation(first), as_relation(second))
    return Task(first.ambient, first.source, second.target, tuple(
        (first.source[i], second.target[j]) for i, row in enumerate(result.rows) for j in sorted(row)))


def regular(first, second):
    checked(first)
    checked(second)
    need(first.ambient == second.ambient, "ambient substrate mismatch")
    return set(first.target) <= set(second.source)


def inclusion(first, second):
    need(regular(first, second), "interface inclusion fails")
    return Task(first.ambient, first.target, second.source, tuple((x, x) for x in first.target))


def regular_compose(first, second):
    if not regular(first, second):
        return None
    return typed_compose(typed_compose(first, inclusion(first, second)), second)
