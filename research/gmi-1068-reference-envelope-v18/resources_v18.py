"""Free-conversion preorders and their complete Boolean target signatures."""
from core_v18 import acceptance, flags


def relation(value):
    if type(value) is not tuple:
        raise ValueError("canonical relation required")
    size = len(value)
    if any(type(row) is not tuple or len(row) != size
           or any(type(bit) is not bool for bit in row) for row in value):
        raise ValueError("square strict Boolean relation required")
    if any(not value[i][i] for i in range(size)):
        raise ValueError("free conversion must be reflexive")
    if any(value[i][j] and value[j][k] and not value[i][k]
           for i in range(size) for j in range(size) for k in range(size)):
        raise ValueError("free conversion must be transitive")
    return value


def state(value, size):
    if type(value) is not int or not 0 <= value < size:
        raise ValueError("resource outside its declared space")


def converts(conversion, first, second):
    relation(conversion)
    state(first, len(conversion))
    state(second, len(conversion))
    return conversion[first][second]


def signatures(conversion):
    relation(conversion)
    return tuple(tuple(conversion[x][target] for target in range(len(conversion)))
                 for x in range(len(conversion)))


def resource_context(admitted, states, conversion, target):
    flags(admitted)
    relation(conversion)
    state(target, len(conversion))
    if type(states) is not tuple or len(states) != len(admitted):
        raise ValueError("one resource or undefined marker per history required")
    for value in states:
        if value is not None:
            state(value, len(conversion))
    return acceptance(admitted, tuple(None if value is None else conversion[value][target]
                                      for value in states))
