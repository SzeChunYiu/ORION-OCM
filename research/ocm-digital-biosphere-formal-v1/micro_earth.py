"""Enumerable 2–8 organism micro-Earths. Exhaustive instruments, not long runs.

State is tiny: genomes in {0,1,2,3}, energy in 0..8, one public library,
observer assay scores that MUST NOT enter K_birthdeath unless leak=True.
"""
from __future__ import annotations

import copy
import itertools
import random


class Cell:
    __slots__ = (
        "uid", "g", "energy", "method", "mem", "parent", "group",
        "assay", "inbox",
    )

    def __init__(self, uid, g, energy, method=0, parent=None, group=None):
        self.uid = uid
        self.g = int(g)
        self.energy = int(energy)
        self.method = int(method)
        self.mem = 0
        self.parent = parent
        self.group = group
        self.assay = 0  # observer-only
        self.inbox = None


class MicroEarth:
    def __init__(self, n, seed=0, leak=False, social="optional",
                 kernels=None, regime=0):
        if n < 2 or n > 8:
            raise ValueError("n in 2..8")
        self.n0 = n
        self.rng = random.Random(seed)
        self.leak = bool(leak)
        self.social = social
        self.kernels = dict(kernels or {})
        self.regime = int(regime)
        self.tick = 0
        self.resource = 16
        self.library = []  # list of methods; usefulness declared separately
        self.useful_method = 1
        self.junk_method = 9
        self.history = []
        self.write_graph = set()  # edges src->dst
        self.cells = []
        for i in range(n):
            g = i % 4
            self.cells.append(Cell(i, g, energy=4, method=0, group=i % 2))
        self.next_uid = n
        self._register_graph()

    def _on(self, name):
        return self.kernels.get(name, True)

    def _register_graph(self):
        # Legal physics edges
        self.write_graph.add(("resource", "energy"))
        self.write_graph.add(("energy", "birth"))
        self.write_graph.add(("P", "resource"))
        if self.leak:
            self.write_graph.add(("assay", "energy"))
            self.write_graph.add(("assay", "birth"))

    def ancestors(self, node, seen=None):
        if seen is None:
            seen = set()
        for a, b in self.write_graph:
            if b == node and a not in seen:
                seen.add(a)
                self.ancestors(a, seen)
        return seen

    def assay_interferes(self):
        return "assay" in self.ancestors("birth") or "assay" in self.ancestors("energy")

    def alive(self):
        return [c for c in self.cells if c.energy > 0]

    def step(self):
        if self._on("K_world"):
            self.resource = min(16, self.resource + (0 if self.regime else 1))
            if self.regime == 1:
                self.resource = max(0, self.resource - 2)
        live = self.alive()
        if self._on("K_senseact"):
            for c in live:
                # Harvest 2, maintenance 1: net +1/tick when resource is present.
                # Harvest 1 cancelled maintenance 1, so clean energy stayed at
                # the start value 4 and never reached birth threshold 6.
                # Reproduction was reachable only through the assay-leak bonus
                # (extra take + lower threshold). That made BIO-T1's clean HOLD
                # vacuous: no birth/death decision occurred to leave uncontaminated.
                take = min(2, self.resource)
                if self.leak:
                    take = min(take + (1 if c.assay > 0 else 0), self.resource)
                self.resource -= take
                c.energy = min(8, c.energy + take - 1)
                self.history.append(("harvest", c.uid, take))
        if self._on("K_learn"):
            for c in live:
                if c.energy >= 3:
                    c.mem = c.g
        if self._on("K_social") and len(live) >= 2:
            self._social(live)
        if self._on("K_assemble"):
            # proximity groups by genome mod 2 — observer clustering, not individuality
            for c in live:
                c.group = c.g % 2
        if self._on("K_birthdeath"):
            self._birthdeath(live)
        self.tick += 1

    def _social(self, live):
        donor = max(live, key=lambda c: c.energy)
        for c in live:
            if c is donor:
                continue
            payload = donor.method if donor.method else donor.g
            if self.social == "forced":
                c.method = payload
                self.history.append(("forced_copy", donor.uid, c.uid, payload))
            elif self.social == "optional":
                # accept only if payload == useful_method
                if payload == self.useful_method:
                    c.method = payload
                    self.history.append(("copy_ok", donor.uid, c.uid, payload))
            elif self.social == "prestige":
                c.method = payload  # copy high-energy even if stale
                self.history.append(("prestige", donor.uid, c.uid, payload))
            c.inbox = payload
        # culture bytes
        self.library.append(donor.method if donor.method else self.junk_method)

    def _birthdeath(self, live):
        born = []
        for c in list(live):
            thr = 6
            if self.leak and c.assay > 0:
                thr = 3
            if c.energy >= thr and len(self.alive()) + len(born) < 8:
                child_g = c.g
                if self._on("K_mut"):
                    if self.rng.random() < 0.25:
                        child_g = (c.g + 1) % 4
                child = Cell(self.next_uid, child_g, energy=2, parent=c.uid,
                             group=c.group)
                if self._on("K_inherit"):
                    if self.kernels.get("inherit_memory", False):
                        child.method = c.method
                        child.mem = c.mem
                self.next_uid += 1
                c.energy -= 2
                born.append(child)
                self.history.append(("birth", c.uid, child.uid))
        self.cells.extend(born)
        for c in list(self.cells):
            if c.energy <= 0:
                self.history.append(("death", c.uid))

    def observer_assay(self):
        """Protected: scores do not write energy unless leak."""
        scores = []
        for c in self.alive():
            score = 1.0 if c.mem == c.g and c.method == self.useful_method else 0.0
            c.assay = int(score) if self.leak else 0
            # always record observer copy separately
            scores.append({"uid": c.uid, "score": score, "feeds_reproduction": self.leak})
        return scores

    def snapshot(self):
        live = self.alive()
        return {
            "tick": self.tick,
            "n_alive": len(live),
            "genomes": [c.g for c in live],
            "methods": [c.method for c in live],
            "energy": [c.energy for c in live],
            "library_bytes": len(self.library),
            "resource": self.resource,
            "leak": self.leak,
            "assay_interferes": self.assay_interferes(),
        }


def enumerate_mutation_neighbourhood(g, alleles=4):
    """All 1-step mutants. Exhaustive for |alleles|=4."""
    return [((g + k) % alleles) for k in range(1, alleles)]


def run_horizon(earth, ticks, assay_every=1):
    assays = []
    snaps = []
    for t in range(ticks):
        earth.step()
        if assay_every and (t + 1) % assay_every == 0:
            assays.append(earth.observer_assay())
        snaps.append(earth.snapshot())
    return snaps, assays


def exhaustive_social_choices(n=3):
    """All forced/optional/prestige × leak on/off for n organisms, 1 tick."""
    rows = []
    for social, leak in itertools.product(
            ("optional", "forced", "prestige"), (False, True)):
        e = MicroEarth(n, seed=1, leak=leak, social=social)
        e.cells[0].method = 1
        e.cells[0].energy = 8
        e.step()
        rows.append({
            "social": social,
            "leak": leak,
            "methods": [c.method for c in e.alive()],
            "interferes": e.assay_interferes(),
            "n": len(e.alive()),
        })
    return rows
