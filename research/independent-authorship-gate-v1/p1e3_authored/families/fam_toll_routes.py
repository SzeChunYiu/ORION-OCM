"""Toll Routes: parallel tolled paths to one summit, sharing a few tolls.

Fixed seed 1103. Six instances; path count, path lengths, shared toll atoms,
and toll prices vary. Each path is entered by buying its first toll; the
summit opens from any completed path, so the minimum seed is the cheapest
hike, not the shortest one.
"""

from families._common import make_instance

FAMILY_NAME = "Toll Routes"
FAMILY_BLURB = ("Several footpaths climb the same summit; paying a trail's "
                "entry toll sets the whole trail alight, so only entry prices "
                "and shared bridge tolls matter — mid-trail prices are decoys.")
SEED = 1103

# paths: list of (path name, step prices list); shared atoms are named alike
ROUTES = [
    ({"paths": [("west", [2, 3]), ("east", [6])]}, []),
    ({"paths": [("west", [1, 1, 9]), ("east", [4, 3]), ("north", [7])]}, []),
    ({"paths": [("west", [5, "shared_bridge", 2]),
                ("east", [3, "shared_bridge", 4])]}, []),
    ({"paths": [("west", [2, 2, 2, 8]), ("east", [9, 1]),
                ("north", [4, 4, 4])]}, []),
    ({"paths": [("west", [3, "pass_gate", 6]), ("east", ["pass_gate", 5, 1]),
                ("north", [2, 7])]}, []),
    ({"paths": [("west", [1, 8, 1]), ("east", [8, 1, 8]),
                ("north", [4, 4]), ("south", ["pass_gate", 3, 3])]}, ["pass_gate"]),
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, (spec, shared_atoms) in enumerate(ROUTES, 1):
        elements = ["summit"]
        weights = {"summit": 90}
        implications = []
        shared_seen = set(shared_atoms)
        for pname, prices in spec["paths"]:
            chain = []
            for j, price in enumerate(prices, 1):
                atom = price if isinstance(price, str) else "%s_step_%d" % (pname, j)
                if atom not in elements:
                    elements.append(atom)
                if atom not in chain:
                    chain.append(atom)
                if isinstance(price, int):
                    weights[atom] = price
                else:
                    weights.setdefault(atom, 5)
            for a, b in zip(chain, chain[1:]):
                implications.append({"if": [a], "then": [b]})
            implications.append({"if": [chain[-1]], "then": ["summit"]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": [],
            "excluded": [],
            "weights": weights,
            "goals": ["summit"],
        }
        out.append(make_instance(FAMILY_NAME, "toll_routes_%02d" % idx, core, {
            "paths": {p: pr for p, pr in spec["paths"]},
            "shared_tolls": shared_atoms,
            "tier": idx,
            "intent_note": "empty base; entry tolls light entire trails, mid-trail prices are decoys",
        }))
    return out
