"""Near-Miss Keys: goal gates lacking exactly one antecedent.

Fixed seed 1108. Six instances; which antecedents are missing, how many
interchangeable substitutes exist, substitute prices, and the number of
near-miss goals vary. Red-herring atoms imply nothing and only cost money.
"""

from families._common import make_instance

FAMILY_NAME = "Near-Miss Keys"
FAMILY_BLURB = ("Locks assembled to a single missing piece; several look-alike "
                "parts could complete each lock at different prices, and the "
                "bench is littered with parts that fit nothing at all.")
SEED = 1108

# each gate: (name, parts, lit parts, substitute candidates with costs)
LOCKS = [
    {"gates": [("lock_a", ["p1", "p2", "p3"], ["p1", "p2"],
                {"sub_x": 3, "sub_y": 6, "sub_z": 2})],
     "herrings": {"junk_1": 1, "junk_2": 1}},
    {"gates": [("lock_a", ["p1", "p2", "p3"], ["p1", "p3"],
                {"sub_x": 4, "sub_y": 4})],
     "herrings": {"junk_1": 2}},
    {"gates": [("lock_a", ["p1", "p2", "p3", "p4"], ["p1", "p2", "p4"],
                {"sub_x": 7, "sub_y": 5})],
     "herrings": {}},
    {"gates": [("lock_a", ["p1", "p2", "p3"], ["p1", "p2"],
                {"sub_x": 2, "sub_y": 9}),
               ("lock_b", ["q1", "q2", "q3"], ["q2", "q3"],
                {"sub_u": 3, "sub_v": 8})],
     "herrings": {"junk_1": 1}},
    {"gates": [("lock_a", ["p1", "p2", "p3"], ["p2", "p3"],
                {"sub_x": 5, "sub_y": 5, "sub_z": 5})],
     "herrings": {"junk_1": 1, "junk_2": 2, "junk_3": 3}},
    {"gates": [("lock_a", ["p1", "p2", "p3"], ["p1"], {"sub_x": 2}),
               ("lock_b", ["q1", "q2"], ["q1", "q2"], {"sub_u": 6})],
     "herrings": {"junk_1": 4}},
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, spec in enumerate(LOCKS, 1):
        elements, weights, implications, base, goals = [], {}, [], [], []
        for name, parts, lit, subs in spec["gates"]:
            goals.append(name)
            elements.append(name)
            weights[name] = 99
            for p in parts:
                if p not in elements:
                    elements.append(p)
            implications.append({"if": parts[:], "then": [name]})
            for sub, cost in subs.items():
                elements.append(sub)
                weights[sub] = cost
                implications.append({"if": sorted(set(lit)) + [sub],
                                     "then": [name]})
            base += [p for p in lit]
        for h, cost in spec["herrings"].items():
            elements.append(h)
            weights[h] = cost
        core = {
            "elements": elements,
            "implications": implications,
            "base": sorted(set(base)),
            "excluded": [],
            "weights": weights,
            "goals": goals,
        }
        out.append(make_instance(FAMILY_NAME, "nearmiss_%02d" % idx, core, {
            "gates": [g[0] for g in spec["gates"]],
            "substitutes": {g[0]: g[3] for g in spec["gates"]},
            "herrings": sorted(spec["herrings"]),
            "tier": idx,
            "intent_note": "lock fires from all parts, or lit parts plus one substitute",
        }))
    return out
