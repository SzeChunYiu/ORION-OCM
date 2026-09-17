"""PROC2 v1 — seeded stochastic neutral program search (GMI #833).

BLIND: genomes are per-cell basis-expression tuples over the frozen basis;
mutations are primitive structural edits; fitness is lexicographic
(battery errors, cost). No family vocabulary, no macros, no accuracy/cost
trade-off constant. Deterministic given a seed.

Genome forms:
  M_ITER:   {"model":"M_ITER","input_cells":n,"update":[e]*w,
             "output_cell":j,"steps":T,"rho":1}
  M_STREAM: {"model":"M_STREAM","cells":k,"update":[e]*k,"readout":e,"rho":1}

Readout-only variant (crossover ablation): M_ITER with w=1 work cell whose
expression may reference input cells only.
"""
from __future__ import annotations

import random

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

from machinery_v1 import (DOMAIN, CONSTS, UNARIES, GUARD, expr_ops,
                          expr_atoms, batch_sim_iter, batch_sim_stream,
                          machine_cost)

UNARY_NAMES = sorted(UNARIES)


# ---------------------------------------------------------------------------
# expression tree utilities
# ---------------------------------------------------------------------------

def expr_nodes(e):
    """List of paths to all nodes; path = tuple of child indices."""
    out = [()]
    if e[0] == "un":
        out += [(2,) + p for p in expr_nodes(e[2])]
    elif e[0] == "add":
        out += [(1,) + p for p in expr_nodes(e[1])]
        out += [(2,) + p for p in expr_nodes(e[2])]
    return out


def expr_get(e, path):
    for i in path:
        e = e[i]
    return e


def expr_set(e, path, new):
    if not path:
        return new
    i = path[0]
    if e[0] == "un":
        return ["un", e[1] if i != 1 else e[1],
                expr_set(e[2], path[1:], new) if i == 2 else e[2]]
    # add node: children at 1, 2
    if i == 1:
        return ["add", expr_set(e[1], path[1:], new), e[2]]
    return ["add", e[1], expr_set(e[2], path[1:], new)]


def expr_size(e):
    return 1 + (expr_size(e[2]) if e[0] == "un" else
                (expr_size(e[1]) + expr_size(e[2]) if e[0] == "add" else 0))


SIZE_CAP = 40  # per-expression node cap (resource bound; reported)


def rand_atom(rng, atom_names):
    return ["atom", rng.choice(atom_names)]


def crossover(ga, gb, rng):
    """Neutral recombination: for M_STREAM/M_ITER genomes, replace one
    parent's cell expression (or the readout) by the other parent's
    expression for the same slot; for equal-length expressions additionally
    graft a random subtree. No new primitives; deterministic given rng."""
    import copy
    child = copy.deepcopy(ga)
    if ga["model"] != gb["model"] or ga["model"] == "M_ITER" and             ga["input_cells"] != gb["input_cells"]:
        return child
    if ga["model"] == "M_STREAM":
        if ga["cells"] != gb["cells"]:
            return child  # atom ranges must match: only equal-cell crossover
        slots = len(child["update"]) + 1  # + readout
        si = rng.randrange(slots)
        if si < len(child["update"]):
            child["update"][si] = copy.deepcopy(gb["update"][si])
        else:
            child["readout"] = copy.deepcopy(gb["readout"])
        return child
    if len(ga["update"]) != len(gb["update"]):
        return child
    wi = rng.randrange(len(child["update"]))
    child["update"][wi] = copy.deepcopy(gb["update"][wi])
    return child


def mutate_expr(e, rng, atom_names):
    """One primitive edit on a random node."""
    nodes = expr_nodes(e)
    path = rng.choice(nodes)
    node = expr_get(e, path)
    kind = node[0]
    move = rng.randrange(6)
    if kind == "atom":
        if move == 0:  # re-point
            return expr_set(e, path, rand_atom(rng, atom_names))
        if move == 1:  # wrap unary
            return expr_set(e, path, ["un", rng.choice(UNARY_NAMES), node])
        return expr_set(e, path, ["add", node, rand_atom(rng, atom_names)])
    if kind == "const":
        if move == 0:  # retarget const
            return expr_set(e, path, ["const", rng.choice(CONSTS)])
        if move == 1:  # wrap unary
            return expr_set(e, path, ["un", rng.choice(UNARY_NAMES), node])
        return expr_set(e, path, ["add", node, ["const", rng.choice(CONSTS)]])
    # un or add
    if kind == "un" and move == 0:  # retarget unary parameter
        return expr_set(e, path, ["un", rng.choice(UNARY_NAMES), node[2]])
    if move == 1:  # wrap
        return expr_set(e, path, ["un", rng.choice(UNARY_NAMES), node])
    if move == 2:  # add const
        return expr_set(e, path, ["add", node, ["const", rng.choice(CONSTS)]])
    if move == 3:  # add atom
        return expr_set(e, path, ["add", node, rand_atom(rng, atom_names)])
    if move == 4:  # splice: replace by first child (shrink)
        if kind == "un":
            return expr_set(e, path, node[2])
        return expr_set(e, path, node[1])
    # graft a fresh small subtree, or rewire within the expression
    if rng.random() < 0.5:
        e2 = rewire(e, rng)
        if e2 is not None:
            return e2
    fresh = rand_atom(rng, atom_names)
    if rng.random() < 0.5:
        fresh = ["un", rng.choice(UNARY_NAMES), fresh]
    return expr_set(e, path, ["add", node, fresh])


