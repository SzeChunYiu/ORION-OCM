"""Exact finite witness tables, not a general causal-identification solver."""

from fractions import Fraction as F
from itertools import product


def bernoulli(p):
    if not isinstance(p, F) or not 0 <= p <= 1:
        raise ValueError("an exact probability is required")
    return ((0, 1 - p), (1, p))


def validate_joint(joint):
    if not joint or any(
        len(k) != 3 or any(type(v) is not int or v not in (0, 1) for v in k)
        or not isinstance(p, F) or p < 0 for k, p in joint.items()
    ) or sum(joint.values()) != 1:
        raise ValueError("normalized exact binary joint required")


def _add(table, key, mass):
    if mass:
        table[key] = table.get(key, F(0)) + mass


def observed(world, flip=F(0)):
    """Z=U is the observed fair root; X=Z xor B with independent B."""
    if type(world) is not int or world not in (0, 1):
        raise ValueError("unknown witness")
    table = {}
    for (u, pu), (b, pb) in product(bernoulli(F(1, 2)), bernoulli(flip)):
        x = u ^ b
        y = u if world == 0 else x
        _add(table, (x, y, u), pu * pb)
    return table


def intervene(world, x):
    """Replace only X's equation; retain U and Y's equation."""
    if type(world) is not int or world not in (0, 1) or type(x) is not int or x not in (0, 1):
        raise ValueError("unknown witness or assignment")
    return sum(p for u, p in bernoulli(F(1, 2))
               if (u if world == 0 else x) == 1)


def marginal_xy(joint):
    validate_joint(joint)
    out = {}
    for (x, y, _z), p in joint.items():
        _add(out, (x, y), p)
    return out


def adjustment(joint, x):
    """Compute from the observed table only; never impute an empty stratum."""
    validate_joint(joint)
    if type(x) is not int or x not in (0, 1):
        raise ValueError("binary assignment required")
    total = F(0)
    for z in (0, 1):
        pz = sum(p for (_xx, _y, zz), p in joint.items() if zz == z)
        if not pz:
            continue
        denom = sum(p for (xx, _y, zz), p in joint.items() if xx == x and zz == z)
        if not denom:
            raise ValueError("unsupported positive-mass adjustment stratum")
        num = joint.get((x, 1, z), F(0))
        total += pz * num / denom
    return total


def conditional_y1(joint, x):
    validate_joint(joint)
    if type(x) is not int or x not in (0, 1):
        raise ValueError("binary assignment required")
    denominator = sum(p for (xx, _y, _z), p in joint.items() if xx == x)
    if not denominator:
        raise ValueError("assignment has zero probability")
    return sum(p for (xx, y, _z), p in joint.items() if xx == x and y == 1) / denominator


def randomized(world, probability=F(1, 2)):
    """Independent replacement X~Bern(probability), no other equation changes."""
    if type(world) is not int or world not in (0, 1):
        raise ValueError("unknown witness")
    table = {}
    for (u, pu), (x, px) in product(bernoulli(F(1, 2)), bernoulli(probability)):
        y = u if world == 0 else x
        _add(table, (x, y, u), pu * px)
    return table


def descendant_joint():
    """X fair, Y=X xor E, Z=Y xor N; E,N independent Bern(1/4)."""
    table = {}
    for (x, px), (e, pe), (n, pn) in product(
        bernoulli(F(1, 2)), bernoulli(F(1, 4)), bernoulli(F(1, 4))
    ):
        y = x ^ e
        _add(table, (x, y, y ^ n), px * pe * pn)
    return table


def descendant_do(x):
    if type(x) is not int or x not in (0, 1):
        raise ValueError("binary assignment required")
    return sum(pe * pn for (e, pe), (_n, pn) in product(
        bernoulli(F(1, 4)), bernoulli(F(1, 4))
    ) if x ^ e == 1)
