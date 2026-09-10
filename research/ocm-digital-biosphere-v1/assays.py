"""Protected observer-only cognition assays.

Scores never enter energy, replication threshold, or inheritance.
The live Earth is not mutated; assays run on a reproduction-frozen clone.
ASSAY_SELECTED_CONTROL is an explicit arm that is NOT in the first ensemble.
"""
from __future__ import annotations

from physics import OP_HARVEST, OP_MOVE, OP_SENSE, OP_STORE


def _mean_energy(earth):
    live = earth.alive()
    if not live:
        return 0.0
    return float(sum(c.energy for c in live)) / len(live)


def assay_memory_return(earth):
    """Can agents use stored sense to re-find a depleted-then-restored patch?"""
    clone = earth.clone_frozen_reproduction()
    # Drain resources except one beacon.
    beacon = (clone.w // 4, clone.h // 4)
    for pos, cell in clone.resources.items():
        for k in list(cell.keys()):
            if k.startswith("_"):
                continue
            cell[k] = 0 if pos != beacon else int(clone.p["resource_cap"])
    start_e = _mean_energy(clone)
    for _ in range(24):
        clone.step(assay_lock=True)
    live = clone.alive()
    if not live:
        return {"name": "memory_return", "score": 0.0, "n": 0}
    near = sum(1 for c in live if abs(c.x - beacon[0]) + abs(c.y - beacon[1]) <= 2)
    return {
        "name": "memory_return",
        "score": float(near) / len(live),
        "n": len(live),
        "energy_delta": _mean_energy(clone) - start_e,
        "feeds_reproduction": False,
    }


def assay_delayed_resource(earth):
    """Planning-ish: resource appears after delay at a fixed cell."""
    clone = earth.clone_frozen_reproduction()
    target = (clone.w // 2, clone.h // 3)
    for cell in clone.resources.values():
        for k in list(cell.keys()):
            if not k.startswith("_"):
                cell[k] = 0
    for _ in range(8):
        clone.step(assay_lock=True)
    clone.resources[target][clone.eco["resources"][0]] = int(clone.p["resource_cap"])
    for _ in range(16):
        clone.step(assay_lock=True)
    live = clone.alive()
    if not live:
        return {"name": "delayed_resource", "score": 0.0, "n": 0}
    near = sum(1 for c in live if abs(c.x - target[0]) + abs(c.y - target[1]) <= 2)
    return {
        "name": "delayed_resource",
        "score": float(near) / len(live),
        "n": len(live),
        "feeds_reproduction": False,
    }


def assay_message_coordination(earth):
    """Do inbox/outbox exist, and does any agent receive a neighbor message?"""
    clone = earth.clone_frozen_reproduction()
    recvs = 0
    for _ in range(12):
        clone.step(assay_lock=True)
        recvs += sum(1 for c in clone.alive() if c.msgs_inbox)
    live = max(1, len(clone.alive()))
    return {
        "name": "message_coordination",
        "score": min(1.0, float(recvs) / (12.0 * live)),
        "n": len(clone.alive()),
        "feeds_reproduction": False,
    }


def run_observer_battery(earth):
    return [
        assay_memory_return(earth),
        assay_delayed_resource(earth),
        assay_message_coordination(earth),
    ]


def assert_assays_do_not_feed(earth, before_census):
    """Reproduction / energy of the live Earth must be unchanged by assays."""
    after = earth.census()
    if after["n_births"] != before_census["n_births"]:
        return "FAIL_ASSAY_FED_BIRTHS"
    if after["organism_energy"] != before_census["organism_energy"]:
        return "FAIL_ASSAY_FED_ENERGY"
    if after["tick"] != before_census["tick"]:
        return "FAIL_ASSAY_ADVANCED_LIVE_TICK"
    return "PASS"
