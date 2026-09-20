"""Exact typed finite stochastic kernels and total relations."""
from dataclasses import dataclass
from fractions import Fraction


def dimensions(n, m):
    if any(type(v) is not int or v < 0 for v in (n, m)):
        raise ValueError("dimensions must be nonnegative integers")


def sequence(value):
    if type(value) not in (list, tuple):
        raise ValueError("expected list or tuple")
    return tuple(value)


def targets(n, m, values):
    dimensions(n, m)
    result = sequence(values)
    if len(result) != n or any(type(v) is not int or not 0 <= v < m for v in result):
        raise ValueError("map targets do not match dimensions")
    return result


@dataclass(frozen=True)
class Kernel:
    n: int
    m: int
    rows: tuple

    def __post_init__(self):
        dimensions(self.n, self.m)
        rows = sequence(self.rows)
        if len(rows) != self.n:
            raise ValueError("source dimension mismatch")
        normalized = []
        for raw in rows:
            row = sequence(raw)
            if len(row) != self.m or any(type(v) not in (int, Fraction) for v in row):
                raise ValueError("target dimension or exact scalar type mismatch")
            converted = tuple(Fraction(v) for v in row)
            if any(v < 0 for v in converted) or sum(converted, Fraction(0)) != 1:
                raise ValueError("row must be nonnegative and normalized")
            normalized.append(converted)
        object.__setattr__(self, "rows", tuple(normalized))


@dataclass(frozen=True)
class Relation:
    n: int
    m: int
    rows: tuple

    def __post_init__(self):
        dimensions(self.n, self.m)
        rows = sequence(self.rows)
        if len(rows) != self.n:
            raise ValueError("source dimension mismatch")
        normalized = []
        for raw in rows:
            if type(raw) not in (list, tuple, set, frozenset):
                raise ValueError("expected finite target container")
            if not raw or any(type(v) is not int or not 0 <= v < self.m for v in raw):
                raise ValueError("relation row must be nonempty valid targets")
            normalized.append(frozenset(raw))
        object.__setattr__(self, "rows", tuple(normalized))


def compose_kernel(first, second):
    if type(first) is not Kernel or type(second) is not Kernel or first.m != second.n:
        raise ValueError("kernel composition is not typed")
    return Kernel(first.n, second.m, tuple(
        tuple(sum((first.rows[i][j] * second.rows[j][k] for j in range(first.m)),
                  Fraction(0)) for k in range(second.m))
        for i in range(first.n)))


def compose_relation(first, second):
    if type(first) is not Relation or type(second) is not Relation or first.m != second.n:
        raise ValueError("relation composition is not typed")
    return Relation(first.n, second.m, tuple(
        frozenset(k for j in row for k in second.rows[j]) for row in first.rows))


def dirac(n, m, values):
    values = targets(n, m, values)
    return Kernel(n, m, tuple(tuple(int(j == value) for j in range(m)) for value in values))


def graph(n, m, values):
    return Relation(n, m, tuple(frozenset((v,)) for v in targets(n, m, values)))


def identity_kernel(n):
    dimensions(n, n)
    return dirac(n, n, tuple(range(n)))


def identity_relation(n):
    dimensions(n, n)
    return graph(n, n, tuple(range(n)))


def support(kernel):
    if type(kernel) is not Kernel:
        raise ValueError("support requires a kernel")
    return Relation(kernel.n, kernel.m, tuple(
        frozenset(j for j, value in enumerate(row) if value > 0) for row in kernel.rows))


def uniformize(relation):
    if type(relation) is not Relation:
        raise ValueError("uniformization requires a relation")
    return Kernel(relation.n, relation.m, tuple(
        tuple(Fraction(1, len(row)) if j in row else Fraction(0)
              for j in range(relation.m)) for row in relation.rows))
