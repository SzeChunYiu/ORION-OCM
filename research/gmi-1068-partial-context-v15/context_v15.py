"""Finite partial contexts with explicit admission and evaluation domains."""
from dataclasses import dataclass


def sequence(value):
    if type(value) not in (tuple, list):
        raise ValueError("expected a list or tuple")
    return tuple(value)


def index(value, size):
    if type(value) is not int or not 0 <= value < size:
        raise ValueError("index outside its declared set")


@dataclass(frozen=True)
class Context:
    n: int
    m: int
    admitted: tuple
    defined: tuple
    values: tuple
    order: tuple

    def __post_init__(self):
        if any(type(v) is not int or v < 0 for v in (self.n, self.m)):
            raise ValueError("dimensions must be nonnegative integers")
        admitted, defined, values = map(sequence, (self.admitted, self.defined, self.values))
        if any(len(v) != self.n for v in (admitted, defined, values)):
            raise ValueError("history dimension mismatch")
        if any(type(v) is not bool for v in admitted + defined):
            raise ValueError("domain flags must be Boolean")
        for flag, value in zip(defined, values):
            if flag:
                index(value, self.m)
            elif value is not None:
                raise ValueError("unevaluated entries must use None")
        order = tuple(sequence(row) for row in sequence(self.order))
        if len(order) != self.m or any(len(row) != self.m for row in order):
            raise ValueError("value order dimension mismatch")
        if any(type(v) is not bool for row in order for v in row):
            raise ValueError("order entries must be Boolean")
        if any(not order[i][i] for i in range(self.m)):
            raise ValueError("value relation is not reflexive")
        if any(order[i][j] and order[j][k] and not order[i][k]
               for i in range(self.m) for j in range(self.m) for k in range(self.m)):
            raise ValueError("value relation is not transitive")
        for name, value in (("admitted", admitted), ("defined", defined),
                            ("values", values), ("order", order)):
            object.__setattr__(self, name, value)


def observe(context, history):
    if type(context) is not Context:
        raise ValueError("expected a validated Context")
    index(history, context.n)
    if not context.admitted[history]:
        return ("ILLEGAL", None)
    if not context.defined[history]:
        return ("UNDEFINED", None)
    return ("VALUE", context.values[history])


def domain(context):
    if type(context) is not Context:
        raise ValueError("expected a validated Context")
    return tuple(i for i in range(context.n) if context.admitted[i] and context.defined[i])


def compare(context, first, second):
    left, right = observe(context, first), observe(context, second)
    if left[0] != "VALUE" or right[0] != "VALUE":
        raise ValueError("comparison is defined only on the evaluated admitted domain")
    return context.order[left[1]][right[1]]


def quotient(context):
    remaining = set(domain(context))
    classes = []
    while remaining:
        first = min(remaining)
        block = frozenset(i for i in remaining
                          if compare(context, first, i) and compare(context, i, first))
        classes.append(block)
        remaining.difference_update(block)
    ordered = tuple(classes)
    relation = tuple(tuple(compare(context, min(a), min(b)) for b in ordered) for a in ordered)
    return ordered, relation


def opposite(context, first, second, low, high, allowed):
    """Construct opposite indicator evaluators on D=P∩E.

    allowed receives only the evaluator values on domain(context), in increasing
    history order. The first function is low at first and high elsewhere on D;
    the second reverses those values. Illegal ambient evaluations are never exposed
    to the predicate. The caller supplies a mathematical membership predicate.
    """
    selected = domain(context)
    for history in (first, second):
        index(history, context.n)
        if history not in selected:
            raise ValueError("reversal witness is not admitted and evaluated")
    for value in (low, high):
        index(value, context.m)
    if first == second or not context.order[low][high] or context.order[high][low]:
        raise ValueError("distinct histories and a strict value pair are required")
    if not callable(allowed):
        raise ValueError("a declared evaluator membership predicate is required")
    results = []
    for at_first, elsewhere in ((low, high), (high, low)):
        values = list(context.values)
        for history in selected:
            values[history] = at_first if history == first else elsewhere
        member = allowed(tuple(values[history] for history in selected))
        if type(member) is not bool or not member:
            raise ValueError("constructed evaluator is outside the permitted class")
        results.append(Context(context.n, context.m, context.admitted, context.defined,
                               tuple(values), context.order))
    return tuple(results)
