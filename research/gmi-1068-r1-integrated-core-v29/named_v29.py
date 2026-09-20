"""Proper ambient injections with explicit object and arrow codecs."""
from dataclasses import dataclass, field
from core_v29 import (categories, index, named, nat, need, partial, presentations,
                      restrictions, same_record, syntax, tup)


@dataclass(frozen=True)
class NamedAdapter:
    category: object
    ambient_size: int
    arrow_labels: tuple
    object_decoder: tuple
    named: object = field(init=False)
    ambient_to_local: tuple = field(init=False)
    local_to_presented: tuple = field(init=False)
    presented_to_local: tuple = field(init=False)

    def __post_init__(self):
        categories.validate_category(self.category)
        nat(self.ambient_size)
        tup(self.arrow_labels)
        tup(self.object_decoder)
        size = len(self.category.table.rows)
        need(len(self.arrow_labels) == size, "arrow injection dimension")
        for label in self.arrow_labels:
            index(label, self.ambient_size)
        need(len(set(self.arrow_labels)) == size, "arrow labels must be injective")
        for obj in self.object_decoder:
            index(obj, self.category.object_count)
        need(tuple(sorted(self.object_decoder)) == tuple(range(self.category.object_count)),
             "external object decoder must be a permutation")
        presented_to_local = tuple(sorted(range(size), key=lambda i: self.arrow_labels[i]))
        local_to_presented = tuple(presented_to_local.index(i) for i in range(size))
        labels = tuple(self.arrow_labels[i] for i in presented_to_local)
        rows = tuple(tuple(None if self.category.table.rows[f][g] is None else
                           local_to_presented[self.category.table.rows[f][g]]
                           for g in presented_to_local) for f in presented_to_local)
        model = presentations.Presented(self.ambient_size, labels, partial.Table(rows))
        identities = tuple(self.arrow_labels[self.category.identities[obj]]
                           for obj in self.object_decoder)
        value = named.NamedPresented(model, identities)
        inverse = {label: i for i, label in enumerate(self.arrow_labels)}
        object.__setattr__(self, "named", value)
        object.__setattr__(self, "ambient_to_local",
                           tuple(inverse.get(i) for i in range(self.ambient_size)))
        object.__setattr__(self, "local_to_presented", local_to_presented)
        object.__setattr__(self, "presented_to_local", presented_to_local)


def checked_adapter(adapter):
    need(type(adapter) is NamedAdapter, "actual NamedAdapter required")
    expected = NamedAdapter(adapter.category, adapter.ambient_size,
                            adapter.arrow_labels, adapter.object_decoder)
    same_record(adapter, expected)
    return adapter


def named_response(adapter, tree):
    checked_adapter(adapter)
    return named.named_eval(adapter.named, tree)


def named_word_response(adapter, tree):
    checked_adapter(adapter)
    return named.named_word(adapter.named, tree)


def typed_query(adapter, tree):
    checked_adapter(adapter)
    syntax.validate_tree(tree, adapter.ambient_size, len(adapter.object_decoder))

    def visit(node):
        if node[0] == "arrow":
            value = adapter.ambient_to_local[node[1]]
            return None if value is None else ("arrow", value)
        if node[0] == "empty":
            return "empty", adapter.object_decoder[node[1]]
        left, right = visit(node[1]), visit(node[2])
        return None if left is None or right is None else ("seq", left, right)
    return visit(tree)


def encode_bundle(adapter, response):
    checked_adapter(adapter)
    if response is None:
        return None
    tup(response)
    need(len(response) == 3, "bundle shape")
    for value in response:
        nat(value)
    source, target, arrow = response
    index(arrow, len(adapter.category.table.rows))
    need((source, target) == (adapter.category.source[arrow], adapter.category.target[arrow]),
         "bundle endpoint mismatch")
    inverse = tuple(adapter.object_decoder.index(i) for i in range(adapter.category.object_count))
    return inverse[source], inverse[target], adapter.arrow_labels[arrow]


def restricted_adapter(adapter, allowed):
    checked_adapter(adapter)
    category, inclusion = restrictions.wide_restriction(adapter.category, allowed)
    result = NamedAdapter(category, adapter.ambient_size,
                          tuple(adapter.arrow_labels[i] for i in inclusion.arrow_map),
                          adapter.object_decoder)
    return result, inclusion
