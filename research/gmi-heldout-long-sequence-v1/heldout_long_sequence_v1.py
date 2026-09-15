from __future__ import annotations

from itertools import combinations_with_replacement
from math import ceil, log2

LEAVES = ("s", "x", "0", "1")
OPS = ("add", "xor", "min", "max")
CALIBRATION_LENGTHS = (3, 5, 7)
HELDOUT_LENGTHS = (17, 31, 63)


def candidates() -> tuple[str, ...]:
    out = list(LEAVES)
    for op in OPS:
        for a, b in combinations_with_replacement(LEAVES, 2):
            out.append(f"{op}({a},{b})")
    assert len(out) == 44
    return tuple(out)


def _leaf(name: str, s: int, x: int) -> int:
    return {"s": s, "x": x, "0": 0, "1": 1}[name]


def evaluate(expr: str, s: int, x: int) -> int:
    if expr in LEAVES:
        return _leaf(expr, s, x)
    op, tail = expr.split("(", 1)
    a, b = tail[:-1].split(",")
    va, vb = _leaf(a, s, x), _leaf(b, s, x)
    if op == "add":
        return va + vb
    if op == "xor":
        return va ^ vb
    if op == "min":
        return min(va, vb)
    if op == "max":
        return max(va, vb)
    raise ValueError(op)


def exact_pairs(expr: str, n: int) -> set[tuple[int, int]]:
    """Exact dynamic quotient of all 2**n binary histories.

    Pair=(candidate state, true count). Merging only identical pairs preserves
    exact terminal correctness while avoiding history enumeration.
    """
    pairs = {(0, 0)}
    for _ in range(n):
        nxt: set[tuple[int, int]] = set()
        for state, count in pairs:
            for x in (0, 1):
                nxt.add((evaluate(expr, state, x), count + x))
        pairs = nxt
    return pairs


def exact(expr: str, n: int) -> bool:
    return all(state == count for state, count in exact_pairs(expr, n))


def node_count(expr: str) -> int:
    return 1 if expr in LEAVES else 3


def depends_on_both(expr: str, n: int) -> bool:
    reachable = {0}
    depends_x = False
    depends_s = False
    for _ in range(n):
        states = sorted(reachable)
        if any(evaluate(expr, s, 0) != evaluate(expr, s, 1) for s in states):
            depends_x = True
        if len(states) >= 2:
            for x in (0, 1):
                vals = {evaluate(expr, s, x) for s in states}
                if len(vals) >= 2:
                    depends_s = True
        reachable = {evaluate(expr, s, x) for s in reachable for x in (0, 1)}
    return depends_s and depends_x


def classify(expr: str, n: int) -> str:
    pairs = exact_pairs(expr, n)
    states = {s for s, _ in pairs}
    if exact(expr, n) and depends_on_both(expr, n) and len(states) == n + 1:
        return "ACCUMULATIVE_CARRY"
    return "OTHER_EXACT" if exact(expr, n) else "INEXACT"


def score_length(n: int) -> dict[str, object]:
    rows = []
    for expr in candidates():
        pairs = exact_pairs(expr, n)
        is_exact = all(s == c for s, c in pairs)
        rows.append({
            "expr": expr,
            "nodes": node_count(expr),
            "exact": is_exact,
            "terminal_state_count": len({s for s, _ in pairs}),
            "class": classify(expr, n),
        })
    exact_rows = [r for r in rows if r["exact"]]
    min_nodes = min(r["nodes"] for r in exact_rows) if exact_rows else None
    winners = [r for r in exact_rows if r["nodes"] == min_nodes]
    bits = ceil(log2(n + 1))
    return {
        "n": n,
        "candidate_count": len(rows),
        "exact_candidate_count": len(exact_rows),
        "minimum_exact_nodes": min_nodes,
        "winners": winners,
        "required_terminal_states": n + 1,
        "carried_state_bits": bits,
        "explicit_history_bits": n,
        "compact_storage_strictly_smaller": bits < n,
    }


def result() -> dict[str, object]:
    calibration = [score_length(n) for n in CALIBRATION_LENGTHS]
    heldout = [score_length(n) for n in HELDOUT_LENGTHS]
    success = all(
        len(r["winners"]) >= 1
        and all(w["class"] == "ACCUMULATIVE_CARRY" for w in r["winners"])
        and all(w["terminal_state_count"] == r["required_terminal_states"] for w in r["winners"])
        and r["compact_storage_strictly_smaller"]
        for r in heldout
    )
    return {
        "schema": "GMI_HELDOUT_LONG_SEQUENCE_V1",
        "freeze_commit": "8e056fc56b833467d7cc4185ca0fda7d7c5f6dde",
        "grammar_candidate_count": len(candidates()),
        "calibration": calibration,
        "heldout": heldout,
        "terminal": (
            "HELDOUT_LONG_SEQUENCE_NEUTRAL_RECOVERY_EXACT_AT_FROZEN_LENGTHS"
            if success else "HELDOUT_LONG_SEQUENCE_PREDICTION_FAILED"
        ),
        "claim_ceiling": "FINITE_EXACT_HELDOUT_LONG_SEQUENCE_NEUTRAL_RECOVERY_PARENT_OWNED_PROGRAM_SYNTHESIS",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(result(), indent=2, sort_keys=True))
