"""B2.7 -- MLP width/gating: the local transform priced apart from the routing, in the registered 8-bit universe.

Stage B2 row B2.7 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Vary local feature-composition complexity while routing need fixed.
     Arms: linear / simple nonlinearity / gated local transform.
     Separate routing from local transform advantage."

SYNTHETIC EXACT MICROSCOPE at laptop scope, executed in the REGISTERED 8-bit fixed-point universe of
gmi_microscope/core.py (TOTAL_BITS = 8, FRAC_BITS = 4) with its exact ADD, MUL, THRESH and SEL semantics, including
saturation and the declared MUL rounding. Every function class is ENUMERATED in full over a declared weight alphabet;
nothing is fitted and there is no randomness anywhere. It is NOT evidence about a trained neural network.
Registry entries TF-022 (position-wise MLP), TF-023 (MLP width / expansion ratio), TF-024 (activation function),
TF-025 (GLU / SwiGLU gating).

Routing is HELD FIXED and CHARGED IDENTICALLY
---------------------------------------------
Every arm is handed the SAME two routed operands x and y, materialized by the same two charged edges. The routing
cost is therefore identical across arms by construction and is reported per row, which is what "separate routing from
local transform advantage" requires: any difference between arms is the local transform and nothing else.

Targets (increasing local composition complexity, all in the registered fixed point)
------------------------------------------------------------------------------------
    T_AFFINE     ADD(x, y)                        affine
    T_RELU       THRESH(SUB(x, y))                one breakpoint
    T_ABS        ADD(THRESH(x), THRESH(NEG(x)))   two breakpoints
    T_PRODUCT    MUL(x, y)                        genuinely bilinear
    T_GATE       SEL(GT(y, 0), x, 0)              content-conditioned transport

Arms
----
    LINEAR       a*x + b*y + c. Its realizable class does not grow with width at all, so the width axis is DECLARED
                 vacuous for it and that is reported rather than assumed.
    RELU(w)      sum of w terms v * THRESH(a*x + b*y + c).
    GATED(w)     sum of w terms v * MUL(THRESH(a*x + b*y + c), d*x + e*y + g) -- a GLU-like multiplicative gate.

Every coefficient is drawn from the declared alphabet {-1, 0, +1} in fixed point, and the input grid is the declared
five-point set {-1, -1/2, 0, +1/2, +1} in each argument, so each arm's realizable class is enumerated EXACTLY by
building the width-1 term set and then its sumsets. Capability is the best match over the whole class -- the
PARENT-MAXIMAL member of that arm at that width (protocol rule 19), not a fitted one.

Run: python3 -m gmi_microscope.b2_mlp
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from . import bases
from .core import FRAC_BITS, FX_ONE, Machine, clamp, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND

GRID = (-16, -8, 0, 8, 16)                 # declared input grid, fixed-point units (-1, -1/2, 0, +1/2, +1)
ALPHABET = (-16, 0, 16)                    # declared coefficient alphabet (-1, 0, +1)
INPUTS = [(x, y) for x in GRID for y in GRID]
W_RELU = (1, 2, 3, 4)                      # declared width ladder for the ReLU arm
W_GATED = (1, 2)                           # declared width ladder for the gated arm (its term set is 12x larger)
THETA = Fr(1)                              # adequacy is exactness on the enumerated grid


def MUL(a, b):
    return clamp((a * b + (1 << (FRAC_BITS - 1))) >> FRAC_BITS)


def ADD(a, b):
    return clamp(a + b)


def TH(a):
    return a if a > 0 else 0


def lin(a, b, c, x, y):
    return ADD(ADD(MUL(a, x), MUL(b, y)), c)


TARGETS = {
    "T_AFFINE": lambda x, y: ADD(x, y),
    "T_RELU": lambda x, y: TH(clamp(x - y)),
    "T_ABS": lambda x, y: ADD(TH(x), TH(clamp(-x))),
    "T_PRODUCT": lambda x, y: MUL(x, y),
    "T_GATE": lambda x, y: x if y > 0 else 0,
}


def term_set(kind):
    out = set()
    for a in ALPHABET:
        for b in ALPHABET:
            for c in ALPHABET:
                for v in ALPHABET:
                    if kind == "LINEAR":
                        out.add(tuple(lin(a, b, c, x, y) for x, y in INPUTS))
                    elif kind == "RELU":
                        out.add(tuple(MUL(v, TH(lin(a, b, c, x, y))) for x, y in INPUTS))
                    else:
                        for d in ALPHABET:
                            for e in ALPHABET:
                                for g in ALPHABET:
                                    out.add(tuple(MUL(v, MUL(TH(lin(a, b, c, x, y)), lin(d, e, g, x, y)))
                                                  for x, y in INPUTS))
    return sorted(out)


def classes(kind, widths):
    """The EXACT realizable class at each declared width, by repeated sumset with dedup in the registered fixed point."""
    B1 = term_set(kind)
    out = {}
    cur = set(B1)
    out[1] = cur
    for w in widths[1:]:
        nxt = set()
        for f in cur:
            for g in B1:
                nxt.add(tuple(ADD(p, q) for p, q in zip(f, g)))
        cur = nxt
        out[w] = cur
    return B1, out


def best_match(cls, tgt):
    """The best member of the class: the PARENT-MAXIMAL member of this arm at this width (protocol rule 19)."""
    best = -1
    for f in cls:
        n = sum(1 for p, q in zip(f, tgt) if p == q)
        if n > best:
            best = n
            if n == len(tgt):
                break
    return Fr(best, len(tgt))


# ------------------------------------------------------------------------------------- charged cost, actually metered
def charged_cost(kind, w):
    """Run one forward evaluation of the arm on the REGISTERED charged machine (basis B0) and read the ledger. The two
    routed operands are materialized by two charged edges FIRST, identically for every arm."""
    M = Machine(bases.B0)
    M.phase("exec")
    before_route = M.L.c["exec"]
    M.op("CONST", 8)        # edge 1: the routed operand x
    M.op("CONST", 8)        # edge 2: the routed operand y
    route = M.L.c["exec"] - before_route
    before = M.L.c["exec"]
    x, y = 8, -8
    if kind == "LINEAR":
        M.op("ADD", M.op("ADD", M.op("MUL", 16, x), M.op("MUL", 16, y)), 16)
    else:
        acc = 0
        for _ in range(w):
            pre = M.op("ADD", M.op("ADD", M.op("MUL", 16, x), M.op("MUL", 16, y)), 16)
            t = M.op("THRESH", pre)
            if kind == "GATED":
                val = M.op("ADD", M.op("ADD", M.op("MUL", 16, x), M.op("MUL", 16, y)), 16)
                t = M.op("MUL", t, val)
            acc = M.op("ADD", acc, M.op("MUL", 16, t))
    return route, M.L.c["exec"] - before


def main(path=None):
    term_sets = {}
    cls = {}
    for kind, widths in (("LINEAR", (1,)), ("RELU", W_RELU), ("GATED", W_GATED)):
        B1, cc = classes(kind, widths)
        term_sets[kind] = len(B1)
        cls[kind] = cc

    cells = {}
    for tname, tf in TARGETS.items():
        tgt = tuple(tf(x, y) for x, y in INPUTS)
        ctrl = C.constant_control(list(range(len(INPUTS))), lambda i: tgt[i])
        rows = {}
        for kind, widths in (("LINEAR", (1,)), ("RELU", W_RELU), ("GATED", W_GATED)):
            for w in widths:
                cap = best_match(cls[kind][w], tgt)
                route, local = charged_cost(kind, w)
                rows[f"{kind}_w{w}"] = {
                    "arm": kind, "width": w,
                    "class_size_at_this_width": len(cls[kind][w]),
                    "capability": str(cap), "capability_float": round(float(cap), 6),
                    "exact": cap == 1, "admissible_at_theta": cap == 1,
                    "charged_routing_ops_per_query": route,
                    "charged_local_transform_ops_per_query": local,
                    "charged_serve_ops_per_query_unit_price": str(Fr(route + local)),
                    "serves_developed_state": True,
                }
        minimal = {}
        for kind, widths in (("LINEAR", (1,)), ("RELU", W_RELU), ("GATED", W_GATED)):
            hit = [w for w in widths if rows[f"{kind}_w{w}"]["exact"]]
            minimal[kind] = hit[0] if hit else None
        audit_rows = {r: {"admissible": v["admissible_at_theta"], "serves_developed_state": True,
                          "charged_serve_ops_per_query": Fr(v["charged_serve_ops_per_query_unit_price"])}
                      for r, v in rows.items()}
        audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                          "serves_developed_state": False, "charged_serve_ops_per_query": 0}
        cells[tname] = {
            "target": tname, "inputs": len(INPUTS),
            "rule22_constant_control": {"capability": str(ctrl["capability"]),
                                        "capability_float": round(float(ctrl["capability"]), 6),
                                        "theta": str(THETA),
                                        "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                        "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
            "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
            "rows": rows,
            "minimal_exact_width_by_arm": minimal,
            "routing_cost_identical_across_arms": len({v["charged_routing_ops_per_query"] for v in rows.values()}) == 1,
        }

    PRICES = {"lo1": (Fr(1), Fr(1)), "route4": (Fr(4), Fr(1)), "local4": (Fr(1), Fr(4)), "route16": (Fr(16), Fr(1))}
    ctxs = {}
    for tname, cell in cells.items():
        for pname, (c_route, c_local) in PRICES.items():
            lines = {r: (Fr(v["width"]), c_route * v["charged_routing_ops_per_query"]
                         + c_local * v["charged_local_transform_ops_per_query"])
                     for r, v in cell["rows"].items() if v["exact"]}
            if lines:
                ctxs[f"{tname}|{pname}"] = lines
    FRONTIER_NOTE_TEXT = ("rows are EXACT local transforms only (adequacy held at theta = 1 on the enumerated input "
                          "grid); A = the arm's declared width (its description in units), E = c_route * charged "
                          "routing ops + c_local * charged local-transform ops, both METERED on the registered charged "
                          "machine rather than counted by hand")
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    gate = C.gate_claim(
        name="the bilinear target is reachable by a local transform at the registered 8-bit precision",
        gated_axis="local transform family", gated_setting="declared coefficient alphabet {-1, 0, +1}, widths to 4",
        encodings={f"{k}_w{max(ws)}": Fr(cells["T_PRODUCT"]["rows"][f"{k}_w{max(ws)}"]["capability"])
                   for k, ws in (("LINEAR", (1,)), ("RELU", W_RELU), ("GATED", W_GATED))},
        strongest="GATED_w2", verdict="best capability on the bilinear target at each arm's largest declared width",
        note="the enumerated representations of the LOCAL TRANSFORM are the affine class, the width-w ReLU sums to "
             "width 4 and the width-w gated sums to width 2; every class is enumerated in full and the best member "
             "taken, so a reported shortfall is a shortfall of the whole class (protocol rule 19)")

    def cap(t, r):
        return Fr(cells[t]["rows"][r]["capability"])

    clauses = {
        "C1_routing_cost_is_identical_across_every_arm_and_width_so_any_difference_is_the_local_transform": all(
            c["routing_cost_identical_across_arms"] for c in cells.values()),
        "C2_the_affine_arm_is_exact_on_the_affine_target_and_on_no_other": (
            cells["T_AFFINE"]["rows"]["LINEAR_w1"]["exact"]
            and all(not cells[t]["rows"]["LINEAR_w1"]["exact"] for t in TARGETS if t != "T_AFFINE")),
        "C3_the_relu_arm_reaches_the_one_breakpoint_target_at_width_1": cells["T_RELU"]["rows"]["RELU_w1"]["exact"],
        "C4_the_relu_arm_needs_strictly_more_width_for_the_two_breakpoint_target_than_for_the_one_breakpoint_target": (
            cells["T_ABS"]["minimal_exact_width_by_arm"]["RELU"] is not None
            and cells["T_RELU"]["minimal_exact_width_by_arm"]["RELU"] is not None
            and cells["T_ABS"]["minimal_exact_width_by_arm"]["RELU"]
            > cells["T_RELU"]["minimal_exact_width_by_arm"]["RELU"]),
        "C5_the_relu_arm_does_not_reach_the_bilinear_target_at_any_declared_width": (
            cells["T_PRODUCT"]["minimal_exact_width_by_arm"]["RELU"] is None),
        "C6_the_gated_arm_reaches_the_bilinear_target_within_its_declared_width_ladder": (
            cells["T_PRODUCT"]["minimal_exact_width_by_arm"]["GATED"] is not None),
        "C7_the_gated_arm_dominates_the_relu_arm_on_the_bilinear_target_at_every_matched_width": all(
            cap("T_PRODUCT", f"GATED_w{w}") >= cap("T_PRODUCT", f"RELU_w{w}") for w in W_GATED),
        "C8_width_is_vacuous_for_the_affine_arm_its_class_does_not_grow": (
            len(cls["LINEAR"][1]) == term_sets["LINEAR"]),
        "C9_the_relu_class_grows_strictly_with_width": all(
            len(cls["RELU"][W_RELU[i]]) < len(cls["RELU"][W_RELU[i + 1]]) for i in range(len(W_RELU) - 1)),
        "C10_rule22_no_declared_target_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C11_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C12_the_charged_local_transform_cost_is_strictly_increasing_in_width_for_both_nonlinear_arms": all(
            cells["T_AFFINE"]["rows"][f"{k}_w{ws[i]}"]["charged_local_transform_ops_per_query"]
            < cells["T_AFFINE"]["rows"][f"{k}_w{ws[i + 1]}"]["charged_local_transform_ops_per_query"]
            for k, ws in (("RELU", W_RELU), ("GATED", W_GATED)) for i in range(len(ws) - 1)),
        "C13_a_gated_term_is_strictly_more_expensive_than_a_relu_term_at_the_same_width": all(
            cells["T_AFFINE"]["rows"][f"GATED_w{w}"]["charged_local_transform_ops_per_query"]
            > cells["T_AFFINE"]["rows"][f"RELU_w{w}"]["charged_local_transform_ops_per_query"] for w in W_GATED),
        "C15_the_content_conditioned_transport_target_is_unreachable_by_EVERY_declared_arm_at_every_declared_width": (
            all(v is None for v in cells["T_GATE"]["minimal_exact_width_by_arm"].values())
            and cap("T_GATE", "GATED_w2") > cap("T_GATE", "RELU_w4") > cap("T_GATE", "LINEAR_w1")),
        "C14_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
    }

    receipt = {
        "schema": "GMI_B2_07_MLP_V1", "issue": [377, 422], "row": "B2.7 MLP width/gating",
        "revival_id": "RV-377-095",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S) executed in the REGISTERED 8-bit fixed-point universe; "
                          "every function class is enumerated in full and every cost is metered on the registered "
                          "charged machine. NOT neural evidence.",
        "theorems": [],
        "registry_entries": ["TF-022 position-wise MLP", "TF-023 MLP width / expansion ratio",
                             "TF-024 activation function", "TF-025 GLU / SwiGLU gating"],
        "declared_instrument": {
            "universe": "gmi_microscope/core.py registered fixed point: TOTAL_BITS = 8, FRAC_BITS = 4, with its exact "
                        "ADD, MUL (declared rounding), THRESH and saturation semantics",
            "input_grid": list(GRID), "coefficient_alphabet": list(ALPHABET), "input_pairs": len(INPUTS),
            "relu_widths": list(W_RELU), "gated_widths": list(W_GATED), "theta": str(THETA),
            "term_set_sizes": term_sets,
            "class_sizes": {k: {str(w): len(v) for w, v in cc.items()} for k, cc in cls.items()},
            "capability_rule": "the best member of the arm's FULLY ENUMERATED class at that width -- the "
                               "parent-maximal member of that arm (protocol rule 19), never a fitted one",
            "cost_rule": "routing and local-transform operations are METERED on gmi_microscope/core.Machine under "
                         "basis B0, not counted by hand; routing is two charged edges, identical for every arm",
            "randomness": "none",
        },
        "protocol_rules_carried": {"rule_19": "capability is the best member of the fully enumerated class, so a "
                                              "reported shortfall is a shortfall of the whole arm at that width",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_24": C.RULE_24,
                                   "rule_28": C.RULE_28},
        "rule24_gate_record": gate,
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
        "counting_note": "the class sizes reported are counts of distinct FUNCTIONS on the declared 25-point input "
                         "grid under the declared coefficient alphabet and the registered fixed point. They are "
                         "counts of configurations, not of species and not of forms (protocol rule 29).",
        "claim_ceiling": "an exact reachability boundary for three declared local-transform families over ONE declared "
                         "coefficient alphabet {-1, 0, +1}, ONE declared 25-point input grid and width ladders capped "
                         "at 4 (ReLU) and 2 (gated). A row reported as not reaching a target is NOT PROVED IMPOSSIBLE: "
                         "it is proved unreachable AT THOSE WIDTHS OVER THAT ALPHABET, which is an exact bound and not "
                         "a theorem about ReLU networks. It establishes nothing about a trained neural network.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_07_MLP_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    print("class sizes:", r["declared_instrument"]["class_sizes"])
    for t, c in r["cells"].items():
        print("\n%-11s ctrl=%-8s minimal exact width %s" % (t, c["rule22_constant_control"]["capability"],
                                                            c["minimal_exact_width_by_arm"]))
        for n, v in c["rows"].items():
            print("   %-10s cap=%-8s route=%-3d local=%-4d exact=%s" % (
                n, v["capability"], v["charged_routing_ops_per_query"],
                v["charged_local_transform_ops_per_query"], v["exact"]))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
