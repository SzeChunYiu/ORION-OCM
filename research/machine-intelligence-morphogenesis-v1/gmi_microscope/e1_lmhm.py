"""RV-377-043: exact-layer ability test of the Codex-lane predicted form F5, the Locally Morphogenetic Heterogeneous Mesh
(LMHM: the morphogenesis operator acts factor-locally, so each factor of a served state may take its own realization family
according to its LOCAL demand; GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1 section 3, kill condition
LOCAL_DEMAND_SIGNATURE_DOES_NOT_PREDICT_LOCAL_MORPHOGENESIS).

Ecology: E_factored (four linear factors, scope-2 queries) with HETEROGENEOUS per-factor revision regimes over U = 16 rounds:
factor 0 revised every round (16), factor 2 every 4th round (4), factor 3 every 8th round (2), factor 1 never (0).
Realization families per factor: C = compiled table rebuilt eagerly and served unverified (MOD_U's mechanism);
V = shadow build, verify-before-swap, abstain while unverified (VLC's mechanism). A mesh is a V-set (which factors are V):
16 meshes; ALL_C = MOD_U, ALL_V = VLC, the others are heterogeneous. The frontier over the 16 meshes at each retention
price lambda tests whether the per-factor (local) demand — exposure = wrong answers a C-factor serves per lifecycle — predicts
the winning mesh by the per-factor rule 'V iff lambda x exposure_f > verification overhead_f' (additivity across factors).
"""
from __future__ import annotations

import itertools
import json
import os
import sys

from . import bases
from .core import Machine, sha256_of
from .e1_vlc import DEV_EVENTS, EVAL_QUERIES, N_F, COEFF_VALUES, Learner, fbits, truth, x_single, lifecycle_cost

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
U_ROUNDS = 16
H_HEAD = 64
REVISION_PERIOD = {0: 1, 1: 0, 2: 4, 3: 8}  # factor -> revised every k-th round (0 = never)
LAMBDAS = [0, 16, 64, 256, 1024, 4096]
MESHES = {"".join("V" if f in vs else "C" for f in range(N_F)): frozenset(vs) for k in range(N_F + 1) for vs in itertools.combinations(range(N_F), k)}


def revised_at(u):
    return [f for f, k in REVISION_PERIOD.items() if k and u % k == 0]


class Mesh:
    def __init__(self, vset):
        self.vset = frozenset(vset); self.row = "".join("V" if f in self.vset else "C" for f in range(N_F))

    def init(self, M):
        self.L = Learner(M); M.declare_store("ftab"); M.declare_program(8); self.stale = set(range(N_F)); self.rejected = 0
        if self.vset: M.declare_store("shadow")

    def _plain(self, M, i):
        M.stores["ftab"] = [(k, v) for k, v in M.stores["ftab"] if k[0] != i]
        for p in range(4):
            x = (p & 1) << (2 * i) | ((p >> 1) & 1) << (2 * i + 1); M.op("S_INSERT", "ftab", (i, p), self.L.value(i, x))
        self.stale.discard(i)

    def _verified(self, M, i):
        M.stores["shadow"] = []
        for p in range(4):
            x = (p & 1) << (2 * i) | ((p >> 1) & 1) << (2 * i + 1); M.op("S_INSERT", "shadow", (i, p), self.L.value(i, x))
        if self.L.consistent(i) and M.read(f"n{i}") >= 2:
            M.stores["ftab"] = [(k, v) for k, v in M.stores["ftab"] if k[0] != i] + list(M.stores["shadow"])
            M.op("S_INSERT", "ftab", (i, 99), 0); M.op("S_DELETE", "ftab", (i, 99)); self.stale.discard(i)
        else:
            self.rejected += 1; M.op("AND", 0, 0)

    def _rebuild(self, M, i):
        (self._verified if i in self.vset else self._plain)(M, i)

    def query(self, M, x, s):
        for i in s:
            if i in self.vset and M.op("EQ", 1 if i in self.stale else 0, 1): return None  # a V-factor abstains while unverified
        acc = 0
        for i in s:
            b0, b1 = fbits(x, i); v = M.op("S_LOOKUP", "ftab", (i, b0 | (b1 << 1))); acc = M.op("ADD", acc, 0 if v is None else v)
        return acc

    def feedback(self, M, x, s, y):
        self.L.observe(x, s, y); self.stale |= set(s)
        for i in sorted(self.stale): self._rebuild(M, i)

    def revise(self, M, factors):
        self.L.reset(factors); self.stale |= set(factors)
        for i in sorted(self.stale): self._rebuild(M, i)


