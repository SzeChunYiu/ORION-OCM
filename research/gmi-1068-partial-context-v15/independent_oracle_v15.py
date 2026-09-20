"""Independent finite relational semantics; no production imports."""
from itertools import product


def is_preorder(order):
    n = len(order)
    return all(order[i][i] for i in range(n)) and all(
        not (order[i][j] and order[j][k]) or order[i][k]
        for i, j, k in product(range(n), repeat=3))


def preorders(n):
    for bits in product((False, True), repeat=n*n):
        order = tuple(tuple(bits[i*n+j] for j in range(n)) for i in range(n))
        if is_preorder(order):
            yield order


def corpus():
    for order in preorders(3):
        for statuses in product(range(5), repeat=3):
            admitted = tuple(s != 0 for s in statuses)
            defined = tuple(s >= 2 for s in statuses)
            values = tuple(s-2 if s >= 2 else None for s in statuses)
            yield admitted, defined, values, order


def observation(model, h):
    admitted, defined, values, _ = model
    if not admitted[h]:
        return 'ILLEGAL', None
    if not defined[h]:
        return 'UNDEFINED', None
    return 'VALUE', values[h]


def domain(model):
    return tuple(i for i, (a,d) in enumerate(zip(model[0], model[1])) if a and d)


def relation(model):
    values, order = model[2:]
    return frozenset((a,b) for a,b in product(domain(model), repeat=2)
                     if order[values[a]][values[b]])


def quotient(model):
    """Connected components of mutual comparison, followed by all-member order."""
    rel, unseen, groups = relation(model), set(domain(model)), []
    while unseen:
        seed = min(unseen)
        group, pending = {seed}, [seed]
        while pending:
            a = pending.pop()
            adjacent = {b for b in unseen if (a,b) in rel and (b,a) in rel} - group
            group.update(adjacent)
            pending.extend(adjacent)
        groups.append(frozenset(group))
        unseen.difference_update(group)
    order = tuple(tuple(all((a,b) in rel for a in left for b in right)
                        for right in groups) for left in groups)
    return tuple(groups), order


def check_quotient(model, candidate):
    return candidate == quotient(model)


def context_tuple(context):
    return context.admitted, context.defined, context.values, context.order


def cyclic_process():
    """One object, three distinct arrows; full composition and identity data."""
    return {'objects': (0,), 'arrows': ((0,0),)*3, 'identities': (0,),
            'composition': tuple(tuple((a+b) % 3 for b in range(3)) for a in range(3)),
            'admitted': (True,)*3}


def opposite_values(model, a, lo, hi):
    """Registered preferLow(a)/preferHigh(a), retaining illegal ambient values."""
    active = set(domain(model))
    first = tuple((lo if h == a else hi) if h in active else value
                  for h,value in enumerate(model[2]))
    second = tuple((hi if h == a else lo) if h in active else value
                   for h,value in enumerate(model[2]))
    return first, second
