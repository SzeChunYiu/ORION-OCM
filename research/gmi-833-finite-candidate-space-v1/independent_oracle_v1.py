#!/usr/bin/env python3
"""Independent direct Cartesian oracle for the registered finite G0 slice.

This intentionally does not import the scientific executor or reuse its option
constructor, candidate class, validation, or count function.
"""

from __future__ import annotations

from itertools import product


def _positive(value: object, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive exact integer")
    return value


def raw_instruction_codes(labels: int, registers: int) -> tuple[tuple[str, int, int, int], ...]:
    labels = _positive(labels, "labels")
    registers = _positive(registers, "registers")
    rows: list[tuple[str, int, int, int]] = []
    rows += [("READ", r, q, -1) for r in range(registers) for q in range(labels)]
    rows += [("INC", r, q, -1) for r in range(registers) for q in range(labels)]
    rows += [
        ("DECJZ", r, positive, zero)
        for r in range(registers)
        for positive in range(labels)
        for zero in range(labels)
    ]
    rows += [("EMIT", r, q, -1) for r in range(registers) for q in range(labels)]
    rows += [("HALT", -1, -1, -1)]
    return tuple(rows)


def enumerate_raw_codes(code_bound: int, register_bound: int) -> tuple[tuple[int, tuple[tuple[str, int, int, int], ...]], ...]:
    code_bound = _positive(code_bound, "code_bound")
    register_bound = _positive(register_bound, "register_bound")
    rows: list[tuple[int, tuple[tuple[str, int, int, int], ...]]] = []
    for registers in range(1, register_bound + 1):
        for labels in range(1, code_bound + 1):
            choices = raw_instruction_codes(labels, registers)
            rows.extend((registers, tuple(table)) for table in product(choices, repeat=labels))
    if len(rows) != len(set(rows)):
        raise AssertionError("independent Cartesian oracle emitted a duplicate")
    return tuple(rows)


def closed_form_count(code_bound: int, register_bound: int) -> int:
    code_bound = _positive(code_bound, "code_bound")
    register_bound = _positive(register_bound, "register_bound")
    answer = 0
    for registers in range(1, register_bound + 1):
        for labels in range(1, code_bound + 1):
            alphabet = 1 + 3 * registers * labels + registers * labels * labels
            answer += alphabet**labels
    return answer
