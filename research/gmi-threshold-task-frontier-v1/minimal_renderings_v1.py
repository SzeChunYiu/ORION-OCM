"""Exhaustive minimal-budget renderings of a Boolean task in the typed register.

The register's operations come from DCR (`typed_program_v1`, `typed_machine_v1`).
This module never executes a candidate: it enumerates the value vectors
reachable by a straight-line expression that uses each of the n unpacked inputs
exactly once, under a declared intermediate-magnitude cap whose non-bindingness
is checked by widening it.

Budget accounting, per `UNPACK_SEQUENCE` reading of an n-tuple:

    n + 2   LOAD_FAST x, UNPACK_SEQUENCE, n * STORE_FAST
    n       one LOAD_FAST per input
    m       one event per binary operation or comparison
    u       one event per unary operation
    c       one LOAD_FAST per integer constant
    1       RETURN_VALUE

An expression over all n inputs needs `m >= n - 1`, and a constant is only ever
loaded together with an operation that consumes it, so `c >= 1` forces
`m >= n + c - 1`. The reachable budgets from `3n + 2` upward are therefore

    3n + 2   u = 0, c = 0
    3n + 3   u = 1, c = 0
    3n + 4   u = 2, c = 0, or u = 0, c = 1

and a unary operation on top of a one-constant shape costs `3n + 5`, so the
one-constant layer needs `u = 0` to stay at `3n + 4`.

Unary operations matter and were missed by this module's first version, which
enumerated binary operations only and therefore did not cover `3n + 3` at all.
On the validated layout `UNARY_NEGATIVE`, `UNARY_INVERT` and `UNARY_NOT` are
admitted at one opcode each; unary `+` is **refused**, because CPython 3.12
compiles it to `CALL_INTRINSIC_1`, which the typed machine does not account.
"""

import itertools
import operator

BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul,
          "^": operator.xor, "&": operator.and_, "|": operator.or_,
          "<<": operator.lshift, ">>": operator.rshift}
# Unary `+` is deliberately absent: the typed machine refuses CALL_INTRINSIC_1.
UNARY = {"-": operator.neg, "~": operator.invert, "not": operator.not_}
COMPARE = {"==": operator.eq, "!=": operator.ne, "<": operator.lt,
           "<=": operator.le, ">": operator.gt, ">=": operator.ge}
SHIFT_LIMIT = 12
UNARY_BUDGET = 2


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


def normalise(vector):
    """Value-equality key. `not` yields a bool and Python has True == 1."""
    return tuple(int(v) for v in vector)


def _binary(op, left, right, cap):
    if op in ("<<", ">>"):
        if any(y < 0 for y in right):
            return None
        if op == "<<" and any(y > SHIFT_LIMIT for y in right):
            return None
    out = tuple(BINARY[op](x, y) for x, y in zip(left, right))
    return out if all(-cap <= v <= cap for v in out) else None


