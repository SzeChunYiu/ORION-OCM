"""Guild Overlap: craft guilds sharing members; crests meet at bridges.

Fixed seed 1105. Six instances; guild count, pairwise overlap, charter
requirements, and starter memberships vary. Shared members let one seeded
artisan advance two guilds at once, but only where the overlap is real.
"""

from families._common import make_instance

FAMILY_NAME = "Guild Overlap"
FAMILY_BLURB = ("Craft guilds whose membership rolls overlap; each guild elects "
                "a crest once enough artisans stand, and grand charters demand "
                "crests plus a bridge fee. Shared artisans are the lever.")
SEED = 1105

# guilds: list of member lists (reused names = shared members)
GUILDS = [
    {"guilds": [["weaver", "dyer", "spinner"], ["dyer", "miller"]],
     "base": ["weaver"], "bridge_cost": 3},
    {"guilds": [["weaver", "dyer", "spinner"], ["dyer", "miller", "spinner"]],
     "base": ["weaver"], "bridge_cost": 2},
    {"guilds": [["smith", "tinker", "founder"], ["founder", "smith", "polisher"],
                ["polisher", "tinker"]], "base": [], "bridge_cost": 4},
    {"guilds": [["smith", "founder"], ["founder", "polisher"], ["polisher", "smith"]],
     "base": [], "bridge_cost": 1},
    {"guilds": [["weaver", "dyer", "spinner", "miller"],
                ["dyer", "spinner"], ["miller", "weaver"]],
     "base": ["weaver"], "bridge_cost": 5},
    {"guilds": [["smith", "tinker"], ["tinker", "founder"], ["founder", "polisher"],
                ["polisher", "smith"]], "base": ["smith"], "bridge_cost": 2},
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, spec in enumerate(GUILDS, 1):
        guilds = spec["guilds"]
        elements = ["bridge_fee", "grand_charter"]
        weights = {"bridge_fee": spec["bridge_cost"], "grand_charter": 99}
        implications = []
        crests = []
        for gi, members in enumerate(guilds, 1):
            crest = "crest_%d" % gi
            crests.append(crest)
            elements.append(crest)
            weights[crest] = 99
            for m in members:
                if m not in elements:
                    elements.append(m)
            implications.append({"if": members, "then": [crest]})
        implications.append({"if": crests + ["bridge_fee"], "then": ["grand_charter"]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": spec["base"],
            "excluded": [],
            "weights": weights,
            "goals": ["grand_charter"],
        }
        out.append(make_instance(FAMILY_NAME, "guild_overlap_%02d" % idx, core, {
            "guilds": guilds,
            "charter_needs": crests + ["bridge_fee"],
            "starter_members": spec["base"],
            "tier": idx,
            "intent_note": "shared members count toward every guild they belong to",
        }))
    return out
