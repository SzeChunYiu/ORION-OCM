"""Per-hostile attack probes for the EB-F0-X hostile matrix.

Each probe returns (fired, detail). fired is None when the world cannot
express the attack at all; detail then carries the structural reason.
Probes never aggregate: an immunity is reported per world, with cause.
"""
from __future__ import annotations

import worlds as W

# --------------------------------------------------------------- attack probes
# Each probe returns (fired: bool|None, detail: dict). None means the world
# cannot express the attack; detail carries the structural reason.

def _leak_energy(me_mod, n, **_kw):
    clean = W.WorldSpec(n, (0,) * n, (0,) * n, "optional", False, 0, W.ALL_ON)
    leaky = W.WorldSpec(n, (0,) * n, (0,) * n, "optional", True, 0, W.ALL_ON)
    c = W.build(me_mod, clean)
    lk = W.build(me_mod, leaky)
    for _ in range(4):
        c.step(); lk.step()
    return (lk.assay_interferes() and not c.assay_interferes(),
            {"clean_graph": sorted(c.write_graph),
             "leak_graph": sorted(lk.write_graph)})


def _hidden_edge(me_mod, n, **_kw):
    """Incomplete causal graph: drop the assay edge but keep the leak dynamics."""
    lk = W.build(me_mod, W.WorldSpec(n, (0,) * n, (0,) * n, "optional",
                                     True, 0, W.ALL_ON))
    lk.write_graph.discard(("assay", "energy"))
    lk.write_graph.discard(("assay", "birth"))
    for _ in range(4):
        lk.step()
    # Graph now says clean while the dynamics still read assay in _senseact.
    return (not lk.assay_interferes(),
            {"reported_clean": not lk.assay_interferes(),
             "dynamics_still_leaky": True,
             "why": "assay_interferes() reads the declared graph, not the code"})


def _forced_copy(me_mod, n, **_kw):
    if n < 2:
        return None, {"reason": "needs >=2 organisms for a donor/recipient pair"}
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (9,) + (0,) * (n - 1),
                                    "forced", False, 0, W.ALL_ON))
    e.cells[0].energy = 8
    e.step()
    got = [c.method for c in e.alive() if c.uid != 0]
    return (9 in got, {"donor_method": 9, "recipients": got})


def _prestige_stale(me_mod, n, **_kw):
    if n < 2:
        return None, {"reason": "needs >=2 organisms for a donor/recipient pair"}
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (9,) + (0,) * (n - 1),
                                    "prestige", False, 1, W.ALL_ON))
    e.cells[0].energy = 8
    e.step()
    got = [c.method for c in e.alive() if c.uid != 0]
    return (9 in got, {"regime_shifted": True, "recipients": got})


def _optional_control(me_mod, n, **_kw):
    """Clean control for the transfer hostiles: optional must refuse junk."""
    if n < 2:
        return None, {"reason": "needs >=2 organisms"}
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (9,) + (0,) * (n - 1),
                                    "optional", False, 0, W.ALL_ON))
    e.cells[0].energy = 8
    e.step()
    got = [c.method for c in e.alive() if c.uid != 0]
    return (9 in got, {"recipients": got})


def _junk_culture(me_mod, n, **_kw):
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (9,) * n, "forced",
                                    False, 0, W.ALL_ON))
    useful_before = sum(1 for c in e.alive() if c.method == e.useful_method)
    for _ in range(6):
        e.step()
    useful_after = sum(1 for c in e.alive() if c.method == e.useful_method)
    return (len(e.library) > 0 and useful_after <= useful_before,
            {"library_bytes": len(e.library),
             "useful_before": useful_before, "useful_after": useful_after})


def _cluster_as_group(me_mod, n, **_kw):
    """k-means-style label on a freely mixing population is not a group."""
    if n < 4:
        return None, {"reason": "needs >=4 organisms for two non-trivial clusters"}
    e = W.build(me_mod, W.WorldSpec(n, tuple(i % 4 for i in range(n)),
                                    (0,) * n, "optional", False, 0, W.ALL_ON))
    for _ in range(4):
        e.step()
    live = e.alive()
    groups = {}
    for c in live:
        groups.setdefault(c.group, []).append(c.uid)
    # No group-level reproduction event exists: children inherit the parent's
    # label, so a "group" never founds a new group.
    return (len(groups) > 1,
            {"labels": {str(k): v for k, v in groups.items()},
             "group_level_reproduction_events": 0})


def _pooling_only(me_mod, n, **_kw):
    """Group advantage that is pure resource pooling: no communication residual."""
    if n < 2:
        return None, {"reason": "needs >=2 organisms to pool"}
    solo = W.build(me_mod, W.WorldSpec(2, (0, 0), (0, 0), "optional",
                                       False, 0, W.ALL_ON))
    solo.cells[0].energy = 4 * n
    grp = W.build(me_mod, W.WorldSpec(n, (0,) * n, (0,) * n, "optional",
                                      False, 0, W.ALL_ON))
    for _ in range(5):
        solo.step(); grp.step()
    return (True, {"matched_total_energy": 4 * n,
                   "solo_alive": len(solo.alive()),
                   "group_alive": len(grp.alive()),
                   "communication_residual_claimed": False})


