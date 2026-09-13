"""RV-377-077 — the 8-bit log row in its BEST possible form, and whether that turns the residual positive.

RV-377-076 executed a negative: on the ambiguous ecology the 8-bit log-domain row holds 0 of 42, 0 of 49, 0 of 294
and 0 of 899 cross-instrument frontier cells, because it costs 3 104 description bits and 208 charged activations
per query against 596 and 12 for `QCOUNT@fx10`. That negative is only worth having if the 8-bit row was given its
BEST form first, and it was not. `RV-377-075` built the row to answer a capability question and never optimised it.
Three things are wrong with its cost, and all three are the audit's to fix, not the row's to keep:

  (i)  DESCRIPTION PADDING. It declares `3*K = 96` scalars of log constants for a class that contains only SEVEN
       distinct likelihood values (`VALS_AMBIG` has 4 value pairs; 1/2 appears twice) and THREE distinct priors.
       The hypothesis -> (predicate, value-pair) map is already paid for inside `CLASS_STRUCT_BITS`.
  (ii) AN ACCOUNTING ASYMMETRY. `dk_precision._Mixture` materializes 32 x 16 = 512 probability constants and
       declares `w_scalars = K = 32` -- it charges its constants to `struct`, not to scalars. The log row charges
       the same kind of constant to scalars. Both conventions are reported here as declared sensitivity columns;
       neither is asserted to be the right one.
  (iii) A TABLE WHERE A LADDER WOULD DO. The 256-entry exponent table spans log2 values the fx8 instrument cannot
       hold (u < -128 is unreachable) and maps everything below u = -80 to zero, so at most 81 entries carry
       information. And the output takes only `S + 1 = 17` distinct values, so the whole map is determined by `S`
       monotone BREAKPOINTS -- a comparison ladder of 16 declared scalars, built from `GT` and `ADD`, which needs
       no store at all and is therefore immune to protocol rule 25's linear-scan charge.

Rows (every one is `RV-377-075`'s arithmetic, bit for bit; only the declaration and the charge change):

  LOGBAYES8_FIXED   the published row with RV-377-076's two defects repaired: the readout division is charged
                    unconditionally (restoring charged-op identity across instruments) and the op counter counts
                    the table reads it already pays for.
  LOGMIN8           + minimal description: 8 log-likelihood constants and 3 log priors instead of 96.
  LOGTRIM8          + the exponent table trimmed to the entries the instrument can reach.
  LOGLAD8           + the exponent LADDER: S declared breakpoints, read as S GT and S-1 ADD, no store.
  LOGLAD8_T4        + top-M pruning of the readout, the device BAYESM and QCOUNT already use.

The question this module decides: after every one of those, does ANY 8-bit row occupy ANY cross-instrument
frontier cell on the ambiguous ecology? If yes, precision buys nothing at all and RV-377-076's residual is
overturned. If no, the residual is confirmed against a parent-maximal version of its own subject.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of
from .dk_precision import (THETA, X_ALL, Arith, CLASS_STRUCT_BITS, DESC_BITS_PER_SCALAR, M_TOP, N_EVENTS,
                           REVOKE_AT, REVOKE_INDEX, capability, ecology, per_event, cost, crossovers, grid_from,
                           ROWS as LIN_ROWS, run as lin_run)
from . import dk_precision_log_audit as AU
from . import dk_precision_residual as RS

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
INSTRUMENTS = ("fx8", "fx10", "fx12", "fx16", "fx24", "fx32", "wide")


def distinct_constants(eco):
    """the log constants a MINIMAL declaration actually needs: one per distinct likelihood value and one per
    distinct prior. The hypothesis -> (predicate, value-pair) map is already inside CLASS_STRUCT_BITS."""
    vals = set()
    for h in eco["hyps"]:
        for x in X_ALL:
            p = F(h["p"][x]); vals.add(p); vals.add(1 - p)
    tot = sum(h["prior"] for h in eco["hyps"])
    pri = {F(h["prior"], tot) for h in eco["hyps"]}
    return len(vals), len(pri)


class MinLogMixture(AU.AuditedLogMixture):
    """RV-377-075's log-domain carrier with a declared description convention, a declared exponent encoding and
    optional top-M readout pruning. The ARITHMETIC is unchanged."""

    exp_encoding = "table_full"        # table_full | table_trim | ladder
    desc_convention = "as_published"   # as_published | linear
    top_m = None                       # None = the full 32-wide readout; 4 = the device BAYESM and QCOUNT use
    table_mode = "sel1"
    fix_div_dependence = True
    charge_branch_gts = False

    def init(self, M):
        super().init(M)
        A = self.A; S = A.S
        self.n_distinct_lik, self.n_distinct_pri = distinct_constants(self.e)
        if self.exp_encoding == "table_trim":
            lo = A.lo if A.lo is not None else self.exp_lo
            self.exp_tab = {u: v for u, v in self.exp_tab.items() if u >= lo and (v != 0 or u == lo)}
        if self.exp_encoding == "ladder":
            # the S monotone breakpoints of u -> round_half_up(S * 2^(u/S)). The map takes S+1 values, so S
            # thresholds determine it exactly; the assertion below proves the equivalence rather than assuming it.
            self.ladder = []
            for k in range(1, S + 1):
                b = None
                for u in range(self.exp_lo, 1):
                    if AU._round_half_up_exact_pow2(u, S) >= k: b = u; break
                self.ladder.append(b if b is not None else 1)
            for u in range(max(self.exp_lo, A.lo if A.lo is not None else self.exp_lo), 1):
                assert sum(1 for b in self.ladder if u >= b) == min(AU._round_half_up_exact_pow2(u, S), S), u
            n_exp = len(self.ladder)
        else:
            n_exp = len(self.exp_tab)
        self.n_exp = n_exp
        base = (3 * self.K) if self.desc_convention == "as_published" else self.K
        if self.desc_convention == "linear":
            # the log constants are charged to struct, exactly as _Mixture charges its 512 probability constants
            self.struct_bits = CLASS_STRUCT_BITS
            base = self.K
        elif self.desc_convention == "minimal":
            base = self.K + self.n_distinct_lik + self.n_distinct_pri
            self.struct_bits = CLASS_STRUCT_BITS
        self.w_scalars = base + n_exp + (self.top_m or 0)
        if self.top_m:
            self.struct_bits = self.struct_bits + self.top_m * 5
            self.top = list(range(self.top_m))

    # ---- the exponent map, under the declared encoding
    def _exp_of(self, M, v):
        A = self.A
        if self.exp_encoding == "ladder":
            n = len(self.ladder); acc = 0
            for b in self.ladder:
                if A.gt(v, b - 1): acc += 1       # charged GT per rung, fixed trip count
            for _ in range(n - 1): M.op("ADD", 0, 0); A.n_ops += 1
            return min(acc, A.S)
        if v > 0: return A.one()
        if v < self.exp_lo: w = 0
        else: w = self.exp_tab.get(v - (v - self.exp_lo) % self.exp_step, 0)
        c = AU.table_read_charge(self.table_mode, len(self.exp_tab))
        M.L.charge(c * B0.cost["EQ" if self.table_mode != "sel1" else "SEL"])
        M.L.native_ops += c; M.L.ops_by_kind["fin"] += c; A.n_ops += c
        return w

    def _rank(self, M):
        """top-M by log-weight, charged exactly as BAYESM's _rank charges it (fixed trip count, no early exit)."""
        A = self.A; used = []
        for _ in range(self.top_m):
            b = -1
            for j in range(self.K):
                g = A.gt(self.lw[j], self.lw[b] if b >= 0 else -(1 << 30))
                if j not in used and (b < 0 or g): b = j
            used.append(b)
        self.top = used
        self._n(M, self.K)

    def observe(self, M, x, y):
        super().observe(M, x, y)
        if self.top_m: self._rank(M)

    def revoke(self, M, idx, x, y):
        super().revoke(M, idx, x, y)
        if self.top_m: self._rank(M)

    def query(self, M, x):
        A = self.A
        idx = self.top if self.top_m else range(self.K)
        ws = [self._exp_of(M, self.lw[j]) for j in idx]
        self._n(M, len(ws))
        num = 0; den = 0
        for k, j in enumerate(idx):
            num = A.add(num, A.mul(ws[k], A.const(F(self.e["hyps"][j]["p"][x]))))
            den = A.add(den, ws[k])
        self._n(M, 2 * len(ws))
        return A.div(num, den)

    def desc_bits(self, tbasis="flat"):
        return self.w_scalars * DESC_BITS_PER_SCALAR + self.struct_bits


