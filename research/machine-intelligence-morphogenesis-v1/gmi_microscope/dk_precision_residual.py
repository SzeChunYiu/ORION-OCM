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


def rho(pe):
    """the r-coefficient the FROZEN cost function actually has: C = desc + H*exec_q + r*(upd_e + ver_e) +
    (r/4)*rev_e = desc + H*exec_q + r*rho, so the cost function is affine in (H, r) with exactly THREE
    coefficients, not five."""
    return pe["upd_e"] + pe["ver_e"] + pe["rev_e"] / 4


def dominates(pa, pb):
    """RAW-COORDINATE domination, the test RV-377-076 clause 2 was frozen with: pa no larger than pb on desc and on
    every one of the four per-use coefficients, strictly smaller somewhere. Sufficient for domination but NOT
    necessary, because upd_e, ver_e and rev_e enter the cost only through their sum rho."""
    ks = ("desc", "exec_q", "upd_e", "ver_e", "rev_e")
    return all(pa[k] <= pb[k] for k in ks) and any(pa[k] < pb[k] for k in ks)


def dominates_cost(pa, pb):
    """COST-COORDINATE domination: pa no larger than pb on each of the three coefficients the frozen cost function
    has -- desc, exec_q and rho -- and strictly smaller on at least one. This is necessary AND sufficient for
    cost_a <= cost_b at EVERY H >= 0 and r >= 0 with strictness somewhere, so no crossover exists in either axis
    and the 'no cell' statement is a theorem about the affine cost function rather than a grid observation
    (gap DG-2)."""
    ka = (pa["desc"], pa["exec_q"], rho(pa)); kb = (pb["desc"], pb["exec_q"], rho(pb))
    return all(x <= y for x, y in zip(ka, kb)) and any(x < y for x, y in zip(ka, kb))


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
    maxH = max([float(v) for k, v in cr.items() if k.startswith("H|")], default=0.0)
    maxR = max([float(v) for k, v in cr.items() if k.startswith("r|")], default=0.0)
    return {"crossovers": {k: str(v) for k, v in cr.items()},
            "crossovers_float": {k: float(v) for k, v in cr.items()},
            "largest_H_crossover": maxH, "largest_r_crossover": maxR,
            "grid_H": hg, "grid_r": rg, "grid_max_H": max(hg) if hg else None,
            "grid_max_r": max(rg) if rg else None,
            "H_grid_extends_past_twice_largest_H_crossover": bool(not hg or max(hg) >= 2 * maxH),
            "r_grid_extends_past_twice_largest_r_crossover": bool(not rg or max(rg) >= 2 * maxR),
            "asymptotic_min_exec_q_as_H_to_infinity": sorted(
                n for n, v in pes.items() if v["exec_q"] == min(p["exec_q"] for p in pes.values())) if pes else [],
            "asymptotic_min_rho_as_r_to_infinity": sorted(
                n for n, v in pes.items() if rho(v) == min(rho(p) for p in pes.values())) if pes else [],
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


# --------------------------------------------------------------------------- part 3b: the scalpel
def _is_tie(u, S, v):
    """the exact value x = S * 2^(u/S) is a half-integer, i.e. x = v - 1/2 where v is the half-UP rounding.
    Decided by raising to the S-th power so that no floating point is involved."""
    return (F(2 * S, 1) ** S) * (F(2) ** u) == F(2 * v - 1) ** S


def tie_census(S):
    """which exponent-table entries are decided by the ROUNDING TIE-BREAK alone."""
    ties = {}
    for u in range(-255, 1):
        v = AU._round_half_up_exact_pow2(u, S)
        if _is_tie(u, S, v):
            ties[u] = {"half_up": v, "half_down": v - 1, "exact_value_times_S": f"{2*v-1}/2",
                       "log2_weight": float(F(u, S))}
    return ties


class HalfDownLogBayes8(AU.AuditedLogBayes8):
    """RV-377-075's row with ONE change: the exponent table rounds ties DOWN instead of up. At fx8 exactly ONE of
    the 256 entries changes -- u = -80, the entry for a weight of exactly 2^-5 = 1/32, which the published
    half-up rule promotes to the instrument's smallest positive value 1/16 and this rule sends to 0. Everything
    else -- arithmetic, constants, events, scoring, theta -- is identical. A scalpel, not a rewrite."""
    row = "LOGBAYES8"

    def init(self, M):
        super().init(M)
        A = self.A
        self.tie_entries_changed = []
        for u, val in list(self.exp_tab.items()):
            v = AU._round_half_up_exact_pow2(u, A.S)
            if _is_tie(u, A.S, v):
                self.exp_tab[u] = A.clamp(v - 1)
                self.tie_entries_changed.append([u, val, A.clamp(v - 1)])


def run_halfdown(eco, precision="fx8", seed=0):
    M = Machine(B0); A = AU.TracedArith(M, precision); ref = HalfDownLogBayes8(eco, A)
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
    lw = list(ref.lw); ws = ref._linear_weights(M)
    served = {xx: A.frac(ref.query(M, xx)) for xx in eco["eval"]}
    cap, excess = capability(eco, served)
    return {"capability": float(round(cap, 6)), "admissible": bool(cap >= THETA),
            "n_table_entries_changed": len(ref.tie_entries_changed),
            "table_entries_changed": ref.tie_entries_changed,
            "linear_weights_raw": ws, "n_linear_weights_nonzero": sum(1 for w in ws if w),
            "log_weights_raw": lw,
            "served_float": {str(k): float(v) for k, v in served.items()}}


def exact_posterior_within(eco, k):
    """the ECOLOGY-ONLY predictor: how many hypotheses of the EXACT posterior lie within a factor 2^k of the
    maximum-a-posteriori weight. The 8-bit exponent table's smallest non-zero entry sits at 2^-5 of the maximum
    (half-up), so this count at k = 5 is what the fx8 readout can represent."""
    post = eco["post"]; mx = max(post)
    return sum(1 for w in post if w * (2 ** k) >= mx)


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
                                 "dominates_logbayes8_fx8_in_cost_coordinates": bool(dominates_cost(pb, pes[me])),
                                 "rho_logbayes8_fx8": str(rho(pes[me])), "rho_other": str(rho(pb)),
                                 "upd_e_logbayes8_fx8": str(pes[me]["upd_e"]), "upd_e_other": str(pb["upd_e"]),
                                 "ver_e_logbayes8_fx8": str(pes[me]["ver_e"]), "ver_e_other": str(pb["ver_e"]),
                                 "rev_e_logbayes8_fx8": str(pes[me]["rev_e"]), "rev_e_other": str(pb["rev_e"]),
                                 "H_crossover": next((str(v) for k, v in rep["crossovers"].items()
                                                      if k.startswith("H|") and me in k and n in k), None),
                                 "r_crossover": next((str(v) for k, v in rep["crossovers"].items()
                                                      if k.startswith("r|") and me in k and n in k), None),
                                 "desc_logbayes8_fx8": str(pes[me]["desc"]), "desc_other": str(pb["desc"]),
                                 "exec_q_logbayes8_fx8": str(pes[me]["exec_q"]), "exec_q_other": str(pb["exec_q"])}
                dm["_SUMMARY"] = {
                    "rows_dominating_logbayes8_fx8_in_RAW_coordinates":
                        sorted(n for n, v in dm.items() if v["dominates_logbayes8_fx8"]),
                    "rows_dominating_logbayes8_fx8_in_COST_coordinates":
                        sorted(n for n, v in dm.items() if v["dominates_logbayes8_fx8_in_cost_coordinates"]),
                    "any_cost_coordinate_dominator": bool(any(
                        v["dominates_logbayes8_fx8_in_cost_coordinates"] for v in dm.values()))}
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

    # ---------------- part 3b: the scalpel, and the ecology-only predictor
    scalpel = {}
    for ek in ("ambig", "noisy"):
      for v in ("A", "B", "C", "D", "E"):
        eco = ecos[f"{ek}|{v}"]
        base = diag[f"{ek}|{v}"]["log_row_state"]
        hd = run_halfdown(eco, "fx8", seed)
        scalpel[f"{ek}|{v}"] = {"published_half_up_capability": base["capability"],
                      "published_half_up_admissible": base["admissible"],
                      "published_n_linear_weights_nonzero": base["n_linear_weights_nonzero"],
                      "half_down_capability": hd["capability"],
                      "half_down_admissible": hd["admissible"],
                      "half_down_n_linear_weights_nonzero": hd["n_linear_weights_nonzero"],
                      "n_table_entries_changed": hd["n_table_entries_changed"],
                      "table_entries_changed": hd["table_entries_changed"],
                      "served_half_up": base["served_float"], "served_half_down": hd["served_float"],
                      "flipped_to_admissible": bool(hd["admissible"] and not base["admissible"]),
                      "flipped_to_inadmissible": bool(base["admissible"] and not hd["admissible"])}
    scalpel_summary = {
        "sequences_flipped_to_admissible": sorted(k for k, v in scalpel.items() if v["flipped_to_admissible"]),
        "sequences_flipped_to_inadmissible": sorted(k for k, v in scalpel.items() if v["flipped_to_inadmissible"]),
        "sequences_unchanged": sorted(k for k, v in scalpel.items()
                                      if v["published_half_up_capability"] == v["half_down_capability"]),
        "n_table_entries_changed": 1}
    predictor = {}
    for v in ("A", "B", "C", "D", "E"):
        eco = ecos[f"ambig|{v}"]
        predictor[v] = {f"exact_posterior_within_2^{k}_of_MAP": exact_posterior_within(eco, k)
                        for k in (3, 4, 5, 6, 7)}
        predictor[v]["executed_n_linear_weights_nonzero_fx8"] = \
            diag[f"ambig|{v}"]["log_row_state"]["n_linear_weights_nonzero"]
        predictor[v]["admissible_fx8"] = ambig_split[v]
    tie = tie_census(16)
    # the negative twin on ALL five declared sequences, including the two never executed before this record
    twin = {}
    for ek in ("ambig", "noisy"):
        for v in ("A", "B", "C", "D", "E"):
            c = AU.run("LOGBAYES8_NOMAXSUB", ecos[f"{ek}|{v}"], "fx8", seed, table_mode="sel1",
                       branch_gts=False, fix_div=True)
            twin[f"{ek}|{v}"] = {"capability": c["capability"], "capability_exact": c["capability_exact"],
                                 "admissible": c["admissible"], "exactly_zero": c["capability_exact"] == "0/1"}
    twin_summary = {"all_ambig_exactly_zero": all(twin[f"ambig|{v}"]["exactly_zero"] for v in "ABCDE"),
                    "all_sequences_exactly_zero": all(t["exactly_zero"] for t in twin.values())}

    # the headline numbers of the residual, in one place
    cA = portfolio(ecos["ambig|A"], instruments=("fx8", "fx10"), table_mode="sel1")
    scanA = AU.run("LOGBAYES8", ecos["ambig|A"], "fx8", seed, table_mode="scan", branch_gts=True, fix_div=True)
    lg = cA[("LOGBAYES8", "fx8")]; qc = cA[("QCOUNT", "fx10")]; bm = cA[("BAYESM", "fx10")]
    headline = {
        "logbayes8_fx8": {"desc_flat": lg["desc_bits"], "desc_scaled": lg["desc_bits_scaled"],
                          "exec_q_reduced_sel1": str(lg["exec_q"]),
                          "exec_q_reduced_registered_B0_scan": str(scanA["exec_q"]),
                          "exec_q_native": str(lg["nat_exec_q"]), "capability": lg["capability"]},
        "qcount_fx10": {"desc_flat": qc["desc_bits"], "desc_scaled": qc["desc_bits_scaled"],
                        "exec_q_reduced": str(qc["exec_q"]), "exec_q_native": str(qc["nat_exec_q"]),
                        "capability": qc["capability"]},
        "bayesm_fx10": {"desc_flat": bm["desc_bits"], "desc_scaled": bm["desc_bits_scaled"],
                        "exec_q_reduced": str(bm["exec_q"]), "capability": bm["capability"]},
        "ratios": {
            "desc_flat_log_over_qcount": float(F(lg["desc_bits"], qc["desc_bits"])),
            "desc_scaled_log_over_qcount": float(F(lg["desc_bits_scaled"], qc["desc_bits_scaled"])),
            "exec_q_reduced_sel1_log_over_qcount": float(lg["exec_q"] / qc["exec_q"]),
            "exec_q_reduced_scan_log_over_qcount": float(scanA["exec_q"] / qc["exec_q"]),
            "exec_q_native_log_over_qcount": float(lg["nat_exec_q"] / qc["nat_exec_q"]),
            "rho_reduced_log_over_qcount": float(rho(per_event(lg, "reduced", False)) /
                                                 rho(per_event(qc, "reduced", False)))},
    }

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
        "part3b_tie_break_scalpel": {
            "per_sequence": scalpel, "summary": scalpel_summary,
            "exponent_table_tie_census_fx8": tie,
            "n_tie_entries_fx8": len(tie),
            "method": "the exponent table's half-UP rounding is replaced by half-DOWN. At fx8 this changes EXACTLY the tie entries -- the entries whose exact value S*2^(u/S) is a half-integer -- and nothing else. Arithmetic, constants, events, scoring rule and theta are untouched."},
        "part3b_ecology_only_predictor": predictor,
        "negative_twin_all_five_sequences": {"per_sequence": twin, "summary": twin_summary},
        "residual_headline": headline,
        "declared_new_flip_schedules": {"D": FLIPS_D, "E": FLIPS_E},
        "claim_ceiling": "one hypothesis class of 32, one prior, five declared event sequences, one machine seed, two ecologies. The frontier is decided on an H,r grid extended past twice every positive analytic crossover, together with a coordinate-wise domination theorem where no crossover exists; it is not a proof over the whole non-negative quadrant for pairs where neither holds. The table-charging regime is declared and the primary column is RV-377-075's own (`sel1`), which is the regime most generous to the log row and therefore hostile to this record's own conclusion.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V5_PRECISION_RESIDUAL_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("ambig admissibility by sequence at fx8:", ambig_split)
    print("separating variables:", separating)
    for k in sorted(scalpel):
        v = scalpel[k]
        print("  scalpel", k, "half_up", v["published_half_up_capability"], v["published_half_up_admissible"],
              "-> half_down", v["half_down_capability"], v["half_down_admissible"],
              "| entries changed", v["n_table_entries_changed"],
              "| nonzero", v["published_n_linear_weights_nonzero"], "->",
              v["half_down_n_linear_weights_nonzero"])
    print("scalpel summary:", scalpel_summary)
    print("ecology-only predictor:", {v: predictor[v] for v in ("A", "B", "C", "D", "E")})
    print("negative twin:", twin_summary, {k: v["capability"] for k, v in sorted(twin.items())})
    print("headline ratios:", headline["ratios"])
    for k, v in sorted(resid.items()):
        print(k, "cells", v["n_cells"], "| logbayes8@fx8 holds", v["cells_held_by_logbayes8_at_fx8"],
              "| any fx8 holds", v["cells_held_by_any_fx8_row"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
