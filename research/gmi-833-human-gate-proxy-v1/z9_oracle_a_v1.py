#!/usr/bin/env python3
"""Z9 outcome oracle, route A: full enumeration of the registered candidate
universe (16 stateless tables + 65,536 one-bit transducers) under the exact
objective of FREEZE_V1.md section 5.  Stdlib only, exact Fractions, python3.8.

Usage:
  z9_oracle_a_v1.py ENVIRONMENTS.json            -> OUTCOMES json on stdout
  z9_oracle_a_v1.py --self-test                  -> reproduces the 20 registered
                                                    transitions of the parent law
"""
from fractions import Fraction
from itertools import product
import json
import sys

MENU = {
    "CUR": lambda a, b, c: a,
    "NOT_CUR": lambda a, b, c: 1 - a,
    "PREV": lambda a, b, c: b,
    "NOT_PREV": lambda a, b, c: 1 - b,
    "PREV2": lambda a, b, c: c,
    "XOR": lambda a, b, c: a ^ b,
    "XNOR": lambda a, b, c: 1 - (a ^ b),
    "AND": lambda a, b, c: a & b,
    "OR": lambda a, b, c: a | b,
    "NAND": lambda a, b, c: 1 - (a & b),
    "XOR2": lambda a, b, c: a ^ c,
    "AND2": lambda a, b, c: b & c,
    "OR2": lambda a, b, c: b | c,
    "MAJ3": lambda a, b, c: 1 if (a + b + c) >= 2 else 0,
    "CONST0": lambda a, b, c: 0,
    "CONST1": lambda a, b, c: 1,
}
CLASSES = ("STATELESS", "PERSISTENT_STATE")


def window(seq, t):
    a = seq[t]
    b = seq[t - 1] if t - 1 >= 0 else 0
    c = seq[t - 2] if t - 2 >= 0 else 0
    return a, b, c


def targets(L, name):
    """Per mode target table: list over sequences of list over scored t."""
    f = MENU[name]
    out = []
    for seq in product((0, 1), repeat=L):
        out.append([f(*window(seq, t)) for t in range(1, L)])
    return out


def error_counts_stateless(L, tgt, out_table):
    """out_table: 2 bits indexed by x_t (mode fixed by caller)."""
    err = 0
    seqs = list(product((0, 1), repeat=L))
    for si, seq in enumerate(seqs):
        for ti, t in enumerate(range(1, L)):
            y = (out_table >> seq[t]) & 1
            err += int(y != tgt[si][ti])
    return err


def error_counts_onebit(L, tgt, next_table, out_table):
    """tables: 4 bits indexed by 2*S + x_t (mode fixed by caller)."""
    err = 0
    seqs = list(product((0, 1), repeat=L))
    for si, seq in enumerate(seqs):
        s = 0
        for t in range(L):
            idx = 2 * s + seq[t]
            if t >= 1:
                y = (out_table >> idx) & 1
                err += int(y != tgt[si][t - 1])
            s = (next_table >> idx) & 1
    return err


def enumerate_universe(L, t0, t1):
    """Return list of (class, e0, e1) for all 65,552 candidates as exact
    Fractions of the cell count.  A machine's mode-m behaviour is the
    restriction of its (S, M, x) tables to M = m: a stateless table on (M, x)
    is a pair of 2-bit tables, a one-bit machine's 8-bit tables split into two
    4-bit tables.  Enumerating the pairs is the same universe."""
    cells = Fraction((2 ** L) * (L - 1))
    tg0, tg1 = targets(L, t0), targets(L, t1)
    stateless = {}
    for tbl in range(4):
        stateless[tbl] = (error_counts_stateless(L, tg0, tbl), error_counts_stateless(L, tg1, tbl))
    out = []
    for m0 in range(4):
        for m1 in range(4):
            out.append(("STATELESS", Fraction(stateless[m0][0]) / cells, Fraction(stateless[m1][1]) / cells))
    one_m0 = {}
    one_m1 = {}
    for nxt in range(16):
        for ot in range(16):
            one_m0[(nxt, ot)] = error_counts_onebit(L, tg0, nxt, ot)
            one_m1[(nxt, ot)] = error_counts_onebit(L, tg1, nxt, ot)
    for k0 in one_m0:
        e0 = Fraction(one_m0[k0]) / cells
        for k1 in one_m1:
            out.append(("PERSISTENT_STATE", e0, Fraction(one_m1[k1]) / cells))
    if len(out) != 16 + 65536:
        raise AssertionError("universe census")
    return out


