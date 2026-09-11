#!/usr/bin/env python3
"""Exact calibration: factored local dynamics vs flat transition table.

This is not an intelligence result. It verifies a standard state-space-explosion
example and records why a generic compact program parent defeats any claim that
factorization alone identifies a fundamental cognitive basis.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

OUT = Path(__file__).with_name("EXACT_FACTORIZATION_SCALING_V1.json")


def factored_step(state: tuple[int, ...], inp: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a ^ b for a, b in zip(state, inp))


def program_step(state: tuple[int, ...], inp: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for i in range(len(state)):
        out.append(state[i] ^ inp[i])
    return tuple(out)


def verify_exact(n: int) -> int:
    values = list(itertools.product((0, 1), repeat=n))
    entries = 0
    for state in values:
        for inp in values:
            expected = factored_step(state, inp)
            actual = program_step(state, inp)
            if expected != actual:
                raise AssertionError((n, state, inp, expected, actual))
            entries += 1
    return entries


def build_receipt() -> dict:
    rows = []
    for n in range(1, 17):
        flat_entries = 4 ** n
        exact_verified = n <= 8
        if exact_verified:
            assert verify_exact(n) == flat_entries
        rows.append(
            {
                "n": n,
                "global_states": 2 ** n,
                "global_inputs": 2 ** n,
                "flat_transition_entries": flat_entries,
                "factored_state_bits": n,
                "factored_execution_xor_ops": n,
                "generic_program_execution_xor_ops": n,
                "exact_transition_equivalence_verified": exact_verified,
                "flat_to_factored_execution_ratio": flat_entries / n,
            }
        )
    return {
        "schema": "ExactFactorizationScalingV1",
        "family": "n independent binary state cells with n-bit external input; synchronous update s_i' = s_i XOR x_i",
        "native_factored_description": "n state cells + one shared local XOR rule + wiring/loop index",
        "flat_parent": "explicit global finite-state transducer table",
        "compact_parent": "ordinary loop/program over a bit vector",
        "rows": rows,
        "interpretation": [
            "The explicit flat transition table has 4^n state-input entries while the factored and generic-program executions use n XOR operations.",
            "Factorization can therefore create exponential succinctness relative to an explicit transition table.",
            "An ordinary compact program preserves the same O(n) execution structure, so the result does not privilege an OCM or neuron-like basis.",
            "The scientifically relevant residual is which factorization/update/search bias is acquired and favored, not whether a flat table exists."
        ],
        "terminal": "FACTORIZATION_EXPONENTIAL_VS_FLAT__GENERAL_PROGRAM_PARENT_COMPACT",
        "claim_ceiling": "exact scaling calibration; standard factorization/state-space-explosion principle; no intelligence novelty"
    }


def main() -> None:
    receipt = build_receipt()
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["terminal"])


if __name__ == "__main__":
    main()
