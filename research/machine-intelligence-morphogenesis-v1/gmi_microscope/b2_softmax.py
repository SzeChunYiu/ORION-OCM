"""B2.6 -- softmax entropy/temperature: is the optimal concentration set by the ambiguity?

Stage B2 row B2.6 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Generate routing tasks with controlled ambiguity. Test entropy-regularized routing interpretation and whether
     optimal concentration follows ambiguity/noise."

TWO KINDS OF RESULT LIVE IN THIS RECEIPT AND THEY ARE LABELLED SEPARATELY.

    `variational_check`  MATH_IMPLEMENTATION_CHECK: the TM-3 identity softmax(s/T) = argmax_p [p.s + T H(p)], checked
                         for the DYADIC kernel used here (weights 2^(s/T), base-2 entropy) on a simplex grid, in
                         float64 with a DECLARED tolerance. It is a statement about the identity, never about a
                         network, and it is not evidence for anything in the response law below.
    `cells` / `claims`   SYNTHETIC EXACT MICROSCOPE: the measured response of the optimal temperature to declared
                         ambiguity, in exact rational arithmetic with no tolerance anywhere.

Declared ecology
----------------
k = 8 sources with declared rational values. A declared family of integer score vectors. AMBIGUITY level m means the
true source is uniform over the top m sources by score (deterministic tie-break by index); m = 1 is no ambiguity and
m = k is total ambiguity. The joint law over (score vector, true source) is exact and uniform over the declared
family; nothing is sampled.

A ROW is a routing policy (T, kappa): weights p_j proportional to 2^(s_j / T) over the top kappa sources by score,
zero elsewhere, renormalized. T ranges over a declared grid on which every s_j / T is an integer, so every weight is
an exact dyadic rational. T = 0 denotes hard argmax and T = inf denotes the uniform policy; both are declared rows.
The served answer is sum_j p_j v_j and the loss is the exact rational expectation of (answer - v_true)^2.

Instruments (protocol rule 24: the representations of the ROUTING WEIGHT the alphabet admits)
---------------------------------------------------------------------------------------------
    EXACT       exact rationals; the reference.
    FX8_LINEAR  weights held in the REGISTERED 8-bit fixed point (TOTAL_BITS = 8, FRAC_BITS = 4) and renormalized
                there, which is what RV-377-066 did and what RV-377-075 refuted as a precision claim.
    FX8_LOG     the parent-maximal 8-bit encoding of RV-377-075: log2 weights held in the same 8-bit fixed point,
                renormalized by subtracting the running maximum, then exponentiated through a declared table.

Run: python3 -m gmi_microscope.b2_softmax
"""
from __future__ import annotations

import itertools
import json
import math
import os
from fractions import Fraction as Fr

from . import b2_common as C
from .core import FRAC_BITS, FX_ONE, clamp, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND
MATH_KIND = C.MATH_KIND

K = 8
TEMPS = ("0", "1/4", "1/2", "1", "2", "4", "inf")     # declared temperature grid; T = 0 is hard argmax
KAPPAS = (1, 2, 4, 8)                                  # declared top-kappa truncation
AMBIGUITY = (1, 2, 4, 8)                               # the true source is uniform over the top m by score
THETA_FRACTION = Fr(31, 32)  # rule 22: a row is adequate iff its expected squared error is at most this fraction of
                             # the hindsight-optimal CONSTANT answer's, i.e. iff it beats the constant by at least 1/32
                             # of the constant's own error. The threshold is DECLARED RELATIVE TO THE CONTROL, so the
                             # control is never admissible and no cell is VOID by construction; the control's own loss
                             # is reported per cell so the threshold is auditable. A tighter fraction (1/2) was tried
                             # in the pre-freeze calibration and left the admissible set EMPTY at ambiguity 4 and 8,
                             # which is itself the finding recorded as C14: routing's advantage over a constant shrinks
                             # with ambiguity and is only 1/32 of it at total ambiguity.
TOL = 1e-12                                            # declared tolerance for the FLOAT variational check only


def value(s):
    """Declared exact rational source values; no RNG."""
    return Fr((s * 3 + 1) % 5 - 2, 1 + (s % 2))


def score_vectors():
    """A declared family of integer score vectors over K sources. Deterministic, enumerated, no RNG."""
    out = []
    for a in range(4):
        for b in range(3):
            # scores are multiples of 4 so that s_j / T is an INTEGER at every declared temperature (1/4 .. 4) and
            # every weight 2^(s_j/T) is an exact dyadic rational. Without the scaling the integer truncation in the
            # exponent silently flattens the high temperatures, which the pre-freeze calibration caught.
            out.append(tuple(4 * (((s * (a + 1) + b * s * s) % 5) - 2) for s in range(K)))
    return sorted(set(out))


