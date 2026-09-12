"""DC3 — energy-landscape carrier: exact microscope and bounded-reduction attack
(GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md section 2, record RV-377-045).

Carrier: a binary state x in {-1, +1}^N together with a symmetric coupling field W. Native law: Hebbian outer-product
accumulation W += x x^T (zero diagonal) and asynchronous energy descent x_i <- sign(sum_j W_ij x_j) to a fixed point.
The obligation the carrier is famous for is CONTENT-ADDRESSABLE COMPLETION: return the stored pattern whose basin
contains a corrupted cue.

Ecology E_complete(N, P, noise): P declared patterns (LCG bits); development shows each pattern once; evaluation gives
each pattern with `noise` bits flipped and asks for the exact original.

Rows:
  HOPFIELD     couplings + asynchronous descent (max SWEEPS sweeps, fixed unit order, stop at a fixed point).
  KNN_PAT      the strongest D2 parent: store the P patterns, answer by nearest stored pattern in Hamming distance.
  TABLE_EXACT  exact-key table over the patterns seen in development (no completion mechanism).
  HOPFIELD_RND negative twin: same descent law over random couplings (the Hebbian law removed).

Accounting: charged ops are the REDUCED price (one op per scalar operation); `native_ops` prices one op per DESCEND
sweep and one per HEBB update (the associative-memory hardware assumption). Description of the served state is
information-theoretic: couplings N(N-1)/2 entries of ceil(log2(2P+1)) bits; patterns P*N bits.
"""
from __future__ import annotations

import json
import math
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
SWEEPS = 10


def lcg_pattern(seed, N):
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF; out = []
    for _ in range(N):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        out.append(1 if ((x >> 16) & 1) else -1)
    return out


def ecology(N, P, noise, seed=11):
    pats = [lcg_pattern(500 + p, N) for p in range(P)]
    rng = seed; cues = []
    for p, pat in enumerate(pats):
        c = list(pat); flipped = set()
        while len(flipped) < noise:
            rng = (rng * 1103515245 + 12345) & 0xFFFFFFFF; i = (rng >> 16) % N
            if i in flipped: continue
            flipped.add(i); c[i] = -c[i]
        cues.append((c, p))
    d_min = min(sum(1 for a, b in zip(pats[i], pats[j]) if a != b) for i in range(P) for j in range(i + 1, P)) if P > 1 else N
    return {"N": N, "P": P, "noise": noise, "patterns": pats, "cues": cues, "min_pairwise_hamming": d_min}


class Arith:
    """charged scalar arithmetic in one of two DECLARED precision instruments, with identical op charges:
      'fx8'  the registered 8-bit fixed-point universe (TOTAL_BITS 8, FRAC_BITS 4; values clamp at +-7.9375);
      'wide' the declared wide-integer instrument of gap G5: the same charged operation sequence evaluated at
             unbounded integer precision. Op counts are identical in the two modes, so any capability difference
             between them is attributable to precision alone."""

    def __init__(self, M, mode): self.M = M; self.mode = mode

    def mul(self, a, b):
        r = self.M.op("MUL", 0, 0) if self.mode == "wide" else None
        return a * b if self.mode == "wide" else self.M.op("MUL", a, b)

    def add(self, a, b):
        if self.mode == "wide":
            self.M.op("ADD", 0, 0); return a + b
        return self.M.op("ADD", a, b)

    def gt(self, a, b):
        if self.mode == "wide":
            self.M.op("GT", 0, 0); return int(a > b)
        return self.M.op("GT", a, b)

    def eq(self, a, b):
        if self.mode == "wide":
            self.M.op("EQ", 0, 0); return int(a == b)
        return self.M.op("EQ", a, b)


class Row:
    row = "?"

    def __init__(self, eco, arith=None): self.e = eco; self.native_ops = 0; self.A = arith

    def init(self, M): pass

    def observe(self, M, pat): pass

    def query(self, M, cue): raise NotImplementedError

    def desc_bits(self): return 0


