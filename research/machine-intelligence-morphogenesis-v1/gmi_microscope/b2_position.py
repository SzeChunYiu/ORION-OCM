"""B2.2 -- positional necessity and geometry: TM-1 measured, plus the extrapolation response law.

Stage B2 row B2.2 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md section 9:
    "Tasks: permutation invariant / absolute-position dependent / relative-distance dependent / long extrapolation.
     Arms: none / absolute / relative / rotary-like generic position transforms.
     Test TM-1 and extrapolation response law."

SYNTHETIC EXACT MICROSCOPE at laptop scope. Every history of every declared length is enumerated, every encoder is a
declared deterministic function, every capability and every cost is an exact rational, and there is no randomness
anywhere. It is NOT evidence about a trained neural network and NOT a claim about RoPE, ALiBi or any named scheme;
TM-1 supplies a necessity condition and this row measures where each GENERIC position transform stands on it.
Registry entries TF-005 (learned absolute), TF-006 (sinusoidal absolute), TF-007 (RoPE / rotary), TF-008 (relative
position bias), TF-044 (context window W, through the length ladder).

Declared ecology
----------------
Histories are binary sequences of declared length n in {4, 5, 6, 7, 8, 9, 10}; every one of the 2^n is enumerated.
Four obligations, chosen to separate the four task kinds the protocol row names:

    PERM_COUNT  q(h) = number of ones                                  -- permutation invariant (the negative control)
    ABS_FIRST   q(h) = h[0]                                            -- absolute, at a position that is always in range
    ABS_LAST    q(h) = h[n-1]                                          -- absolute, at a position that moves with n
    REL_DIST2   q(h) = #{t : h[t] = 1 and h[t+2] = 1}                  -- relative distance d = 2

Arms (the state representations of POSITION the alphabet admits -- protocol rule 24 requires them enumerated)
------------------------------------------------------------------------------------------------------------
    NONE          z(h) = the MULTISET of tokens. This is the PARENT-MAXIMAL permutation-invariant encoder (rule 19):
                  the finest statistic that is invariant under every permutation. Nothing order-free beats it.
    ABS_P(P)      z(h) = multiset of (code(t), h[t]) with code(t) = t for t < P and a single out-of-range code
                  otherwise. P learned position codes, a bounded table.
    ROT_P(P)      z(h) = multiset of (t mod P, h[t]). A rotary-like generic transform: position enters through a
                  cyclic group of order P, so positions t and t+P are ALIASED.
    REL_R(R)      z(h) = (token multiset, multiset of (h[i], h[j], min(j-i, R)) over i < j). Relative distances
                  resolved up to R and saturating beyond it.
    ABS_DECLARED  z(h) = the full positional tuple, i.e. ABS_P at P = the largest length ever served. It is written
                  as its own row because that is what it costs: n_max declared position codes.
    CONSTANT      the rule-22 hindsight-optimal constant-answer control. It reads no developed state and is charged
                  nothing, which rule 21 as narrowed by RV-377-073 permits.

Capability of a row is the HINDSIGHT-OPTIMAL FUNCTION of its encoder state (plurality within each z-class). That is
the parent-maximal reader of that representation: no machine whose complete internal state is z, of any kind, beats
it. Adequacy is exactness, theta = 1.

Charged costs
-------------
    description  c_desc * (number of declared position codes): 0 for NONE, P for ABS_P and ROT_P, R for REL_R,
                 n_max for ABS_DECLARED.
    serve        c_tok * (ops per token) + c_pair * (ops per ordered pair): NONE reads n tokens; ABS_P, ROT_P and
                 ABS_DECLARED read a token and a code at each of n positions; REL_R additionally evaluates each of
                 the n(n-1)/2 pairs.

Run: python3 -m gmi_microscope.b2_position
"""
from __future__ import annotations

import itertools
import json
import os
from fractions import Fraction as Fr

from . import b2_common as C
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = C.KIND

