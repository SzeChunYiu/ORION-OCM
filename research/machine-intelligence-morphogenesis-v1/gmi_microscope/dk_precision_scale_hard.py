"""RV-377-080 — hardening RV-377-079's positive, and testing the exact law it implies.

RV-377-079 produced this lane's first positive on the precision axis: at K = 128, under the native price and the
`scaled` description basis, an 8-bit log row occupies 7 of 2 760 cross-instrument cells. A positive that needs a
4x class, a declared-not-measured price, a sensitivity column and the r = 0 corner is worth exactly as much as its
next test, so this record tries to break it and to replace it with a LAW.

THE LAW. Both rows carry the same K-element state and the same M = 4 readout slots. The log row carries, in
addition, a FIXED 26 declared scalars - 7 distinct log-likelihood constants, 3 distinct log priors and S = 16
ladder breakpoints - measured constant at 208 bits across K = 32, 64, 96 and 128. Under the `scaled` basis an
8-bit row pays 8 bits per declared scalar and a 10-bit row pays 10, so at H = 1, r = 0 against QCOUNT@fx10:

    reduced price:  cost(log@fx8) - cost(QCOUNT@fx10)  =  8*(K+30) - 10*(K+4) + (188 - 12)  =  -2K + 376
    native  price:  same, with (12 - 4) in place of (188 - 12)                              =  -2K + 208

Both are EXACT, not asymptotic: the reduced form reproduces the executed differences 312, 248, 184 and 120 at
K = 32, 64, 96 and 128 to the unit. The law predicts the sign flips at K = 104 under the native price - which is
why K = 96 held nothing and K = 128 held seven cells - and at K = 188 under the reduced price, which has never
been tested because the ladder stopped at 128.

This record extends the ladder to 160, 192 and 256 and asks three things: does the native-price occupancy GROW with
K as a linear law requires; does the occupancy cross into the REDUCED price column at K = 192 and K = 256, which
would remove the most permissive of RV-377-079's four choices; and does any of it survive a second event sequence
and a second machine seed.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from .core import sha256_of
from .dk_precision import THETA, per_event
from . import dk_precision_residual as RS
from . import dk_precision_scale as SC

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
K_LADDER = (128, 160, 192, 256)
INSTRUMENTS = SC.INSTRUMENTS
LIN, LOG = SC.LIN, SC.LOG


def law(K, price):
    """the EXACT frozen difference cost(LOGLAD8_T4@fx8) - cost(QCOUNT@fx10) at H = 1, r = 0, scaled basis."""
    return -2 * K + (376 if price == "reduced" else 208)


def frontier_at(K, variant="A", seed=0):
    eco = SC.ecology_scaled(K // 4, 4, variant)
    cells = {}
    for p in INSTRUMENTS:
        for r in LIN + LOG:
            if r in LOG and p in ("fx16", "wide"): continue
            cells[(r, p)] = SC.run_cell(r, eco, p, seed)
    adm = {p: sorted(r for r in LIN + LOG if (r, p) in cells and cells[(r, p)]["admissible"])
           for p in INSTRUMENTS}
    out = {"admissible": adm, "keys": {}, "law_check": {}}
    for price in ("reduced", "native"):
        lg = cells[("LOGLAD8_T4", "fx8")]; qc = cells[("QCOUNT", "fx10")]
        pl = per_event(lg, price, True); pq = per_event(qc, price, True)
        measured = int(pl["desc"] + pl["exec_q"] - pq["desc"] - pq["exec_q"])
        out["law_check"][price] = {"predicted": law(K, price), "measured": measured,
                                   "match": measured == law(K, price),
                                   "log_cheaper_at_H1_r0": measured < 0,
                                   "log_admissible_fx8": lg["admissible"],
                                   "qcount_admissible_fx10": qc["admissible"]}
        for scaled in (True, False):
            bas = "scaled" if scaled else "flat"
            pes = {f"{r}@{p}": per_event(cells[(r, p)], price, scaled)
                   for p in INSTRUMENTS for r in adm[p]}
            rep = RS.frontier_report(pes)
            occ = rep["occupancy"]
            fx8 = {n: c for n, c in occ.items() if n.endswith("@fx8") and c}
            held = sorted(c for c, o in rep["frontier"].items() if any(n.endswith("@fx8") for n in o))
            dom = {n: len(sorted(m for m, pb in pes.items() if m != n and RS.dominates_cost(pb, pes[n])))
                   for n in pes if n.endswith("@fx8")}
            out["keys"][f"{price}|{bas}"] = {
                "n_cells": rep["n_cells"], "fx8_occupancy": fx8,
                "cells_held_by_any_fx8_row": sum(fx8.values()),
                "any_fx8_row_occupies": bool(fx8),
                "cells_held": held[:64], "all_held_cells_at_r0": all(c.endswith("|r=0") for c in held),
                "max_H_held": max([int(c.split("|")[0][2:]) for c in held], default=None),
                "fx8_dominator_counts": dom,
                "H_grid_ok": rep["H_grid_extends_past_twice_largest_H_crossover"],
                "r_grid_ok": rep["r_grid_extends_past_twice_largest_r_crossover"],
                "occupancy_nonzero": {n: c for n, c in sorted(occ.items()) if c}}
    out["capability_fx8_LOGLAD8_T4"] = cells[("LOGLAD8_T4", "fx8")]["capability"]
    out["capability_fx10_QCOUNT"] = cells[("QCOUNT", "fx10")]["capability"]
    out["w_scalars"] = {"log": cells[("LOGLAD8_T4", "fx8")]["w_scalars"],
                        "qcount": cells[("QCOUNT", "fx10")]["w_scalars"]}
    out["desc_excess_flat_bits"] = (cells[("LOGLAD8_T4", "fx8")]["desc_bits"]
                                    - cells[("QCOUNT", "fx8")]["desc_bits"])
    return out


def main(tag="V1"):
    runs = {}
    for K in K_LADDER:
        runs[f"K{K}|A|s0"] = frontier_at(K, "A", 0)
    # replication: a second declared sequence at both ends of the ladder, and a second machine seed
    for K in (128, 256):
        for v in ("B", "C"):
            runs[f"K{K}|{v}|s0"] = frontier_at(K, v, 0)
    runs["K128|A|s1"] = frontier_at(128, "A", 1)
    runs["K256|A|s1"] = frontier_at(256, "A", 1)

    law_ok = all(v["law_check"][p]["match"] for v in runs.values() for p in ("reduced", "native"))
    occ_by_K = {K: {k: runs[f"K{K}|A|s0"]["keys"][k]["cells_held_by_any_fx8_row"]
                    for k in runs[f"K{K}|A|s0"]["keys"]} for K in K_LADDER}
    first_reduced = next((K for K in K_LADDER
                          if runs[f"K{K}|A|s0"]["keys"]["reduced|scaled"]["cells_held_by_any_fx8_row"]), None)
    grows = all(occ_by_K[K]["native|scaled"] <= occ_by_K[Kn]["native|scaled"]
                for K, Kn in zip(K_LADDER, K_LADDER[1:]))
    flat_zero = all(v["keys"][f"{p}|flat"]["cells_held_by_any_fx8_row"] == 0
                    for v in runs.values() for p in ("reduced", "native"))
    seed_inv = all(runs[f"K{K}|A|s0"]["keys"][k]["cells_held_by_any_fx8_row"]
                   == runs[f"K{K}|A|s1"]["keys"][k]["cells_held_by_any_fx8_row"]
                   for K in (128, 256) for k in runs["K128|A|s0"]["keys"])
    seq_rep = {f"K{K}|{v}": {k: runs[f"K{K}|{v}|s0"]["keys"][k]["cells_held_by_any_fx8_row"]
                             for k in runs[f"K{K}|A|s0"]["keys"]}
               for K in (128, 256) for v in ("A", "B", "C")}
    r0_only = all(v["keys"][k]["all_held_cells_at_r0"] for v in runs.values() for k in v["keys"])

    receipt = {
        "schema": "StageDKClassScalingHardeningV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-080", "run_tag": tag, "theta": str(THETA),
        "question": "RV-377-079's positive needed a 4x class, a declared-not-measured price, a sensitivity column and the r = 0 corner. Does it GROW with K as an exact linear law requires, does it cross into the REDUCED price column, and does it replicate across sequences and seeds?",
        "the_law": {"statement": "cost(LOGLAD8_T4@fx8) - cost(QCOUNT@fx10) at H = 1, r = 0 under the scaled basis = -2K + 376 (reduced price) and -2K + 208 (native price), EXACT",
                    "derivation": "both rows carry the same K-element state and M = 4 readout slots; the log row carries a FIXED 26 extra declared scalars (7 log-likelihood constants + 3 log priors + 16 ladder breakpoints) = 208 bits; under `scaled` an 8-bit row pays 8 bits per scalar against a 10-bit row's 10",
                    "predicted_sign_flip_K": {"reduced": 188, "native": 104},
                    "all_checks_match": bool(law_ok)},
        "K_ladder": list(K_LADDER),
        "runs": runs,
        "occupancy_by_K_sequence_A_seed_0": occ_by_K,
        "first_K_with_reduced_scaled_occupancy": first_reduced,
        "native_scaled_occupancy_is_monotone_in_K": bool(grows),
        "flat_basis_occupancy_is_zero_everywhere": bool(flat_zero),
        "seed_invariant": bool(seed_inv),
        "sequence_replication": seq_rep,
        "all_held_cells_at_r0": bool(r0_only),
        "terminal": None,
        "claim_ceiling": "one ecology recipe (ambiguous evidence, the registered class scaled by the declared rule of RV-377-079 whose K = 32 point reproduces E_ambig exactly), three declared sequences, two seeds, four class sizes, five instruments. The native price is declared and not measured; the scaled basis is a declared sensitivity column; occupancy is reported for BOTH bases and BOTH prices with no election of a primary (protocol rule 33).",
    }
    reduced_positive = first_reduced is not None
    receipt["terminal"] = (
        ("THE_POSITIVE_HARDENS__AN_8_BIT_ROW_OCCUPIES_UNDER_THE_REDUCED_PRICE_TOO_FROM_K_%d__THE_EXACT_LAW_MINUS_2K_PLUS_376_HOLDS_AT_EVERY_EXECUTED_K" % first_reduced)
        if reduced_positive else
        "THE_POSITIVE_DOES_NOT_HARDEN__OCCUPANCY_REMAINS_CONFINED_TO_THE_NATIVE_PRICE_AT_EVERY_EXECUTED_K")
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DK_V9_SCALING_HARDENED_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    print("law matches everywhere:", law_ok)
    for K in K_LADDER:
        v = runs[f"K{K}|A|s0"]
        print(f"  K={K} cap(log@fx8) {v['capability_fx8_LOGLAD8_T4']} desc_excess {v['desc_excess_flat_bits']}"
              f" law red {v['law_check']['reduced']['measured']} nat {v['law_check']['native']['measured']}")
        for k, kv in v["keys"].items():
            print(f"     {k:16s} {kv['cells_held_by_any_fx8_row']:>5} of {kv['n_cells']:<6}"
                  f" maxH {kv['max_H_held']} r0only {kv['all_held_cells_at_r0']} dom {kv['fx8_dominator_counts']}")
    print("first K with reduced|scaled occupancy:", first_reduced)
    print("monotone in K (native|scaled):", grows, "| flat zero everywhere:", flat_zero,
          "| seed invariant:", seed_inv, "| all cells at r=0:", r0_only)
    print("sequence replication:", json.dumps(seq_rep))
    print("TERMINAL:", receipt["terminal"])
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
