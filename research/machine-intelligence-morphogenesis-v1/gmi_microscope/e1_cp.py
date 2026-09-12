"""RV-377-033: E1 at the exact charged layer for the ChatGPT-lane Cognitive Polyphenism prediction (#409 / #410,
COGNITIVE_POLYPHENISM_PREDICTION_V1, GMI_CP_E1_PARENT_FRONTIER_PROTOCOL_V1). Tests the CP ability vector B1-B4
(GMI_THEORY_CORE_V3_EXECUTED section 5.2) with real learning, compilation, revision and versioning under the frozen cost model.

Ecology E_factored3 (declared): the E_factored world of e1_vlc.py (four linear factors over own bit pairs, 2-factor scopes) served
through THREE regimes that share the same latent factors:
  A  EXACT    answer = sum of the scope's factor values (exact within 1/16)
  B  BOOL     answer = 1 if the sum exceeds 0.75, else 0
  C  ARGMAX   answer = index (0/1) of the larger factor value in the scope (0 on ties)
Development feedback arrives ONLY in regime A (exact labels); regimes B and C are queried but never labelled, so regime-B/C
capability measures CROSS-REGIME TRANSFER through shared developmental state (CP-5 / ability B1). U revision rounds redefine one
factor and are followed by three regime-A feedback events. Capability = mean over the three regimes of the exact fraction on the 24
unseen-pattern queries (theta 0.85); a row is admissible only if EVERY regime's fraction is >= theta.
Episodes: each of the U + 1 serving windows activates the regimes listed in the cell (sparse: one regime per window, cycling;
dense: all three every window); a phenotype is only ever needed for an active regime.

Rows (same learner as e1_vlc.Learner = the authoritative source; rows differ in organization):
  INTERP   single broad realization: every query interprets the source (arithmetic per query, no phenotype tables)
  EAGER    source + three compiled phenotype tables (per-factor tables for A; per-scope Boolean/argmax tables for B/C over the
           81 seen + 175 unseen inputs = 256 x 6 entries each) rebuilt for ALL regimes after every source update
  CP       source + version tag; each phenotype carries the source version it was compiled from and is rebuilt LAZILY on the
           first query of its regime after a source update (only active regimes are ever rebuilt); a stale phenotype never serves
  INDEP    three independent learners, one per regime, each fed only its own regime's labels (regimes B/C get none): the
           no-sharing control (predicted inadmissible in B/C)
"""
from __future__ import annotations

import json
import os

from . import bases
from .core import Machine, clamp, fx, sha256_of
from .e1_vlc import DEV_EVENTS, EVAL_QUERIES, N_F, SCOPES, Learner, fbits, truth, x_single

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85; TAU = fx(0.75)
COEFF_VALUES = [fx(v) for v in (0.25, 0.5, 0.75, 1.0)]
REGIMES = ("A", "B", "C")


def truth_regime(coeffs, x, s, regime):
    if regime == "A": return truth(coeffs, x, s)
    if regime == "B": return 1 if truth(coeffs, x, s) > TAU else 0
    a, b = s; va = clamp(coeffs[a][0] * fbits(x, a)[0] + coeffs[a][1] * fbits(x, a)[1]); vb = clamp(coeffs[b][0] * fbits(x, b)[0] + coeffs[b][1] * fbits(x, b)[1])
    return 1 if vb > va else 0


class Interp:
    row = "INTERP"

    def init(self, M):
        self.L = Learner(M); M.declare_program(6)

    def _sum(self, M, x, s):
        return clamp(sum(self.L.value(i, x) for i in s))

    def query(self, M, x, s, regime):
        if regime == "A": return self._sum(M, x, s)
        if regime == "B": return 1 if M.op("GT", self._sum(M, x, s), TAU) else 0
        a, b = s; return 1 if M.op("GT", self.L.value(b, x), self.L.value(a, x)) else 0

    def feedback(self, M, x, s, y, regime):
        if regime == "A": self.L.observe(x, s, y)

    def revise(self, M, factors):
        self.L.reset(factors)

    def end_round(self, M):
        pass


class Eager(Interp):
    row = "EAGER"

    def init(self, M):
        self.L = Learner(M); M.declare_program(10)
        for r in REGIMES: M.declare_store(f"ph{r}")
        self.built = {r: False for r in REGIMES}

    def _compile(self, M, regime):
        M.stores[f"ph{regime}"] = []
        if regime == "A":
            for i in range(N_F):
                for p in range(4): M.op("S_INSERT", f"ph{regime}", (i, p), self.L.value(i, x_single(i, (p & 1, p >> 1))))
        else:
            for x in range(256):
                for s in SCOPES: M.op("S_INSERT", f"ph{regime}", (x, s), Interp.query(self, M, x, s, regime))
        self.built[regime] = True

    def query(self, M, x, s, regime):
        if not self.built[regime]: M.phase("upd"); self._compile(M, regime); M.phase("exec")
        if regime == "A":
            acc = 0
            for i in s:
                b0, b1 = fbits(x, i); v = M.op("S_LOOKUP", "phA", (i, b0 | (b1 << 1))); acc = M.op("ADD", acc, 0 if v is None else v)
            return acc
        v = M.op("S_LOOKUP", f"ph{regime}", (x, s)); return 0 if v is None else v

    def end_round(self, M):
        for r in REGIMES: self._compile(M, r)  # eager: every phenotype rebuilt at the end of each update round

    def feedback(self, M, x, s, y, regime):
        if regime == "A": self.L.observe(x, s, y)

    def revise(self, M, factors):
        self.L.reset(factors)
        for r in REGIMES: self.built[r] = False


