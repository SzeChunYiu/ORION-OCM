"""Transport object names and arrow names through actual parent operations."""
from core_v25 import Typed, index, need, old_categories, old_partial, permutation
from presentations_v25 import Presented, checked
from syntax_v25 import map_tree
from trees_v25 import checked_category


def relabel_category(cat, arrow_map, object_map):
    checked_category(cat)
    n = len(cat.table.rows)
    permutation(arrow_map, n)
    permutation(object_map, cat.object_count)
    source, target, identities = [None] * n, [None] * n, [None] * cat.object_count
    for a in range(n):
        source[arrow_map[a]] = object_map[cat.source[a]]
        target[arrow_map[a]] = object_map[cat.target[a]]
    for o in range(cat.object_count):
        identities[object_map[o]] = arrow_map[cat.identities[o]]
    result = Typed(cat.object_count, tuple(source), tuple(target), tuple(identities),
                   old_partial.relabel(cat.table, arrow_map))
    old_categories.validate_category(result)
    return result


def map_response(cat, response, arrow_map, object_map):
    checked_category(cat)
    permutation(arrow_map, len(cat.table.rows))
    permutation(object_map, cat.object_count)
    if response is None:
        return None
    need(type(response) is tuple and len(response) == 3, "bundled response shape")
    for value in response:
        need(type(value) is int, "bundled response integer")
    index(response[2], len(cat.table.rows))
    a = response[2]
    need(response == (cat.source[a], cat.target[a], a), "bundled response endpoints")
    return object_map[response[0]], object_map[response[1]], arrow_map[a]


def relabel_presented(model, ambient_map):
    checked(model)
    permutation(ambient_map, model.ambient_size)
    labels = tuple(sorted(ambient_map[label] for label in model.labels))
    local_map = tuple(labels.index(ambient_map[label]) for label in model.labels)
    return Presented(model.ambient_size, labels, old_partial.relabel(model.table, local_map))
