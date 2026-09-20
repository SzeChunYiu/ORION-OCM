"""Finite checks for conditional admissibility and declared scalar aggregation."""
from fractions import Fraction


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def admissible_subcategory(n, identities, compose, allowed):
    """Validate an ambient category, then test closure of a wide restriction.

    compose[(f, g)] is g after f. No missing composition is silently admitted.
    """
    if not _integer(n) or n < 1:
        raise ValueError("nonempty finite ambient arrow set required")
    if not isinstance(compose, dict):
        raise ValueError("composition must be a dictionary")
    if not isinstance(identities, (tuple, list)) or not identities:
        raise ValueError("identities must be a nonempty sequence")
    arrows = set(range(n))
    if any(not _integer(x) or x not in arrows for x in identities):
        raise ValueError("invalid identity")
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate identity")
    for pair, value in compose.items():
        if (not isinstance(pair, tuple) or len(pair) != 2
                or any(not _integer(x) or x not in arrows for x in pair)
                or not _integer(value) or value not in arrows):
            raise ValueError("invalid composition entry")
    try:
        entries = tuple(allowed)
    except TypeError as exc:
        raise ValueError("allowed must be iterable") from exc
    if any(not _integer(x) or x not in arrows for x in entries):
        raise ValueError("invalid allowed arrow")
    kept = set(entries)
    domains, codomains = {}, {}
    for f in arrows:
        starts = [i for i in identities if compose.get((i, f)) == f]
        ends = [i for i in identities if compose.get((f, i)) == f]
        if len(starts) != 1 or len(ends) != 1:
            raise ValueError("unique domain and codomain identities required")
        domains[f], codomains[f] = starts[0], ends[0]
    for i in identities:
        if domains[i] != i or codomains[i] != i:
            raise ValueError("identity at wrong object")
    for f in arrows:
        for g in arrows:
            legal = codomains[f] == domains[g]
            if legal != ((f, g) in compose):
                raise ValueError("composition table has illegal or missing pair")
            if legal:
                fg = compose[f, g]
                if domains[fg] != domains[f] or codomains[fg] != codomains[g]:
                    raise ValueError("composite has wrong endpoints")
    for f in arrows:
        for g in arrows:
            if (f, g) in compose:
                fg = compose[f, g]
                for h in arrows:
                    if (g, h) in compose:
                        if compose[fg, h] != compose[f, compose[g, h]]:
                            raise ValueError("nonassociative ambient composition")
    units = all(i in kept for i in identities)
    closed = all(value in kept for (f, g), value in compose.items()
                 if f in kept and g in kept)
    return {"identities": units, "composition": closed,
            "subcategory": units and closed}


def budget_paths(limit):
    """Arrows of the consumed-resource chain 0 <= i <= j <= limit."""
    if not _integer(limit) or limit < 0:
        raise ValueError("limit must be a nonnegative integer")
    return tuple((i, j) for i in range(limit + 1) for j in range(i, limit + 1))


def aggregates(profile, weights):
    """Three declared objectives; neither min nor max needs probability weights."""
    try:
        profile, weights = tuple(profile), tuple(weights)
    except TypeError as exc:
        raise ValueError("profile and weights must be sequences") from exc
    if not profile or len(profile) != len(weights):
        raise ValueError("nonempty aligned profile and weights required")
    for x in (*profile, *weights):
        if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
            raise ValueError("exact rational inputs required")
    values, mass = tuple(map(Fraction, profile)), tuple(map(Fraction, weights))
    if any(p < 0 for p in mass) or sum(mass) != 1:
        raise ValueError("expectation requires normalized nonnegative weights")
    return {"min": min(values), "max": max(values),
            "weighted": sum((v * p for v, p in zip(values, mass)), Fraction())}
