"""RV-377-032: E1 at the exact charged layer for the ChatGPT-lane VLC prediction (#418 / #419, GMI_MISSING_MORPHOLOGY_PREDICTION_V1,
GMI_VLC_PREDICTION_UPDATE_V2). Executes the parent-portfolio rung (their V2) on a factored ecology with REAL learning,
compilation, revision, verification and measured collateral regression, under the frozen charged cost model.

Ecology E_factored (declared):
  * 8-bit inputs; four semantic factors f_i, each a LINEAR function of its own two bits (f_i = a_i b_{2i} + c_i b_{2i+1}),
    coefficients in {0.25, 0.5, 0.75, 1.0}; a query = (x, scope) with scope a 2-subset of the factors (6 scopes) and answer
    y = sum_{i in scope} f_i(x). Seen inputs: per factor the patterns (0,0), (0,1), (1,0) are seen, (1,1) is UNSEEN
    (generalization needs the linear structure; a raw table cannot answer it).
  * Development: 24 feedback events (x, scope, y) covering the seen patterns of every factor; a REVISION redefines the
    coefficients of `cone` factors (announced: the affected factor ids are given, as a dependency-cone message), followed by
    3 fresh feedback events per revised factor.
  * Capability: exact agreement (within 1/16) on all 6 scopes x 4 unseen-pattern inputs after the last revision.
  * Lifecycle cost (frozen coordinates): C = desc + H * exec_q + U * (upd_e + ver_e + rev_e) + lambda * U * regress_e, where
    regress_e = number of UNAFFECTED (scope disjoint from the cone) queries whose served answer changed after a revision
    (collateral regression, measured by verification), and lambda is the retention price of the cell.

Rows (the portfolio; every row learns the same per-factor linear model from feedback — the rows differ ONLY in
materialization / serving / revision / verification organization, which isolates the morphology question):
  MONO_C  monolithic compiled: one global table over (x, scope) (256 x 6 entries) materialized from the learned factors;
          serve = one lookup; revision = rebuild the WHOLE table (alpha = 1).
  MOD_U   modular unversioned: per-factor 4-entry tables rebuilt in place for the revised factors only, adopted without
          verification (a wrong rebuild is served until the next rebuild).
  VLC     modular + authority/serving separation + verify-before-swap: per-factor tables rebuilt as a shadow version,
          checked against the factor's stored evidence (verifier calls), adopted only if consistent; else the old version is
          kept (retention); two copies of the rebuilt factor's table exist during the swap (memory charged in desc).
  DENSE   monolithic gradient net over 12 inputs (8 bits + 4 scope bits), retrain-all from the example store on revision.
  MEM     exact triple memory (x, scope) -> y (no generalization; control).
  KNN     Hamming kNN over stored triples (generalizing memory; control).
"""
from __future__ import annotations

import itertools
import json
import os

from . import bases
from .core import FX_ONE, Machine, clamp, fx, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
N_F = 4
SCOPES = list(itertools.combinations(range(N_F), 2))
COEFF_VALUES = [fx(v) for v in (0.25, 0.5, 0.75, 1.0)]
THETA = 0.85
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]; U_GRID = [0, 1, 2, 4, 8, 16, 32]


def fbits(x, i):
    return (x >> (2 * i)) & 1, (x >> (2 * i + 1)) & 1


def factor_value(coeffs, i, x):
    b0, b1 = fbits(x, i); a, c = coeffs[i]
    return clamp(a * b0 + c * b1)


def truth(coeffs, x, scope):
    return clamp(sum(factor_value(coeffs, i, x) for i in scope))


def seen_inputs():
    # inputs whose every factor pattern is in {(0,0),(0,1),(1,0)}: 3^4 = 81 inputs; unseen: at least one factor at (1,1)
    return [x for x in range(256) if all(fbits(x, i) != (1, 1) for i in range(N_F))]


SEEN = seen_inputs(); UNSEEN = [x for x in range(256) if x not in SEEN]
# development schedule: 24 feedback events cycling scopes and seen inputs so that every factor sees all three seen patterns
def x_single(i, p):
    return (p[0] << (2 * i)) | (p[1] << (2 * i + 1))


DEV_EVENTS = [(x_single(i, p), tuple(sorted((i, j)))) for i in range(N_F) for p in ((1, 0), (0, 1)) for j in range(N_F) if j != i]  # 24 events
EVAL_QUERIES = [(x, s) for s in SCOPES for x in (0b11111111, 0b11110101, 0b01011111, 0b11010111)]  # unseen-pattern inputs
UNAFFECTED_PROBES = [(x, s) for s in SCOPES for x in (0b00010110, 0b01100001)]


