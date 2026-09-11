"""RV-377-038: the lineage / historical-persistence twin (ChatGPT lane theorem GMI-MN4 'drift does not identify persistence
demand', witness A5, demand coordinate beta_lin, gate G3 implementation-equivalence tournament, hostile F10).

Two obligations with IDENTICAL revision process (nu: U revisions of one factor each) that differ ONLY in whether historical
("as-of version v") queries are legal:
  E  ephemeral   — only current queries; old states may be destroyed.
  P  persistent  — as-of queries are legal: the answer must be the one under the factor coefficients that were current at
                   version v (v = 0 .. current); capability counts current AND as-of queries.
Rows (same learner; they differ only in whether and how history is kept):
  MOD_U      single current version (no A5): as-of queries are answered with the current state.
  HIST_SNAP  A5 by full snapshots: every superseded per-factor table is kept, tagged with its version (persistent-root encoding).
  HIST_LOG   A5 by an undo log: the current tables plus a log of (version, factor, old table); an as-of query replays the log
             backwards from the current version (log encoding of the same witness).
Predictions are about the A5 witness (as-of correctness), admissibility under E vs P, and the cost ordering of the two
A5 encodings as a function of the queried history depth.
"""
from __future__ import annotations

import json
import os

from . import bases
from .core import Machine, clamp, fx, sha256_of
from .e1_vlc import DEV_EVENTS, N_F, SCOPES, Learner, ModularUnversioned, fbits, truth, x_single

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
COEFF_VALUES = [fx(v) for v in (0.25, 0.5, 0.75, 1.0)]
EVAL_X = (0b11111111, 0b11110101, 0b01011111, 0b11010111)
CURRENT_QUERIES = [(x, s) for s in SCOPES for x in EVAL_X]


class Current(ModularUnversioned):
    row = "MOD_U"

    def query_asof(self, M, x, s, v):
        return self.query(M, x, s)  # no history: answers with the current version

    def end_round(self, M): pass


class HistSnap(ModularUnversioned):
    row = "HIST_SNAP"

    def init(self, M):
        super().init(M); M.declare_store("hist"); M.declare("version", "fin", 0)

    def _rebuild(self, M, i):
        # snapshot the superseded table of factor i under the current version before rebuilding it
        for k, v in M.stores["ftab"]:
            if k[0] == i: M.op("S_INSERT", "hist", (M.read("version"), i, k[1]), v)
        super()._rebuild(M, i)

    def end_round(self, M):
        M.write("version", M.op("INC", M.read("version")))

    def query_asof(self, M, x, s, v):
        acc = 0
        for i in s:
            b0, b1 = fbits(x, i); p = b0 | (b1 << 1); val = None
            for vv in range(v + 1, M.read("version") + 1):  # history index v = state current during version v+1: use the first snapshot taken at a version >= v+1
                val = M.op("S_LOOKUP", "hist", (vv, i, p))
                if val is not None: break
            if val is None: val = M.op("S_LOOKUP", "ftab", (i, p))
            acc = M.op("ADD", acc, 0 if val is None else val)
        return acc


class HistLog(ModularUnversioned):
    row = "HIST_LOG"

    def init(self, M):
        super().init(M); M.declare_store("log"); M.declare("version", "fin", 0)

    def _rebuild(self, M, i):
        old = [(k[1], v) for k, v in M.stores["ftab"] if k[0] == i]
        M.op("S_INSERT", "log", (M.read("version"), i), old)  # one undo record per superseded table
        super()._rebuild(M, i)

    def end_round(self, M):
        M.write("version", M.op("INC", M.read("version")))

    def query_asof(self, M, x, s, v):
        # replay the undo log backwards from the current version down to v
        cur = {k: val for k, val in M.stores["ftab"]}
        for vv in range(M.read("version"), v, -1):  # undo every record taken at a version > v (records at version vv hold the table current during version vv)
            for i in range(N_F):
                rec = M.op("S_LOOKUP", "log", (vv, i))
                if rec is not None:
                    for p, val in rec: cur[(i, p)] = val; M.op("CONST", 0)
        acc = 0
        for i in s:
            b0, b1 = fbits(x, i); acc = M.op("ADD", acc, cur.get((i, b0 | (b1 << 1)), 0))
        return acc


ROWS = {"MOD_U": Current, "HIST_SNAP": HistSnap, "HIST_LOG": HistLog}
CELLS = {"E_EPHEMERAL": {"U": 8, "asof": False, "depth": 0}, "P_PERSISTENT_D1": {"U": 8, "asof": True, "depth": 1}, "P_PERSISTENT_D8": {"U": 8, "asof": True, "depth": 8}}
H_HEAD = 64


