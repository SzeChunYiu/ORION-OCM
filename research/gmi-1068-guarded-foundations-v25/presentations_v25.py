"""Lawful subtype operations retain a declared ambient label interface."""
from dataclasses import dataclass
from core_v25 import Table, index, nat, need, old_partial
from syntax_v25 import leaves, validate_tree


@dataclass(frozen=True)
class Presented:
    ambient_size: int
    labels: tuple
    table: Table

    def __post_init__(self):
        nat(self.ambient_size)
        need(type(self.labels) is tuple, "carrier labels must be tuple")
        for label in self.labels:
            index(label, self.ambient_size)
        need(tuple(sorted(set(self.labels))) == self.labels, "ascending unique labels")
        need(type(self.table) is Table and len(self.table.rows) == len(self.labels),
             "actual subtype table dimension")
        old_partial.validate(self.table)


def checked(model):
    need(type(model) is Presented, "expected Presented")
    return model


def padded(model):
    checked(model)
    lookup = {label: i for i, label in enumerate(model.labels)}
    rows = []
    for x in range(model.ambient_size):
        row = []
        for y in range(model.ambient_size):
            value = None
            if x in lookup and y in lookup:
                local = model.table.rows[lookup[x]][lookup[y]]
                if local is not None:
                    value = model.labels[local]
            row.append(value)
        rows.append(tuple(row))
    return Table(tuple(rows))


def carrier_from_table(model):
    table = padded(model)
    return tuple(i for i, row in enumerate(table.rows)
                 if any(value is not None for value in row))


def raw_eval(model, tree):
    checked(model)
    validate_tree(tree, model.ambient_size, model.ambient_size)
    lookup = {label: i for i, label in enumerate(model.labels)}
    units = {model.labels[i] for i in old_partial.units(model.table)}

    def visit(node):
        if node[0] == "arrow":
            return node[1] if node[1] in lookup else None
        if node[0] == "empty":
            return node[1] if node[1] in units else None
        left, right = visit(node[1]), visit(node[2])
        if left is None or right is None:
            return None
        local = model.table.rows[lookup[left]][lookup[right]]
        return None if local is None else model.labels[local]
    return visit(tree)


def guarded_word(model, tree):
    checked(model)
    validate_tree(tree, model.ambient_size, model.ambient_size)
    lookup = {label: i for i, label in enumerate(model.labels)}
    units = {model.labels[i] for i in old_partial.units(model.table)}
    ls = leaves(tree)
    if any(leaf[1] not in lookup or (leaf[0] == "empty" and leaf[1] not in units)
           for leaf in ls):
        return None
    value = old_partial.word(model.table, tuple(lookup[leaf[1]] for leaf in ls))
    return None if value is None else model.labels[value]


def core_signature(model):
    checked(model)
    return model.labels, padded(model).rows