def cap_expr(e):
    return e if expr_size(e) <= SIZE_CAP else None


def rewire(e, rng):
    """Cost-neutral assembly move: point a random ADD node's child at
    another random subtree of the same expression (no new nodes)."""
    nodes = expr_nodes(e)
    adds = [p for p in nodes if isinstance(expr_get(e, p), list)
            and expr_get(e, p)[0] == "add"]
    if not adds:
        return e
    p = rng.choice(adds)
    node = expr_get(e, p)
    side = rng.choice((1, 2))
    sub_nodes = expr_nodes(node[side])
    q = rng.choice(sub_nodes)
    sub = expr_get(node[side], q)
    new_node = list(node)
    new_node[side] = sub
    return expr_set(e, p, new_node)


def expr_valid(e):
    """Structural validity: every node is a well-formed expression list."""
    if not isinstance(e, list) or not e:
        return False
    t = e[0]
    if t == "atom":
        return isinstance(e[1], str)
    if t == "const":
        return isinstance(e[1], int)
    if t == "un":
        return isinstance(e[1], str) and expr_valid(e[2])
    if t == "add":
        return expr_valid(e[1]) and expr_valid(e[2])
    return False


def _atoms_in_range(e, n_stream_cells, n_total_cells, model):
    for a in expr_atoms(e):
        if a == "x":
            if model != "M_STREAM":
                return False
            continue
        if not a.startswith("s"):
            return False
        if int(a[1:]) >= n_total_cells:
            return False
    return True


def genome_valid(g):
    if g["model"] == "M_ITER":
        exprs = g["update"]
        total = g["input_cells"] + len(g["update"])
        ok = all(expr_valid(e) for e in exprs) and all(
            _atoms_in_range(e, 0, total, g["model"]) for e in exprs)
        return ok and 0 <= g["output_cell"] < total
    exprs = list(g["update"]) + [g["readout"]]
    total = g["cells"]
    return all(expr_valid(e) for e in exprs) and all(
        _atoms_in_range(e, total, total, g["model"]) for e in exprs)


def copy_subtree(source, target, rng):
    """Graft a uniformly random subtree of `source` into a uniformly random
    node position of `target` (neutral structural move; no new primitives)."""
    spaths = expr_nodes(source)
    tpaths = expr_nodes(target)
    sp = rng.choice(spaths)
    sub = expr_get(source, sp)
    tp = rng.choice(tpaths)
    new = expr_set(target, tp, ["add", expr_get(target, tp), sub])
    return new


# ---------------------------------------------------------------------------
# genome mutation
# ---------------------------------------------------------------------------


def remap_atoms(e, dropped, n_old):
    """Reindex cell atoms after dropping cell `dropped` (of n_old): shift
    higher indices down; references to the dropped cell become const 0."""
    t = e[0]
    if t == "atom":
        name = e[1]
        if not name.startswith("s"):
            return e
        i = int(name[1:])
        if i == dropped:
            return ["const", 0]
        if i > dropped:
            return ["atom", "s%d" % (i - 1)]
        return e
    if t == "const":
        return e
    if t == "un":
        return ["un", e[1], remap_atoms(e[2], dropped, n_old)]
    return ["add", remap_atoms(e[1], dropped, n_old),
            remap_atoms(e[2], dropped, n_old)]


