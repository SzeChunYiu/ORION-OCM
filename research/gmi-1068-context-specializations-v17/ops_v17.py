"""Codomain maps and duality retain the actual partial evaluator domain."""
from core_v17 import Context, checked, order


def map_properties(source_order, target_order, mapping):
    source, target = order(source_order), order(target_order)
    if type(mapping) is not tuple or len(mapping) != len(source):
        raise ValueError("one mapped index per source value required")
    if any(type(value) is not int or not 0 <= value < len(target) for value in mapping):
        raise ValueError("mapped index outside target")
    monotone = all(not source[a][b] or target[mapping[a]][mapping[b]]
                   for a in range(len(source)) for b in range(len(source)))
    reflecting = all(not target[mapping[a]][mapping[b]] or source[a][b]
                     for a in range(len(source)) for b in range(len(source)))
    return monotone, reflecting, len(set(mapping)) == len(mapping)


def map_values(context, target_order, mapping):
    checked(context)
    target = order(target_order)
    map_properties(context.order, target, mapping)
    values = tuple(mapping[v] if defined else None
                   for v, defined in zip(context.values, context.defined))
    return Context(context.n, len(target), context.admitted, context.defined, values, target)


def postcompose(context, target_order, mapping):
    checked(context)
    if not map_properties(context.order, target_order, mapping)[0]:
        raise ValueError("global codomain map is not monotone")
    return map_values(context, target_order, mapping)


def dual(context):
    checked(context)
    relation = tuple(tuple(context.order[b][a] for b in range(context.m))
                     for a in range(context.m))
    return Context(context.n, context.m, context.admitted, context.defined, context.values, relation)
