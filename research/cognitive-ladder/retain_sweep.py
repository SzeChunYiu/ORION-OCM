"""The E10 sweep: run every arm at every registered setting, and price sigma after.

Three grids, all registered in ``RETAIN_PLAN["sweep"]``:

``primary_grid``   extension size against bit budget -- the compressibility axis
                   and the scarcity axis, which is where the hypothesis lives
``horizon_slice``  extension size against horizon -- tests P3, that m* falls as
                   there is more demand to amortize induction over
``skew_slice``     extension size against demand skew -- uniform demand is the
                   hardest setting for every cache and is included so that a
                   crossover cannot be an artifact of a convenient skew

Each cell runs ``reps`` independent streams drawn from ``protected_seed``.  The
pilot stream used before the plan was frozen is drawn from ``pilot_seed`` and is
disjoint by construction, so pilot data cannot be relabelled as confirmatory.
"""

from __future__ import annotations

import random
import statistics
from typing import Any, Mapping, Sequence

from retain import COMMITMENT, RETAIN_PLAN, build_world, demand_stream
from retain_arms import ARM_ROLES, ARMS, Ledger, run_arm

__all__ = ["cell", "primary", "horizon_slice", "skew_slice", "pilot", "crossover"]

SWEEP: Mapping[str, Any] = RETAIN_PLAN["sweep"]
SIGMAS: Sequence[float] = tuple(SWEEP["sigmas"])


def _seed_for(tag: str, rep: int) -> int:
    return int(COMMITMENT.protected_seed[:12], 16) ^ (hash_str(tag) + rep * 7919)


def hash_str(text: str) -> int:
    """Deterministic across processes, unlike ``hash``, which is salted."""
    acc = 0
    for ch in text:
        acc = (acc * 131 + ord(ch)) & 0xFFFFFFFF
    return acc


def cell(extension: int, budget_bits: int, horizon: int, skew: float,
         reps: int, seed_base: int, tag: str) -> dict:
    """One grid point: every arm, ``reps`` streams, means per coordinate."""
    world = build_world(SWEEP["rule_count"], extension)
    per_arm: dict[str, list[Ledger]] = {a: [] for a in ARMS}
    for rep in range(reps):
        seed = seed_base ^ (hash_str(tag) + rep * 7919)
        stream = demand_stream(world, horizon, skew, random.Random(seed))
        for arm_id in ARMS:
            per_arm[arm_id].append(run_arm(arm_id, world, stream, budget_bits, seed))
    out = {
        "extension": extension, "budget_bits": budget_bits, "horizon": horizon,
        "skew": skew, "reps": reps, "answers": world.answers, "arms": {},
    }
    for arm_id, leds in per_arm.items():
        out["arms"][arm_id] = {
            "role": ARM_ROLES[arm_id],
            "correctness": min(l.correctness() for l in leds),
            "derivations": statistics.mean(l.derivations for l in leds),
            "inductions": statistics.mean(l.inductions for l in leds),
            "applications": statistics.mean(l.applications for l in leds),
            "hits": statistics.mean(l.hits for l in leds),
            "derive_work": statistics.mean(l.derive_work for l in leds),
            "apply_work": statistics.mean(l.apply_work for l in leds),
            "lookup_work": statistics.mean(l.lookup_work for l in leds),
            "induce_work": statistics.mean(l.induce_work for l in leds),
            "bit_steps": statistics.mean(l.bit_steps for l in leds),
            "peak_bits": max(l.peak_bits for l in leds),
            "total_work_by_sigma": {
                str(s): statistics.mean(l.total_work(s) for l in leds) for s in SIGMAS
            },
        }
    arm = out["arms"]["generalizing_arm"]["total_work_by_sigma"]
    out["ratio_to_belady_instance_by_sigma"] = {
        s: (arm[s] / out["arms"]["belady_instance_cache"]["total_work_by_sigma"][s]
            if out["arms"]["belady_instance_cache"]["total_work_by_sigma"][s] else float("inf"))
        for s in arm
    }
    out["ratio_to_belady_mixed_by_sigma"] = {
        s: (arm[s] / out["arms"]["belady_mixed_reference"]["total_work_by_sigma"][s]
            if out["arms"]["belady_mixed_reference"]["total_work_by_sigma"][s] else float("inf"))
        for s in arm
    }
    out["delta_purified_by_sigma"] = {
        s: out["arms"]["random_retention_placebo"]["total_work_by_sigma"][s] - arm[s]
        for s in arm
    }
    return out


def _base(protected: bool) -> int:
    digest = COMMITMENT.protected_seed if protected else COMMITMENT.pilot_seed
    return int(digest[:12], 16)


def primary(protected: bool = True, reps: int | None = None) -> list[dict]:
    g = SWEEP["primary_grid"]
    reps = SWEEP["reps"] if reps is None else reps
    return [cell(m, b, g["horizon"], g["skew"], reps, _base(protected), f"primary-{m}-{b}")
            for m in g["extension_sizes"] for b in g["budget_bits"]]


def horizon_slice(protected: bool = True, reps: int | None = None) -> list[dict]:
    g = SWEEP["horizon_slice"]
    reps = SWEEP["reps"] if reps is None else reps
    return [cell(m, g["budget_bits"], h, g["skew"], reps, _base(protected), f"horizon-{m}-{h}")
            for m in g["extension_sizes"] for h in g["horizons"]]


def skew_slice(protected: bool = True, reps: int | None = None) -> list[dict]:
    g = SWEEP["skew_slice"]
    reps = SWEEP["reps"] if reps is None else reps
    return [cell(m, g["budget_bits"], g["horizon"], k, reps, _base(protected), f"skew-{m}-{k}")
            for m in g["extension_sizes"] for k in g["skews"]]


def pilot() -> list[dict]:
    """The single-replicate scan run before the plan was frozen, on pilot_seed."""
    g = SWEEP["primary_grid"]
    return [cell(m, b, g["horizon"], g["skew"], 1, _base(False), f"pilot-{m}-{b}")
            for m in g["extension_sizes"] for b in g["budget_bits"]]


def crossover(rows: Sequence[dict], sigma: float, budget_bits: int | None = None,
              horizon: int | None = None) -> int | None:
    """Smallest extension size at which the arm beats the clairvoyant instance parent.

    Returns ``None`` when the arm never beats it, which is the kill criterion
    firing rather than a missing value, and callers must say so.
    """
    key = str(sigma)
    best: int | None = None
    for row in rows:
        if budget_bits is not None and row["budget_bits"] != budget_bits:
            continue
        if horizon is not None and row["horizon"] != horizon:
            continue
        if row["ratio_to_belady_instance_by_sigma"][key] < 1.0:
            best = row["extension"] if best is None else min(best, row["extension"])
    return best
