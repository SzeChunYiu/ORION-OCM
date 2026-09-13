"""Exact common finite interface, adapted from WTT's validated model register."""
from dataclasses import dataclass
from fractions import Fraction as F

def exact(value):
    if type(value) not in (int,F):
        raise ValueError("integers/Fractions required")
    return F(value)

@dataclass(frozen=True)
class Model:
    rows: tuple
    charges: tuple

def model(rows,charges):
    result=Model(tuple(tuple(tuple(exact(p) for p in row) for row in acts)
                       for acts in rows),
                 tuple(tuple(exact(c) for c in acts) for acts in charges))
    validate(result)
    return result

def validate(item):
    n=len(item.rows)
    if not n or len(item.charges)!=n:
        raise ValueError("complete nonempty state register required")
    for acts,costs in zip(item.rows,item.charges):
        if not acts or len(acts)!=len(costs):
            raise ValueError("complete nonempty action register required")
        for row,cost in zip(acts,costs):
            if len(row)!=n+2 or any(exact(p)<0 for p in row) or sum(row)!=1:
                raise ValueError("invalid probability row with two terminals")
            if exact(cost)<0:
                raise ValueError("nonnegative charge required")
