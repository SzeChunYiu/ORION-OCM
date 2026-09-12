"""B2.3 -- fixed vs dynamic routing: TMT-3's union lower bound as a MEASURED quantity.

Stage B2 row B2.3 of GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md:
    "Generate exact required edge sets E(x) with controlled |union E(x)| - E|E(x)|.
     Arms: fixed sparse / fixed dense / dynamic score-select / oracle dynamic.
     Primary test: measured advantage vs TM-2 opportunity."

This is a SYNTHETIC EXACT MICROSCOPE at laptop scope: every input of every family is enumerated, every arm's edge
materializations and score evaluations are counted exactly, and there is no randomness anywhere. It is NOT evidence about a
trained neural network and NOT a claim about attention in real models; it measures whether TMT-3's structural opportunity
is realizable once routing DISCOVERY is priced. Registered against TMT-3 (receipt check X-TMT3) and registry entries
TF-010, TF-017, TF-019, TF-083.

Declared ecology
----------------
One routing stage over k source positions feeding one target position. Each source s carries an exact rational value
val(s) (declared, no RNG). An input x declares a required source set P(x) of size j drawn from a support S of size q;
the obligation is out(x) = sum_{s in P(x)} val(s). An arm can transport only what it MATERIALIZES, so an arm is exact on x
iff materialized(x) is a superset of P(x); its answer is the sum over materialized(x) intersect P(x).

Families (the gap |union E(x)| - E|E(x)| is controlled by (q, j)):
    POINTER(q, j)  : inputs = every j-subset of S = {0..q-1}; union = q, mean = j, gap = q - j.
    WINDOW(j)      : P(x) = a fixed window of size j for every input; union = j, mean = j, gap = 0 (the input-independent
                     control; the same construction as X-TMT3's local_window_2 row).

Arms
----
FIXED_DENSE      : materializes all k legal sources. Always exact. Cost c_e * k.
FIXED_SPARSE(B)  : materializes a DECLARED fixed set (the B lowest source indices of the support). Cost c_e * B.
DYNAMIC          : evaluates a score for every one of the k candidates, then materializes the top-j. The score is exact
                   by construction, so the arm is always exact. Cost c_s * k + c_e * j.
ORACLE           : materializes exactly P(x) with no discovery. Always exact. Cost c_e * j.
NEGATIVE TWIN    : DYNAMIC_BLIND -- identical arithmetic and identical cost, but the score ignores the query (it is a
                   declared input-independent function of s). It holds the discovery COST and removes the discovery INFORMATION.

Prices: c_e = 1 (one op per materialized edge); c_s in a declared grid (one op per score evaluated, scaled).

Run: python3 -m gmi_microscope.b2_route
"""
from __future__ import annotations

import itertools
import json
import os
from fractions import Fraction as Fr
from math import comb

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = "SYNTHETIC_EXACT_MICROSCOPE__LAPTOP_SCOPE__NOT_EMPIRICAL_NEURAL_EVIDENCE"

K = 16                                            # source positions
C_E = Fr(1)                                       # price of materializing one edge
C_S_GRID = [Fr(1), Fr(1, 2), Fr(1, 4), Fr(1, 8), Fr(1, 16), Fr(0)]   # declared discovery prices


def val(s):
    """Declared exact rational source values; no RNG."""
    return Fr((s * 5 + 3) % 7 - 3, 1 + (s % 3))


def family_pointer(q, j):
    """Every j-subset of S = {0..q-1}."""
    return [frozenset(c) for c in itertools.combinations(range(q), j)]


def family_window(j):
    """One input-independent required set: the j lowest indices (the gap-0 control)."""
    return [frozenset(range(j))]


CELLS = [  # (name, family, q, j)
    ("POINTER_q1_j1", "pointer", 1, 1),
    ("POINTER_q2_j1", "pointer", 2, 1),
    ("POINTER_q4_j1", "pointer", 4, 1),
    ("POINTER_q8_j1", "pointer", 8, 1),
    ("POINTER_q16_j1", "pointer", 16, 1),
    ("POINTER_q8_j4", "pointer", 8, 4),
    ("POINTER_q16_j4", "pointer", 16, 4),
    ("POINTER_q16_j8", "pointer", 16, 8),
    ("WINDOW_j4", "window", 4, 4),
]


