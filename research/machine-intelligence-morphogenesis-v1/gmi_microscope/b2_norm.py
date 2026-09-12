"""B2.9 -- normalization: is the conditioning MEDIATOR the predictor, or the architecture label?

Stage B2 row B2.9 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Factorial: depth x activation-scale drift x precision x batch/sequence statistics.
     Arms: none / center+scale / RMS-like / alternative matched normalizers.
     Test conditioning mediator rather than architecture label."

SYNTHETIC EXACT MICROSCOPE. Every representable state of every declared precision is enumerated; every normalizer is
a declared deterministic map; there is no randomness and no tolerance anywhere. NOT neural evidence. Registry entries
TF-028 (LayerNorm), TF-029 (RMSNorm), TF-031 (epsilon constants and clipping), TF-075 (mixed-precision training).

Precision is a declared FAMILY, not a single width
--------------------------------------------------
`Fixed(total_bits, frac_bits)` reproduces gmi_microscope/core.py's semantics exactly at (8, 4) -- saturation, the
declared MUL rounding -- and that equality is ASSERTED at import time, so the registered 8-bit universe is the
(8, 4) member of the family and the wider members are declared extensions of it, never a different arithmetic.
Protocol rule 24 requires a precision claim to enumerate the REPRESENTATIONS of the carrier's state; here they are
the three declared widths crossed with the six declared normalizers, and the strongest is tested at the gated width.

The MEDIATOR
------------
The row's claim is that capability is predicted by a CONDITIONING quantity and not by an architecture label. The
declared mediator is the number of DISTINCT FINAL STATES the stack leaves over the enumerated input grid: what a
normalizer does, in this universe, is decide how many distinctions survive the depth. Two readings are frozen
separately, a strong one (equal mediator implies equal capability, so the label carries NO information beyond it)
and a weak one (capability is monotone in the mediator), because they can come apart and it matters which survives.

Run: python3 -m gmi_microscope.b2_norm
"""
from __future__ import annotations

import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from . import bases
from .core import FRAC_BITS as CORE_FRAC
from .core import TOTAL_BITS as CORE_TOTAL
from .core import Machine, clamp, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND


class Fixed:
    """A declared fixed-point instrument. At (8, 4) it IS gmi_microscope/core.py's arithmetic; see assert below."""

    def __init__(self, total_bits, frac_bits):
        self.total, self.frac = total_bits, frac_bits
        self.one = 1 << frac_bits
        self.hi = (1 << (total_bits - 1)) - 1
        self.lo = -(1 << (total_bits - 1))

    def clamp(self, v):
        return self.hi if v > self.hi else self.lo if v < self.lo else int(v)

    def add(self, a, b):
        return self.clamp(a + b)

    def mul(self, a, b):
        return self.clamp((a * b + (1 << (self.frac - 1))) >> self.frac)

    def grid(self):
        return list(range(self.lo, self.hi + 1))


_F8 = Fixed(CORE_TOTAL, CORE_FRAC)
assert all(_F8.mul(a, b) == clamp((a * b + (1 << (CORE_FRAC - 1))) >> CORE_FRAC)
           for a in range(_F8.lo, _F8.hi + 1, 7) for b in range(_F8.lo, _F8.hi + 1, 11)), \
    "Fixed(8,4) must reproduce core.py's MUL and saturation exactly"

PRECISIONS = ((8, 4), (12, 6), (16, 8))        # (8, 4) is the REGISTERED universe
DEPTHS = (1, 2, 4, 8, 16)
DRIFTS = (Fr(1, 4), Fr(1, 2), Fr(1), Fr(2))    # activation-scale drift per layer
ARMS = ("NONE", "CENTER_SCALE_DECLARED", "RMS_DECLARED", "MAXABS_BATCH", "RMS_BATCH", "CONST_SCALE_TWIN")
BATCH_ARMS = ("MAXABS_BATCH", "RMS_BATCH")
N_CLASSES = 4
THETA = Fr(3, 4)


