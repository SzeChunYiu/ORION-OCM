"""Inheritance arms. Genome always copies with mutation; memory policy varies."""
from __future__ import annotations

import random

from physics import OP_HARVEST, OP_HALT, OP_MOVE, OP_MSG_RECV, OP_MSG_SEND
from physics import OP_NOP, OP_REPLICATE, OP_SENSE, OP_STORE
from vm import clip_genome


ARMS = (
    "DARWINIAN",
    "BALDWINIAN",
    "LAMARCKIAN",
    "C_VERIFIED",
    "CULTURAL_HORIZONTAL",
)


def mutate(genome, rng, genome_max, p=0.12):
    g = list(genome)
    if rng.random() < p and g:
        i = rng.randrange(len(g))
        g[i] = rng.randrange(16)
    if rng.random() < p * 0.5 and len(g) < genome_max:
        g.insert(rng.randrange(len(g) + 1), rng.randrange(16))
    if rng.random() < p * 0.5 and len(g) > 3:
        del g[rng.randrange(len(g))]
    return clip_genome(g, genome_max)


def inherit_memory(arm, parent, offspring, rng):
    """Memory copy policy. Never copies assay scores (cells have none)."""
    slots = len(offspring.mem)
    if arm == "LAMARCKIAN":
        offspring.mem = list(parent.mem)[:slots]
        while len(offspring.mem) < slots:
            offspring.mem.append(0)
    elif arm == "C_VERIFIED":
        # Only slots written after a successful harvest this life (acc>0 crude).
        if parent.acc > 0:
            offspring.mem = list(parent.mem)[:slots]
        else:
            offspring.mem = [0] * slots
    else:
        offspring.mem = [0] * slots
    offspring.acc = 0
    offspring.pc = 0


def cultural_transfer(world):
    """Horizontal: a received message may overwrite one mem slot. Not energy."""
    if world.inherit_arm != "CULTURAL_HORIZONTAL":
        return
    for cell in world.alive():
        if not cell.msgs_inbox:
            continue
        msg = cell.msgs_inbox[-1]
        payload = int(msg.get("payload", 0)) & 255
        slot = payload % len(cell.mem)
        cell.mem[slot] = payload
        # Explicitly: messages never add energy.
        cell.energy = cell.energy  # no-op document


# Founder palettes labeled by CognitiveUnitContractV1 types (issue 221).
# These are genomes, not warrants. Approximate units never mint C.

def founder_genome(kind, rng, genome_max=32):
    kind = str(kind)
    if kind == "reactive":
        # fsm_controller: sense, harvest, move, repeat
        g = [OP_SENSE, OP_HARVEST, OP_MOVE, OP_SENSE, OP_HARVEST, OP_MOVE]
    elif kind == "memory":
        # episodic_memory + fact_relation: store sense, recall, harvest
        g = [OP_SENSE, OP_STORE, OP_HARVEST, OP_RECALL, OP_MOVE, OP_SENSE, OP_HARVEST]
    elif kind == "rule":
        # production_rule
        g = [OP_SENSE, OP_CMP, OP_JZ, OP_HARVEST, OP_MOVE, OP_REPLICATE, OP_NOP]
    elif kind == "communicator":
        g = [OP_SENSE, OP_HARVEST, OP_MSG_SEND, OP_MSG_RECV, OP_MOVE, OP_STORE]
    elif kind == "planner":
        # search_planner-ish: sense, compare, conditional harvest/move
        g = [OP_SENSE, OP_CMP, OP_JZ, OP_MOVE, OP_SENSE, OP_HARVEST, OP_REPLICATE]
    elif kind == "mixed":
        g = [OP_SENSE, OP_HARVEST, OP_STORE, OP_MSG_SEND, OP_MOVE, OP_REPLICATE,
             OP_SENSE, OP_HARVEST, OP_MSG_RECV]
    else:
        g = [OP_SENSE, OP_HARVEST, OP_MOVE]
    while len(g) < 8:
        g.append(OP_NOP)
    return clip_genome(g, genome_max)


FOUNDER_TO_CONTRACT = {
    "reactive": "fsm_controller",
    "memory": "episodic_memory",
    "rule": "production_rule",
    "communicator": "local_executive",
    "planner": "search_planner",
    "mixed": "heterogeneous_founder_palette",
}
