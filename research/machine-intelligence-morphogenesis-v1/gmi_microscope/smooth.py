"""Stage D'/E' — the smooth-generalization ecology E_smooth with reference rows, so that the
revision-axis handover (PH-REV) becomes observable where a dense-update form can win.

Ecology (frozen; identical to blind.py E_smooth): 16 inputs x in 0..15 (4 bits), target
y = fx(0.25*b0 + 0.5*b1 - 0.25*b2 + 0.5*b3); TRAINING inputs = {0,3,5,6,9,10,12,15};
H = 16 feedback events (two passes over the 8 seen inputs); queries on ALL 16 inputs after every
event; verification after every event; one revocation (of the t=2 example) at t = 9.
Capability = 1 - mean|out - y|/1.5 over all 16 inputs after the protocol (theta = 0.85).

Rows (programs over the primitive universe; parents' accounting documented):
  S4  parametric gradient learner: 4 inputs -> h hidden (ReLU) -> linear output; squared-error
      gradient step (LR 0.25); revocation = retrain from initial params on remaining examples.
  S2  exact program search over the linear-coefficient grammar c in {-1,-1/2,-1/4,0,1/4,1/2,1}^4
      (2401 programs), enumerate-test against stored examples on every counterexample; library
      insert; revocation = re-synthesis. (Levin/CEGIS parent: the target IS in the grammar.)
  S5  exemplar memory keyed on x (returns stored value or 0): cannot generalize by construction.
  S3  particle set over the same linear-coefficient hypotheses (K particles), likelihood by
      squared error, conditioning + one-coefficient mutation moves; local? no — reweights all.
Prediction frozen in CLAIM_LADDER_V2 (E'): at r = 0, S4 is on the frontier for H >= 8 IF it
reaches theta; any local row reaching theta overtakes it at r* computed from per-event costs; if
S4 never reaches theta the frontier is not dense and the handover is again not observable.
A second registered possibility (Abbe/Shalev-Shwartz reading): exact enumeration (S2) reaches
theta = 1.0 while the 8-bit gradient learner does not — an exact-search vs gradient separation.
Writes microscopes/results/STAGE_DE_SMOOTH_V1.json and STAGE_DE_SMOOTH_REPORT_V1.md.
"""
from __future__ import annotations

import itertools
import json
import os

from . import bases
from .core import COORDS, FX_ONE, Machine, clamp, fx, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
ALL_X = list(range(16))
TRAIN = [0, 3, 5, 6, 9, 10, 12, 15]
TARGET = {x: clamp(fx(0.25 * (x & 1) + 0.5 * ((x >> 1) & 1) - 0.25 * ((x >> 2) & 1) + 0.5 * ((x >> 3) & 1))) for x in ALL_X}
H = 16
REVOKE_AT = 9
THETA = 0.85
COEFFS = [fx(v) for v in (-1, -0.5, -0.25, 0, 0.25, 0.5, 1)]
GRAMMAR = list(itertools.product(COEFFS, repeat=4))  # 2401 linear programs
bits = lambda x: [(x >> i) & 1 for i in range(4)]


def linear_eval(M, coeffs, x):
    s = 0
    for i, c in enumerate(coeffs):
        if bits(x)[i]:
            s = M.op("ADD", s, c)
        else:
            M.op("AND", 0, 0)  # one gate per unused bit (uniform program cost)
    return s


