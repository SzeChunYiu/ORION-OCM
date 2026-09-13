"""Finite rational candidate/schedule profiles; physical premises remain external."""
from fractions import Fraction as F


def validate(rows):
    """Rows are (stable candidate ID, declared label, full joint cost tuple)."""
    if not isinstance(rows, (tuple, list)):
        raise ValueError("explicit finite row sequence required")
    ids, width = set(), None
    for name, label, point in rows:
        if not isinstance(name, str) or not name or name in ids:
            raise ValueError("unique nonempty candidate IDs required")
        if not isinstance(label, str) or not label:
            raise ValueError("declared label required")
        ids.add(name)
        if not isinstance(point, tuple) or not point or any(
            not isinstance(x, F) or x < 0 for x in point
        ):
            raise ValueError("finite nonnegative rational profile tuple required")
        if width is None:
            width = len(point)
        if len(point) != width:
            raise ValueError("profile dimensions must match")
    return width


def weak(a, b):
    if len(a) != len(b):
        raise ValueError("profile dimensions must match")
    return all(x <= y for x, y in zip(a, b))


def dominates(a, b):
    return weak(a, b) and a != b


def frontier(rows):
    validate(rows)
    return tuple(row for row in rows
                 if not any(dominates(other[2], row[2]) for other in rows))


def constructive_closure(actual, constructive_ids, necessary):
    """Check complete finite certificate sets, then recover all actual fibers."""
    validate(actual)
    chosen = tuple(row for row in actual if row[0] in constructive_ids)
    if not chosen or set(constructive_ids) != {row[0] for row in chosen}:
        raise ValueError("nonempty actual constructive register required")
    width = len(chosen[0][2])
    if any(not isinstance(p, tuple) or len(p) != width or
           any(not isinstance(x, F) or x < 0 for x in p) for p in necessary):
        raise ValueError("invalid necessary profile set")
    if any(row[2] not in necessary for row in actual):
        raise ValueError("relaxation omits an actual profile")
    if any(not any(weak(c[2], p) for c in chosen) for p in necessary):
        raise ValueError("constructive coverage fails")
    selected_profiles = {row[2] for row in frontier(chosen)}
    return tuple(row for row in actual if row[2] in selected_profiles)


def completion_report(worlds):
    """Exact consequences of a supplied nonempty finite compatible set."""
    if not isinstance(worlds, (tuple, list)) or not worlds:
        raise ValueError("nonempty finite compatible set required")
    selected = [frontier(rows) for rows in worlds]
    labels = [frozenset(row[1] for row in rows) for rows in selected]
    names = [frozenset(row[0] for row in rows) for rows in selected]
    stable_labels, widths = {}, set()
    for rows in worlds:
        width = validate(rows)
        if width is not None:
            widths.add(width)
        for name, label, _ in rows:
            if name in stable_labels and stable_labels[name] != label:
                raise ValueError("candidate identity changes label between worlds")
            stable_labels[name] = label
    if len(widths) > 1:
        raise ValueError("worlds must share the profile interface")
    identified = all(x == labels[0] for x in labels)
    return {
        "selected_ids": tuple(names),
        "selected_label_sets": tuple(labels),
        "label_set_identified": identified,
        "robust_unique_label": next(iter(labels[0])) if identified and len(labels[0]) == 1 else None,
        "selection_exists_in_every_world": all(labels),
        "common_optimal_candidates": frozenset.intersection(*names),
    }


def feasible_rows(universe, edges, starts, adequate):
    """Only graph reachability; exact adequacy/full joint profiles are supplied."""
    validate(universe)
    ids = {row[0] for row in universe}
    if not set(starts) <= ids or not set(adequate) <= ids:
        raise ValueError("unknown initial/adequate candidate")
    if any(s not in ids or t not in ids for s, t in edges):
        raise ValueError("unknown development edge endpoint")
    seen = set(starts)
    while True:
        nxt = seen | {t for s, t in edges if s in seen}
        if nxt == seen:
            break
        seen = nxt
    return tuple(row for row in universe if row[0] in seen and row[0] in adequate)
