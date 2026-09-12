"""B2.8 -- residual connection: signal propagation vs depth in the registered 8-bit universe.

Stage B2 row B2.8 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Vary depth and perturbation magnitude. Measure Jacobian/signal propagation, optimization success and protected
     outcome. Negative control: shallow regime where skip path should add little."

WHAT THIS ROW EXECUTES AND WHAT IT DOES NOT. It executes the depth axis, the perturbation axis, forward signal
propagation, the measured response to an input perturbation, and the protected outcome, all in the REGISTERED 8-bit
fixed-point universe with every input enumerated. It does NOT execute "optimization success": no learning is run
anywhere in this lane's B2 rows, so that half of the protocol row is declared OPEN and is recorded as such in the
receipt. Nothing here is evidence about a trained neural network, and in particular nothing here bears on the
GRADIENT-TRANSPORT argument for residual connections, which is the argument the parent literature actually makes.
Registry entries TF-026 (residual connection), TF-027 (residual stream), TF-031 (epsilon constants and clipping).

Arms
----
    PLAIN             x <- f(x)
    RESIDUAL          x <- x + f(x)
    PLAIN_RESCALED    x <- f(x) / g, a plain path with a declared per-layer rescaling and NO skip. This is the
                      PARENT-MAXIMAL opponent required by protocol rule 19 and by rule 24's demand that a depth gate
                      enumerate the representations of the carrier's state: if scale control alone survives depth,
                      then "the skip is necessary at depth" is the wrong claim.

The sublayer is f(x) = g*x + b_l with a declared per-layer gain g (the scale-drift axis) and declared biases. A
one-dimensional state is used deliberately: it makes every claim exactly enumerable over all 256 representable
states, and it is the reason the gradient-transport argument is out of scope here.

Run: python3 -m gmi_microscope.b2_residual
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from . import b2_depth as D
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND

ARMS = ("PLAIN", "RESIDUAL", "PLAIN_RESCALED")
GAINS = (4, 8, 16, 24, 32)                    # fixed-point gains: 0.25, 0.5, 1.0, 1.5, 2.0
THETA_CAP = Fr(3, 4)                          # a row is adequate iff its capability is at least this
PRICES = {"d1_e1": (Fr(1), Fr(1)), "d8_e1": (Fr(8), Fr(1)), "d1_e8": (Fr(1), Fr(8))}
FRONTIER_NOTE_TEXT = ("rows are (arm, depth) stacks whose capability on the declared protected obligation is at least "
                      "theta = 3/4; A = c_desc * depth (declared blocks), E = c_exec * charged execution operations "
                      "per query, METERED on the registered charged machine")


def run_cell(g, delta):
    rows = {}
    for arm in ARMS:
        for L in D.DEPTHS:
            p = D.profile(L, g, arm, delta)
            cost = D.charged_cost(L, arm)
            rows[f"{arm}_L{L}"] = {
                "arm": arm, "depth": L, "gain_fx": g, "perturbation_lsb": delta,
                "distinct_states": p["distinct_states"],
                "max_response_lsb": p["max_response_lsb"],
                "saturated_fraction": str(p["saturated_fraction"]),
                "collapsed_to_one_state": p["collapsed_to_one_state"],
                "capability": str(p["capability"]), "capability_float": round(float(p["capability"]), 6),
                "exact": p["capability"] >= THETA_CAP,
                "admissible_at_theta": p["capability"] >= THETA_CAP,
                "serves_developed_state": True,
                "charged_serve_ops_per_query_unit_price": str(Fr(cost)),
            }
    ctrl = C.constant_control(D.GRID, D.obligation)
    audit_rows = {r: {"admissible": v["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(v["charged_serve_ops_per_query_unit_price"])}
                  for r, v in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA_CAP),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "gain_fx": g, "gain_value": str(Fr(g, 16)), "perturbation_lsb": delta,
        "states_enumerated": len(D.GRID), "obligation_classes": D.N_CLASSES,
        "rule22_constant_control": {"capability": str(ctrl["capability"]), "theta": str(THETA_CAP),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA_CAP),
                                    "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
    }


def main(path=None):
    cells = {f"g={g}|delta={d}": run_cell(g, d) for g in GAINS for d in D.DELTAS}

    ctxs = {}
    for key, cell in cells.items():
        for pname, (c_de, c_ex) in PRICES.items():
            lines = {r: (c_de * v["depth"], c_ex * Fr(v["charged_serve_ops_per_query_unit_price"]))
                     for r, v in cell["rows"].items() if v["exact"]}
            if lines:
                ctxs[f"{key}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    def cap(g, arm, L, d=1):
        return Fr(cells[f"g={g}|delta={d}"]["rows"][f"{arm}_L{L}"]["capability"])

    def dist(g, arm, L, d=1):
        return cells[f"g={g}|delta={d}"]["rows"][f"{arm}_L{L}"]["distinct_states"]

    Lmax = max(D.DEPTHS)
    gate = C.gate_claim(
        name="a skip path is necessary to propagate signal through depth in the registered 8-bit universe",
        gated_axis="depth", gated_setting=f"L = {Lmax}",
        encodings={arm: cap(8, arm, Lmax) for arm in ARMS},
        strongest="PLAIN_RESCALED",
        verdict="capability at the gated depth on the contractive-drift cell (gain 1/2)",
        note="protocol rule 24: a DEPTH gate must enumerate the representations of the carrier's state the alphabet "
             "admits and test the strongest at the gated setting. The three declared representations are the plain "
             "state, the state plus a skip path, and the state under per-layer scale control with no skip; the last "
             "is declared the strongest and is tested at every depth and every drift.")

    clauses = {
        "C1_negative_control_at_depth_1_and_unit_gain_the_skip_adds_almost_nothing": (
            cap(16, "PLAIN", 1) - cap(16, "RESIDUAL", 1) <= Fr(1, 128)
            and cap(16, "PLAIN", Lmax) - cap(16, "RESIDUAL", Lmax) >= Fr(1, 2)),
        "C2_in_the_contractive_regime_the_plain_path_collapses_to_one_state_and_the_residual_path_does_not": (
            cells["g=8|delta=1"]["rows"][f"PLAIN_L{Lmax}"]["collapsed_to_one_state"]
            and not cells["g=8|delta=1"]["rows"][f"RESIDUAL_L{Lmax}"]["collapsed_to_one_state"]
            and all(dist(8, "PLAIN", D.DEPTHS[i]) > dist(8, "PLAIN", D.DEPTHS[i + 1])
                    for i in range(len(D.DEPTHS) - 1))),
        "C3_rule19_the_scale_controlled_opponent_beats_the_residual_arm_at_the_deepest_setting_at_every_declared_gain": all(
            cap(g, "PLAIN_RESCALED", Lmax) > cap(g, "RESIDUAL", Lmax) for g in GAINS),
        "C4_at_unit_gain_the_skip_is_strictly_HARMFUL_at_every_declared_depth": all(
            cap(16, "RESIDUAL", L) < cap(16, "PLAIN", L) for L in D.DEPTHS),
        "C5_the_two_failure_modes_are_different_the_plain_path_underflows_and_the_residual_path_saturates": (
            Fr(cells["g=8|delta=1"]["rows"][f"PLAIN_L{Lmax}"]["saturated_fraction"]) == 0
            and Fr(cells["g=8|delta=1"]["rows"][f"RESIDUAL_L{Lmax}"]["saturated_fraction"]) > Fr(1, 2)),
        "C6_the_measured_response_to_an_input_perturbation_falls_to_zero_for_the_collapsed_plain_path": (
            cells["g=8|delta=1"]["rows"][f"PLAIN_L{Lmax}"]["max_response_lsb"] == 0
            and cells["g=8|delta=1"]["rows"][f"PLAIN_RESCALED_L{Lmax}"]["max_response_lsb"] > 0),
        "C7_the_scale_controlled_opponent_is_depth_invariant_in_the_contractive_regime": (
            len({dist(8, "PLAIN_RESCALED", L) for L in D.DEPTHS}) == 1
            and len({cap(8, "PLAIN_RESCALED", L) for L in D.DEPTHS}) == 1),
        "C8_the_skip_costs_strictly_more_charged_operations_per_layer_than_the_plain_path": all(
            Fr(cells["g=16|delta=1"]["rows"][f"RESIDUAL_L{L}"]["charged_serve_ops_per_query_unit_price"])
            > Fr(cells["g=16|delta=1"]["rows"][f"PLAIN_L{L}"]["charged_serve_ops_per_query_unit_price"])
            for L in D.DEPTHS),
        "C9_the_measured_response_is_nondecreasing_in_the_declared_perturbation_for_every_row": all(
            cells[f"g={g}|delta={D.DELTAS[i]}"]["rows"][r]["max_response_lsb"]
            <= cells[f"g={g}|delta={D.DELTAS[i + 1]}"]["rows"][r]["max_response_lsb"]
            for g in GAINS for r in cells[f"g={g}|delta=1"]["rows"] for i in range(len(D.DELTAS) - 1)),
        "C10_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C11_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C12_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
        "C13_the_residual_arm_is_NOT_the_frontier_occupant_at_the_deepest_setting_in_any_declared_cell": all(
            f"RESIDUAL_L{Lmax}" not in occ for b in b2_frontiers.values() for _, _, occ in b["frontier_runs"]),
    }

    receipt = {
        "schema": "GMI_B2_08_RESIDUAL_V1", "issue": [377, 422], "row": "B2.8 residual connection",
        "revival_id": "RV-377-096",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S) in the REGISTERED 8-bit fixed-point universe, every one "
                          "of the 256 representable states enumerated, every cost metered on the registered charged "
                          "machine. NOT neural evidence.",
        "not_executed_and_declared_open": [
            "OPTIMIZATION SUCCESS. The protocol row asks for it; no learning is run anywhere in this lane's B2 rows, "
            "so it is NOT executed here and is declared OPEN_NONBLOCKING rather than silently dropped.",
            "GRADIENT TRANSPORT. The parent argument for residual connections is that the Jacobian of y = x + f(x) "
            "contains an identity term, which helps OPTIMIZATION of a deep composition. This row measures FORWARD "
            "signal propagation in a one-dimensional quantized stack and says nothing whatever about that argument. "
            "TMT-9 / X-TMT9 already checks the Jacobian identity itself, mathematically.",
        ],
        "theorems": ["TMT-9 residual Jacobian identity (receipt check X-TMT9) -- a MATHEMATICAL check of the identity, "
                     "not invoked as evidence here"],
        "registry_entries": ["TF-026 residual connection", "TF-027 residual stream", "TF-031 epsilon constants and "
                             "value clipping"],
        "declared_instrument": {
            "universe": "gmi_microscope/core.py registered fixed point, TOTAL_BITS = 8, FRAC_BITS = 4, with saturation",
            "states_enumerated": len(D.GRID), "depths": list(D.DEPTHS), "gains_fx": list(GAINS),
            "gains_value": [str(Fr(g, 16)) for g in GAINS], "perturbations_lsb": list(D.DELTAS),
            "theta_capability": str(THETA_CAP), "arms": list(ARMS), "obligation_classes": D.N_CLASSES,
            "obligation": "which of four equal bands of the fixed-point range the INPUT lay in, read off the FINAL "
                          "state by the hindsight-optimal function of that state (parent-maximal reader, rule 19)",
            "sublayer": "f(x) = ADD(MUL(g, x), b_l) with declared per-layer biases; no randomness anywhere",
            "cost_rule": "charged execution operations METERED on gmi_microscope/core.Machine under basis B0",
        },
        "protocol_rules_carried": {"rule_19": "the opponent to the skip is the strongest scale-controlled plain path, "
                                              "not a convenient one", "rule_21": C.RULE_21, "rule_22": C.RULE_22,
                                   "rule_24": C.RULE_24, "rule_28": C.RULE_28},
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
        "claim_ceiling": "forward signal propagation of a ONE-DIMENSIONAL linear-sublayer stack in the registered "
                         "8-bit fixed point, at five declared gains, five depths and three perturbations. It "
                         "establishes NOTHING about a trained neural network, NOTHING about gradient transport, and "
                         "NOTHING about residual connections in a high-dimensional network where the skip path's "
                         "argument is about optimization rather than about forward range. What it does establish is "
                         "that in THIS universe the skip is a scale amplifier of gain 1 + g and is never the best "
                         "declared way to carry a distinction through depth.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_08_RESIDUAL_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for g in GAINS:
        print("\ngain %s" % str(Fr(g, 16)))
        for arm in ARMS:
            print("  %-15s" % arm, [(L, r["cells"][f"g={g}|delta=1"]["rows"][f"{arm}_L{L}"]["distinct_states"],
                                     r["cells"][f"g={g}|delta=1"]["rows"][f"{arm}_L{L}"]["capability"])
                                    for L in D.DEPTHS])
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
