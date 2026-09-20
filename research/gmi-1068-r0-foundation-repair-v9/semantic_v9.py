"""Finite semantic recovery and one fixed ambient process presentation."""
from itertools import product

DOMAIN = (0, 1, 0, 0)
CODOMAIN = (0, 1, 1, 1)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def nat(x):
    return type(x) is int and x >= 0


def tables(reduct, target):
    need(type(reduct) is tuple and type(target) is tuple, "tuple tables required")
    need(len(reduct) == len(target), "different model domains")
    need(all(nat(x) for x in reduct + target), "nonnegative integer labels required")


def decoder(reduct, target):
    """Return the unique decoder on the attained reduct image, or None."""
    tables(reduct, target)
    result = {}
    for p, o in zip(reduct, target):
        if p in result and result[p] != o:
            return None
        result[p] = o
    return result


def verify_decoder(reduct, target, candidate):
    tables(reduct, target)
    need(type(candidate) is dict, "decoder must be a dictionary")
    need(all(nat(k) and nat(v) for k, v in candidate.items()), "invalid decoder labels")
    need(set(candidate) == set(reduct), "decoder must have precisely the attained domain")
    return all(candidate[p] == o for p, o in zip(reduct, target))


def collision(reduct, target):
    tables(reduct, target)
    for i in range(len(reduct)):
        for j in range(i):
            if reduct[i] == reduct[j] and target[i] != target[j]:
                return (j, i)
    return None


def arrow(a):
    need(nat(a) and a < 4, "invalid ambient arrow")


def compose(first, second):
    """Execute first, then second; return their ambient composite."""
    arrow(first)
    arrow(second)
    need(CODOMAIN[first] == DOMAIN[second], "noncomposable arrows")
    return second if first < 2 else first


def admitted(mask, a):
    need(nat(mask) and mask < 4, "invalid admissibility mask")
    arrow(a)
    return a < 2 or bool(mask & (1 << (a - 2)))


def path_composite(start, path):
    need(type(start) is int and start in (0, 1), "invalid source object")
    need(type(path) is tuple, "path must be tuple")
    current = start
    for a in path:
        arrow(a)
        need(DOMAIN[a] == CODOMAIN[current], "ill-typed ambient path")
        current = compose(current, a)
    return current


def evaluate_history(mask, objective, start, path):
    need(type(objective) is tuple and len(objective) == 4
         and all(nat(x) for x in objective), "invalid ambient evaluator")
    composite = path_composite(start, path)
    need(nat(mask) and mask < 4, "invalid admissibility mask")
    # Explicit path admission, not inferred by inspecting the evaluator's type.
    if not all(admitted(mask, a) for a in path):
        return None
    return objective[composite]


def attainable(mask, objective, start):
    """All ambient paths reduce to these four composites in this category."""
    need(type(start) is int and start in (0, 1), "invalid start")
    # Validate even if a later iterator would have no matching transitions.
    evaluate_history(mask, objective, start, ())
    return tuple(sorted({objective[a] for a in range(4)
                         if DOMAIN[a] == start and admitted(mask, a)}))


def presentation(reduct, target, model_order, process_names, objective_names):
    tables(reduct, target)
    need(type(model_order) is tuple and all(nat(i) for i in model_order)
         and sorted(model_order) == list(range(len(reduct))), "not a model bijection")
    for names, used in ((process_names, set(reduct)), (objective_names, set(target))):
        need(type(names) is dict and all(nat(k) and nat(v) for k, v in names.items()),
             "invalid presentation map")
        need(set(names) == used and len(set(names.values())) == len(used),
             "presentation map is not injective on exactly the attained image")
    return (tuple(process_names[reduct[i]] for i in model_order),
            tuple(objective_names[target[i]] for i in model_order))


def binary_units(table):
    need(type(table) is tuple and len(table) == 2
         and all(type(row) is tuple and len(row) == 2 for row in table),
         "invalid binary operation shape")
    need(all(type(x) is int and x in (0, 1) for row in table for x in row),
         "invalid binary operation value")
    return tuple(e for e in range(2)
                 if all(table[e][x] == x and table[x][e] == x for x in range(2)))


def associative(table):
    binary_units(table)
    return all(table[table[a][b]][c] == table[a][table[b][c]]
               for a, b, c in product(range(2), repeat=3))
