#!/usr/bin/env python3
"""Exact finite witnesses for NONNEURAL_CONSTRUCTIVE_DERIVATION_THEOREM_V1."""

from itertools import product
import json


def direct_parity(bits):
    p = 0
    for bit in bits:
        p ^= bit
    return p


def fsm_parity(bits):
    state = 0  # EVEN
    for bit in bits:
        state ^= bit
    return state


def one_state_mealy_exact(output_on_0, output_on_1, max_len=3):
    table = {0: output_on_0, 1: output_on_1}
    for n in range(1, max_len + 1):
        for bits in product([0, 1], repeat=n):
            # A one-state Mealy machine can only emit a function of the current input.
            emitted = table[bits[-1]]
            if emitted != direct_parity(bits):
                return False
    return True


def majority_obligation(bits):
    return int(sum(bits) >= 2)


def majority_circuit(bits):
    a, b, c = bits
    return int((a and b) or (a and c) or (b and c))


def main():
    # A. Running parity: two-state semantic automaton is exact on all strings length 0..8.
    parity_strings = 0
    for n in range(0, 9):
        for bits in product([0, 1], repeat=n):
            assert fsm_parity(bits) == direct_parity(bits)
            parity_strings += 1
    assert parity_strings == 511

    # B. Every possible one-state binary-input/binary-output Mealy table fails running parity.
    one_state_tables = 0
    one_state_exact = 0
    for out0, out1 in product([0, 1], repeat=2):
        one_state_tables += 1
        one_state_exact += int(one_state_mealy_exact(out0, out1))
    assert one_state_tables == 4
    assert one_state_exact == 0

    # C. Exact stateless truth-table/circuit witness for 3-bit majority.
    truth_table = {bits: majority_obligation(bits) for bits in product([0, 1], repeat=3)}
    majority_checks = 0
    for bits in product([0, 1], repeat=3):
        table_out = truth_table[bits]
        circuit_out = majority_circuit(bits)
        target = majority_obligation(bits)
        assert table_out == target == circuit_out
        majority_checks += 1
    assert majority_checks == 8

    receipt = {
        "terminal": "GRAND_GMI_NONNEURAL_CONSTRUCTIVE_DERIVATION_ALL_GREEN",
        "running_parity_strings_length_0_to_8": parity_strings,
        "one_state_mealy_tables_checked": one_state_tables,
        "one_state_exact_running_parity_machines": one_state_exact,
        "minimal_running_parity_semantic_states": 2,
        "majority_truth_table_circuit_checks": majority_checks,
        "nonneural_compiler_classes": ["finite_state_transducer", "truth_table", "boolean_circuit", "straight_line_program"],
        "neural_exclusion_claimed_from_semantics_alone": False
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
