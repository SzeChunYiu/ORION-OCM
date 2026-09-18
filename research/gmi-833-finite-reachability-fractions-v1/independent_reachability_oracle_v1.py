#!/usr/bin/env python3
"""Source-separated direct-product and protected-execution oracle."""

from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORDS = ((), (0,), (1,))
STEP_CAP = 6


def options(n: int, r: int) -> tuple[tuple[str, int, int, int], ...]:
    rows: list[tuple[str, int, int, int]] = []
    for reg in range(r):
        for target in range(n):
            rows.append(("READ", reg, target, -1))
    for reg in range(r):
        for target in range(n):
            rows.append(("INC", reg, target, -1))
    for reg in range(r):
        for nonzero in range(n):
            for zero in range(n):
                rows.append(("DECJZ", reg, nonzero, zero))
    for reg in range(r):
        for target in range(n):
            rows.append(("EMIT", reg, target, -1))
    rows.append(("HALT", -1, -1, -1))
    return tuple(rows)


def direct_presentations(nmax: int, rmax: int) -> tuple[tuple[int, tuple[tuple[str, int, int, int], ...]], ...]:
    rows = []
    for r in range(1, rmax + 1):
        for n in range(1, nmax + 1):
            for table in product(options(n, r), repeat=n):
                rows.append((r, tuple(table)))
    return tuple(rows)


def execute(code, word: tuple[int, ...]) -> tuple[str, tuple[int, ...]]:
    r, table = code
    registers = [0] * r
    pc = 0
    input_pos = 0
    output: list[int] = []
    steps = 0
    while True:
        if steps >= STEP_CAP:
            return ("STEP_LIMIT", tuple(output))
        op, register, target0, target1 = table[pc]
        if op == "HALT":
            return ("HALTED", tuple(output))
        steps += 1
        if op == "READ":
            if input_pos >= len(word):
                return ("BLOCKED_INPUT", tuple(output))
            registers[register] = word[input_pos]
            input_pos += 1
            pc = target0
        elif op == "INC":
            registers[register] += 1
            pc = target0
        elif op == "DECJZ":
            if registers[register] > 0:
                registers[register] -= 1
                pc = target0
            else:
                pc = target1
        elif op == "EMIT":
            output.append(registers[register])
            pc = target0
        else:
            raise ValueError("unknown operation in independent oracle")


def semantic_key(code) -> tuple[tuple[str, tuple[int, ...]], ...]:
    return tuple(execute(code, word) for word in WORDS)


def jsonable_key(key) -> list[list[object]]:
    return [[status, list(output)] for status, output in key]


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def oracle_census(path: Path | None = None) -> dict[str, object]:
    registry = json.loads((path or HERE / "LAW_REGISTRY_V1.json").read_text(encoding="utf-8"))
    universe = direct_presentations(2, 2)
    universe_keys = {semantic_key(code) for code in universe}
    rows = []
    for law in registry["laws"]:
        reached = direct_presentations(law["max_code_cells"], law["max_register_cells"])
        keys = {semantic_key(code) for code in reached}
        rows.append({
            "law_id": law["id"],
            "reachable_presentation_count": len(reached),
            "reachable_quotient_class_count": len(keys),
            "reachable_semantic_keys_sha256": sha256(
                canonical_json(sorted(jsonable_key(key) for key in keys)).encode("utf-8")
            ).hexdigest(),
        })
    return {
        "universe_presentation_count": len(universe),
        "universe_quotient_count": len(universe_keys),
        "laws": rows,
    }


if __name__ == "__main__":
    print(canonical_json(oracle_census()), end="")
