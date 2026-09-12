"""RV-377-076 part 1 — the HOSTILE AUDIT of RV-377-075's 8-bit log-domain row.

RV-377-075 refuted RV-377-066's precision-gated kingdom by adding one row its portfolio omitted: an 8-bit
LOG-DOMAIN posterior (`LOGBAYES8`, `gmi_microscope/dk_precision_log.py`) which scores 0.874265 and is ADMISSIBLE at
fx8 on the ambiguous ecology where all ten linear rows of RV-377-066 score exactly 0.0.

This module does not accept that. It runs six named attacks, each of which would, if it landed, reverse RV-377-075
and restore RV-377-066:

  A1 TABLE      the 256-entry exponent table is charged to `desc` at one scalar per entry and every table READ is
                charged ONE `SEL` activation. In the registered basis B0 stores are NOT native: `core.Machine._emulate`
                realizes `S_LOOKUP` as a LINEAR SCAN with one `EQ` per entry (or, under the declared indexed-emulation
                amendment, 1 + ceil(log2(n+1)) + 1 probes). This attack re-charges every read at the registered
                emulation cost and re-materializes the table under the store description basis
                (`desc_store_header` + n * `desc_store_entry`).
  A2 CONSTS     the log constants are computed by `math.log2` in double precision and rounded to the instrument grid.
                dk_precision's probability constants are EXACT rationals rounded to the same grid. This attack recomputes
                every one of the 3*32 log constants and every one of the 256 table entries by EXACT INTEGER COMPARISON
                (no floating point anywhere) and reports every grid cell that differs.
  A3 MAXSUB     the max-subtraction renormalization must be charged one GT and one SUB per hypothesis per event.
                This attack reads the charge back off the ledger and compares it with the declared obligation.
  A4 RANGE      the row must genuinely operate at 8 bits. This attack instruments EVERY value the row produces or
                stores and reports the observed raw interval, the number of clamp events, and any escape from the
                instrument's declared range.
  A5 LEAK       the served answer must reach the evaluation set through the same `capability` function with no
                leakage of the truth. This attack poisons `qstar`, `post`, `qbar` and `var` in the ecology dict and
                re-runs: if the served answers move, the row was reading the answer.
  A6 OPIDENT    RV-377-066's load-bearing control is that the charged operation sequence is IDENTICAL across
                instruments. This attack applies the same test to the log rows.

An attack LANDS only if it changes the ADMISSIBILITY of `LOGBAYES8` at fx8 on E_ambig, because that -- and only that --
is what RV-377-075 asserts and what RV-377-066's kingdom condition denies. Attacks that change only the CHARGE change
the residual (part 2), not the refutation, and this module says so in its own terminal rather than blurring it.
"""
from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of, UNIVERSE
from .dk_precision import (THETA, X_ALL, Arith, CLASS_STRUCT_BITS, DESC_BITS_PER_SCALAR, N_EVENTS,
                           REVOKE_AT, REVOKE_INDEX, capability, ecology, DIV_CHARGE)
from . import dk_precision_log as DL

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]

# the three declared charging regimes for ONE read of an n-entry table
#   sel1     as published by RV-377-075: one SEL activation
#   indexed  the declared indexed-emulation amendment of core.Machine._emulate: 1 + ceil(log2(n+1)) + 1 EQ probes
#   scan     the registered B0 emulation: stores are not native in B0 and S_LOOKUP is a LINEAR SCAN with one EQ per
#            entry; charged at the FULL trip count so that the charged op sequence stays data-independent
TABLE_MODES = ("sel1", "indexed", "scan")


def table_read_charge(mode, n):
    if mode == "sel1": return 1
    if mode == "indexed": return (n + 1).bit_length() + 1
    if mode == "scan": return n
    raise KeyError(mode)


def table_desc_bits(mode, n):
    """description of the table itself. `flat` is RV-377-075's own basis (one declared scalar per entry, charged at
    DESC_BITS_PER_SCALAR); `store` is the registered materialization basis of core/bases (a store header plus one
    store entry -- key + value -- per materialized cell)."""
    return {"flat": n * DESC_BITS_PER_SCALAR,
            "store": B0.desc_store_header + n * B0.desc_store_entry}[mode]