def mutate_genome(g, rng, cell_cap, readout_only=False, work_only_atoms=None):
    import copy
    g = copy.deepcopy(g)
    move = rng.randrange(10 if not readout_only else 5)
    if g["model"] == "M_ITER":
        w = len(g["update"])
        n_in = g["input_cells"]
        if readout_only:
            atom_names = ["s%d" % i for i in range(n_in)]
        elif work_only_atoms is not None:
            atom_names = work_only_atoms
        else:
            atom_names = ["s%d" % i for i in range(n_in + w)]
        if move == 0 or w == 0:  # mutate a work expr (or grow one)
            i = rng.randrange(w) if w else 0
            if w == 0:
                g["update"] = [rand_atom(rng, atom_names)]
            else:
                me = mutate_expr(g["update"][i], rng, atom_names)
                me = cap_expr(me)
                if me is not None:
                    g["update"][i] = me
        elif move == 6 and w >= 2:  # copy subtree between work exprs
            i, j = rng.sample(range(w), 2)
            me = copy_subtree(g["update"][i], g["update"][j], rng)
            me = cap_expr(me)
            if me is not None:
                g["update"][i] = me
        elif move == 7 and w < cell_cap:  # duplicate a work cell
            i = rng.randrange(w)
            dup = g["update"][i]
            g["update"].append(dup)
        elif move == 1 and w < cell_cap:  # add work cell
            g["update"].append(rand_atom(rng, atom_names))
        elif move == 2 and w > 1:  # drop work cell (re-map atom refs)
            di = rng.randrange(w)
            g["update"].pop(di)
            g["update"] = [remap_atoms(e, n_in + di, n_in + w)
                           for e in g["update"]]
            if g["output_cell"] >= n_in + di:
                g["output_cell"] = max(0, g["output_cell"] - 1)
        elif move == 3:  # move output
            g["output_cell"] = rng.randrange(n_in + len(g["update"]))
        else:  # re-mutate another expr
            i = rng.randrange(w)
            me = mutate_expr(g["update"][i], rng, atom_names)
            me = cap_expr(me)
            if me is not None:
                g["update"][i] = me
    else:  # M_STREAM
        k = g["cells"]
        atom_names = ["s%d" % i for i in range(k)] + ["x"]
        if move == 0:
            i = rng.randrange(k)
            me = mutate_expr(g["update"][i], rng, atom_names)
            me = cap_expr(me)
            if me is not None:
                g["update"][i] = me
        elif move == 6 and k >= 2:  # copy subtree between cells
            i, j = rng.sample(range(k), 2)
            me = copy_subtree(g["update"][i], g["update"][j], rng)
            me = cap_expr(me)
            if me is not None:
                g["update"][i] = me
        elif move == 7 and k < cell_cap:  # duplicate a cell
            g["update"].append(g["update"][rng.randrange(k)])
            g["cells"] = k + 1
        elif move == 1 and k < cell_cap:
            g["cells"] = k + 1
            g["update"].append(rand_atom(rng, ["s%d" % i for i in range(k + 1)]
                                         + ["x"]))
        elif move == 2 and k > 1:
            di = rng.randrange(k)
            g["update"].pop(di)
            g["readout"] = remap_atoms(g["readout"], di, k)
            g["update"] = [remap_atoms(e, di, k) for e in g["update"]]
            g["cells"] = k - 1
        elif move == 3:
            me = mutate_expr(g["readout"], rng, atom_names)
            me = cap_expr(me)
            if me is not None:
                g["readout"] = me
        else:
            me = mutate_expr(g["readout"], rng, atom_names)
            me = cap_expr(me)
            if me is not None:
                g["readout"] = me
    return g


def rand_genome_iter(rng, n_in, steps, cell_cap, readout_only=False):
    w = rng.randrange(1, min(3, cell_cap) + 1)
    atoms_in = ["s%d" % i for i in range(n_in)]
    if readout_only:
        update = [grown_expr(rng, atoms_in) for _ in range(1)]
    else:
        atoms = atoms_in + ["s%d" % i for i in range(n_in, n_in + w)]
        update = [grown_expr(rng, atoms) for _ in range(w)]
    return {"model": "M_ITER", "input_cells": n_in, "update": update,
            "output_cell": n_in, "steps": steps, "rho": 1}


def grown_expr(rng, atom_names, edits_poisson=6):
    """Random expression grown by a small random number of primitive edits
    from a random atom (neutral initialization distribution)."""
    e = rand_atom(rng, atom_names)
    for _ in range(rng.randrange(0, edits_poisson)):
        e2 = mutate_expr(e, rng, atom_names)
        if cap_expr(e2) is not None:
            e = e2
    return e


def rand_genome_stream(rng, cell_cap):
    k = rng.randrange(1, min(3, cell_cap) + 1)
    atoms = ["s%d" % i for i in range(k)] + ["x"]
    return {"model": "M_STREAM", "cells": k,
            "update": [grown_expr(rng, atoms) for _ in range(k)],
            "readout": grown_expr(rng, atoms), "rho": 1}


# ---------------------------------------------------------------------------
# fitness
# ---------------------------------------------------------------------------

class IterTaskSet:
    def __init__(self, layouts, required, steps):
        self.X = np.array(layouts, dtype=np.int64)
        self.y = np.array(required, dtype=np.int64)
        self.steps = steps

    def evaluate(self, g):
        final, legal, _traj = batch_sim_iter(g, self.X, np)
        pred = final[:, g["output_cell"]]
        errs = int(np.count_nonzero(pred != self.y)) + int(
            np.count_nonzero(~legal)) * (self.X.shape[0] + 1)
        return errs, machine_cost(g)