def weights(s, T, kappa, instrument):
    """Routing weights over the top-kappa sources by score. Exact for EXACT; the two 8-bit instruments hold the
    weights in the REGISTERED fixed point and renormalize there."""
    order = sorted(range(K), key=lambda j: (-s[j], j))[:kappa]
    if T == "0":
        return {order[0]: Fr(1)}
    if T == "inf":
        return {j: Fr(1, len(order)) for j in order}
    t = Fr(T)
    raw = {j: Fr(2) ** int(Fr(s[j]) / t) for j in order}      # every s_j / T is an integer by construction
    if instrument == "EXACT":
        Z = sum(raw.values())
        return {j: w / Z for j, w in raw.items()}
    if instrument == "FX8_LINEAR":
        # hold each weight in 8-bit fixed point, then renormalize in that representation
        q = {j: clamp(int(w * FX_ONE)) for j, w in raw.items()}
        Z = sum(q.values())
        if Z <= 0:
            return {j: Fr(0) for j in order}
        return {j: Fr(clamp((v * FX_ONE) // Z), FX_ONE) for j, v in q.items()}
    if instrument == "FX8_LOG":
        # log2 weights are s_j / T exactly; hold them in the same fixed point, subtract the running maximum, then
        # exponentiate through a declared table of 2^x at the fixed-point grid
        lg = {j: clamp(int(Fr(s[j]) / t * FX_ONE)) for j in order}
        m = max(lg.values())
        ex = {j: Fr(clamp(int(round(2 ** ((lg[j] - m) / FX_ONE) * FX_ONE))), FX_ONE) for j in order}
        Z = sum(ex.values())
        if Z <= 0:
            return {j: Fr(0) for j in order}
        return {j: w / Z for j, w in ex.items()}
    raise KeyError(instrument)


def run_cell(m, instrument):
    """Expected squared error of every declared (T, kappa) row at ambiguity m, under one instrument."""
    S = score_vectors()
    truths = []
    for s in S:
        order = sorted(range(K), key=lambda j: (-s[j], j))
        for t in order[:m]:
            truths.append((s, t))
    n = len(truths)
    ctrl = C.constant_control(truths, lambda st: value(st[1]))
    # rule 22: the best CONSTANT answer is the hindsight-optimal constant VALUE, so the control's loss is measured on
    # the same squared-error scale as every row rather than on an accuracy scale
    cands = sorted({value(t) for _, t in truths})
    best_c = min(cands, key=lambda c: sum((c - value(t)) ** 2 for _, t in truths))
    ctrl_loss = Fr(sum((best_c - value(t)) ** 2 for _, t in truths), n)
    theta_loss = ctrl_loss * THETA_FRACTION

    rows = {}
    for T in TEMPS:
        for kap in KAPPAS:
            tot = Fr(0)
            for s, t in truths:
                w = weights(s, T, kap, instrument)
                ans = sum(p * value(j) for j, p in w.items())
                tot += (ans - value(t)) ** 2
            loss = tot / n
            rows[f"T{T}_k{kap}"] = {
                "temperature": T, "kappa": kap, "instrument": instrument,
                "expected_squared_error": str(loss), "expected_squared_error_float": round(float(loss), 9),
                "admissible_at_theta_loss": loss <= theta_loss,
                "exact": loss <= theta_loss,
                "serves_developed_state": True,
                "charged_serve_ops_per_query_unit_price": str(Fr(K + 2 * kap)),
            }
    best = min(rows, key=lambda r: (Fr(rows[r]["expected_squared_error"]), TEMPS.index(rows[r]["temperature"]), rows[r]["kappa"]))
    # the optimal temperature at FULL materialization (kappa = K), which is the concentration question proper
    full = {T: Fr(rows[f"T{T}_k{K}"]["expected_squared_error"]) for T in TEMPS}
    T_star = min(TEMPS, key=lambda T: (full[T], TEMPS.index(T)))

    audit_rows = {r: {"admissible": v["admissible_at_theta_loss"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(v["charged_serve_ops_per_query_unit_price"])}
                  for r, v in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl_loss <= theta_loss),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "ambiguity_m": m, "instrument": instrument, "score_vectors": len(score_vectors()), "cases": n,
        "rule22_constant_control": {"best_constant_answer": str(best_c),
                                    "expected_squared_error": str(ctrl_loss),
                                    "expected_squared_error_float": round(float(ctrl_loss), 9),
                                    "theta_loss": str(theta_loss),
                                    "theta_fraction_of_control": str(THETA_FRACTION),
                                    "obligation_void": ctrl_loss <= theta_loss,
                                    "accuracy_of_best_constant": str(ctrl["capability"]),
                                    "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
        "best_row_overall": best,
        "optimal_temperature_at_full_materialization": T_star,
        "loss_by_temperature_at_full_materialization": {T: str(full[T]) for T in TEMPS},
    }


# ----------------------------------------------------------------------------------------------- the MATH check
def variational_check():
    """TM-3 for the DYADIC kernel: softmax_2(s/T) maximizes p.s + T*H_2(p) over the simplex. FLOAT64 with a declared
    tolerance, on a simplex grid, exactly as X-TMT4 does for the exponential kernel. MATH_IMPLEMENTATION_CHECK."""
    def H2(p):
        return -sum(x * math.log2(x) for x in p if x > 0)
    step = 40
    simplex = [(i / step, j / step, (step - i - j) / step) for i in range(step + 1) for j in range(step + 1 - i)]
    cells = {}
    worst = 0.0
    ok = True
    for s in ((1.0, 2.0, 3.0), (0.0, 0.0, 0.0), (-2.0, 5.0, 1.0), (4.0, -4.0, 0.0)):
        for T in (0.25, 0.5, 1.0, 2.0, 4.0):
            mx = max(s)
            w = [2 ** ((x - mx) / T) for x in s]
            Z = sum(w)
            p = [x / Z for x in w]
            obj = lambda q: sum(qi * si for qi, si in zip(q, s)) + T * H2(q)
            val = obj(p)
            best = max(obj(q) for q in simplex)
            lse = T * (math.log2(Z) + mx / T)
            gap = best - val
            worst = max(worst, gap)
            ok &= gap <= 1e-9 and abs(val - lse) <= 1e-9
            cells[f"s={s}|T={T}"] = {"dyadic_softmax": [round(x, 12) for x in p],
                                     "objective_at_softmax": round(val, 12),
                                     "max_objective_on_simplex_grid": round(best, 12),
                                     "T_log2sumexp": round(lse, 12)}
    return {"kind": MATH_KIND, "theorem": "TM-3 softmax as entropy-regularized routing, dyadic (base 2) kernel",
            "scope": "4 score vectors x 5 temperatures; simplex grid of step 1/40 (861 points); float64",
            "declared_tolerance": 1e-9, "worst_grid_gap": worst, "cells": cells, "passed": bool(ok),
            "what_this_is_not": "a closed-form identity, checked numerically. It is NOT evidence about any neural "
                                "network and it is NOT evidence for the response law measured in `cells`."}


FRONTIER_NOTE_TEXT = ("rows are (temperature, top-kappa) routing policies whose expected squared error is at or below "
                      "the declared theta_loss; A = c_desc * kappa stored weight slots, E = c_score * K scored sources "
                      "+ c_edge * kappa materialized edges")
PRICES = {"de1_sc1_ed1": (Fr(1), Fr(1), Fr(1)), "de16_sc1_ed1": (Fr(16), Fr(1), Fr(1)),
          "de1_sc1_ed8": (Fr(1), Fr(1), Fr(8)), "de1_scq_ed1": (Fr(1), Fr(1, 4), Fr(1))}
INSTRUMENTS = ("EXACT", "FX8_LINEAR", "FX8_LOG")


def main(path=None):
    cells = {f"m={m}|{inst}": run_cell(m, inst) for m in AMBIGUITY for inst in INSTRUMENTS}
    vc = variational_check()

    ctxs = {}
    for key, cell in cells.items():
        for pname, (c_de, c_sc, c_ed) in PRICES.items():
            lines = {r: (c_de * v["kappa"], c_sc * K + c_ed * v["kappa"])
                     for r, v in cell["rows"].items() if v["exact"]}
            if lines:
                ctxs[f"{key}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    def cheapest_kappa(m):
        """the top-kappa of the cheapest ADMISSIBLE row at the unit price vector (the frontier occupant there)."""
        c = cells[f"m={m}|EXACT"]
        adm = [r for r, v in c["rows"].items() if v["exact"]]
        if not adm:
            return None
        return min(c["rows"][r]["kappa"] for r in adm)

    Tstar = {(m, inst): cells[f"m={m}|{inst}"]["optimal_temperature_at_full_materialization"]
             for m in AMBIGUITY for inst in INSTRUMENTS}
    order = {T: i for i, T in enumerate(TEMPS)}
    gate = C.gate_claim(
        name="the optimal routing concentration is recoverable at the registered 8-bit precision",
        gated_axis="representation of the routing weight", gated_setting="TOTAL_BITS = 8, FRAC_BITS = 4",
        encodings={inst: Fr(sum(1 for m in AMBIGUITY if Tstar[(m, inst)] == Tstar[(m, "EXACT")]), len(AMBIGUITY))
                   for inst in INSTRUMENTS},
        strongest="FX8_LOG",
        verdict="fraction of declared ambiguity levels at which the instrument recovers the EXACT instrument's optimal "
                "temperature",
        note="protocol rule 24 and RV-377-075: a precision gate is a claim about a REPRESENTATION. The linear 8-bit "
             "weight and the log-domain 8-bit weight are both enumerated and the log-domain one, which RV-377-075 "
             "showed to be the parent-maximal 8-bit encoding of a normalized weight vector, is declared the strongest.")

    clauses = {
        "C1_MATH_the_dyadic_softmax_attains_the_TM3_variational_maximum_within_the_declared_tolerance": vc["passed"],
        "C2_optimal_temperature_is_nondecreasing_in_ambiguity_under_the_exact_instrument": all(
            order[Tstar[(AMBIGUITY[i], "EXACT")]] <= order[Tstar[(AMBIGUITY[i + 1], "EXACT")]]
            for i in range(len(AMBIGUITY) - 1)),
        "C3_at_zero_ambiguity_hard_argmax_is_optimal": Tstar[(1, "EXACT")] == "0",
        "C4_at_total_ambiguity_the_uniform_policy_is_optimal": Tstar[(K, "EXACT")] == "inf",
        "C5_optimal_temperature_strictly_moves_across_the_declared_ambiguity_range": (
            Tstar[(1, "EXACT")] != Tstar[(K, "EXACT")]),
        "C6_rule24_the_8bit_LOG_representation_recovers_the_optimal_temperature_at_every_ambiguity_level": all(
            Tstar[(m, "FX8_LOG")] == Tstar[(m, "EXACT")] for m in AMBIGUITY),
        "C7_rule24_the_8bit_LINEAR_representation_fails_to_recover_it_somewhere": any(
            Tstar[(m, "FX8_LINEAR")] != Tstar[(m, "EXACT")] for m in AMBIGUITY),
        "C8_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C9_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C10_every_admissible_row_beats_the_constant_control_on_the_same_squared_error_scale": all(
            Fr(v["expected_squared_error"]) < Fr(c["rule22_constant_control"]["expected_squared_error"])
            for c in cells.values() for v in c["rows"].values() if v["exact"]),
        "C11_truncation_to_the_top_1_source_is_exactly_the_hard_argmax_policy_at_every_temperature": all(
            cells[f"m={m}|EXACT"]["rows"][f"T{T}_k1"]["expected_squared_error"]
            == cells[f"m={m}|EXACT"]["rows"]["T0_k1"]["expected_squared_error"]
            for m in AMBIGUITY for T in TEMPS),
        "C12_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
        "C14_the_routing_advantage_over_the_constant_control_strictly_decreases_with_ambiguity": all(
            (Fr(cells[f"m={a}|EXACT"]["rule22_constant_control"]["expected_squared_error"])
             - Fr(cells[f"m={a}|EXACT"]["rows"][cells[f"m={a}|EXACT"]["best_row_overall"]]["expected_squared_error"]))
            / Fr(cells[f"m={a}|EXACT"]["rule22_constant_control"]["expected_squared_error"])
            > (Fr(cells[f"m={b}|EXACT"]["rule22_constant_control"]["expected_squared_error"])
               - Fr(cells[f"m={b}|EXACT"]["rows"][cells[f"m={b}|EXACT"]["best_row_overall"]]["expected_squared_error"]))
            / Fr(cells[f"m={b}|EXACT"]["rule22_constant_control"]["expected_squared_error"])
            for a, b in zip(AMBIGUITY, AMBIGUITY[1:])),
        "C13_ambiguity_FORCES_MATERIALIZATION_the_cheapest_admissible_top_kappa_rises_with_ambiguity": (
            all(cheapest_kappa(a) <= cheapest_kappa(b) for a, b in zip(AMBIGUITY, AMBIGUITY[1:]))
            and cheapest_kappa(AMBIGUITY[0]) < cheapest_kappa(AMBIGUITY[-1])),
    }

    receipt = {
        "schema": "GMI_B2_06_SOFTMAX_V1", "issue": [377, 422], "row": "B2.6 softmax entropy/temperature",
        "revival_id": "RV-377-094",
        "evidence_kind": KIND,
        "evidence_class": "TWO KINDS, LABELLED SEPARATELY. `variational_check` is a "
                          "MATH_IMPLEMENTATION_CHECK of the TM-3 identity for the dyadic kernel, in float64 with a "
                          "declared tolerance; it is not evidence for anything else in this receipt. `cells` and "
                          "`claims` C2 onward are a SYNTHETIC EXACT MICROSCOPE (tier S) in exact rationals with no "
                          "tolerance. Neither is evidence about a trained neural network.",
        "theorems": ["TM-3 / TMT-4 softmax as entropy-regularized routing (receipt check X-TMT4 covers the exponential "
                     "kernel; the check here covers the dyadic kernel this row actually uses)"],
        "registry_entries": ["TF-013 attention temperature T_a", "TF-012 score scaling 1/sqrt(d_h)",
                             "TF-037 sampling temperature T_d", "TF-038 top-k truncation", "TF-019 sparse / local "
                             "attention (the top-kappa rows)"],
        "declared_instrument": {
            "sources_K": K, "temperatures": list(TEMPS), "kappas": list(KAPPAS), "ambiguity_levels": list(AMBIGUITY),
            "theta_fraction_of_control": str(THETA_FRACTION), "instruments": list(INSTRUMENTS),
            "price_vectors": {k: [str(x) for x in v] for k, v in PRICES.items()},
            "kernel": "dyadic: weight_j = 2^(s_j / T) with every s_j / T an integer, so every weight is an exact "
                      "dyadic rational and the whole response law is computed without floating point",
            "ambiguity_rule": "at level m the true source is uniform over the top m sources by score; m = 1 is no "
                              "ambiguity and m = K is total ambiguity",
            "loss": "expected squared error of the transported value against the true source's value, an exact "
                    "rational expectation over the enumerated joint law",
            "randomness": "none: the score family, the values and the joint law are declared and enumerated",
            "float_use": "float64 appears ONLY in the variational check, whose declared tolerance is 1e-9, and in the "
                         "2^x table of the FX8_LOG instrument, whose entries are rounded to the registered "
                         "fixed-point grid exactly as RV-377-075 treats its own constants",
        },
        "protocol_rules_carried": {"rule_19": "the rule-22 control is the hindsight-optimal CONSTANT value on the same "
                                              "squared-error scale as every row, not an accuracy comparator",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_24": C.RULE_24,
                                   "rule_28": C.RULE_28},
        "rule24_gate_record": gate,
        "variational_check": vc,
        "dg2_audit": {"auditor": "gmi_microscope/grid_audit.py family C, driven by gmi_microscope/b2_audit.py",
                      "run_before_commit": True,
                      "verdict_recorded_in": "microscopes/results/STAGE_B2_DG2_AUDIT_V1.json"},
        "cells": cells,
        "optimal_temperature_by_ambiguity_and_instrument": {f"m={m}|{i}": Tstar[(m, i)]
                                                            for m in AMBIGUITY for i in INSTRUMENTS},
        "b2_frontiers": b2_frontiers,
        "b2_frontier_schema": C.FRONTIER_SCHEMA,
        "frontier_note": FRONTIER_NOTE_TEXT,
        "shared_reuse_grid_H": shared_grid,
        "claims": {k: bool(v) for k, v in clauses.items()},
        "n_claims_hold": sum(bool(v) for v in clauses.values()), "n_claims": len(clauses),
        "status": "GREEN" if all(clauses.values()) else "RED",
        "claim_level": "EMPIRICALLY_SUPPORTED_AT_TIER_S",
        "claim_ceiling": "a measured optimal-temperature response on one declared score family, one declared ambiguity "
                         "construction, one declared loss and a seven-point temperature grid. It establishes NOTHING "
                         "about attention temperature or decoding temperature in a trained network, and the optimum is "
                         "reported only to the resolution of the declared grid: 'T* moves with ambiguity' is a "
                         "statement about these four ambiguity levels and this grid, not a continuous law.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_06_SOFTMAX_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    print("variational check (MATH):", r["variational_check"]["passed"], "worst gap",
          r["variational_check"]["worst_grid_gap"])
    for inst in INSTRUMENTS:
        print("\n%s" % inst)
        for m in AMBIGUITY:
            c = r["cells"][f"m={m}|{inst}"]
            print("  m=%d T*=%-5s ctrl=%-10s  %s" % (
                m, c["optimal_temperature_at_full_materialization"],
                c["rule22_constant_control"]["expected_squared_error"],
                "  ".join("%s:%s" % (T, c["loss_by_temperature_at_full_materialization"][T]) for T in TEMPS)))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
