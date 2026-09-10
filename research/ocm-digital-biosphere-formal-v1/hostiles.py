"""Hostile runners. Each instrument must be able to fail."""
from __future__ import annotations

import os

import lib
import theorems


def run_all():
    rows = theorems.run_all()
    hostiles = [r for r in rows if r.get("status") == "HOSTILE_DETECTED"
                or r.get("status") == "COUNTEREXAMPLE"]
    registry = lib.load_json(os.path.join(lib.ROOT, "HOSTILE_REGISTRY_V1.json"))
    required = set(h["id"] for h in registry.get("hostiles", []))
    unpaired = sorted(h["id"] for h in registry.get("hostiles", [])
                      if not h.get("clean_control"))
    seen = set()
    for r in rows:
        h = r.get("hostile")
        if h:
            seen.add(h)
    missing = sorted(required - seen)
    return {
        "n_rows": len(rows),
        "n_hostile_or_counterexample": len(hostiles),
        "required_hostiles": sorted(required),
        "seen_hostiles": sorted(seen),
        "missing_required": missing,
        "unpaired_clean_controls": unpaired,
        "instruments_can_fail": (not missing) and (not unpaired),
    }