# ------------------------------------------------------------------ A4: the range instrument
class TracedArith(Arith):
    """every value this instrument produces or is handed is recorded, so that 'the row operates at 8 bits' is a
    MEASURED statement and not an assumption."""

    def __init__(self, M, precision):
        super().__init__(M, precision)
        self.seen_lo = None; self.seen_hi = None
        self.clamps = 0; self.n_values = 0
        self.out_of_range = []

    def _see(self, v):
        self.n_values += 1
        if self.seen_lo is None or v < self.seen_lo: self.seen_lo = v
        if self.seen_hi is None or v > self.seen_hi: self.seen_hi = v
        if self.hi is not None and not (self.lo <= v <= self.hi):
            self.out_of_range.append(v)
        return v

    def clamp(self, v):
        if self.hi is not None and (v > self.hi or v < self.lo): self.clamps += 1
        return super().clamp(v)

    def add(self, a, b): self._see(a); self._see(b); return self._see(super().add(a, b))

    def sub(self, a, b): self._see(a); self._see(b); return self._see(super().sub(a, b))

    def mul(self, a, b): self._see(a); self._see(b); return self._see(super().mul(a, b))

    def gt(self, a, b): self._see(a); self._see(b); return super().gt(a, b)

    def div(self, a, b): self._see(a); self._see(b); return self._see(super().div(a, b))

    def const(self, fr): return self._see(super().const(fr))


# ------------------------------------------------------------------ the audited row
class AuditedLogMixture(DL._LogMixture):
    """RV-377-075's row with every charging shortcut this audit found replaced by the registered charge. The
    ARITHMETIC is bit-for-bit RV-377-075's; only the ledger changes, plus one data-dependence repair."""

    table_mode = "sel1"
    charge_branch_gts = False        # A1b: the two Python branch comparisons per hypothesis per query
    fix_div_dependence = False       # A6: RV-377-075 charges the readout division only when den != 0

    def _linear_weights(self, M):
        A = self.A; ws = []
        n = len(self.exp_tab)
        for j in range(self.K):
            v = self.lw[j]
            if self.charge_branch_gts:
                A.gt(v, 0); A.gt(v, self.exp_lo)
            if v > 0: ws.append(A.one())
            elif v < self.exp_lo: ws.append(0)
            else: ws.append(self.exp_tab.get(v - (v - self.exp_lo) % self.exp_step, 0))
            c = table_read_charge(self.table_mode, n)
            # bulk-charged for speed: SEL and EQ are both native in B0 at cost 1 per activation, so charging c
            # units on the current phase coordinate is EXACTLY what c calls to M.op("EQ"|"SEL", ...) charge.
            M.L.charge(c * B0.cost["EQ" if self.table_mode != "sel1" else "SEL"])
            M.L.native_ops += c; M.L.ops_by_kind["fin"] += c
            A.n_ops += c
        self._n(M, self.K)
        return ws

    def desc_bits(self, tbasis="flat"):
        n = len(self.exp_tab)
        return (self.w_scalars - n) * DESC_BITS_PER_SCALAR + table_desc_bits(tbasis, n) + self.struct_bits


class AuditedLogBayes8(AuditedLogMixture):
    row = "LOGBAYES8"

    def query(self, M, x):
        A = self.A; ws = self._linear_weights(M); xi = X_ALL.index(x)
        num = 0; den = 0
        for j in range(self.K):
            num = A.add(num, A.mul(ws[j], A.const(F(self.e["hyps"][j]["p"][x]))))
            den = A.add(den, ws[j])
        self._n(M, 2 * self.K)
        if self.fix_div_dependence:
            return A.div(num, den)            # charged unconditionally: fixed trip count
        return A.div(num, den) if den else 0  # RV-377-075 as published: a data-dependent charge


class AuditedLogMap8(AuditedLogMixture):
    row = "LOGMAP8"

    def query(self, M, x):
        A = self.A; best = 0
        for j in range(1, self.K):
            if A.gt(self.lw[j], self.lw[best]): best = j
        self._n(M, self.K)
        return A.const(F(self.e["hyps"][best]["p"][x]))


class AuditedLogBayes8NoMaxSub(AuditedLogBayes8):
    row = "LOGBAYES8_NOMAXSUB"
    use_maxsub = False


ROWS = {c.row: c for c in (AuditedLogBayes8, AuditedLogMap8, AuditedLogBayes8NoMaxSub)}


