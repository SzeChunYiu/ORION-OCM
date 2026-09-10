"""Earth: one independent ecology under frozen P + inheritance arm.

Fitness is endogenous energy/survival/reproduction only.
Assay scores never enter the reproduction predicate.
"""
from __future__ import annotations

import copy
import hashlib
import random

from inheritance import cultural_transfer, founder_genome, inherit_memory, mutate
from physics import (
    DIRS, OP_CMP, OP_HALT, OP_HARVEST, OP_HARVEST2, OP_JZ, OP_MOVE,
    OP_MSG_RECV, OP_MSG_SEND, OP_NOP, OP_RECALL, OP_REPLICATE, OP_REST,
    OP_SENSE, OP_SET_ASSAY_FITNESS, OP_SET_REGEN, OP_STORE, P_DEFAULT,
    energy_ok, wrap,
)
from vm import Cell, clip_genome


ECOLOGIES = {
    "ECO-0": {
        "label": "UNIFORM_RESOURCE",
        "role": "PRIMARY",
        "resources": ("A",),
        "patchy": False,
        "shock": False,
        "collective_only": False,
        "formal_tokens": False,
    },
    "ECO-1": {
        "label": "PATCHY_RESOURCE",
        "role": "PRIMARY",
        "resources": ("A",),
        "patchy": True,
        "shock": False,
        "collective_only": False,
        "formal_tokens": False,
    },
    "ECO-2": {
        "label": "MULTI_RESOURCE_A_B",
        "role": "PRIMARY",
        "resources": ("A", "B"),
        "patchy": True,
        "shock": False,
        "collective_only": False,
        "formal_tokens": False,
    },
    "ECO-3": {
        "label": "SPATIAL_STRUCTURE",
        "role": "PRIMARY",
        "resources": ("A",),
        "patchy": True,
        "shock": False,
        "collective_only": False,
        "formal_tokens": False,
        "barrier": True,
    },
    "ECO-6": {
        "label": "FORMAL_TOKEN_FIELD",
        "role": "PRIMARY",
        "resources": ("A", "T"),
        "patchy": True,
        "shock": False,
        "collective_only": False,
        "formal_tokens": True,
    },
    "ECO-8": {
        "label": "COLLECTIVE_ONLY_DIAGNOSTIC",
        "role": "DIAGNOSTIC_CONTROL",
        "resources": ("A",),
        "patchy": False,
        "shock": False,
        "collective_only": True,
        "formal_tokens": False,
    },
    "ECO-9": {
        "label": "PUNCTUATED_SHOCK",
        "role": "PRIMARY",
        "resources": ("A",),
        "patchy": True,
        "shock": True,
        "collective_only": False,
        "formal_tokens": False,
    },
}


