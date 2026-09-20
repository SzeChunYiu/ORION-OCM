"""Actual thin processes, generated histories and four distinct observation views."""
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product
from core_v28 import Encoded, categories, checked_history, contexts, history, index, need, partial, tup

EDGES = ((0, 0), (0, 1), (1, 0), (1, 1))
DECODER = (Fraction(0), Fraction(1))
ORDER = ((True, True), (False, True))


def history_roster():
    result = []
    for length in range(4):
        for start in range(2):
            for suffix in product(range(2), repeat=length):
                walk = (start,) + suffix
                result.append((start, tuple(2 * a + b for a, b in zip(walk, walk[1:]))))
    return tuple(result)


ROSTER = history_roster()


@dataclass(frozen=True)
class ReverseModel:
    admission: tuple
    state_values: tuple
    state_defined: tuple
    graph: object = field(init=False)
    category: object = field(init=False)
    ambient_to_local: tuple = field(init=False)
    local_to_ambient: tuple = field(init=False)

    def __post_init__(self):
        for values, size in ((self.admission, 4), (self.state_values, 2), (self.state_defined, 2)):
            tup(values)
            need(len(values) == size, "model dimension")
        need(all(type(x) is bool for x in self.admission + self.state_defined), "strict Boolean flags")
        for value in self.state_values:
            index(value, 2)
        need(self.admission[0] and self.admission[3], "reflexive relation required")
        for a, b, c in product(range(2), repeat=3):
            need(not (self.admission[2*a+b] and self.admission[2*b+c]) or self.admission[2*a+c],
                 "transitive relation required")
        local = tuple(i for i, bit in enumerate(self.admission) if bit)
        ambient = tuple(local.index(i) if bit else None for i, bit in enumerate(self.admission))
        edges = tuple(EDGES[i] for i in local)
        rows = tuple(tuple(ambient[2*a+d] if b == c else None for c, d in edges) for a, b in edges)
        category = categories.Typed(2, tuple(a for a, _ in edges), tuple(b for _, b in edges),
                                    (ambient[0], ambient[3]), partial.Table(rows))
        categories.validate_category(category)
        for name, value in (("graph", history.Graph(2, EDGES)), ("category", category),
                            ("ambient_to_local", ambient), ("local_to_ambient", local)):
            object.__setattr__(self, name, value)


def checked(model, path):
    need(type(model) is ReverseModel, "ReverseModel required")
    return checked_history((model.graph.vertices, model.graph.edges), path)


def generated_admitted(model, path):
    canonical, _ = checked(model, path)
    return history.admitted(model.graph, model.admission, canonical)


def reverse_observe(model, path):
    canonical, end = checked(model, path)
    admitted = history.admitted(model.graph, model.admission, canonical)
    defined = model.state_defined[end]
    value = model.state_values[end] if defined else None
    encoded = Encoded(contexts.Context(1, 2, (admitted,), (defined,), (value,), ORDER),
                      (canonical,), DECODER)
    return encoded.observe(0)


def reverse_context(model):
    need(type(model) is ReverseModel, "ReverseModel required")
    flags, defined, values = [], [], []
    for path in ROSTER:
        _, end = checked(model, path)
        flags.append(generated_admitted(model, path))
        defined.append(model.state_defined[end])
        values.append(model.state_values[end] if defined[-1] else None)
    return Encoded(contexts.Context(30, 2, tuple(flags), tuple(defined), tuple(values), ORDER),
                   ROSTER, DECODER)


def views(model):
    encoded = reverse_context(model)
    tags = tuple((path, encoded.observe(i)) for i, path in enumerate(ROSTER))
    return {
        "weak_state": tuple((i, model.state_values[i], model.state_defined[i]) for i in range(2)),
        "active_domain": tuple((path, tag[1]) for path, tag in tags if tag[0] == "VALUE"),
        "tagged": tags,
        "domain_signature": tuple((path, encoded.context.admitted[i]) for i, path in enumerate(ROSTER)),
    }
