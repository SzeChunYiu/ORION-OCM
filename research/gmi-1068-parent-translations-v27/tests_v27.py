"""Labelled independent tests preserve paired and zero-valued outcomes."""
from dataclasses import dataclass
from fractions import Fraction
from core_v27 import nat, need, stochastic, tup
from events_v27 import Event, compose_event


def outcome_id(value):
    if type(value) is int:
        nat(value)
        return value
    need(type(value) is tuple and len(value) == 2, "outcome ID must be Nat or binary pair")
    outcome_id(value[0])
    outcome_id(value[1])
    return value


@dataclass(frozen=True)
class Test:
    n: int
    m: int
    outcomes: tuple

    def __post_init__(self):
        nat(self.n)
        nat(self.m)
        tup(self.outcomes)
        ids = []
        for item in self.outcomes:
            need(type(item) is tuple and len(item) == 2, "labelled event pair required")
            label, event = item
            outcome_id(label)
            need(type(event) is Event, "checked Event required")
            need((event.n, event.m) == (self.n, self.m), "test component dimension mismatch")
            ids.append(label)
        need(len(set(ids)) == len(ids), "duplicate outcome ID")
        for i in range(self.n):
            need(sum((x for _, e in self.outcomes for x in e.rows[i]), Fraction(0)) == 1,
                 "test aggregate is not normalized")


def checked(test):
    need(type(test) is Test, "actual Test required")
    return test


def aggregate(test):
    checked(test)
    return stochastic.Kernel(test.n, test.m, tuple(tuple(
        sum((e.rows[i][j] for _, e in test.outcomes), Fraction(0))
        for j in range(test.m)) for i in range(test.n)))


def compose_test(first, second):
    checked(first)
    checked(second)
    need(first.m == second.n, "test composition dimension mismatch")
    return Test(first.n, second.m, tuple(
        ((a, b), compose_event(p, q)) for a, p in first.outcomes for b, q in second.outcomes))