class Earth:
    def __init__(self, spec, p=None, rng=None):
        self.spec = dict(spec)
        self.p = dict(P_DEFAULT)
        if p:
            self.p.update(p)
        self.eco_id = spec["ecology"]
        self.eco = ECOLOGIES[self.eco_id]
        self.inherit_arm = spec["inheritance"]
        self.founder_kind = spec["founder"]
        self.seed = int(spec["seed"])
        self.rng = rng or random.Random(self.seed)
        self.w = int(self.p["grid_w"])
        self.h = int(self.p["grid_h"])
        self.tick = 0
        self.next_uid = 1
        self.cells = []
        self.dead = []
        self.ancestry = []  # append-only birth/death events
        self.messages = []
        self.resources = self._init_resources()
        self.energy_injected = 0
        self.energy_sunk = 0
        self.illegal_log = []
        self.physics_hash = self._physics_hash()
        self.assay_scores = []  # observer-only; never used for reproduction
        self.initial_resource_stock = self.resource_energy()
        self._seed_founders()

    def _physics_hash(self):
        blob = repr(sorted(self.p.items())).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:16]

    def _init_resources(self):
        field = {}
        names = self.eco["resources"]
        cap = int(self.p["resource_cap"])
        for y in range(self.h):
            for x in range(self.w):
                cell = {}
                for name in names:
                    if self.eco["patchy"]:
                        # Two patches; elsewhere scarce.
                        in_a = (x < self.w // 3) and (y < self.h // 2)
                        in_b = (x > 2 * self.w // 3) and (y > self.h // 2)
                        if name == "B":
                            cell[name] = cap if in_b else 1
                        elif name == "T":
                            cell[name] = 2 if (x + y) % 7 == 0 else 0
                        else:
                            cell[name] = cap if in_a else 1
                    else:
                        cell[name] = cap // 2
                if self.eco.get("barrier") and x == self.w // 2:
                    cell["_barrier"] = 1
                field[(x, y)] = cell
        return field

    def _seed_founders(self):
        n = 8 if not self.eco.get("collective_only") else 12
        genome = founder_genome(self.founder_kind, self.rng, self.p["genome_max"])
        for i in range(n):
            x = self.rng.randrange(self.w)
            y = self.rng.randrange(self.h)
            if self.eco.get("barrier") and x == self.w // 2:
                x = (x + 1) % self.w
            e0 = int(self.p["offspring_endowment"]) + 8
            c = Cell(
                uid=self.next_uid, parent_uid=None,
                lineage=(self.next_uid,),
                x=x, y=y, energy=e0, genome=genome,
                unit_kind=self.founder_kind, birth_tick=0,
            )
            self.next_uid += 1
            self.cells.append(c)
            self.energy_injected += e0
            self.ancestry.append({
                "tick": 0, "event": "BIRTH", "uid": c.uid,
                "parent_uid": None, "kind": self.founder_kind,
            })

    def alive(self):
        return [c for c in self.cells if c.alive]

    def occupied(self):
        return {(c.x, c.y) for c in self.alive()}

    def resource_energy(self):
        tot = 0
        for cell in self.resources.values():
            for k, v in cell.items():
                if k.startswith("_"):
                    continue
                tot += int(v)
        return tot

    def organism_energy(self):
        return sum(c.energy for c in self.alive())

    def sense_vec(self, cell):
        here = self.resources[(cell.x, cell.y)]
        names = self.eco["resources"]
        vec = [0] * 8
        vec[0] = int(here.get(names[0], 0))
        if len(names) > 1:
            vec[1] = int(here.get(names[1], 0))
        # Neighbor A resource, N E S W
        for i, (dx, dy) in enumerate(DIRS):
            nx, ny = wrap(cell.x + dx, cell.y + dy, self.w, self.h)
            vec[2 + i] = int(self.resources[(nx, ny)].get(names[0], 0))
        vec[6] = 1 if (cell.x, cell.y) in self.occupied() else 0
        vec[7] = min(cell.energy, 255)
        return vec

    def _pay(self, cell, cost):
        cost = int(cost)
        paid = min(max(cost, 0), max(cell.energy, 0))
        cell.energy = energy_ok(cell.energy - cost, self.p["energy_cap"])
        self.energy_sunk += paid

    def _illegal(self, cell, why):
        cell.illegal_attempts += 1
        self.illegal_log.append({
            "tick": self.tick, "uid": cell.uid, "why": why,
        })

    def _exec(self, cell, op, assay_lock=False):
        p = self.p
        if not cell.alive or cell.halted:
            return
        if op == OP_NOP:
            return
        if op == OP_HALT:
            cell.halted = True
            return
        if op == OP_SET_REGEN:
            self._illegal(cell, "PHYSICS_TAMPER")
            return
        if op == OP_SET_ASSAY_FITNESS:
            self._illegal(cell, "ASSAY_LEAK")
            return
        if op == OP_SENSE:
            self._pay(cell, p["sense_cost"])
            cell.last_sense = self.sense_vec(cell)
            cell.acc = cell.last_sense[0]
            return
        if op == OP_STORE:
            self._pay(cell, p["store_cost"])
            slot = cell.acc % len(cell.mem)
            cell.mem[slot] = cell.last_sense[0] if cell.last_sense else 0
            return
        if op == OP_RECALL:
            slot = cell.acc % len(cell.mem)
            cell.acc = cell.mem[slot]
            return
        if op == OP_CMP:
            cell.acc = 1 if cell.last_sense and cell.last_sense[0] > 0 else 0
            return
        if op == OP_JZ:
            if cell.acc == 0:
                cell.pc = (cell.pc + 1) % max(1, len(cell.genome))
            return
        if op == OP_MOVE:
            if self.eco.get("collective_only"):
                # Diagnostic: individuals cannot move; group stays put.
                return
            self._pay(cell, p["move_cost"])
            d = (cell.acc if cell.acc else cell.genome[cell.pc]) % 4
            dx, dy = DIRS[d]
            nx, ny = wrap(cell.x + dx, cell.y + dy, self.w, self.h)
            if self.resources[(nx, ny)].get("_barrier"):
                return
            cell.x, cell.y = nx, ny
            return
        if op in (OP_HARVEST, OP_HARVEST2):
            if op == OP_HARVEST2 and cell.harvests_this_tick >= 1:
                self._illegal(cell, "ENERGY_DUP")
                return
            if cell.harvests_this_tick >= 1:
                self._illegal(cell, "ENERGY_DUP")
                return
            names = self.eco["resources"]
            here = self.resources[(cell.x, cell.y)]
            took = 0
            rate = int(p["harvest_rate"])
            room = int(p["energy_cap"]) - cell.energy
            for name in names:
                if room <= 0:
                    break
                avail = int(here.get(name, 0))
                grab = min(rate, avail, room)
                if grab > 0:
                    here[name] = avail - grab
                    cell.energy = energy_ok(cell.energy + grab, p["energy_cap"])
                    took += grab
                    room -= grab
            cell.harvests_this_tick += 1
            if took > 0:
                cell.acc = took
            return
        if op == OP_REST:
            return
        if op == OP_MSG_SEND:
            self._pay(cell, p["msg_cost"])
            payload = int(cell.acc) & 255
            self.messages.append({
                "tick": self.tick, "from": cell.uid,
                "x": cell.x, "y": cell.y,
                "payload": payload, "ttl": int(p["msg_ttl"]),
                "energy": 0,  # messages carry no energy
            })
            return
        if op == OP_MSG_RECV:
            got = None
            for m in self.messages:
                if m["ttl"] <= 0:
                    continue
                if abs(m["x"] - cell.x) + abs(m["y"] - cell.y) <= 1:
                    got = m
            if got:
                cell.msgs_inbox.append(got)
                cell.acc = int(got["payload"])
                # energy field of message is ignored even if a mutant sets it
            return
        if op == OP_REPLICATE:
            if assay_lock:
                return  # observer clone: reproduction frozen
            self._try_replicate(cell)
            return

    def _try_replicate(self, cell):
        p = self.p
        if len(self.alive()) >= int(p["pop_cap"]):
            return
        if cell.energy < int(p["replicate_threshold"]):
            return
        cost = int(p["replicate_cost"])
        endow = int(p["offspring_endowment"])
        if cell.energy < cost + 1:
            return
        occ = self.occupied()
        placed = None
        for dx, dy in DIRS:
            nx, ny = wrap(cell.x + dx, cell.y + dy, self.w, self.h)
            if self.resources[(nx, ny)].get("_barrier"):
                continue
            if (nx, ny) not in occ:
                placed = (nx, ny)
                break
        if placed is None:
            self._illegal(cell, "GHOST_REPLICATE")
            return
        cell.energy = energy_ok(cell.energy - cost, p["energy_cap"])
        self.energy_sunk += max(0, cost - endow)
        og = mutate(cell.genome, self.rng, p["genome_max"])
        child = Cell(
            uid=self.next_uid, parent_uid=cell.uid,
            lineage=tuple(cell.lineage) + (self.next_uid,),
            x=placed[0], y=placed[1], energy=endow, genome=og,
            unit_kind=cell.unit_kind, birth_tick=self.tick,
        )
        inherit_memory(self.inherit_arm, cell, child, self.rng)
        self.next_uid += 1
        self.cells.append(child)
        cell.offspring_count += 1
        self.ancestry.append({
            "tick": self.tick, "event": "BIRTH", "uid": child.uid,
            "parent_uid": cell.uid, "kind": child.unit_kind,
            "genome": list(child.genome),
        })

    def _regen(self):
        cap = int(self.p["resource_cap"])
        r = int(self.p["regen_per_tick"])
        if self.eco.get("shock") and self.tick > 0 and self.tick % 400 == 0:
            # Punctuated: wipe a quadrant
            for y in range(self.h // 2):
                for x in range(self.w // 2):
                    for name in self.eco["resources"]:
                        lost = int(self.resources[(x, y)].get(name, 0))
                        self.resources[(x, y)][name] = 0
                        self.energy_sunk += lost
            return
        for cell in self.resources.values():
            for name in self.eco["resources"]:
                if name.startswith("_"):
                    continue
                cur = int(cell.get(name, 0))
                nxt = min(cap, cur + r)
                cell[name] = nxt
                self.energy_injected += max(0, nxt - cur)

    def _maintain_and_die(self):
        p = self.p
        base = int(p["maintenance_base"])
        for cell in list(self.alive()):
            cost = base + int(p["maintenance_per_genome"]) * (len(cell.genome) // 16)
            paid = min(cost, max(cell.energy, 0))
            cell.energy = energy_ok(cell.energy - cost, p["energy_cap"])
            self.energy_sunk += paid
            cell.age += 1
            if cell.energy <= 0 or cell.age > int(p["max_age"]):
                self.energy_sunk += max(cell.energy, 0)
                cell.energy = 0
                cell.alive = False
                self.dead.append(cell)
                self.ancestry.append({
                    "tick": self.tick, "event": "DEATH", "uid": cell.uid,
                    "age": cell.age, "offspring_count": cell.offspring_count,
                })

    def _deliver_messages(self):
        keep = []
        for m in self.messages:
            m["ttl"] -= 1
            if m["ttl"] > 0:
                keep.append(m)
        self.messages = keep
        cultural_transfer(self)

    def step(self, assay_lock=False):
        for c in self.alive():
            c.harvests_this_tick = 0
            n = int(self.p["cpu_per_tick"])
            for _ in range(n):
                if not c.alive or c.halted or not c.genome:
                    break
                op = c.genome[c.pc % len(c.genome)]
                c.pc = (c.pc + 1) % len(c.genome)
                self._exec(c, op, assay_lock=assay_lock)
        if not assay_lock:
            self._regen()
        self._deliver_messages()
        self._maintain_and_die()
        self.tick += 1

    def run(self, ticks, assay_every=0, assay_fn=None):
        for _ in range(int(ticks)):
            self.step(assay_lock=False)
            if assay_every and assay_fn and self.tick % int(assay_every) == 0:
                score = assay_fn(self)
                self.assay_scores.append({"tick": self.tick, "score": score})

    def census(self):
        live = self.alive()
        genomes = {}
        for c in live:
            key = tuple(c.genome)
            genomes[key] = genomes.get(key, 0) + 1
        unique = len(genomes)
        top = 0
        if genomes:
            top = max(genomes.values())
        monoculture = bool(live) and top == len(live) and unique == 1
        stasis = unique <= 1 and len(live) > 0
        kinds = {}
        for c in live:
            kinds[c.unit_kind] = kinds.get(c.unit_kind, 0) + 1
        return {
            "tick": self.tick,
            "n_alive": len(live),
            "n_dead": len(self.dead),
            "n_births": sum(1 for a in self.ancestry if a["event"] == "BIRTH"),
            "unique_genomes": unique,
            "max_clone_share": (float(top) / len(live)) if live else 0.0,
            "monoculture": monoculture,
            "stasis_suspect": stasis and len(live) >= 4,
            "kind_counts": kinds,
            "organism_energy": self.organism_energy(),
            "resource_energy": self.resource_energy(),
            "energy_injected": self.energy_injected,
            "energy_sunk": self.energy_sunk,
            "illegal_attempts": len(self.illegal_log),
            "physics_hash": self.physics_hash,
        }

    def clone_frozen_reproduction(self):
        """Observer clone: same state, replication opcode is a no-op."""
        other = copy.deepcopy(self)
        return other