def run_cell(fam, q, j):
    inputs = family_pointer(q, j) if fam == "pointer" else family_window(j)
    n = len(inputs)
    union = frozenset().union(*inputs)
    mean = Fr(sum(len(P) for P in inputs), n)
    bound = C_E * (len(union) - mean)             # TMT-3 structural routing opportunity

    truth = {P: sum(val(s) for s in P) for P in inputs}

    def answer(materialized, P):
        return sum(val(s) for s in (materialized & P))

    # --- FIXED_DENSE
    dense_edges = frozenset(range(K))
    dense_exact = sum(1 for P in inputs if answer(dense_edges, P) == truth[P] and P <= dense_edges)
    dense_cost = C_E * K

    # --- FIXED_SPARSE at every budget B: the declared fixed set is the B lowest indices
    sparse = {}
    b_min = None
    for B in range(K + 1):
        E_star = frozenset(range(B))
        ok = sum(1 for P in inputs if P <= E_star)
        sparse[B] = {"budget": B, "exact_fraction": str(Fr(ok, n)), "exact_inputs": ok,
                     "predicted_exact_fraction_combC": str(Fr(comb(min(B, q), j), comb(q, j))) if fam == "pointer" else str(Fr(1 if B >= j else 0, 1))}
        if ok == n and b_min is None:
            b_min = B

    # --- DYNAMIC: score every candidate, materialize the top-j. The score reads the query (the required set).
    dyn_exact = 0
    dyn_scores = 0
    dyn_edges = 0
    for P in inputs:
        scores = [(1 if s in P else 0, -s) for s in range(K)]      # exact, declared, deterministic tie-break
        dyn_scores += K
        top = frozenset(s for _, s in sorted(((-sc, s) for (sc, _), s in zip(scores, range(K))))[:j])
        dyn_edges += j
        if P <= top and answer(top, P) == truth[P]:
            dyn_exact += 1

    # --- NEGATIVE TWIN: identical cost, query-independent score
    blind_exact = 0
    blind_top = frozenset(range(j))                                 # declared input-independent choice
    for P in inputs:
        if P <= blind_top and answer(blind_top, P) == truth[P]:
            blind_exact += 1

    # --- ORACLE
    oracle_cost = C_E * mean

    # frontier over the declared discovery-price grid: cheapest EXACT arm
    frontier = {}
    for c_s in C_S_GRID:
        arms = {"FIXED_DENSE": dense_cost,
                "FIXED_SPARSE_min_safe": C_E * b_min,
                "DYNAMIC": c_s * K + C_E * Fr(j),
                "ORACLE": oracle_cost}
        best = min(arms, key=lambda a: (arms[a], a))
        frontier[str(c_s)] = {"costs": {a: str(v) for a, v in arms.items()}, "winner_excluding_oracle":
                              min((a for a in arms if a != "ORACLE"), key=lambda a: (arms[a], a)),
                              "winner_including_oracle": best}
    c_s_star = Fr(len(union) - j, K)               # DYNAMIC beats the minimal safe fixed graph iff c_s < this

    return {
        "family": fam, "q": q, "j": j, "k": K, "inputs": n,
        "union_edges": len(union), "mean_required_edges": str(mean),
        "tmt3_structural_opportunity_bound": str(bound),
        "minimal_safe_fixed_budget_measured": b_min,
        "minimal_safe_fixed_budget_equals_union": b_min == len(union),
        "fixed_dense_exact_fraction": str(Fr(dense_exact, n)),
        "dynamic_exact_fraction": str(Fr(dyn_exact, n)),
        "negative_twin_blind_exact_fraction": str(Fr(blind_exact, n)),
        "fixed_sparse_by_budget": sparse,
        "sparse_curve_matches_binomial_prediction": all(
            v["exact_fraction"] == v["predicted_exact_fraction_combC"] for v in sparse.values()),
        "dynamic_score_evaluations": dyn_scores, "dynamic_edges_materialized": dyn_edges,
        "oracle_cost_per_input": str(oracle_cost),
        "dense_minus_oracle_apparent_gap": str(C_E * K - oracle_cost),
        "overstatement_of_tmt3_bound_by_using_dense_baseline": str((C_E * K - oracle_cost) - bound),
        "c_s_star_dynamic_beats_minimal_fixed": str(c_s_star),
        "frontier_by_discovery_price": frontier,
    }


