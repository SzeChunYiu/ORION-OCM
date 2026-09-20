"""Lawful total maps; failure reflection is a theorem, not a constructor premise."""
from dataclasses import dataclass
from core_v26 import checked_category, checked_path, index, need, old_partial, syntax


@dataclass(frozen=True)
class Functor:
    source: object
    target: object
    object_map: tuple
    arrow_map: tuple

    def __post_init__(self):
        source, target = checked_category(self.source), checked_category(self.target)
        for mapping, size, bound in (
            (self.object_map, source.object_count, target.object_count),
            (self.arrow_map, len(source.table.rows), len(target.table.rows)),
        ):
            need(type(mapping) is tuple and len(mapping) == size, "map shape")
            for value in mapping:
                index(value, bound)
        for arrow, mapped in enumerate(self.arrow_map):
            need(target.source[mapped] == self.object_map[source.source[arrow]]
                 and target.target[mapped] == self.object_map[source.target[arrow]], "map endpoints")
        for obj, identity in enumerate(source.identities):
            need(self.arrow_map[identity] == target.identities[self.object_map[obj]], "map identity")
        for f, row in enumerate(source.table.rows):
            for g, product in enumerate(row):
                if product is not None:
                    need(target.table.rows[self.arrow_map[f]][self.arrow_map[g]]
                         == self.arrow_map[product], "map composition")


def checked_functor(functor):
    need(type(functor) is Functor, "expected Functor")
    return functor


def object_injective(functor):
    checked_functor(functor)
    return len(set(functor.object_map)) == len(functor.object_map)


def map_response(functor, response):
    checked_functor(functor)
    if response is None:
        return None
    need(type(response) is tuple and len(response) == 3, "response shape")
    for value in response:
        need(type(value) is int, "response integer")
    arrow = response[2]
    index(arrow, len(functor.source.table.rows))
    need(response == (functor.source.source[arrow], functor.source.target[arrow], arrow),
         "response endpoints")
    return (functor.object_map[response[0]], functor.object_map[response[1]],
            functor.arrow_map[arrow])


def map_tree(functor, tree):
    checked_functor(functor)
    syntax.validate_tree(tree, len(functor.source.table.rows), functor.source.object_count)

    def visit(node):
        if node[0] == "arrow":
            return ("arrow", functor.arrow_map[node[1]])
        if node[0] == "empty":
            return ("empty", functor.object_map[node[1]])
        return ("seq", visit(node[1]), visit(node[2]))
    return visit(tree)


def map_path(functor, path):
    checked_functor(functor)
    start, word = checked_path(functor.source, path)
    return functor.object_map[start], tuple(functor.arrow_map[a] for a in word)


def path_response(category, path):
    start, word = checked_path(category, path)
    if not word:
        return start, start, category.identities[start]
    if category.source[word[0]] != start:
        return None
    value = old_partial.word(category.table, word)
    return None if value is None else (start, category.target[value], value)
