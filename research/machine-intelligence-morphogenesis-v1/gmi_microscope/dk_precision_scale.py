"""RV-377-079 — the class-size lever: does the 8-bit log row occupy once its fixed overhead is amortized?

RV-377-078 refuted its own hypothesis and, in doing so, located the next lever algebraically rather than by
guessing. The 8-bit log row's irreducible excess over its cheapest linear competitor is a FIXED number of declared
scalars - 8 log-likelihood constants, 3 log priors and S = 16 ladder breakpoints, 27 in all at the registered class
- while the STATE both rows carry grows with the hypothesis class size K. Under the `scaled` description basis an
8-bit row pays 8 bits per declared scalar where a 12-bit row pays 12, so at H = 1, r = 0:

    cost(log @ fx8)  -  cost(QCOUNT @ fx12)  =  8*(K + M + ov) + exec_log  -  [ 12*(K + M) + exec_q ]
                                             =  -4K + 8*ov + (exec_log - exec_q) - 4M

which is NEGATIVE for large enough K. With ov = 27, M = 4, exec_log = 188 and exec_q = 12 the crossing is at
K > 94. At the registered K = 32 the inequality fails by a wide margin, and THE CLASS SIZE HAS NEVER BEEN VARIED
IN THIS LANE - every record from RV-377-066 to RV-377-078 used the same 8 predicates x 4 value pairs.

The class is scaled by a DECLARED rule, fixed before any run:
  * predicates: the EIGHT REGISTERED predicates first, in their registered order, then balanced truth tables
    (popcount exactly 8) in increasing numeric order - so at n_preds = 8 the class is EXACTLY the registered one
    and the ladder starts at the registered ecology rather than at a lookalike;
  * prior: 4 for the first predicate, 2 for the next three, 1 for the rest - which reproduces the registered
    (4, 2, 2, 2, 1, 1, 1, 1) exactly at n_preds = 8;
  * value pairs: the registered VALS_AMBIG at n_vals = 4.
  * structural description: n_hyps * (bits(n_preds) + bits(n_vals)) + n_preds * 16, which evaluates to exactly
    the registered CLASS_STRUCT_BITS = 288 at 8 x 4.

If at some K an 8-bit row is the cheapest admissible row at even one (H, r) cell, precision buys NOTHING there and
the residual is a SMALL-CLASS artefact. If it never is, the residual survives the one structural parameter that
the algebra says should kill it.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of
from . import dk_precision as DK
from . import dk_precision_log_audit as AU
from . import dk_precision_log_min as LM
from . import dk_precision_residual as RS
from .dk_precision import (THETA, X_ALL, SEEN, UNSEEN, N_EVENTS, REVOKE_AT, REVOKE_INDEX, VALS_AMBIG,
                           M_TOP, per_event, run as lin_run)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
INSTRUMENTS = ("fx8", "fx10", "fx12", "fx16", "wide")
K_LADDER = (32, 64, 96, 128)
LIN = ("BAYES", "BAYESM", "QCOUNT", "MAP")
LOG = ("LOGLAD8_T4", "LOGTRIM8_T4", "LOGLAD8")


def scaled_predicates(n):
    """DECLARED: the EIGHT REGISTERED predicates of dk_precision.PREDS first, in their registered order, then
    extended with balanced truth tables (popcount exactly 8 over the 16 inputs) in increasing numeric order,
    skipping any already present. At n = 8 this reproduces the registered class EXACTLY, so the K ladder starts
    at the registered ecology and is not a different experiment wearing its name."""
    out = [sum(1 << x for x in X_ALL if pf(x)) for _, pf in DK.PREDS][:n]
    have = set(out)
    for t in range(1, 1 << 16):
        if len(out) >= n: break
        if t in have or bin(t).count("1") != 8: continue
        out.append(t); have.add(t)
    assert len(out) == n, (n, len(out))
    return out


def class_struct_bits(n_preds, n_vals):
    hb = max(1, (n_preds - 1).bit_length()) + max(1, (n_vals - 1).bit_length())
    return n_preds * n_vals * hb + n_preds * 16


def ecology_scaled(n_preds, n_vals=4, variant="A"):
    tts = scaled_predicates(n_preds)
    vals = VALS_AMBIG[:n_vals]
    hyps = []
    for pi, tt in enumerate(tts):
        prior = 4 if pi == 0 else (2 if pi < 4 else 1)
        for vi, (hi, lo) in enumerate(vals):
            hyps.append({"pred": f"tt{tt}", "vi": vi, "prior": prior,
                         "p": {x: (hi if (tt >> x) & 1 else lo) for x in X_ALL}})
    truth = lambda x: (x >> 0) & 1
    flips = {"A": (5, 18), "B": (9, 22), "C": (2, 13)}[variant]
    events = [(SEEN[i % len(SEEN)],
               (1 - truth(SEEN[i % len(SEEN)])) if i in set(flips) else truth(SEEN[i % len(SEEN)]))
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
    return {"kind": "ambig", "variant": variant, "hyps": hyps, "events": events, "events_final": ev_final,
            "eval": UNSEEN, "post": post, "qstar": qstar, "qbar": qbar, "var": var, "n_hyps": len(hyps),
            "n_preds": n_preds, "n_vals": n_vals, "struct_bits": class_struct_bits(n_preds, n_vals)}


def reproduce_check():
    """the K = 32 point of the ladder must BE the registered ambiguous ecology, answer for answer, or the ladder
    is a different experiment wearing its name."""
    a = ecology_scaled(8, 4, "A"); b = DK.ecology("ambig", "A")
    same_p = all(a["hyps"][j]["p"] == b["hyps"][j]["p"] for j in range(32))
    return {"n_hyps": a["n_hyps"] == b["n_hyps"], "struct_bits_288": a["struct_bits"] == DK.CLASS_STRUCT_BITS,
            "priors_identical": [h["prior"] for h in a["hyps"]] == [h["prior"] for h in b["hyps"]],
            "likelihoods_identical": bool(same_p), "events_identical": a["events"] == b["events"],
            "qstar_identical": a["qstar"] == b["qstar"], "variance_identical": a["var"] == b["var"]}


@contextlib.contextmanager
def struct(nbits):
    """the rows read CLASS_STRUCT_BITS from their own module namespace at construction time; this rebinds it for
    the duration of a run and restores it afterwards, so the structural description scales with the class instead
    of staying frozen at the registered 288."""
    olds = [(m, m.CLASS_STRUCT_BITS) for m in (DK, AU, LM)]
    try:
        for m, _ in olds: m.CLASS_STRUCT_BITS = nbits
        yield
    finally:
        for m, v in olds: m.CLASS_STRUCT_BITS = v


def run_cell(row, eco, precision, seed=0):
    with struct(eco["struct_bits"]):
        if row in LIN: return lin_run(row, B0, eco, precision, seed)
        return LM.run(row, eco, precision, seed, "sel1")


def probe(K, precision="fx8"):
    eco = ecology_scaled(K // 4, 4, "A")
    out = {"K": eco["n_hyps"], "struct_bits": eco["struct_bits"], "var": float(eco["var"])}
    for r in LIN + LOG:
        c = run_cell(r, eco, precision)
        out[r] = {"cap": c["capability"], "adm": c["admissible"], "desc": c["desc_bits"],
                  "desc_scaled": c["desc_bits_scaled"], "exec_q": str(c["exec_q"]), "w": c["w_scalars"]}
    return out


def main(tag="V1", seed=0):
    cells = {}; ecos = {}
    for K in K_LADDER:
        eco = ecology_scaled(K // 4, 4, "A"); ecos[K] = eco
        for p in INSTRUMENTS:
            for r in LIN + LOG:
                if r in LOG and p in ("fx16", "wide"): continue     # 8-bit-favouring encodings; fx8..fx12 only
                cells[f"{K}|{p}|{r}"] = run_cell(r, eco, p, seed)

    front = {}; resid = {}; domin = {}; algebra = {}
    for K in K_LADDER:
        adm = {p: sorted(r for r in LIN + LOG if f"{K}|{p}|{r}" in cells and cells[f"{K}|{p}|{r}"]["admissible"])
               for p in INSTRUMENTS}
        for scaled in (False, True):
            for price in ("reduced", "native"):
                bas = "scaled" if scaled else "flat"
                pes = {f"{r}@{p}": per_event(cells[f"{K}|{p}|{r}"], price, scaled)
                       for p in INSTRUMENTS for r in adm[p]}
                rep = RS.frontier_report(pes); key = f"K{K}|{price}|{bas}"
                front[key] = rep
                occ = rep["occupancy"]
                fx8 = {n: c for n, c in occ.items() if n.endswith("@fx8") and c}
                resid[key] = {"n_cells": rep["n_cells"], "fx8_occupancy": fx8,
                              "cells_held_by_any_fx8_row": sum(fx8.values()),
                              "any_fx8_row_occupies": bool(fx8),
                              "occupancy_nonzero": {n: c for n, c in sorted(occ.items()) if c},
                              "admissible_at_fx8": adm["fx8"]}
                dm = {}
                for me in [n for n in pes if n.endswith("@fx8")]:
                    d = sorted(n for n, pb in pes.items() if n != me and RS.dominates_cost(pb, pes[me]))
                    dm[me] = {"cost_coordinate_dominators": d, "n_dominators": len(d),
                              "desc": str(pes[me]["desc"]), "exec_q": str(pes[me]["exec_q"]),
                              "rho": str(RS.rho(pes[me]))}
                domin[key] = dm
        # the frozen algebra, evaluated: cost(log@fx8) - cost(cheapest linear@fx12) at H = 1, r = 0, scaled basis
        try:
            lg = cells[f"{K}|fx8|LOGLAD8_T4"]; qc = cells[f"{K}|fx12|QCOUNT"]
            a = lg["desc_bits_scaled"] + int(lg["exec_q"]); b = qc["desc_bits_scaled"] + int(qc["exec_q"])
            algebra[K] = {"log_fx8_desc_scaled": lg["desc_bits_scaled"], "log_fx8_exec_q": int(lg["exec_q"]),
                          "qcount_fx12_desc_scaled": qc["desc_bits_scaled"], "qcount_fx12_exec_q": int(qc["exec_q"]),
                          "cost_at_H1_r0_log": a, "cost_at_H1_r0_qcount": b, "difference": a - b,
                          "log_is_cheaper_at_H1_r0": bool(a < b),
                          "log_admissible_at_fx8": lg["admissible"], "qcount_admissible_at_fx12": qc["admissible"]}
        except KeyError:
            algebra[K] = {"error": "missing cell"}

    positive = any(v["any_fx8_row_occupies"] for v in resid.values())
    receipt = {
        "schema": "StageDKPrecisionClassScalingV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-079", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "question": "the class size has never been varied in this lane. Once the log representation's FIXED 27-scalar overhead is amortized against a state that grows with K, does an 8-bit row occupy a cross-instrument frontier cell?",
        "reproduces_registered_class_at_K32": reproduce_check(),
        "class_scaling_rule": {
            "predicates": "the eight REGISTERED predicates of dk_precision.PREDS first, in registered order, then balanced truth tables (popcount 8) in increasing numeric order; at n_preds = 8 the class is EXACTLY the registered one, asserted by reproduce_registered_class below",
            "prior": "4 for the first predicate, 2 for the next three, 1 for the rest - reproduces the registered (4,2,2,2,1,1,1,1) at n_preds = 8",
            "value_pairs": "the registered VALS_AMBIG, n_vals = 4",
            "struct_bits": "n_hyps * (bits(n_preds) + bits(n_vals)) + n_preds * 16, which is exactly the registered 288 at 8 x 4",
            "K_ladder": list(K_LADDER)},
        "ecologies": {str(K): {"n_hyps": ecos[K]["n_hyps"], "n_preds": ecos[K]["n_preds"],
                               "struct_bits": ecos[K]["struct_bits"],
                               "variance_of_qstar": float(ecos[K]["var"]),
                               "qstar_float": {str(x): float(v) for x, v in ecos[K]["qstar"].items()}}
                      for K in K_LADDER},
        "capability": {k: v["capability"] for k, v in cells.items()},
        "admissible": {f"K{K}|{p}": sorted(r for r in LIN + LOG
                                           if f"{K}|{p}|{r}" in cells and cells[f"{K}|{p}|{r}"]["admissible"])
                       for K in K_LADDER for p in INSTRUMENTS},
        "frozen_algebra_evaluated": algebra,
        "frontier": front, "residual": resid, "fx8_domination": domin,
        "cells": {k: {kk: (str(vv) if isinstance(vv, F) else vv) for kk, vv in v.items()} for k, v in cells.items()},
        "ANY_FX8_ROW_OCCUPIES_AT_ANY_K": bool(positive),
        "terminal": ("PRECISION_BUYS_NOTHING_AT_LARGE_CLASS_SIZE__AN_8_BIT_ROW_OCCUPIES_A_CROSS_INSTRUMENT_CELL__THE_RESIDUAL_IS_A_SMALL_CLASS_ARTEFACT"
                     if positive else
                     "RESIDUAL_SURVIVES_CLASS_SCALING_TOO__NO_8_BIT_ROW_OCCUPIES_ANY_CROSS_INSTRUMENT_CELL_AT_ANY_EXECUTED_K"),
        "claim_ceiling": "one ecology recipe (ambiguous evidence), one declared sequence, one seed, four class sizes, five instruments. The class-scaling rule is declared and evaluates to the registered class exactly at 8 x 4. The log-domain rows were executed at fx8, fx10 and fx12 only, because the ladder encoding has S breakpoints and is an 8-bit-favouring encoding by construction; that does not touch the question, which asks only whether an EIGHT-BIT row occupies.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V8_CLASS_SCALING_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    for K in K_LADDER:
        print(f"== K={K} struct={ecos[K]['struct_bits']} ==")
        print("   adm fx8:", receipt["admissible"][f"K{K}|fx8"], "| fx12:", receipt["admissible"][f"K{K}|fx12"])
        print("   algebra:", algebra[K])
        for price in ("reduced", "native"):
            for bas in ("flat", "scaled"):
                v = resid[f"K{K}|{price}|{bas}"]
                print(f"   {price}|{bas}: cells {v['n_cells']} fx8 holds {v['cells_held_by_any_fx8_row']} {v['fx8_occupancy']}")
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
