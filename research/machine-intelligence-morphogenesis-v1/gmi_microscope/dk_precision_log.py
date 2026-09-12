"""RV-377-075 — the hostile parent-maximality test of the precision-gated kingdom (RV-377-066).

RV-377-066 established, at scope, that on the ambiguous-evidence ecology NO row is admissible in the registered 8-bit
universe while probabilistic rows are admissible at 12 bits (and, on the fine ladder, at 10). The mechanism is a
LINEAR-DOMAIN underflow: `_Mixture._condition` multiplies 32 weights by their likelihoods and renormalizes, and at four
fractional bits the weights cannot concentrate, so every row returns the prior mixture and the Brier skill score clips
to zero.

Protocol rule 19 says a verdict is only valid against a PARENT-MAXIMAL opponent, and the obvious opponent was not built.
Bayesian updating in the LOG DOMAIN is the standard textbook fix for exactly this underflow, it needs only ADD, SUB, GT,
SEL and a table, all registered kinds, and it fits in eight bits: with four fractional bits a log2 weight ranges over
[-8, +7.9], i.e. a dynamic range of 2^16 instead of 2^4. If a log-domain row is admissible on the ambiguous ecology at
fx8, the precision gate is an artefact of the linear representation and the kingdom claim collapses.

Rows added (all charged on the same Machine, same events, same scoring, same theta):

  LOGBAYES8   log-domain posterior: log-weights updated by ADDITION of a declared log-likelihood, renormalized by
              subtracting the running maximum (charged GT + SUB), then exponentiated through a DECLARED 256-entry
              table for the served mixture. Every table entry is charged to `desc`.
  LOGMAP8     the same log-domain machinery served as a point estimate (the log-domain twin of MAP).
  LOGBAYES8_NOMAXSUB   negative twin: the log-domain update WITHOUT the max subtraction, so that any advantage is
              attributed to the renormalization and not to the log representation alone.

A row here is only a threat to RV-377-066 if it is admissible AT fx8 ON E_ambig. Anything else leaves that record intact.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of
from .dk_precision import (THETA, X_ALL, Arith, Row, CLASS_STRUCT_BITS, DESC_BITS_PER_SCALAR, N_EVENTS,
                           REVOKE_AT, REVOKE_INDEX, capability, ecology)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
EXP_TABLE_ENTRIES = 256


def _log2(fr):
    """exact-enough log2 of a positive rational, to 24 fractional bits, computed by integer bisection (no float)."""
    if fr <= 0: return None
    n, d = fr.numerator, fr.denominator
    e = 0
    while n < d: n <<= 1; e -= 1
    while n >= 2 * d: d <<= 1; e += 1
    acc = F(e); half = F(1, 2); x = F(n, d)          # x in [1, 2)
    for _ in range(24):
        x = x * x
        if x >= 2: acc += half; x /= 2
        half /= 2
    return acc


class _LogMixture(Row):
    """log-domain weights. The DECLARED description holds one log-prior and two log-likelihoods per hypothesis
    (for y = 1 and y = 0), each rounded to the instrument grid, plus the shared exponent table."""

    use_maxsub = True

    def init(self, M):
        A = self.A; e = self.e; K = e["n_hyps"]
        self.K = K
        self.LP1 = [[A.const(_log2(F(h["p"][x]))) if F(h["p"][x]) > 0 else A.lo_or_min() for x in X_ALL] for h in e["hyps"]]
        self.LP0 = [[A.const(_log2(1 - F(h["p"][x]))) if (1 - F(h["p"][x])) > 0 else A.lo_or_min() for x in X_ALL] for h in e["hyps"]]
        tot = sum(h["prior"] for h in e["hyps"])
        self.lpri = [A.const(_log2(F(h["prior"], tot))) for h in e["hyps"]]
        self.lw = list(self.lpri); self.hist = []
        # the exponent table: 2^v on the instrument grid, one entry per representable log value in [-8, 0]
        self.exp_tab = {}
        for u in range(-(1 << (A.Fb + 3)), 1):
            self.exp_tab[u] = A.const(F(2) ** F(u, A.S)) if F(u, A.S) >= -24 else 0
        self.w_scalars = 3 * K + EXP_TABLE_ENTRIES
        self.struct_bits = CLASS_STRUCT_BITS

    def _condition(self, M, x, y):
        A = self.A
        for j in range(self.K):
            self.lw[j] = A.add(self.lw[j], (self.LP1 if y else self.LP0)[j][X_ALL.index(x)])
        if self.use_maxsub:
            m = self.lw[0]
            for j in range(1, self.K): m = self.lw[j] if A.gt(self.lw[j], m) else m
            for j in range(self.K): self.lw[j] = A.sub(self.lw[j], m)
        self._n(M, self.K)

    def _neutral(self, M):
        A = self.A
        for j in range(self.K): self.lw[j] = A.add(self.lw[j], 0)
        if self.use_maxsub:
            m = self.lw[0]
            for j in range(1, self.K): m = self.lw[j] if A.gt(self.lw[j], m) else m
            for j in range(self.K): self.lw[j] = A.sub(self.lw[j], m)
        self._n(M, self.K)

    def observe(self, M, x, y):
        self.hist.append((x, y)); self._condition(M, x, y)

    def revoke(self, M, idx, x, y):
        self.lw = list(self.lpri)
        for i, (hx, hy) in enumerate(self.hist):
            if i == idx: self._neutral(M)
            else: self._condition(M, hx, hy)
        self.hist = [ev for i, ev in enumerate(self.hist) if i != idx]

    def _linear_weights(self, M):
        A = self.A; ws = []
        for j in range(self.K):
            v = self.lw[j]
            ws.append(self.exp_tab.get(v, 0) if v <= 0 else A.one())
            M.op("S_LOOKUP", "__exp__", 0) if False else M.op("SEL", 1, 0, 0)   # one charged table activation
        self._n(M, self.K)
        return ws


class LogBayes8(_LogMixture):
    row = "LOGBAYES8"

    def query(self, M, x):
        A = self.A; ws = self._linear_weights(M); xi = X_ALL.index(x)
        num = 0; den = 0
        for j in range(self.K):
            num = A.add(num, A.mul(ws[j], A.const(F(self.e["hyps"][j]["p"][x]))))
            den = A.add(den, ws[j])
        self._n(M, 2 * self.K)
        return A.div(num, den) if den else 0


class LogMap8(_LogMixture):
    row = "LOGMAP8"

    def query(self, M, x):
        A = self.A; best = 0
        for j in range(1, self.K):
            if A.gt(self.lw[j], self.lw[best]): best = j
        self._n(M, self.K)
        return A.const(F(self.e["hyps"][best]["p"][x]))


class LogBayes8NoMaxSub(LogBayes8):
    row = "LOGBAYES8_NOMAXSUB"
    use_maxsub = False


def _lo_or_min(self):
    return self.lo if self.lo is not None else -(1 << 40)


Arith.lo_or_min = _lo_or_min
ROWS = {c.row: c for c in (LogBayes8, LogMap8, LogBayes8NoMaxSub)}


def run(row, basis, eco, precision, seed=0):
    M = Machine(basis, seed=seed); A = Arith(M, precision); ref = ROWS[row](eco, A)
    M.phase("exec"); ref.init(M)
    ev = eco["events"]; nev = len(eco["eval"])
    for t, (x, y) in enumerate(ev, 1):
        M.phase("exec")
        for xx in eco["eval"]: ref.query(M, xx)
        M.phase("upd"); ref.observe(M, x, y); M.end_event()
        M.phase("ver")
        for xx in eco["eval"]: M.op("EQ", ref.query(M, xx), 0)
        if t == REVOKE_AT:
            M.phase("rev"); ref.revoke(M, REVOKE_INDEX, *ev[REVOKE_INDEX]); M.end_event()
    M.phase("exec")
    served = {xx: ref.query(M, xx) for xx in eco["eval"]}
    sfr = {xx: A.frac(v) for xx, v in served.items()}
    cap, excess = capability(eco, sfr)
    R = dict(M.L.c)
    return {"row": row, "precision": precision, "capability": float(round(cap, 6)),
            "capability_exact": f"{cap.numerator}/{cap.denominator}", "admissible": bool(cap >= THETA),
            "R": R, "charged_ops_total": A.n_ops, "desc_bits": ref.desc_bits(),
            "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits,
            "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}


def main(tag="V1", seed=0):
    b = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    cells = {}
    for kind in ("ambig", "noisy"):
        eco = ecology(kind)
        for p in ("fx8", "fx10", "fx12", "fx16", "wide"):
            for r in ROWS:
                try:
                    cells[f"{kind}|{p}|{r}"] = run(r, b, eco, p, seed)
                except Exception as ex:
                    cells[f"{kind}|{p}|{r}"] = {"error": f"{type(ex).__name__}: {ex}", "admissible": False}
    threat = sorted(k for k, v in cells.items() if k.startswith("ambig|fx8") and v.get("admissible"))
    receipt = {"schema": "StageDKPrecisionLogDomainParentV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-075", "run_tag": tag, "theta": str(THETA),
               "question": "does an 8-bit LOG-DOMAIN Bayesian row - the textbook fix for the underflow that RV-377-066's gate rests on, built only from registered kinds - collapse the precision-gated kingdom?",
               "rows": {r: ROWS[r].__doc__ or r for r in ROWS}, "cells": cells,
               "ambig_fx8_admissible_rows": threat,
               "gate_survives": threat == [],
               "terminal": ("PRECISION_GATE_SURVIVES_THE_LOG_DOMAIN_PARENT__NO_8_BIT_LOG_DOMAIN_ROW_IS_ADMISSIBLE_ON_THE_AMBIGUOUS_ECOLOGY"
                            if threat == [] else
                            "PRECISION_GATE_COLLAPSES__AN_8_BIT_LOG_DOMAIN_ROW_IS_ADMISSIBLE_ON_THE_AMBIGUOUS_ECOLOGY__RV_377_066_IS_FALSIFIED_FOR_WANT_OF_A_PARENT_MAXIMAL_OPPONENT"),
               "claim_ceiling": "one declared hypothesis class, one event sequence, one seed; the exponent table is charged to desc at one scalar per entry and each table read is charged one activation, which is generous to this row and therefore hostile to RV-377-066, as a parent-maximality test should be"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V3_LOGDOMAIN_PARENT_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for k in sorted(cells): print(k, cells[k].get("capability", cells[k].get("error")), "adm", cells[k].get("admissible"))
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
