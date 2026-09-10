"""Forkjoin Lattice: layered DAG, joins of two parents per node.

Fixed seed 1106. Six instances; depth, width, fan-in pattern, and how much of
the ground layer starts lit vary. A node needs all its listed parents, so one
dark parent holds the whole upper cone dark.
"""

from families._common import make_instance

FAMILY_NAME = "Forkjoin Lattice"
FAMILY_BLURB = ("A lattice of forking wires and rejoining junctions built upward "
                "from a ground row of sockets; every junction demands its full "
                "parent set, and the apex answers only to a fully lit ground.")
SEED = 1106

# (depth, width, base ground positions 1-indexed, shortcut pairs)
LATTICES = [
    (3, 3, [1, 2], []),
    (4, 3, [1, 3], []),
    (4, 4, [1, 2, 4], [(2, 3)]),
    (4, 3, [2], []),
    (4, 4, [1, 2], [(1, 3), (2, 4)]),
    (5, 3, [1, 2, 3], [(2, 2)]),
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, (depth, width, base_cols, shortcuts) in enumerate(LATTICES, 1):
        names = {}
        for l in range(depth):
            for c in range(width):
                names[(l, c)] = "cell_%d_%d" % (l, c + 1)
        elements = sorted(names.values()) + ["apex"]
        weights = {"apex": 99}
        base = [names[(0, c - 1)] for c in base_cols]
        for l in range(depth):
            for c in range(width):
                weights[names[(l, c)]] = 1 + (l * 2 + c) % 8
        weights["apex"] = 99
        implications = []
        for l in range(depth - 1):
            for c in range(width):
                pn = [names[(l, c)], names[(l, (c + 1) % width)]]
                implications.append({"if": pn, "then": [names[(l + 1, c)]]})
        for (l, c) in shortcuts:
            implications.append({"if": [names[(l, c - 1)]],
                                 "then": [names[(l + 1, c - 1)]]})
        implications.append({"if": [names[(depth - 1, c)] for c in range(width)],
                             "then": ["apex"]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": base,
            "excluded": [],
            "weights": weights,
            "goals": ["apex"],
        }
        out.append(make_instance(FAMILY_NAME, "forkjoin_%02d" % idx, core, {
            "depth": depth, "width": width,
            "lit_ground_columns": base_cols,
            "single_parent_shortcuts": shortcuts,
            "tier": idx,
            "intent_note": "each junction needs both listed parents; shortcuts are wires",
        }))
    return out
