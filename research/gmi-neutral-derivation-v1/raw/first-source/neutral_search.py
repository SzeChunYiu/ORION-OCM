"""Complete size-indexed enumeration modulo a trace congruence, no target macros."""
from dataclasses import dataclass
from neutral_machine import inputs, objective


@dataclass
class Fiber:
    program: tuple
    multiplicity: int


def binary_signature(table, left, right):
    return tuple(((table >> (2 * a[0] + b[0])) & 1,
                  a[1] + b[1], a[2] + b[2] + 1,
                  a[3] + b[3], a[4] | b[4]) for a, b in zip(left, right))


def branch_signature(condition, yes, no):
    result = []
    for c, y, n in zip(condition, yes, no):
        arm = y if c[0] else n
        result.append((arm[0], c[1] + arm[1], c[2] + arm[2],
                       c[3] + arm[3] + 1, c[4] | arm[4]))
    return tuple(result)


def grammar_counts(arity, bound):
    counts = [0] * (bound + 1)
    counts[1] = arity + 2
    for size in range(2, bound + 1):
        counts[size] = 16 * sum(counts[a] * counts[size - 1 - a]
                                for a in range(1, size - 1))
        counts[size] += sum(
            counts[a] * counts[b] * counts[size - 1 - a - b]
            for a in range(1, size - 2) for b in range(1, size - 1 - a)
        )
    return counts


def enumerate_space(arity, bound):
    if bound < 1:
        raise ValueError("Positive finite description bound required")
    domain = inputs(arity)
    levels = [{} for _ in range(bound + 1)]
    counters = {"compositions": 0, "signature_cells": 0}

    def insert(size, sig, count, program):
        counters["compositions"] += 1
        counters["signature_cells"] += len(domain)
        if sig in levels[size]:
            levels[size][sig].multiplicity += count
        else:
            levels[size][sig] = Fiber(program, count)

    for value in (0, 1):
        sig = tuple((value, 0, 0, 0, 0) for _ in domain)
        insert(1, sig, 1, ("c", value))
    for index in range(arity):
        sig = tuple((x[index], 1, 0, 0, 1 << index) for x in domain)
        insert(1, sig, 1, ("r", index))
    for size in range(2, bound + 1):
        for a in range(1, size - 1):
            b = size - 1 - a
            for left, lf in levels[a].items():
                for right, rf in levels[b].items():
                    for table in range(16):
                        insert(size, binary_signature(table, left, right),
                               lf.multiplicity * rf.multiplicity,
                               ("b", table, lf.program, rf.program))
        for a in range(1, size - 2):
            for b in range(1, size - 1 - a):
                c = size - 1 - a - b
                for condition, cf in levels[a].items():
                    for yes, yf in levels[b].items():
                        for no, nf in levels[c].items():
                            insert(size, branch_signature(condition, yes, no),
                                   cf.multiplicity * yf.multiplicity * nf.multiplicity,
                                   ("i", cf.program, yf.program, nf.program))
    expected = grammar_counts(arity, bound)
    actual = [sum(f.multiplicity for f in level.values()) for level in levels]
    if actual != expected:
        raise ValueError("Enumeration multiplicities violate complete grammar recurrence")
    counters.update(raw_terms_by_size=actual,
                    trace_fibers_by_size=[len(level) for level in levels])
    return levels, counters


def minimize(levels, truth, probabilities, prices):
    truth = tuple(map(int, truth))
    best = None
    winners = []
    for size, level in enumerate(levels):
        for sig, fiber in level.items():
            if tuple(row[0] for row in sig) != truth:
                continue
            cost = objective(sig, size, probabilities, prices)
            if best is None or cost < best:
                best, winners = cost, [(size, sig, fiber)]
            elif cost == best:
                winners.append((size, sig, fiber))
    if best is None:
        raise ValueError("INCONCLUSIVE_GRAMMAR: no exact realization within bound")
    return best, winners


def verify_optimum(levels, truth, probabilities, prices, claimed_cost, winners):
    actual_cost, actual = minimize(levels, truth, probabilities, prices)
    actual_keys = {(size, sig) for size, sig, _ in actual}
    claimed_keys = {(size, sig) for size, sig, _ in winners}
    if actual_cost != claimed_cost or actual_keys != claimed_keys:
        raise ValueError("Missing, extra, or incorrectly priced optimal trace fiber")
