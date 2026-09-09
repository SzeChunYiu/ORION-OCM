"""GS-R0 wide sampling bound (GRAND SEARCH #221 sec 18) — GS_BOUND_V1.

The amend-1..4 arms search inside CENSUS_BOUND_V1 (56160 genomes, frozen).
The Grand Search samples the FULL schema vocabulary (#221 sec 3): every
F_arch knowledge-space family, heterogeneous unit compositions up to 5
extra units from all 12 cognitive unit types, every topology / executive /
learning / revision / memory family.  O_basis is not a free field — it is
derived from (units, L, K, R) by operators_for() exactly as in the census
genome builder, so "sampling over O_basis operators" means sampling the
unit/L/K/R combinations that enable each operator subset.

Size: |F_arch|=10, extras C(12,0..5)=1+12+66+220+495+792=1586,
|T|=8, |Pi|=7, |L|=9, |R|=3, |K|=6  =>
10 * 1586 * 8 * 7 * 9 * 3 * 6 = 143,881,920 candidate genomes before the
compile-time legality filter (same filter the census enumeration applies).

Every sampler here is seeded-RNG deterministic and REPRODUCES the exact
genome-construction discipline of morphology/direct_genome._make (so gate
behaviour, digests and cost model are identical to the frozen stack).
"""
from __future__ import annotations

import random
from itertools import combinations
from typing import Dict, Iterator, List, Sequence, Tuple

from morphology.compile import compile_genome, InvariantViolation
from morphology.direct_genome import _make
from morphology.schema import (EXECUTIVE_FAMILIES, FIELD_FAMILIES,
                               LEARNING_FAMILIES, MEMORY_FAMILIES,
                               OPERATORS, REVISION_FAMILIES,
                               TOPOLOGY_FAMILIES, UNIT_TYPES)

GS_BOUND_V1: Dict[str, object] = {
    "bound_id": "GS_BOUND_V1",
    "F_arch": tuple(sorted(FIELD_FAMILIES)),
    "extra_units": tuple(sorted(t for t in UNIT_TYPES if t != "fact_relation")),
    "max_extra_units": 5,
    "T_family": tuple(sorted(TOPOLOGY_FAMILIES)),
    "Pi_arch": tuple(sorted(EXECUTIVE_FAMILIES)),
    "L": tuple(sorted(LEARNING_FAMILIES)),
    "R": tuple(sorted(REVISION_FAMILIES)),
    "K": tuple(sorted(MEMORY_FAMILIES)),
}


def gs_bound_closed_form_size() -> int:
    n_extra = sum(1 for n in range(0, GS_BOUND_V1["max_extra_units"] + 1)
                  for _ in combinations(range(len(GS_BOUND_V1["extra_units"])), n))
    parts = (len(GS_BOUND_V1["F_arch"]) * n_extra * len(GS_BOUND_V1["T_family"])
             * len(GS_BOUND_V1["Pi_arch"]) * len(GS_BOUND_V1["L"])
             * len(GS_BOUND_V1["R"]) * len(GS_BOUND_V1["K"]))
    return parts


def gs_uniform_sample(rng: random.Random):
    """Uniform-ish draw over the full GS bound (same construction as
    direct_genome.random_genome but over the wide vocabulary)."""
    b = GS_BOUND_V1
    n = rng.randint(0, b["max_extra_units"])
    extras = sorted(rng.sample(list(b["extra_units"]), n))
    return _make(rng.choice(list(b["F_arch"])), extras,
                 rng.choice(list(b["T_family"])), rng.choice(list(b["Pi_arch"])),
                 rng.choice(list(b["L"])), rng.choice(list(b["R"])),
                 rng.choice(list(b["K"])))


# ------------------------------------------------------------------ lanes
# Four stratified sampling lanes (#221 sec 18: basic units / heterogeneous
# compositions / F_arch families / O_basis operators).  A lane sampler is a
# deterministic function of rng; every draw is evaluated and charged like any
# other candidate (no lane skips evaluations).

def lane_units(rng: random.Random):
    """Basic-units lane: extras in {0, 1} — minimal / single-unit bodies."""
    n = rng.randint(0, 1)
    extras = sorted(rng.sample(list(GS_BOUND_V1["extra_units"]), n))
    return _make(rng.choice(list(GS_BOUND_V1["F_arch"])), extras,
                 rng.choice(list(GS_BOUND_V1["T_family"])),
                 rng.choice(list(GS_BOUND_V1["Pi_arch"])),
                 rng.choice(list(GS_BOUND_V1["L"])), rng.choice(list(GS_BOUND_V1["R"])),
                 rng.choice(list(GS_BOUND_V1["K"])))


