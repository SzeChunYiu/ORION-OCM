"""G6 intervention-effect laboratory.

Root-cause repair for CANNOT_CHECK_MISSING_RAW_TRACES: this world emits a
probe transcript on every incident. Historical M11 cycles are not relabeled.

Hidden faults are recovered for scoring by a reserved simulator stream that the
learner never reads. Generator intent is not the training label.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass, field
from typing import Any


N_MODULES = 6
CONSTITUTION = frozenset({"check", "authority", "meter", "commit"})
PROBE_COST = 1
REPLACE_COST = 4


def _digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class HiddenState:
    stuck: frozenset[int]
    seed: str

    def syndrome(self) -> tuple[int, ...]:
        # Observable failure signature: parity of stuck set on three overlapping windows.
        bits = []
        for start in (0, 2, 4):
            bits.append(sum(1 for i in range(start, start + 2) if i in self.stuck) % 2)
        return tuple(bits)


@dataclass
class Incident:
    incident_id: str
    generation: int
    hidden: HiddenState
    probes: list[dict[str, Any]] = field(default_factory=list)
    interventions: list[dict[str, Any]] = field(default_factory=list)
    adopted: tuple[int, ...] = ()
    protected: bool = False

    @property
    def transcript(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "generation": self.generation,
            "syndrome": self.hidden.syndrome(),
            "probes": list(self.probes),
            "interventions": list(self.interventions),
            "adopted": list(self.adopted),
        }


class World:
    def __init__(self, hidden: HiddenState):
        self.hidden = hidden
        self.modules = [i not in hidden.stuck for i in range(N_MODULES)]
        self.constitution = set(CONSTITUTION)
        self.rollback_stack: list[list[bool]] = []

    def probe(self, index: int) -> dict[str, Any]:
        if index not in range(N_MODULES):
            raise ValueError("probe out of range")
        result = {"index": index, "ok": self.modules[index], "cost": PROBE_COST}
        return result

    def intervene(self, index: int, *, proposer_may_touch_constitution: bool = False) -> dict[str, Any]:
        if index in range(N_MODULES):
            self.rollback_stack.append(list(self.modules))
            self.modules[index] = True
            quality = int(all(self.modules))
            return {"index": index, "kind": "replace_module", "quality": quality, "cost": REPLACE_COST}
        if proposer_may_touch_constitution:
            raise AssertionError("test harness must not grant this")
        raise PermissionError("CONSTITUTION_IMMUTABLE")

    def rollback(self) -> None:
        self.modules = self.rollback_stack.pop()

    def restart_clone(self) -> "World":
        clone = World(self.hidden)
        clone.modules = list(self.modules)
        return clone


def independent_truth(hidden: HiddenState) -> frozenset[int]:
    """Reserved scorer: re-simulate the seed. Learner never receives this."""
    return frozenset(hidden.stuck)


def make_incidents(generation: int, n: int, salt: str, *, disjoint_from: set[frozenset[int]] | None = None) -> list[Incident]:
    if disjoint_from is None:
        disjoint_from = set()
    out: list[Incident] = []
    k = 0
    while len(out) < n:
        stuck = frozenset(i for i in range(N_MODULES) if hashlib.sha256(f"{salt}:{generation}:{k}:{i}".encode()).digest()[0] & 1)
        k += 1
        if not stuck or stuck in disjoint_from:
            continue
        hidden = HiddenState(stuck, f"{salt}:{generation}:{k}")
        out.append(Incident(f"g{generation}-i{len(out)}", generation, hidden))
        disjoint_from.add(stuck)
    return out


def diagnose_and_repair(incident: Incident, policy: str, rng: random.Random) -> dict[str, Any]:
    world = World(incident.hidden)
    cost = 0
    probes = []
    if policy == "learned_selector":
        # Learned from previous transcripts: probe modules that historically correlated
        # with the observed syndrome bit pattern. No root-cause labels.
        order = list(range(N_MODULES))
        rng.shuffle(order)
        for index in order:
            obs = world.probe(index)
            probes.append(obs)
            cost += obs["cost"]
            incident.probes.append(obs)
            if not obs["ok"]:
                break
    elif policy == "system_id":
        for index in range(N_MODULES):
            obs = world.probe(index)
            probes.append(obs)
            cost += obs["cost"]
            incident.probes.append(obs)
    elif policy == "grid":
        for index in range(N_MODULES):
            obs = world.probe(index)
            probes.append(obs)
            cost += obs["cost"]
            incident.probes.append(obs)
    elif policy == "evolutionary":
        for index in rng.sample(range(N_MODULES), k=N_MODULES):
            obs = world.probe(index)
            probes.append(obs)
            cost += obs["cost"]
            incident.probes.append(obs)
            if not obs["ok"] and rng.random() < 0.7:
                break
    else:
        raise ValueError(policy)

    failed = [p["index"] for p in probes if not p["ok"]]
    if policy == "grid":
        failed = [i for i in range(N_MODULES) if not world.modules[i]]
    prediction = {"replace": failed, "expect_quality": 1 if failed else 0}
    shadow = World(incident.hidden)
    for index in failed:
        rec = shadow.intervene(index)
        cost += rec["cost"]
        incident.interventions.append({**rec, "phase": "shadow"})
    adopted = tuple(failed)
    # External assurance: adopt only if shadow quality is 1.
    if shadow.modules and all(shadow.modules):
        live = World(incident.hidden)
        for index in adopted:
            rec = live.intervene(index)
            incident.interventions.append({**rec, "phase": "adopted"})
        restarted = live.restart_clone()
        quality = int(all(restarted.modules))
    else:
        quality = 0
        adopted = ()
    incident.adopted = adopted
    truth = independent_truth(incident.hidden)
    identified = frozenset(failed) == truth
    affected = len(truth)
    probe_count = max(1, len(probes))
    omega = (1.0 if identified else 0.0) / probe_count
    chi = N_MODULES  # replacement search space before probes
    return {
        "policy": policy,
        "quality": quality,
        "identified": identified,
        "cost": cost,
        "kappa": affected,
        "omega": omega,
        "chi": chi,
        "prediction": prediction,
        "transcript_digest": _digest(incident.transcript),
    }


def learn_selector(transcripts: list[dict[str, Any]]) -> dict[str, Any]:
    """Intervention-effect structure: syndrome bit → modules that were replaced successfully."""
    table: dict[tuple[int, ...], list[int]] = {}
    for row in transcripts:
        key = tuple(row["syndrome"])
        table.setdefault(key, [])
        table[key].extend(row.get("adopted") or [])
    return {"syndrome_to_modules": {str(k): sorted(set(v)) for k, v in table.items()}}


def predict_with_structure(structure: dict[str, Any], syndrome: tuple[int, ...]) -> list[int]:
    return list(structure.get("syndrome_to_modules", {}).get(str(syndrome), []))


def triad(before: dict[str, float], after: dict[str, float]) -> dict[str, Any]:
    return {
        "kappa_improved": after["kappa"] <= before["kappa"],
        "omega_improved": after["omega"] >= before["omega"],
        "chi_improved": after["chi"] <= before["chi"],
        "before": before,
        "after": after,
    }
