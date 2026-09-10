"""Frozen v1 synthetic plant, loaded in place. This successor does not copy or retune it."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

LAB_DIR = Path(__file__).resolve().parents[1] / "g6-intervention-lab-v1"
V1_WORLD = LAB_DIR / "world.py"


def load_lab():
    name = "g6_intervention_lab_v1_world"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, V1_WORLD)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen plant {V1_WORLD}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fresh_incident(Lab, incident):
    return Lab.Incident(incident.incident_id, incident.generation, incident.hidden)


def clone_cohort(Lab, incidents):
    return [fresh_incident(Lab, incident) for incident in incidents]


def failed_from_probes(probes: list[dict[str, Any]], n_modules: int) -> tuple[int, ...]:
    failed = [0] * n_modules
    for probe in probes:
        if not probe["ok"]:
            failed[probe["index"]] = 1
    return tuple(failed)


def fail_closed_repair(Lab, incident, order: list[int]) -> dict[str, Any]:
    """Shared execution: probe in `order`, replace observed failures, stop at quality 1.

    Parents receive the same probe/intervene/restart permissions as the v1 selector.
    Hidden stuck sets are not passed into parent fit functions.
    """
    n_modules = Lab.N_MODULES
    world = Lab.World(incident.hidden)
    cost = 0
    seen: list[int] = []
    failed: list[int] = []
    sequence = list(dict.fromkeys([i for i in order if i in range(n_modules)] + list(range(n_modules))))
    for index in sequence:
        obs = world.probe(index)
        incident.probes.append(obs)
        cost += obs["cost"]
        seen.append(index)
        if not obs["ok"]:
            rec = world.intervene(index)
            incident.interventions.append({**rec, "phase": "shadow"})
            cost += rec["cost"]
            failed.append(index)
        if all(world.modules):
            break
    restarted = world.restart_clone()
    quality = int(all(restarted.modules))
    incident.adopted = tuple(failed)
    truth = Lab.independent_truth(incident.hidden)
    identified = frozenset(failed) == truth
    return {
        "quality": quality,
        "identified": int(identified),
        "cost": cost,
        "kappa": len(truth),
        "omega": (1.0 if identified else 0.0) / max(1, len(incident.probes)),
        "chi": max(1, len(sequence)),
        "n_probes": len(incident.probes),
        "n_replaced": len(failed),
        "order": sequence[: len(incident.probes)],
        "adopted": list(failed),
    }
