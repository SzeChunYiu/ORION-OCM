"""Trap Vaults: cheap keys spring excluded traps; safe keys cost more.

Fixed seed 1104. Six instances; trap depth, number of trapped keys, whether
any safe key exists, and the arity of safe routes vary. Closure alone may look
innocent; the seed question is where the poison hides.
"""

from families._common import make_instance

FAMILY_NAME = "Trap Vaults"
FAMILY_BLURB = ("Vault keys of suspicious cheapness spring poison needles that "
                "ruin the whole run; honest keys cost more. Some vaults have no "
                "honest key at all, and only reading the needle-rules tells you.")
SEED = 1104

# (cheap keys [(name, cost)], safe specs, impossible flag)
# safe spec: (atoms with costs, chain to vault, conjunctions needed)
VAULTS = [
    {"cheap": [("rusty_key", 1)], "safe": [("brass_key", 5)]},
    {"cheap": [("rusty_key", 1), ("bent_key", 2)],
     "safe": [("brass_key", 4), ("steel_key", 4)]},
    {"cheap": [("rusty_key", 1)], "safe": [("long_key_a", 2), ("long_key_b", 3)],
     "safe_joint": True},
    {"cheap": [("rusty_key", 1), ("bent_key", 1), ("bone_key", 2)],
     "safe": []},
    {"cheap": [("rusty_key", 1), ("bent_key", 2)],
     "safe": [("steel_key", 9)]},
    {"cheap": [("rusty_key", 1)],
     "safe": [("ivory_key_a", 3), ("ivory_key_b", 3), ("ivory_key_c", 3)],
     "safe_joint": True},
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, spec in enumerate(VAULTS, 1):
        elements = ["camp", "vault_open"]
        implications = []
        weights = {"vault_open": 99}
        excluded = []
        for name, cost in spec["cheap"]:
            elements += [name, "needle_" + name]
            weights[name] = cost
            excluded.append("needle_" + name)
            implications.append({"if": ["camp", name], "then": ["needle_" + name]})
            implications.append({"if": ["needle_" + name], "then": ["vault_open"]})
        joint = spec.get("safe_joint", False)
        safe_atoms = [n for n, _ in spec["safe"]]
        for name, cost in spec["safe"]:
            elements.append(name)
            weights[name] = cost
        if spec["safe"]:
            if joint:
                implications.append({"if": ["camp"] + safe_atoms,
                                     "then": ["vault_open"]})
            else:
                for name in safe_atoms:
                    implications.append({"if": ["camp", name],
                                         "then": ["vault_open"]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": ["camp"],
            "excluded": excluded,
            "weights": weights,
            "goals": ["vault_open"],
        }
        out.append(make_instance(FAMILY_NAME, "trap_vaults_%02d" % idx, core, {
            "cheap_keys": [n for n, _ in spec["cheap"]],
            "safe_keys": safe_atoms,
            "safe_route_needs_all": joint,
            "tier": idx,
            "intent_note": "cheap keys spring needles; vault_open priced to forbid direct seeding",
        }))
    return out