def lane_hetero(rng: random.Random):
    """Heterogeneous-composition lane: 2..5 extra units from all 12 types."""
    n = rng.randint(2, GS_BOUND_V1["max_extra_units"])
    extras = sorted(rng.sample(list(GS_BOUND_V1["extra_units"]), n))
    return _make(rng.choice(list(GS_BOUND_V1["F_arch"])), extras,
                 rng.choice(list(GS_BOUND_V1["T_family"])),
                 rng.choice(list(GS_BOUND_V1["Pi_arch"])),
                 rng.choice(list(GS_BOUND_V1["L"])), rng.choice(list(GS_BOUND_V1["R"])),
                 rng.choice(list(GS_BOUND_V1["K"])))


class _FarchRoundRobin:
    """F_arch-stratified lane: cycles deterministically through all 10
    knowledge-space families so every family receives an equal sampling
    quota regardless of rng draws (rng still decides the other fields)."""

    def __init__(self) -> None:
        self.i = 0

    def __call__(self, rng: random.Random):
        fams = list(GS_BOUND_V1["F_arch"])
        F = fams[self.i % len(fams)]
        self.i += 1
        b = GS_BOUND_V1
        n = rng.randint(0, b["max_extra_units"])
        extras = sorted(rng.sample(list(b["extra_units"]), n))
        return _make(F, extras, rng.choice(list(b["T_family"])),
                     rng.choice(list(b["Pi_arch"])), rng.choice(list(b["L"])),
                     rng.choice(list(b["R"])), rng.choice(list(b["K"])))


class _ObasisRoundRobin:
    """O_basis lane: cycles through the 12 operators; each draw is rejected
    and re-drawn (max 24 tries) until the derived O_basis ENABLES the target
    operator, so each operator's enabling region receives a sampling quota.
    Fallback after 24 misses: plain uniform draw (charged like any draw)."""

    def __init__(self) -> None:
        self.i = 0

    def __call__(self, rng: random.Random):
        target = OPERATORS[self.i % len(OPERATORS)]
        self.i += 1
        for _ in range(24):
            g = gs_uniform_sample(rng)
            if target in g.O_basis:
                return g
        return g


LANES: Dict[str, object] = {
    "units": lane_units,
    "hetero": lane_hetero,
    "farch": _FarchRoundRobin,
    "obasis": _ObasisRoundRobin,
}


def lane_sampler(lane: str, rng: random.Random):
    obj = LANES[lane]
    return obj() if isinstance(obj, type) else obj


def weighted_sampler(lane_weights: Dict[str, float], rng: random.Random):
    """GS-R1h adaptive-allocation sampler: pick a lane per draw with the
    given weights (missing lanes weight 0), then draw from that lane.
    Allocation-only adaptation — the lanes themselves are frozen."""
    lanes = sorted(lane_weights)
    w = [max(0.0, float(lane_weights[k])) for k in lanes]
    sams = {k: lane_sampler(k, rng) for k in lanes}
    total = sum(w) or 1.0

    def _draw(r: random.Random):
        x = r.random() * total
        acc = 0.0
        lane = lanes[-1]
        for k, wk in zip(lanes, w):
            acc += wk
            if x <= acc:
                lane = k
                break
        return sams[lane](r)

    return _draw


# ------------------------------------------------------------- enumeration
def enumerate_gs_bound(shard: Tuple[int, int] = (0, 1)) -> Iterator:
    """Deterministic enumeration of every candidate genome in GS_BOUND_V1,
    compile-legality filtered exactly like enumerate_census.  shard=(i, n)
    yields only genomes whose flat index satisfies idx % n == i (same
    discipline as census_p00 --chunk), so an n-way array covers the bound
    exactly once with no overlap."""
    b = GS_BOUND_V1
    i, n = shard
    extras_pool: Sequence[str] = list(b["extra_units"])
    idx = -1
    for F in b["F_arch"]:
        for k in range(0, b["max_extra_units"] + 1):
            for extras in combinations(extras_pool, k):
                for T in b["T_family"]:
                    for Pi in b["Pi_arch"]:
                        for L in b["L"]:
                            for R in b["R"]:
                                for K in b["K"]:
                                    idx += 1
                                    if idx % n != i:
                                        continue
                                    g = _make(F, extras, T, Pi, L, R, K)
                                    try:
                                        compile_genome(g)
                                    except InvariantViolation:
                                        continue
                                    yield g


def grammar_signature(g) -> str:
    """Stable signature of the grammar tuple (everything except theta /
    unit ids) — the key used by the failure-memory nogood ledger."""
    extras = tuple(sorted(u.unit_type for u in g.U if u.unit_type != "fact_relation"))
    return "|".join((g.F_arch, ",".join(extras), g.T_family, g.Pi_arch,
                     g.L, g.R, g.K))