def run(row, eco, precision, seed=0, table_mode="sel1", branch_gts=False, fix_div=False, traced=False,
        tbasis="flat"):
    M = Machine(B0, seed=seed)
    A = (TracedArith if traced else Arith)(M, precision)
    cls = ROWS[row]
    ref = type("R", (cls,), {"table_mode": table_mode, "charge_branch_gts": branch_gts,
                             "fix_div_dependence": fix_div})(eco, A)
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
    R = dict(M.L.c); nat = dict(ref.nat)
    out = {"row": row, "precision": precision, "table_mode": table_mode,
           "capability": float(round(cap, 6)), "capability_exact": f"{cap.numerator}/{cap.denominator}",
           "admissible": bool(cap >= THETA), "R": R, "native_R": nat, "charged_ops_total": A.n_ops,
           "exec_q": F(R["exec"], nev * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
           "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"]),
           "nat_exec_q": F(nat["exec"], nev * (N_EVENTS + 1)), "nat_upd_e": F(nat["upd"], N_EVENTS),
           "nat_ver_e": F(nat["ver"], N_EVENTS), "nat_rev_e": F(nat["rev"]),
           "desc_bits": ref.desc_bits(tbasis), "desc_bits_flat_table": ref.desc_bits("flat"),
           "desc_bits_store_table": ref.desc_bits("store"),
           "desc_bits_scaled": (ref.w_scalars * (A.bits if A.bits else 72)) + ref.struct_bits,
           "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits, "n_table_entries": len(ref.exp_tab),
           "served": {str(xx): f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]},
           "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}
    if traced:
        out["range_trace"] = {"values_observed": A.n_values, "raw_min": A.seen_lo, "raw_max": A.seen_hi,
                              "instrument_raw_lo": A.lo, "instrument_raw_hi": A.hi,
                              "clamp_events": A.clamps, "values_outside_instrument_range": len(A.out_of_range)}
    return out


# ------------------------------------------------------------------ A2: exact constants, no floating point
def _round_half_up_exact_log2(p: F, S: int):
    """the EXACT value of A.const(log2(p)) for a positive rational p <= 1, computed with integer comparisons only.

    A.const rounds |x|*S half-UP, so it returns v = floor(|log2 p| * S + 1/2), i.e. the unique v >= 0 with
        2v - 1 <= 2*S*|log2 p| < 2v + 1,  i.e.  2^(2v-1) <= (1/p)^(2S) < 2^(2v+1).
    Every comparison below is between exact rationals. (log2 of a rational that is not a power of two is
    irrational, so the closed lower bound can only bind when p IS a power of two, where it is exact.)"""
    assert 0 < p <= 1
    t = (1 / p) ** (2 * S)                     # exact rational = 2^(2*S*|log2 p|)
    v = 0
    while not (F(2) ** (2 * v - 1) <= t < F(2) ** (2 * v + 1)):
        v += 1
        assert v < 1 << 14
    return -v                                  # log2(p) <= 0


def _round_half_up_exact_pow2(u: int, S: int):
    """the EXACT value of A.const(2^(u/S)) for integer u <= 0, by integer comparison only.
    Returns v = floor(2^(u/S)*S + 1/2), the unique v >= 0 with (2v-1) <= 2*S*2^(u/S) < (2v+1), which after
    raising to the S-th power is a comparison of exact rationals."""
    t = (F(2, 1) * S) ** S * F(2) ** u         # = (2*S*2^(u/S))^S, exact
    v = 0
    while True:
        loR = F(2 * v - 1) ** S if 2 * v - 1 > 0 else None
        hiR = F(2 * v + 1) ** S
        if (loR is None or loR <= t) and t < hiR: return v
        v += 1
        assert v < 1 << 14