class Learner:
    """Shared per-factor linear learner (exact solve from the three seen patterns): the semantic developmental state."""

    def __init__(self, M):
        self.M = M
        for i in range(N_F):
            M.declare(f"a{i}", "fx", 0); M.declare(f"c{i}", "fx", 0); M.declare(f"n{i}", "fin", 0)
        M.declare_store("evidence")

    def observe(self, x, scope, y):
        M = self.M
        M.op("S_INSERT", "evidence", (x, scope), y)
        # credit assignment: with two factors per scope, solve from single-active-bit evidence when available
        for i in scope:
            other = [j for j in scope if j != i][0]
            b0, b1 = fbits(x, i); o0, o1 = fbits(x, other)
            est_other = clamp(M.op("ADD", M.op("MUL", M.read(f"a{other}"), fx(1.0) if o0 else 0), M.op("MUL", M.read(f"c{other}"), fx(1.0) if o1 else 0)))
            resid = M.op("SUB", y, est_other)
            if b0 and not b1: M.write(f"a{i}", resid); M.write(f"n{i}", M.op("INC", M.read(f"n{i}")))
            elif b1 and not b0: M.write(f"c{i}", resid); M.write(f"n{i}", M.op("INC", M.read(f"n{i}")))

    def value(self, i, x):
        M = self.M; b0, b1 = fbits(x, i)
        return clamp(M.op("ADD", M.op("MUL", M.read(f"a{i}"), fx(1.0) if b0 else 0), M.op("MUL", M.read(f"c{i}"), fx(1.0) if b1 else 0)))

    def reset(self, factors):
        for i in factors:
            self.M.write(f"a{i}", 0); self.M.write(f"c{i}", 0); self.M.write(f"n{i}", 0)
        self.M.stores["evidence"] = [(k, v) for k, v in self.M.stores["evidence"] if not (set(k[1]) & set(factors))]
        self.M.op("S_DELETE", "evidence", None)

    def consistent(self, i):
        """verifier: the current factor model reproduces every stored evidence triple involving factor i (EQ ops charged)."""
        M = self.M; ok = 1
        for (x, scope), y in M.stores["evidence"]:
            if i in scope:
                pred = clamp(sum(self.value(j, x) for j in scope))
                ok = M.op("AND", ok, M.op("EQ", pred, y))
        return ok


class MonoCompiled:
    row = "MONO_C"

    def init(self, M):
        self.L = Learner(M); M.declare_store("table"); M.declare_program(6); self.built = False

    def _build(self, M):
        M.stores["table"] = []
        for x in range(256):
            for s in SCOPES:
                M.op("S_INSERT", "table", (x, s), clamp(sum(self.L.value(i, x) for i in s)))
        self.built = True

    def query(self, M, x, s):
        v = M.op("S_LOOKUP", "table", (x, s)); return 0 if v is None else v

    def feedback(self, M, x, s, y):
        self.L.observe(x, s, y); self._build(M)  # eager whole-table rebuild (alpha = 1)

    def revise(self, M, factors):
        self.L.reset(factors); self._build(M)


class ModularUnversioned:
    row = "MOD_U"

    def init(self, M):
        self.L = Learner(M); M.declare_store("ftab"); M.declare_program(8); self.stale = set(range(N_F))

    def _rebuild(self, M, i):
        M.stores["ftab"] = [(k, v) for k, v in M.stores["ftab"] if k[0] != i]
        for p in range(4):
            x = (p & 1) << (2 * i) | ((p >> 1) & 1) << (2 * i + 1)
            M.op("S_INSERT", "ftab", (i, p), self.L.value(i, x))
        self.stale.discard(i)

    def query(self, M, x, s):
        acc = 0
        for i in s:
            b0, b1 = fbits(x, i); v = M.op("S_LOOKUP", "ftab", (i, b0 | (b1 << 1))); acc = M.op("ADD", acc, 0 if v is None else v)
        return acc

    def feedback(self, M, x, s, y):
        self.L.observe(x, s, y); self.stale |= set(s)
        for i in sorted(self.stale): self._rebuild(M, i)  # eager local rebuild of the touched factors only

    def revise(self, M, factors):
        self.L.reset(factors); self.stale |= set(factors)
        for i in sorted(self.stale): self._rebuild(M, i)


