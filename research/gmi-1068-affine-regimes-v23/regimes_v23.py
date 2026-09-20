"""Exact all-pair affine refinement with every boundary and winning identity."""
from fractions import Fraction
from itertools import combinations
from core_v23 import family_checked, frontier, index, interval, parameters
from contexts_v23 import at


def score(family, candidate, t):
    family_checked(family)
    index(candidate, len(family.ids))
    return parameters(family, t)[candidate]


def winner_ids(family, t):
    encoded = at(family, t)
    context = encoded.context
    values = frontier.attained(context, tuple(range(context.n)))
    maxima = frontier.maximal(context.order, values)
    return tuple(sorted(encoded.decoder[code][0] for code in maxima))


def diagram(family, lo, hi):
    interval(family, lo, hi)
    active = tuple(i for i in range(len(family.ids))
                   if family.admitted[i] and family.defined[i])
    points = {lo, hi}
    for i, j in combinations(active, 2):
        slope = family.slopes[i] - family.slopes[j]
        if slope:
            root = (family.intercepts[j] - family.intercepts[i]) / slope
            if lo <= root <= hi:
                points.add(root)
    ordered = sorted(points)
    boundaries = tuple((t, winner_ids(family, t)) for t in ordered)
    cells = tuple((a, b, (a + b) / Fraction(2), winner_ids(family, (a + b) / Fraction(2)))
                  for a, b in zip(ordered, ordered[1:]))
    labels = [row[1] for row in boundaries] + [row[3] for row in cells]
    possible = tuple(sorted({identity for winners in labels for identity in winners}))
    universal = set(labels[0])
    for winners in labels[1:]:
        universal.intersection_update(winners)
    return {"boundaries": boundaries, "cells": cells, "possible": possible,
            "universal": tuple(sorted(universal)),
            "unique_everywhere": possible[0] if len(possible) == 1 else None}
