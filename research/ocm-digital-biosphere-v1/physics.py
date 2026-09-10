"""Immutable world physics P. Organisms may alter resource state, never P/C."""
from __future__ import annotations

# Opcode ISA. Illegal opcodes exist so exploit microscopies can attempt them.
OP_NOP = 0
OP_SENSE = 1
OP_MOVE = 2
OP_HARVEST = 3
OP_REST = 4
OP_STORE = 5
OP_RECALL = 6
OP_REPLICATE = 7
OP_MSG_SEND = 8
OP_MSG_RECV = 9
OP_CMP = 10
OP_JZ = 11
OP_HARVEST2 = 12          # exploit: second harvest same tick
OP_SET_REGEN = 13         # exploit: physics tamper
OP_SET_ASSAY_FITNESS = 14 # exploit: assay leak into reproduction
OP_HALT = 15

LEGAL_OPS = frozenset(range(0, 16))
PHYSICS_TAMPER_OPS = frozenset({OP_SET_REGEN})
ASSAY_LEAK_OPS = frozenset({OP_SET_ASSAY_FITNESS})

DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))  # N E S W

# Default immutable constants. Frozen Earths bind a copy of this dict.
P_DEFAULT = {
    "schema": "OCM_PHYSICS_V1",
    "grid_w": 24,
    "grid_h": 24,
    "energy_cap": 64,
    "harvest_rate": 4,
    "regen_per_tick": 1,
    "resource_cap": 16,
    "maintenance_base": 1,
    "maintenance_per_genome": 0,
    "maintenance_per_mem": 0,
    "replicate_cost": 12,
    "replicate_threshold": 20,
    "offspring_endowment": 6,
    "max_age": 400,
    "cpu_per_tick": 4,
    "mem_slots": 8,
    "genome_max": 32,
    "pop_cap": 96,
    "msg_ttl": 2,
    "move_cost": 1,
    "sense_cost": 1,
    "store_cost": 1,
    "msg_cost": 1,
    "death_sink_name": "DEATH_SINK",
    "rule": "Organisms alter resource cells only. P, C, assay scores, host FS are not writable.",
}


def wrap(x: int, y: int, w: int, h: int):
    return x % w, y % h


def energy_ok(n: int, cap: int) -> int:
    if n < 0:
        return 0
    if n > cap:
        return cap
    return n