class StreamTaskSet:
    """Stream tasks: rows have streams + required output at final position
    (mode='final') or at every position (mode='all')."""

    def __init__(self, streams, required, mode):
        self.S = np.array(streams, dtype=np.int64)
        self.mode = mode
        if mode == "final":
            self.y = np.array(required, dtype=np.int64)
        else:
            self.Y = np.array(required, dtype=np.int64)

    def evaluate(self, g):
        outs, legal, _ = batch_sim_stream(g, self.S, np)
        if self.mode == "final":
            pred = outs[:, -1]
            errs = int(np.count_nonzero(pred != self.y))
        else:
            errs = int(np.count_nonzero(outs != self.Y))
        errs += int(np.count_nonzero(~legal)) * (self.S.shape[0] + 1)
        return errs, machine_cost(g)


def evolve(taskset, seed, budget, cell_cap, genome="iter", n_in=0, steps=16,
           mu=16, lam=64, readout_only=False, init=None):
    """(mu+lambda) stochastic search; lexicographic fitness; deterministic."""
    rng = random.Random(seed)
    if init is not None:
        pop = [init]
        while len(pop) < mu:
            if genome == "iter":
                pop.append(rand_genome_iter(rng, n_in, steps, cell_cap,
                                            readout_only))
            else:
                pop.append(rand_genome_stream(rng, cell_cap))
    else:
        pop = []
        while len(pop) < mu:
            if genome == "iter":
                pop.append(rand_genome_iter(rng, n_in, steps, cell_cap,
                                            readout_only))
            else:
                pop.append(rand_genome_stream(rng, cell_cap))
    evaled = {}

    worst = (10 ** 9, 10 ** 9)

    def fit(g):
        key = repr(g)
        if key not in evaled:
            evaled[key] = taskset.evaluate(g) if genome_valid(g) else worst
        return evaled[key]

    scored = [(fit(g), g) for g in pop]
    evals = len(pop)
    best = min(scored, key=lambda p: (p[0], repr(p[1])))
    while evals < budget:
        children = []
        parents_pool = [g for (f, g) in scored]  # population maintained below
        while len(children) < lam:
            if len(parents_pool) >= 2 and rng.random() < 0.5:
                pa, pb = rng.sample(parents_pool, 2)
                child = crossover(pa, pb, rng)
            else:
                child = rng.choice(parents_pool)
            child = mutate_genome(child, rng, cell_cap, readout_only)
            children.append(child)
        scored_children = [(fit(g), g) for g in children]
        evals += len(children)
        # NEUTRAL-DRIFT SELECTION: the next population is a uniform random
        # sample among genomes tying the best error count (cost does not
        # gate survival on the plateau, so structure can accumulate); the
        # champion is tracked separately as the lexicographic
        # (errors, cost) minimum ever seen.
        union = scored + scored_children
        best_err = min(f[0] for f, _ in union)
        plateau = [g for f, g in union if f[0] == best_err]
        if len(plateau) <= mu:
            parents = plateau
        else:
            idxs = rng.sample(range(len(plateau)), mu)
            parents = [plateau[i] for i in idxs]
        # dedup population representatives to avoid convergence to clones
        seen = set()
        uniq = []
        for g in parents:
            k = repr(g)
            if k not in seen:
                seen.add(k)
                uniq.append(g)
        scored = [(fit(g), g) for g in uniq]
        b = min([(f, g) for f, g in union], key=lambda p: (p[0], repr(p[1])))
        if (b[0], repr(b[1])) < (best[0], repr(best[1])):
            best = b
    return {"fitness": list(best[0]), "genome": best[1],
            "evals": evals, "seed": seed,
            "distinct_genomes_evaluated": len(evaled),
            "selection": "neutral-drift plateau sampling; champion "
                         "lexicographic (errors, cost)"}


# ---------------------------------------------------------------------------
# null batteries (200-seed random admission, frozen hash)
# ---------------------------------------------------------------------------

def frozen_hash(s):
    return ((s + 1) * 2654435761) % (2 ** 32)


def null_outputs_bit(seed, n, required_original):
    """Draw n uniform {0,1} outputs from the frozen hash stream of a seed."""
    rng = random.Random(frozen_hash(seed))
    return [rng.randint(0, 1) for _ in range(n)]


def null_truth_tables(seed, n_tasks):
    """n_tasks random functions {0,1}^2 -> D (7 values), frozen-hash seeded."""
    rng = random.Random(frozen_hash(seed))
    outs = []
    for _ in range(n_tasks):
        outs.append([rng.choice(DOMAIN) for _ in range(4)])
    return outs