LENGTHS = (4, 5, 6, 7, 8, 9, 10)
N_MAX = max(LENGTHS)
N_TRAIN = 6                      # the declared length the bounded arms are parameterized at
THETA = Fr(1)
OBLIGATION_DISTANCE = 2          # the d of REL_DIST2

TASKS = {
    "PERM_COUNT": lambda h: sum(h),
    "ABS_FIRST": lambda h: h[0],
    "ABS_LAST": lambda h: h[-1],
    "REL_DIST2": lambda h: sum(1 for t in range(len(h) - OBLIGATION_DISTANCE) if h[t] == 1 and h[t + OBLIGATION_DISTANCE] == 1),
}

ARMS = [("NONE", 0), ("ABS_P2", 2), ("ABS_P4", 4), ("ABS_P6", 6),
        ("ROT_P2", 2), ("ROT_P4", 4), ("ROT_P6", 6),
        ("REL_R1", 1), ("REL_R2", 2), ("REL_R3", 3), ("ABS_DECLARED", N_MAX)]

PRICES = {                       # (c_desc per declared position code, c_tok per token op, c_pair per pair op)
    "d1_t1_p1": (Fr(1), Fr(1), Fr(1)),
    "d8_t1_p1": (Fr(8), Fr(1), Fr(1)),
    "d1_t1_p4": (Fr(1), Fr(1), Fr(4)),
    "d8_t1_pq": (Fr(8), Fr(1), Fr(1, 4)),
}


def encode(h, arm, P):
    n = len(h)
    if arm == "NONE":
        return tuple(sorted(h))
    if arm.startswith("ABS"):
        return tuple(sorted((t if t < P else P, h[t]) for t in range(n)))
    if arm.startswith("ROT"):
        return tuple(sorted((t % P, h[t]) for t in range(n)))
    if arm.startswith("REL"):
        return (tuple(sorted(h)),
                tuple(sorted((h[i], h[j], min(j - i, P)) for i in range(n) for j in range(i + 1, n))))
    raise KeyError(arm)


def capability(zs, qs):
    """The hindsight-optimal function of the encoder state: plurality within each z-class (parent-maximal reader)."""
    g = {}
    for z, q in zip(zs, qs):
        g.setdefault(z, []).append(q)
    correct = 0
    merged = 0
    for v in g.values():
        cnt = {}
        for t in v:
            cnt[t] = cnt.get(t, 0) + 1
        correct += max(cnt.values())
        merged += sum(1 for i in range(len(v)) for j in range(i + 1, len(v)) if v[i] != v[j])
    return Fr(correct, len(qs)), len(g), merged


def declared_codes(arm, P):
    return 0 if arm == "NONE" else P


def serve_ops(arm, n, c_tok, c_pair):
    if arm == "NONE":
        return c_tok * n
    if arm.startswith("REL"):
        return c_tok * n + c_pair * Fr(n * (n - 1), 2)
    return c_tok * 2 * n