def reachable(n, cap, unary_budget=0, constants=()):
    """{unary ops used: {value vector: one rendering}} at the full leaf set.

    Leaves are the n inputs, plus -- when `constants` is non-empty -- exactly one
    further leaf holding any one of those constants. Every leaf is used once.
    """
    require(type(cap) is int and cap > 0, "positive magnitude cap required")
    require(type(unary_budget) is int and 0 <= unary_budget <= UNARY_BUDGET,
            "unary budget outside the declared range")
    pts = points(n)
    table = {}

    def add(slot, vector, text):
        table.setdefault(slot, {}).setdefault(normalise(vector), text)

    for i in range(n):
        add((1 << i, 0), tuple(p[i] for p in pts), "v%d" % i)
    leaves = n
    if constants:
        leaves = n + 1
        for constant in sorted(set(constants)):
            add((1 << n, 0), tuple(constant for _ in pts), repr(constant))
    full = (1 << leaves) - 1
    for mask in range(1, full + 1):
        for used in range(unary_budget + 1):
            if bin(mask).count("1") >= 2:
                acc = {}
                sub = (mask - 1) & mask
                while sub:
                    other = mask ^ sub
                    if sub < other:
                        for split in range(used + 1):
                            left = table.get((sub, split))
                            right = table.get((other, used - split))
                            if not left or not right:
                                continue
                            for a, atext in left.items():
                                for b, btext in right.items():
                                    for op in BINARY:
                                        for x, xt, y, yt in ((a, atext, b, btext),
                                                             (b, btext, a, atext)):
                                            got = _binary(op, x, y, cap)
                                            if got is not None:
                                                acc.setdefault(normalise(got),
                                                               "(%s %s %s)" % (xt, op, yt))
                    sub = (sub - 1) & mask
                for vector, text in acc.items():
                    add((mask, used), vector, text)
            if used:
                previous = table.get((mask, used - 1))
                if previous:
                    for vector, text in list(previous.items()):
                        for name, function in UNARY.items():
                            got = tuple(function(v) for v in vector)
                            if all(-cap <= int(v) <= cap for v in got):
                                add((mask, used), got, "%s(%s)" % (name, text))
    return {used: table.get((full, used), {}) for used in range(unary_budget + 1)}


def comparison_constants(vector, target, op):
    """Every integer c with `vector op c` equal to target, exactly.

    Returned as a sorted tuple when finite, or ("interval", lo, hi) with None for
    an open end, which the caller intersects with its declared constant range.
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


def survey(n, target, cap, constants, include_arithmetic=True,
           unary_budget=UNARY_BUDGET):
    """Exhaustive minimal-budget survey of one task at one cap.

    `constant_free_by_unary_count` covers the `3n + 2`, `3n + 3` and `3n + 4`
    budgets that use no constant, indexed by how many unary operations they
    spend. `comparison` and `arithmetic` are the two one-constant `3n + 4`
    shapes, which must spend no unary operation to stay at that budget.

    The enumeration covers expression trees over the n unpacked inputs. Shapes
    that read a registered data binding instead -- the constant tables -- are
    covered by direct measurement in `frontier_registers_v1`, not here.
    """
    require(len(target) == 2 ** n, "target must cover the whole domain")
    require(all(t in (0, 1) for t in target), "target must be Boolean")
    allowed = sorted(set(constants))
    require(allowed and all(type(c) is int for c in allowed), "integer constants required")
    normalised_target = normalise(target)
    plain = reachable(n, cap, unary_budget=unary_budget)
    constant_free = {}
    for used, rows in sorted(plain.items()):
        constant_free["3n+%d" % (2 + used)] = sorted(
            text for vector, text in rows.items() if vector == normalised_target)
    comparison = []
    for vector, text in plain[0].items():
        for op in sorted(COMPARE):
            found = comparison_constants(vector, normalised_target, op)
            if found and found[0] == "interval":
                lo, hi = found[1], found[2]
                found = tuple(c for c in allowed
                              if (lo is None or c >= lo) and (hi is None or c <= hi))
            for c in found:
                if c in allowed:
                    comparison.append({"rendering": "%s %s %d" % (text, op, c),
                                       "affine_operand": affine_form(vector, n) is not None})
    if include_arithmetic:
        with_constant = reachable(n, cap, unary_budget=0, constants=allowed)
        arithmetic = sorted(text for vector, text in with_constant[0].items()
                            if vector == normalised_target)
    else:
        arithmetic = None
    comparison.sort(key=lambda row: (not row["affine_operand"], row["rendering"]))
    return {"constant_free_by_unary_count": constant_free,
            "comparison_3n_plus_4": comparison,
            "arithmetic_3n_plus_4": arithmetic,
            "arithmetic_shape_enumerated": include_arithmetic,
            "distinct_value_vectors_by_unary_count":
                {str(used): len(rows) for used, rows in sorted(plain.items())},
            "magnitude_cap": cap,
            "unary_budget": unary_budget,
            "constants": allowed}