class S4Net:
    row = "S4"; ladder = (2, 4); LR = fx(0.25)

    def __init__(self, h): self.h = h

    def init(self, M):
        init = [0.5, -0.25, 0.75, -0.5, 0.25, 0.5, -0.75, 0.25, 0.5, -0.5, 0.25, 0.75, -0.25, 0.5, 0.25, -0.5, 0.125, -0.125, 0.375, -0.375, 0.625, -0.625, 0.875, -0.875]
        k = 0
        for j in range(self.h):
            for i in range(4):
                M.declare(f"w{j}{i}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"b{j}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"v{j}", "fx", fx(init[k % len(init)])); k += 1
        M.declare("c", "fx", 0)
        M.declare_store("examples")
        M.declare_program(10 * self.h + 2)
        self.names = list(M.cells)
        self._initial = {n: M.read(n) for n in self.names}

    def _forward(self, M, x, record=False):
        xb = [fx(1.0) if b else 0 for b in bits(x)]
        if record: M.start_tape()
        acts = []
        for j in range(self.h):
            s = M.read(f"b{j}")
            for i in range(4):
                s = M.op("ADD", s, M.op("MUL", M.read(f"w{j}{i}"), xb[i]))
            acts.append(M.op("THRESH", s))
        out = M.read("c")
        for j in range(self.h):
            out = M.op("ADD", out, M.op("MUL", M.read(f"v{j}"), acts[j]))
        return out, acts, xb

    def query(self, M, x):
        return self._forward(M, x)[0]

    def _step(self, M, x, y):
        out, acts, xb = self._forward(M, x, record=True)
        err = M.op("SUB", out, y)
        _cl = clamp
        if "ADJ" in M.basis.native:
            M.op("ADJ", err); mul = lambda a, b: _cl((a * b + 8) >> 4)
        else:
            M.op("ADJ", err); mul = lambda a, b: M.op("MUL", a, b)
        upd = {"c": _cl(M.read("c") - mul(self.LR, err))}
        for j in range(self.h):
            upd[f"v{j}"] = _cl(M.read(f"v{j}") - mul(self.LR, mul(err, acts[j])))
            g_act = mul(err, M.read(f"v{j}")) if acts[j] > 0 else 0
            upd[f"b{j}"] = _cl(M.read(f"b{j}") - mul(self.LR, g_act))
            for i in range(4):
                upd[f"w{j}{i}"] = _cl(M.read(f"w{j}{i}") - mul(self.LR, mul(g_act, xb[i])))
        for n, v in upd.items(): M.write(n, v)

    def feedback(self, M, x, y):
        M.op("S_INSERT", "examples", x, y); self._step(M, x, y)

    def revoke(self, M, x):
        M.op("S_DELETE", "examples", x)
        for n in self.names: M.write(n, self._initial[n])
        for ex, ey in list(M.stores["examples"]): self._step(M, ex, ey)


class S2Search:
    row = "S2"; ladder = (2, 4)

    def __init__(self, n): self.n = n

    def init(self, M):
        M.declare_store("library"); M.declare_store("examples"); M.declare("current", "fin", 0)
        M.declare_program(8)
        for i in range(self.n - 1): M.op("S_INSERT", "library", 100 + i, i)
        self.idx = 0

    def query(self, M, x):
        return linear_eval(M, GRAMMAR[self.idx], x)

    def _synth(self, M):
        exs = list(M.stores["examples"])
        for k, coeffs in enumerate(GRAMMAR):
            ok = True
            for ex, ey in exs:
                if linear_eval(M, coeffs, ex) != ey: ok = False; break
            if ok:
                self.idx = k; M.write("current", k % 4); M.op("S_INSERT", "library", 0, k); return

    def feedback(self, M, x, y):
        if self.query(M, x) == y: return
        M.op("S_INSERT", "examples", x, y); self._synth(M)

    def revoke(self, M, x):
        M.op("S_DELETE", "examples", x); M.op("S_DELETE", "library", 0); self._synth(M)


class S5Memory:
    row = "S5"; ladder = (2, 4)

    def __init__(self, n): self.n = n

    def init(self, M):
        M.declare_store("mem"); M.declare_program(3)
        for i in range(self.n - 1): M.op("S_INSERT", "mem", 100 + i, 0)

    def query(self, M, x):
        v = M.op("S_LOOKUP", "mem", x); return 0 if v is None else v

    def feedback(self, M, x, y):
        M.op("S_DELETE", "mem", x); M.op("S_INSERT", "mem", x, y)

    def revoke(self, M, x):
        M.op("S_DELETE", "mem", x)


