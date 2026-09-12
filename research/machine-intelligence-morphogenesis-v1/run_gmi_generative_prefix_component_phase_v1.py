#!/usr/bin/env python3
import json
from pathlib import Path


def trie_edges(strings, L):
    prefixes = set()
    for s in strings:
        for ell in range(1, L + 1):
            prefixes.add(s[:ell])
    return len(prefixes)


def main():
    L = 4
    strings = [format(i, f"0{L}b") for i in range(2 ** L)]
    horizons = [0, 1, 2, 4, 8]
    target_sets = 0
    phase_cells = 0
    violations = 0
    phase_counts = {str(r): {"prefix": 0, "component": 0, "tie": 0} for r in horizons}
    zero_saving_targets = 0

    for mask in range(1, 1 << len(strings)):
        S = [strings[i] for i in range(len(strings)) if (mask >> i) & 1]
        K = len(S)
        E = trie_edges(S, L)
        saving = K * L - E
        if saving < 0:
            violations += 1
        if saving == 0:
            zero_saving_targets += 1
        for R in horizons:
            component = K * L + R
            prefix = E + R * L
            predicted = saving > R * (L - 1)
            actual = prefix < component
            if predicted != actual:
                violations += 1
            if prefix < component:
                phase_counts[str(R)]["prefix"] += 1
            elif component < prefix:
                phase_counts[str(R)]["component"] += 1
            else:
                phase_counts[str(R)]["tie"] += 1
            phase_cells += 1
        target_sets += 1

    receipt = {
        "artifact": "GMI_GENERATIVE_PREFIX_COMPONENT_PHASE_RECEIPT_V1",
        "status": "EXACT_FINITE_GENERATIVE_BURDEN_CALIBRATION",
        "runner": "run_gmi_generative_prefix_component_phase_v1.py",
        "string_length": L,
        "possible_strings": len(strings),
        "nonempty_target_sets": target_sets,
        "reuse_horizons": horizons,
        "phase_cells": phase_cells,
        "zero_prefix_saving_targets": zero_saving_targets,
        "phase_counts": phase_counts,
        "violations": violations,
        "claim_ceiling": "Exact uniform deterministic-string target family and two frozen realization languages only; not real AR/latent/diffusion/flow family selection.",
        "terminal": "GENERATIVE_PREFIX_COMPONENT_PHASE_EXACT_GREEN" if violations == 0 else "GENERATIVE_PREFIX_COMPONENT_PHASE_RED"
    }
    out = Path(__file__).with_name("GMI_GENERATIVE_PREFIX_COMPONENT_PHASE_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
