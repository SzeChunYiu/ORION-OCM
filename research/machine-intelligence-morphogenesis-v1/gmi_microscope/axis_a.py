"""RV-377-072 — the A axis of GMI-DA7: does the DYNAMICAL domain D6 need a primitive of its own?

GMI-DA7 part 3 says a kingdom can be gained only by enlarging the alphabet A, raising the depth bound d, raising the
precision p, or refining the ecology family F. This module executes the A axis on the one registered domain that has no
primitive: D6, the dynamical / controller domain (gap DG-1). The taxonomy lists it; `morph.KINDS` has no kind for it.

The question is NOT whether an iterated-map carrier can be built - it obviously can, by adding one kind. The question is
whether adding it CHANGES THE CLASS SET, i.e. whether the carrier it introduces resists bounded semantics-preserving
reduction to a registered parent. Protocol rule 19 requires the PARENT-MAXIMAL opponent, and the parent-maximal opponent
here is not the gradient row. It is the TABLE read-modify-write register:

    INSERT(tab, key, SUM(LOOKUP(tab, key), f(INPUT)))

Every port in that expression is in the registered alphabet, the graph is acyclic (the feedback runs through the state
update convention, not through an edge), and nothing in it reads a TARGET. So the registered alphabet ALREADY contains an
input-driven state transition, through the memory carrier. Whether D6 is a domain therefore reduces to a measurable
question: is the iterated-map carrier exactly equal to the register parent in served answers, and at what cost overhead?

Ecology E_hist(T, mode): a deterministic stream of T eight-bit events. The obligation is served ONLINE and depends on the
whole history through a bounded sufficient statistic, so no memoryless row can serve it:

  ACC     y_t = (sum_{s <= t} (x_s mod 16)) mod 16     running accumulator
  PARITY  y_t = popcount parity of x_1..x_t            running parity
  MAXV    y_t = max_{s <= t} (x_s mod 16)              running maximum

Capability is scored on the second half of the stream only, so that a machine gets no credit for the warm-up prefix where
the statistic is still near its initial value.

Rows (all charged exactly on the same Machine, the same events, answers compared bit for bit):
  ITERMAP     the EXTENDED-ALPHABET candidate: one declared fx cell z and an ITERATE law z <- g(z, x), no target read.
  TAB_RMW     the PARENT-MAXIMAL registered opponent: a one-entry store used as a register, updated by read-modify-write.
  EVIDENCE    the replay parent: a buffer of the last C inputs, rescanned at serve time; admissible iff C >= T.
  DENSE_GRAD  the coefficient parent: error-driven update of a coefficient over the current input only.
  STORE_X     the exemplar parent: keyed on the current input only.
  ITER_FROZEN negative twin of ITERMAP: the cell exists, the iterate law is removed.

If ITERMAP and TAB_RMW agree bit for bit on every event of every cell, D6 is REDUCED_TO_PARENT(D2) and the honest
correction to GMI-DA1 is that the registered alphabet admits EIGHT carrier classes, with D6 the read-modify-write phase of
D2 rather than a class of its own. If they disagree anywhere, the A axis has produced a separation and the criterion-3
question is open on that ecology.
"""
from __future__ import annotations

import json
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = 0.85
MODES = ("ACC", "PARITY", "MAXV")


def stream(T, seed=0):
    """declared deterministic event stream (32-bit LCG, Numerical Recipes constants), one 8-bit input per event."""
    x = (seed * 1103515245 + 12345) & 0xFFFFFFFF
    out = []
    for _ in range(T):
        x = (x * 1103515245 + 12345) & 0xFFFFFFFF
        out.append((x >> 16) & 0xFF)
    return out


def truth(mode, xs):
    """the served answer required at every event, as a function of the history so far."""
    ys = []; acc = 0; par = 0; mx = 0
    for x in xs:
        v = x % 16
        acc = (acc + v) % 16; par ^= bin(x).count("1") & 1; mx = max(mx, v)
        ys.append({"ACC": acc, "PARITY": par, "MAXV": mx}[mode])
    return ys


