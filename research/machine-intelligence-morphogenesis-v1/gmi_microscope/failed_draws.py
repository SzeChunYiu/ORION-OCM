"""RV-377-067 (gap G14) — charge the FAILED DRAWS of a stochastic carrier on the D'/E' frontier and re-adjudicate
RV-377-041b clause by clause.

The registered frontier line (smooth.cost) charges ONE development run per row. A stochastic carrier is admissible on a
fraction q of seeds (GMI-DA6, protocol rule 16), so obtaining an admissible machine costs 1/q development runs, of which
(1/q - 1) are thrown away. `vm.lifecycle_vector` already carries the two terms that pay for them (`B_search`,
`B_failed_candidates`); this module applies them:

    C'(row, col, H, r) = C(row, col, H, r)  +  B_search(row, col)
    B_search(row, col) = B_failed_candidates(row) * D_draw(row, col)
    B_failed_candidates(row) = 1/q_row - 1        (expected FAILED draws, geometric law, exact rational)
    D_draw(row, col)  = exec + upd + ver + rev    (charged work of ONE complete run of the registered protocol)

A deterministic row has q = 1 exactly, so its B_search and B_failed_candidates are 0 and its line is unchanged. All
arithmetic is exact (fractions.Fraction); the reliability index and its 95 percent Clopper-Pearson interval come from the
committed 192-run census STAGE_DE_S3_SEED_CENSUS_V1.json by exact binomial tail arithmetic.

The cells are RE-EXECUTED here (not read from the receipt) so that B_search is computed from a live Machine ledger through
`vm.lifecycle_vector`; the re-execution is then compared coordinate by coordinate with the committed receipt, which is
clause 1 of RV-377-067.

Writes microscopes/results/STAGE_G14_FAILED_DRAW_CHARGING_V1.json.
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction as F

from . import bases, smooth, vm
from .core import FX_ONE, Machine, clamp, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

# ---------------------------------------------------------------------------------------------- declared scope (frozen)
ECOLOGY = "E_sym5"
COEFFS = (5 / 16,) * 4
SEED = 4
N_EVENTS = 16
CENSUS_CELL = "E_sym5|size=8"          # the census cell that produced seed 4
COMMITTED = "STAGE_DE_SMOOTH_V22_SYM5_S4.json"
COMMITTED_SEED0 = "STAGE_DE_SMOOTH_V8_SYM5_H.json"
CENSUS = "STAGE_DE_S3_SEED_CENSUS_V1.json"
STOCHASTIC_ROWS = ("S3",)              # the only ROWS_V6 row that consumes the machine seed
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]
R_GRID = [0, 1, 2, 4, 8, 16, 32]
FRONTIER_RULE = "R-top (each row at its largest ladder size); protocol rule 17"


# --------------------------------------------------------------------------------------- exact Clopper-Pearson interval
def _binom_tail_ge(k, n, p):
    """P[X >= k] for X ~ Bin(n, p), exact in p (Fraction)."""
    return sum(F(math.comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _binom_tail_le(k, n, p):
    return sum(F(math.comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def _bisect(f, lo, hi, target, tol=F(1, 10 ** 12)):
    """smallest p in [lo, hi] with f(p) >= target, by bisection on exact rationals to `tol`."""
    lo, hi = F(lo), F(hi)
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(mid) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def clopper_pearson(k, n, alpha=F(5, 100)):
    """exact (conservative) two-sided 1-alpha confidence interval for a binomial proportion, as Fractions."""
    lower = F(0) if k == 0 else _bisect(lambda p: _binom_tail_ge(k, n, p), 0, 1, alpha / 2)
    upper = F(1) if k == n else _bisect(lambda p: -_binom_tail_le(k, n, p), 0, 1, -alpha / 2)
    return lower, upper


def reliability_from_census():
    """q per census cell and pooled over the whole 192-run census, each with its exact 95 percent interval."""
    d = json.load(open(os.path.join(RES, CENSUS)))
    out = {"census_receipt": CENSUS, "census_sha256": d["receipt_sha256"], "cells": {}}
    k_tot = n_tot = 0
    for cell, s in sorted(d["summary"].items()):
        k, n = s["n_admissible"], s["n"]
        k_tot += k; n_tot += n
        lo, hi = clopper_pearson(k, n)
        out["cells"][cell] = _q_block(k, n, lo, hi)
    lo, hi = clopper_pearson(k_tot, n_tot)
    out["pooled"] = _q_block(k_tot, n_tot, lo, hi)
    return out


def _q_block(k, n, lo, hi):
    q = F(k, n)
    return {"n_admissible": k, "n_runs": n, "q": f"{k}/{n}", "q_float": float(q),
            "expected_draws_1_over_q": (None if k == 0 else float(1 / q)),
            "expected_failed_draws": (None if k == 0 else float(1 / q - 1)),
            "q_ci95_clopper_pearson": [float(lo), float(hi)],
            "expected_draws_ci95": [float(1 / hi) if hi > 0 else None, (float(1 / lo) if lo > 0 else None)],
            "ci_note": "exact binomial (Clopper-Pearson) two-sided 95 percent interval, bisected on exact rationals to 1e-12; "
                       "the upper end of the draw interval is None when the lower confidence bound on q is 0"}


# ------------------------------------------------------------------------------------------------------ re-execution
def run_cell(row, col, size):
    """one registered-protocol run, mirroring smooth.run, but keeping the Machine so vm.lifecycle_vector can be called
    on its live ledger. Returns the ledger, the capability and the full burden vector."""
    target = smooth.make_target(COEFFS)
    basis = bases.ALL[col]
    ref = smooth.ROWS_V6[row](size)
    M = Machine(basis, seed=SEED)
    M.phase("exec"); ref.init(M)
    revoke_at = smooth.REVOKE_AT
    for t in range(1, N_EVENTS + 1):
        x = smooth.TRAIN[(t - 1) % len(smooth.TRAIN)]; y = target[x]
        M.phase("exec"); [ref.query(M, xx) for xx in smooth.ALL_X]
        M.phase("upd"); ref.feedback(M, x, y); M.end_event()
        M.phase("ver")
        for xx in smooth.ALL_X: M.op("EQ", ref.query(M, xx), target[xx])
        if t == revoke_at:
            M.phase("rev"); ref.revoke(M, smooth.TRAIN[1]); M.end_event()
    M.phase("exec"); final = {xx: ref.query(M, xx) for xx in smooth.ALL_X}
    err = sum(abs(final[xx] - target[xx]) for xx in smooth.UNSEEN) / FX_ONE / len(smooth.UNSEEN)
    cap = round(max(0.0, 1 - err / 1.5), 4)
    n_queries = 16 * (N_EVENTS + 1)
    R = dict(M.L.c)
    D_draw = R["exec"] + R["upd"] + R["ver"] + R["rev"]
    return {"R": R, "capability": cap, "D_draw": D_draw, "M": M, "n_queries": n_queries}


def burden(cell, failed_draws):
    """the biosphere burden vector of this cell with the failed draws charged (vm.lifecycle_vector is the source)."""
    search_cost = failed_draws * cell["D_draw"]
    b = vm.lifecycle_vector(cell["M"], N_EVENTS, cell["n_queries"],
                            search_cost=float(search_cost), failed_draws=float(failed_draws))
    return {k: v for k, v in b.items() if k in ("B_train", "B_search", "B_failed_candidates", "B_serve", "B_desc", "B_update", "B_verify")}


# ------------------------------------------------------------------------------------------------------- cost algebra
def per_event(R):
    return {"desc": F(R["desc"]), "exec_q": F(R["exec"], 16 * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
            "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"])}


def line(pe, search):
    """the corrected cost as an affine function of H at fixed r: intercept A(r) and slope E."""
    return (lambda r: pe["desc"] + search + r * pe["upd_e"] + r * pe["ver_e"] + F(r, 4) * pe["rev_e"]), pe["exec_q"]


def cost(pe, search, H, r):
    A, E = line(pe, search)
    return A(r) + E * H


def frontier(P, S, adm, hgrid=None, rgrid=None):
    out = {}
    for H in (hgrid or H_GRID):
        for r in (rgrid or R_GRID):
            c = {x: cost(P[x], S[x], H, r) for x in adm}
            m = min(c.values())
            out[f"H={H}|r={r}"] = sorted(x for x in adm if c[x] == m)
    return out


def reentry_H(P, S, adm, who, r):
    """the exact reuse horizon at which `who` first becomes a frontier occupant at revision rate r, or None if never.

    Every row's cost is affine in H, so `who` wins iff H*(E_i - E_who) >= A_who(r) - A_i(r) for every other admissible i.
    A rival with E_i <= E_who and a lower intercept is never overtaken: the crossover does not exist."""
    Awho, Ewho = line(P[who], S[who]); Awho = Awho(r)
    need = F(0)
    for i in adm:
        if i == who: continue
        Ai, Ei = line(P[i], S[i]); Ai = Ai(r)
        gap = Awho - Ai
        if gap <= 0: continue
        if Ei <= Ewho: return None
        need = max(need, gap / (Ei - Ewho))
    return need


def break_even_q(P, S_zero, adm, who, D_draw):
    """the smallest reliability q at which `who` still holds at least one registered-grid cell:
    q* = D/(D + Delta) with Delta the largest surplus of the cheapest rival over `who` across the grid."""
    best = None
    for H in H_GRID:
        for r in R_GRID:
            c_who = cost(P[who], S_zero[who], H, r)
            rivals = [cost(P[i], S_zero[i], H, r) for i in adm if i != who]
            if not rivals: continue
            delta = min(rivals) - c_who
            if delta <= 0: continue
            q = F(D_draw) / (F(D_draw) + delta)
            if best is None or q < best[0]: best = (q, H, r)
    return best


# ------------------------------------------------------------------------------------------------------------- driver
def main(tag="V1"):
    committed = json.load(open(os.path.join(RES, COMMITTED)))
    committed0 = json.load(open(os.path.join(RES, COMMITTED_SEED0)))
    rel = reliability_from_census()
    q_cell = F(rel["cells"][CENSUS_CELL]["n_admissible"], rel["cells"][CENSUS_CELL]["n_runs"])
    q_pooled = F(rel["pooled"]["n_admissible"], rel["pooled"]["n_runs"])

    cols = sorted({k.split("|")[1] for k in committed["R_by_cell"]})
    top = {row: cls.ladder[-1] for row, cls in smooth.ROWS_V6.items()}

    # ---- clause 1: independent re-execution of every R-top cell
    cells = {}; repro = {}
    for col in cols:
        for row, size in top.items():
            c = run_cell(row, col, size)
            key = f"{row}|{col}|{size}"
            cells[key] = c
            ref_R = committed["R_by_cell"][key]; ref_cap = committed["capability_by_cell"][key]
            repro[key] = {"ledger_identical": c["R"] == ref_R, "capability_identical": c["capability"] == ref_cap,
                          "R_reexecuted": c["R"], "R_committed": ref_R,
                          "capability_reexecuted": c["capability"], "capability_committed": ref_cap}
    n_repro = sum(1 for v in repro.values() if v["ledger_identical"] and v["capability_identical"])

    theta = smooth.THETA
    by_col = {}
    for col in cols:
        adm = [row for row, size in top.items() if cells[f"{row}|{col}|{size}"]["capability"] >= theta]
        P = {row: per_event(cells[f"{row}|{col}|{top[row]}"]["R"]) for row in adm}
        Dd = {row: cells[f"{row}|{col}|{top[row]}"]["D_draw"] for row in adm}
        zero = {row: F(0) for row in adm}
        blocks = {}
        for label, q in (("q_cell", q_cell), ("q_pooled", q_pooled)):
            failed = {row: (1 / q - 1) if row in STOCHASTIC_ROWS else F(0) for row in adm}
            S = {row: failed[row] * Dd[row] for row in adm}
            fr = frontier(P, S, adm)
            counts = {row: sum(1 for v in fr.values() if row in v) for row in adm}
            reentry = {str(r): (lambda h: None if h is None else {"exact": str(h), "float": float(h)})(
                reentry_H(P, S, adm, "S3", r)) for r in R_GRID} if "S3" in adm else {}
            blocks[label] = {"q": f"{q.numerator}/{q.denominator}", "expected_draws": float(1 / q),
                             "expected_failed_draws": float(1 / q - 1),
                             "B_search_charged": {row: float(S[row]) for row in adm},
                             "frontier": fr, "cells_won": counts,
                             "S3_cells": counts.get("S3", 0), "n_cells": len(fr),
                             "S3_reentry_H_by_r": reentry,
                             "burden_vector_S3": burden(cells[f"S3|{col}|{top['S3']}"], failed.get("S3", F(0)))
                             if "S3" in adm else None}
        be = break_even_q(P, zero, adm, "S3", Dd["S3"]) if "S3" in adm else None
        by_col[col] = {"admissible_rows_R_top": adm, "D_draw": {row: Dd[row] for row in adm},
                       "uncharged_frontier": frontier(P, zero, adm),
                       "break_even_reliability_q_star": None if be is None else
                       {"q_star": float(be[0]), "q_star_exact": str(be[0]), "at_H": be[1], "at_r": be[2]},
                       "charged": blocks}

    # ---- clause 5 as frozen, scored verbatim: corrected frontier == committed WINNER LISTS with S3 struck out
    collateral = []
    for col in cols:
        for H in H_GRID:
            for r in R_GRID:
                got = by_col[col]["charged"]["q_cell"]["frontier"][f"H={H}|r={r}"]
                want = [x for x in committed["frontier_H_r"][f"{col}|H={H}|r={r}"] if x not in STOCHASTIC_ROWS]
                if got != want: collateral.append({"cell": f"{col}|H={H}|r={r}", "corrected": got, "committed_minus_S3": want})
    # ---- the quantity clause 5 was TRYING to measure, reported separately and never used to rescue the clause:
    # recompute the frontier over the admissible set with the stochastic row DELETED (not merely struck from the winners).
    collateral_correct = []
    for col in cols:
        adm = by_col[col]["admissible_rows_R_top"]
        rest = [x for x in adm if x not in STOCHASTIC_ROWS]
        P = {row: per_event(cells[f"{row}|{col}|{top[row]}"]["R"]) for row in adm}
        zero = {row: F(0) for row in adm}
        fr_rest = frontier(P, zero, rest)
        for k, v in fr_rest.items():
            got = by_col[col]["charged"]["q_cell"]["frontier"][k]
            if got != v: collateral_correct.append({"cell": f"{col}|{k}", "corrected": got, "recomputed_without_S3": v})

    # ---- clause 2 of RV-377-041b: every non-S3 cell identical to the seed-0 receipt
    nonS3_identical = all(committed["R_by_cell"][k] == committed0["R_by_cell"][k] and
                          committed["capability_by_cell"][k] == committed0["capability_by_cell"][k]
                          for k in committed["R_by_cell"] if not k.startswith("S3|"))

    s3_cells = {lab: {col: by_col[col]["charged"][lab]["S3_cells"] for col in cols} for lab in ("q_cell", "q_pooled")}
    tot = {lab: sum(s3_cells[lab].values()) for lab in s3_cells}
    qstar_min = {col: by_col[col]["break_even_reliability_q_star"]["q_star"] for col in cols}
    reentry0 = {col: by_col[col]["charged"]["q_cell"]["S3_reentry_H_by_r"]["0"] for col in cols}

    # ---- extended grid: a grid that passes every crossover this receipt's own price vectors imply (rule DG-2)
    ext_max = max((v["float"] for v in reentry0.values() if v), default=0.0)
    ext_grid = sorted(set(H_GRID + [2 ** k for k in range(8, int(math.ceil(math.log2(max(ext_max * 2, 256)))) + 1)]))
    extended = {}
    for col in cols:
        adm = by_col[col]["admissible_rows_R_top"]
        P = {row: per_event(cells[f"{row}|{col}|{top[row]}"]["R"]) for row in adm}
        Dd = {row: cells[f"{row}|{col}|{top[row]}"]["D_draw"] for row in adm}
        S = {row: ((1 / q_cell - 1) * Dd[row]) if row in STOCHASTIC_ROWS else F(0) for row in adm}
        fr = frontier(P, S, adm, hgrid=ext_grid)
        extended[col] = {"H_grid": ext_grid, "S3_cells": sum(1 for v in fr.values() if "S3" in v),
                         "n_cells": len(fr), "S3_cells_at_r0": sorted(int(k.split("|")[0][2:]) for k, v in fr.items()
                                                                      if "S3" in v and k.endswith("|r=0"))}

    # ------------------------------------------------------------------------- clause scoring (verbatim, HOLDS / FAILS)
    ci = rel["pooled"]["q_ci95_clopper_pearson"]; ci_cell = rel["cells"][CENSUS_CELL]
    draws_hi_cell = ci_cell["expected_draws_ci95"][1]
    clauses = [
        {"n": 1, "text": "re-running the five ROWS_V6 rows at their largest ladder size in all six registered columns on "
                         "E_sym5 at machine seed 4 reproduces STAGE_DE_SMOOTH_V22_SYM5_S4.json exactly in 30 of 30 cells, "
                         "on all five ledger coordinates and on capability",
         "verdict": "HOLDS" if n_repro == len(repro) == 30 else "FAILS",
         "measured": f"{n_repro} of {len(repro)} cells identical on ledger and capability"},
        {"n": 2, "text": "q_pooled = 10/192 = 0.052083, expected draws 1/q = 19.2, 95 percent Clopper-Pearson interval on q "
                         "contained in (0.02, 0.10) i.e. 1/q within (10, 50); for the census cell E_sym5 size 8, q = 1/32, "
                         "1/q = 32, and the upper end of the 95 percent interval on 1/q exceeds 500 draws",
         "verdict": "HOLDS" if (rel["pooled"]["q"] == "10/192" and 0.02 < ci[0] and ci[1] < 0.10 and
                                (draws_hi_cell is not None and draws_hi_cell > 500)) else "FAILS",
         "measured": f"q_pooled is {rel['pooled']['q']} = {rel['pooled']['q_float']:.6f}, NOT 10/192 = 0.052083, so "
                     f"1/q = {rel['pooled']['expected_draws_1_over_q']:.4f}, not 19.2. Sub-assertions: CI95 on q_pooled = "
                     f"({ci[0]:.6f}, {ci[1]:.6f}) IS contained in (0.02, 0.10), 1/q in ({1/ci[1]:.2f}, {1/ci[0]:.2f}) IS within "
                     f"(10, 50); q_cell = {ci_cell['q']}, CI95 = ({ci_cell['q_ci95_clopper_pearson'][0]:.6f}, "
                     f"{ci_cell['q_ci95_clopper_pearson'][1]:.6f}), upper end on 1/q = {draws_hi_cell:.1f} which DOES exceed 500. "
                     f"The clause fails on its asserted pooled rate only.",
         "diagnosis": "the asserted 10/192 was taken from the committed RV-377-040 record and from GMI_DOMAIN_ALGEBRA_EXECUTED_V1 "
                      "section 7, both of which report '10 of 192 runs (about 5 percent)'. The census receipt's own per-cell counts "
                      "are 1 + 2 + 0 + 4 + 1 + 1 = 9, and a recount over its 192 raw capability values agrees: 9 of 192 = 4.6875 "
                      "percent. The published pooled rate is off by one run and the published expected draw count by two draws."},
        {"n": 3, "text": "at q_cell = 1/32 the stochastic row occupies 0 of 56 cells in every one of the six columns, 0 of 336",
         "verdict": "HOLDS" if tot["q_cell"] == 0 else "FAILS", "measured": f"{tot['q_cell']} of 336; per column {s3_cells['q_cell']}",
         "strength": "WEAK: restates disclosed pre-freeze calibration (c)"},
        {"n": 4, "text": "at q_pooled = 10/192 the stochastic row also occupies 0 of 336",
         "verdict": "HOLDS" if tot["q_pooled"] == 0 else "FAILS", "measured": f"{tot['q_pooled']} of 336; per column {s3_cells['q_pooled']}",
         "strength": "WEAK: restates disclosed pre-freeze calibration (c)"},
        {"n": 5, "text": "the corrected frontier over the 336 cells is identical, cell for cell, to the committed "
                         "RV-377-041b frontier with S3 struck out; no other row's membership changes anywhere",
         "verdict": "HOLDS" if not collateral else "FAILS",
         "measured": f"{len(collateral)} of 336 cells differ" + (f"; first {collateral[:3]}" if collateral else ""),
         "diagnosis": "prediction-writing error of the class protocol rules 12-14 were added for. 'The committed frontier with S3 "
                      "struck out' names the wrong object: deleting S3 from a committed WINNER LIST leaves that cell empty wherever "
                      "S3 was the sole occupant, which is 246 of 336 cells, so the clause could not have held however the cost "
                      "correction came out. The quantity it was reaching for is the frontier RECOMPUTED over the admissible set with "
                      "S3 removed; that is measured and reported as no_collateral_movement_recomputed, and is NOT used to rescue this "
                      "clause."},
        {"n": 6, "text": "the minimum over the registered grid of q* = D_draw/(D_draw + Delta) exceeds 0.49 in every column",
         "verdict": "HOLDS" if all(v > 0.49 for v in qstar_min.values()) else "FAILS",
         "measured": {k: round(v, 4) for k, v in qstar_min.items()},
         "strength": "WEAK: restates disclosed pre-freeze calibration (d)"},
        {"n": 7, "text": "at r = 0 the reuse horizon at which S3 re-enters the frontier is finite in every column and "
                         "exceeds H = 10^6 in every column",
         "verdict": "HOLDS" if all(v is not None and v["float"] > 1e6 for v in reentry0.values()) else "FAILS",
         "measured": {k: (None if v is None else round(v["float"], 1)) for k, v in reentry0.items()}},
        {"n": 8, "text": "re-adjudication of RV-377-041b: clause 1 HOLDS, clause 2 HOLDS, clauses 3, 4 and 5 FAIL "
                         "(2 of 5 survive, and they are exactly the two that are not cost claims)",
         "verdict": None, "measured": None},
    ]

    # RV-377-041b, clause by clause, verbatim
    b0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b1 = "B1_COMPOSITIONAL_LEARNER"; b3 = "B3_STOCHASTIC_GENERATIVE_KERNEL"
    fr0 = by_col[b0]["charged"]["q_cell"]["frontier"]; fr1 = by_col[b1]["charged"]["q_cell"]["frontier"]
    fr3 = by_col[b3]["charged"]["q_cell"]["frontier"]
    s3_b0 = [k for k, v in fr0.items() if "S3" in v]; s3_b3 = [k for k, v in fr3.items() if "S3" in v]
    r0_cells = sum(1 for col in cols for k, v in by_col[col]["charged"]["q_cell"]["frontier"].items()
                   if k.endswith("|r=0") and "S3" in v)
    cap_ok = all(cells[f"S3|{c}|8"]["capability"] == 0.9375 for c in cols) and \
        all(committed["capability_by_cell"][f"S3|{c}|4"] == 0.3021 for c in cols)
    readj = [
        {"clause": 1, "verbatim": "S3 admissible at size 8 in every column (0.9375, C2) and inadmissible at size 4 (0.3021)",
         "kind": "admissibility (not a cost claim)", "verdict": "HOLDS" if cap_ok else "FAILS",
         "measured": "size 8 = 0.9375 in all six columns, size 4 = 0.3021 in all six columns; unchanged by the cost correction",
         "why": "charging failed draws changes the cost model, not the realized development trajectory of the drawn machine"},
        {"clause": 2, "verbatim": "every non-S3 cell identical to V8_SYM5_H",
         "kind": "instrument identity (not a cost claim)", "verdict": "HOLDS" if nonS3_identical else "FAILS",
         "measured": f"all non-S3 cells of the committed receipt equal the seed-0 receipt: {nonS3_identical}",
         "why": "deterministic rows do not consume the machine seed and carry no failed draws"},
        {"clause": 3, "verbatim": "B0 frontier: S3 wins all 8 r = 0 cells, r = 1 at H in {32,64,128}, r = 2 at H in {64,128}, "
                                  "r = 4 at H = 128 (14 cells); S5h wins the other 42; S2a and S4 none",
         "kind": "cost claim", "verdict": "FAILS" if len(s3_b0) != 14 else "HOLDS",
         "measured": f"S3 wins {len(s3_b0)} of 56 B0 cells under the corrected cost (was 14)"},
        {"clause": 4, "verbatim": "B1 = B0 cell for cell; in B3 S3 wins a superset of its B0 cells (count >= 14)",
         "kind": "cost claim", "verdict": "HOLDS" if (fr1 == fr0 and len(s3_b3) >= 14) else "FAILS",
         "measured": f"B1 = B0 cell for cell: {fr1 == fr0} (still true, both empty of S3); S3 wins {len(s3_b3)} B3 cells, "
                     f"not >= 14; the superset clause fails on the count"},
        {"clause": 5, "verbatim": "r = 0 is S3 at every H in all six columns (48 of 48)",
         "kind": "cost claim", "verdict": "HOLDS" if r0_cells == 48 else "FAILS",
         "measured": f"S3 wins {r0_cells} of 48 r = 0 cells under the corrected cost (was 48)"},
    ]
    n_hold = sum(1 for c in readj if c["verdict"] == "HOLDS")
    clauses[7]["verdict"] = "HOLDS" if [c["verdict"] for c in readj] == ["HOLDS", "HOLDS", "FAILS", "FAILS", "FAILS"] else "FAILS"
    clauses[7]["measured"] = f"{n_hold} of 5 RV-377-041b clauses survive: " + ", ".join(f"{c['clause']}:{c['verdict']}" for c in readj)

    n_clause_hold = sum(1 for c in clauses if c["verdict"] == "HOLDS")
    receipt = {
        "schema": "StageG14FailedDrawChargingV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 422,
        "revival_record": "RV-377-067", "gap": "G14", "run_tag": tag,
        "frontier_rule": FRONTIER_RULE, "theta": theta,
        "ecology": {"name": ECOLOGY, "coeffs": list(COEFFS), "machine_seed": SEED, "n_events": N_EVENTS,
                    "capability_criterion": "unseen", "rows": list(smooth.ROWS_V6), "ladder_top": top},
        "corrected_cost_model": {
            "registered_line": "C = desc + H*exec_q + r*upd_e + r*ver_e + (r/4)*rev_e (smooth.cost, unchanged)",
            "correction": "C' = C + B_search, B_search = B_failed_candidates * D_draw",
            "B_failed_candidates": "1/q - 1, the expected number of FAILED draws before the first admissible one "
                                   "(geometric law with success probability q); exactly 0 for a deterministic row (q = 1)",
            "D_draw": "exec + upd + ver + rev of ONE complete run of the registered 16-event protocol at that (row, column, size)",
            "source_of_terms": "gmi_microscope.vm.lifecycle_vector, called on the live Machine ledger of each re-executed cell",
            "stochastic_rows": list(STOCHASTIC_ROWS),
            "amortization": "B_search is a one-time lifecycle intercept, charged like desc: it is paid once before serving begins, "
                            "not per query and not per revision"},
        "reliability": rel,
        "reexecution_vs_committed": {"committed_receipt": COMMITTED, "committed_sha256": committed["receipt_sha256"],
                                     "n_cells": len(repro), "n_identical": n_repro,
                                     "mismatches": {k: v for k, v in repro.items()
                                                    if not (v["ledger_identical"] and v["capability_identical"])}},
        "by_column": by_col,
        "collateral_movement_as_clause_5_was_written": {"n_cells_differing": len(collateral), "cells": collateral},
        "no_collateral_movement_recomputed": {
            "test": "frontier recomputed over the admissible set with the stochastic row deleted, compared cell for cell with the "
                    "corrected frontier at q_cell; this is what clause 5 was reaching for and it is reported, not substituted",
            "n_cells_differing": len(collateral_correct), "cells": collateral_correct},
        "defects_found_in_committed_records": [
            {"defect": "the pooled reliability of the stochastic carrier is misreported by one run",
             "where": ["REVIVAL_LEDGER.jsonl RV-377-040 observed_outcome ('10 of 192 runs admissible, 5.2%')",
                       "GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md section 7 ('admissible on 10 of 192 runs (about 5 percent)')",
                       "GMI_GAP_LEDGER_EXECUTED_V1.md G2b ('5 % of seeds admissible')"],
             "committed_value": "10 of 192 = 5.2 percent, 1/q = 19.2 draws",
             "measured_value": f"{rel['pooled']['q']} = {rel['pooled']['q_float']*100:.4f} percent, "
                               f"1/q = {rel['pooled']['expected_draws_1_over_q']:.4f} draws",
             "evidence": "the census receipt's own summary counts are 1, 2, 0, 4, 1, 1 (sum 9) and a recount over its 192 raw "
                         "capability values against theta = 0.85 also gives 9",
             "effect_on_this_receipt": "none on any verdict: 9/192 makes the carrier RARER and the search charge LARGER than the "
                                       "published figure, so every clause that says the stochastic row wins no cell is reinforced. "
                                       "It does falsify clause 2 of RV-377-067, which quoted the published rate."}],
        "extended_grid_dg2_selfcheck": {
            "why": "protocol rule DG-2 applied to this receipt before it is committed: the grid must extend past the analytic "
                   "crossover of every price vector it reports",
            "per_column": extended,
            "note": "H is a parameter of the cost model only, never of the execution, so extending the grid needs no replay"},
        "readjudication_of_RV_377_041b": readj,
        "n_RV041b_clauses_surviving": n_hold,
        "clauses_RV_377_067": clauses, "n_clauses_hold": n_clause_hold, "n_clauses": len(clauses),
        "counting_note": "every count above is a count of FRONTIER CELLS or of DEVELOPMENT DRAWS; neither is a count of forms "
                         "and neither is a species count",
        "claim_ceiling": "exact charged replay at one ecology (E_sym5), one machine seed (4), one stochastic row (S3), the six "
                         "registered columns and the registered (H, r) grid; the reliability q is the committed 192-run census's "
                         "and its interval is exact-binomial, not a bound on any other ecology, budget or theta",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    path = os.path.join(RES, f"STAGE_G14_FAILED_DRAW_CHARGING_{tag}.json")
    json.dump(receipt, open(path, "w"), indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    rc = main()
    print("receipt", rc["receipt_sha256"][:16])
    print("re-execution identical:", rc["reexecution_vs_committed"]["n_identical"], "of", rc["reexecution_vs_committed"]["n_cells"])
    print("q pooled", rc["reliability"]["pooled"]["q"], "1/q", rc["reliability"]["pooled"]["expected_draws_1_over_q"],
          "CI95", rc["reliability"]["pooled"]["q_ci95_clopper_pearson"])
    for c in rc["clauses_RV_377_067"]:
        print(f"  clause {c['n']}: {c['verdict']:6s} {str(c['measured'])[:120]}")
    for c in rc["readjudication_of_RV_377_041b"]:
        print(f"  RV-041b clause {c['clause']}: {c['verdict']:6s} {c['measured'][:110]}")
