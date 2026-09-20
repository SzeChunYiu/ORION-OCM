"""Actual finite functions and independent typed optional-structure checks."""
from itertools import product

BIT_FUNCTIONS = ((0, 1), (0, 0), (1, 1))


def compose_functions(first, second):
    if type(first) not in (tuple, list) or type(second) not in (tuple, list):
        raise ValueError("function tables must be finite sequences")
    if any(type(value) is not int or value < 0 or value >= len(second) for value in first):
        raise ValueError("first map does not land in second domain")
    if any(type(value) is not int or value < 0 for value in second):
        raise ValueError("invalid output value")
    return tuple(second[value] for value in first)


def reset_composite(first, second):
    result = compose_functions(first, second)
    if result not in BIT_FUNCTIONS:
        raise ValueError("outside reset category")
    return result


def table(value):
    if type(value) not in (tuple, list) or not value:
        raise ValueError("nonempty carrier required")
    size = len(value)
    if any(type(row) not in (tuple, list) or len(row) != size for row in value):
        raise ValueError("square table required")
    if any(type(entry) is not int or not 0 <= entry < size for row in value for entry in row):
        raise ValueError("invalid carrier label")
    return tuple(tuple(row) for row in value)


def actual_operation(candidate, first, second):
    # Translate labels to actual function values before comparing laws.
    return BIT_FUNCTIONS[candidate[BIT_FUNCTIONS.index(first)][BIT_FUNCTIONS.index(second)]]


def candidate_properties(candidate):
    candidate = table(candidate)
    if len(candidate) != 3:
        raise ValueError("three-function carrier required")
    associative = True
    for a, b, c in product(BIT_FUNCTIONS, repeat=3):
        left = actual_operation(candidate, actual_operation(candidate, a, b), c)
        right = actual_operation(candidate, a, actual_operation(candidate, b, c))
        associative &= left == right
    unit = all(actual_operation(candidate, BIT_FUNCTIONS[0], a) == a
               and actual_operation(candidate, a, BIT_FUNCTIONS[0]) == a for a in BIT_FUNCTIONS)
    return associative, unit


def interchange_equations(candidate):
    results = []
    for a, b, c, d in product(BIT_FUNCTIONS, repeat=4):
        left = actual_operation(candidate, reset_composite(a, b), reset_composite(c, d))
        right = reset_composite(actual_operation(candidate, a, c), actual_operation(candidate, b, d))
        results.append((tuple(BIT_FUNCTIONS.index(f) for f in (a, b, c, d)), left == right))
    return tuple(results)


def operations():
    for entries in product(range(3), repeat=9):
        yield tuple(tuple(entries[3*i:3*i+3]) for i in range(3))


def arrows(product_loops=False):
    return tuple((obj, loop) for obj in BIT_FUNCTIONS for loop in range(2 if product_loops else 1))


def sequential(first, second):
    if first[0] != second[0]:
        raise ValueError("different typed objects")
    return first[0], (first[1] + second[1]) % 2


def parallel(first, second):
    return reset_composite(first[0], second[0]), (first[1] + second[1]) % 2


def rename(candidate, permutation):
    candidate = table(candidate)
    if type(permutation) not in (tuple, list) or any(type(i) is not int for i in permutation):
        raise ValueError("invalid permutation")
    if sorted(permutation) != list(range(len(candidate))):
        raise ValueError("not a bijection")
    result = [[None] * len(candidate) for _ in candidate]
    for a, b in product(range(len(candidate)), repeat=2):
        result[permutation[a]][permutation[b]] = permutation[candidate[a][b]]
    return tuple(tuple(row) for row in result)


def normalized_operations():
    free = tuple((a, b) for a, b in product(range(3), repeat=2) if a and b)
    for values in product(range(3), repeat=len(free)):
        candidate = [[b if a == 0 else a if b == 0 else None for b in range(3)] for a in range(3)]
        for (a, b), value in zip(free, values):
            candidate[a][b] = value
        yield tuple(tuple(row) for row in candidate)


def verify_obstruction(records):
    if type(records) not in (tuple, list):
        raise ValueError("explicit candidate records required")
    seen = set()
    for record in records:
        if type(record) not in (tuple, list) or len(record) != 2:
            raise ValueError("candidate and failed equation required")
        candidate, failure = table(record[0]), record[1]
        if candidate in seen:
            raise ValueError("duplicate candidate")
        seen.add(candidate)
        if type(failure) not in (tuple, list) or len(failure) != 4 or any(
                type(v) is not int or not 0 <= v < 3 for v in failure):
            raise ValueError("actual interchange witness required")
        if len(candidate) != 3:
            raise ValueError("wrong carrier")
        a, b, c, d = (BIT_FUNCTIONS[i] for i in failure)
        left = actual_operation(candidate, reset_composite(a, b), reset_composite(c, d))
        right = reset_composite(actual_operation(candidate, a, c), actual_operation(candidate, b, d))
        if left == right:
            raise ValueError("interchange witness is not a failure")
    if seen != set(normalized_operations()):
        raise ValueError("not every common-unit operation was covered")
    return True
