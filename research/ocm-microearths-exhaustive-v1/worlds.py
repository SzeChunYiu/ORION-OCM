"""Exhaustive micro-Earth world enumeration (issue #296 sec.16).

The frozen contract's micro_earth.MicroEarth pins one initial condition
(g = i % 4, energy 4, method 0). Exhaustiveness is the residual: every
initial genome/method assignment crossed with every social-transfer policy,
every hostile switch and every kernel ablation.

Two enumeration modes:
  FULL     -- ordered initial assignments, |cells|^n
  MULTISET -- unordered, quotient by population permutation

MULTISET is only legitimate if the trajectory observable is permutation
invariant. That is an empirical claim about the frozen dynamics, so it is a
test (permutation_invariance_probe), not an assumption.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import os
from typing import Iterable, Iterator, NamedTuple

ALLELES = (0, 1, 2, 3)
# 0 = no method, 1 = useful_method, 9 = junk_method (micro_earth defaults)
METHODS = (0, 1, 9)
SOCIAL = ("optional", "forced", "prestige")
LEAK = (False, True)
REGIME = (0, 1)

# Eight kernels from the frozen contract plus the inherit_memory sub-switch
# that gates the body of K_inherit.
KERNEL_NAMES = (
    "K_world", "K_senseact", "K_learn", "K_social",
    "K_assemble", "K_birthdeath", "K_mut", "K_inherit",
)
KERNEL_BITS = len(KERNEL_NAMES) + 1  # + inherit_memory
N_KERNEL_SPECS = 1 << KERNEL_BITS    # 512

DEFAULT_TICKS = 6


def load_micro_earth(contract_dir: str):
    """Import the frozen micro_earth module by path, without polluting sys.path."""
    path = os.path.join(contract_dir, "micro_earth.py")
    spec = importlib.util.spec_from_file_location("frozen_micro_earth", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load frozen micro_earth from %s" % path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class WorldSpec(NamedTuple):
    n: int
    genomes: tuple
    methods: tuple
    social: str
    leak: bool
    regime: int
    kernel_id: int
    seed: int = 0

    def kernels(self) -> dict:
        return kernel_spec(self.kernel_id)

    def key(self) -> str:
        return "n%d|g%s|m%s|%s|L%d|R%d|k%03d|s%d" % (
            self.n, "".join(map(str, self.genomes)),
            "".join(map(str, self.methods)), self.social,
            int(self.leak), self.regime, self.kernel_id, self.seed)


def kernel_spec(kernel_id: int) -> dict:
    """Decode a kernel id into the ablation map micro_earth._on() reads."""
    out = {}
    for i, name in enumerate(KERNEL_NAMES):
        out[name] = bool((kernel_id >> i) & 1)
    out["inherit_memory"] = bool((kernel_id >> len(KERNEL_NAMES)) & 1)
    return out


ALL_ON = (1 << len(KERNEL_NAMES)) - 1          # every kernel on, inherit_memory off
ALL_ON_INHERIT = ALL_ON | (1 << len(KERNEL_NAMES))


def build(me_mod, spec: WorldSpec):
    """Instantiate a frozen MicroEarth at an arbitrary initial condition."""
    e = me_mod.MicroEarth(spec.n, seed=spec.seed, leak=spec.leak,
                          social=spec.social, kernels=spec.kernels(),
                          regime=spec.regime)
    for cell, g, m in zip(e.cells, spec.genomes, spec.methods):
        cell.g = int(g)
        cell.method = int(m)
    return e


def _tick_observable(e) -> tuple:
    """Permutation-invariant per-tick observable.

    Deliberately excludes uid, parent and group: uid/parent are index labels,
    and group is index-derived when K_assemble is ablated. Group is carried by
    the level analysis instead, where its observer status is the point.
    """
    live = sorted((c.g, c.method, c.energy, c.mem) for c in e.alive())
    return (e.tick, len(live), tuple(live), e.resource, len(e.library))


def trajectory(me_mod, spec: WorldSpec, ticks: int = DEFAULT_TICKS,
               assay: bool = True) -> list:
    """Mirror the frozen run_horizon: observer_assay() runs after every step.

    This matters. observer_assay() is what writes cell.assay, and under leak
    the harvest kernel reads cell.assay. Stepping without it silently disables
    the leak channel, which makes reproduction unreachable and every
    downstream kernel look dead.
    """
    e = build(me_mod, spec)
    out = [_tick_observable(e)]
    for _ in range(ticks):
        e.step()
        if assay:
            e.observer_assay()
        out.append(_tick_observable(e))
    return out


def signature(me_mod, spec: WorldSpec, ticks: int = DEFAULT_TICKS,
              assay: bool = True) -> str:
    payload = json.dumps(trajectory(me_mod, spec, ticks, assay),
                         separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


# ---------------------------------------------------------------- enumeration

def initial_assignments(n: int, mode: str = "FULL") -> Iterator[tuple]:
    """Yield (genomes, methods) initial conditions."""
    if mode == "FULL":
        for g in itertools.product(ALLELES, repeat=n):
            for m in itertools.product(METHODS, repeat=n):
                yield g, m
    elif mode == "MULTISET":
        cells = [(g, m) for g in ALLELES for m in METHODS]  # 12 cell kinds
        for combo in itertools.combinations_with_replacement(cells, n):
            yield tuple(c[0] for c in combo), tuple(c[1] for c in combo)
    else:
        raise ValueError("mode must be FULL or MULTISET")


def n_initial(n: int, mode: str = "FULL") -> int:
    k = len(ALLELES) * len(METHODS)  # 12
    if mode == "FULL":
        return k ** n
    return math.comb(k + n - 1, n)


def enumeration_size(n: int, mode: str = "FULL") -> int:
    return n_initial(n, mode) * len(SOCIAL) * len(LEAK) * len(REGIME) * N_KERNEL_SPECS


def bound_table(n_range: Iterable[int] = range(2, 9)) -> list:
    rows = []
    for n in n_range:
        rows.append({
            "n_org": n,
            "initial_full": n_initial(n, "FULL"),
            "initial_multiset": n_initial(n, "MULTISET"),
            "worlds_full": enumeration_size(n, "FULL"),
            "worlds_multiset": enumeration_size(n, "MULTISET"),
            "reduction_factor": round(
                n_initial(n, "FULL") / n_initial(n, "MULTISET"), 2),
        })
    return rows


def enumerate_worlds(n: int, mode: str = "MULTISET", seed: int = 0,
                     shard: tuple | None = None) -> Iterator[WorldSpec]:
    """Deterministic stride sharding: shard=(i, k) yields every k-th world."""
    idx = 0
    si, sk = shard if shard else (0, 1)
    for g, m in initial_assignments(n, mode):
        for social in SOCIAL:
            for leak in LEAK:
                for regime in REGIME:
                    for kid in range(N_KERNEL_SPECS):
                        if idx % sk == si:
                            yield WorldSpec(n, g, m, social, leak, regime,
                                            kid, seed)
                        idx += 1


def stride_sample(n: int, k: int, mode: str = "MULTISET", seed: int = 0) -> list:
    """k worlds spread evenly across the WHOLE enumeration.

    A prefix of enumerate_worlds is degenerate: it pins one initial condition
    and walks kernel_id upward, so it never reaches the all-kernels-on config.
    Any instrument fed a prefix reports dead kernels that are not dead.
    """
    total = enumeration_size(n, mode)
    if k >= total:
        return list(enumerate_worlds(n, mode=mode, seed=seed))
    step = total // k
    return list(enumerate_worlds(n, mode=mode, seed=seed, shard=(0, step)))[:k]


def initial_conditions(n: int, k: int, mode: str = "MULTISET") -> list:
    """k (genomes, methods, social, leak, regime) settings, kernels excluded."""
    combos = []
    for g, m in initial_assignments(n, mode):
        for social in SOCIAL:
            for leak in LEAK:
                for regime in REGIME:
                    combos.append((g, m, social, leak, regime))
    if k >= len(combos):
        return combos
    step = max(1, len(combos) // k)
    return combos[::step][:k]