class CP(Eager):
    row = "CP"

    def init(self, M):
        super().init(M); M.declare("version", "fin", 0)
        for r in REGIMES: M.declare(f"tag{r}", "fin", -1)
        self.rebuilds = 0

    def query(self, M, x, s, regime):
        if not M.op("EQ", M.read(f"tag{regime}"), M.read("version")):  # stale or never compiled: rebuild THIS phenotype only, now
            M.phase("upd"); self._compile(M, regime); M.write(f"tag{regime}", M.read("version")); self.rebuilds += 1; M.phase("exec")  # rebuild work is charged as update work, not serving
        return Eager.query(self, M, x, s, regime)

    def end_round(self, M):
        M.write("version", M.op("INC", M.read("version")))  # lazy: nothing rebuilt until a regime is queried

    def revise(self, M, factors):
        self.L.reset(factors)


class Indep(Interp):
    row = "INDEP"

    def init(self, M):
        self.L = Learner(M); M.declare_program(8)
        for r in ("B", "C"): M.declare_store(f"mem{r}")  # regimes B/C: independent exact memories fed only their own labels

    def query(self, M, x, s, regime):
        if regime == "A": return self._sum(M, x, s)
        v = M.op("S_LOOKUP", f"mem{regime}", (x, s)); return 0 if v is None else v

    def feedback(self, M, x, s, y, regime):
        if regime == "A": self.L.observe(x, s, y)
        else: M.op("S_DELETE", f"mem{regime}", (x, s)); M.op("S_INSERT", f"mem{regime}", (x, s), y)

    def revise(self, M, factors):
        self.L.reset(factors)
        for r in ("B", "C"): M.stores[f"mem{r}"] = [(k, v) for k, v in M.stores[f"mem{r}"] if not (set(k[1]) & set(factors))]


ROWS = {"INTERP": Interp, "EAGER": Eager, "CP": CP, "INDEP": Indep}
CELLS = {
    "PPLUS": {"regimes": REGIMES, "active_per_window": 1, "U": 8, "H": 64, "shared": True},
    "N1_ONE_REGIME": {"regimes": ("A",), "active_per_window": 1, "U": 8, "H": 64, "shared": True},
    "N2_DENSE_ACTIVITY": {"regimes": REGIMES, "active_per_window": 3, "U": 8, "H": 64, "shared": True},
    "N3_NO_SHARED_SEMANTICS": {"regimes": REGIMES, "active_per_window": 1, "U": 8, "H": 64, "shared": False},
}


