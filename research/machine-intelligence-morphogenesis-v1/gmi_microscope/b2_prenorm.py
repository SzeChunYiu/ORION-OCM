"""B2.10 -- pre-norm vs post-norm: the identity path, exactly, and what depth does to it at 8 bits.

Stage B2 row B2.10 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Measure optimization stability vs depth and residual magnitude."

TWO KINDS OF RESULT, LABELLED SEPARATELY.

    `identity_path`  MATH_IMPLEMENTATION_CHECK: the exact end-to-end derivative of each declared stack, in EXACT
                     RATIONALS with no quantization at all. For a linear sublayer these are closed forms --
                     (1 + alpha*g/s)^L for the pre-norm stack and ((1 + alpha*g)/s)^L for the post-norm stack -- and
                     the receipt computes both and compares them. This is an identity about the composition, not
                     evidence about anything.
    `cells`          SYNTHETIC EXACT MICROSCOPE: what the REGISTERED 8-bit fixed-point universe does to the same
                     stacks, over all 256 representable states, at four declared residual magnitudes and five depths.

WHAT IS NOT EXECUTED. The protocol row asks for "optimization stability" and no learning is run anywhere in this
lane's B2 rows, so that is declared OPEN and recorded in the receipt rather than proxied by a forward quantity with
a suggestive name. The end-to-end derivative below is the composition's derivative, which is a fact about the
architecture and NOT a measurement of training behaviour. Registry entry TF-030 (pre-norm vs post-norm placement),
with TF-026, TF-028 and TF-029 as context.

Run: python3 -m gmi_microscope.b2_prenorm
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from . import bases
from .core import FRAC_BITS, FX_MAX, FX_MIN, Machine, clamp, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND
MATH_KIND = C.MATH_KIND

GRID = list(range(FX_MIN, FX_MAX + 1))
DEPTHS = (1, 2, 4, 8, 16)
ALPHAS = (Fr(1, 4), Fr(1, 2), Fr(1), Fr(2))      # residual magnitude
GAIN = Fr(1)                                      # declared sublayer gain g
SCALES = (Fr(1), Fr(2), Fr(4))                    # declared normalizer scale s
ARMS = ("PRE_NORM", "POST_NORM", "RESIDUAL_NO_NORM", "NORM_ONLY_PLAIN")
N_CLASSES = 4
THETA = Fr(3, 4)
ONE = 1 << FRAC_BITS


def MUL(a, b):
    return clamp((a * b + (1 << (FRAC_BITS - 1))) >> FRAC_BITS)


def ADD(a, b):
    return clamp(a + b)


def fxq(q):
    """A declared rational rendered on the registered fixed-point grid."""
    return clamp(int(round(float(q) * ONE)))


def bias(l):
    return ((l * 3) % 5) - 2


def obligation(x):
    return min(N_CLASSES - 1, (x - FX_MIN) * N_CLASSES // (FX_MAX - FX_MIN + 1))


# ------------------------------------------------------------------------------- the MATH part: the identity path
def identity_gain(arm, alpha, g, s, L):
    """The EXACT end-to-end derivative of the declared stack, in exact rationals, with NO quantization."""
    if arm == "PRE_NORM":
        per = 1 + alpha * g / s
    elif arm == "POST_NORM":
        per = (1 + alpha * g) / s
    elif arm == "RESIDUAL_NO_NORM":
        per = 1 + alpha * g
    elif arm == "NORM_ONLY_PLAIN":
        per = alpha * g / s
    else:
        raise KeyError(arm)
    return per ** L


def identity_path_check():
    """A closed-form comparison of the two placements, exact. MATH_IMPLEMENTATION_CHECK, not evidence."""
    cells = {}
    ok = True
    for alpha in ALPHAS:
        for s in SCALES:
            for L in DEPTHS:
                pre = identity_gain("PRE_NORM", alpha, GAIN, s, L)
                post = identity_gain("POST_NORM", alpha, GAIN, s, L)
                cells[f"alpha={alpha}|s={s}|L={L}"] = {
                    "pre_norm_end_to_end_gain": str(pre), "post_norm_end_to_end_gain": str(post),
                    "pre_ge_one": pre >= 1, "post_lt_one": post < 1,
                    "ratio_pre_over_post": str(pre / post) if post != 0 else None}
                # the identity: the pre-norm stack's per-layer derivative is 1 + alpha*g/s, which is at least 1 for
                # non-negative alpha, g and s; the post-norm stack's is (1 + alpha*g)/s and is below 1 exactly when
                # s > 1 + alpha*g
                ok &= (pre >= 1) and ((post < 1) == (s > 1 + alpha * GAIN))
    return {"kind": MATH_KIND, "statement": "for a linear sublayer the pre-norm stack's end-to-end derivative is "
                                            "(1 + alpha*g/s)^L and the post-norm stack's is ((1 + alpha*g)/s)^L; the "
                                            "first is at least 1 for non-negative alpha, g and s and the second is "
                                            "below 1 exactly when s exceeds 1 + alpha*g",
            "scope": f"{len(ALPHAS)} residual magnitudes x {len(SCALES)} normalizer scales x {len(DEPTHS)} depths, "
                     f"exact rationals, no quantization",
            "arithmetic": "exact rationals (fractions.Fraction); no floating point and no tolerance",
            "cells": cells, "passed": bool(ok),
            "what_this_is_not": "a fact about the composition of linear maps. It is NOT a measurement of optimization "
                                "behaviour, NOT evidence about a trained network, and NOT evidence for the quantized "
                                "measurements in `cells`."}


# ------------------------------------------------------------------- the EMPIRICAL part: the registered 8-bit universe
def step(x, l, arm, alpha, s):
    ga, sa = fxq(GAIN), fxq(Fr(1) / s)
    aa = fxq(alpha)
    if arm == "PRE_NORM":
        n = MUL(x, sa)
        return ADD(x, MUL(aa, ADD(MUL(ga, n), bias(l))))
    if arm == "POST_NORM":
        return MUL(ADD(x, MUL(aa, ADD(MUL(ga, x), bias(l)))), sa)
    if arm == "RESIDUAL_NO_NORM":
        return ADD(x, MUL(aa, ADD(MUL(ga, x), bias(l))))
    if arm == "NORM_ONLY_PLAIN":
        return MUL(MUL(aa, ADD(MUL(ga, x), bias(l))), sa)
    raise KeyError(arm)


def profile(arm, alpha, s, L):
    out = {}
    for x0 in GRID:
        x = x0
        for l in range(L):
            x = step(x, l, arm, alpha, s)
        out[x0] = x
    distinct = len(set(out.values()))
    groups = {}
    for x in GRID:
        groups.setdefault(out[x], []).append(obligation(x))
    correct = sum(max({t: v.count(t) for t in set(v)}.values()) for v in groups.values())
    sat = sum(1 for x in GRID if out[x] in (FX_MAX, FX_MIN))
    tot = kept = 0
    for i, x in enumerate(GRID):
        ox = obligation(x)
        for y in GRID[i + 1:]:
            if ox != obligation(y):
                tot += 1
                if out[x] != out[y]:
                    kept += 1
    return {"distinct_states": distinct, "saturated_fraction": Fr(sat, len(GRID)),
            "obligation_distinct_pairs_kept": Fr(kept, tot) if tot else Fr(1),
            "capability": Fr(correct, len(GRID))}


def charged_cost(arm, L):
    M = Machine(bases.B0)
    M.phase("exec")
    before = M.L.c["exec"]
    x = 8
    for l in range(L):
        x = step_metered(M, x, l, arm)
    return M.L.c["exec"] - before


def step_metered(M, x, l, arm):
    if arm == "PRE_NORM":
        n = M.op("MUL", x, 16)
        return M.op("ADD", x, M.op("MUL", 16, M.op("ADD", M.op("MUL", 16, n), bias(l))))
    if arm == "POST_NORM":
        return M.op("MUL", M.op("ADD", x, M.op("MUL", 16, M.op("ADD", M.op("MUL", 16, x), bias(l)))), 16)
    if arm == "RESIDUAL_NO_NORM":
        return M.op("ADD", x, M.op("MUL", 16, M.op("ADD", M.op("MUL", 16, x), bias(l))))
    return M.op("MUL", M.op("MUL", 16, M.op("ADD", M.op("MUL", 16, x), bias(l))), 16)


FRONTIER_NOTE_TEXT = ("rows are (placement, depth) stacks whose capability is at least theta = 3/4; A = c_desc * depth, "
                      "E = c_exec * charged execution operations per query, metered on the registered charged machine")
PRICES = {"d1_e1": (Fr(1), Fr(1)), "d8_e1": (Fr(8), Fr(1)), "d1_e8": (Fr(1), Fr(8))}


def run_cell(alpha, s):
    rows = {}
    for arm in ARMS:
        for L in DEPTHS:
            p = profile(arm, alpha, s, L)
            rows[f"{arm}_L{L}"] = {
                "arm": arm, "depth": L, "residual_magnitude_alpha": str(alpha), "normalizer_scale_s": str(s),
                "distinct_states": p["distinct_states"],
                "saturated_fraction": str(p["saturated_fraction"]),
                "obligation_distinct_pairs_kept": str(p["obligation_distinct_pairs_kept"]),
                "capability": str(p["capability"]), "capability_float": round(float(p["capability"]), 6),
                "exact_end_to_end_identity_gain": str(identity_gain(arm, alpha, GAIN, s, L)),
                "exact": p["capability"] >= THETA, "admissible_at_theta": p["capability"] >= THETA,
                "serves_developed_state": True,
                "charged_serve_ops_per_query_unit_price": str(Fr(charged_cost(arm, L))),
            }
    ctrl = C.constant_control(GRID, obligation)
    audit_rows = {r: {"admissible": v["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(v["charged_serve_ops_per_query_unit_price"])}
                  for r, v in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "residual_magnitude_alpha": str(alpha), "normalizer_scale_s": str(s), "states_enumerated": len(GRID),
        "rule22_constant_control": {"capability": str(ctrl["capability"]), "theta": str(THETA),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                    "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
    }


def main(path=None):
    ipc = identity_path_check()
    cells = {f"a={a}|s={s}": run_cell(a, s) for a in ALPHAS for s in SCALES}

    ctxs = {}
    for key, cell in cells.items():
        for pname, (c_de, c_ex) in PRICES.items():
            lines = {r: (c_de * v["depth"], c_ex * Fr(v["charged_serve_ops_per_query_unit_price"]))
                     for r, v in cell["rows"].items() if v["exact"]}
            if lines:
                ctxs[f"{key}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    def cap(a, s, arm, L):
        return Fr(cells[f"a={a}|s={s}"]["rows"][f"{arm}_L{L}"]["capability"])

    def med(a, s, arm, L):
        return Fr(cells[f"a={a}|s={s}"]["rows"][f"{arm}_L{L}"]["obligation_distinct_pairs_kept"])

    Lmax = max(DEPTHS)
    gate = C.gate_claim(
        name="the placement of the normalizer decides whether a distinction survives depth",
        gated_axis="depth", gated_setting=f"L = {Lmax}",
        encodings={arm: cap(Fr(1), Fr(4), arm, Lmax) for arm in ARMS},
        strongest="PRE_NORM", verdict="capability at the gated depth at unit residual magnitude and scale 4",
        note="protocol rule 24: the four enumerated representations of the carrier's state through depth are the "
             "pre-norm placement, the post-norm placement, a residual path with no normalizer and a normalized plain "
             "path with no residual. All four are run at every declared residual magnitude, scale and depth.")

    clauses = {
        "C1_MATH_the_pre_norm_end_to_end_derivative_is_at_least_one_and_the_post_norm_one_is_below_one_exactly_when_s_exceeds_1_plus_alpha_g": ipc["passed"],
        "C2_at_the_deepest_setting_and_scale_above_unity_pre_norm_capability_exceeds_post_norm_capability": all(
            cap(a, s, "PRE_NORM", Lmax) > cap(a, s, "POST_NORM", Lmax) for a in ALPHAS for s in SCALES if s > 1),
        "C3_at_unit_scale_the_two_placements_are_indistinguishable_at_every_depth_and_residual_magnitude": all(
            cap(a, Fr(1), "PRE_NORM", L) == cap(a, Fr(1), "POST_NORM", L) for a in ALPHAS for L in DEPTHS),
        "C4_the_post_norm_stack_collapses_with_depth_at_every_scale_above_unity": all(
            cells[f"a={a}|s={s}"]["rows"][f"POST_NORM_L{Lmax}"]["distinct_states"]
            < cells[f"a={a}|s={s}"]["rows"]["POST_NORM_L1"]["distinct_states"]
            for a in ALPHAS for s in SCALES if s > 1),
        "C5_the_residual_path_without_a_normalizer_saturates_at_depth_at_every_declared_residual_magnitude": all(
            Fr(cells[f"a={a}|s={Fr(1)}"]["rows"][f"RESIDUAL_NO_NORM_L{Lmax}"]["saturated_fraction"]) > Fr(1, 4)
            for a in ALPHAS),
        "C6_capability_falls_with_the_residual_magnitude_for_the_post_norm_placement_at_the_deepest_setting": all(
            cap(ALPHAS[i], s, "POST_NORM", Lmax) >= cap(ALPHAS[i + 1], s, "POST_NORM", Lmax)
            for i in range(len(ALPHAS) - 1) for s in SCALES),
        "C7_the_obligation_aware_mediator_of_RV_377_097_orders_the_two_placements_the_same_way_capability_does": all(
            (med(a, s, "PRE_NORM", Lmax) > med(a, s, "POST_NORM", Lmax))
            == (cap(a, s, "PRE_NORM", Lmax) > cap(a, s, "POST_NORM", Lmax))
            for a in ALPHAS for s in SCALES),
        "C8_the_two_placements_cost_the_same_number_of_charged_operations_at_every_depth": all(
            cells[f"a={Fr(1)}|s={Fr(1)}"]["rows"][f"PRE_NORM_L{L}"]["charged_serve_ops_per_query_unit_price"]
            == cells[f"a={Fr(1)}|s={Fr(1)}"]["rows"][f"POST_NORM_L{L}"]["charged_serve_ops_per_query_unit_price"]
            for L in DEPTHS),
        "C9_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C10_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C11_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
    }

    receipt = {
        "schema": "GMI_B2_10_PRENORM_V1", "issue": [377, 422], "row": "B2.10 pre/post norm",
        "revival_id": "RV-377-098",
        "evidence_kind": KIND,
        "evidence_class": "TWO KINDS, LABELLED SEPARATELY. `identity_path` is a MATH_IMPLEMENTATION_CHECK of a "
                          "closed-form derivative composition in exact rationals with no quantization; it is not "
                          "evidence for anything. `cells` is a SYNTHETIC EXACT MICROSCOPE in the registered 8-bit "
                          "fixed point over all 256 representable states. Neither is neural evidence.",
        "not_executed_and_declared_open": [
            "OPTIMIZATION STABILITY. The protocol row asks for it by name. No learning is run anywhere in this lane's "
            "B2 rows, so it is NOT executed and is declared OPEN_NONBLOCKING. The end-to-end derivative reported here "
            "is a property of the COMPOSITION, which is an architecture fact, and it is not a measurement of training "
            "behaviour; calling it one would be exactly the substitution this block exists to prevent.",
        ],
        "theorems": ["TMT-9 residual Jacobian identity (X-TMT9), a mathematical check, not invoked as evidence here"],
        "registry_entries": ["TF-030 pre-norm vs post-norm placement", "TF-026 residual connection",
                             "TF-028 LayerNorm", "TF-029 RMSNorm"],
        "declared_instrument": {
            "universe": "the registered fixed point, TOTAL_BITS = 8, FRAC_BITS = 4, with saturation",
            "states_enumerated": len(GRID), "depths": list(DEPTHS),
            "residual_magnitudes_alpha": [str(a) for a in ALPHAS], "normalizer_scales_s": [str(s) for s in SCALES],
            "sublayer_gain_g": str(GAIN), "arms": list(ARMS), "theta": str(THETA), "obligation_classes": N_CLASSES,
            "mediator": "the obligation-aware mediator established by RV-377-097: the fraction of obligation-distinct "
                        "input pairs the stack does not merge",
            "cost_rule": "charged execution operations METERED on gmi_microscope/core.Machine under basis B0",
            "randomness": "none",
        },
        "protocol_rules_carried": {"rule_19": "the two placements are compared against two further controls, a "
                                              "residual path with no normalizer and a normalized plain path with no "
                                              "residual, so neither placement is compared only to the other",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_24": C.RULE_24,
                                   "rule_28": C.RULE_28},
        "rule24_gate_record": gate,
        "identity_path": ipc,
        "dg2_audit": {"auditor": "gmi_microscope/grid_audit.py family C, driven by gmi_microscope/b2_audit.py",
                      "run_before_commit": True,
                      "verdict_recorded_in": "microscopes/results/STAGE_B2_DG2_AUDIT_V1.json"},
        "cells": cells,
        "b2_frontiers": b2_frontiers,
        "b2_frontier_schema": C.FRONTIER_SCHEMA,
        "frontier_note": FRONTIER_NOTE_TEXT,
        "shared_reuse_grid_H": shared_grid,
        "claims": {k: bool(v) for k, v in clauses.items()},
        "n_claims_hold": sum(bool(v) for v in clauses.values()), "n_claims": len(clauses),
        "status": "GREEN" if all(clauses.values()) else "RED",
        "claim_level": "EMPIRICALLY_SUPPORTED_AT_TIER_S",
        "claim_ceiling": "an exact derivative composition plus a quantized forward measurement, both on a "
                         "ONE-DIMENSIONAL LINEAR-sublayer stack with a declared constant normalizer scale. It "
                         "establishes NOTHING about optimization stability, NOTHING about a trained neural network, "
                         "and nothing about pre-norm or post-norm transformers, whose normalizer scale is estimated "
                         "from a vector of activations and moves during training. What it establishes is that the two "
                         "placements differ only through the scale they apply to the identity contribution, and that "
                         "the difference is exactly zero when that scale is unity.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_10_PRENORM_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    print("identity path (MATH):", r["identity_path"]["passed"])
    for s in SCALES:
        print("\nscale s=%s" % s)
        for arm in ARMS:
            print("  %-18s" % arm, [(str(a), r["cells"][f"a={a}|s={s}"]["rows"][f"{arm}_L16"]["capability"])
                                    for a in ALPHAS])
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
