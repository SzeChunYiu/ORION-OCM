"""Actual finite composition laws and their folded parity evaluations."""
from dataclasses import dataclass


def label(value, size):
    if type(value) is not int or not 0 <= value < size:
        raise ValueError("strict in-range label required")
    return value


@dataclass(frozen=True)
class Monoid:
    table: tuple
    identity: int

    def __post_init__(self):
        if type(self.table) is not tuple or not self.table:
            raise ValueError("nonempty canonical composition table required")
        size = len(self.table)
        label(self.identity, size)
        for row in self.table:
            if type(row) is not tuple or len(row) != size:
                raise ValueError("square tuple table required")
            for value in row:
                label(value, size)
        for a in range(size):
            if self.table[self.identity][a] != a or self.table[a][self.identity] != a:
                raise ValueError("identity law failed")
            for b in range(size):
                for c in range(size):
                    if self.table[self.table[a][b]][c] != self.table[a][self.table[b][c]]:
                        raise ValueError("associativity failed")


def c4():
    return Monoid(tuple(tuple((a + b) % 4 for b in range(4)) for a in range(4)), 0)


def v4():
    return Monoid(tuple(tuple(a ^ b for b in range(4)) for a in range(4)), 0)


def fold(monoid, word):
    if type(monoid) is not Monoid or type(word) is not tuple:
        raise ValueError("Monoid and canonical word required")
    current = monoid.identity
    for value in word:
        current = monoid.table[current][label(value, len(monoid.table))]
    return current


def context(monoid, word):
    return fold(monoid, word) % 2