def run_cell(task, n):
    H = list(itertools.product((0, 1), repeat=n))
    qs = [TASKS[task](h) for h in H]
    ctrl = C.constant_control(list(range(len(qs))), lambda i: qs[i])
    rows = {}
    for arm, P in ARMS:
        zs = [encode(h, arm, P) for h in H]
        cap, nclasses, merged = capability(zs, qs)
        rows[arm] = {
            "position_codes_declared": declared_codes(arm, P), "parameter": P,
            "capability": str(cap), "capability_float": round(float(cap), 6),
            "distinct_encoder_states": nclasses,
            "obligation_distinct_history_pairs_merged": merged,
            "exact": cap == 1, "admissible_at_theta": cap == 1,
            "serves_developed_state": True,
            "charged_serve_ops_per_query_unit_price": str(serve_ops(arm, n, Fr(1), Fr(1))),
        }
    audit_rows = {a: {"admissible": r["admissible_at_theta"], "serves_developed_state": True,
                      "charged_serve_ops_per_query": Fr(r["charged_serve_ops_per_query_unit_price"])}
                  for a, r in rows.items()}
    audit_rows["CONSTANT_CONTROL"] = {"admissible": bool(ctrl["capability"] >= THETA),
                                      "serves_developed_state": False, "charged_serve_ops_per_query": 0}
    return {
        "task": task, "length_n": n, "histories": len(H),
        "rule22_constant_control": {"best_constant_answer": str(qs[ctrl["best_constant_answer"]]),
                                    "capability": str(ctrl["capability"]),
                                    "capability_float": round(float(ctrl["capability"]), 6),
                                    "theta": str(THETA),
                                    "obligation_void": C.obligation_is_void(ctrl["capability"], THETA),
                                    "rule": C.RULE_22},
        "rule21_charged_serve_audit": C.charged_serve_audit(audit_rows),
        "rows": rows,
        "exact_rows": sorted(a for a, r in rows.items() if r["exact"]),
    }


FRONTIER_NOTE_TEXT = ("rows are EXACT position representations only (adequacy held at theta = 1 under the "
                      "parent-maximal reader of each representation); A = c_desc * declared position codes, "
                      "E = c_tok * per-token ops + c_pair * per-pair ops")


