"""Family registry for the implication-system studio package."""

FAMILY_MODULES = [
    "fam_cascade_ladders",
    "fam_quorum_gates",
    "fam_toll_routes",
    "fam_trap_vaults",
    "fam_guild_overlap",
    "fam_forkjoin_lattice",
    "fam_loop_spinup",
    "fam_nearmiss_keys",
    "fam_redundant_rails",
    "fam_ledger_tradeoffs",
]

FAMILIES = FAMILY_MODULES

__all__ = ["FAMILY_MODULES", "FAMILIES", "counts", "total"]


def counts():
    import importlib
    out = {}
    for m in FAMILY_MODULES:
        mod = importlib.import_module("families." + m)
        out[mod.FAMILY_NAME] = len(mod.emit(mod.SEED))
    return out


def total():
    return sum(counts().values())