class VLC(ModularUnversioned):
    row = "VLC"

    def init(self, M):
        super().init(M); M.declare_store("shadow"); self.rejected = 0

    def query(self, M, x, s):
        for i in s:
            if M.op("EQ", 1 if i in self.stale else 0, 1): return None  # invalid factor: abstain (flagged), never serve a stale/unverified version
        return super().query(M, x, s)

    def _rebuild(self, M, i):
        # shadow build, verify against evidence, adopt only if consistent (verify-before-swap); else keep the served version
        M.stores["shadow"] = []
        for p in range(4):
            x = (p & 1) << (2 * i) | ((p >> 1) & 1) << (2 * i + 1)
            M.op("S_INSERT", "shadow", (i, p), self.L.value(i, x))
        if self.L.consistent(i) and M.read(f"n{i}") >= 2:
            M.stores["ftab"] = [(k, v) for k, v in M.stores["ftab"] if k[0] != i] + list(M.stores["shadow"])
            M.op("S_INSERT", "ftab", (i, 99), 0); M.op("S_DELETE", "ftab", (i, 99))  # the atomic swap, charged as one write
            self.stale.discard(i)
        else:
            self.rejected += 1; M.op("AND", 0, 0)


class DenseNet:
    row = "DENSE"; H_UNITS = 4; LR = fx(0.25)

    def init(self, M):
        init = [0.5, -0.25, 0.75, -0.5, 0.25, 0.5, -0.75, 0.25, 0.5, -0.5, 0.25, 0.75, -0.25, 0.5, 0.25, -0.5, 0.125, -0.125, 0.375, -0.375, 0.625, -0.625, 0.875, -0.875]
        k = 0
        for j in range(self.H_UNITS):
            for i in range(12): M.declare(f"w{j}_{i}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"b{j}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"v{j}", "fx", fx(init[k % len(init)])); k += 1
        M.declare("c", "fx", 0); M.declare_store("examples"); M.declare_program(10 * self.H_UNITS + 2)
        self.names = list(M.cells); self._initial = {n: M.read(n) for n in self.names}

    def _inp(self, x, s):
        return [fx(1.0) if (x >> i) & 1 else 0 for i in range(8)] + [fx(1.0) if i in s else 0 for i in range(N_F)]

    def _forward(self, M, x, s):
        xb = self._inp(x, s); acts = []
        for j in range(self.H_UNITS):
            v = M.read(f"b{j}")
            for i in range(12): v = M.op("ADD", v, M.op("MUL", M.read(f"w{j}_{i}"), xb[i]))
            acts.append(M.op("THRESH", v))
        out = M.read("c")
        for j in range(self.H_UNITS): out = M.op("ADD", out, M.op("MUL", M.read(f"v{j}"), acts[j]))
        return out, acts, xb

    def query(self, M, x, s):
        return self._forward(M, x, s)[0]

    def _step(self, M, x, s, y):
        out, acts, xb = self._forward(M, x, s); err = M.op("SUB", out, y)
        mul = lambda a, b: M.op("MUL", a, b)
        M.write("c", clamp(M.read("c") - mul(self.LR, err)))
        for j in range(self.H_UNITS):
            M.write(f"v{j}", clamp(M.read(f"v{j}") - mul(self.LR, mul(err, acts[j]))))
            g = mul(err, M.read(f"v{j}")) if acts[j] > 0 else 0
            if g:
                M.write(f"b{j}", clamp(M.read(f"b{j}") - mul(self.LR, g)))
                for i in range(12): M.write(f"w{j}_{i}", clamp(M.read(f"w{j}_{i}") - mul(self.LR, mul(g, xb[i]))))

    def feedback(self, M, x, s, y):
        M.op("S_DELETE", "examples", (x, s)); M.op("S_INSERT", "examples", (x, s), y)
        self._step(M, x, s, y)
        for (ex, es), ey in list(M.stores["examples"]): self._step(M, ex, es, ey)  # one replay pass (charged)

    def revise(self, M, factors):
        M.stores["examples"] = [(k, v) for k, v in M.stores["examples"] if not (set(k[1]) & set(factors))]
        for n in self.names: M.write(n, self._initial[n])
        for _ in range(2):
            for (x, s), y in list(M.stores["examples"]): self._step(M, x, s, y)


class TripleMemory:
    row = "MEM"

    def init(self, M):
        M.declare_store("mem"); M.declare_program(3)

    def query(self, M, x, s):
        v = M.op("S_LOOKUP", "mem", (x, s)); return 0 if v is None else v

    def feedback(self, M, x, s, y):
        M.op("S_DELETE", "mem", (x, s)); M.op("S_INSERT", "mem", (x, s), y)

    def revise(self, M, factors):
        M.stores["mem"] = [(k, v) for k, v in M.stores["mem"] if not (set(k[1]) & set(factors))]; M.op("S_DELETE", "mem", None)


