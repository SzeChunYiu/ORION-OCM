"""RV-377-042: exact-layer ability test of the Codex-lane predicted form F3, the Verifier-Gated Speculative Compiler (VGSC:
cheap proposal -> isolated verification -> compiled serving; GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1 section 3, kill
condition VGSC_PHASE_DOES_NOT_RESPOND_TO_GENERATOR_VERIFIER_REUSE_PRICES).

Ecology: E_factored (four linear factors over bit pairs, scope-2 queries) with U = 16 revision rounds, one factor per round,
three fresh feedback events per round. Compilation is a SEARCH here (the learner stores evidence only; a factor's table is
compiled by enumerating the 16 coefficient pairs and verifying each against the factor's evidence), so that verifying one
candidate (c_v) is cheap relative to compiling (c_exact ~ up to 16 c_v). The revision process is a declared step sequence per
factor; a GENERATOR proposes 'the last step repeats' (c_g), which is right with frequency p_a fixed by the cell.
Rows:
  EXACT      keep serving the stale table during the update window; search-compile at the end of the round
  EXACT_ABS  abstain on affected scopes during the window (A4 semantics without speculation); search-compile at the end
  SPEC       adopt the generator's proposal at the revision signal without verification; never compile (unverified speculation)
  VGSC       proposal into a shadow at the revision signal; abstain until the first feedback event verifies it (then serve it);
             a later contradicting event rolls it back to abstention; search-compile at the end only if the proposal failed
Cells: p_a in {0, 0.25, 0.5, 0.75, 1.0} x retention price lambda in {0, 16, 256}; headline H = 64; six registered columns.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

from . import bases
from .core import Machine, clamp, fx, sha256_of
from .e1_vlc import COEFF_VALUES, DEV_EVENTS, EVAL_QUERIES, N_F, SCOPES, fbits, truth, x_single, lifecycle_cost

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
U_ROUNDS = 16
H_HEAD = 64
CANDIDATES = list(itertools.product(COEFF_VALUES, COEFF_VALUES))  # 16 coefficient pairs, fixed enumeration order
# declared step sequences (index steps mod 4, applied to both coefficients of the revised factor at its k-th revision);
# the generator predicts 'same step as last time' (default +1 before any history), so p_a = fraction of right predictions
STEP_SEQ = {"PA100": (1, 1, 1, 1), "PA075": (1, 1, 1, 2), "PA050": (1, 1, 2, 1), "PA025": (1, 2, 1, 2), "PA000": (2, 1, 2, 1)}
P_A = {"PA100": 1.0, "PA075": 0.75, "PA050": 0.5, "PA025": 0.25, "PA000": 0.0}
LAMBDAS = {"L0": 0, "L16": 16, "L256": 256}


class EvidenceLearner:
    """stores evidence; holds the compiled coefficient cells a_i, c_i (written by the compiler or the generator), the previous
    adopted values pa_i, pc_i (generator history) and the verifier consistent(i)."""

    def __init__(self, M):
        self.M = M
        for i in range(N_F):
            M.declare(f"a{i}", "fx", 0); M.declare(f"c{i}", "fx", 0); M.declare(f"pa{i}", "fx", 0); M.declare(f"pc{i}", "fx", 0)
        M.declare_store("evidence")

    def observe(self, x, scope, y):
        self.M.op("S_INSERT", "evidence", (x, scope), y)

    def value(self, i, x):
        M = self.M; b0, b1 = fbits(x, i)
        return clamp(M.op("ADD", M.op("MUL", M.read(f"a{i}"), fx(1.0) if b0 else 0), M.op("MUL", M.read(f"c{i}"), fx(1.0) if b1 else 0)))

    def forget(self, i):
        self.M.stores["evidence"] = [(k, v) for k, v in self.M.stores["evidence"] if i not in k[1]]
        self.M.op("S_DELETE", "evidence", None)

    def consistent(self, i):
        M = self.M; ok = 1
        for (x, scope), y in M.stores["evidence"]:
            if i in scope and fbits(x, i) != (0, 0):  # evidence in which factor i is active (single-active events: the other factor contributes 0)
                pred = clamp(sum(self.value(j, x) for j in scope)); ok = M.op("AND", ok, M.op("EQ", pred, y))
        return ok

    def set_coeffs(self, i, a, c, remember=True):
        M = self.M
        if remember: M.write(f"pa{i}", M.read(f"a{i}")); M.write(f"pc{i}", M.read(f"c{i}"))
        M.write(f"a{i}", a); M.write(f"c{i}", c)

    def propose(self, i):
        """generator: repeat the last step in value space (wrap 1.0 -> 0.25); default step +0.25 before any history."""
        M = self.M; out = []
        for cur, prev in ((f"a{i}", f"pa{i}"), (f"c{i}", f"pc{i}")):
            step = M.op("SUB", M.read(cur), M.read(prev)) if M.read(prev) else fx(0.25)
            if M.op("GT", 0, step): step = M.op("ADD", step, fx(1.0))
            v = M.op("ADD", M.read(cur), step)
            if M.op("GT", v, fx(1.0)): v = M.op("SUB", v, fx(1.0))
            out.append(v)
        return out[0], out[1]

    def search_compile(self, i):
        """exact compiler: enumerate the 16 candidates in fixed order, adopt the first consistent with the factor's evidence."""
        M = self.M; a_old, c_old = M.read(f"a{i}"), M.read(f"c{i}"); tried = 0
        for a, c in CANDIDATES:
            M.write(f"a{i}", a); M.write(f"c{i}", c); tried += 1
            if self.consistent(i):
                M.write(f"pa{i}", a_old); M.write(f"pc{i}", c_old); return tried
        M.write(f"a{i}", a_old); M.write(f"c{i}", c_old); return tried


