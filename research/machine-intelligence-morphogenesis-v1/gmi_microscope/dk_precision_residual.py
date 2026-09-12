"""RV-377-076 part 2 and 3 — the RESIDUAL after RV-377-075, and why declared sequence B fails.

RV-377-075 killed the CAPABILITY claim of RV-377-066: at fx8 on the ambiguous ecology an 8-bit log-domain posterior
is admissible (0.874265) where all ten linear rows score exactly 0.0. What it did not kill is the COST claim, and
that is what this module executes.

PART 2 (the residual). The 8-bit log row is admissible but expensive: 3 104 description bits against 544-596 for the
linear rows at wider instruments, and 208 charged activations per query against 12. Two frontiers are computed over
the full H x r grid, under both declared price vectors and BOTH description bases (flat and `scaled`):

  PER-INSTRUMENT   protocol rule 17 as RV-377-066 ran it: a row occupies a cell iff it is admissible AND its
                   exact-rational lifecycle cost is minimal over the rows admissible AT THE SAME INSTRUMENT.
  CROSS-INSTRUMENT the question RV-377-066's kingdom rule was really asking: a (row, instrument) pair occupies a
                   cell iff it is admissible and its cost is minimal over EVERY admissible (row, instrument) pair.
                   This is the frontier on which "is a wider instrument ever strictly necessary?" is decidable.

Gap DG-2 is discharged in the only two ways it can be. Where a pair has a positive analytic crossover the grid is
extended past TWICE it. Where one row dominates another COORDINATE-WISE -- desc at least as large and every
per-use coefficient at least as large, one strictly -- no crossover exists at any H, r >= 0, and the "no cell"
statement is a THEOREM about the affine cost function rather than a grid observation. Both are reported per pair.

PART 3 (sequence B). The log row is admissible on declared sequences A (0.874265) and C (0.874265) and inadmissible
on B (0.400545). Three structural hypotheses are tested against the executed state of the row itself:
  H1 EVIDENCE-BEFORE-REVOCATION: B differs in how many events, or how many FLIPPED events, precede the revocation.
  H2 FLIP POSITION: the position of the flipped labels relative to the revoked index drives it.
  H3 CONCENTRATION: the exact posterior on B is genuinely less concentrated, so the obligation itself is harder.
Two further declared flip schedules, D and E, are executed as the split test RV-377-075 registered for its successor.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of
from .dk_precision import (THETA, X_ALL, SEEN, UNSEEN, N_EVENTS, REVOKE_AT, REVOKE_INDEX, PREDS, PRED_PRIOR,
                           LADDER, BITS, ROWS as LIN_ROWS, D3_ROWS, _hyp_table, capability, ecology,
                           per_event, cost, crossovers, grid_from, run as lin_run)
from . import dk_precision as DK
from . import dk_precision_log_audit as AU

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]

INSTRUMENTS = ("fx8", "fx10", "fx12", "fx16", "fx24", "fx32", "wide")
LOG_ROWS = ("LOGBAYES8", "LOGMAP8", "LOGBAYES8_NOMAXSUB")
# two FURTHER declared flip schedules, frozen with RV-377-076 and not executed before that freeze: the split test
# RV-377-075 registered for its successor ("a fourth and fifth declared sequence will split roughly as A and C did
# against B").
FLIPS_D = {"ambig": (0, 11), "noisy": (2, 5, 10, 15, 20)}
FLIPS_E = {"ambig": (7, 20), "noisy": (4, 9, 13, 18, 23)}


def ecology_flips(kind, flips, name):
    """dk_precision.ecology for an ARBITRARY declared flip schedule; identical in every other respect."""
    hyps = _hyp_table(kind)
    truth = (lambda x: (x >> 0) & 1) if kind == "ambig" else (lambda x: (x >> 3) & 1)
    flips = set(flips)
    events = []
    for i in range(N_EVENTS):
        x = SEEN[i % len(SEEN)]; y = truth(x)
        events.append((x, (1 - y) if i in flips else y))
    ev_final = [e for i, e in enumerate(events) if i != REVOKE_INDEX]
    post = []
    for h in hyps:
        w = F(h["prior"])
        for x, y in ev_final: w *= h["p"][x] if y else (1 - h["p"][x])
        post.append(w)
    Z = sum(post); post = [w / Z for w in post]
    ev_x = X_ALL if kind == "noisy" else UNSEEN
    qstar = {x: sum(post[j] * hyps[j]["p"][x] for j in range(len(hyps))) for x in ev_x}
    qbar = sum(qstar.values()) / len(ev_x)
    var = sum((qstar[x] - qbar) ** 2 for x in ev_x)
    return {"kind": kind, "variant": name, "hyps": hyps, "events": events, "events_final": ev_final,
            "eval": ev_x, "post": post, "qstar": qstar, "qbar": qbar, "var": var, "n_hyps": len(hyps),
            "flips": sorted(flips)}


def all_ecologies():
    e = {}
    for kind in ("ambig", "noisy"):
        for v in ("A", "B", "C"):
            eco = ecology(kind, v)
            eco["flips"] = sorted(set(i for i, (x, y) in enumerate(eco["events"])
                                      if y != ((x >> 0) & 1 if kind == "ambig" else (x >> 3) & 1)))
            e[f"{kind}|{v}"] = eco
        e[f"{kind}|D"] = ecology_flips(kind, FLIPS_D[kind], "D")
        e[f"{kind}|E"] = ecology_flips(kind, FLIPS_E[kind], "E")
    return e


# --------------------------------------------------------------------------- the combined portfolio
def portfolio(eco, instruments=INSTRUMENTS, table_mode="sel1", fix_div=True, seed=0):
    """every row of RV-377-066 plus every row of RV-377-075, at every instrument, as per-event cost vectors."""
    cells = {}
    for p in instruments:
        for r in LIN_ROWS:
            cells[(r, p)] = lin_run(r, B0, eco, p, seed)
        for r in LOG_ROWS:
            cells[(r, p)] = AU.run(r, eco, p, seed, table_mode=table_mode, branch_gts=(table_mode != "sel1"),
                                   fix_div=fix_div)
    return cells


def dominates(pa, pb):
    """pa dominates pb coordinate-wise: pa is at least as cheap on desc and on every per-use coefficient, and
    strictly cheaper on at least one. Then cost_a <= cost_b for EVERY H >= 0 and r >= 0, strictly somewhere, so no
    crossover exists and the 'no cell' statement is a theorem about the affine cost function (gap DG-2)."""
    ks = ("desc", "exec_q", "upd_e", "ver_e", "rev_e")
    return all(pa[k] <= pb[k] for k in ks) and any(pa[k] < pb[k] for k in ks)


def frontier_report(pes, base_h=(1, 2, 16, 128, 1024, 8192), base_r=(0, 1, 4, 16, 64, 256)):
    cr = crossovers(pes)
    hg = grid_from(cr, "H", base_h); rg = grid_from(cr, "r", base_r)
    fr = {}
    for Hh in hg:
        for r in rg:
            if not pes: fr[f"H={Hh}|r={r}"] = []; continue
            cs = {n: cost(p, Hh, r) for n, p in pes.items()}; m = min(cs.values())
            fr[f"H={Hh}|r={r}"] = sorted(n for n, v in cs.items() if v == m)
    occ = {}
    for n in pes: occ[n] = sum(1 for v in fr.values() if n in v)
    maxcross = max([float(v) for v in cr.values()], default=0.0)
    return {"crossovers": {k: str(v) for k, v in cr.items()},
            "crossovers_float": {k: float(v) for k, v in cr.items()},
            "largest_crossover": maxcross, "grid_H": hg, "grid_r": rg,
            "grid_max_H": max(hg) if hg else None,
            "grid_extends_past_twice_largest_crossover": bool(not cr or max(hg) >= 2 * maxcross),
            "n_cells": len(fr), "occupancy": occ, "frontier": fr}


# --------------------------------------------------------------------------- part 3: sequence diagnostics
def posterior_stats(eco):
    post = eco["post"]; mx = max(post)
    supp = sum(1 for w in post if w > 0)
    eff = 1 / sum(w * w for w in post)          # participation ratio: the effective number of live hypotheses
    srt = sorted(post, reverse=True)
    return {"max_posterior_weight": float(mx), "max_posterior_weight_exact": f"{mx.numerator}/{mx.denominator}",
            "support_size": supp, "effective_hypotheses_participation_ratio": float(eff),
            "top4_mass": float(sum(srt[:4])), "top1_over_top2": float(srt[0] / srt[1]) if srt[1] > 0 else None,
            "var_qstar": float(eco["var"]), "var_qstar_exact": f"{eco['var'].numerator}/{eco['var'].denominator}",
            "qbar": float(eco["qbar"])}


def sequence_diagnostics(eco, precision="fx8"):
    """H1/H2/H3 measured, plus the internal state of the log row at serve time."""
    kind = eco["kind"]
    truth = (lambda x: (x >> 0) & 1) if kind == "ambig" else (lambda x: (x >> 3) & 1)
    flips = sorted(set(i for i, (x, y) in enumerate(eco["events"]) if y != truth(x)))
    # H1/H2
    h12 = {"flip_indices": flips,
           "n_flips": len(flips),
           "n_flips_before_revocation_point": sum(1 for i in flips if i < REVOKE_AT),
           "n_flips_after_revocation_point": sum(1 for i in flips if i >= REVOKE_AT),
           "revocation_after_event": REVOKE_AT, "revoked_event_index": REVOKE_INDEX,
           "revoked_event_was_flipped": bool(REVOKE_INDEX in flips),
           "first_flip_index": flips[0] if flips else None,
           "distance_first_flip_to_revoked_index": (flips[0] - REVOKE_INDEX) if flips else None,
           "n_events_retained_after_revocation": N_EVENTS - 1}
    h3 = posterior_stats(eco)
    # the log row's executed state
    M = Machine(B0); A = AU.TracedArith(M, precision)
    ref = AU.AuditedLogBayes8(eco, A)
    M.phase("exec"); ref.init(M)
    ev = eco["events"]
    for t, (x, y) in enumerate(ev, 1):
        M.phase("exec")
        for xx in eco["eval"]: ref.query(M, xx)
        M.phase("upd"); ref.observe(M, x, y); M.end_event()
        M.phase("ver")
        for xx in eco["eval"]: M.op("EQ", ref.query(M, xx), 0)
        if t == REVOKE_AT:
            M.phase("rev"); ref.revoke(M, REVOKE_INDEX, *ev[REVOKE_INDEX]); M.end_event()
    M.phase("exec")
    lw = list(ref.lw)
    ws = ref._linear_weights(M)
    served = {xx: ref.query(M, xx) for xx in eco["eval"]}
    sfr = {xx: A.frac(v) for xx, v in served.items()}
    cap, excess = capability(eco, sfr)
    den = 0
    for w in ws: den = A.add(den, w)
    state = {"capability": float(round(cap, 6)), "admissible": bool(cap >= THETA),
             "log_weights_raw": lw, "log_weights_distinct": len(set(lw)),
             "n_log_weights_at_max": sum(1 for v in lw if v == max(lw)),
             "linear_weights_raw": ws, "n_linear_weights_nonzero": sum(1 for w in ws if w),
             "readout_denominator_raw": den,
             "readout_denominator_saturates": bool(A.hi is not None and den >= A.hi),
             "instrument_raw_hi": A.hi, "clamp_events": A.clamps,
             "served": {str(k): f"{v.numerator}/{v.denominator}" for k, v in sfr.items()},
             "served_float": {str(k): float(v) for k, v in sfr.items()},
             "qstar_float": {str(k): float(eco["qstar"][k]) for k in eco["eval"]},
             "per_input_squared_error": {str(k): float((sfr[k] - eco["qstar"][k]) ** 2) for k in eco["eval"]},
             "brier_excess": float(excess)}
    return {"H1_H2_evidence_and_flip_structure": h12, "H3_posterior_concentration": h3, "log_row_state": state}


# --------------------------------------------------------------------------- main
def main(tag="V1", seed=0, table_mode="sel1"):
    ecos = all_ecologies()
    # ---------------- part 2: the frontier
    front = {}; caps = {}; domin = {}
    for ekey in ("ambig|A", "noisy|A"):
        eco = ecos[ekey]
        cells = portfolio(eco, table_mode=table_mode)
        for (r, p), c in cells.items():
            caps[f"{ekey}|{r}|{p}"] = c["capability"]
        adm = {p: sorted(r for r in list(LIN_ROWS) + list(LOG_ROWS) if cells[(r, p)]["admissible"])
               for p in INSTRUMENTS}
        for scaled in (False, True):
            for price in ("reduced", "native"):
                bas = "scaled" if scaled else "flat"
                # per-instrument
                for p in INSTRUMENTS:
                    pes = {r: per_event(cells[(r, p)], price, scaled) for r in adm[p]}
                    front[f"{ekey}|per_instrument|{p}|{price}|{bas}"] = frontier_report(pes)
                # cross-instrument
                pes = {f"{r}@{p}": per_event(cells[(r, p)], price, scaled)
                       for p in INSTRUMENTS for r in adm[p]}
                rep = frontier_report(pes)
                front[f"{ekey}|cross_instrument|ALL|{price}|{bas}"] = rep
                # DG-2: for every pair involving the 8-bit log row, either a crossover or a domination theorem
                dm = {}
                me = "LOGBAYES8@fx8"
                if me in pes:
                    for n, pb in pes.items():
                        if n == me: continue
                        dm[n] = {"dominates_logbayes8_fx8": bool(dominates(pb, pes[me])),
                                 "is_dominated_by_logbayes8_fx8": bool(dominates(pes[me], pb)),
                                 "H_crossover": next((str(v) for k, v in rep["crossovers"].items()
                                                      if k.startswith("H|") and me in k and n in k), None),
                                 "r_crossover": next((str(v) for k, v in rep["crossovers"].items()
                                                      if k.startswith("r|") and me in k and n in k), None),
                                 "desc_logbayes8_fx8": str(pes[me]["desc"]), "desc_other": str(pb["desc"]),
                                 "exec_q_logbayes8_fx8": str(pes[me]["exec_q"]), "exec_q_other": str(pb["exec_q"])}
                domin[f"{ekey}|{price}|{bas}"] = dm
        front[f"{ekey}|admissible_sets"] = adm

    # the residual, stated as numbers
    resid = {}
    for ekey in ("ambig|A", "noisy|A"):
        for price in ("reduced", "native"):
            for bas in ("flat", "scaled"):
                k = f"{ekey}|cross_instrument|ALL|{price}|{bas}"
                occ = front[k]["occupancy"]
                logocc = occ.get("LOGBAYES8@fx8", 0)
                fx8occ = sum(v for n, v in occ.items() if n.endswith("@fx8"))
                resid[f"{ekey}|{price}|{bas}"] = {
                    "n_cells": front[k]["n_cells"],
                    "cells_held_by_logbayes8_at_fx8": logocc,
                    "cells_held_by_any_fx8_row": fx8occ,
                    "cells_held_by_a_wider_instrument": front[k]["n_cells"] - fx8occ,
                    "occupancy": occ,
                    "wider_instrument_strictly_necessary_for_admissibility":
                        front[f"{ekey}|admissible_sets"]["fx8"] == [],
                    "wider_instrument_strictly_cheaper_in_every_cell": bool(fx8occ == 0)}

    # ---------------- part 3: sequence diagnostics
    diag = {}
    for ekey, eco in sorted(ecos.items()):
        diag[ekey] = sequence_diagnostics(eco, "fx8")
    split = {ekey: {"capability_fx8": diag[ekey]["log_row_state"]["capability"],
                    "admissible_fx8": diag[ekey]["log_row_state"]["admissible"]}
             for ekey in sorted(ecos)}
    ambig_split = {v: split[f"ambig|{v}"]["admissible_fx8"] for v in ("A", "B", "C", "D", "E")}

    # which structural hypothesis separates the admissible sequences from the inadmissible ones?
    def sep(field, path):
        vals = {}
        for v in ("A", "B", "C", "D", "E"):
            d = diag[f"ambig|{v}"]
            for seg in path: d = d[seg]
            vals[v] = d[field] if isinstance(d, dict) else d
        adm = {v for v in vals if ambig_split[v]}; bad = {v for v in vals if not ambig_split[v]}
        A_vals = {vals[v] for v in adm}; B_vals = {vals[v] for v in bad}
        return {"values": vals, "admissible_values": sorted(map(str, A_vals)),
                "inadmissible_values": sorted(map(str, B_vals)),
                "separates": bool(A_vals and B_vals and not (A_vals & B_vals))}

    h_tests = {
        "H1_n_flips_before_revocation": sep("n_flips_before_revocation_point", ["H1_H2_evidence_and_flip_structure"]),
        "H1_n_flips_after_revocation": sep("n_flips_after_revocation_point", ["H1_H2_evidence_and_flip_structure"]),
        "H2_first_flip_index": sep("first_flip_index", ["H1_H2_evidence_and_flip_structure"]),
        "H2_revoked_event_was_flipped": sep("revoked_event_was_flipped", ["H1_H2_evidence_and_flip_structure"]),
        "H3_support_size": sep("support_size", ["H3_posterior_concentration"]),
        "H3_max_posterior_weight": sep("max_posterior_weight", ["H3_posterior_concentration"]),
        "H3_effective_hypotheses": sep("effective_hypotheses_participation_ratio", ["H3_posterior_concentration"]),
        "H3_top4_mass": sep("top4_mass", ["H3_posterior_concentration"]),
        "H3_var_qstar": sep("var_qstar", ["H3_posterior_concentration"]),
        "INSTRUMENT_readout_denominator_saturates": sep("readout_denominator_saturates", ["log_row_state"]),
        "INSTRUMENT_n_linear_weights_nonzero": sep("n_linear_weights_nonzero", ["log_row_state"]),
        "INSTRUMENT_n_log_weights_at_max": sep("n_log_weights_at_max", ["log_row_state"]),
    }
    separating = sorted(k for k, v in h_tests.items() if v["separates"])

    receipt = {
        "schema": "StageDKPrecisionResidualV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-076", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "table_charging_regime": table_mode,
        "question": "after RV-377-075 killed the capability claim, does precision buy DESCRIPTION rather than CAPABILITY on this ecology?",
        "cost_model": "C = desc + H*exec_q + r*(upd_e + ver_e) + (r/4)*rev_e",
        "frontier_rules": {
            "per_instrument": "protocol rule 17 as RV-377-066 ran it: minimal cost over the rows admissible AT THE SAME INSTRUMENT",
            "cross_instrument": "minimal cost over EVERY admissible (row, instrument) pair; this is the frontier on which 'is a wider instrument strictly necessary' is decidable"},
        "dg2_discipline": "for every pair the receipt reports either a positive analytic crossover, with the grid extended past twice the largest of them, or a COORDINATE-WISE DOMINATION, under which no crossover exists at any H, r >= 0 and the 'no cell' statement is a theorem about the affine cost function rather than a grid observation",
        "instruments": list(INSTRUMENTS),
        "rows": sorted(list(LIN_ROWS) + list(LOG_ROWS)),
        "capability": caps,
        "frontier": front,
        "logbayes8_fx8_pairwise_domination": domin,
        "residual": resid,
        "part3_sequence_diagnostics": diag,
        "part3_split_over_five_declared_sequences": split,
        "part3_ambig_admissibility_by_sequence": ambig_split,
        "part3_hypothesis_separation": h_tests,
        "part3_separating_variables": separating,
        "declared_new_flip_schedules": {"D": FLIPS_D, "E": FLIPS_E},
        "claim_ceiling": "one hypothesis class of 32, one prior, five declared event sequences, one machine seed, two ecologies. The frontier is decided on an H,r grid extended past twice every positive analytic crossover, together with a coordinate-wise domination theorem where no crossover exists; it is not a proof over the whole non-negative quadrant for pairs where neither holds. The table-charging regime is declared and the primary column is RV-377-075's own (`sel1`), which is the regime most generous to the log row and therefore hostile to this record's own conclusion.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V5_PRECISION_RESIDUAL_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("ambig admissibility by sequence at fx8:", ambig_split)
    print("separating variables:", separating)
    for k, v in sorted(resid.items()):
        print(k, "cells", v["n_cells"], "| logbayes8@fx8 holds", v["cells_held_by_logbayes8_at_fx8"],
              "| any fx8 holds", v["cells_held_by_any_fx8_row"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