def run(row, basis, spec, seed=0):
    ref = ROWS[row](); M = Machine(basis, seed=seed)
    coeffs = [(COEFF_VALUES[(2 * i) % 4], COEFF_VALUES[(2 * i + 1) % 4]) for i in range(N_F)]
    history = [list(coeffs)]
    M.phase("exec"); ref.init(M)
    for x, s in DEV_EVENTS:
        M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
    M.phase("upd"); ref.end_round(M); M.end_event()
    n_q = 0
    for u in range(spec["U"]):
        i = u % N_F; coeffs[i] = (COEFF_VALUES[(coeffs[i][0] // 4 + 1 + u) % 4], COEFF_VALUES[(coeffs[i][1] // 4 + 2 + u) % 4])
        M.phase("rev"); ref.revise(M, [i]); M.end_event()
        for p in ((1, 0), (0, 1), (0, 0)):
            x = x_single(i, p); s = tuple(sorted((i, (i + 1) % N_F)))
            M.phase("upd"); ref.feedback(M, x, s, truth(coeffs, x, s)); M.end_event()
        M.phase("upd"); ref.end_round(M); M.end_event()
        history.append(list(coeffs))
        M.phase("exec")
        for x, s in CURRENT_QUERIES: ref.query(M, x, s); n_q += 1
        if spec["asof"]:
            v = max(0, len(history) - 1 - spec["depth"])
            for x, s in CURRENT_QUERIES: ref.query_asof(M, x, s, v); n_q += 1
    M.phase("ver")
    cur_ok = sum(int(abs(ref.query(M, x, s) - truth(coeffs, x, s)) <= 1) for x, s in CURRENT_QUERIES) / len(CURRENT_QUERIES)
    asof_ok = None
    if spec["asof"]:
        v = max(0, len(history) - 1 - spec["depth"]); ok = 0
        for x, s in CURRENT_QUERIES:
            ok += int(abs(ref.query_asof(M, x, s, v) - truth(history[v], x, s)) <= 1)
        asof_ok = ok / len(CURRENT_QUERIES)
    cap = cur_ok if asof_ok is None else round(min(cur_ok, asof_ok), 4)
    desc_state = sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells) + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values())
    R = dict(M.L.c); U = spec["U"]
    return {"row": row, "basis": basis.name, "current_ok": cur_ok, "asof_ok": asof_ok, "capability": cap, "admissible": cap >= THETA, "desc_state": desc_state, "R": R,
            "per_query_exec": R["exec"] / n_q, "per_update": {k: R[k] / U for k in ("upd", "rev")}}


def lifecycle_cost(r, H, U):
    return r["desc_state"] + H * r["per_query_exec"] + U * (r["per_update"]["upd"] + r["per_update"]["rev"])


def main(tag="V19_E1_LINEAGE", seed=0):
    cols = list(bases.ALL); cells = {}
    for cell, spec in CELLS.items():
        for row in ROWS:
            for col in cols: cells[(cell, row, col)] = run(row, bases.ALL[col], spec, seed)
    frontier = {}; adm = {}
    for cell, spec in CELLS.items():
        for col in cols:
            rows_adm = [row for row in ROWS if cells[(cell, row, col)]["admissible"]]; adm[f"{cell}|{col}"] = rows_adm
            costs = {row: lifecycle_cost(cells[(cell, row, col)], H_HEAD, spec["U"]) for row in rows_adm}
            frontier[f"{cell}|{col}"] = sorted(r for r, c in costs.items() if c <= min(costs.values()) + 1e-9) if costs else []
    c2 = {f"{cell}|{row}": all((cells[(cell, row, col)]["capability"], cells[(cell, row, col)]["asof_ok"]) == (cells[(cell, row, cols[0])]["capability"], cells[(cell, row, cols[0])]["asof_ok"]) for col in cols) for cell in CELLS for row in ROWS}
    receipt = {"schema": "StageE1LineageV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "related": [418, 419], "revival_record": "RV-377-038", "run_tag": tag,
               "cells_spec": CELLS, "rows": list(ROWS), "C2": c2, "cells": {f"{cell}|{row}|{col}": {k: v for k, v in r.items() if k not in ("row", "basis")} for (cell, row, col), r in cells.items()},
               "admissible": adm, "frontier": frontier, "claim_ceiling": "exact charged lifecycle; MN4 twin executed with learned factors; two A5 encodings"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_E1_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("C2 all:", all(c2.values()))
    for cell in CELLS:
        print(cell, {row: (cells[(cell, row, cols[0])]["current_ok"], cells[(cell, row, cols[0])]["asof_ok"]) for row in ROWS}, "| frontier:", {c.split('_')[0]: frontier[f"{cell}|{c}"] for c in cols})
    return receipt


if __name__ == "__main__":
    main()