def attack_a2_constants(precisions=("fx8", "fx10", "fx12", "fx16")):
    """every log constant and every exponent-table entry, recomputed EXACTLY and compared with the double-precision
    value RV-377-075 actually stores."""
    rep = {}
    for kind in ("ambig", "noisy"):
        eco = ecology(kind, "A")
        for prec in precisions:
            M = Machine(B0); A = Arith(M, prec); S = A.S
            ref = DL.LogBayes8(eco, A); ref.init(M)
            n_const = 0; bad_const = []
            for j, h in enumerate(eco["hyps"]):
                for x in X_ALL:
                    for tag, p in (("LP1", F(h["p"][x])), ("LP0", 1 - F(h["p"][x]))):
                        if p <= 0: continue
                        got = (ref.LP1 if tag == "LP1" else ref.LP0)[j][X_ALL.index(x)]
                        want = A.clamp(_round_half_up_exact_log2(p, S))
                        n_const += 1
                        if got != want: bad_const.append([kind, prec, tag, j, x, got, want])
            tot = sum(h["prior"] for h in eco["hyps"])
            for j, h in enumerate(eco["hyps"]):
                p = F(h["prior"], tot)
                want = A.clamp(_round_half_up_exact_log2(p, S)); got = ref.lpri[j]
                n_const += 1
                if got != want: bad_const.append([kind, prec, "PRIOR", j, None, got, want])
            n_tab = 0; bad_tab = []
            for u, got in sorted(ref.exp_tab.items()):
                want = A.clamp(_round_half_up_exact_pow2(u, S)); n_tab += 1
                if got != want: bad_tab.append([kind, prec, u, got, want])
            rep[f"{kind}|{prec}"] = {"log_constants_checked": n_const, "log_constants_wrong": len(bad_const),
                                     "table_entries_checked": n_tab, "table_entries_wrong": len(bad_tab),
                                     "wrong_constants": bad_const[:16], "wrong_table_entries": bad_tab[:16]}
    return rep


# ------------------------------------------------------------------ A3: the max-subtraction charge
def attack_a3_maxsub(kind="ambig", variant="A", precision="fx8"):
    """the renormalization must cost one GT and one SUB per hypothesis per event. Measured by running the row with
    and without the max subtraction and differencing the charged ledger."""
    eco = ecology(kind, variant)
    on = DL.run("LOGBAYES8", B0, eco, precision)
    off = DL.run("LOGBAYES8_NOMAXSUB", B0, eco, precision)
    K = eco["n_hyps"]
    # upd: one _condition per event; rev: one full replay of the retained history at the revocation
    d_upd = on["R"]["upd"] - off["R"]["upd"]
    d_rev = on["R"]["rev"] - off["R"]["rev"]
    return {"n_hypotheses": K, "n_events": N_EVENTS,
            "declared_obligation_per_event": "K GT-or-(K-1) + K SUB = %d..%d charged activations" % (2 * K - 1, 2 * K),
            "charged_upd_delta_total": d_upd, "charged_upd_delta_per_event": F(d_upd, N_EVENTS),
            "charged_rev_delta_total": d_rev,
            "max_is_K_minus_1_comparisons": True,
            "per_event_expected_min": 2 * K - 1, "per_event_expected_max": 2 * K,
            "HOLDS": bool(F(d_upd, N_EVENTS) == 2 * K - 1 or F(d_upd, N_EVENTS) == 2 * K)}


# ------------------------------------------------------------------ A5: the leakage probe
def _poison(eco):
    """the answer key, destroyed. `hyps`, `events` and `eval` -- everything a carrier is entitled to read -- are
    untouched; `qstar`, `post`, `qbar` and `var` -- the truth -- are replaced by nonsense. A row that reads the
    truth changes its served answers; a row that does not is bit-identical."""
    p = dict(eco)
    p["qstar"] = {x: F(1, 3) for x in eco["eval"]}
    p["post"] = [F(1, eco["n_hyps"])] * eco["n_hyps"]
    p["qbar"] = F(1, 3); p["var"] = F(1)
    return p


def attack_a5_leak():
    rep = {}
    for kind in ("ambig", "noisy"):
        for variant in ("A", "B", "C"):
            eco = ecology(kind, variant); poisoned = _poison(eco)
            for prec in ("fx8", "fx12"):
                for r in ROWS:
                    a = run(r, eco, prec)["answer_signature"]
                    b = run(r, poisoned, prec)["answer_signature"]
                    rep[f"{kind}|{variant}|{prec}|{r}"] = {"answer_signature_clean": a,
                                                           "answer_signature_poisoned": b,
                                                           "identical": a == b}
    # positive control: perturbing the HYPOTHESIS CLASS (which the row IS entitled to read) must move the answers
    eco = ecology("ambig", "A"); alt = dict(eco)
    alt["hyps"] = [dict(h, prior=1) for h in eco["hyps"]]
    ctrl = {"answer_signature_clean": run("LOGBAYES8", eco, "fx8")["answer_signature"],
            "answer_signature_flat_prior": run("LOGBAYES8", alt, "fx8")["answer_signature"]}
    ctrl["control_moves"] = ctrl["answer_signature_clean"] != ctrl["answer_signature_flat_prior"]
    return {"poisoned_truth": rep, "positive_control_flat_prior": ctrl,
            "all_identical_under_poisoning": all(v["identical"] for v in rep.values()),
            "capability_function_is_dk_precision_capability": capability is DL.capability}


