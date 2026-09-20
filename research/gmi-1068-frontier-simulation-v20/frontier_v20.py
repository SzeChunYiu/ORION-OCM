"""Actual finite attained images, maximal values and class representatives."""
from core_v20 import checked, order, subset


def maximal(relation, values):
    relation = order(relation)
    values = subset(values, len(relation))
    return tuple(x for x in values if all(
        not relation[x][y] or relation[y][x] for y in values))


def representatives(relation, values):
    relation = order(relation)
    result = []
    for x in maximal(relation, values):
        if not any(relation[x][y] and relation[y][x] for y in result):
            result.append(x)
    return tuple(result)


def downset(relation, values):
    relation = order(relation)
    values = subset(values, len(relation))
    return tuple(x for x in range(len(relation)) if any(relation[x][y] for y in values))


def cofinal(relation, values, retained):
    relation = order(relation)
    size = len(relation)
    values, retained = subset(values, size), subset(retained, size)
    return set(retained).issubset(values) and all(
        any(relation[x][y] for y in retained) for x in values)


def attained(context, histories):
    checked(context)
    histories = subset(histories, context.n)
    return tuple(sorted({context.values[h] for h in histories
                         if context.admitted[h] and context.defined[h]}))