VARIANTS = {
    "LOGBAYES8_FIXED": dict(exp_encoding="table_full", desc_convention="as_published", top_m=None),
    "LOGMIN8":         dict(exp_encoding="table_full", desc_convention="minimal", top_m=None),
    "LOGTRIM8":        dict(exp_encoding="table_trim", desc_convention="minimal", top_m=None),
    "LOGLAD8":         dict(exp_encoding="ladder",     desc_convention="minimal", top_m=None),
    "LOGLAD8_T4":      dict(exp_encoding="ladder",     desc_convention="minimal", top_m=M_TOP),
    "LOGTRIM8_T4":     dict(exp_encoding="table_trim", desc_convention="minimal", top_m=M_TOP),
}


def run(name, eco, precision, seed=0, table_mode="sel1"):
    cfg = VARIANTS[name]
    M = Machine(B0, seed=seed); A = Arith(M, precision)
    cls = type("R", (MinLogMixture,), dict(cfg, row=name, table_mode=table_mode))
    ref = cls(eco, A)
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
    sfr = {xx: A.frac(ref.query(M, xx)) for xx in eco["eval"]}
    cap, excess = capability(eco, sfr)
    R = dict(M.L.c); nat = dict(ref.nat)
    return {"row": name, "precision": precision, "table_mode": table_mode,
            "capability": float(round(cap, 6)), "capability_exact": f"{cap.numerator}/{cap.denominator}",
            "admissible": bool(cap >= THETA), "R": R, "native_R": nat, "charged_ops_total": A.n_ops,
            "exec_q": F(R["exec"], nev * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
            "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"]),
            "nat_exec_q": F(nat["exec"], nev * (N_EVENTS + 1)), "nat_upd_e": F(nat["upd"], N_EVENTS),
            "nat_ver_e": F(nat["ver"], N_EVENTS), "nat_rev_e": F(nat["rev"]),
            "desc_bits": ref.desc_bits(), "desc_bits_scaled": ref.w_scalars * (A.bits or 72) + ref.struct_bits,
            "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits, "n_exp_scalars": ref.n_exp,
            "n_distinct_likelihood_constants": ref.n_distinct_lik, "n_distinct_prior_constants": ref.n_distinct_pri,
            "served": {str(xx): f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]},
            "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}


