"""Independent decoder assignments and typed-history operational semantics.

No imports from the production checker. Objective tables have one common
ambient four-arrow domain regardless of path admission.
"""
from itertools import product

ARROWS = ((0, 0, "identity"), (1, 1, "identity"),
          (0, 1, "first"), (0, 1, "second"))


def candidates(reduct, alphabet, domain=None):
    domain = tuple(sorted(set(reduct))) if domain is None else tuple(domain)
    return tuple(dict(zip(domain, values)) for values in product(alphabet, repeat=len(domain)))


def decoders(reduct, target, alphabet, domain=None):
    return tuple(candidate for candidate in candidates(reduct, alphabet, domain)
                 if all(p in candidate and candidate[p] == o for p, o in zip(reduct, target)))


def admitted_arrows(mask):
    return frozenset((0, 1)) | frozenset(a for a in (2, 3) if mask // (2 ** (a - 2)) % 2)


def composition(first, second):
    source, middle, first_kind = ARROWS[first]
    other_middle, target, second_kind = ARROWS[second]
    if middle != other_middle:
        raise ValueError("ill-typed composition")
    if first_kind == "identity":
        return second
    if second_kind == "identity":
        return first
    raise ValueError("ambient category has no composable two nonidentities")


def history(mask, objective, start, path):
    current_object, normal_form, admitted = start, start, admitted_arrows(mask)
    legal = True
    for arrow in path:
        source, target, kind = ARROWS[arrow]
        if source != current_object:
            raise ValueError("ill-typed history")
        current_object = target
        if kind != "identity":
            normal_form = arrow
        legal = legal and arrow in admitted
    return objective[normal_form] if legal else None


def paths(maximum_length):
    return tuple(word for length in range(maximum_length + 1)
                 for word in product(range(4), repeat=length))


def attainable_by_paths(mask, objective, start, maximum_length=4):
    values = set()
    for path in paths(maximum_length):
        try:
            value = history(mask, objective, start, path)
        except ValueError:
            continue
        if value is not None:
            values.add(value)
    return tuple(sorted(values))


def units(table):
    identity_function = tuple(range(len(table)))
    return tuple(candidate for candidate in range(len(table))
                 if tuple(table[candidate]) == identity_function
                 and tuple(row[candidate] for row in table) == identity_function)


def left_fold(table, values):
    value = values[0]
    for right in values[1:]:
        value = table[value][right]
    return value


def right_fold(table, values):
    if len(values) == 1:
        return values[0]
    return table[values[0]][right_fold(table, values[1:])]