class TripleKNN(TripleMemory):
    row = "KNN"

    def query(self, M, x, s):
        best_d, acc, cnt = 99, 0, 0
        for (kx, ks), v in M.op("S_SCAN", "mem"):
            if ks != s: M.op("EQ", 0, 1); continue
            d = 0
            for i in range(8): d = M.op("ADD", d, M.op("XOR", (kx >> i) & 1, (x >> i) & 1))
            if M.op("GT", best_d, d): best_d, acc, cnt = d, v, 1
            elif M.op("EQ", d, best_d): acc = M.op("ADD", acc, v); cnt = M.op("INC", cnt)
        if cnt == 0: return 0
        while cnt > 1: acc = M.op("SHR", acc, 1); cnt = M.op("SHR", cnt, 1)
        return acc


ROWS = {"MONO_C": MonoCompiled, "MOD_U": ModularUnversioned, "VLC": VLC, "DENSE": DenseNet, "MEM": TripleMemory, "KNN": TripleKNN}
CELLS = {  # updates U, cone size, retention price lambda (per wrong answer served; abstention priced lambda/16), reuse horizon H
    "RSTAR": {"U": 8, "cone": 1, "lambda": 256, "H": 64},
    "T1_STATIONARY": {"U": 0, "cone": 1, "lambda": 256, "H": 64},
    "T2_DENSE_CONE": {"U": 8, "cone": 4, "lambda": 256, "H": 64},
    "T3_WEAK_RETENTION": {"U": 8, "cone": 1, "lambda": 0, "H": 64},
    "T4_SHORT_REUSE": {"U": 8, "cone": 1, "lambda": 256, "H": 2},
}


