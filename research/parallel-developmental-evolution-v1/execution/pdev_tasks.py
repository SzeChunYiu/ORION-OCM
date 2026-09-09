"""PDEV task construction: fresh, parent-disjoint development task identities.

The #149 canonical lineage (pinned ``ladder_adapter.task``) consumed these
(domain, scale, instance) contracts before any PDEV task existed:

    s: (3,0) (3,1) (1,2) (3,3) (10,4) (30,5) (3,6) (20,11) (3,10)
    d: (1,0) (2,1) (1,1) (3,0)

PDEV tasks therefore draw ONLY from scales the parent never used (s: fresh
scales entirely; d: fresh scales -- the d instance axis is exhausted at {0,1}
by the donor's two registered revision schedules, so scale is the only fresh
axis).  Contract identity is sha256({"domain","scale","instance"}) exactly as
the parent computed it, so disjointness is checkable, not asserted.

The allocator is a deterministic frozen enumeration: consumers pop the next
task for a slot, and the global ledger of consumed identities is written to
disk so no generation can silently reuse a semantic id.

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

SCHEMA = "pdev217.task_pool.v1"

#: Everything the pinned parent adapter consumed (verified against
#: research/self-evolution-v1 pinned run machine history, vendor/pinned).
PARENT_CONSUMED: Tuple[Tuple[str, int, int], ...] = (
    ("s", 3, 0), ("s", 3, 1), ("s", 1, 2), ("s", 3, 3), ("s", 10, 4),
    ("s", 30, 5), ("s", 3, 6), ("s", 20, 11), ("s", 3, 10),
    ("d", 1, 0), ("d", 2, 1), ("d", 1, 1), ("d", 3, 0),
)

#: Frozen fresh pools (enumerated before any outcome was measured).
S_SCALES: Tuple[int, ...] = (2, 4, 5, 6, 7, 8, 9, 12, 15, 16, 18, 21, 24, 25, 27, 28)
D_SCALES: Tuple[int, ...] = tuple(range(4, 40))
#: s probe positions are 2003 + 2*instance for any instance >= 0 (parent used
#: 0..11); fresh instances start at 100.
S_INSTANCE_BASE = 100
D_INSTANCES: Tuple[int, ...] = (0, 1)

#: Deterministic enumeration order of the fresh pool.
POOL: Tuple[Tuple[str, int, int], ...] = tuple(
    [("s", scale, S_INSTANCE_BASE + i)
     for scale in S_SCALES for i in range(0, 12)]
    + [("d", scale, inst) for scale in D_SCALES for inst in D_INSTANCES]
)

for _c in POOL:
    assert _c not in PARENT_CONSUMED, "pool collides with parent contract"


def task(domain: str, scale: int, instance: int, phase: str) -> Dict[str, object]:
    """Same contract-identity rule as the pinned parent adapter."""
    contract = {"domain": domain, "scale": scale, "instance": instance}
    identity = hashlib.sha256(
        json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return {**contract, "task_id": phase + ":" + identity,
            "semantic_id": identity, "ecology": "development"}


def task_from_contract(contract: Mapping[str, object], phase: str) -> Dict[str, object]:
    return task(str(contract["domain"]), int(contract["scale"]),
                int(contract["instance"]), phase)


def semantic_id_of(domain: str, scale: int, instance: int) -> str:
    contract = {"domain": domain, "scale": scale, "instance": instance}
    return hashlib.sha256(
        json.dumps(contract, sort_keys=True).encode()).hexdigest()


class TaskLedger:
    """Persistent allocator over the frozen pool (file-locked by convention:
    only the centre writes it; workers receive already-allocated suites)."""

    def __init__(self, path: str):
        self.path = Path(path)
        if self.path.exists():
            payload = json.loads(self.path.read_text())
            if payload.get("schema") != SCHEMA:
                raise ValueError("unknown task ledger schema")
            self.consumed = [tuple(x) for x in payload["consumed"]]
        else:
            self.consumed = []
        for c in self.consumed:
            if c in PARENT_CONSUMED:
                raise ValueError("task ledger claims a parent-consumed contract")

    def _remaining(self) -> List[Tuple[str, int, int]]:
        used = set(self.consumed)
        return [c for c in POOL if c not in used]

    def count_remaining(self, domain: Optional[str] = None) -> int:
        return sum(1 for c in self._remaining()
                   if domain is None or c[0] == domain)

    def take(self, n: int, domain: Optional[str] = None, phase: str = "dev",
             label: str = "") -> List[Dict[str, object]]:
        remaining = [c for c in self._remaining()
                     if domain is None or c[0] == domain]
        if len(remaining) < n:
            raise ValueError("fresh task pool exhausted for %r (%d left)"
                             % (domain, len(remaining)))
        chosen = remaining[:n]
        self.consumed.extend(chosen)
        return [task(d, s, i, phase) for (d, s, i) in chosen]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(
            {"schema": SCHEMA,
             "parent_consumed": [list(c) for c in PARENT_CONSUMED],
             "pool_size": len(POOL),
             "consumed": [list(c) for c in self.consumed]}, sort_keys=True))
        os.replace(str(tmp), str(self.path))


#: Suite recipes (frozen): each generation cycle allocates fresh tasks per
#: recipe; the same suite object is reused within a generation for selection,
#: and never again in any later generation.
SUITE_RECIPES: Dict[str, Mapping[str, object]] = {
    "dev":        {"n": 6, "mix": "s4d2"},   # development experiences (cycle intake)
    "target":     {"n": 6, "mix": "s4d2"},   # shadow target suite (disjoint)
    "preservation": {"n": 6, "mix": "s4d2"},  # shadow preservation suite
    "harmful":    {"n": 4, "mix": "s4d0"},   # absent-family traps (s only)
    "fresh":      {"n": 6, "mix": "s4d2"},   # disjoint fresh-use suite
    "relabel":    {"n": 4, "mix": "s4d0"},   # memorization-hostile relabels
    "audit":      {"n": 4, "mix": "s3d1"},   # H2/H9 dynamic-audit suite
}