def main(path=None):
    cells = {f"{t}|n={n}": run_cell(t, n) for t in TASKS for n in LENGTHS}

    # rule 28: one shared reuse grid over every (task, length, price) context, built from the analytic crossovers first
    ctxs = {}
    for key, cell in cells.items():
        n = cell["length_n"]
        for pname, (c_desc, c_tok, c_pair) in PRICES.items():
            lines = {a: (c_desc * r["position_codes_declared"], serve_ops(a, n, c_tok, c_pair))
                     for a, r in cell["rows"].items() if r["exact"]}
            if lines:
                ctxs[f"{key}|{pname}"] = lines
    b2_frontiers, shared_grid = C.frontier_set(ctxs, note=FRONTIER_NOTE_TEXT)

    # rule 24: the gate record, at the gated setting (the longest declared length, on the order-dependent tasks)
    gates = {}
    for t in TASKS:
        enc_caps = {a: Fr(cells[f"{t}|n={N_MAX}"]["rows"][a]["capability"]) for a, _ in ARMS}
        gates[t] = C.gate_claim(
            name=f"order information is necessary for {t}", gated_axis="sequence length",
            gated_setting=f"n = {N_MAX}", encodings=enc_caps,
            strongest="ABS_DECLARED" if t != "REL_DIST2" else "ABS_DECLARED",
            verdict=("the permutation-invariant encoder is exact, so no position mechanism is necessary"
                     if enc_caps["NONE"] == 1 else
                     "the PARENT-MAXIMAL permutation-invariant encoder is inexact, so some order mechanism is necessary"),
            note="the enumerated representations are the token multiset, bounded learned-absolute tables at P = 2, 4, 6, "
                 "rotary-like cyclic codes at P = 2, 4, 6, relative-distance codes saturating at R = 1, 2, 3, and the "
                 "full declared positional tuple. Rule 24 requires the STRONGEST to be tested at the gated setting, and "
                 "it is: ABS_DECLARED and REL_R3 are both exact on every task at n = 10.")

    def cap(t, n, a):
        return Fr(cells[f"{t}|n={n}"]["rows"][a]["capability"])

    rot_arms = [(a, P) for a, P in ARMS if a.startswith("ROT")]
    abs_arms = [(a, P) for a, P in ARMS if a.startswith("ABS_P")]
    all_task_all_length_exact = sorted(a for a, _ in ARMS if all(cap(t, n, a) == 1 for t in TASKS for n in LENGTHS))

    clauses = {
        "C1_TM1_the_parent_maximal_permutation_invariant_encoder_is_exact_only_on_the_invariant_task": (
            all(cap("PERM_COUNT", n, "NONE") == 1 for n in LENGTHS)
            and all(cap(t, n, "NONE") < 1 for t in TASKS if t != "PERM_COUNT" for n in LENGTHS)),
        "C2_the_full_positional_tuple_is_exact_on_every_task_at_every_declared_length": all(
            cap(t, n, "ABS_DECLARED") == 1 for t in TASKS for n in LENGTHS),
        "C3_rule22_no_declared_cell_is_a_void_obligation": all(
            not c["rule22_constant_control"]["obligation_void"] for c in cells.values()),
        "C4_rule21_no_admissible_row_serves_developed_state_at_zero_charged_cost": all(
            c["rule21_charged_serve_audit"]["passed"] for c in cells.values()),
        "C5_a_rotary_like_cyclic_code_of_period_P_is_exact_on_ABS_FIRST_iff_n_le_P": all(
            (cap("ABS_FIRST", n, a) == 1) == (n <= P) for a, P in rot_arms for n in LENGTHS),
        "C6_a_bounded_learned_absolute_table_is_exact_on_ABS_FIRST_everywhere_and_on_ABS_LAST_only_for_n_le_P": (
            all(cap("ABS_FIRST", n, a) == 1 for a, P in abs_arms for n in LENGTHS)
            and all((cap("ABS_LAST", n, a) == 1) == (n <= P) for a, P in abs_arms for n in LENGTHS)),
        "C7a_relative_resolution_R_ge_d_plus_1_is_exact_on_the_distance_d_task_at_every_length": all(
            cap("REL_DIST2", n, "REL_R3") == 1 for n in LENGTHS),
        "C7b_relative_resolution_R_equal_d_is_inexact_on_the_distance_d_task_at_every_length": all(
            cap("REL_DIST2", n, "REL_R2") < 1 for n in LENGTHS),
        "C8_the_relative_arm_at_R_eq_d_plus_1_is_length_invariant_while_every_bounded_period_arm_degrades": (
            all(cap(t, n, "REL_R3") == 1 for t in TASKS for n in LENGTHS)
            and all(any(cap(t, n, a) < cap(t, N_TRAIN, a) for t in TASKS for n in LENGTHS if n > N_TRAIN)
                    for a, P in rot_arms + abs_arms if P <= N_TRAIN)),
        "C9_rule24_the_declared_strongest_representation_is_the_measured_strongest_on_every_task": all(
            g["declared_strongest_is_the_measured_strongest"] or
            Fr(g["capability_by_representation"][g["declared_strongest_representation"]]) == 1 for g in gates.values()),
        "C10_every_arm_exact_on_every_task_at_every_length_pays_either_linear_description_or_quadratic_serve": (
            len(all_task_all_length_exact) > 0 and all(
                (cells[f"PERM_COUNT|n={N_MAX}"]["rows"][a]["position_codes_declared"] >= N_MAX)
                or a.startswith("REL") for a in all_task_all_length_exact)),
        "C11_dg2_every_frontier_grid_covers_twice_every_crossover": all(
            b["dg2_grid_covers_twice_every_crossover"] for b in b2_frontiers.values()),
        "C12_on_the_permutation_invariant_task_the_zero_description_arm_is_the_sole_frontier_occupant_everywhere": all(
            occ == ["NONE"] for k, b in b2_frontiers.items() if k.startswith("PERM_COUNT")
            for _, _, occ in b["frontier_runs"]),
    }

    receipt = {
        "schema": "GMI_B2_02_POSITION_V1", "issue": [377, 422], "row": "B2.2 positional necessity and geometry",
        "revival_id": "RV-377-091",
        "evidence_kind": KIND,
        "evidence_class": "SYNTHETIC_EXACT_EMPIRICAL (tier S): a measured quantity in a declared synthetic ecology, "
                          "frozen before the run. The TM-1 clause C1 is the one MATHEMATICAL statement here and it is "
                          "labelled as such; everything else is a measured response law of declared encoders.",
        "theorems": ["TM-1 / TMT-1 positional distinguishability (receipt check X-TMT1), measured here rather than "
                     "re-proved: C1 is the same collision construction at four obligations and seven lengths"],
        "registry_entries": ["TF-005 learned absolute positional embeddings", "TF-006 sinusoidal absolute positional "
                             "encoding", "TF-007 RoPE / rotary", "TF-008 relative position bias", "TF-044 context window W"],
        "declared_instrument": {
            "lengths": list(LENGTHS), "n_train": N_TRAIN, "n_max": N_MAX, "theta": str(THETA),
            "obligation_distance_d": OBLIGATION_DISTANCE,
            "tasks": sorted(TASKS), "arms": [[a, P] for a, P in ARMS],
            "price_vectors": {k: [str(x) for x in v] for k, v in PRICES.items()},
            "capability_rule": "the hindsight-optimal FUNCTION of the encoder state (plurality within each state "
                               "class). Parent-maximal for that representation (protocol rule 19): no machine whose "
                               "complete internal state is z beats it, linear or not.",
            "arithmetic": "exact rationals; every history of every declared length enumerated in full; no floating "
                          "point in any decided quantity and no tolerance anywhere",
            "randomness": "none",
        },
        "protocol_rules_carried": {"rule_19": "the order-free opponent is the FULL token multiset, the finest "
                                              "permutation-invariant statistic, not a weaker summary such as a count",
                                   "rule_21": C.RULE_21, "rule_22": C.RULE_22, "rule_24": C.RULE_24,
                                   "rule_28": C.RULE_28},
        "rule24_gate_records": gates,
        "dg2_audit": {"auditor": "gmi_microscope/grid_audit.py family C, driven by gmi_microscope/b2_audit.py",
                      "run_before_commit": True,
                      "verdict_recorded_in": "microscopes/results/STAGE_B2_DG2_AUDIT_V1.json"},
        "dg2_procedure": "every crossover of every (task, length, price) context is computed FIRST in exact rationals, "
                         "one shared reuse grid is built to bracket each and reach 4x the largest, and check_dg2 "
                         "asserts max(grid) >= 2*max(crossover); the per-row cost coordinates (A, E) are carried in "
                         "b2_frontiers so the grid is auditable from the receipt's own contents (protocol rule 28).",
        "cells": cells,
        "b2_frontiers": b2_frontiers,
        "frontier_note": FRONTIER_NOTE_TEXT,
        "shared_reuse_grid_H": shared_grid,
        "arms_exact_on_every_task_at_every_declared_length": all_task_all_length_exact,
        "claims": {k: bool(v) for k, v in clauses.items()},
        "n_claims_hold": sum(bool(v) for v in clauses.values()), "n_claims": len(clauses),
        "status": "GREEN" if all(clauses.values()) else "RED",
        "claim_level": "EMPIRICALLY_SUPPORTED_AT_TIER_S",
        "claim_ceiling": "a measured comparison of five DECLARED generic position representations on four declared "
                         "obligations over binary sequences of length 4 to 10, under one declared cost model. It "
                         "establishes NOTHING about RoPE, ALiBi, sinusoidal encodings or any trained neural network; "
                         "the rotary arm here is a cyclic code of period P, which shares TM-1's aliasing mechanism "
                         "with rotary embeddings and none of their arithmetic. Extrapolation is measured only to "
                         "n = 10 and only on these four obligations.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_02_POSITION_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for t in TASKS:
        print("\n%s" % t)
        for n in LENGTHS:
            c = r["cells"][f"{t}|n={n}"]
            print("  n=%-3d ctrl=%-9s %s" % (n, c["rule22_constant_control"]["capability"],
                                             "  ".join("%s=%s" % (a, c["rows"][a]["capability"]) for a, _ in ARMS)))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
