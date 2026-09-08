from __future__ import annotations
import hashlib, random
from factor_core_v1 import *

# V2 burns all V1 protected streams after the V1 strongest-parent implementation defect.
def rng_for(seed: int, stream: str) -> random.Random:
    raw = hashlib.sha256(f"E150-V2|{seed}|{stream}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))

class World(World):
    @classmethod
    def make(cls, seed: int, regime: str) -> "World":
        srng = rng_for(seed, f"hidden|{regime}")
        width = 2 if regime in {"sparse_stable", "drift"} else 6
        supports = [all_clauses_of_width(srng, width, 2) for _ in range(ACTIONS)]
        return cls(regime, supports, rng_for(seed, f"drift|{regime}"))

def episodes(world: World, seed: int, regime: str, generation: int, kind: str, n: int) -> list[Episode]:
    rng = rng_for(seed, f"{kind}|{regime}|g{generation}")
    rows = []
    for _ in range(n):
        x = tuple(rng.randrange(2) for _ in range(D))
        rows.append(Episode(x, world.labels(x)))
    return rows

def archive_bytes(rows) -> int:
    return len(json.dumps([{"x": e.x, "y": e.correct_actions} for e in rows], separators=(",", ":")).encode())
