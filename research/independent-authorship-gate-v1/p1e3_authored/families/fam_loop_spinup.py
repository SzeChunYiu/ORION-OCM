"""Loop Spinup: closed flywheel rings that idle until seeded, then self-run.

Fixed seed 1107. Six instances; ring sizes, entry prices, ring-to-ring
couplings, and one poisoned ring vary. A ring with no lit atom never turns;
one seeded atom spins the whole loop, so the cheapest entry point is the game.
"""

from families._common import make_instance

FAMILY_NAME = "Loop Spinup"
FAMILY_BLURB = ("Flywheels of linked arms that only turn if some arm is already "
                "moving; each ring offers a few entry cranks at different prices, "
                "rings can crank rings, and one ring hides a poisoned arm.")
SEED = 1107

# rings: list of (name, size, [(atom, cost)] entry prices)
RINGS = [
    {"rings": [("red", 4, {"red_a1": 5, "red_a2": 2})]},
    {"rings": [("red", 5, {"red_a1": 4, "red_a2": 7, "red_a3": 3}),
               ("blue", 3, {"blue_a1": 6})],
     "couple": [("red", 2, "blue")]},
    {"rings": [("red", 6, {"red_a1": 2, "red_a2": 9})],
     "poison": [("red", 3)]},
    {"rings": [("red", 4, {"red_a1": 3}), ("blue", 4, {"blue_a1": 5}),
               ("green", 3, {"green_a1": 7})],
     "couple": [("red", 1, "blue"), ("blue", 2, "green")]},
    {"rings": [("red", 5, {"red_a1": 8, "red_a2": 1})],
     "poison": [("red", 1), ("red", 5)]},
    {"rings": [("red", 3, {"red_a1": 2}), ("blue", 3, {"blue_a1": 9})],
     "couple": [("red", 1, "blue"), ("blue", 1, "red")]},
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, spec in enumerate(RINGS, 1):
        elements, weights, implications, excluded = [], {}, [], []
        ring_atoms = {}
        for name, size, entries in spec["rings"]:
            atoms = ["%s_a%d" % (name, i) for i in range(1, size + 1)]
            ring_atoms[name] = atoms
            elements += atoms
            for a in atoms:
                weights[a] = 99
            for e, cost in entries.items():
                weights[e] = cost
            for a, b in zip(atoms, atoms[1:] + atoms[:1]):
                implications.append({"if": [a], "then": [b]})
        for name, pos in spec.get("poison", []):
            excluded.append(ring_atoms[name][pos - 1])
        for src, pos, dst in spec.get("couple", []):
            implications.append({"if": [ring_atoms[src][pos - 1],
                                        ring_atoms[src][pos % len(ring_atoms[src])]],
                                 "then": [ring_atoms[dst][0]]})
        elements.append("flywheel")
        weights["flywheel"] = 99
        for atoms in ring_atoms.values():
            implications.append({"if": [atoms[1]], "then": ["flywheel"]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": [],
            "excluded": excluded,
            "weights": weights,
            "goals": ["flywheel"],
        }
        out.append(make_instance(FAMILY_NAME, "loop_spinup_%02d" % idx, core, {
            "rings": {n: s for n, s, _ in spec["rings"]},
            "entry_prices": {n: e for n, _, e in spec["rings"]},
            "poisoned_arms": excluded,
            "tier": idx,
            "intent_note": "seed any one arm cheaply; poison arms block their entries",
        }))
    return out