def main(tag="V1", seed=0, table_mode="sel1"):
    ecos = RS.all_ecologies()
    cells = {}
    for ek in ("ambig", "noisy"):
        for v in ("A", "B", "C", "D", "E"):
            eco = ecos[f"{ek}|{v}"]
            for p in ("fx8", "fx10", "fx12"):
                for name in VARIANTS:
                    cells[f"{ek}|{v}|{p}|{name}"] = run(name, eco, p, seed, table_mode)

    # the combined frontier: RV-377-066's ten linear rows + RV-377-075's three log rows + these six, all instruments
    front = {}; resid = {}; domin = {}
    for ekey in ("ambig|A", "noisy|A"):
        eco = ecos[ekey]
        port = RS.portfolio(eco, instruments=INSTRUMENTS, table_mode=table_mode)
        for p in ("fx8", "fx10", "fx12"):
            for name in VARIANTS: port[(name, p)] = cells[f"{ekey}|{p}|{name}"]
        adm = {p: sorted(r for (r, q) in port if q == p and port[(r, q)]["admissible"]) for p in INSTRUMENTS}
        for scaled in (False, True):
            for price in ("reduced", "native"):
                bas = "scaled" if scaled else "flat"
                pes = {f"{r}@{p}": per_event(port[(r, p)], price, scaled) for p in INSTRUMENTS for r in adm[p]}
                rep = RS.frontier_report(pes)
                key = f"{ekey}|{price}|{bas}"
                front[key] = rep
                occ = rep["occupancy"]
                fx8 = {n: c for n, c in occ.items() if n.endswith("@fx8") and c}
                resid[key] = {"n_cells": rep["n_cells"], "fx8_occupancy": fx8,
                              "cells_held_by_any_fx8_row": sum(fx8.values()),
                              "any_fx8_row_occupies": bool(fx8),
                              "occupancy_nonzero": {n: c for n, c in sorted(occ.items()) if c}}
                dm = {}
                for me in [n for n in pes if n.endswith("@fx8")]:
                    dom = sorted(n for n, pb in pes.items()
                                 if n != me and RS.dominates_cost(pb, pes[me]))
                    dm[me] = {"cost_coordinate_dominators": dom, "n_dominators": len(dom),
                              "desc": str(pes[me]["desc"]), "exec_q": str(pes[me]["exec_q"]),
                              "rho": str(RS.rho(pes[me]))}
                domin[key] = dm
        front[f"{ekey}|admissible_sets"] = adm

    positive = any(v["any_fx8_row_occupies"] for k, v in resid.items() if k.startswith("ambig"))
    receipt = {
        "schema": "StageDKLogMinimalDescriptionV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-077", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "table_charging_regime": table_mode,
        "question": "after minimal description, a trimmed table, a store-free exponent LADDER and top-M pruning, does ANY 8-bit row occupy ANY cross-instrument frontier cell on the ambiguous ecology?",
        "variants": {k: {kk: str(vv) for kk, vv in v.items()} for k, v in VARIANTS.items()},
        "cells": {k: {kk: (str(vv) if isinstance(vv, F) else vv) for kk, vv in v.items()} for k, v in cells.items()},
        "frontier": front, "residual": resid, "fx8_domination": domin,
        "ANY_FX8_ROW_OCCUPIES_ON_E_AMBIG": bool(positive),
        "terminal": ("PRECISION_BUYS_NOTHING__AN_8_BIT_ROW_OCCUPIES_A_CROSS_INSTRUMENT_CELL_ON_E_ambig__RV_377_076_RESIDUAL_OVERTURNED"
                     if positive else
                     "RESIDUAL_CONFIRMED_AGAINST_A_PARENT_MAXIMAL_8_BIT_ROW__NO_8_BIT_ROW_OCCUPIES_ANY_CROSS_INSTRUMENT_CELL_ON_E_ambig"),
        "claim_ceiling": "the six variants change only the DECLARATION and the CHARGE; the arithmetic is RV-377-075's bit for bit, except that top-M pruning changes the served answer and its capability is therefore measured, not assumed. Two description conventions are reported and neither is asserted correct.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V6_LOG_MINIMAL_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("== ambig|A at fx8 ==")
    for name in VARIANTS:
        c = cells[f"ambig|A|fx8|{name}"]
        print(f"  {name:18s} cap {c['capability']:<10} adm {str(c['admissible']):5s} desc {c['desc_bits']:<6}"
              f" scaled {c['desc_bits_scaled']:<6} exec_q {str(c['exec_q']):<8} w {c['w_scalars']} (exp {c['n_exp_scalars']})")
    for k in sorted(resid): print(k, "cells", resid[k]["n_cells"], "| fx8 holds", resid[k]["cells_held_by_any_fx8_row"], resid[k]["fx8_occupancy"])
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
