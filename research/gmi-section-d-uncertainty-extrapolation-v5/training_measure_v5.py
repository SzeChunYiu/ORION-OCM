#!/usr/bin/env python3
"""Training-only measurement for Section D V5.

This program is intentionally incapable of running the held-out sizes. Its sole
purpose is to produce the n={2,3,4,5} numeric receipt used by the second-stage
freeze.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

TRAINING_SIZES = (2, 3, 4, 5)
AUTHORITY = "ab231d78aae98beb679ca0e0ce8c36c4651dc438"


def require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def relation(n: int):
    return {f"k{i}": f"v{(i + 1) % n}" for i in range(n)}


def value_index(rel):
    return {v: k for k, v in rel.items()}


def key_lookup(rel, direction: str, token: str):
    if direction == "F":
        return rel[token], 1
    found = None
    ops = 0
    for k, v in rel.items():
        ops += 1
        if v == token:
            found = k
    require(found is not None, "reverse lookup target missing")
    return found, ops


def value_lookup(inv, direction: str, token: str):
    if direction == "R":
        return inv[token], 1
    found = None
    ops = 0
    for v, k in inv.items():
        ops += 1
        if k == token:
            found = v
    require(found is not None, "forward lookup target missing")
    return found, ops


def migrate(rel):
    out = {}
    ops = 0
    for k, v in rel.items():
        ops += 1  # read
        out[v] = k
        ops += 1  # write
    return out, ops


def block(n: int):
    # Exactly 3 forward + 4 reverse requests; tokens may repeat at tiny n.
    return (
        ("F", "k0"),
        ("F", f"k{1 % n}"),
        ("F", f"k{(n - 1) % n}"),
        ("R", "v0"),
        ("R", f"v{1 % n}"),
        ("R", f"v{(n - 1) % n}"),
        ("R", "v0"),
    )


def expected(rel, direction, token):
    return rel[token] if direction == "F" else value_index(rel)[token]


def measure(n: int):
    require(n in TRAINING_SIZES, "held-out sizes are forbidden in training program")
    rel = relation(n)
    inv = value_index(rel)
    _, migration_ops = migrate(rel)
    key_ops = 0
    value_ops = 0
    for direction, token in block(n):
        kout, kop = key_lookup(rel, direction, token)
        vout, vop = value_lookup(inv, direction, token)
        target = expected(rel, direction, token)
        require(kout == target == vout, "training implementation failed exactness")
        key_ops += kop
        value_ops += vop
    return {
        "n": n,
        "persistent_cells_single_orientation": n,
        "migration_ops": migration_ops,
        "key_block_ops": key_ops,
        "value_block_ops": value_ops,
    }


def build():
    rows = [measure(n) for n in TRAINING_SIZES]
    payload = {
        "authority_freeze_commit": AUTHORITY,
        "training_sizes": list(TRAINING_SIZES),
        "rows": rows,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["numeric_receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main():
    result = build()
    out = Path(__file__).with_name("TRAIN_V5.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