def bias(l):
    return ((l * 3) % 5) - 2


def obligation(x, F):
    return min(N_CLASSES - 1, (x - F.lo) * N_CLASSES // (F.hi - F.lo + 1))


def isqrt(n):
    if n <= 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x, y = y, (y + n // y) // 2
    return x


def run_layer(states, l, g, arm, F):
    """One layer applied to the WHOLE enumerated batch at once, because the batch-statistic arms need the batch."""
    f = [F.add(F.mul(int(g * F.one), x), bias(l)) for x in states]
    if arm == "NONE":
        return f
    if arm == "CENTER_SCALE_DECLARED":
        s = int(g * F.one) or F.one
        return [F.mul(F.add(v, 0), (F.one * F.one) // s) for v in f]
    if arm == "RMS_DECLARED":
        s = int(g * F.one) or F.one
        return [F.mul(v, (F.one * F.one) // s) for v in f]
    if arm == "CONST_SCALE_TWIN":
        # the negative twin: identical arithmetic, a DECLARED constant scale, no data dependence at all
        return [F.mul(v, F.one) for v in f]
    if arm == "MAXABS_BATCH":
        m = max((abs(v) for v in f), default=0) or 1
        return [F.mul(v, (F.hi * F.one) // m) for v in f]
    if arm == "RMS_BATCH":
        r = isqrt(sum(v * v for v in f) // max(1, len(f))) or 1
        return [F.mul(v, (F.one * F.one) // max(1, r)) for v in f]
    raise KeyError(arm)


def profile(L, g, arm, F):
    grid = F.grid()
    st = list(grid)
    for l in range(L):
        st = run_layer(st, l, g, arm, F)
    out = dict(zip(grid, st))
    distinct = len(set(st))
    groups = {}
    for x in grid:
        groups.setdefault(out[x], []).append(obligation(x, F))
    correct = 0
    for v in groups.values():
        cnt = {}
        for t in v:
            cnt[t] = cnt.get(t, 0) + 1
        correct += max(cnt.values())
    sat = sum(1 for x in grid if out[x] in (F.hi, F.lo))
    # the OBLIGATION-AWARE mediator: the fraction of obligation-distinct input pairs the stack does NOT merge. It is
    # the X-TMT1 / X-TMT2 quantity and it is the refinement the plain distinct-state COUNT is tested against. It is
    # computed only on grids small enough to enumerate every pair exactly (the registered 8-bit instrument).
    sep = None
    if len(grid) <= 512:
        tot = kept = 0
        for i, x in enumerate(grid):
            ox = obligation(x, F)
            for y in grid[i + 1:]:
                if ox != obligation(y, F):
                    tot += 1
                    if out[x] != out[y]:
                        kept += 1
        sep = Fr(kept, tot) if tot else Fr(1)
    return {"distinct_states": distinct, "max_abs_state": max(abs(v) for v in st),
            "obligation_distinct_pairs_kept": sep,
            "saturated_fraction": Fr(sat, len(grid)), "capability": Fr(correct, len(grid)),
            "states_enumerated": len(grid)}


def charged_cost(L, arm):
    """Metered on the registered charged machine (basis B0)."""
    M = Machine(bases.B0)
    M.phase("exec")
    before = M.L.c["exec"]
    x = 8
    for l in range(L):
        f = M.op("ADD", M.op("MUL", 16, x), bias(l))
        if arm == "NONE":
            x = f
        elif arm == "CENTER_SCALE_DECLARED":
            x = M.op("MUL", M.op("SUB", f, 0), 16)
        elif arm in ("RMS_DECLARED", "CONST_SCALE_TWIN"):
            x = M.op("MUL", f, 16)
        elif arm == "MAXABS_BATCH":
            x = M.op("MUL", f, M.op("GT", f, 0))          # the batch statistic costs one comparison per element
        else:
            x = M.op("MUL", f, M.op("MUL", f, 16))        # the RMS statistic costs one square per element
    return M.L.c["exec"] - before


FRONTIER_NOTE_TEXT = ("rows are (arm, depth) stacks whose capability is at least theta = 3/4; A = c_desc * depth, "
                      "E = c_exec * charged execution operations per query, metered on the registered charged machine")
PRICES = {"d1_e1": (Fr(1), Fr(1)), "d8_e1": (Fr(8), Fr(1)), "d1_e8": (Fr(1), Fr(8))}


def run_cell(prec, g):
    F = Fixed(*prec)
    rows = {}
    for arm in ARMS:
        for L in DEPTHS:
            p = profile(L, g, arm, F)
            rows[f"{arm}_L{L}"] = {
                "arm": arm, "depth": L, "precision_bits": list(prec), "drift": str(g),
                "uses_batch_statistic": arm in BATCH_ARMS,
                "mediator_distinct_states": p["distinct_states"],
                "mediator_obligation_distinct_pairs_kept": None if p["obligation_distinct_pairs_kept"] is None
                                                           else str(p["obligation_distinct_pairs_kept"]),
                "max_abs_state": p["max_abs_state"],
                "saturated_fraction": str(p["saturated_fraction"]),
                "capability": str(p["capability"]), "capability_float": round(float(p["capability"]), 6),
                "exact": p["capability"] >= THETA, "admissible_at_theta": p["capability"] >= THETA,
                "serves_developed_state": True,
                "charged_serve_ops_per_query_unit_price": str(Fr(charged_cost(L, arm))),
            }
    ctrl = C.constant_control(F.grid(), lambda x: obligation(x, F))
    audit_rows = {r: {"admissible": v["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(v["charged_serve_ops_per_query_unit_price"])}
                  for r, v in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "precision_bits": list(prec), "drift": str(g), "states_enumerated": len(F.grid()),
        "rule22_constant_control": {"capability": str(ctrl["capability"]), "theta": str(THETA),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                    "rule": "see protocol_rules_carried.rule_22 at the receipt's top level"},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
    }


def main(path=None):
    cells = {f"p={p[0]}.{p[1]}|g={g}": run_cell(p, g) for p in PRECISIONS for g in DRIFTS}

    ctxs = {}
    for key, cell in cells.items():
        for pname, (c_de, c_ex) in PRICES.items():
            lines = {r: (c_de * v["depth"], c_ex * Fr(v["charged_serve_ops_per_query_unit_price"]))
                     for r, v in cell["rows"].items() if v["exact"]}
            if lines:
                ctxs[f"{key}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    # the MEDIATOR test, on the registered 8-bit instrument, pooled over every drift and depth
    pooled = []
    for g in DRIFTS:
        for r, v in cells[f"p=8.4|g={g}"]["rows"].items():
            pooled.append((v["mediator_distinct_states"], Fr(v["capability"]), v["arm"]))
    by_med = {}
    for m, c, a in pooled:
        by_med.setdefault(m, set()).add(c)
    strong_ok = all(len(v) == 1 for v in by_med.values())
    violations = sorted((m, sorted(str(x) for x in v)) for m, v in by_med.items() if len(v) > 1)[:8]
    srt = sorted(pooled)
    weak_ok = all(srt[i][1] <= srt[i + 1][1] for i in range(len(srt) - 1))
    # the refined, obligation-aware mediator
    pooled2 = []
    for g in DRIFTS:
        for r, v in cells[f"p=8.4|g={g}"]["rows"].items():
            pooled2.append((Fr(v["mediator_obligation_distinct_pairs_kept"]), Fr(v["capability"]), v["arm"]))
    by_med2 = {}
    for m, c, a in pooled2:
        by_med2.setdefault(m, set()).add(c)
    srt2 = sorted(pooled2)
    refined_monotone = all(srt2[i][1] <= srt2[i + 1][1] for i in range(len(srt2) - 1))
    refined_strong = all(len(v) == 1 for v in by_med2.values())
    spread2 = max((max(v) - min(v) for v in by_med2.values()), default=Fr(0))
    # how much does the LABEL add once the mediator is known? the spread of capability within a mediator bucket
    spread = max((max(v) - min(v) for v in by_med.values()), default=Fr(0))

    Lmax = max(DEPTHS)
    gate = C.gate_claim(
        name="normalization is required to carry a distinction through depth at the registered precision",
        gated_axis="precision (total bits, fractional bits)", gated_setting="the registered (8, 4)",
        encodings={arm: Fr(cells[f"p=8.4|g={Fr(1,2)}"]["rows"][f"{arm}_L{Lmax}"]["capability"]) for arm in ARMS},
        strongest="MAXABS_BATCH",
        verdict="capability at the gated precision and the deepest setting, on the contractive-drift cell",
        note="protocol rule 24: the enumerated representations are six declared normalizers crossed with three "
             "declared widths, the registered (8, 4) and two wider ones; the strongest declared normalizer is tested "
             "at the gated width and at every drift and depth")

    def cap(p, g, arm, L):
        return Fr(cells[f"p={p[0]}.{p[1]}|g={g}"]["rows"][f"{arm}_L{L}"]["capability"])

    clauses = {
        "C1_MEDIATOR_STRONG_equal_mediator_implies_equal_capability_so_the_arm_label_adds_nothing": strong_ok,
        "C2_MEDIATOR_WEAK_capability_is_monotone_nondecreasing_in_the_mediator": weak_ok,
        "C13_MEDIATOR_REFINED_capability_is_monotone_in_the_obligation_aware_mediator": refined_monotone,
        "C14_MEDIATOR_REFINED_STRONG_equal_obligation_aware_mediator_implies_equal_capability": refined_strong,
        "C3_the_unnormalized_arm_collapses_at_depth_under_contractive_drift_at_the_registered_precision": (
            cells[f"p=8.4|g={Fr(1,2)}"]["rows"][f"NONE_L{Lmax}"]["mediator_distinct_states"] == 1),
        "C4_at_least_one_declared_normalizer_holds_capability_at_the_deepest_setting_at_every_declared_drift": all(
            any(cap((8, 4), g, arm, Lmax) >= THETA for arm in ARMS if arm != "NONE") for g in DRIFTS),
        "C5_the_negative_twin_with_a_data_independent_scale_is_exactly_the_unnormalized_arm_at_unit_drift": all(
            cap(p, Fr(1), "CONST_SCALE_TWIN", L) == cap(p, Fr(1), "NONE", L) for p in PRECISIONS for L in DEPTHS),
        "C6_the_negative_twin_differs_from_the_batch_normalizers_wherever_the_drift_is_not_unity": any(
            cap((8, 4), g, "CONST_SCALE_TWIN", Lmax) != cap((8, 4), g, "MAXABS_BATCH", Lmax)
            for g in DRIFTS if g != 1),
        "C7_widening_the_precision_never_lowers_the_capability_of_any_arm_at_any_depth_or_drift": all(
            cap(PRECISIONS[i], g, arm, L) <= cap(PRECISIONS[i + 1], g, arm, L)
            for i in range(len(PRECISIONS) - 1) for g in DRIFTS for arm in ARMS for L in DEPTHS),
        "C8_precision_alone_does_not_rescue_the_unnormalized_arm_under_contractive_drift": all(
            cap(p, Fr(1, 2), "NONE", Lmax) < THETA for p in PRECISIONS),
        "C9_a_batch_estimated_scale_costs_strictly_more_charged_operations_than_a_declared_one": all(
            Fr(cells["p=8.4|g=1"]["rows"][f"MAXABS_BATCH_L{L}"]["charged_serve_ops_per_query_unit_price"])
            > Fr(cells["p=8.4|g=1"]["rows"][f"RMS_DECLARED_L{L}"]["charged_serve_ops_per_query_unit_price"])
            for L in DEPTHS),
        "C10_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C11_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C12_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
    }

    receipt = {
        "schema": "GMI_B2_09_NORM_V1", "issue": [377, 422], "row": "B2.9 normalization",
        "revival_id": "RV-377-097",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S). The registered 8-bit universe is the (8, 4) member of "
                          "a declared fixed-point family whose equality with gmi_microscope/core.py's arithmetic is "
                          "ASSERTED at import. NOT neural evidence.",
        "theorems": [],
        "registry_entries": ["TF-028 LayerNorm", "TF-029 RMSNorm", "TF-031 epsilon constants and value clipping",
                             "TF-075 mixed-precision training"],
        "declared_instrument": {
            "precisions": [list(p) for p in PRECISIONS], "registered_precision": [CORE_TOTAL, CORE_FRAC],
            "depths": list(DEPTHS), "drifts": [str(g) for g in DRIFTS], "arms": list(ARMS),
            "batch_statistic_arms": list(BATCH_ARMS), "theta": str(THETA), "obligation_classes": N_CLASSES,
            "mediator": "the number of DISTINCT FINAL STATES the stack leaves over the enumerated input grid",
            "batch_axis": "the 'batch/sequence statistics' axis of the protocol row is the distinction between a "
                          "DECLARED scale and one ESTIMATED from the whole enumerated batch at each layer; the "
                          "negative twin CONST_SCALE_TWIN holds the arithmetic and removes the data dependence",
            "capability_rule": "the hindsight-optimal function of the final state (parent-maximal reader, rule 19)",
            "cost_rule": "charged execution operations METERED on gmi_microscope/core.Machine under basis B0",
            "randomness": "none",
        },
        "protocol_rules_carried": {"rule_19": C.RULE_24.split(";")[0], "rule_21": C.RULE_21, "rule_22": C.RULE_22,
                                   "rule_24": C.RULE_24, "rule_28": C.RULE_28},
        "rule24_gate_record": gate,
        "mediator_test": {
            "pooled_rows": len(pooled), "instrument": "the registered (8, 4)",
            "distinct_mediator_values": len(by_med),
            "strong_reading_holds": strong_ok,
            "weak_reading_holds": weak_ok,
            "largest_capability_spread_within_one_mediator_value": str(spread),
            "mediator_values_carrying_more_than_one_capability": violations,
            "refined_mediator": "the fraction of obligation-distinct input pairs the stack does NOT merge",
            "refined_monotone_holds": refined_monotone,
            "refined_strong_holds": refined_strong,
            "largest_capability_spread_within_one_refined_mediator_value": str(spread2),
            "distinct_refined_mediator_values": len(by_med2),
            "reading": "the STRONG reading is that the architecture label carries no information once the mediator is "
                       "known; the WEAK reading is only that capability is monotone in it. They can come apart and "
                       "the receipt records which survives.",
        },
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
        "claim_ceiling": "a measured conditioning law for six declared normalizers on a ONE-DIMENSIONAL linear-sublayer "
                         "stack, at three declared widths, four declared drifts and five depths. With one coordinate "
                         "there is no recentering to do and no batch to average over except the enumerated input grid "
                         "itself, so 'LayerNorm' and 'RMSNorm' here are GAUGE CHOICES on a scalar and are NOT the "
                         "operations of those names on a vector. It establishes nothing about a trained neural network.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_09_NORM_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for g in DRIFTS:
        print("\ndrift %s (registered 8.4)" % g)
        for arm in ARMS:
            print("  %-22s" % arm, [(L, r["cells"][f"p=8.4|g={g}"]["rows"][f"{arm}_L{L}"]["mediator_distinct_states"],
                                     r["cells"][f"p=8.4|g={g}"]["rows"][f"{arm}_L{L}"]["capability"]) for L in DEPTHS])
    print("\nmediator test:", {k: v for k, v in r["mediator_test"].items() if k != "reading"})
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
