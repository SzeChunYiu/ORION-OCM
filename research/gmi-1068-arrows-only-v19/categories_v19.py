"""Finite typed construction and explicit bundled-arrow operations."""
from dataclasses import dataclass
from partial_v19 import Table, index, need, units, validate


@dataclass(frozen=True)
class Typed:
    object_count: int
    source: tuple
    target: tuple
    identities: tuple
    table: Table

    def __post_init__(self):
        need(type(self.object_count) is int and self.object_count >= 0, "object count")
        need(type(self.table) is Table, "expected Table")
        size = len(self.table.rows)
        for endpoints in (self.source, self.target):
            need(type(endpoints) is tuple and len(endpoints) == size, "endpoint shape")
            for obj in endpoints:
                index(obj, self.object_count)
        need(type(self.identities) is tuple
             and len(self.identities) == self.object_count, "identity shape")
        for identity in self.identities:
            index(identity, size)


def validate_category(cat):
    need(type(cat) is Typed, "expected Typed")
    size, rows = len(cat.table.rows), cat.table.rows
    for obj, identity in enumerate(cat.identities):
        need(cat.source[identity] == obj == cat.target[identity], "identity endpoints")
    for f in range(size):
        need(rows[cat.identities[cat.source[f]]][f] == f, "left identity")
        need(rows[f][cat.identities[cat.target[f]]] == f, "right identity")
        for g in range(size):
            value = rows[f][g]
            need((value is not None) == (cat.target[f] == cat.source[g]), "composability")
            if value is not None:
                need(cat.source[value] == cat.source[f]
                     and cat.target[value] == cat.target[g], "composite endpoints")
    for f in range(size):
        for g in range(size):
            value = rows[f][g]
            if value is not None:
                for h in range(size):
                    if cat.target[g] == cat.source[h]:
                        need(rows[value][h] == rows[f][rows[g][h]], "typed associativity")


def reconstruct(table):
    validate(table)
    identities = units(table)
    object_of = {identity: obj for obj, identity in enumerate(identities)}
    source, target = [], []
    for arrow in range(len(table.rows)):
        left = [e for e in identities if table.rows[e][arrow] == arrow]
        right = [e for e in identities if table.rows[arrow][e] == arrow]
        need(len(left) == len(right) == 1, "derived units are not unique")
        source.append(object_of[left[0]])
        target.append(object_of[right[0]])
    result = Typed(len(identities), tuple(source), tuple(target), identities, table)
    validate_category(result)
    return result


def flatten(cat):
    validate_category(cat)
    rows = tuple(tuple(cat.table.rows[f][g] if cat.target[f] == cat.source[g] else None
                       for g in range(len(cat.table.rows)))
                 for f in range(len(cat.table.rows)))
    return Table(rows)


def bundles(cat):
    validate_category(cat)
    return tuple((cat.source[f], cat.target[f], f) for f in range(len(cat.table.rows)))


def bundled_product(cat, f, g):
    validate_category(cat)
    for arrow in (f, g):
        need(type(arrow) is tuple and len(arrow) == 3, "bundled arrow shape")
        for value in arrow:
            need(type(value) is int, "bundled arrow integer")
        index(arrow[2], len(cat.table.rows))
        need(arrow == (cat.source[arrow[2]], cat.target[arrow[2]], arrow[2]),
             "bundled arrow endpoints")
    if f[1] != g[0]:
        return None
    value = cat.table.rows[f[2]][g[2]]
    return (f[0], g[1], value)