class Exact:
    row = "EXACT"; abstain_in_window = False

    def init(self, M):
        self.L = EvidenceLearner(M); M.declare_store("ftab"); M.declare_program(8); self.stale = set(); self.searches = 0; self.candidates_tried = 0

    def _table(self, M, i):
        M.stores["ftab"] = [(k, v) for k, v in M.stores["ftab"] if k[0] != i]
        for p in range(4):
            x = (p & 1) << (2 * i) | ((p >> 1) & 1) << (2 * i + 1); M.op("S_INSERT", "ftab", (i, p), self.L.value(i, x))

    def _compile(self, M, i):
        self.searches += 1; self.candidates_tried += self.L.search_compile(i); self._table(M, i); self.stale.discard(i)

    def query(self, M, x, s):
        if self.abstain_in_window:
            for i in s:
                if M.op("EQ", 1 if i in self.stale else 0, 1): return None
        acc = 0
        for i in s:
            b0, b1 = fbits(x, i); v = M.op("S_LOOKUP", "ftab", (i, b0 | (b1 << 1))); acc = M.op("ADD", acc, 0 if v is None else v)
        return acc

    def develop(self, M, events):
        for x, s, y in events: self.L.observe(x, s, y)
        for i in range(N_F): self._compile(M, i)

    def revise(self, M, i):
        self.L.forget(i); self.stale.add(i)

    def feedback(self, M, x, s, y):
        self.L.observe(x, s, y)

    def end_round(self, M, i):
        if i in self.stale: self._compile(M, i)


class ExactAbstain(Exact):
    row = "EXACT_ABS"; abstain_in_window = True


class Spec(Exact):
    row = "SPEC"; abstain_in_window = False

    def revise(self, M, i):
        self.L.forget(i); a, c = self.L.propose(i); self.L.set_coeffs(i, a, c); self._table(M, i)  # unverified adoption

    def end_round(self, M, i): pass


class VGSC(Exact):
    row = "VGSC"; abstain_in_window = True

    def init(self, M):
        super().init(M); M.declare("sha", "fx", 0); M.declare("shc", "fx", 0); self.proposal = {}; self.adopted = set(); self.failed = set(); self.n_verify = 0; self.rollbacks = 0

    def revise(self, M, i):
        self.L.forget(i); self.stale.add(i); a, c = self.L.propose(i); M.write("sha", a); M.write("shc", c); self.proposal[i] = (a, c)

    def feedback(self, M, x, s, y):
        self.L.observe(x, s, y)
        for i in list(self.proposal):
            if i in self.failed: continue
            a_old, c_old = M.read(f"a{i}"), M.read(f"c{i}"); self.L.set_coeffs(i, M.read("sha"), M.read("shc"), remember=False)
            self.n_verify += 1; ok = self.L.consistent(i)
            if ok:
                if i not in self.adopted: self.adopted.add(i); M.write(f"pa{i}", a_old); M.write(f"pc{i}", c_old); self._table(M, i); self.stale.discard(i)
            else:
                self.L.set_coeffs(i, a_old, c_old, remember=False)
                if i in self.adopted: self.adopted.discard(i); self.rollbacks += 1
                self.failed.add(i); self.stale.add(i)

    def end_round(self, M, i):
        if i in self.stale: self._compile(M, i)
        self.proposal.pop(i, None); self.adopted.discard(i); self.failed.discard(i)


ROWS = {"EXACT": Exact, "EXACT_ABS": ExactAbstain, "SPEC": Spec, "VGSC": VGSC}


