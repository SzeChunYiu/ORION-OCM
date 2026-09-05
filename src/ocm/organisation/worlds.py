"""Synthetic multiscale worlds with an oracle (M8 §11): known latent organisation, so topology
recovery and navigation regret are exact.  Families: clean hierarchy, overlapping communities,
misleading hierarchy (labels contradict the latent structure), dynamic topology (a later split),
cross-domain bridges, revocation events.  Frozen seed; the generator never encodes field/subject
labels into the oracle (M8 §15 hostile) — labels are separate, possibly misleading, metadata.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile


@dataclass(frozen=True)
class OracleWorld:
    world_id: str
    family: str
    ks: KnowledgeSpace
    latent_regions: tuple[frozenset[str], ...]      # ground-truth organisation (may overlap)
    bridges: tuple[tuple[str, str], ...]            # cross-region edges (edge ids)
    labels: dict[str, str]                          # atom → declared label (may be misleading)
    tasks: tuple[tuple[str, str], ...]              # (seed atom, target atom) queries with known answers
    revocations: tuple[frozenset, ...]              # revocation events to replay
    split_event: tuple[str, tuple[frozenset[str], frozenset[str]]] | None = None   # dynamic topology


def _ring_edges(ids: list[str], prefix: str, ev_base: int, rng: random.Random, density: float = 0.5) -> list[Hyperedge]:
    edges = []
    k = 0
    for i, a in enumerate(ids):
        b = ids[(i + 1) % len(ids)]
        edges.append(Hyperedge(f"{prefix}e{k}", (a,), (b,), "DEPENDENCE"))
        k += 1
    for i, a in enumerate(ids):
        for b in ids[i + 2:]:
            if rng.random() < density:
                edges.append(Hyperedge(f"{prefix}e{k}", (a,), (b,), "SUPPORT"))
                k += 1
    return edges


def generate(family: str, *, seed: str = "OCM-M8-WORLDS-20260905", regions: int = 4, size: int = 8) -> OracleWorld:
    rng = random.Random(seed)          # same structural draws for every family: families differ by construction, not by seed
    atoms: list[Atom] = []
    edges: list[Hyperedge] = []
    latent: list[frozenset[str]] = []
    labels: dict[str, str] = {}
    ev = 0
    for r in range(regions):
        ids = [f"r{r}a{i}" for i in range(size)]
        for a in ids:
            ev += 1
            atoms.append(Atom(a, "claim", WarrantProfile.of({f"ev{ev}"}), scope=Scope.of(f"ctx{r}")))
            # misleading: declared labels cut *across* the latent regions (by atom index), so a hand
            # hierarchy built from them groups unrelated atoms
            labels[a] = f"field{r}" if family != "misleading_hierarchy" else f"field{int(a.split('a')[1]) % regions}"
        edges += _ring_edges(ids, f"r{r}", ev, rng)
        latent.append(frozenset(ids))
    if family == "overlapping_communities":
        # one atom per adjacent pair belongs to both regions
        shared = []
        for r in range(regions - 1):
            a, b = f"r{r}a{size - 1}", f"r{r + 1}a0"
            edges.append(Hyperedge(f"ov{r}", (a,), (b,), "SUPPORT"))
            edges.append(Hyperedge(f"ov{r}b", (b,), (a,), "SUPPORT"))
            shared.append((a, b))
        latent = [frozenset(latent[r] | {f"r{r + 1}a0"}) if r < regions - 1 else latent[r] for r in range(regions)]
    bridges: list[tuple[str, str]] = []
    if family in ("cross_domain_bridges", "clean_hierarchy", "misleading_hierarchy", "dynamic_topology", "revocation_events"):
        nb = 2 if family == "cross_domain_bridges" else 1
        for r in range(regions - 1):
            for j in range(nb):
                eid = f"bridge{r}_{j}"
                edges.append(Hyperedge(eid, (f"r{r}a{j}",), (f"r{r + 1}a{j + 3}",), "DEPENDENCE"))
                bridges.append((f"r{r}a{j}", f"r{r + 1}a{j + 3}"))
    ks = KnowledgeSpace(tuple(atoms), tuple(edges))
    # tasks: within-region and cross-region targets
    tasks = []
    for r in range(regions):
        tasks.append((f"r{r}a0", f"r{r}a{size // 2}"))
        if r < regions - 1:
            tasks.append((f"r{r}a0", f"r{r + 1}a{size // 2}"))
    revocations: tuple[frozenset, ...] = ()
    if family == "revocation_events":
        revocations = (frozenset({"ev2"}), frozenset({"ev2", f"ev{size + 2}"}))
    split = None
    if family == "dynamic_topology":
        half = size // 2
        split = ("r0", (frozenset(f"r0a{i}" for i in range(half)), frozenset(f"r0a{i}" for i in range(half, size))))
    wid = hashlib.sha256(f"{seed}|{family}|{regions}|{size}".encode()).hexdigest()[:12]
    return OracleWorld(wid, family, ks, tuple(latent), tuple(bridges), labels, tuple(tasks), revocations, split)


FAMILIES = ("clean_hierarchy", "overlapping_communities", "misleading_hierarchy", "dynamic_topology", "cross_domain_bridges", "revocation_events")


def partition_recovery(latent: tuple[frozenset[str], ...], found: tuple[frozenset[str], ...]) -> dict[str, Any]:
    """Exact set-overlap recovery: for each latent region the best Jaccard over found regions."""
    scores = []
    for L in latent:
        best = max((len(L & F) / len(L | F) for F in found), default=0.0)
        scores.append(best)
    return {"mean_best_jaccard": round(sum(scores) / len(scores), 4) if scores else None, "exact_regions": sum(1 for s in scores if s == 1.0), "latent": len(latent), "found": len(found)}
