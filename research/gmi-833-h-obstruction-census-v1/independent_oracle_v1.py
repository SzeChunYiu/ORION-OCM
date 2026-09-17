#!/usr/bin/env python3
"""Source-separated tuple-truth-table oracle for the H obstruction census.

This module intentionally imports no primary checker code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "ORACLE_RESULT_V1.json"
ROWS = tuple(range(256))
OBS = tuple(range(8))


def canon(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def var(index):
    return tuple((row >> index) & 1 for row in ROWS)


V = tuple(var(i) for i in range(8))
ZERO = (0,) * 256
ONE = (1,) * 256


def neg(a):
    return tuple(1 - bit for bit in a)


def xor(a, b):
    return tuple(left ^ right for left, right in zip(a, b))


def land(a, b):
    return tuple(left & right for left, right in zip(a, b))


def targets():
    return {
        "COPY_SIGNAL": V[0],
        "INVERT_SIGNAL": neg(V[0]),
        "PAIR_PARITY": xor(V[0], V[1]),
        "PAIR_CONJUNCTION": land(V[0], V[1]),
        "TRIPLE_PARITY": xor(xor(V[0], V[1]), V[2]),
        "TRIPLE_CONJUNCTION": land(land(V[0], V[1]), V[2]),
        "UNEXCITED_CONTEXT": V[3],
        "HISTORY_STATE_CHANNEL": V[4],
        "STOCHASTIC_SOURCE_CHANNEL": V[5],
        "UPDATE_FEEDBACK_CHANNEL": V[6],
        "EXTERNAL_PEER_TOOL_CHANNEL": V[7],
    }


def exact_layers(limit=5):
    exact = {1: {ZERO, ONE, V[0], V[1], V[2], V[3]}}
    seen = set(exact[1])
    minimum = {table: 1 for table in exact[1]}
    for cost in range(2, limit + 1):
        proposed = {neg(table) for table in exact[cost - 1]}
        for left_cost in range(1, cost - 1):
            right_cost = cost - 1 - left_cost
            if right_cost < 1:
                continue
            for left in exact.get(left_cost, set()):
                for right in exact.get(right_cost, set()):
                    proposed.add(xor(left, right))
                    proposed.add(land(left, right))
        layer = proposed - seen
        exact[cost] = layer
        for table in layer:
            minimum[table] = cost
        seen.update(layer)
    return minimum, exact


def project(table):
    return tuple(table[row] for row in OBS)


def digest(table):
    packed = bytearray(32)
    for row, bit in enumerate(table):
        packed[row // 8] |= bit << (row % 8)
    return hashlib.sha256(bytes(packed)).hexdigest()


def build():
    minimum, exact = exact_layers()
    target_map = targets()
    candidates = {table: cost for table, cost in minimum.items() if cost <= 3}
    target_results = {}
    for name, target in sorted(target_map.items()):
        fits = {table: cost for table, cost in candidates.items() if project(table) == project(target)}
        fit_cost = min(fits.values()) if fits else None
        minimum_fits = sorted(digest(table) for table, cost in fits.items() if cost == fit_cost)
        target_results[name] = {
            "target_digest": digest(target),
            "minimum_full_cost": minimum.get(target),
            "minimum_fit_cost": fit_cost,
            "minimum_fit_digests": minimum_fits,
            "identified": len(minimum_fits) == 1 and minimum_fits[0] == digest(target),
        }
    return {
        "schema": "GMI833HObstructionIndependentOracleV1",
        "implementation": "tuple truth tables plus set-valued exact-cost closure; no primary import",
        "new_semantics_by_minimum_cost": {str(cost): len(exact[cost]) for cost in range(1, 6)},
        "target_results": target_results,
        "verdict": "INDEPENDENT_ORACLE_COMPLETE",
    }


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = canon(build())
    if args.check:
        if not OUT.exists() or OUT.read_bytes() != payload:
            raise SystemExit("ORACLE_RESULT_V1.json absent or stale")
        print("ORACLE_RESULT_V1_OK sha256=%s" % hashlib.sha256(payload).hexdigest())
    else:
        OUT.write_bytes(payload)
        print("wrote %s sha256=%s" % (OUT, hashlib.sha256(payload).hexdigest()))


if __name__ == "__main__":
    main()

