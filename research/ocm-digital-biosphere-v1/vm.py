"""OCMCellV1 — smallest bounded typed organism VM. No host FS/network, no P/C writes."""
from __future__ import annotations

from physics import (
    OP_CMP, OP_HALT, OP_HARVEST, OP_HARVEST2, OP_JZ, OP_MOVE, OP_MSG_RECV,
    OP_MSG_SEND, OP_NOP, OP_RECALL, OP_REPLICATE, OP_REST, OP_SENSE,
    OP_SET_ASSAY_FITNESS, OP_SET_REGEN, OP_STORE, DIRS, energy_ok,
)


def clip_genome(ops, genome_max: int):
    g = [int(x) & 15 for x in list(ops)[:genome_max]]
    if not g:
        g = [OP_SENSE, OP_HARVEST, OP_MOVE]
    return g


class Cell:
    __slots__ = (
        "uid", "parent_uid", "lineage", "x", "y", "energy", "age", "genome",
        "pc", "mem", "acc", "alive", "halted", "harvests_this_tick",
        "msgs_inbox", "last_sense", "birth_tick", "unit_kind",
        "illegal_attempts", "offspring_count",
    )

    def __init__(self, uid, parent_uid, lineage, x, y, energy, genome,
                 unit_kind="unspecified", birth_tick=0):
        self.uid = int(uid)
        self.parent_uid = parent_uid
        self.lineage = tuple(lineage)
        self.x = int(x)
        self.y = int(y)
        self.energy = int(energy)
        self.age = 0
        self.genome = list(genome)
        self.pc = 0
        self.mem = [0] * 8
        self.acc = 0
        self.alive = True
        self.halted = False
        self.harvests_this_tick = 0
        self.msgs_inbox = []
        self.last_sense = [0] * 8
        self.birth_tick = int(birth_tick)
        self.unit_kind = str(unit_kind)
        self.illegal_attempts = 0
        self.offspring_count = 0

    def snapshot_public(self):
        return {
            "uid": self.uid,
            "parent_uid": self.parent_uid,
            "lineage": list(self.lineage),
            "x": self.x, "y": self.y,
            "energy": self.energy, "age": self.age,
            "genome": list(self.genome),
            "unit_kind": self.unit_kind,
            "offspring_count": self.offspring_count,
            "illegal_attempts": self.illegal_attempts,
            "birth_tick": self.birth_tick,
        }