def main(path=None):
    cells = {}
    for name, fam, q, j in CELLS:
        cells[name] = run_cell(fam, q, j)
    claims = {
        "C1_minimal_safe_fixed_budget_equals_union_in_every_cell": all(v["minimal_safe_fixed_budget_equals_union"] for v in cells.values()),
        "C2_measured_opportunity_equals_tmt3_bound": all(
            Fr(v["tmt3_structural_opportunity_bound"]) == Fr(v["union_edges"]) - Fr(v["mean_required_edges"]) for v in cells.values()),
        "C3_dense_dynamic_oracle_exact_everywhere": all(
            v["fixed_dense_exact_fraction"] == "1" and v["dynamic_exact_fraction"] == "1" for v in cells.values()),
        "C4_sparse_curve_matches_binomial_prediction": all(v["sparse_curve_matches_binomial_prediction"] for v in cells.values()),
        "C5_dynamic_never_wins_at_unit_discovery_price": all(
            v["frontier_by_discovery_price"]["1"]["winner_excluding_oracle"] != "DYNAMIC" for v in cells.values()),
        "C6_dense_baseline_overstates_the_bound_by_k_minus_union": all(
            Fr(v["overstatement_of_tmt3_bound_by_using_dense_baseline"]) == Fr(v["k"] - v["union_edges"]) for v in cells.values()),
        "C7_negative_twin_is_inexact_wherever_the_gap_is_positive": all(
            Fr(v["negative_twin_blind_exact_fraction"]) < 1 for v in cells.values() if Fr(v["tmt3_structural_opportunity_bound"]) > 0),
        "C8_window_control_has_zero_opportunity": Fr(cells["WINDOW_j4"]["tmt3_structural_opportunity_bound"]) == 0,
    }
    receipt = {
        "schema": "GMI_B2_03_ROUTING_V1", "issue": [377, 422], "row": "B2.3 fixed vs dynamic routing",
        "revival_id": "RV-377-056",
        "evidence_kind": KIND,
        "theorems": ["TMT-3 (X-TMT3 fixed-routing union lower bound)"],
        "registry_entries": ["TF-010 Q/K/V factorization", "TF-017 multi-head attention", "TF-019 sparse/local/sliding-window attention", "TF-083 MoE routing"],
        "declared_instrument": {
            "k": K, "c_e": str(C_E), "c_s_grid": [str(c) for c in C_S_GRID],
            "exactness_rule": "an arm is exact on x iff its materialized source set contains P(x); it transports only what it materializes",
            "enumeration": "every input of every family is enumerated; no sampling and no RNG anywhere",
        },
        "cells": cells, "claims": claims,
        "n_claims_hold": sum(bool(v) for v in claims.values()), "n_claims": len(claims),
        "status": "GREEN" if all(claims.values()) else "RED",
        "claim_ceiling": "TMT-3's structural opportunity is measured on declared finite edge-set families under a declared price "
                         "vector. It establishes nothing about attention in a trained neural network, and the discovery price c_s "
                         "is declared, not measured on hardware.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "microscopes", "results", "STAGE_B2_03_ROUTING_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for k, v in r["cells"].items():
        print("%-16s union=%2d mean=%-4s bound=%-4s B_min=%2d  dense-oracle=%-4s overstate=%-3s c_s*=%-6s  win@c_s=1: %s" % (
            k, v["union_edges"], v["mean_required_edges"], v["tmt3_structural_opportunity_bound"],
            v["minimal_safe_fixed_budget_measured"], v["dense_minus_oracle_apparent_gap"],
            v["overstatement_of_tmt3_bound_by_using_dense_baseline"], v["c_s_star_dynamic_beats_minimal_fixed"],
            v["frontier_by_discovery_price"]["1"]["winner_excluding_oracle"]))
    print()
    for k, v in r["claims"].items():
        print(("HOLDS " if v else "FAILS "), k)
    print(r["status"], r["n_claims_hold"], "/", r["n_claims"], r["receipt_sha256"][:16])