def run(row, basis, U, cone, seed=0):
    """One lifecycle: development, then U revision rounds (each: revise `cone` factors, 3 fresh feedback events per factor,
    probe the unaffected queries before/after to measure collateral regression). Returns per-phase charges, capability, regression."""
    ref = ROWS[row](); M = Machine(basis, seed=seed)
    coeffs = [(COEFF_VALUES[(2 * i) % 4], COEFF_VALUES[(2 * i + 1) % 4]) for i in range(N_F)]
    M.phase("exec"); ref.init(M)
    for x, s in DEV_EVENTS:
        M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
    M.phase("exec")
    for x, s in EVAL_QUERIES: ref.query(M, x, s)
    n_probe = 0; regress = 0; wrong = 0; abstain = 0
    for u in range(U):
        factors = [(u + j) % N_F for j in range(cone)]
        before = {q: ref.query(M, *q) for q in UNAFFECTED_PROBES if not (set(q[1]) & set(factors))}
        for i in factors: coeffs[i] = (COEFF_VALUES[(coeffs[i][0] // 4 + 1 + u) % 4], COEFF_VALUES[(coeffs[i][1] // 4 + 2 + u) % 4])
        M.phase("rev"); ref.revise(M, factors); M.end_event()
        affected = [q for q in EVAL_QUERIES if set(q[1]) & set(factors)]
        for i in factors:
            for p in ((1, 0), (0, 1), (0, 0)):
                x = x_single(i, p); j = (i + 1) % N_F; s = tuple(sorted((i, j)))
                M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
                M.phase("exec")  # served answers during the update window (exposure): wrong vs abstained, on affected scopes
                for q in affected:
                    v = ref.query(M, *q)
                    if v is None: abstain += 1
                    elif abs(v - truth(coeffs, *q)) > 1: wrong += 1
        M.phase("ver")
        for q, v in before.items():
            n_probe += 1; after = ref.query(M, *q); regress += 0 if (after is not None and M.op("EQ", after, v)) else 1
        M.phase("exec")
        for x, s in EVAL_QUERIES: ref.query(M, x, s)
    M.phase("exec"); final = {q: ref.query(M, *q) for q in EVAL_QUERIES}
    cap = sum(int(final[q] is not None and abs(final[q] - truth(coeffs, *q)) <= 1) for q in EVAL_QUERIES) / len(EVAL_QUERIES)
    n_q = len(EVAL_QUERIES) * (U + 1) + (U * 3 * cone * len(EVAL_QUERIES) // 2)
    desc_state = sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells) + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values())
    return {"row": row, "basis": basis.name, "U": U, "cone": cone, "R": dict(M.L.c), "desc_state": desc_state, "capability": round(cap, 4), "regressions": regress, "n_probes": n_probe,
            "wrong_served_in_window": wrong, "abstained_in_window": abstain,
            "per_query_exec": M.L.c["exec"] / n_q, "per_update": {k: (M.L.c[k] / U if U else 0) for k in ("upd", "ver", "rev")}, "regress_per_update": (regress / U if U else 0),
            "wrong_per_update": (wrong / U if U else 0), "abstain_per_update": (abstain / U if U else 0), "rejected_swaps": getattr(ref, "rejected", None)}


def lifecycle_cost(r, H, U, lam_wrong, lam_abstain=None):
    """C = desc(final state) + H exec_q + U (upd + ver + rev) + U (lam_wrong (regressions + wrong served) + lam_abstain abstentions)."""
    lam_abstain = lam_wrong / 16 if lam_abstain is None else lam_abstain
    return r["desc_state"] + H * r["per_query_exec"] + U * (r["per_update"]["upd"] + r["per_update"]["ver"] + r["per_update"]["rev"]) + U * (lam_wrong * (r["regress_per_update"] + r["wrong_per_update"]) + lam_abstain * r["abstain_per_update"])


def main(tag="V13_E1_VLC", seed=0):
    cols = list(bases.ALL); cells = {}
    for cell, spec in CELLS.items():
        for row in ROWS:
            for col in cols:
                cells[(cell, row, col)] = run(row, bases.ALL[col], spec["U"], spec["cone"], seed)
    out_cells = {}; frontier = {}; adm = {}
    for cell, spec in CELLS.items():
        for col in cols:
            rows_adm = [row for row in ROWS if cells[(cell, row, col)]["capability"] >= THETA]
            adm[f"{cell}|{col}"] = rows_adm
            costs = {row: lifecycle_cost(cells[(cell, row, col)], spec["H"], spec["U"], spec["lambda"]) for row in rows_adm}
            out_costs = costs
            if costs:
                cmin = min(costs.values()); frontier[f"{cell}|{col}"] = sorted(r for r, c in costs.items() if c <= cmin + 1e-9)
            else: frontier[f"{cell}|{col}"] = []
            # full (H, U) grid for the cell's cone/lambda
            for Hh in H_GRID:
                for Uu in U_GRID:
                    c2 = {row: lifecycle_cost(cells[(cell, row, col)], Hh, Uu, spec["lambda"]) for row in rows_adm}
                    if c2:
                        cmin = min(c2.values()); frontier[f"{cell}|{col}|H={Hh}|U={Uu}"] = sorted(r for r, c in c2.items() if c <= cmin + 1e-9)
    for (cell, row, col), r in cells.items():
        out_cells[f"{cell}|{row}|{col}"] = {k: v for k, v in r.items() if k not in ("row", "basis")}
    c2 = {f"{cell}|{row}": all(cells[(cell, row, col)]["capability"] == cells[(cell, row, cols[0])]["capability"] and cells[(cell, row, col)]["regressions"] == cells[(cell, row, cols[0])]["regressions"] and cells[(cell, row, col)]["wrong_served_in_window"] == cells[(cell, row, cols[0])]["wrong_served_in_window"] for col in cols) for cell in CELLS for row in ROWS}
    receipt = {"schema": "StageE1VLCV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "related": [418, 419], "revival_record": "RV-377-032", "run_tag": tag,
               "ecology": {"factors": N_F, "scopes": SCOPES, "seen_inputs": len(SEEN), "unseen_inputs": len(UNSEEN), "dev_events": len(DEV_EVENTS), "eval_queries": len(EVAL_QUERIES), "theta": THETA, "cells": CELLS},
               "rows": list(ROWS), "C2_capability_and_regression_column_invariant": c2, "cells": out_cells, "admissible": adm, "frontier": frontier,
               "claim_ceiling": "exact charged lifecycle at a 4-factor, 8-bit scope; the rows share one learner and differ only in materialization/serving/revision/verification organization; parent portfolio is the registered six rows, not the full E1 ladder"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("C2 all:", all(c2.values()))
    for cell in CELLS:
        print(cell, {row: (cells[(cell, row, cols[0])]["capability"], cells[(cell, row, cols[0])]["regressions"]) for row in ROWS}, "| frontier by col:", {c.split('_')[0]: frontier[f"{cell}|{c}"] for c in cols})
    return receipt


if __name__ == "__main__":
    main()
