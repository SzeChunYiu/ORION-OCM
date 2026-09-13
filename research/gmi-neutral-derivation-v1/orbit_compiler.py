"""Generic exact affine constraint compiler; no architecture templates."""

from fractions import Fraction as F


def validate(nin, nout, generators, allowed):
    if type(nin) is not int or type(nout) is not int or min(nin, nout) < 1:
        raise ValueError("positive finite dimensions required")
    for pin, pout in generators:
        if sorted(pin) != list(range(nin)) or sorted(pout) != list(range(nout)):
            raise ValueError("generator must pair input/output permutations")
    if any(not (0 <= r < nout and 0 <= c <= nin) for r, c in allowed):
        raise ValueError("support outside coefficient domain")


def equations(nin, nout, generators, allowed):
    validate(nin, nout, generators, allowed)
    width = nin + 1
    dim = width * nout
    rows = []
    for pin, pout in generators:
        aug = tuple(pin) + (nin,)
        for r in range(nout):
            for c in range(width):
                row = [F(0)] * dim
                row[r * width + c] += 1
                row[pout[r] * width + aug[c]] -= 1
                rows.append(row)
    for r in range(nout):
        for c in range(width):
            if (r, c) not in allowed:
                row = [F(0)] * dim
                row[r * width + c] = 1
                rows.append(row)
    return rows, dim


def nullspace(rows, dim):
    """General rational RREF; arithmetic count includes operations on zeros."""
    a = [[F(x) for x in row] for row in rows]
    if any(len(row) != dim for row in a):
        raise ValueError("ragged equations")
    pivots = []
    work = 0
    for col in range(dim):
        pivot = next((r for r in range(len(pivots), len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        dest = len(pivots)
        a[dest], a[pivot] = a[pivot], a[dest]
        scale = a[dest][col]
        a[dest] = [x / scale for x in a[dest]]
        work += dim
        for r in range(len(a)):
            if r != dest and a[r][col]:
                scale = a[r][col]
                a[r] = [x - scale * y for x, y in zip(a[r], a[dest])]
                work += 2 * dim
        pivots.append(col)
    free = [c for c in range(dim) if c not in pivots]
    basis = []
    for col in free:
        v = [F(0)] * dim
        v[col] = 1
        for r, p in enumerate(pivots):
            v[p] = -a[r][col]
        basis.append(tuple(v))
    return tuple(basis), {"rank": len(pivots), "rational_arithmetic": work}


def compile_affine(nin, nout, generators, allowed):
    rows, dim = equations(nin, nout, generators, allowed)
    basis, counters = nullspace(rows, dim)
    instructions = []
    for k, vector in enumerate(basis):
        for pos, value in enumerate(vector):
            if value:
                if value != 1:
                    raise ValueError("equality constraints must yield indicator basis")
                instructions.append((pos // (nin + 1), pos % (nin + 1), k))
    return {
        "nin": nin, "nout": nout, "basis": basis,
        "instructions": tuple(instructions), "dimension": len(basis),
        "counters": {**counters, "equations": len(rows),
                     "constraint_entries": len(rows) * dim,
                     "coefficient_entries": dim,
                     "active_entries": len(instructions)},
    }


def execute(compiled, parameters, x):
    if len(x) != compiled["nin"] or len(parameters) != compiled["dimension"]:
        raise ValueError("dimension mismatch")
    values = tuple(F(v) for v in x) + (F(1),)
    y = [F(0)] * compiled["nout"]
    for out, inp, par in compiled["instructions"]:
        y[out] += F(parameters[par]) * values[inp]
    size = len(compiled["instructions"])
    return tuple(y), {"multiplications": size, "additions": size,
                      "parameter_reads": size, "input_reads": size,
                      "output_initializations": len(y)}
