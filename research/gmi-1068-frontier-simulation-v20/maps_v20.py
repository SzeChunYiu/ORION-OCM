"""Partial evaluation transport; guarded monotonicity is a separate condition."""
from core_v20 import Context, checked, index, nat, need, order, subset


def mapping(values, source_size, target_size):
    need(type(values) is tuple and len(values) == source_size, "partial map dimension")
    for value in values:
        if value is not None:
            index(value, target_size)
    return values


def guarded(source_order, target_order, values):
    source_order, target_order = order(source_order), order(target_order)
    values = mapping(values, len(source_order), len(target_order))
    return all(not source_order[x][y] or values[x] is None or
               (values[y] is not None and target_order[values[x]][values[y]])
               for x in range(len(values)) for y in range(len(values)))


def image(values, selected, target_size):
    nat(target_size)
    need(type(values) is tuple, "partial map tuple")
    values = mapping(values, len(values), target_size)
    selected = subset(selected, len(values))
    return tuple(sorted({values[x] for x in selected if values[x] is not None}))


def postcompose(context, target_order, values):
    checked(context)
    target_order = order(target_order)
    values = mapping(values, context.m, len(target_order))
    output = tuple(values[context.values[h]] if context.defined[h] else None
                   for h in range(context.n))
    return Context(context.n, len(target_order), context.admitted,
                   tuple(value is not None for value in output), output, target_order)
