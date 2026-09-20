"""Finite tagged partial multiplication; assumptions are checked separately."""
from dataclasses import dataclass


def need(condition, message):
    if not condition:
        raise ValueError(message)


def index(value, size):
    need(type(value) is int and 0 <= value < size, "invalid arrow index")
    return value


@dataclass(frozen=True)
class Table:
    rows: tuple

    def __post_init__(self):
        need(type(self.rows) is tuple, "table must be a tuple")
        size = len(self.rows)
        for row in self.rows:
            need(type(row) is tuple and len(row) == size, "nonsquare table")
            for value in row:
                if value is not None:
                    index(value, size)


def units(table):
    need(type(table) is Table, "expected Table")
    rows = table.rows
    return tuple(e for e in range(len(rows)) if rows[e][e] == e and all(
        (rows[e][x] is None or rows[e][x] == x)
        and (rows[x][e] is None or rows[x][e] == x)
        for x in range(len(rows))))


def laws(table):
    need(type(table) is Table, "expected Table")
    rows, size = table.rows, len(table.rows)
    unit_set = units(table)
    local = all(any(rows[e][x] == x for e in unit_set)
                and any(rows[x][e] == x for e in unit_set)
                for x in range(size))
    associative = coherent = True
    for x in range(size):
        for y in range(size):
            xy = rows[x][y]
            for z in range(size):
                yz = rows[y][z]
                lhs = None if xy is None else rows[xy][z]
                rhs = None if yz is None else rows[x][yz]
                associative = associative and lhs == rhs
                if xy is not None and yz is not None and lhs is None:
                    coherent = False
    return {"associativity": associative, "local_units": local, "coherence": coherent}


def validate(table):
    need(type(table) is Table, "expected Table")
    failed = [name for name, value in laws(table).items() if not value]
    need(not failed, "partial-algebra laws failed: " + ",".join(failed))


def word(table, arrows):
    need(type(table) is Table, "expected Table")
    need(type(arrows) is tuple and bool(arrows), "nonempty word tuple required")
    size = len(table.rows)
    for arrow in arrows:
        index(arrow, size)
    result = arrows[0]
    for arrow in arrows[1:]:
        if result is None:
            return None
        result = table.rows[result][arrow]
    return result


def empty(table, anchor):
    need(type(table) is Table, "expected Table")
    index(anchor, len(table.rows))
    return anchor if anchor in units(table) else None


def relabel(table, permutation):
    need(type(table) is Table, "expected Table")
    size = len(table.rows)
    need(type(permutation) is tuple and len(permutation) == size, "permutation shape")
    for value in permutation:
        index(value, size)
    need(len(set(permutation)) == size, "permutation must be bijective")
    result = [[None] * size for _ in range(size)]
    for x in range(size):
        for y in range(size):
            value = table.rows[x][y]
            result[permutation[x]][permutation[y]] = None if value is None else permutation[value]
    return Table(tuple(tuple(row) for row in result))