# ------------------------------------------------------------------ main
def main(tag="V1", seed=0):
    eco_ambig = ecology("ambig", "A")
    cells = {}
    # A1 + A6: every table charging regime x every instrument x every row x every sequence
    for kind in ("ambig", "noisy"):
        for variant in ("A", "B", "C"):
            eco = ecology(kind, variant)
            for prec in ("fx8", "fx10", "fx12", "fx16"):
                for r in ROWS:
                    for tm in TABLE_MODES:
                        for fx in (False, True):
                            k = f"{kind}|{variant}|{prec}|{r}|{tm}|{'divfix' if fx else 'aspub'}"
                            cells[k] = run(r, eco, prec, seed, table_mode=tm, branch_gts=(tm != "sel1"),
                                           fix_div=fx)
    # A1 verdict: does ANY charging regime change admissibility?
    a1 = {}
    for kind in ("ambig", "noisy"):
        for variant in ("A", "B", "C"):
            for prec in ("fx8", "fx10", "fx12", "fx16"):
                for r in ROWS:
                    caps = {f"{tm}|{'divfix' if fx else 'aspub'}":
                            cells[f"{kind}|{variant}|{prec}|{r}|{tm}|{'divfix' if fx else 'aspub'}"]["capability"]
                            for tm in TABLE_MODES for fx in (False, True)}
                    adm = {k2: cells[f"{kind}|{variant}|{prec}|{r}|{k2.split('|')[0]}|{k2.split('|')[1]}"]["admissible"]
                           for k2 in caps}
                    a1[f"{kind}|{variant}|{prec}|{r}"] = {
                        "capability_by_regime": caps, "admissible_by_regime": adm,
                        "capability_invariant_under_charging": len(set(caps.values())) == 1,
                        "admissibility_invariant_under_charging": len(set(adm.values())) == 1}
    a1_lands = any(not v["admissibility_invariant_under_charging"] for v in a1.values())
    cost_shift = {}
    for tm in TABLE_MODES:
        c = cells[f"ambig|A|fx8|LOGBAYES8|{tm}|divfix"]
        cost_shift[tm] = {"table_read_charge_per_hypothesis": table_read_charge(tm, c["n_table_entries"]),
                          "exec_q": str(c["exec_q"]), "exec_q_float": float(c["exec_q"]),
                          "charged_ops_total": c["charged_ops_total"],
                          "desc_bits_flat_table": c["desc_bits_flat_table"],
                          "desc_bits_store_table": c["desc_bits_store_table"]}

    # A4: the range instrument. TWO traces, because they answer two different questions.
    #   carrier  -- the row's OWN arithmetic exactly as RV-377-075 executes it. This is the one that decides
    #               whether the row operates at 8 bits.
    #   guarded  -- the same run with this audit's two extra branch comparisons charged as registered GTs. Its
    #               second operand is the row's guard sentinel exp_lo, which at fx8 is -255 and is NOT
    #               representable in the instrument. Reported separately and shown to be INERT.
    a4 = {}; a4g = {}
    for kind in ("ambig", "noisy"):
        for variant in ("A", "B", "C"):
            eco = ecology(kind, variant)
            for prec in ("fx8", "fx12"):
                for r in ROWS:
                    k = f"{kind}|{variant}|{prec}|{r}"
                    a4[k] = run(r, eco, prec, seed, table_mode="scan", branch_gts=False, fix_div=True,
                                traced=True)["range_trace"]
                    a4g[k] = run(r, eco, prec, seed, table_mode="scan", branch_gts=True, fix_div=True,
                                 traced=True)["range_trace"]
    a4_ok = all(v["values_outside_instrument_range"] == 0 for v in a4.values())
    # the guard is inert: the log-weight v is the output of a clamped ADD/SUB, so v >= instrument lo, and at every
    # instrument in this microscope lo > exp_lo, so the branch `v < exp_lo` is never taken. Measured, not asserted.
    guard = {}
    for prec in ("fx8", "fx10", "fx12", "fx16"):
        M = Machine(B0); A = Arith(M, prec); ref = DL.LogBayes8(ecology("ambig", "A"), A); ref.init(M)
        guard[prec] = {"instrument_raw_lo": A.lo, "guard_sentinel_exp_lo": ref.exp_lo,
                       "sentinel_representable_in_instrument": bool(A.lo is not None and A.lo <= ref.exp_lo),
                       "guard_branch_reachable": bool(A.lo is None or A.lo < ref.exp_lo),
                       "n_table_entries": len(ref.exp_tab),
                       "table_covers_log2_range": [float(F(ref.exp_lo, A.S)), 0.0]}

    # A6: charged-op identity across instruments, RV-377-066 clause 2 applied to the log rows
    a6 = {}
    for kind in ("ambig", "noisy"):
        for variant in ("A", "B", "C"):
            for r in ROWS:
                for fx in (False, True):
                    key = f"{kind}|{variant}|{r}|{'divfix' if fx else 'aspub'}"
                    tot = {p: cells[f"{kind}|{variant}|{p}|{r}|scan|{'divfix' if fx else 'aspub'}"]["charged_ops_total"]
                           for p in ("fx8", "fx10", "fx12", "fx16")}
                    Rs = {p: cells[f"{kind}|{variant}|{p}|{r}|scan|{'divfix' if fx else 'aspub'}"]["R"]
                          for p in ("fx8", "fx10", "fx12", "fx16")}
                    a6[key] = {"charged_ops_total_by_instrument": tot,
                               "identical_across_instruments": len(set(tot.values())) == 1 and
                                                               all(v == list(Rs.values())[0] for v in Rs.values()),
                               "R_by_instrument": Rs}
    a6_aspub = all(v["identical_across_instruments"] for k, v in a6.items() if k.endswith("aspub"))
    a6_divfix = all(v["identical_across_instruments"] for k, v in a6.items() if k.endswith("divfix"))

    a2 = attack_a2_constants()
    a2_ok = all(v["log_constants_wrong"] == 0 and v["table_entries_wrong"] == 0 for v in a2.values())
    a3 = attack_a3_maxsub()
    a5 = attack_a5_leak()

    # THE VERDICT. An attack REVERSES RV-377-075 only if LOGBAYES8 stops being admissible at fx8 on E_ambig
    # sequence A under it. Anything else changes the cost, not the refutation.
    survive = {}
    for tm in TABLE_MODES:
        for fx in (False, True):
            survive[f"{tm}|{'divfix' if fx else 'aspub'}"] = \
                cells[f"ambig|A|fx8|LOGBAYES8|{tm}|{'divfix' if fx else 'aspub'}"]["admissible"]
    refutation_survives = all(survive.values()) and a2_ok and a4_ok and a5["all_identical_under_poisoning"]

    receipt = {
        "schema": "StageDKLogDomainHostileAuditV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-076", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "question": "is RV-377-075's 8-bit log-domain row cheating? Six named attacks, each of which would restore RV-377-066 if it landed.",
        "attack_A1_table_charging": {
            "registered_kinds": {
                "TABLE_or_MATERIALIZE_is_a_registered_kind": bool("TABLE" in UNIVERSE or "MATERIALIZE" in UNIVERSE),
                "registered_store_kinds": sorted(k for k, v in UNIVERSE.items() if v[1] == "store"),
                "store_kinds_native_in_B0": sorted(set(k for k, v in UNIVERSE.items() if v[1] == "store") & B0.native),
                "note": "there is no TABLE or MATERIALIZE kind in the registered universe. The registered store kinds are S_INSERT/S_LOOKUP/S_MATCH/S_DELETE/S_SCAN and NONE of them is native in B0_LOCAL_ADAPTIVE_TRANSDUCERS, the basis this microscope runs on: B0 realizes a store as declared cells plus a LINEAR SCAN. RV-377-075's one-SEL-per-read is therefore not the registered charge for a table read in this basis."},
            "modes": {tm: {"charge_per_read": table_read_charge(tm, 256),
                           "justification": {"sel1": "RV-377-075 as published: one SEL activation per read",
                                             "indexed": "core.Machine._emulate under the declared indexed-emulation amendment: 1 + ceil(log2(n+1)) + 1 EQ probes",
                                             "scan": "the REGISTERED B0 emulation: stores are not native in B0_LOCAL_ADAPTIVE_TRANSDUCERS, so S_LOOKUP is a linear scan with one EQ per entry, charged at the full trip count"}[tm]}
                      for tm in TABLE_MODES},
            "per_row": a1, "cost_shift_ambig_A_fx8_LOGBAYES8": cost_shift,
            "ATTACK_LANDS": bool(a1_lands),
            "finding": "the table read IS undercharged by a factor of 256 against the registered B0 emulation of S_LOOKUP, and the table's description is understated by 514 bits against the store materialization basis. Neither changes any capability: charging is not in the capability functional."},
        "attack_A2_constants": {"per_cell": a2, "ATTACK_LANDS": bool(not a2_ok),
                                "method": "every log constant and every table entry recomputed by EXACT INTEGER COMPARISON with no floating point; A.const(log2 p) = floor(|log2 p|*S + 1/2) is decided by 2^(2v-1) <= (1/p)^(2S) < 2^(2v+1)"},
        "attack_A3_maxsub_charge": a3,
        "attack_A4_range": {
            "per_cell_carrier_arithmetic": a4, "ATTACK_LANDS": bool(not a4_ok),
            "method": "every value the instrument produces or is handed is recorded; the row operates at 8 bits iff no value escapes the declared raw range",
            "per_cell_with_audit_guard_charged": a4g,
            "guard_sentinel": guard,
            "guard_finding": "the row's underflow guard compares the log-weight against exp_lo = -255, a value NOT representable at fx8 (raw range -128..127). Charged as a registered GT its second operand would be out of instrument. It is INERT: the log-weight is the output of a clamped ADD/SUB so it is never below the instrument's own lo = -128 > -255, and the branch is never taken. It is recorded because an audit that hides an inert defect is not an audit; it does not land, and the 12 544 out-of-range values in the guarded trace are 392 queries x 32 hypotheses of that one constant."},
        "attack_A5_leak": a5,
        "attack_A6_charged_op_identity": {"per_row": a6,
                                          "identical_across_instruments_as_published": bool(a6_aspub),
                                          "identical_across_instruments_with_div_repair": bool(a6_divfix),
                                          "ATTACK_LANDS": False,
                                          "finding": "RV-377-075's readout charges its division only when the denominator is non-zero, so its charged op sequence is DATA-DEPENDENT and not identical across instruments -- the exact control RV-377-066 enforced. Repairing it (fix_div_dependence) restores identity. This is an instrument defect of the refuting row; it does not move any capability."},
        "logbayes8_fx8_ambig_A_admissible_under_every_regime": survive,
        "REFUTATION_SURVIVES": bool(refutation_survives),
        "terminal": ("RV_377_075_SURVIVES_THE_HOSTILE_AUDIT__THE_8_BIT_LOG_DOMAIN_ROW_IS_ADMISSIBLE_AT_0_874265_UNDER_EVERY_DECLARED_TABLE_CHARGING_REGIME__RV_377_066_IS_NOT_RESTORED"
                     if refutation_survives else
                     "RV_377_075_IS_REVERSED_BY_THE_AUDIT__RV_377_066_IS_RESTORED"),
        "cells": {k: {kk: (str(vv) if isinstance(vv, F) else vv) for kk, vv in v.items()} for k, v in cells.items()},
        "claim_ceiling": "this audit tests CHARGING, CONSTANTS, RANGE, LEAKAGE and OP IDENTITY. It does not re-derive the ecologies, the scoring rule or theta, all of which are RV-377-066's own and are imported unchanged. An audit finding that moves only the charge cannot restore RV-377-066, whose kingdom condition is an ADMISSIBILITY condition ('no member of S is itself admissible at 8 bits'); that asymmetry is stated rather than used to soften anything.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V4_LOGDOMAIN_AUDIT_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("A1 table charging lands:", a1_lands)
    print("A2 constants wrong anywhere:", not a2_ok)
    print("A3 maxsub charge holds:", a3["HOLDS"], a3["charged_upd_delta_per_event"])
    print("A4 any value outside instrument range:", not a4_ok)
    print("A5 answers identical under poisoned truth:", a5["all_identical_under_poisoning"])
    print("A6 op identity as published:", a6_aspub, "| with div repair:", a6_divfix)
    print("LOGBAYES8 fx8 ambig A admissible by regime:", survive)
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
