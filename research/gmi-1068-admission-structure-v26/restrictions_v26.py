"""Actual same-object wide restrictions with inherited operations."""
from core_v26 import Table, Typed, checked_category, index, need
from functors_v26 import Functor


def checked_allowed(category, allowed):
    checked_category(category)
    need(type(allowed) is tuple, "allowed arrows must be tuple")
    for arrow in allowed:
        index(arrow, len(category.table.rows))
    need(len(set(allowed)) == len(allowed), "duplicate allowed arrow")
    return tuple(sorted(allowed))


def admission_laws(category, allowed):
    admitted = set(checked_allowed(category, allowed))
    identities = all(identity in admitted for identity in category.identities)
    closed = all(category.table.rows[f][g] is None or category.table.rows[f][g] in admitted
                 for f in admitted for g in admitted)
    return identities, closed


def wide_restriction(category, allowed):
    labels = checked_allowed(category, allowed)
    need(all(admission_laws(category, labels)), "restriction must retain identities and composites")
    local = {arrow: i for i, arrow in enumerate(labels)}
    rows = tuple(tuple(None if category.table.rows[f][g] is None
                       else local[category.table.rows[f][g]] for g in labels) for f in labels)
    result = Typed(category.object_count, tuple(category.source[f] for f in labels),
                   tuple(category.target[f] for f in labels),
                   tuple(local[e] for e in category.identities), Table(rows))
    checked_category(result)
    return result, Functor(result, category, tuple(range(category.object_count)), labels)