def run(row, basis, spec, seed=0):
    ref = ROWS[row](); M = Machine(basis, seed=seed)
    coeffs = [(COEFF_VALUES[(2 * i) % 4], COEFF_VALUES[(2 * i + 1) % 4]) for i in range(N_F)]
    # N3: regimes B and C are generated from INDEPENDENT latent coefficients (no shared semantics)
    coeffs_alt = [(COEFF_VALUES[(3 - i) % 4], COEFF_VALUES[(2 + 3 * i) % 4]) for i in range(N_F)]
    def tr(x, s, regime):
        return truth_regime(coeffs if (spec["shared"] or regime == "A") else coeffs_alt, x, s, regime)
    regimes = spec["regimes"]
    M.phase("exec"); ref.init(M)
    for x, s in DEV_EVENTS:
        M.phase("upd"); ref.feedback(M, x, s, tr(x, s, "A"), "A")
        if row == "INDEP":
            for r in regimes:
                if r != "A": ref.feedback(M, x, s, tr(x, s, r), r)
        M.end_event()
    M.phase("upd"); ref.end_round(M); M.end_event()
    n_q = 0; windows = spec["U"] + 1
    for w in range(windows):
        active = [regimes[(w + k) % len(regimes)] for k in range(spec["active_per_window"])] if len(regimes) > 1 else list(regimes)
        M.phase("exec")
        for r in active:
            for x, s in EVAL_QUERIES: ref.query(M, x, s, r); n_q += 1
        if w < spec["U"]:
            i = w % N_F
            coeffs[i] = (COEFF_VALUES[(coeffs[i][0] // 4 + 1 + w) % 4], COEFF_VALUES[(coeffs[i][1] // 4 + 2 + w) % 4])
            if not spec["shared"]: coeffs_alt[i] = (COEFF_VALUES[(coeffs_alt[i][0] // 4 + 3 + w) % 4], COEFF_VALUES[(coeffs_alt[i][1] // 4 + 1 + w) % 4])
            M.phase("rev"); ref.revise(M, [i]); M.end_event()
            for p in ((1, 0), (0, 1), (0, 0)):
                x = x_single(i, p); s = tuple(sorted((i, (i + 1) % N_F)))
                M.phase("upd"); ref.feedback(M, x, s, tr(x, s, "A"), "A")
                if row == "INDEP":
                    for r in regimes:
                        if r != "A": ref.feedback(M, x, s, tr(x, s, r), r)
                M.end_event()
            M.phase("upd"); ref.end_round(M); M.end_event()
    M.phase("ver")
    caps = {}
    for r in regimes:
        ok = 0
        for x, s in EVAL_QUERIES:
            v = ref.query(M, x, s, r); t = tr(x, s, r)
            ok += int(v is not None and abs(v - t) <= (1 if r == "A" else 0))
        caps[r] = round(ok / len(EVAL_QUERIES), 4)
    desc_state = sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells) + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values())
    R = dict(M.L.c); U = spec["U"]
    return {"row": row, "basis": basis.name, "capability_by_regime": caps, "admissible": all(c >= THETA for c in caps.values()), "desc_state": desc_state, "R": R,
            "per_query_exec": R["exec"] / n_q, "per_update": {k: (R[k] / U if U else 0) for k in ("upd", "rev")}, "verify": R["ver"], "rebuilds": getattr(ref, "rebuilds", None)}


def lifecycle_cost(r, H, U):
    return r["desc_state"] + H * r["per_query_exec"] + U * (r["per_update"]["upd"] + r["per_update"]["rev"])


def main(tag="V14_E1_CP", seed=0):
    cols = list(bases.ALL); cells = {}
    for cell, spec in CELLS.items():
        for row in ROWS:
            for col in cols: cells[(cell, row, col)] = run(row, bases.ALL[col], spec, seed)
    frontier = {}; adm = {}
    for cell, spec in CELLS.items():
        for col in cols:
            rows_adm = [row for row in ROWS if cells[(cell, row, col)]["admissible"]]; adm[f"{cell}|{col}"] = rows_adm
            costs = {row: lifecycle_cost(cells[(cell, row, col)], spec["H"], spec["U"]) for row in rows_adm}
            frontier[f"{cell}|{col}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []
            for Hh in (1, 4, 16, 64, 256, 1024, 4096, 16384):
                c2 = {row: lifecycle_cost(cells[(cell, row, col)], Hh, spec["U"]) for row in rows_adm}
                frontier[f"{cell}|{col}|H={Hh}"] = sorted(r for r, c in c2.items() if c <= min(c2.values()) + 1e-9) if c2 else []
    hstar = {}
    for cell, spec in CELLS.items():
        for col in cols:
            i, c = cells[(cell, "INTERP", col)], cells[(cell, "CP", col)]
            d_serve = i["per_query_exec"] - c["per_query_exec"]; d_upd = (c["per_update"]["upd"] + c["per_update"]["rev"]) - (i["per_update"]["upd"] + i["per_update"]["rev"]) + (c["desc_state"] - i["desc_state"]) / max(spec["U"], 1)
            hstar[f"{cell}|{col}"] = round(d_upd / d_serve, 1) if d_serve > 0 else None  # queries per window at which CP overtakes INTERP
    c2 = {f"{cell}|{row}": all(cells[(cell, row, col)]["capability_by_regime"] == cells[(cell, row, cols[0])]["capability_by_regime"] for col in cols) for cell in CELLS for row in ROWS}
    receipt = {"schema": "StageE1CPV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "related": [409, 410], "revival_record": "RV-377-033", "run_tag": tag,
               "ecology": {"regimes": REGIMES, "tau": TAU, "cells": {k: dict(v, regimes=list(v["regimes"])) for k, v in CELLS.items()}, "eval_queries": len(EVAL_QUERIES), "theta": THETA},
               "rows": list(ROWS), "C2_capability_column_invariant": c2, "cells": {f"{cell}|{row}|{col}": {k: v for k, v in r.items() if k not in ("row", "basis")} for (cell, row, col), r in cells.items()},
               "admissible": adm, "frontier": frontier, "Hstar_CP_over_INTERP_queries_per_window": hstar,
               "claim_ceiling": "exact charged lifecycle at a 4-factor, 3-regime, 8-bit scope; one shared learner; the parent portfolio is the registered four rows, not the full P0-P11 ladder"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("C2 all:", all(c2.values()))
    for cell in CELLS:
        print(cell, {row: cells[(cell, row, cols[0])]["capability_by_regime"] for row in ROWS}, "| frontier:", {c.split('_')[0]: frontier[f"{cell}|{c}"] for c in cols})
    return receipt


if __name__ == "__main__":
    main()
