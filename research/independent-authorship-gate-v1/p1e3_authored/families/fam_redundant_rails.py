"""Redundant Rails: one junction served by many rails at different arity/price.

Fixed seed 1109. Six instances; conjunction arity, singleton price, decoy
count, and nesting of redundancy vary. Several rails reach the same junction;
only the price/arity trade decides the cheapest seed, and decoy rails feed a
near-identical junction that leads nowhere.
"""

from families._common import make_instance

FAMILY_NAME = "Redundant Rails"
FAMILY_BLURB = ("Junction boxes wired in parallel: a bundle of cheap switches "
                "thrown together does the job of one costly master switch, and "
                "look-alike junctions tempt the eye while powering nothing.")
SEED = 1109

# (bundle arity, bundle per-switch price, master price, decoys, nested level)
RAILS = [
    (2, 1, 4, 0, 1),
    (3, 1, 3, 1, 1),
    (2, 2, 5, 2, 1),
    (4, 1, 5, 0, 2),
    (3, 2, 7, 0, 2),
    (2, 1, 2, 3, 1),
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, (arity, cheap, master, decoys, nest) in enumerate(RAILS, 1):
        elements, weights, implications = [], {}, []
        for level in range(1, nest + 1):
            jname = "junction_%d" % level
            elements.append(jname)
            weights[jname] = 99
            if level > 1:
                implications.append({"if": ["junction_%d" % (level - 1)],
                                     "then": [jname]})
            bundle = ["sw_%d_%d" % (level, i) for i in range(1, arity + 1)]
            master_sw = "master_%d" % level
            elements += bundle + [master_sw]
            for s in bundle:
                weights[s] = cheap
            weights[master_sw] = master
            implications.append({"if": bundle, "then": [jname]})
            implications.append({"if": [master_sw], "then": [jname]})
        elements.append("main_line")
        weights["main_line"] = 99
        implications.append({"if": ["junction_%d" % nest], "then": ["main_line"]})
        for d in range(1, decoys + 1):
            dj = "decoy_junction_%d" % d
            ds = ["decoy_sw_%d_%d" % (d, i) for i in range(1, arity + 1)]
            elements += [dj] + ds
            weights[dj] = 99
            for s in ds:
                weights[s] = cheap
            implications.append({"if": ds, "then": [dj]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": [],
            "excluded": [],
            "weights": weights,
            "goals": ["main_line"],
        }
        out.append(make_instance(FAMILY_NAME, "rails_%02d" % idx, core, {
            "bundle_arity": arity,
            "bundle_switch_price": cheap,
            "master_price": master,
            "decoy_junctions": decoys,
            "nested_levels": nest,
            "tier": idx,
            "intent_note": "compare bundle total vs master price per level; decoys are inert",
        }))
    return out