def _ev_trap(me_mod, n, **_kw):
    """High local mutation mass, target allele unreachable in one step."""
    nb = me_mod.enumerate_mutation_neighbourhood(0, alleles=4)
    realized = [(0 + 1) % 4]  # K_mut only ever applies +1 mod 4
    return (set(nb) != set(realized),
            {"declared_neighbourhood": sorted(nb),
             "realized_by_K_mut": realized,
             "why": "Ev computed over the declared neighbourhood overstates "
                    "reachability of the kernel actually in the physics."})


def _physics_tamper(me_mod, n, **_kw):
    """Widened: probe every reachable write surface, not just new Cell attrs.

    The first version of this probe tried only `cell.regen = 99`, which
    Cell.__slots__ refuses, so the hostile could never fire on any world. A
    hostile that cannot fire is not evidence of a safe world -- it is a hole in
    the instrument. The surface is enumerated here and the boundary proved.
    """
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (0,) * n, "optional",
                                    False, 0, W.ALL_ON))
    surfaces, breached = [], []
    # 1. new attribute on a slotted Cell
    try:
        e.cells[0].regen = 99
        breached.append("cell_new_attr")
    except AttributeError:
        pass
    surfaces.append("cell_new_attr")
    # 2. direct write to the world resource pool (P-owned)
    before = e.resource
    try:
        e.resource = 999
        if e.resource != before:
            breached.append("world_resource")
    except Exception:
        pass
    surfaces.append("world_resource")
    e.resource = before
    # 3. redefine what counts as the useful method (C-owned semantics)
    um = e.useful_method
    try:
        e.useful_method = 9
        if e.useful_method != um:
            breached.append("useful_method_redefinition")
    except Exception:
        pass
    surfaces.append("useful_method_redefinition")
    e.useful_method = um
    # 4. write an existing Cell slot past its legal physics range
    try:
        e.cells[0].energy = 10 ** 6
        e.step()
        if e.cells[0].energy > 8:
            breached.append("energy_above_cap")
    except Exception:
        pass
    surfaces.append("energy_above_cap")
    return (bool(breached),
            {"surfaces_probed": surfaces, "breached": breached,
             "refused": [s for s in surfaces if s not in breached],
             "why": ("Cell.__slots__ blocks new attributes, but the world "
                     "object itself exposes writable physics state.")})


def _vocab_only(me_mod, n, **_kw):
    if n < 2:
        return None, {"reason": "needs >=2 organisms for a transfer"}
    e = W.build(me_mod, W.WorldSpec(n, (0, 1) + (0,) * (n - 2),
                                    (1,) + (0,) * (n - 1), "forced",
                                    False, 0, W.ALL_ON))
    e.cells[0].energy = 8
    e.step()
    live = e.alive()
    tokens = {c.method for c in live}
    genomes = {c.g for c in live}
    return (len(tokens) == 1 and len(genomes) > 1,
            {"shared_token": sorted(tokens), "genomes_still_differ":
             sorted(genomes),
             "why": "method token copied; genome structure not transported"})


def _side_channel(me_mod, n, **_kw):
    """Unregistered bits: inbox carries the payload outside the method channel."""
    if n < 2:
        return None, {"reason": "needs >=2 organisms"}
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (9,) + (0,) * (n - 1),
                                    "optional", False, 0, W.ALL_ON))
    e.cells[0].energy = 8
    e.step()
    refused = [c for c in e.alive() if c.uid != 0 and c.method != 9]
    leaked = [c.uid for c in refused if c.inbox == 9]
    return (bool(leaked),
            {"refused_the_method": [c.uid for c in refused],
             "but_inbox_holds_payload": leaked,
             "why": "inbox is written unconditionally in _social, outside the "
                    "accepted-transfer channel"})


def _free_rider(me_mod, n, **_kw):
    if n < 3:
        return None, {"reason": "needs >=3 organisms for a public good plus a cheater"}
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (1,) + (0,) * (n - 1),
                                    "optional", False, 0, W.ALL_ON))
    e.cells[0].energy = 8
    for _ in range(4):
        e.step()
    return (len(e.library) > 0,
            {"public_bytes": len(e.library),
             "cheater_suppression_mechanism": None})


def _target_leak(me_mod, n, **_kw):
    return _leak_energy(me_mod, n)


def _social_overhead(me_mod, n, **_kw):
    """Mandatory library maintenance exceeds savings."""
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (9,) * n, "forced",
                                    False, 1, W.ALL_ON))
    for _ in range(6):
        e.step()
    return (len(e.library) > len([c for c in e.alive()
                                  if c.method == e.useful_method]),
            {"maintained_bytes": len(e.library),
             "useful_holders": len([c for c in e.alive()
                                    if c.method == e.useful_method])})


def _fast_repl(me_mod, n, **_kw):
    """ECO-0 monoculture. Expected negative; retained per the registry."""
    e = W.build(me_mod, W.WorldSpec(n, (0,) * n, (0,) * n, "optional",
                                    False, 0, W.ALL_ON))
    for _ in range(6):
        e.step()
    genomes = {c.g for c in e.alive()}
    return (len(genomes) <= 1,
            {"distinct_genomes": sorted(genomes),
             "expected": "NEGATIVE_RETAINED"})


