#!/usr/bin/env python3
"""Development-only audit required by PROTECTED_PROTOCOL_V2.md.  Never runs protected seeds."""
from pathlib import Path

from factor_core_v2 import Episode, World, episodes
from factor_arms_v2 import FactorLocal, SymbolicCompact, SymbolicMemory
from factor_run_v2 import run_seed

assert tuple(Episode.__dataclass_fields__) == ("x", "correct_actions")
world = World.make(1, "sparse_stable")
g1 = episodes(world, 1, "sparse_stable", 1, "train", 96)
g2 = episodes(world, 1, "sparse_stable", 2, "train", 96)
factor, compact, memory = FactorLocal(), SymbolicCompact(), SymbolicMemory()
for arm in (factor, compact, memory):
    arm.update(g1, 1)
for arm in (factor, compact, memory):
    arm.update(g2, 2)
assert compact.models == factor.models == memory.models
assert not hasattr(compact, "history")
assert len(memory.history) == 192 and memory.history[:96] == g1 and memory.history[96:] == g2
assert factor.relevance and compact.relevance == set() and memory.relevance == set()

result = run_seed(1, "sparse_stable")
last = result["generations"][-1]["arms"]
assert last["factor_local"]["heldout_accuracy"] == 1.0
assert last["factor_local"]["support_f1"] == 1.0
assert last["symbolic_compact_parent"]["heldout_accuracy"] == 1.0
assert last["symbolic_compact_parent"]["state_bytes"] < last["factor_local"]["state_bytes"]
assert last["symbolic_incremental_memory_parent"]["state_bytes"] > last["symbolic_compact_parent"]["state_bytes"]

source = Path(__file__).with_name("factor_run_v2.py").read_text()
assert 'default="1,2,3,4,5,6,7,8"' in source
for seed in range(9101, 9141):
    assert str(seed) not in source
print("V2_DEV_IMPLEMENTATION_AUDIT_PASS")