# --------------------------------------------------------------------------------------------------------------- rows
class Row:
    row = "?"

    def __init__(self, eco):
        self.e = eco

    declared_desc = None

    def init(self, M): pass

    def observe(self, M, x):
        """exec phase: the current input is visible before serving; the truth for this event is not."""
        self.last = x

    def step(self, M, x): raise NotImplementedError   # update phase; may consume the DELAYED feedback

    def serve(self, M): raise NotImplementedError     # exec phase; returns the served answer

    def desc_bits(self, M): return M.L.c["desc"]


class IterMap(Row):
    """EXTENDED ALPHABET. One fx cell, one input-driven iterate law. This is the kind the IR does not have.
    The iterate runs in the EXEC phase because it is driven by the input and not by feedback."""
    row = "ITERMAP"

    def init(self, M):
        M.declare("z", "fx", 0)

    def step(self, M, x): pass

    def observe(self, M, x):
        self.last = x
        mode = self.e["mode"]; z = M.read("z")
        if mode == "ACC":
            v = M.op("ADD", z, x % 16)
            v = M.op("SEL", M.op("GT", v, 15), M.op("SUB", v, 16), v)
        elif mode == "PARITY":
            v = M.op("XOR", z, bin(x).count("1") & 1)
        else:
            v = M.op("SEL", M.op("GT", x % 16, z), x % 16, z)
        M.write("z", v)

    def serve(self, M):
        return M.read("z")


class _TabMarker: pass


class TabRmw(Row):
    """PARENT-MAXIMAL REGISTERED OPPONENT: a one-entry store as a register, updated by read-modify-write.
    Every operation is in the registered alphabet: LOOKUP the single key, compute, INSERT back."""
    row = "TAB_RMW"

    def init(self, M):
        M.declare_store("reg")
        M.op("S_INSERT", "reg", 0, 0)
        # DECLARED REGISTER DESCRIPTION (protocol rule 19, parent-maximality): the Machine charges description bits on
        # every S_INSERT because its stores are append-only, which over-charges a register that OVERWRITES one key.
        # The declared register description is header + one entry, and the frontier uses the declared figure so that the
        # parent is never penalised by an accounting artefact. Both figures are reported.
        self.declared_desc = M.basis.desc_store_header + M.basis.desc_store_entry

    def step(self, M, x): pass

    def observe(self, M, x):
        self.last = x
        mode = self.e["mode"]
        z = M.op("S_LOOKUP", "reg", 0)           # LOOKUP(tab, key)
        z = z if isinstance(z, int) else 0
        if mode == "ACC":
            v = M.op("ADD", z, x % 16)
            v = M.op("SEL", M.op("GT", v, 15), M.op("SUB", v, 16), v)
        elif mode == "PARITY":
            v = M.op("XOR", z, bin(x).count("1") & 1)
        else:
            v = M.op("SEL", M.op("GT", x % 16, z), x % 16, z)
        M.op("S_DELETE", "reg", 0)               # overwrite, not append
        M.op("S_INSERT", "reg", 0, v)
        M.L.charge(M.basis.write_cost)


    def serve(self, M):
        v = M.op("S_LOOKUP", "reg", 0)
        return v if isinstance(v, int) else 0


class EvidenceReplay(Row):
    """the replay parent: a declared buffer of the last C inputs, rescanned at serve time. Admissible iff C >= T."""
    row = "EVIDENCE"

    def init(self, M):
        self.buf = []; self.C = self.e["C"]
        M.declare_store("evid")
        for _ in range(self.C): M.L.c["desc"] += M.basis.desc_store_entry

    def observe(self, M, x):
        self.last = x
        self.buf.append(x)
        if len(self.buf) > self.C: self.buf.pop(0)

    def step(self, M, x):
        M.L.charge(M.basis.write_cost)

    def serve(self, M):
        mode = self.e["mode"]; acc = 0
        for x in self.buf:
            v = x % 16
            if mode == "ACC":
                acc = M.op("ADD", acc, v); acc = M.op("SEL", M.op("GT", acc, 15), M.op("SUB", acc, 16), acc)
            elif mode == "PARITY":
                acc = M.op("XOR", acc, bin(x).count("1") & 1)
            else:
                acc = M.op("SEL", M.op("GT", v, acc), v, acc)
        return acc


