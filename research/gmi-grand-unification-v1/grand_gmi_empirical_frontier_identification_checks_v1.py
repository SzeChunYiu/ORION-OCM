"""Exact rational finite-register frontier identification; see EFI-1--4."""
from fractions import Fraction
from itertools import product
import json


def _rational(x):
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise ValueError("finite exact integer/Fraction required")
    return Fraction(x)


def _profiles(world):
    rows = tuple(tuple(_rational(x) for x in row) for row in world)
    if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError("nonempty rectangular candidate profile table required")
    return rows


def _boxes(boxes):
    rows = tuple(tuple(tuple(_rational(x) for x in pair) for pair in row)
                 for row in boxes)
    if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError("nonempty candidate/coordinate box table required")
    if any(len(p) != 2 or p[0] > p[1] for r in rows for p in r):
        raise ValueError("ordered closed interval required")
    return rows


def _dominates(x, y):
    return all(a <= b for a, b in zip(x, y)) and x != y


def frontier(world):
    rows = _profiles(world)
    return frozenset(i for i, x in enumerate(rows)
                     if not any(j != i and _dominates(y, x)
                                for j, y in enumerate(rows)))


def identify(worlds):
    rows = tuple(_profiles(w) for w in worlds)
    if not rows or any((len(w), len(w[0])) != (len(rows[0]), len(rows[0][0]))
                       for w in rows):
        raise ValueError("nonempty worlds with a fixed register required")
    patterns = frozenset(frontier(w) for w in rows)
    return frozenset.union(*patterns), frozenset.intersection(*patterns), patterns


def box_membership(boxes):
    rows = _boxes(boxes)
    lower = tuple(tuple(p[0] for p in r) for r in rows)
    upper = tuple(tuple(p[1] for p in r) for r in rows)
    possible = frozenset(i for i in range(len(rows))
                         if not any(j != i and _dominates(upper[j], lower[i])
                                    for j in range(len(rows))))
    necessary = frozenset(i for i in range(len(rows))
                          if not any(j != i and _dominates(lower[j], upper[i])
                                     for j in range(len(rows))))
    return possible, necessary


def ordered_partitions(n):
    """All weak orders on labels 0..n-1, without duplicate partitions."""
    if n == 0:
        yield ()
        return
    for blocks in ordered_partitions(n - 1):
        for j in range(len(blocks)):
            yield blocks[:j] + (blocks[j] + (n - 1,),) + blocks[j + 1:]
        for j in range(len(blocks) + 1):
            yield blocks[:j] + ((n - 1,),) + blocks[j:]


def _order_witness(intervals, blocks):
    lower = [max(intervals[i][0] for i in b) for b in blocks]
    upper = [min(intervals[i][1] for i in b) for b in blocks]
    r = len(blocks)
    if any(l > u for l, u in zip(lower, upper)):
        return None
    gaps = [(upper[q] - lower[p]) / (q - p)
            for p in range(r) for q in range(p + 1, r)]
    if gaps and min(gaps) <= 0:
        return None
    delta = min(gaps) / 2 if gaps else Fraction(0)
    levels = [max(lower[p] + (q - p) * delta for p in range(q + 1))
              for q in range(r)]
    values = [None] * len(intervals)
    for b, t in zip(blocks, levels):
        for i in b:
            values[i] = t
    return tuple(values)


def rectangle_frontiers(boxes):
    rows = _boxes(boxes)
    coordinates = []
    for k in range(len(rows[0])):
        intervals = tuple(r[k] for r in rows)
        coordinates.append(tuple(w for blocks in ordered_partitions(len(rows))
                                 if (w := _order_witness(intervals, blocks)) is not None))
    return frozenset(frontier(tuple(zip(*columns)))
                     for columns in product(*coordinates))


def family_supports(patterns, families):
    return frozenset(frozenset(families[i] for i in f) for f in patterns)


def _oracle(world):
    """Independent sorted-profile scan; keep all equal-profile candidates."""
    retained = []
    for i in sorted(range(len(world)), key=lambda j: world[j]):
        if not any(world[j] != world[i]
                   and all(a <= b for a, b in zip(world[j], world[i]))
                   for j in retained):
            retained.append(i)
    return frozenset(retained)


def _require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def run_checks():
    intervals = tuple((a, b) for a in range(3) for b in range(a, 3))
    census = worlds_seen = 0
    for flat in product(intervals, repeat=4):
        boxes = (flat[:2], flat[2:])
        worlds = tuple((v[:2], v[2:])
                       for v in product(*(range(a, b + 1) for a, b in flat)))
        expected = frozenset(_oracle(w) for w in worlds)
        possible, necessary = box_membership(boxes)
        _require(possible == frozenset.union(*expected), "possible membership")
        _require(necessary == frozenset.intersection(*expected), "necessary membership")
        _require(rectangle_frontiers(boxes) == expected, "frontier patterns")
        census += 1
        worlds_seen += len(worlds)
    order_cases = order_worlds = 0
    grid = tuple(Fraction(k, 2) for k in range(5))
    for intervals3 in product(intervals, repeat=3):
        observed = set()
        for values in product(*(tuple(t for t in grid if a <= t <= b)
                                for a, b in intervals3)):
            observed.add(tuple(tuple(i for i, x in enumerate(values) if x == t)
                               for t in sorted(set(values))))
            order_worlds += 1
        rational = tuple(tuple(Fraction(t) for t in p) for p in intervals3)
        feasible = {b for b in ordered_partitions(3)
                    if _order_witness(rational, b) is not None}
        _require(feasible == observed, "ordered-partition feasibility")
        order_cases += 1
    uncertain = (((88, 88), (1, 3), (1, 3)), ((312, 312), (2, 4), (2, 4)))
    patterns = rectangle_frontiers(uncertain)
    _require(patterns == frozenset((frozenset((0,)), frozenset((0, 1)))),
             "possible coexistence is not necessary coexistence")
    _require(box_membership(uncertain) == (frozenset((0, 1)), frozenset((0,))),
             "strict coordinate minimum survives")
    correlated = (((1,), (0,), (2,)), ((1,), (2,), (0,)))
    _require(0 not in identify(correlated)[0], "correlated domination")
    _require(0 in box_membership((((1, 1),), ((0, 2),), ((0, 2),)))[0],
             "rectangular relaxation admits a fictitious world")
    interior = rectangle_frontiers((((0, 2),), ((1, 3),)))
    _require(frozenset((0, 1)) in interior, "interior tie retained")
    corner = frozenset(_oracle(((a,), (b,))) for a, b in product((0, 2), (1, 3)))
    _require(frozenset((0, 1)) not in corner, "corner-only negative control")
    return {"schema": "grand-gmi-empirical-frontier-identification-v1",
            "verdict": "PASS", "all_checks_green": True,
            "terminal": "EMPIRICAL_FRONTIER_IDENTIFICATION_FINITE_GREEN", "scope": "finite rational registers; full boxes or explicit worlds",
            "two_candidate_two_coordinate_boxes": census,
            "independent_integer_worlds": worlds_seen,
            "three_candidate_coordinate_boxes": order_cases,
            "independent_half_integer_order_worlds": order_worlds,
            "uncertain_parity_frontiers": [sorted(f) for f in sorted(patterns, key=lambda f: (len(f), sorted(f)))],
            "correlation_counterexample": "box-possible candidate never survives joint worlds",
            "corner_counterexample": "interior coexistence missed by endpoint worlds",
            "empirical_measurements_run": False}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
