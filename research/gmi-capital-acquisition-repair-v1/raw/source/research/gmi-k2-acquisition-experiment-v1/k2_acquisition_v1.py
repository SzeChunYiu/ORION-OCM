"""K2 acquisition experiment: does retained capital make acquiring NEW capital cheaper?

Exact, deterministic, no randomness in the search itself.  Cost is the number of
candidate programs enumerated before the first verified solution - an integer,
not a timing.
"""
from itertools import product

PRIMITIVES = {
    "inc":    lambda x: x + 1,
    "dec":    lambda x: x - 1,
    "double": lambda x: x * 2,
    "square": lambda x: x * x,
}
PROBES = (0, 1, 2, 3)


def run_program(ops, table, x):
    for op in ops:
        x = table[op](x)
    return x


def semantics(ops, table):
    return tuple(run_program(ops, table, x) for x in PROBES)


def enumerate_until(target_sem, table, max_len):
    """Enumerate programs in length order; return (cost, solution) or (cost, None).

    cost = number of candidates examined.  Deterministic given the op ordering.
    """
    names = sorted(table)
    cost = 0
    for L in range(1, max_len + 1):
        for ops in product(names, repeat=L):
            cost += 1
            if semantics(ops, table) == target_sem:
                return cost, ops
    return cost, None


def with_library(library):
    """Library entries become single callable instructions (macros)."""
    table = dict(PRIMITIVES)
    for name, ops in library.items():
        table[name] = (lambda o: (lambda x: run_program(o, PRIMITIVES, x)))(ops)
    return table


def acquisition_cost(target_sem, library, max_len):
    return enumerate_until(target_sem, with_library(library), max_len)


# --- experiment layer -------------------------------------------------------

def shortest_len(target_sem, table, cap):
    """Minimal program length reaching the target under this instruction table."""
    from itertools import product as _p
    for L in range(1, cap + 1):
        for ops in _p(sorted(table), repeat=L):
            if semantics(ops, table) == target_sem:
                return L
    return None


def reuse_available(target_sem, library, cap):
    """Semantic predicate: does the library SHORTEN the target's description?

    Syntactic substring matching is wrong here - two programs can be
    semantically equal and syntactically disjoint.
    """
    lr = shortest_len(target_sem, dict(PRIMITIVES), cap)
    lh = shortest_len(target_sem, with_library(library), cap)
    if lr is None or lh is None:
        return None
    return lh < lr


def k2_trial(target_sem, library, cap):
    """One K2 comparison: marginal acquisition cost with the library vs without."""
    reset_cost, _ = enumerate_until(target_sem, dict(PRIMITIVES), cap)
    h_cost, _ = enumerate_until(target_sem, with_library(library), cap)
    return {"reset": reset_cost, "h": h_cost,
            "k2": h_cost < reset_cost, "h_worse": h_cost > reset_cost}


def minimal_length_population(minlen, cap):
    """Targets whose SHORTEST primitive program is exactly `minlen` - held out
    from any census run at a smaller cap."""
    from itertools import product as _p
    seen = set()
    for L in range(1, minlen):
        for ops in _p(sorted(PRIMITIVES), repeat=L):
            seen.add(semantics(ops, PRIMITIVES))
    out = {}
    for ops in _p(sorted(PRIMITIVES), repeat=minlen):
        s = semantics(ops, PRIMITIVES)
        if s not in seen:
            out.setdefault(s, ops)
    return out