class S3Particles:
    row = "S3"; ladder = (4, 8)

    def __init__(self, K): self.K = K

    def init(self, M):
        for i in range(self.K):
            M.declare(f"p{i}", "fin", (i * 397) % len(GRAMMAR)); M.declare(f"w{i}", "fx", fx(1.0 / self.K))
        M.declare_store("evidence"); M.declare_program(10)

    def query(self, M, x):
        best = max(range(self.K), key=lambda i: M.read(f"w{i}"))
        return linear_eval(M, GRAMMAR[M.read(f"p{best}")], x)

    def _fit(self, M, k):
        n = 0
        for ex, ey in M.stores["evidence"]:
            n += M.op("EQ", linear_eval(M, GRAMMAR[k], ex), ey)
        return n

    def _condition(self, M):
        ws = []
        for i in range(self.K):
            w = fx(1.0)
            for ex, ey in M.stores["evidence"]:
                like = fx(0.9) if linear_eval(M, GRAMMAR[M.read(f"p{i}")], ex) == ey else fx(0.1)
                w = M.op("SCORE", w, like)
            ws.append(w)
        ws = M.op("NORMALIZE", ws)
        for i in range(self.K): M.write(f"w{i}", ws[i])
        for i in range(self.K):
            if M.op("SAMPLE", 0.5):
                slot = (M.op("SAMPLE", 0.5) << 1) | M.op("SAMPLE", 0.5)
                cur = list(GRAMMAR[M.read(f"p{i}")])
                cur[slot] = COEFFS[(COEFFS.index(cur[slot]) + 1 + (M.op("SAMPLE", 0.5) * 3)) % len(COEFFS)]
                k2 = GRAMMAR.index(tuple(cur))
                if self._fit(M, k2) >= self._fit(M, M.read(f"p{i}")): M.write(f"p{i}", k2)

    def feedback(self, M, x, y):
        M.op("S_INSERT", "evidence", x, y); self._condition(M)

    def revoke(self, M, x):
        M.op("S_DELETE", "evidence", x); self._condition(M)


ROWS = {"S4": S4Net, "S2": S2Search, "S5": S5Memory, "S3": S3Particles}
DENSE = {"S4", "S3"}
LOCAL = {"S2", "S5"}


def run(row, basis, size, seed=0):
    ref = ROWS[row](size)
    M = Machine(basis, seed=seed)
    M.phase("exec"); ref.init(M)
    D = []; max_writes = 0
    for t in range(1, H + 1):
        x = TRAIN[(t - 1) % len(TRAIN)]; y = TARGET[x]
        M.phase("exec"); D.append({xx: ref.query(M, xx) for xx in ALL_X})
        M.phase("upd"); ref.feedback(M, x, y); max_writes = max(max_writes, len(M.L.writes_in_event)); M.end_event()
        M.phase("ver")
        for xx in ALL_X: M.op("EQ", ref.query(M, xx), TARGET[xx])
        if t == REVOKE_AT:
            M.phase("rev"); ref.revoke(M, TRAIN[1]); M.end_event()
    M.phase("exec"); final = {xx: ref.query(M, xx) for xx in ALL_X}; D.append(final)
    err = sum(abs(final[xx] - TARGET[xx]) for xx in ALL_X) / FX_ONE / len(ALL_X)
    cap = max(0.0, 1 - err / 1.5)
    n_cells = len(M.cells) + sum(len(s) for s in M.stores.values())
    return {"row": row, "basis": basis.name, "size": size, "D": D, "R": dict(M.L.c), "capability": round(cap, 4), "max_writes": max_writes, "n_cells": n_cells}


def per_event(R):
    return {"desc": R["desc"], "exec_q": R["exec"] / (16 * (H + 1)), "upd_e": R["upd"] / H, "ver_e": R["ver"] / H, "rev_e": R["rev"]}


def cost(pe, Hh, r):
    return pe["desc"] + Hh * pe["exec_q"] + r * pe["upd_e"] + r * pe["ver_e"] + (r / 4) * pe["rev_e"]


