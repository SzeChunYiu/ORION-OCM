"""RV-377-078 — the ecology lever: does precision buy NOTHING where likelihood MAGNITUDE must be inferred?

RV-377-077 drove the precision residual on `E_ambig` down to its irreducible core: 156 excess description bits
and 56 excess charged activations per query for the best 8-bit log row against `QCOUNT@fx10`. The 8-bit row still
holds no cross-instrument cell, so on that ecology precision buys a small but real amount of description.

Every cell `QCOUNT` holds, it holds because of one structural fact: on `E_ambig` and `E_noisy` a hypothesis can be
reduced to its THRESHOLDED prediction without losing what the obligation needs. `QCount.init` builds
`expl[j][x] = 1 if p[x] >= 1/2 else 0` and counts agreements — the MAGNITUDE of the likelihood is discarded
entirely, and the ecologies are forgiving enough that it does not matter.

`E_graded` removes that forgiveness, and it is the textbook regime a strictly proper scoring rule exists for. The
declared value pairs are widened to (15/16, 1/16), (3/4, 1/4), (9/16, 7/16), (1/2, 1/2), and the declared flip
schedule is thinned to ONE flip in 24 events, so the posterior concentrates on an EXTREME value pair. Every value
pair of a predicate has the same thresholded prediction, so a count row cannot tell 15/16 from 9/16 even in
principle: it must serve the average of the pairs it cannot separate, while the correct answer is the extreme one.

PROTOCOL RULE 19 IS NOT WAIVED BECAUSE THIS ECOLOGY WAS BUILT TO BE HARD FOR A COUNT ROW. Two further opponents
are built specifically to survive it, both inside the registered 8-bit universe:

  QCOUNT2   the GRADED count row: instead of counting agreements it accumulates the declared likelihood itself,
            quantized to the instrument grid, so it keeps the magnitude a count row throws away. This is the
            strongest linear 8-bit opponent this lane can build for this ecology, and it is built BEFORE the
            verdict, not after.
  QCOUNT2M  the same accumulator with max-renormalization, the anti-underflow device BAYESM uses.

The question: on `E_graded`, does any row admissible in the registered 8-bit universe OCCUPY a cross-instrument
frontier cell? If the only admissible 8-bit row is the log-domain one AND it occupies, precision buys NOTHING
here, and the residual is an `E_ambig` property rather than a precision property.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of
from .dk_precision import (THETA, X_ALL, SEEN, UNSEEN, N_EVENTS, REVOKE_AT, REVOKE_INDEX, PREDS, PRED_PRIOR,
                           EVENT_SCALE, M_TOP, CLASS_STRUCT_BITS, Arith, _Mixture, QCount, capability,
                           per_event, ROWS as LIN_ROWS, run as lin_run)
from . import dk_precision_log_audit as AU
from . import dk_precision_log_min as LM
from . import dk_precision_residual as RS

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
INSTRUMENTS = ("fx8", "fx10", "fx12", "fx16", "fx24", "fx32", "wide")

# DECLARED, and declared for a reason that is stated rather than discovered: the pairs are widened so that the
# extreme pair is far from the mean of the pairs a count row cannot separate, and the flip schedule is thinned so
# the posterior actually concentrates on it. Both are properties of the ECOLOGY and are visible before any row runs.
VALS_GRADED = ((F(15, 16), F(1, 16)), (F(3, 4), F(1, 4)), (F(9, 16), F(7, 16)), (F(1, 2), F(1, 2)))
FLIPS_GRADED = {"A": (5,), "B": (11,), "C": (2,), "D": (17,), "E": (0,)}


def hyp_table_graded():
    hyps = []
    for pi, (pname, pf) in enumerate(PREDS):
        for vi, (hi, lo) in enumerate(VALS_GRADED):
            hyps.append({"pred": pname, "vi": vi, "prior": PRED_PRIOR[pi],
                         "p": {x: (hi if pf(x) else lo) for x in X_ALL}})
    return hyps


def ecology_graded(variant="A"):
    hyps = hyp_table_graded()
    truth = lambda x: (x >> 0) & 1
    flips = set(FLIPS_GRADED[variant])
    events = [(SEEN[i % len(SEEN)],
               (1 - truth(SEEN[i % len(SEEN)])) if i in flips else truth(SEEN[i % len(SEEN)]))
              for i in range(N_EVENTS)]
    ev_final = [e for i, e in enumerate(events) if i != REVOKE_INDEX]
    post = []
    for h in hyps:
        w = F(h["prior"])
        for x, y in ev_final: w *= h["p"][x] if y else (1 - h["p"][x])
        post.append(w)
    Z = sum(post); post = [w / Z for w in post]
    qstar = {x: sum(post[j] * hyps[j]["p"][x] for j in range(len(hyps))) for x in UNSEEN}
    qbar = sum(qstar.values()) / len(UNSEEN)
    var = sum((qstar[x] - qbar) ** 2 for x in UNSEEN)
    return {"kind": "graded", "variant": variant, "hyps": hyps, "events": events, "events_final": ev_final,
            "eval": UNSEEN, "post": post, "qstar": qstar, "qbar": qbar, "var": var, "n_hyps": len(hyps),
            "flips": sorted(flips)}


# ----------------------------------------------------------------- the parent-maximal opponents for THIS ecology
class QCountGraded(_Mixture):
    """THE GRADED COUNT ROW. QCOUNT reduces a hypothesis to `p[x] >= 1/2` and counts agreements, discarding the
    magnitude. This row keeps it: it accumulates the declared likelihood itself, quantized to the instrument grid,
    in units of 1/EVENT_SCALE, then keeps the top M and normalizes. It never multiplies likelihoods, so it cannot
    underflow, and it is the strongest LINEAR 8-bit opponent this lane can build for an ecology where magnitude
    is what must be inferred. Built before the verdict."""
    row = "QCOUNT2"
    use_max = False

    def init(self, M):
        super().init(M)
        A = self.A; K = self.e["n_hyps"]
        self.c = [0] * K
        self.top = list(range(M_TOP)); self.tw = [A.const(F(1, M_TOP))] * M_TOP
        self.w_scalars = K + M_TOP; self.struct_bits = CLASS_STRUCT_BITS + M_TOP * 5

    def _rank(self, M):
        A = self.A; K = self.e["n_hyps"]; used = []
        for _ in range(M_TOP):
            b = -1
            for j in range(K):
                g = A.gt(self.c[j], self.c[b] if b >= 0 else -(1 << 30))
                if j not in used and (b < 0 or g): b = j
            used.append(b)
        self.top = used
        if self.use_max:
            mx = self.c[used[0]]
            self.tw = [A.div(self.c[j], mx) if mx else self.c[j] for j in used]
            s = 0
            for w in self.tw: s = A.add(s, w)
            self.tw = [A.div(w, s) for w in self.tw]
        else:
            s = 0
            for j in used: s = A.add(s, self.c[j])
            self.tw = [A.div(self.c[j], s) for j in used]
        self._n(M, K)

    def _acc(self, M, x, y, sign):
        A = self.A
        for j in range(self.e["n_hyps"]):
            p = F(self.e["hyps"][j]["p"][x]); lk = A.const(p if y else 1 - p)
            d = A.mul(lk, A.const(F(1, EVENT_SCALE)))
            self.c[j] = A.add(self.c[j], d) if sign > 0 else A.sub(self.c[j], d)
        self._n(M, self.e["n_hyps"])

    def observe(self, M, x, y): self.hist.append((x, y)); self._acc(M, x, y, +1); self._rank(M)

    def revoke(self, M, idx, x, y):
        self._acc(M, x, y, -1)
        self.hist = [ev for i, ev in enumerate(self.hist) if i != idx]
        self._rank(M)

    def query(self, M, x):
        A = self.A; acc = 0
        for m in range(M_TOP): acc = A.add(acc, A.mul(self.tw[m], self.P[self.top[m]][x]))
        self._n(M, M_TOP)
        return acc


class QCountGradedMax(QCountGraded):
    row = "QCOUNT2M"
    use_max = True


EXTRA_ROWS = {c.row: c for c in (QCountGraded, QCountGradedMax)}


def run_extra(name, eco, precision, seed=0):
    M = Machine(B0, seed=seed); A = Arith(M, precision); ref = EXTRA_ROWS[name](eco, A)
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
    return {"row": name, "precision": precision, "capability": float(round(cap, 6)),
            "capability_exact": f"{cap.numerator}/{cap.denominator}", "admissible": bool(cap >= THETA),
            "R": R, "native_R": nat, "charged_ops_total": A.n_ops,
            "exec_q": F(R["exec"], nev * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
            "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"]),
            "nat_exec_q": F(nat["exec"], nev * (N_EVENTS + 1)), "nat_upd_e": F(nat["upd"], N_EVENTS),
            "nat_ver_e": F(nat["ver"], N_EVENTS), "nat_rev_e": F(nat["rev"]),
            "desc_bits": ref.desc_bits(), "desc_bits_scaled": ref.desc_bits_scaled(),
            "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits,
            "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}


def probe(variant="A", precision="fx8"):
    """the pre-freeze calibration probe: capabilities only, no frontier."""
    eco = ecology_graded(variant)
    out = {"var_qstar": float(eco["var"]), "qbar": float(eco["qbar"]),
           "qstar": {str(k): float(v) for k, v in eco["qstar"].items()},
           "max_posterior_weight": float(max(eco["post"]))}
    for r in LIN_ROWS: out[r] = lin_run(r, B0, eco, precision)["capability"]
    for r in EXTRA_ROWS: out[r] = run_extra(r, eco, precision)["capability"]
    for r in LM.VARIANTS: out[r] = LM.run(r, eco, precision)["capability"]
    return out


def main(tag="V1", seed=0, table_mode="sel1"):
    ecos = {v: ecology_graded(v) for v in ("A", "B", "C", "D", "E")}
    cells = {}
    for v, eco in ecos.items():
        for p in INSTRUMENTS:
            for r in LIN_ROWS: cells[f"{v}|{p}|{r}"] = lin_run(r, B0, eco, p, seed)
            for r in EXTRA_ROWS: cells[f"{v}|{p}|{r}"] = run_extra(r, eco, p, seed)
            if p in ("fx8", "fx10", "fx12"):
                for r in LM.VARIANTS: cells[f"{v}|{p}|{r}"] = LM.run(r, eco, p, seed, table_mode)

    front = {}; resid = {}; domin = {}
    eco = ecos["A"]
    allrows = list(LIN_ROWS) + list(EXTRA_ROWS) + list(LM.VARIANTS)
    adm = {p: sorted(r for r in allrows if f"A|{p}|{r}" in cells and cells[f"A|{p}|{r}"]["admissible"])
           for p in INSTRUMENTS}
    for scaled in (False, True):
        for price in ("reduced", "native"):
            bas = "scaled" if scaled else "flat"
            pes = {f"{r}@{p}": per_event(cells[f"A|{p}|{r}"], price, scaled)
                   for p in INSTRUMENTS for r in adm[p]}
            rep = RS.frontier_report(pes); key = f"graded|A|{price}|{bas}"
            front[key] = rep
            occ = rep["occupancy"]
            fx8 = {n: c for n, c in occ.items() if n.endswith("@fx8") and c}
            resid[key] = {"n_cells": rep["n_cells"], "fx8_occupancy": fx8,
                          "cells_held_by_any_fx8_row": sum(fx8.values()),
                          "any_fx8_row_occupies": bool(fx8),
                          "occupancy_nonzero": {n: c for n, c in sorted(occ.items()) if c}}
            dm = {}
            for me in [n for n in pes if n.endswith("@fx8")]:
                dm[me] = {"cost_coordinate_dominators": sorted(n for n, pb in pes.items()
                                                               if n != me and RS.dominates_cost(pb, pes[me])),
                          "desc": str(pes[me]["desc"]), "exec_q": str(pes[me]["exec_q"]),
                          "rho": str(RS.rho(pes[me]))}
                dm[me]["n_dominators"] = len(dm[me]["cost_coordinate_dominators"])
            domin[key] = dm
    positive = any(v["any_fx8_row_occupies"] for v in resid.values())
    adm8 = adm["fx8"]
    only_log = bool(adm8) and all(r in LM.VARIANTS or r.startswith("LOG") for r in adm8)

    receipt = {
        "schema": "StageDKPrecisionGradedEcologyV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-078", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "question": "on an ecology where likelihood MAGNITUDE must be inferred, does any 8-bit row OCCUPY a cross-instrument frontier cell -- i.e. does precision buy nothing at all there?",
        "ecology": {"name": "E_graded", "declared_value_pairs": [[str(a), str(b)] for a, b in VALS_GRADED],
                    "declared_flip_schedules": {k: list(v) for k, v in FLIPS_GRADED.items()},
                    "why": "every value pair of a predicate has the SAME thresholded prediction, so a count row cannot separate 15/16 from 9/16 even in principle; the thinned flip schedule makes the posterior concentrate on an extreme pair, so the average a count row must serve is far from the answer",
                    "eval_inputs": UNSEEN, "seen_inputs": SEEN,
                    "qstar": {str(x): f"{v.numerator}/{v.denominator}" for x, v in eco["qstar"].items()},
                    "qstar_float": {str(x): float(v) for x, v in eco["qstar"].items()},
                    "variance_of_qstar": float(eco["var"]), "base_rate": float(eco["qbar"]),
                    "max_posterior_weight": float(max(eco["post"]))},
        "parent_maximal_opponents_built_before_the_verdict": {
            "QCOUNT2": "the GRADED count row: accumulates the declared likelihood itself, quantized to the instrument grid, instead of counting thresholded agreements",
            "QCOUNT2M": "the same accumulator with max-renormalization, the anti-underflow device BAYESM uses"},
        "rows": sorted(allrows),
        "capability": {k: v["capability"] for k, v in cells.items()},
        "admissible_sets": adm,
        "admissible_at_fx8": adm8,
        "only_log_domain_rows_admissible_at_fx8": bool(only_log),
        "frontier": front, "residual": resid, "fx8_domination": domin,
        "cells": {k: {kk: (str(vv) if isinstance(vv, F) else vv) for kk, vv in v.items()} for k, v in cells.items()},
        "ANY_FX8_ROW_OCCUPIES_ON_E_GRADED": bool(positive),
        "terminal": ("PRECISION_BUYS_NOTHING_ON_E_graded__AN_8_BIT_ROW_OCCUPIES_THE_CROSS_INSTRUMENT_FRONTIER__THE_RESIDUAL_IS_AN_E_ambig_PROPERTY_AND_NOT_A_PRECISION_PROPERTY"
                     if positive else
                     "RESIDUAL_SURVIVES_ON_E_graded_TOO__NO_8_BIT_ROW_OCCUPIES_ANY_CROSS_INSTRUMENT_CELL"),
        "claim_ceiling": "E_graded is DECLARED and was constructed so that likelihood magnitude matters; that construction is stated in the receipt and in the module docstring rather than discovered after the fact, and protocol rule 19 is discharged by building two graded count rows as opponents BEFORE the verdict. It is one ecology, one class of 32, one prior, five declared flip schedules, one seed.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V7_GRADED_ECOLOGY_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("var(q*)", float(eco["var"]), "qbar", float(eco["qbar"]))
    print("admissible at fx8:", adm8)
    for p in INSTRUMENTS: print(f"  adm[{p}] =", adm[p])
    for k in sorted(resid):
        print(k, "cells", resid[k]["n_cells"], "| fx8 holds", resid[k]["cells_held_by_any_fx8_row"],
              resid[k]["fx8_occupancy"])
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
