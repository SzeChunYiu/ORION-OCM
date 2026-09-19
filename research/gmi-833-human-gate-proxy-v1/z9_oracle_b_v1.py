#!/usr/bin/env python3
"""Z9 outcome oracle, route B: independent algorithm.  For each class the
optimum is found WITHOUT enumerating output tables: for the stateless class the
optimal output per visible cell (M, x_t) is the majority target over that cell;
for the one-bit class every next-state table (16 per mode) is enumerated and,
for each, the optimal output is chosen per (S, M, x_t) cell by majority over the
cells that reach that (S, x_t) under that next-state table.  Per-mode optima are
combined with the prevalence weights.  Imports nothing from route A.  Stdlib
only, exact integers/Fractions, python3.8.
"""
from fractions import Fraction
import json
import sys


def bits(L):
    return [[(n >> (L - 1 - i)) & 1 for i in range(L)] for n in range(2 ** L)]


def tgt(name, a, b, c):
    if name == "CUR":
        return a
    if name == "NOT_CUR":
        return 1 - a
    if name == "PREV":
        return b
    if name == "NOT_PREV":
        return 1 - b
    if name == "PREV2":
        return c
    if name == "XOR":
        return (a + b) % 2
    if name == "XNOR":
        return 1 - (a + b) % 2
    if name == "AND":
        return a * b
    if name == "OR":
        return 1 if (a + b) > 0 else 0
    if name == "NAND":
        return 1 - a * b
    if name == "XOR2":
        return (a + c) % 2
    if name == "AND2":
        return b * c
    if name == "OR2":
        return 1 if (b + c) > 0 else 0
    if name == "MAJ3":
        return 1 if a + b + c >= 2 else 0
    if name == "CONST0":
        return 0
    if name == "CONST1":
        return 1
    raise KeyError(name)


def cell_rows(L, name):
    """Yield (x_t, x_{t-1}, x_{t-2}, target) for every scored cell."""
    rows = []
    for seq in bits(L):
        for t in range(1, L):
            a = seq[t]
            b = seq[t - 1]
            c = seq[t - 2] if t >= 2 else 0
            rows.append((seq, t, tgt(name, a, b, c)))
    return rows


def stateless_min_errors(L, name):
    """Majority per x_t cell.  Returns integer error count."""
    rows = cell_rows(L, name)
    err = 0
    for x in (0, 1):
        ones = sum(1 for seq, t, y in rows if seq[t] == x and y == 1)
        tot = sum(1 for seq, t, y in rows if seq[t] == x)
        err += min(ones, tot - ones)
    return err


def onebit_min_errors(L, name):
    """For each 4-bit next-state table over (S, x_t): run the state
    trajectory, then choose the output per (S, x_t) cell by majority."""
    rows = cell_rows(L, name)
    seqs = bits(L)
    best = None
    for nxt in range(16):
        # state visited at each (sequence, t)
        state_at = {}
        for si, seq in enumerate(seqs):
            s = 0
            for t in range(L):
                state_at[(si, t)] = s
                s = (nxt >> (2 * s + seq[t])) & 1
        counts = {}
        for seq, t, y in rows:
            si = seqs.index(seq)
            key = (state_at[(si, t)], seq[t])
            o, z = counts.get(key, (0, 0))
            counts[key] = (o + y, z + 1 - y)
        err = sum(min(o, z) for o, z in counts.values())
        if best is None or err < best:
            best = err
    return best


def solve(env):
    L = int(env["L"])
    p = Fraction(env["p"])
    eta = Fraction(env["eta"])
    cells = Fraction((2 ** L) * (L - 1))
    e0s = Fraction(stateless_min_errors(L, env["target_0"])) / cells
    e1s = Fraction(stateless_min_errors(L, env["target_1"])) / cells
    e0o = Fraction(onebit_min_errors(L, env["target_0"])) / cells
    e1o = Fraction(onebit_min_errors(L, env["target_1"])) / cells
    Es = (1 - p) * e0s + p * e1s
    Eo = (1 - p) * e0o + p * e1o
    res = {"env_id": env["env_id"], "E_stateless": str(Es), "E_onebit": str(Eo),
           "lambda_star": str(eta * (Es - Eo)), "J_best_stateless": {}, "J_best_onebit": {},
           "winner_class_set": {}}
    for lam_s in env["lambdas"]:
        lam = Fraction(lam_s)
        js, jo = eta * Es, eta * Eo + lam
        res["J_best_stateless"][lam_s] = str(js)
        res["J_best_onebit"][lam_s] = str(jo)
        res["winner_class_set"][lam_s] = (["STATELESS"] if js < jo else
                                          ["PERSISTENT_STATE"] if jo < js else
                                          ["PERSISTENT_STATE", "STATELESS"])
    return res


def run(batch):
    return {"schema": "GMI_833_Z9_OUTCOMES_V1", "route": "B_cellwise_per_next_state",
            "batch": batch.get("batch"), "outcomes": [solve(e) for e in batch["environments"]]}


if __name__ == "__main__":
    print(json.dumps(run(json.load(open(sys.argv[1]))), sort_keys=True, indent=1))
