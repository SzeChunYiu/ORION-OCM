"""Exhaustive minimal-budget renderings of a Boolean task in the typed register.

The register's binary operations and its one-comparison-per-expression rule come
from DCR (`typed_program_v1`, `typed_machine_v1`). This module never executes a
candidate: it enumerates the value vectors reachable by a straight-line
expression that uses each of the n unpacked inputs exactly once, under a declared
intermediate-magnitude cap whose non-bindingness is checked by widening it.

Budget accounting, per `UNPACK_SEQUENCE` reading of an n-tuple:

    n + 2   LOAD_FAST x, UNPACK_SEQUENCE, n * STORE_FAST
    n       one LOAD_FAST per input
    m       one event per binary operation
    c       one LOAD_FAST per constant
    1       RETURN_VALUE

so an expression with n - 1 operations and no constant costs 3n + 2, and one
with a single constant costs 3n + 4 whether the constant is consumed by a
comparison or by an arithmetic operation. No budget of 3n + 3 exists.
"""

import itertools
import operator

BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul,
          "^": operator.xor, "&": operator.and_, "|": operator.or_,
          "<<": operator.lshift, ">>": operator.rshift}
COMPARE = {"==": operator.eq, "!=": operator.ne, "<": operator.lt,
           "<=": operator.le, ">": operator.gt, ">=": operator.ge}
SHIFT_LIMIT = 12


class EnumerationError(ValueError):
    """The enumeration was asked for something outside its declared scope."""


def require(condition, message):
    if not condition:
        raise EnumerationError(message)


def points(n):
    require(type(n) is int and 1 <= n <= 6, "declared scope is 1 <= n <= 6")
    return tuple(itertools.product((0, 1), repeat=n))


def majority(n):
    """1 exactly when at least half the inputs are 1."""
    return tuple(int(2 * sum(p) >= n) for p in points(n))


def parity(n):
    return tuple(sum(p) & 1 for p in points(n))


def _apply(op, left, right, cap):
    if op in ("<<", ">>"):
        if any(y < 0 for y in right):
            return None
        if op == "<<" and any(y > SHIFT_LIMIT for y in right):
            return None
    out = tuple(BINARY[op](x, y) for x, y in zip(left, right))
    return out if all(-cap <= v <= cap for v in out) else None


def reachable(n, cap, constants=()):
    """{value vector: one canonical rendering} using every leaf exactly once.

    Leaves are the n inputs, plus -- when `constants` is non-empty -- exactly one
    further leaf holding any one of those constants.
    """
    require(type(cap) is int and cap > 0, "positive magnitude cap required")
    pts = points(n)
    table = {1 << i: {tuple(p[i] for p in pts): "v%d" % i} for i in range(n)}
    if constants:
        table[1 << n] = {tuple(c for _ in pts): repr(c) for c in sorted(set(constants))}
    full = (1 << (n + (1 if constants else 0))) - 1
    for mask in range(1, full + 1):
        if mask in table or bin(mask).count("1") < 2:
            continue
        acc = {}
        sub = (mask - 1) & mask
        while sub:
            other = mask ^ sub
            if sub < other and sub in table and other in table:
                for left, ltext in table[sub].items():
                    for right, rtext in table[other].items():
                        for op in BINARY:
                            for a, at, b, bt in ((left, ltext, right, rtext),
                                                 (right, rtext, left, ltext)):
                                got = _apply(op, a, b, cap)
                                if got is not None:
                                    acc.setdefault(got, "(%s %s %s)" % (at, op, bt))
            sub = (sub - 1) & mask
        if acc:
            table[mask] = acc
    return table.get(full, {})


def comparison_constants(vector, target, op):
    """Every integer c with `vector op c` equal to target, as an exact set/range.

    Returned as a sorted tuple when finite, or ("interval", lo, hi) with None for
    an open end. Only finite answers are used by the callers below.
    """
    ones = [v for v, t in zip(vector, target) if t]
    zeros = [v for v, t in zip(vector, target) if not t]
    if op == ">=":
        lo = (max(zeros) + 1) if zeros else None
        hi = min(ones) if ones else None
    elif op == ">":
        lo = (max(zeros)) if zeros else None
        hi = (min(ones) - 1) if ones else None
    elif op == "<=":
        lo = max(ones) if ones else None
        hi = (min(zeros) - 1) if zeros else None
    elif op == "<":
        lo = (max(ones) + 1) if ones else None
        hi = min(zeros) if zeros else None
    elif op == "==":
        if len(set(ones)) != 1 or set(ones) & set(zeros):
            return ()
        return (ones[0],) if ones else ()
    elif op == "!=":
        if len(set(zeros)) != 1 or set(ones) & set(zeros):
            return ()
        return (zeros[0],) if zeros else ()
    else:
        raise EnumerationError("unmodeled comparison: " + str(op))
    if lo is None or hi is None:
        return ("interval", lo, hi)
    return tuple(range(lo, hi + 1))


def affine_form(vector, n):
    """(offset, weights) when the vector is affine in the inputs, else None."""
    table = dict(zip(points(n), vector))
    zero = tuple([0] * n)
    offset = table[zero]
    weights = []
    for i in range(n):
        unit = [0] * n
        unit[i] = 1
        weights.append(table[tuple(unit)] - offset)
    for point, value in table.items():
        if value != offset + sum(w * b for w, b in zip(weights, point)):
            return None
    return offset, tuple(weights)


def survey(n, target, cap, constants, include_arithmetic=True):
    """Exhaustive minimal-budget survey of one task at one cap.

    `constant_free` is the 3n+2 budget; `comparison` and `arithmetic` are the two
    3n+4 shapes. Every returned rendering is classified by whether the value it
    compares is an affine form of the inputs.
    """
    require(len(target) == 2 ** n, "target must cover the whole domain")
    require(all(t in (0, 1) for t in target), "target must be Boolean")
    allowed = sorted(set(constants))
    require(allowed and all(type(c) is int for c in allowed), "integer constants required")
    plain = reachable(n, cap)
    constant_free = sorted(text for vec, text in plain.items() if vec == target)
    comparison = []
    for vector, text in plain.items():
        for op in sorted(COMPARE):
            found = comparison_constants(vector, target, op)
            if found and found[0] == "interval":
                lo, hi = found[1], found[2]
                found = tuple(c for c in allowed
                              if (lo is None or c >= lo) and (hi is None or c <= hi))
            for c in found:
                if c in allowed:
                    comparison.append({"rendering": "%s %s %d" % (text, op, c),
                                       "affine_operand": affine_form(vector, n) is not None})
    if include_arithmetic:
        withconst = reachable(n, cap, constants=allowed)
        arithmetic = sorted(text for vec, text in withconst.items() if vec == target)
    else:
        arithmetic = None
    comparison.sort(key=lambda row: (not row["affine_operand"], row["rendering"]))
    return {"constant_free_3n_plus_2": constant_free,
            "comparison_3n_plus_4": comparison,
            "arithmetic_3n_plus_4": arithmetic,
            "arithmetic_shape_enumerated": include_arithmetic,
            "distinct_value_vectors": len(plain),
            "magnitude_cap": cap,
            "constants": allowed}
