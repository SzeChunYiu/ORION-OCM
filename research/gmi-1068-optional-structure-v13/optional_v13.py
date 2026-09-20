"""Exact optional-structure countermodels and finite algebra checks."""
from itertools import product

# Labels: identity, reset-to-zero, reset-to-one; execute first then second.
RESET_COMPOSITION = ((0, 1, 2), (1, 1, 2), (2, 1, 2))


def validate_table(table):
    if not isinstance(table, (tuple, list)) or not table:
        raise ValueError("nonempty square table required")
    size = len(table)
    if any(not isinstance(row, (tuple, list)) or len(row) != size for row in table):
        raise ValueError("nonempty square table required")
    if any(type(value) is not int or not 0 <= value < size for row in table for value in row):
        raise ValueError("table values must be exact carrier indices")
    return tuple(tuple(row) for row in table)


def _index(value, size):
    if type(value) is not int or not 0 <= value < size:
        raise ValueError("invalid carrier index")
    return value


def unit_laws(table, e):
    table = validate_table(table)
    _index(e, len(table))
    return all(table[e][a] == a and table[a][e] == a for a in range(len(table)))


def associative(table):
    table = validate_table(table)
    return all(table[table[a][b]][c] == table[a][table[b][c]]
               for a, b, c in product(range(len(table)), repeat=3))


def inverses(table, e):
    table = validate_table(table)
    if not unit_laws(table, e) or not associative(table):
        raise ValueError("inverse claims require a lawful monoid")
    return tuple((a, b) for a, b in product(range(len(table)), repeat=2)
                 if table[a][b] == e and table[b][a] == e)


def interchange_failure(seq, tensor):
    seq, tensor = validate_table(seq), validate_table(tensor)
    if len(seq) != len(tensor):
        raise ValueError("carrier size mismatch")
    for a, b, c, d in product(range(len(seq)), repeat=4):
        if tensor[seq[a][b]][seq[c][d]] != seq[tensor[a][c]][tensor[b][d]]:
            return a, b, c, d
    return None


def _model(model):
    if type(model) is not str or model not in ("discrete", "product"):
        raise ValueError("unknown model")
    return 1 if model == "discrete" else 2


def _arrow(model, arrow):
    count = _model(model)
    if not isinstance(arrow, (tuple, list)) or len(arrow) != 2:
        raise ValueError("arrow must contain object and parity")
    obj, bit = arrow
    return _index(obj, 3), _index(bit, count)


def hom(model, source, target):
    count = _model(model)
    _index(source, 3)
    _index(target, 3)
    return tuple((source, bit) for bit in range(count)) if source == target else ()


def identity(model, obj):
    _model(model)
    return _index(obj, 3), 0


def compose(model, first, second):
    first, second = _arrow(model, first), _arrow(model, second)
    if first[0] != second[0]:
        raise ValueError("incompatible arrow endpoints")
    return first[0], first[1] ^ second[1]


def tensor(model, first, second):
    first, second = _arrow(model, first), _arrow(model, second)
    return RESET_COMPOSITION[first[0]][second[0]], first[1] ^ second[1]


def weak_tensor_necessary(seq, e, tensor, left, right):
    """Necessary bifunctor/unitor laws only; no associator sufficiency claim."""
    seq, tensor = validate_table(seq), validate_table(tensor)
    if len(seq) != len(tensor):
        raise ValueError("carrier size mismatch")
    _index(left, len(seq))
    _index(right, len(seq))
    invertible = {a for a, _ in inverses(seq, e)}
    if left not in invertible or right not in invertible or tensor[e][e] != e:
        return False
    for a in range(len(seq)):
        if seq[tensor[e][a]][left] != seq[left][a]:
            return False
        if seq[tensor[a][e]][right] != seq[right][a]:
            return False
    return interchange_failure(seq, tensor) is None