def run(mesh, basis, seed=0):
    ref = Mesh(MESHES[mesh]); M = Machine(basis, seed=seed)
    coeffs = [(COEFF_VALUES[(2 * i) % 4], COEFF_VALUES[(2 * i + 1) % 4]) for i in range(N_F)]
    M.phase("exec"); ref.init(M)
    for x, s in DEV_EVENTS:
        M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
    M.phase("exec")
    for x, s in EVAL_QUERIES: ref.query(M, x, s)
    wrong = 0; abstain = 0; n_q = len(EVAL_QUERIES); wrong_f = {f: 0 for f in range(N_F)}; abst_f = {f: 0 for f in range(N_F)}; n_rev = {f: 0 for f in range(N_F)}
    for u in range(U_ROUNDS):
        factors = revised_at(u)
        for i in factors: coeffs[i] = (COEFF_VALUES[(coeffs[i][0] // 4 + 1 + u) % 4], COEFF_VALUES[(coeffs[i][1] // 4 + 2 + u) % 4]); n_rev[i] += 1
        M.phase("rev"); ref.revise(M, factors); M.end_event()
        for i in factors:
            affected = [q for q in EVAL_QUERIES if i in q[1]]
            for p in ((1, 0), (0, 1), (0, 0)):
                x = x_single(i, p); s = tuple(sorted((i, (i + 1) % N_F)))
                M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
                M.phase("exec")
                for q in affected:
                    v = ref.query(M, *q); n_q += 1
                    if v is None: abstain += 1; abst_f[i] += 1
                    elif abs(v - truth(coeffs, *q)) > 1: wrong += 1; wrong_f[i] += 1
        M.phase("exec")
        for x, s in EVAL_QUERIES: ref.query(M, x, s); n_q += 1
    M.phase("exec"); final = {q: ref.query(M, *q) for q in EVAL_QUERIES}
    cap = sum(int(final[q] is not None and abs(final[q] - truth(coeffs, *q)) <= 1) for q in EVAL_QUERIES) / len(EVAL_QUERIES)
    desc_state = sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells) + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values())
    R = dict(M.L.c); U = U_ROUNDS
    return {"mesh": mesh, "basis": basis.name, "R": R, "desc_state": desc_state, "capability": round(cap, 4), "wrong_served_in_window": wrong, "abstained_in_window": abstain,
            "wrong_by_revised_factor": wrong_f, "abstained_by_revised_factor": abst_f, "revisions_by_factor": n_rev, "rejected_swaps": ref.rejected, "regressions": 0,
            "per_query_exec": R["exec"] / n_q, "per_update": {k: R[k] / U for k in ("upd", "ver", "rev")}, "regress_per_update": 0.0, "wrong_per_update": wrong / U, "abstain_per_update": abstain / U}


def main(tag="V23_E1_LMHM", seed=0, columns=None):
    cols = columns or dict(bases.ALL); cells = {}
    for mesh in MESHES:
        for col in cols: cells[(mesh, col)] = run(mesh, cols[col], seed)
    frontier = {}; additivity = {}
    for col in cols:
        base = cells[("CCCC", col)]
        for lam in LAMBDAS:
            for H in (4, H_HEAD, 128):
                costs = {m: lifecycle_cost(cells[(m, col)], H, U_ROUNDS, lam) for m in MESHES if cells[(m, col)]["capability"] >= THETA}
                frontier[f"{col}|lambda={lam}|H={H}"] = sorted(m for m, c in costs.items() if c <= min(costs.values()) + 1e-9)
            # additivity: delta cost of a mesh vs the sum of its single-V deltas (headline H)
            single = {f: lifecycle_cost(cells[("".join("V" if g == f else "C" for g in range(N_F)), col)], H_HEAD, U_ROUNDS, lam) - lifecycle_cost(base, H_HEAD, U_ROUNDS, lam) for f in range(N_F)}
            for m, vs in MESHES.items():
                if len(vs) >= 2:
                    d_obs = lifecycle_cost(cells[(m, col)], H_HEAD, U_ROUNDS, lam) - lifecycle_cost(base, H_HEAD, U_ROUNDS, lam); d_sum = sum(single[f] for f in vs)
                    additivity[f"{col}|lambda={lam}|{m}"] = {"delta_observed": d_obs, "delta_sum_of_singles": d_sum, "interaction": d_obs - d_sum, "base_cost": lifecycle_cost(base, H_HEAD, U_ROUNDS, lam)}
    c2 = {m: len({(cells[(m, col)]["capability"], cells[(m, col)]["wrong_served_in_window"], cells[(m, col)]["abstained_in_window"]) for col in cols}) == 1 for m in MESHES}
    receipt = {"schema": "StageE1LMHMV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "revival_record": "RV-377-043", "run_tag": tag, "codex_form": "F5 LMHM (GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1)",
               "cells_spec": {"revision_period_by_factor": REVISION_PERIOD, "U": U_ROUNDS, "H_head": H_HEAD, "lambdas": LAMBDAS, "meshes": sorted(MESHES)}, "C2": c2,
               "cells": {f"{m}|{col}": {k: v for k, v in r.items() if k not in ("mesh", "basis")} for (m, col), r in cells.items()}, "frontier": frontier, "additivity": additivity,
               "claim_ceiling": "exact charged lifecycle at scope; two realization families per factor; one seed (deterministic rows)"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("C2 all:", all(c2.values()))
    for col in cols:
        print("==", col.split("_")[0], "wrong/abst by factor (CCCC / VVVV):", cells[("CCCC", col)]["wrong_by_revised_factor"], cells[("VVVV", col)]["abstained_by_revised_factor"])
        for lam in LAMBDAS: print("   lambda", lam, "frontier H=4/64/128:", [frontier[f"{col}|lambda={lam}|H={H}"] for H in (4, H_HEAD, 128)])
    return receipt


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calib":
        cs = {c: bases.ALL[c] for c in bases.ALL if c.startswith(("B0", "B2"))}; main(tag="CALIB_LMHM", columns=cs)
    else:
        main()