def run(row, basis, pa_cell, seed=0):
    ref = ROWS[row](); M = Machine(basis, seed=seed); steps = STEP_SEQ[pa_cell]
    idx = [[(2 * i) % 4, (2 * i + 1) % 4] for i in range(N_F)]
    coeffs = [(COEFF_VALUES[idx[i][0]], COEFF_VALUES[idx[i][1]]) for i in range(N_F)]
    M.phase("exec"); ref.init(M)
    M.phase("upd"); ref.develop(M, [(x, s, truth(coeffs, x, s)) for x, s in DEV_EVENTS]); M.end_event()
    dev = dict(M.L.c)
    M.phase("exec")
    for x, s in EVAL_QUERIES: ref.query(M, x, s)
    wrong = 0; abstain = 0; n_q = len(EVAL_QUERIES); k = [0] * N_F
    for u in range(U_ROUNDS):
        i = u % N_F; st = steps[k[i]]; k[i] += 1
        idx[i] = [(idx[i][0] + st) % 4, (idx[i][1] + st) % 4]; coeffs[i] = (COEFF_VALUES[idx[i][0]], COEFF_VALUES[idx[i][1]])
        M.phase("rev"); ref.revise(M, i); M.end_event()
        affected = [q for q in EVAL_QUERIES if i in q[1]]
        for p in ((1, 0), (0, 1), (0, 0)):
            x = x_single(i, p); s = tuple(sorted((i, (i + 1) % N_F)))
            M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
            M.phase("exec")
            for q in affected:
                v = ref.query(M, *q); n_q += 1
                if v is None: abstain += 1
                elif abs(v - truth(coeffs, *q)) > 1: wrong += 1
        M.phase("upd"); ref.end_round(M, i); M.end_event()
        M.phase("exec")
        for x, s in EVAL_QUERIES: ref.query(M, x, s); n_q += 1
    M.phase("exec"); final = {q: ref.query(M, *q) for q in EVAL_QUERIES}
    cap = sum(int(final[q] is not None and abs(final[q] - truth(coeffs, *q)) <= 1) for q in EVAL_QUERIES) / len(EVAL_QUERIES)
    desc_state = sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells) + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values())
    R = dict(M.L.c); U = U_ROUNDS
    return {"row": row, "basis": basis.name, "pa_cell": pa_cell, "p_a": P_A[pa_cell], "R": R, "R_development": dev, "desc_state": desc_state, "capability": round(cap, 4),
            "wrong_served_in_window": wrong, "abstained_in_window": abstain, "per_query_exec": R["exec"] / n_q,
            "per_update": {kk: (R[kk] - dev.get(kk, 0)) / U for kk in ("upd", "ver", "rev")}, "per_update_incl_dev": {kk: R[kk] / U for kk in ("upd", "ver", "rev")},
            "regress_per_update": 0.0, "wrong_per_update": wrong / U, "abstain_per_update": abstain / U,
            "searches": ref.searches, "candidates_tried": ref.candidates_tried, "n_verify": getattr(ref, "n_verify", None), "rollbacks": getattr(ref, "rollbacks", None)}


def main(tag="V21_E1_VGSC", seed=0, columns=None):
    cols = columns or dict(bases.ALL); cells = {}
    for pa in STEP_SEQ:
        for row in ROWS:
            for col in cols: cells[(pa, row, col)] = run(row, cols[col], pa, seed)
    frontier = {}; adm = {}
    for pa in STEP_SEQ:
        for col in cols:
            rows_adm = [r for r in ROWS if cells[(pa, r, col)]["capability"] >= THETA]; adm[f"{pa}|{col}"] = rows_adm
            for lname, lam in LAMBDAS.items():
                for H in (H_HEAD, 4, 128):
                    costs = {r: lifecycle_cost(cells[(pa, r, col)], H, U_ROUNDS, lam) for r in rows_adm}
                    frontier[f"{pa}|{lname}|H={H}|{col}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []
    c2 = {f"{pa}|{row}": len({(cells[(pa, row, col)]["capability"], cells[(pa, row, col)]["wrong_served_in_window"], cells[(pa, row, col)]["abstained_in_window"]) for col in cols}) == 1 for pa in STEP_SEQ for row in ROWS}
    receipt = {"schema": "StageE1VGSCV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "revival_record": "RV-377-042", "run_tag": tag, "codex_form": "F3 VGSC (GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1)",
               "cells_spec": {"step_sequences": STEP_SEQ, "p_a": P_A, "lambdas": LAMBDAS, "U": U_ROUNDS, "H_head": H_HEAD, "candidates": len(CANDIDATES)}, "rows": list(ROWS), "C2": c2,
               "cells": {f"{pa}|{row}|{col}": {k: v for k, v in r.items() if k not in ("row", "basis", "pa_cell")} for (pa, row, col), r in cells.items()}, "admissible": adm, "frontier": frontier,
               "claim_ceiling": "exact charged lifecycle at scope; generator and compiler declared; one seed (all rows deterministic)"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("C2 all:", all(c2.values()))
    c0 = list(cols)[0]
    for pa in STEP_SEQ:
        print(pa, {row: (cells[(pa, row, c0)]["capability"], cells[(pa, row, c0)]["wrong_served_in_window"], cells[(pa, row, c0)]["abstained_in_window"], round(cells[(pa, row, c0)]["per_update"]["upd"] + cells[(pa, row, c0)]["per_update"]["rev"])) for row in ROWS})
        print("   frontier H=64:", {f"{l}|{c.split('_')[0]}": frontier[f"{pa}|{l}|H=64|{c}"] for l in LAMBDAS for c in cols})
    return receipt


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calib":
        B0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; main(tag="CALIB_VGSC_B0", columns={B0: bases.ALL[B0]})
    else:
        main()
