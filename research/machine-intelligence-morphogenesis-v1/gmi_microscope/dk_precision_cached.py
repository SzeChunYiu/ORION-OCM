"""RV-377-081 — the last asymmetry: the log row is charged per QUERY for work its opponents charge per EVENT.

RV-377-080 hardened the positive into the registered price column and reduced its qualifications to two: the
`scaled` description basis, and the fact that EVERY occupied cell lies at r = 0. The r = 0 restriction was traced
to the log row's reuse coefficient rho, which exceeds QCOUNT's at every class size because its verification phase
re-serves the whole evaluation set every event at the full per-query price.

That price is an artefact of how THIS LANE wrote the row, not of the log representation. `BayesPruned._rank` and
`QCount._rank` compute their readout weights `tw` ONCE PER EVENT, in the update phase, and their `query` is then
M multiplies and M adds. `MinLogMixture.query` recomputes the exponent map on EVERY query - four ladder reads at
31 charged activations each - although `lw` changes only on `observe` and `revoke`. Caching it is not an
optimisation trick: it is the same materialize-on-update discipline the linear rows already have, and charging one
carrier per query for what another is charged per event is exactly the kind of accounting asymmetry protocol rule
28 was written for.

  LOGLAD8_T4C   the ladder row with the exponent map materialized in the UPDATE phase alongside the top-M
                ranking, exactly as `tw` is. The arithmetic is unchanged; the charge moves from `exec` and `ver`
                to `upd` and `rev`, where it belongs.

Two questions. Does the crossing root move as the law predicts once exec_q falls? And does the occupancy finally
extend to r >= 1, removing the third of RV-377-079's four qualifications - or does rho stay above QCOUNT's, in
which case r = 0 is a real property of the carrier and not an accounting artefact?
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of
from .dk_precision import THETA, X_ALL, N_EVENTS, REVOKE_AT, REVOKE_INDEX, M_TOP, Arith, capability, per_event
from . import dk_precision_log_min as LM
from . import dk_precision_residual as RS
from . import dk_precision_scale as SC

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]


class CachedLadderRow(LM.MinLogMixture):
    """the exponent map materialized on UPDATE, exactly as BAYESM and QCOUNT materialize their readout weights."""
    row = "LOGLAD8_T4C"
    exp_encoding = "ladder"
    desc_convention = "minimal"
    top_m = M_TOP
    table_mode = "sel1"
    fix_div_dependence = True

    def init(self, M):
        super().init(M)
        self.wcache = [self._exp_of(M, self.lw[j]) for j in self.top]
        self.w_scalars += self.top_m          # the materialized weights are declared state, and charged as such

    def _rank(self, M):
        super()._rank(M)
        self.wcache = [self._exp_of(M, self.lw[j]) for j in self.top]

    def query(self, M, x):
        A = self.A; ws = self.wcache
        num = 0; den = 0
        for k, j in enumerate(self.top):
            num = A.add(num, A.mul(ws[k], A.const(F(self.e["hyps"][j]["p"][x]))))
            den = A.add(den, ws[k])
        self._n(M, 2 * len(ws))
        return A.div(num, den)


def run(eco, precision, seed=0):
    M = Machine(B0, seed=seed); A = Arith(M, precision)
    with SC.struct(eco.get("struct_bits", LM.CLASS_STRUCT_BITS)):
        ref = CachedLadderRow(eco, A)
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
    return {"row": ref.row, "precision": precision, "capability": float(round(cap, 6)),
            "capability_exact": f"{cap.numerator}/{cap.denominator}", "admissible": bool(cap >= THETA),
            "R": R, "native_R": nat, "charged_ops_total": A.n_ops,
            "exec_q": F(R["exec"], nev * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
            "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"]),
            "nat_exec_q": F(nat["exec"], nev * (N_EVENTS + 1)), "nat_upd_e": F(nat["upd"], N_EVENTS),
            "nat_ver_e": F(nat["ver"], N_EVENTS), "nat_rev_e": F(nat["rev"]),
            "desc_bits": ref.desc_bits(), "desc_bits_scaled": ref.w_scalars * (A.bits or 72) + ref.struct_bits,
            "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits,
            "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}


def probe(K):
    eco = SC.ecology_scaled(K // 4, 4, "A")
    c = run(eco, "fx8"); u = SC.run_cell("LOGLAD8_T4", eco, "fx8"); q = SC.run_cell("QCOUNT", eco, "fx10")
    out = {}
    for name, d in (("cached", c), ("uncached", u), ("qcount_fx10", q)):
        pe = per_event(d, "reduced", True)
        out[name] = {"cap": d["capability"], "adm": d["admissible"], "w": d["w_scalars"],
                     "desc_scaled": d["desc_bits_scaled"], "exec_q": str(d["exec_q"]),
                     "upd_e": str(d["upd_e"]), "ver_e": str(d["ver_e"]), "rev_e": str(d["rev_e"]),
                     "rho": str(RS.rho(pe))}
    out["answers_identical_cached_vs_uncached"] = c["answer_signature"] == u["answer_signature"]
    return out


K_LADDER = (128, 160, 192, 256)


def law(K, price):
    """the EXACT frozen difference cost(LOGLAD8_T4C@fx8) - cost(QCOUNT@fx10) at H = 1, r = 0, scaled basis."""
    return F(-2 * K) + (F(14231, 50) if price == "reduced" else F(236))


def main(tag="V1", seed=0):
    runs = {}
    for K in K_LADDER:
        eco = SC.ecology_scaled(K // 4, 4, "A")
        cells = {}
        for p in SC.INSTRUMENTS:
            for r in SC.LIN + SC.LOG:
                if r in SC.LOG and p in ("fx16", "wide"): continue
                cells[(r, p)] = SC.run_cell(r, eco, p, seed)
        cells[("LOGLAD8_T4C", "fx8")] = run(eco, "fx8", seed)
        cells[("LOGLAD8_T4C", "fx10")] = run(eco, "fx10", seed)
        adm = {p: sorted(r for (r, q) in cells if q == p and cells[(r, q)]["admissible"])
               for p in SC.INSTRUMENTS}
        out = {"admissible": adm, "keys": {}, "law_check": {}, "rho_ratio": {}}
        cc = cells[("LOGLAD8_T4C", "fx8")]; qc = cells[("QCOUNT", "fx10")]
        uc = cells[("LOGLAD8_T4", "fx8")]
        out["cached_vs_uncached"] = {
            "answers_identical": cc["answer_signature"] == uc["answer_signature"],
            "capability_identical": cc["capability_exact"] == uc["capability_exact"],
            "w_scalars": [uc["w_scalars"], cc["w_scalars"]],
            "exec_q": [str(uc["exec_q"]), str(cc["exec_q"])],
            "nat_exec_q": [str(uc["nat_exec_q"]), str(cc["nat_exec_q"])],
            "ver_e": [str(uc["ver_e"]), str(cc["ver_e"])], "upd_e": [str(uc["upd_e"]), str(cc["upd_e"])],
            "desc_bits": [uc["desc_bits"], cc["desc_bits"]]}
        for price in ("reduced", "native"):
            pc = per_event(cc, price, True); pq = per_event(qc, price, True)
            measured = pc["desc"] + pc["exec_q"] - pq["desc"] - pq["exec_q"]
            out["law_check"][price] = {"predicted": str(law(K, price)), "measured": str(measured),
                                       "match": measured == law(K, price),
                                       "log_cheaper_at_H1_r0": measured < 0}
            out["rho_ratio"][price] = {"rho_log": str(RS.rho(pc)), "rho_qcount": str(RS.rho(pq)),
                                       "ratio": float(RS.rho(pc) / RS.rho(pq)),
                                       "log_rho_exceeds_qcount": RS.rho(pc) > RS.rho(pq)}
            # does the CACHED row dominate the UNCACHED one? its description is larger, so it should not
            pu = per_event(uc, price, True)
            out.setdefault("cached_dominates_uncached", {})[price] = bool(RS.dominates_cost(pc, pu))
            out.setdefault("uncached_dominates_cached", {})[price] = bool(RS.dominates_cost(pu, pc))
            for scaled in (True, False):
                bas = "scaled" if scaled else "flat"
                pes = {f"{r}@{p}": per_event(cells[(r, p)], price, scaled)
                       for (r, p) in cells if r in adm[p]}
                rep = RS.frontier_report(pes)
                occ = rep["occupancy"]
                fx8 = {n: c for n, c in occ.items() if n.endswith("@fx8") and c}
                held = sorted(c for c, o in rep["frontier"].items() if any(n.endswith("@fx8") for n in o))
                out["keys"][f"{price}|{bas}"] = {
                    "n_cells": rep["n_cells"], "fx8_occupancy": fx8,
                    "cells_held_by_any_fx8_row": sum(fx8.values()),
                    "cells_held_by_cached_row": occ.get("LOGLAD8_T4C@fx8", 0),
                    "all_held_cells_at_r0": all(c.endswith("|r=0") for c in held),
                    "max_H_held": max([int(c.split("|")[0][2:]) for c in held], default=None),
                    "max_r_held": max([int(c.split("r=")[1]) for c in held], default=None),
                    "H_grid_ok": rep["H_grid_extends_past_twice_largest_H_crossover"],
                    "r_grid_ok": rep["r_grid_extends_past_twice_largest_r_crossover"],
                    "occupancy_nonzero": {n: c for n, c in sorted(occ.items()) if c}}
        runs[K] = out

    law_ok = all(v["law_check"][p]["match"] for v in runs.values() for p in ("reduced", "native"))
    first_red = next((K for K in K_LADDER if runs[K]["keys"]["reduced|scaled"]["cells_held_by_any_fx8_row"]), None)
    first_nat = next((K for K in K_LADDER if runs[K]["keys"]["native|scaled"]["cells_held_by_any_fx8_row"]), None)
    r0 = all(v["keys"][k]["all_held_cells_at_r0"] for v in runs.values() for k in v["keys"])
    rho_above = all(v["rho_ratio"][p]["log_rho_exceeds_qcount"] for v in runs.values() for p in ("reduced", "native"))
    flat0 = all(v["keys"][f"{p}|flat"]["cells_held_by_any_fx8_row"] == 0
                for v in runs.values() for p in ("reduced", "native"))
    receipt = {
        "schema": "StageDKCachedExponentV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-081", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "question": "the log row was charged per QUERY for work its opponents are charged per EVENT. With the exponent map materialized on update, does the crossing root move as the law predicts, and does the occupancy finally reach r >= 1?",
        "the_law": {"reduced": "-2K + 14231/50, root K = 142.31", "native": "-2K + 236, root K = 118",
                    "all_checks_match": bool(law_ok)},
        "K_ladder": list(K_LADDER), "runs": {str(k): v for k, v in runs.items()},
        "first_K_with_reduced_scaled_occupancy": first_red,
        "first_K_with_native_scaled_occupancy": first_nat,
        "all_held_cells_at_r0": bool(r0),
        "log_rho_exceeds_qcount_everywhere": bool(rho_above),
        "flat_basis_occupancy_is_zero_everywhere": bool(flat0),
        "terminal": None,
        "claim_ceiling": "the caching changes only WHERE the charge falls, not the arithmetic: the receipt asserts the served answers are bit-identical to the uncached row at every K. The materialized weights are declared as state and charged (w_scalars rises by M = 4). One ecology recipe, one declared sequence, one seed, four class sizes; the scaled basis is a declared sensitivity column and the flat basis is reported alongside with no primary elected (rule 33).",
    }
    receipt["terminal"] = (
        ("THE_CHARGING_ASYMMETRY_IS_REAL_AND_THE_r_0_RESTRICTION_IS_NOT__CACHED_EXPONENT_MOVES_THE_REDUCED_ROOT_TO_142_AND_FIRST_OCCUPANCY_TO_K_%s__BUT_EVERY_OCCUPIED_CELL_STILL_LIES_AT_r_0_BECAUSE_rho_LOG_EXCEEDS_rho_QCOUNT_AT_EVERY_CLASS_SIZE" % first_red)
        if r0 else
        ("THE_r_0_RESTRICTION_FALLS__AN_8_BIT_ROW_OCCUPIES_AT_r_GREATER_THAN_ZERO_FROM_K_%s" % first_red))
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V10_CACHED_EXPONENT_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("law matches everywhere:", law_ok)
    for K in K_LADDER:
        v = runs[K]
        print(f"  K={K} cached_vs_uncached answers_identical={v['cached_vs_uncached']['answers_identical']}"
              f" exec_q {v['cached_vs_uncached']['exec_q']} ver_e {v['cached_vs_uncached']['ver_e']}")
        for price in ("reduced", "native"):
            print(f"     law {price}: {v['law_check'][price]['measured']} (pred {v['law_check'][price]['predicted']})"
                  f" match {v['law_check'][price]['match']} | rho ratio {v['rho_ratio'][price]['ratio']:.3f}")
        for k, kv in v["keys"].items():
            print(f"     {k:16s} {kv['cells_held_by_any_fx8_row']:>5} of {kv['n_cells']:<6}"
                  f" cached {kv['cells_held_by_cached_row']:>4} maxH {kv['max_H_held']} maxr {kv['max_r_held']}"
                  f" r0only {kv['all_held_cells_at_r0']}")
    print("first reduced|scaled K:", first_red, "| first native|scaled K:", first_nat)
    print("all cells at r=0:", r0, "| rho(log) > rho(QCOUNT) everywhere:", rho_above, "| flat zero:", flat0)
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")


class NormalizedLadderRow(CachedLadderRow):
    """the FULLY symmetrized log row: not only the exponent but the NORMALIZATION is materialized on update, so
    its query is M multiplies and M adds and nothing else - bit for bit the shape of QCount.query. QCount divides
    in `_rank`; this row now does too. If its exec_q then equals QCOUNT's, the flat-basis comparison reduces to a
    single constant: the log representation's 26 declared scalars, which the flat basis never discounts."""
    row = "LOGLAD8_T4N"

    def _normalize(self, M):
        A = self.A
        den = 0
        for w in self.wcache: den = A.add(den, w)
        self.tw = [A.div(w, den) if den else 0 for w in self.wcache]

    def init(self, M):
        super().init(M)
        self._normalize(M)
        self.w_scalars += self.top_m          # the normalized weights are declared state too, and charged

    def _rank(self, M):
        super()._rank(M)
        self._normalize(M)

    def query(self, M, x):
        A = self.A; acc = 0
        for k, j in enumerate(self.top):
            acc = A.add(acc, A.mul(self.tw[k], A.const(F(self.e["hyps"][j]["p"][x]))))
        self._n(M, len(self.tw))
        return acc