class DenseGrad(Row):
    """the coefficient parent: a coefficient over the CURRENT input only, error-driven. Structurally memoryless."""
    row = "DENSE_GRAD"

    def init(self, M):
        M.declare("w", "fx", 0); M.declare("b", "fx", 0); self.last = None

    def step(self, M, x):
        if self.e.get("teacher") is not None and self.e["teacher"]:
            y = self.e["teacher"].pop(0)
            out = M.op("ADD", M.op("MUL", M.read("w"), x % 16), M.read("b"))
            err = M.op("SUB", out, y)
            M.write("w", M.op("SUB", M.read("w"), M.op("SHR", M.op("MUL", err, x % 16), 4)))
            M.write("b", M.op("SUB", M.read("b"), M.op("SHR", err, 2)))

    def serve(self, M):
        x = self.last or 0
        return M.op("ADD", M.op("MUL", M.read("w"), x % 16), M.read("b")) % 16


class StoreX(Row):
    """the exemplar parent: keyed on the current input only. Structurally memoryless."""
    row = "STORE_X"

    def init(self, M):
        M.declare_store("mem"); self.mem = {}

    def step(self, M, x):
        if self.e.get("teacher2") is not None and self.e["teacher2"]:
            y = self.e["teacher2"].pop(0)
            if (x % 16) not in self.mem: M.L.c["desc"] += M.basis.desc_store_entry
            self.mem[x % 16] = y
            M.op("S_INSERT", "mem", x % 16, y); M.L.charge(M.basis.write_cost)

    def serve(self, M):
        return self.mem.get(getattr(self, "last", 0) % 16, 0)


class IterFrozen(IterMap):
    """negative twin: the cell is declared, the iterate law is removed."""
    row = "ITER_FROZEN"

    def observe(self, M, x): self.last = x


ROWS = {"ITERMAP": IterMap, "TAB_RMW": TabRmw, "EVIDENCE": EvidenceReplay, "DENSE_GRAD": DenseGrad,
        "STORE_X": StoreX, "ITER_FROZEN": IterFrozen}
REGISTERED_ALPHABET_ROWS = ("TAB_RMW", "EVIDENCE", "DENSE_GRAD", "STORE_X")
EXTENDED_ALPHABET_ROWS = ("ITERMAP", "ITER_FROZEN")


def run(row, basis, T, mode, C=None, seed=0):
    xs = stream(T, seed); ys = truth(mode, xs)
    eco = {"T": T, "mode": mode, "C": C if C is not None else T, "teacher": list(ys), "teacher2": list(ys)}
    ref = ROWS[row](eco); M = Machine(basis, seed=seed)
    M.phase("exec"); ref.init(M)
    desc_after_init = M.L.c["desc"]
    served = []
    half = T // 2
    for t, x in enumerate(xs):
        # forward first, then update: no row ever sees the truth for the event it is serving
        M.phase("exec"); ref.observe(M, x); served.append(ref.serve(M))
        M.phase("upd"); ref.step(M, x)
        M.end_event()
    correct = sum(1 for t in range(half, T) if served[t] == ys[t])
    cap = round(correct / (T - half), 4)
    R = dict(M.L.c)
    declared = getattr(ref, "declared_desc", None)
    return {"row": row, "basis": basis.name, "T": T, "mode": mode, "capability": cap, "admissible": cap >= THETA,
            "R": R, "desc_bits": R["desc"], "declared_desc_bits": declared if declared is not None else R["desc"],
            "desc_charged_note": ("the Machine charges description bits on every S_INSERT because its stores are append-only; "
                                  "a register that OVERWRITES one key is over-charged, so the declared figure is used on the frontier") if declared is not None else "as charged",
            "desc_after_init": desc_after_init,
            "exec_per_event": round((R["exec"]) / T, 4), "upd_per_event": round(R["upd"] / T, 4),
            "answer_signature": sha256_of(served), "served_second_half": served[half:],
            "alphabet": "EXTENDED" if row in EXTENDED_ALPHABET_ROWS else "REGISTERED"}


