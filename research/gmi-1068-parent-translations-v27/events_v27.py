"""Exact finite classical events with subnormalized rows."""
from dataclasses import dataclass
from fractions import Fraction
from core_v27 import Kernel, nat, need, stochastic, tup


@dataclass(frozen=True)
class Event:
    n: int
    m: int
    rows: tuple

    def __post_init__(self):
        nat(self.n)
        nat(self.m)
        rows = tup(self.rows)
        need(len(rows) == self.n, "event source dimension mismatch")
        for row in rows:
            tup(row)
            need(len(row) == self.m, "event target dimension mismatch")
            need(all(type(x) is Fraction for x in row), "exact Fraction entries required")
            need(all(x >= 0 for x in row), "negative event entry")
            need(sum(row, Fraction(0)) <= 1, "event row exceeds one")


def checked(event):
    need(type(event) is Event, "actual Event required")
    return event


def identity_event(n):
    nat(n)
    return Event(n, n, tuple(tuple(Fraction(int(i == j)) for j in range(n))
                             for i in range(n)))


def compose_event(first, second):
    checked(first)
    checked(second)
    need(first.m == second.n, "event composition dimension mismatch")
    return Event(first.n, second.m, tuple(tuple(
        sum((first.rows[i][j] * second.rows[j][k] for j in range(first.m)), Fraction(0))
        for k in range(second.m)) for i in range(first.n)))


def normalized(event):
    checked(event)
    return all(sum(row, Fraction(0)) == 1 for row in event.rows)


def to_kernel(event):
    checked(event)
    need(normalized(event), "event is not a normalized channel")
    return stochastic.Kernel(event.n, event.m, event.rows)


def from_kernel(kernel):
    need(type(kernel) is Kernel, "actual cached V14 Kernel required")
    return Event(kernel.n, kernel.m, kernel.rows)