def solve(env):
    L = int(env["L"])
    p = Fraction(env["p"])
    eta = Fraction(env["eta"])
    if not (0 <= p <= 1) or eta <= 0 or L not in (3, 4):
        raise ValueError("environment outside the registered family")
    uni = enumerate_universe(L, env["target_0"], env["target_1"])
    best = {}
    for cls, e0, e1 in uni:
        E = (1 - p) * e0 + p * e1
        if cls not in best or E < best[cls]:
            best[cls] = E
    res = {"env_id": env["env_id"], "E_stateless": str(best["STATELESS"]),
           "E_onebit": str(best["PERSISTENT_STATE"]),
           "lambda_star": str(eta * (best["STATELESS"] - best["PERSISTENT_STATE"])),
           "J_best_stateless": {}, "J_best_onebit": {}, "winner_class_set": {},
           "candidates_evaluated": len(uni)}
    for lam_s in env["lambdas"]:
        lam = Fraction(lam_s)
        if lam <= 0:
            raise ValueError("lambda must be positive")
        js = eta * best["STATELESS"]
        jo = eta * best["PERSISTENT_STATE"] + lam
        res["J_best_stateless"][lam_s] = str(js)
        res["J_best_onebit"][lam_s] = str(jo)
        if js < jo:
            w = ["STATELESS"]
        elif jo < js:
            w = ["PERSISTENT_STATE"]
        else:
            w = ["PERSISTENT_STATE", "STATELESS"]
        res["winner_class_set"][lam_s] = w
    return res


def run(batch):
    return {"schema": "GMI_833_Z9_OUTCOMES_V1", "route": "A_full_enumeration",
            "batch": batch.get("batch"), "outcomes": [solve(e) for e in batch["environments"]]}


def self_test():
    """The parent law (L=3, CUR/PREV): lambda* = eta*p/2 on all 20 registered cases."""
    ok = 0
    grid = [(Fraction(1, 5), Fraction(1)), (Fraction(2, 5), Fraction(2)), (Fraction(3, 5), Fraction(3)),
            (Fraction(4, 5), Fraction(4)), (Fraction(1), Fraction(1))]
    for p in (Fraction(1, 5), Fraction(2, 5), Fraction(3, 5), Fraction(4, 5), Fraction(1)):
        for eta in (Fraction(1), Fraction(2), Fraction(3), Fraction(4)):
            ls = eta * p / 2
            env = {"env_id": "T", "L": 3, "target_0": "CUR", "target_1": "PREV", "p": str(p), "eta": str(eta),
                   "lambdas": [str(ls / 2), str(3 * ls / 2), str(ls)]}
            r = solve(env)
            ok += int(Fraction(r["lambda_star"]) == ls
                      and r["winner_class_set"][str(ls / 2)] == ["PERSISTENT_STATE"]
                      and r["winner_class_set"][str(3 * ls / 2)] == ["STATELESS"]
                      and r["winner_class_set"][str(ls)] == ["PERSISTENT_STATE", "STATELESS"])
    del grid
    return ok


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        n = self_test()
        print(json.dumps({"self_test_cases_reproduced": n, "expected": 20}))
        sys.exit(0 if n == 20 else 1)
    batch = json.load(open(sys.argv[1]))
    print(json.dumps(run(batch), sort_keys=True, indent=1))
