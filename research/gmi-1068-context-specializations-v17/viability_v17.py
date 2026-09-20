"""Greatest safe existential kernel for an explicitly supplied step relation."""
from core_v17 import flags
from specializations_v17 import acceptance


def validate(relation, safe):
    if type(relation) is not tuple:
        raise ValueError("canonical relation tuple required")
    size = len(relation)
    if any(type(row) is not tuple or len(row) != size
           or any(type(v) is not bool for v in row) for row in relation):
        raise ValueError("square strict Boolean relation required")
    if type(safe) is not frozenset or any(type(v) is not int or not 0 <= v < size
                                        for v in safe):
        raise ValueError("safe states must be a canonical subset")
    return size


def survivor_trace(relation, safe):
    validate(relation, safe)
    trace = [safe]
    while True:
        current = trace[-1]
        following = frozenset(x for x in current if any(relation[x][y] for y in current))
        if following == current:
            return tuple(trace)
        trace.append(following)


def viability(relation, safe):
    return survivor_trace(relation, safe)[-1]


def viability_context(admitted, endpoints, relation, safe):
    flags(admitted)
    size = validate(relation, safe)
    if type(endpoints) is not tuple or len(endpoints) != len(admitted):
        raise ValueError("one endpoint or undefined marker per history required")
    if any(v is not None and (type(v) is not int or not 0 <= v < size) for v in endpoints):
        raise ValueError("endpoint outside state space")
    kernel = viability(relation, safe)
    return acceptance(admitted, tuple(None if v is None else v in kernel for v in endpoints))
