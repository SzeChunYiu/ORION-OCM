"""All 15 registered hostiles across all 8 registered worlds (issue #296 sec.16).

The frozen hostiles.py gates on a hand-written `required` set of six ids, so
nine of the fifteen entries in HOSTILE_REGISTRY_V1.json never gate anything.
This module runs every registered hostile against every registered world and
reports, per (hostile, world):

  FIRED               the hostile flipped the instrument
  SILENT_CLEAN        the matched clean control stayed silent (required)
  IMMUNE_<reason>     the world cannot express the attack -- structural, with
                      the reason named, never aggregated away

A hostile that fires nowhere, and a clean control that is not silent, are both
defects of the instrument, not of the world.
"""
from __future__ import annotations

import json
import os

import hostile_probes as P

FIRED = "FIRED"
NOT_FIRED = "NOT_FIRED"
SILENT = "SILENT_CLEAN"
NOISY = "CLEAN_CONTROL_NOT_SILENT"


def load_registries(contract_dir: str) -> dict:
    out = {}
    for name in ("HOSTILE_REGISTRY_V1.json", "EXACT_WORLD_REGISTRY_V1.json"):
        p = os.path.join(contract_dir, name)
        with open(p, "r", encoding="utf-8") as fh:
            out[name] = json.load(fh)
    return out


def frozen_gate_coverage(contract_dir: str, hostiles_mod) -> dict:
    """Which registered hostiles actually gate the frozen EB-F0 result?"""
    reg = load_registries(contract_dir)["HOSTILE_REGISTRY_V1.json"]
    registered = [h["id"] for h in reg["hostiles"]]
    rep = hostiles_mod.run_all()
    required = set(rep.get("required_hostiles") or [])
    ungated = sorted(set(registered) - required)
    return {
        "n_registered": len(registered),
        "n_required_by_gate": len(required),
        "registered": sorted(registered),
        "required_by_gate": sorted(required),
        "registered_but_ungated": ungated,
        "gate_covers_registry": not ungated,
        "verdict": ("GATE_UNDER_COVERS_REGISTRY" if ungated
                    else "GATE_COVERS_REGISTRY"),
        "note": ("instruments_can_fail is computed as `not missing` against "
                 "the required set only, so ungated hostiles cannot affect "
                 "GATE_HOLDS."),
    }


PROBES = {
    "H-LEAK-ASSAY-ENERGY": P._leak_energy,
    "H-LEAK-HIDDEN-EDGE": P._hidden_edge,
    "H-TARGET-LEAK": P._target_leak,
    "H-SOCIAL-OVERHEAD": P._social_overhead,
    "H-FORCED-COPY": P._forced_copy,
    "H-PRESTIGE-STALE": P._prestige_stale,
    "H-SIDE-CHANNEL": P._side_channel,
    "H-POOLING-ONLY": P._pooling_only,
    "H-CLUSTER-AS-GROUP": P._cluster_as_group,
    "H-VOCAB-ONLY": P._vocab_only,
    "H-EV-TRAP": P._ev_trap,
    "H-JUNK-CULTURE": P._junk_culture,
    "H-PHYSICS-TAMPER": P._physics_tamper,
    "H-FAST-REPL": P._fast_repl,
    "H-FREE-RIDER": P._free_rider,
}

# Clean controls that MUST stay silent for the transfer-family hostiles.
CLEAN_CONTROLS = {
    "H-FORCED-COPY": P._optional_control,
    "H-PRESTIGE-STALE": P._optional_control,
    "H-SIDE-CHANNEL": None,  # its own control is the refusal it detects
}


def run_matrix(me_mod, contract_dir: str) -> dict:
    reg = load_registries(contract_dir)
    hostiles = reg["HOSTILE_REGISTRY_V1.json"]["hostiles"]
    micro_worlds = reg["EXACT_WORLD_REGISTRY_V1.json"]["worlds"]
    cells = []
    for h in hostiles:
        hid = h["id"]
        probe = PROBES.get(hid)
        for mw in micro_worlds:
            n = int(mw["n_org"])
            if probe is None:
                cells.append({"hostile": hid, "world": mw["id"], "n_org": n,
                              "status": "CANNOT_CHECK_NO_PROBE_IMPLEMENTED",
                              "missing_instrument": "attack probe for %s" % hid})
                continue
            try:
                fired, detail = probe(me_mod, n)
            except Exception as exc:
                cells.append({"hostile": hid, "world": mw["id"], "n_org": n,
                              "status": "CANNOT_CHECK_PROBE_RAISED",
                              "missing_instrument":
                                  "probe that runs at n=%d" % n,
                              "error": "%s: %s" % (type(exc).__name__, exc)})
                continue
            if fired is None:
                cells.append({"hostile": hid, "world": mw["id"], "n_org": n,
                              "status": "IMMUNE_STRUCTURAL",
                              "reason": detail.get("reason"),
                              "detail": detail})
                continue
            row = {"hostile": hid, "world": mw["id"], "n_org": n,
                   "status": FIRED if fired else NOT_FIRED, "detail": detail}
            ctrl = CLEAN_CONTROLS.get(hid)
            if ctrl is not None:
                cfired, cdetail = ctrl(me_mod, n)
                if cfired is None:
                    row["clean_control"] = "IMMUNE_STRUCTURAL"
                else:
                    row["clean_control"] = NOISY if cfired else SILENT
                row["clean_control_detail"] = cdetail
            cells.append(row)
    return _summarize(cells, hostiles)


def _summarize(cells: list, hostiles: list) -> dict:
    per = {}
    for c in cells:
        d = per.setdefault(c["hostile"], {
            "fired_in": [], "silent_in": [], "immune_in": [],
            "cannot_check": [], "clean_control_noisy_in": []})
        if c["status"] == FIRED:
            d["fired_in"].append(c["world"])
        elif c["status"] == NOT_FIRED:
            d["silent_in"].append(c["world"])
        elif c["status"].startswith("IMMUNE"):
            d["immune_in"].append({"world": c["world"],
                                   "reason": c.get("reason")})
        else:
            d["cannot_check"].append({"world": c["world"],
                                      "status": c["status"],
                                      "missing_instrument":
                                          c.get("missing_instrument")})
        if c.get("clean_control") == NOISY:
            d["clean_control_noisy_in"].append(c["world"])
    never_fire = sorted(h for h, d in per.items() if not d["fired_in"])
    noisy = sorted(h for h, d in per.items() if d["clean_control_noisy_in"])
    return {
        "instrument": "hostile_matrix_15x8",
        "n_hostiles": len(hostiles),
        "n_worlds": len({c["world"] for c in cells}),
        "n_cells": len(cells),
        "cells": cells,
        "per_hostile": per,
        "hostiles_that_never_fire": never_fire,
        "clean_controls_not_silent": noisy,
        "can_fail": True,
        "verdict": ("ALL_HOSTILES_FIRE_SOMEWHERE" if not never_fire
                    else "SOME_HOSTILES_NEVER_FIRE"),
    }