def main(seed=0):
    cols = list(bases.ALL)
    cells = {}
    for row, cls in ROWS.items():
        for col in cols:
            for size in cls.ladder:
                cells[(row, col, size)] = run(row, bases.ALL[col], size, seed)
    c2 = {f"{row}@{size}": all(cells[(row, col, size)]["D"] == cells[(row, cols[0], size)]["D"] for col in cols) for row, cls in ROWS.items() for size in cls.ladder}
    caps = {f"{row}|{col}|{size}": cells[(row, col, size)]["capability"] for (row, col, size) in cells}
    H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]; R_GRID = [0, 1, 2, 4, 8, 16, 32]
    frontier = {}; ph = {}
    for col in cols:
        for Hh in H_GRID:
            for r in R_GRID:
                adm = []
                for row, cls in ROWS.items():
                    size = cls.ladder[-1]
                    c = cells[(row, col, size)]
                    if c["capability"] >= THETA:
                        adm.append((row, cost(per_event(c["R"]), Hh, r)))
                if not adm:
                    frontier[f"{col}|H={Hh}|r={r}"] = []; continue
                cmin = min(v for _, v in adm)
                frontier[f"{col}|H={Hh}|r={r}"] = sorted(row for row, v in adm if v <= cmin + 1e-9)
        seq = [frontier[f"{col}|H=16|r={r}"] for r in R_GRID]
        dense = [any(w in DENSE for w in s) for s in seq]; local = [any(w in LOCAL for w in s) for s in seq]
        if not any(dense):
            v = "NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0)"
        elif dense[0] and (not dense[-1]) and local[-1]:
            v = "SUPPORTED__DENSE_WINS_LOW_r_LOCAL_WINS_HIGH_r"
        elif all(dense):
            v = "NOT_OBSERVABLE__DENSE_WINS_AT_EVERY_r (no local row reaches theta)"
        else:
            v = "REFUTED_OR_NONMONOTONE"
        ph[col] = {"winners_by_r_H16": dict(zip(map(str, R_GRID), seq)), "verdict": v}
    receipt = {"schema": "StageDESmoothV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "ecology": {"inputs": 16, "train": TRAIN, "H": H, "revoke_at": REVOKE_AT, "theta": THETA},
               "C2": c2, "capability_by_cell": caps, "R_by_cell": {f"{row}|{col}|{size}": cells[(row, col, size)]["R"] for (row, col, size) in cells},
               "writes_by_cell": {f"{row}|{col}|{size}": cells[(row, col, size)]["max_writes"] for (row, col, size) in cells},
               "frontier_H_r": frontier, "PH_REV": ph, "grammar_size": len(GRAMMAR),
               "claim_ceiling": "P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts."}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, "STAGE_DE_SMOOTH_V1.json"), "w"), indent=1, sort_keys=True, default=str)
    L = ["# Stage D'/E' — smooth-generalization ecology: report V1\n", f"Receipt `STAGE_DE_SMOOTH_V1.json` (sha256 `{receipt['receipt_sha256'][:16]}…`). 16 inputs, 8 seen; θ = {THETA}; rows S4 (gradient net), S2 (exact linear search, grammar of {len(GRAMMAR)}), S5 (exemplar memory), S3 (particles over the grammar).\n",
         "## Capability after the protocol (largest ladder size, by column)\n", "| row | " + " | ".join(c.split('_')[0] for c in cols) + " |", "|---|" + "---|" * len(cols)]
    for row, cls in ROWS.items():
        L.append(f"| {row}@{cls.ladder[-1]} | " + " | ".join(str(caps[f"{row}|{c}|{cls.ladder[-1]}"]) for c in cols) + " |")
    L.append("\nC2 (Dev tables identical across columns): " + str(all(c2.values())) + "\n")
    L.append("## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)\n")
    for col, p in ph.items():
        L.append(f"- **{col.split('_')[0]}**: {p['verdict']} — winners by r at H=16: {p['winners_by_r_H16']}")
    L.append("\n" + receipt["claim_ceiling"] + "\n")
    open(os.path.join(RES, "STAGE_DE_SMOOTH_REPORT_V1.md"), "w").write("\n".join(L) + "\n")
    print("C2 all:", all(c2.values()))
    for row, cls in ROWS.items():
        print(row, {c.split('_')[0]: caps[f"{row}|{c}|{cls.ladder[-1]}"] for c in cols})
    for col, p in ph.items():
        print(col.split('_')[0], p["verdict"], p["winners_by_r_H16"])


if __name__ == "__main__":
    main()