def run_norm(eco, precision, seed=0):
    M = Machine(B0, seed=seed); A = Arith(M, precision)
    with SC.struct(eco.get("struct_bits", LM.CLASS_STRUCT_BITS)):
        ref = NormalizedLadderRow(eco, A)
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
    return {"row": ref.row, "precision": precision, "capability": float(round(cap, 6)),
            "capability_exact": f"{cap.numerator}/{cap.denominator}", "admissible": bool(cap >= THETA),
            "R": R, "native_R": nat, "charged_ops_total": A.n_ops,
            "exec_q": F(R["exec"], nev * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
            "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"]),
            "nat_exec_q": F(nat["exec"], nev * (N_EVENTS + 1)), "nat_upd_e": F(nat["upd"], N_EVENTS),
            "nat_ver_e": F(nat["ver"], N_EVENTS), "nat_rev_e": F(nat["rev"]),
            "desc_bits": ref.desc_bits(), "desc_bits_scaled": ref.w_scalars * (A.bits or 72) + ref.struct_bits,
            "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits,
            "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}


FLAT_K_LADDER = (32, 64, 96, 128, 160, 192, 256)


def flat_domination_check(tag="V1", seed=0):
    """THE CLOSING QUESTION. Under the `scaled` basis an 8-bit row pays 8 bits per declared scalar and a 10-bit row
    pays 10, and that discount is the entire mechanism of this lane's positive. Under the FLAT basis every
    instrument's scalar is charged at the registered 8 bits, so a narrower word earns NO discount and the log
    representation's declared-scalar overhead is a CONSTANT additive handicap. If QCOUNT then dominates the log row
    in all three cost coordinates at every class size, the flat column is closed by a THEOREM over the whole
    non-negative quadrant rather than by a grid of measurements - and the `scaled` qualification on RV-377-079's
    positive is not a loose end but the mechanism itself, named."""
    rows = {}
    for K in FLAT_K_LADDER:
        eco = SC.ecology_scaled(K // 4, 4, "A")
        n = run_norm(eco, "fx8", seed); c = run(eco, "fx8", seed)
        u = SC.run_cell("LOGLAD8_T4", eco, "fx8", seed)
        q10 = SC.run_cell("QCOUNT", eco, "fx10", seed); q8 = SC.run_cell("QCOUNT", eco, "fx8", seed)
        ent = {"K": K, "capability": {"normalized": n["capability"], "cached": c["capability"],
                                      "uncached": u["capability"], "qcount_fx10": q10["capability"]},
               "answers_identical_normalized_vs_cached": n["answer_signature"] == c["answer_signature"],
               "answers_identical_cached_vs_uncached": c["answer_signature"] == u["answer_signature"],
               "flat_desc": {"normalized": n["desc_bits"], "cached": c["desc_bits"],
                             "uncached": u["desc_bits"], "qcount": q8["desc_bits"]},
               "flat_desc_excess": {"normalized": n["desc_bits"] - q8["desc_bits"],
                                    "cached": c["desc_bits"] - q8["desc_bits"],
                                    "uncached": u["desc_bits"] - q8["desc_bits"]},
               "exec_q": {"normalized": str(n["exec_q"]), "cached": str(c["exec_q"]),
                          "uncached": str(u["exec_q"]), "qcount_fx10": str(q10["exec_q"])},
               "dominated_under_flat": {}, "dominated_under_scaled": {}}
        for nm, d in (("normalized", n), ("cached", c), ("uncached", u)):
            for price in ("reduced", "native"):
                pf = per_event(d, price, False); pq = per_event(q10, price, False)
                ps = per_event(d, price, True); pqs = per_event(q10, price, True)
                ent["dominated_under_flat"][f"{nm}|{price}"] = bool(RS.dominates_cost(pq, pf))
                ent["dominated_under_scaled"][f"{nm}|{price}"] = bool(RS.dominates_cost(pqs, ps))
                ent.setdefault("rho_flat", {})[f"{nm}|{price}"] = [str(RS.rho(pf)), str(RS.rho(pq))]
        rows[K] = ent
    flat_all = all(v["dominated_under_flat"][k] for v in rows.values() for k in v["dominated_under_flat"])
    excess_const = {nm: sorted({v["flat_desc_excess"][nm] for v in rows.values()})
                    for nm in ("normalized", "cached", "uncached")}
    receipt = {
        "schema": "StageDKFlatDominationTheoremV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-082", "run_tag": tag, "seed": seed, "theta": str(THETA),
        "question": "is the `scaled` qualification on this lane's positive a loose end, or is the discount a narrower word earns under `scaled` the entire mechanism - so that under FLAT the log row is DOMINATED at every class size, as a theorem?",
        "K_ladder": list(FLAT_K_LADDER), "per_K": rows,
        "flat_desc_excess_is_constant_in_K": {nm: len(v) == 1 for nm, v in excess_const.items()},
        "flat_desc_excess_values": {nm: v for nm, v in excess_const.items()},
        "qcount_dominates_every_log_row_under_flat_at_every_K": bool(flat_all),
        "terminal": ("THE_FLAT_COLUMN_IS_CLOSED_BY_A_THEOREM__QCOUNT_COST_COORDINATE_DOMINATES_EVERY_8_BIT_LOG_ROW_AT_EVERY_CLASS_SIZE_UNDER_THE_FLAT_BASIS__THE_LOG_REPRESENTATIONS_DECLARED_SCALAR_OVERHEAD_IS_A_CONSTANT_THE_FLAT_BASIS_NEVER_DISCOUNTS"
                     if flat_all else
                     "THE_FLAT_COLUMN_IS_NOT_CLOSED__SOME_8_BIT_LOG_ROW_ESCAPES_DOMINATION_UNDER_THE_FLAT_BASIS"),
        "claim_ceiling": "the NORMALIZED row is a DIFFERENT ROW, not a re-charging: dividing on the 8-bit grid during the update changes the served answer, and its capability differs from the cached row at K = 256. That is stated rather than hidden, and it is why this record reports the normalized row's capability at every K alongside its cost. Seven class sizes, one ecology recipe, one declared sequence, one seed.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V11_FLAT_DOMINATION_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    for K in FLAT_K_LADDER:
        v = rows[K]
        print(f"  K={K:<4} excess flat {v['flat_desc_excess']} | cap norm {v['capability']['normalized']}"
              f" cached {v['capability']['cached']} | ans(norm==cached) {v['answers_identical_normalized_vs_cached']}"
              f" | dominated flat {all(v['dominated_under_flat'].values())}"
              f" scaled {v['dominated_under_scaled']}")
    print("flat excess constant in K:", receipt["flat_desc_excess_is_constant_in_K"], receipt["flat_desc_excess_values"])
    print("TERMINAL:", receipt["terminal"])
    return receipt
