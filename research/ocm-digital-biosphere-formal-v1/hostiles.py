"""Hostile runners. Each instrument must be able to fail."""
from __future__ import annotations

import theorems


def run_all():
    rows = theorems.run_all()
    hostiles = [r for r in rows if r.get("status") == "HOSTILE_DETECTED"
                or r.get("status") == "COUNTEREXAMPLE"]
    required = {
        "H-LEAK-ASSAY-ENERGY", "H-FORCED-COPY", "H-VOCAB-ONLY", "H-EV-TRAP",
        "H-JUNK-CULTURE", "H-CLUSTER-AS-GROUP",
    }
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
        "instruments_can_fail": not missing,
    }