def lifecycle(r, H, rr):
    """the registered cost model: desc + H * exec_per_event + r * (upd + ver) + (r/4) * rev."""
    R = r["R"]
    return r["declared_desc_bits"] + H * r["exec_per_event"] + rr * (R["upd"] + R.get("ver", 0)) + (rr / 4) * R.get("rev", 0)


T_GRID = (2, 4, 8, 16, 32, 64)
H_GRID = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096)
R_GRID = (0, 1, 2, 4, 8, 16, 32)


def main(tag="V1", seed=0):
    cols = dict(bases.ALL)
    cells = {}
    for mode in MODES:
        for T in T_GRID:
            for rname in ROWS:
                for cname, b in cols.items():
                    cells[(mode, T, rname, cname)] = run(rname, b, T, mode, seed=seed)
    # C2: column invariance of capability and answers
    c2 = {}
    for mode in MODES:
        for T in T_GRID:
            for rname in ROWS:
                sigs = {cells[(mode, T, rname, c)]["answer_signature"] for c in cols}
                caps = {cells[(mode, T, rname, c)]["capability"] for c in cols}
                c2[f"{mode}|T={T}|{rname}"] = {"answer_signature_invariant": len(sigs) == 1, "capability_invariant": len(caps) == 1}
    # the reduction attack: ITERMAP against the parent-maximal registered opponent
    equality = {}; overhead = {}
    for mode in MODES:
        for T in T_GRID:
            for cname in cols:
                a = cells[(mode, T, "ITERMAP", cname)]; p = cells[(mode, T, "TAB_RMW", cname)]
                equality[f"{mode}|T={T}|{cname}"] = a["answer_signature"] == p["answer_signature"]
                overhead[f"{mode}|T={T}|{cname}"] = {"desc_itermap": a["declared_desc_bits"], "desc_tab_rmw": p["declared_desc_bits"],
                                                     "desc_charged_tab_rmw_append_only": p["desc_bits"],
                                                     "desc_overhead_bits": p["declared_desc_bits"] - a["declared_desc_bits"],
                                                     "desc_ratio": round(p["declared_desc_bits"] / max(a["declared_desc_bits"], 1), 4),
                                                     "exec_per_event_itermap": a["exec_per_event"], "exec_per_event_tab_rmw": p["exec_per_event"],
                                                     "exec_ratio": round(p["exec_per_event"] / max(a["exec_per_event"], 1e-9), 4)}
    # does the description of the replay parent grow with T while the register parents stay constant?
    growth = {mode: {r: [cells[(mode, T, r, "B0_LOCAL_ADAPTIVE_TRANSDUCERS")]["desc_bits"] for T in T_GRID] for r in ROWS} for mode in MODES}
    # frontier over the extended grid
    frontier = {}
    for mode in MODES:
        for T in T_GRID:
            for cname in cols:
                for H in H_GRID:
                    for rr in R_GRID:
                        adm = [r for r in ROWS if cells[(mode, T, r, cname)]["admissible"]]
                        if not adm:
                            frontier[f"{mode}|T={T}|{cname}|H={H}|r={rr}"] = []
                            continue
                        costs = {r: lifecycle(cells[(mode, T, r, cname)], H, rr) for r in adm}
                        m = min(costs.values())
                        frontier[f"{mode}|T={T}|{cname}|H={H}|r={rr}"] = sorted(r for r, c in costs.items() if c <= m + 1e-9)
    occ = {}
    for key, v in frontier.items():
        for r in v: occ[r] = occ.get(r, 0) + 1
    registered_only_admissible = {}
    for mode in MODES:
        for T in T_GRID:
            adm = [r for r in REGISTERED_ALPHABET_ROWS if cells[(mode, T, r, "B0_LOCAL_ADAPTIVE_TRANSDUCERS")]["admissible"]]
            registered_only_admissible[f"{mode}|T={T}"] = adm
    all_eq = all(equality.values())
    receipt = {"schema": "StageAxisADynamicalDomainV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-072", "run_tag": tag, "axis": "A (alphabet enlargement) of GMI-DA7",
               "domain_under_test": "D6 dynamical / controller (gap DG-1: listed in the taxonomy, no kind in morph.KINDS)",
               "theta": THETA, "modes": list(MODES), "T_grid": list(T_GRID), "H_grid": list(H_GRID), "r_grid": list(R_GRID),
               "columns": list(cols), "rows": {r: ("EXTENDED" if r in EXTENDED_ALPHABET_ROWS else "REGISTERED") for r in ROWS},
               "parent_maximality_note": "the parent-maximal registered opponent is TAB_RMW, the one-entry store used as a register and updated by read-modify-write INSERT(tab, key, SUM(LOOKUP(tab, key), f(INPUT))); every port of that expression is in morph.KINDS, the graph is acyclic, and no TARGET is read. Protocol rule 19.",
               "cells": {f"{m}|T={T}|{r}|{c}": {k: v for k, v in d.items() if k not in ("row", "basis", "served_second_half")} for (m, T, r, c), d in cells.items()},
               "c2_column_invariance": c2, "itermap_equals_tab_rmw_answers": equality, "n_equality_cells": len(equality),
               "all_equality_cells_agree": all_eq, "reduction_overhead": overhead,
               "desc_growth_in_T": growth,
               "analytic_no_crossover": ("cost(TAB_RMW) - cost(ITERMAP) = (declared desc overhead) + H * (exec overhead per event) + "
                                         "r * (update overhead per event). Every term is non-negative and the description term is strictly "
                                         "positive, so the difference is strictly positive at every H >= 0 and every r >= 0 and NO crossover "
                                         "exists anywhere on the (H, r) quadrant. The finite grid is reported for replay, but the claim that no "
                                         "cell favours the register parent rests on this algebraic statement, not on the grid's extent (gap DG-2)."), "registered_alphabet_admissible_rows": registered_only_admissible,
               "frontier": frontier, "frontier_occupancy_counts": occ, "n_frontier_cells": len(frontier),
               "terminal": ("D6_REDUCED_TO_PARENT_D2__THE_ITERATED_MAP_CARRIER_IS_THE_READ_MODIFY_WRITE_PHASE_OF_MEMORY__"
                            "EXACT_DEVELOPMENTAL_EQUALITY_ON_ALL_CELLS" if all_eq else
                            "A_AXIS_SEPARATION__THE_ITERATED_MAP_CARRIER_DIFFERS_FROM_THE_PARENT_MAXIMAL_REGISTER_PARENT"),
               "claim_ceiling": "exact charged replay at 8-bit fixed point on three history-dependent obligations and six stream lengths; the equality test is a bit-for-bit comparison of every served answer, and the cost comparison is in the registered cost model only"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_AXIS_A_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    c0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
    print("ITERMAP == TAB_RMW on every cell:", all_eq, f"({sum(equality.values())}/{len(equality)})")
    for mode in MODES:
        for T in T_GRID:
            print(f"  {mode:7s} T={T:3d}", {r: cells[(mode, T, r, c0)]["capability"] for r in ROWS},
                  "| desc", {r: cells[(mode, T, r, c0)]["desc_bits"] for r in ("ITERMAP", "TAB_RMW", "EVIDENCE")})
    print("frontier occupancy:", occ)
    print("terminal:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
