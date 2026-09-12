#!/usr/bin/env python3
"""Exact checks for Grand GMI proof search, verification and reuse V1."""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def truth_decision_queries(n):
    # Zero-or-one valid candidate, no positive seen yet. The no-proof world
    # forces examination of every remaining candidate.
    if n == 0:
        return 0
    return 1 + truth_decision_queries(n - 1)


@lru_cache(maxsize=None)
def promised_one_identification_queries(n):
    # Exactly one candidate is promised valid. With one candidate left its
    # identity is determined without another discovery query.
    if n <= 1:
        return 0
    return 1 + promised_one_identification_queries(n - 1)


def verifier_checks():
    truth_cases = 0
    truth_exact = 0
    identification_cases = 0
    identification_exact = 0
    rows = []
    for n in range(1, 17):
        tq = truth_decision_queries(n)
        iq = promised_one_identification_queries(n)
        truth_cases += 1
        truth_exact += tq == n
        identification_cases += 1
        identification_exact += iq == n - 1
        rows.append({
            "candidates": n,
            "truth_decision_queries": tq,
            "truth_formula": n,
            "promised_one_identification_queries": iq,
            "identification_formula": n - 1,
        })
    return {
        "truth_cases": truth_cases,
        "truth_exact": truth_exact,
        "identification_cases": identification_cases,
        "identification_exact": identification_exact,
        "rows": rows,
    }


def reuse_checks():
    cells = 0
    inequality_matches = 0
    beneficial = 0
    ties = 0
    worse = 0
    first_benefit = None
    first_tie = None
    first_worse = None

    for derive in range(1, 9):
        for reuse in range(0, 9):
            for storage in range(0, 9):
                for multiplicity in range(1, 13):
                    fresh = multiplicity * derive
                    cached = derive + storage + (multiplicity - 1) * reuse
                    direct_beneficial = cached < fresh
                    theorem_beneficial = storage < (multiplicity - 1) * (derive - reuse)
                    cells += 1
                    inequality_matches += direct_beneficial == theorem_beneficial

                    row = {
                        "derive": derive,
                        "reuse": reuse,
                        "storage": storage,
                        "multiplicity": multiplicity,
                        "fresh_cost": fresh,
                        "cached_cost": cached,
                    }
                    if cached < fresh:
                        beneficial += 1
                        if first_benefit is None:
                            first_benefit = row
                    elif cached == fresh:
                        ties += 1
                        if first_tie is None:
                            first_tie = row
                    else:
                        worse += 1
                        if first_worse is None:
                            first_worse = row

    return {
        "cells": cells,
        "inequality_matches": inequality_matches,
        "beneficial": beneficial,
        "ties": ties,
        "worse": worse,
        "first_benefit": first_benefit,
        "first_tie": first_tie,
        "first_worse": first_worse,
    }


def run():
    verifier = verifier_checks()
    reuse = reuse_checks()
    ok = (
        verifier["truth_cases"] == 16
        and verifier["truth_exact"] == 16
        and verifier["identification_cases"] == 16
        and verifier["identification_exact"] == 16
        and reuse["cells"] == 7776
        and reuse["inequality_matches"] == 7776
        and reuse["beneficial"] == 3050
        and reuse["ties"] == 284
        and reuse["worse"] == 4442
    )
    return {
        "terminal": (
            "GRAND_GMI_PROOF_SEARCH_REUSE_TRANCHE_ALL_GREEN"
            if ok else "GRAND_GMI_PROOF_SEARCH_REUSE_TRANCHE_RED"
        ),
        "all_checks_green": ok,
        "determinism": "exact-integer-no-rng",
        "verifier": verifier,
        "reuse_phase": reuse,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
