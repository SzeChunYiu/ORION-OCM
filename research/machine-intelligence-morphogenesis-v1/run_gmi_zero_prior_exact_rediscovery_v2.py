#!/usr/bin/env python3
import json
from pathlib import Path


def choose(costs):
    best = min(costs.values())
    winners = sorted(k for k, v in costs.items() if abs(v - best) < 1e-12)
    return winners


def main():
    cases = []

    # A. exact index vs similarity cleanup
    cases.append(("noisy_cue", {"exact_index": 111.0, "similarity_cleanup": 20.0}, ["similarity_cleanup"]))
    cases.append(("exact_cue", {"exact_index": 11.0, "similarity_cleanup": 20.0}, ["exact_index"]))

    # B. point state vs full belief
    cases.append(("confidence_sensitive", {"point_state": 101.0, "belief_state": 2.0}, ["belief_state"]))
    cases.append(("map_only", {"point_state": 1.0, "belief_state": 2.0}, ["point_state"]))

    # C. search vs compile
    cases.append(("low_reuse", {"precompiled_state": 68.0, "per_query_search": 32.0}, ["per_query_search"]))
    cases.append(("high_reuse", {"precompiled_state": 96.0, "per_query_search": 256.0}, ["precompiled_state"]))

    # D. checker-gated vs direct
    p, cg, cv, bad = 0.6, 1.0, 0.2, 10.0
    cases.append(("high_adoption_risk", {"direct": cg + (1-p)*bad, "checked": (cg+cv)/p}, ["checked"]))
    p, cv, bad = 0.99, 2.0, 0.1
    cases.append(("cheap_error_high_quality", {"direct": cg + (1-p)*bad, "checked": (cg+cv)/p}, ["direct"]))

    # E. single vs aggregate with squared-error variance + serving price
    K, lam, sigma2 = 4, 0.05, 1.0
    rho = 0.0
    cases.append(("diverse_errors", {"single": sigma2 + lam, "aggregate": sigma2*(rho+(1-rho)/K) + lam*K}, ["aggregate"]))
    rho = 1.0
    cases.append(("identical_errors", {"single": sigma2 + lam, "aggregate": sigma2*(rho+(1-rho)/K) + lam*K}, ["single"]))

    # F. reusable model/planning vs direct per-goal policy
    G = 20
    cases.append(("many_goals", {"model_plan": 10 + G, "direct_policy": 2*G}, ["model_plan"]))
    G = 2
    cases.append(("few_goals", {"model_plan": 10 + G, "direct_policy": 2*G}, ["direct_policy"]))

    # G. stable core / sparse volatile residual / full rewrite
    cases.append(("volatile_exceptions", {"core_only": 1020.0, "core_residual": 70.0, "full_rewrite": 1120.0}, ["core_residual"]))
    cases.append(("stable_core", {"core_only": 20.0, "core_residual": 25.0, "full_rewrite": 120.0}, ["core_only"]))

    results = []
    misses = 0
    for name, costs, expected in cases:
        winners = choose(costs)
        ok = winners == expected
        misses += int(not ok)
        results.append({"case": name, "costs": costs, "winner": winners, "expected": expected, "ok": ok})

    receipt = {
        "artifact": "GMI_ZERO_PRIOR_EXACT_REDISCOVERY_RECEIPT_V2",
        "status": "EXACT_HAND_REGISTERED_PROPERTY_REDISCOVERY",
        "runner": "run_gmi_zero_prior_exact_rediscovery_v2.py",
        "cells": len(cases),
        "mechanism_pairs_or_portfolios": 7,
        "misses": misses,
        "results": results,
        "claim_ceiling": "Hand-registered exact property benchmark only; not broad independent-encoding leave-one-family-out K4/K5 closure.",
        "terminal": "ZERO_PRIOR_EXACT_PROPERTY_REDISCOVERY_V2_GREEN" if misses == 0 else "ZERO_PRIOR_EXACT_PROPERTY_REDISCOVERY_V2_RED"
    }
    out = Path(__file__).with_name("GMI_ZERO_PRIOR_EXACT_REDISCOVERY_RECEIPT_V2.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if misses:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
