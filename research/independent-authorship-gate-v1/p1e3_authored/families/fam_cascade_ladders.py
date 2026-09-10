"""Cascade Ladders: braided forward chains with skip rungs and dead-end spurs.

Fixed seed 1101. Six instances; ladder length, skip-rung pattern, spur count,
and goal placement vary. The interesting structure: skipping ahead via rungs
can leap over a dead-end spur, and the goal sits past the last honest rung.
"""

from families._common import make_instance

FAMILY_NAME = "Cascade Ladders"
FAMILY_BLURB = ("A ladder of rungs where each rung lights the next; occasional "
                "skip rungs jump two or three ahead, while dead-end spurs branch "
                "off and go nowhere. One asks how far the cascade actually runs.")
SEED = 1101

# (length, skip pattern [(i, jump)], spurs [rung index], goal rung)
LADDERS = [
    (6,  [(1, 3)],            [2],      6),
    (8,  [(2, 3), (5, 2)],    [1, 4],   8),
    (10, [(3, 4)],            [2, 6],   10),
    (12, [(1, 2), (4, 5)],    [3, 8],   12),
    (9,  [(2, 4), (7, 2)],    [5],      9),
    (14, [(3, 3), (6, 4), (10, 3)], [4, 9], 14),
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, (length, skips, spurs, goal_rung) in enumerate(LADDERS, 1):
        rungs = ["rung_%02d" % i for i in range(1, length + 1)]
        elements = list(rungs)
        implications = []
        for i in range(length - 1):
            implications.append({"if": [rungs[i]], "then": [rungs[i + 1]]})
        for start, jump in skips:
            implications.append({"if": [rungs[start - 1]],
                                 "then": [rungs[start - 1 + jump]]})
        spur_atoms = []
        for s in spurs:
            sp = ["spur_%02d_a" % s, "spur_%02d_b" % s]
            spur_atoms.extend(sp)
            implications.append({"if": [rungs[s - 1]], "then": [sp[0]]})
            implications.append({"if": [sp[0]], "then": [sp[1]]})
        elements += spur_atoms
        core = {
            "elements": elements,
            "implications": implications,
            "base": [rungs[0]],
            "excluded": [],
            "weights": {},
            "goals": [rungs[goal_rung - 1]],
        }
        out.append(make_instance(FAMILY_NAME, "cascade_ladders_%02d" % idx, core, {
            "ladder_length": length,
            "skip_rungs": skips,
            "spur_positions": spurs,
            "tier": idx,
            "intent_note": "chain should close to the top rung; spurs are inert tails",
        }))
    return out