class Hopfield(Row):
    row = "HOPFIELD"

    def init(self, M):
        N = self.e["N"]; self.W = [[0] * N for _ in range(N)]

    def observe(self, M, pat):
        N = self.e["N"]
        for i in range(N):
            for j in range(i + 1, N):
                v = self.A.mul(pat[i], pat[j]); self.W[i][j] = self.A.add(self.W[i][j], v); self.W[j][i] = self.W[i][j]
        self.native_ops += 1  # one HEBB op at the declared native price

    def query(self, M, cue):
        N = self.e["N"]; x = list(cue)
        for _ in range(SWEEPS):
            changed = False
            for i in range(N):
                s = 0
                for j in range(N):
                    if i != j: s = self.A.add(s, self.A.mul(self.W[i][j], x[j]))
                nx = 1 if self.A.gt(s, 0) else (-1 if self.A.gt(0, s) else x[i])
                if nx != x[i]: x[i] = nx; changed = True
            self.native_ops += 1  # one DESCEND sweep at the declared native price
            if not changed: break
        return x

    def desc_bits(self):
        N, P = self.e["N"], self.e["P"]
        return (N * (N - 1) // 2) * max(1, math.ceil(math.log2(2 * P + 1)))


class HopfieldRnd(Hopfield):
    """negative twin: the descent law over couplings that carry no Hebbian information."""
    row = "HOPFIELD_RND"

    def init(self, M):
        N = self.e["N"]; self.W = [[0] * N for _ in range(N)]
        r = 99
        for i in range(N):
            for j in range(i + 1, N):
                r = (r * 1103515245 + 12345) & 0xFFFFFFFF
                self.W[i][j] = self.W[j][i] = ((r >> 16) % 3) - 1

    def observe(self, M, pat):
        self.native_ops += 1


class KnnPat(Row):
    row = "KNN_PAT"

    def init(self, M): self.mem = []

    def observe(self, M, pat): self.mem.append(list(pat))

    def query(self, M, cue):
        if not self.mem: return list(cue)
        ds = []
        for p in self.mem:
            d = 0
            for a, b in zip(p, cue): d = self.A.add(d, 0 if self.A.eq(a, b) else 1)
            ds.append(d)
        self.native_ops += len(self.mem)
        best = 0
        for i in range(1, len(ds)):
            if self.A.gt(ds[best], ds[i]): best = i
        return list(self.mem[best])

    def desc_bits(self): return len(self.mem) * self.e["N"]


class TableExact(Row):
    row = "TABLE_EXACT"

    def init(self, M): self.mem = {}

    def observe(self, M, pat): self.mem[tuple(pat)] = list(pat)

    def query(self, M, cue):
        self.native_ops += 1
        r = self.mem.get(tuple(cue))
        return list(r) if r is not None else list(cue)

    def desc_bits(self): return len(self.mem) * self.e["N"]


ROWS = {"HOPFIELD": Hopfield, "KNN_PAT": KnnPat, "TABLE_EXACT": TableExact, "HOPFIELD_RND": HopfieldRnd}


def run(row, basis, eco, seed=0, precision="fx8"):
    M = Machine(basis, seed=seed); ref = ROWS[row](eco, Arith(M, precision))
    M.phase("exec"); ref.init(M)
    for pat in eco["patterns"]:
        M.phase("upd"); ref.observe(M, pat); M.end_event()
    learn = dict(M.L.c)
    M.phase("exec"); correct = 0; outs = []
    for cue, p in eco["cues"]:
        out = ref.query(M, cue); outs.append(tuple(out)); correct += int(out == eco["patterns"][p])
    cap = round(correct / len(eco["cues"]), 4)
    R = dict(M.L.c)
    return {"row": row, "basis": basis.name, "precision": precision, "capability": cap, "admissible": cap >= THETA, "R": R, "learn_ops": learn["upd"], "exec_per_query": (R["exec"] - learn["exec"]) / len(eco["cues"]),
            "native_ops": ref.native_ops, "desc_bits": ref.desc_bits(), "answer_signature": sha256_of(outs)}


CELLS = {"N32_P2_n3": {"N": 32, "P": 2, "noise": 3}, "N32_P4_n3": {"N": 32, "P": 4, "noise": 3}, "N32_P8_n3": {"N": 32, "P": 8, "noise": 3},
         "N32_P16_n3": {"N": 32, "P": 16, "noise": 3}, "N32_P4_n1": {"N": 32, "P": 4, "noise": 1}, "N32_P8_n1": {"N": 32, "P": 8, "noise": 1}}


def lifecycle(r, H, native=False):
    return r["desc_bits"] + H * (r["native_ops"] / max(len(r.get("cues", [])) or 1, 1) if native else r["exec_per_query"])


def desc_crossover(N):
    """the number of patterns P* at which the coupling description equals the pattern-store description."""
    for P in range(1, 10000):
        if P * N >= (N * (N - 1) // 2) * max(1, math.ceil(math.log2(2 * P + 1))): return P
    return None


def main(tag="V25_DC3_ENERGY", seed=0):
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b = bases.ALL[col]; cells = {}; ecos = {}
    for cname, spec in CELLS.items():
        eco = ecology(spec["N"], spec["P"], spec["noise"]); ecos[cname] = eco
        for rname in ROWS:
            for prec in ("fx8", "wide"): cells[(cname, rname, prec)] = run(rname, b, eco, seed, prec)
    frontier = {}
    for cname in CELLS:
        n_q = len(ecos[cname]["cues"])
        for price in ("reduced", "native"):
            for prec in ("fx8", "wide"):
                for H in (1, 16, 128, 1024):
                    adm = [r for r in ROWS if cells[(cname, r, prec)]["admissible"]]
                    costs = {r: cells[(cname, r, prec)]["desc_bits"] + H * ((cells[(cname, r, prec)]["native_ops"] / n_q) if price == "native" else cells[(cname, r, prec)]["exec_per_query"]) for r in adm}
                    frontier[f"{cname}|{prec}|{price}|H={H}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []
    receipt = {"schema": "StageDC3EnergyV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "revival_record": "RV-377-045", "run_tag": tag, "domain_candidate": "DC3 energy landscape (Hopfield / associative memory)",
               "cells_spec": CELLS, "sweeps_max": SWEEPS, "theta": THETA, "rows": list(ROWS),
               "ecology_facts": {c: {"min_pairwise_hamming": ecos[c]["min_pairwise_hamming"], "noise": ecos[c]["noise"], "n_cues": len(ecos[c]["cues"])} for c in CELLS},
               "precision_instruments": {"fx8": "registered universe: TOTAL_BITS 8, FRAC_BITS 4, clamp at +-7.9375", "wide": "declared wide-integer instrument (gap G5): identical charged operation sequence at unbounded integer precision"},
               "cells": {f"{c}|{r}|{p}": {k: v for k, v in d.items() if k not in ("row", "basis")} for (c, r, p), d in cells.items()},
               "description_crossover_P_star_N32": desc_crossover(32), "frontier": frontier,
               "claim_ceiling": "exact charged replay at scope; one declared pattern set per cell; native prices declared, not measured"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DC_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("description crossover P* at N=32:", receipt["description_crossover_P_star_N32"])
    for cname in CELLS:
        print(cname, "fx8", {r: cells[(cname, r, "fx8")]["capability"] for r in ROWS}, "wide", {r: cells[(cname, r, "wide")]["capability"] for r in ROWS},
              "| desc", {r: cells[(cname, r, "wide")]["desc_bits"] for r in ("HOPFIELD", "KNN_PAT")},
              "| exec/q", {r: round(cells[(cname, r, "wide")]["exec_per_query"]) for r in ("HOPFIELD", "KNN_PAT")},
              "| front(wide) H=128", frontier[f"{cname}|wide|reduced|H=128"], frontier[f"{cname}|wide|native|H=128"])
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "V25_DC3_ENERGY")
