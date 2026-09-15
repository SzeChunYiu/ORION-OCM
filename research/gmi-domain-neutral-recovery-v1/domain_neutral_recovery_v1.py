#!/usr/bin/env python3
"""Exhaustive family-name-hidden searches for three Issue #602 domains."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def _select(scored: list[tuple[int, tuple[Any, ...]]]) -> tuple[int, tuple[Any, ...]]:
    if not scored:
        raise ValueError("no exact candidate")
    return min(scored)


# Relational compatibility/assembly ------------------------------------------
RELATIONAL_CANDIDATES = tuple(product(("equal", "unconditional"), ("merge", "left")))
RELATIONAL_CASES = (
    ((('a', 0), ('b', 1)), (('b', 1), ('c', 0))),
    ((('a', 0), ('b', 1)), (('b', 0), ('c', 0))),
    ((('a', 1),), (('d', 0),)),
)


def _relational_apply(candidate: tuple[str, str], case: tuple[tuple[tuple[str, int], ...], ...]):
    test, output = candidate
    left, right = map(dict, case)
    overlap = left.keys() & right.keys()
    compatible = test == "unconditional" or all(left[key] == right[key] for key in overlap)
    if not compatible:
        return None
    if output == "left":
        return tuple(sorted(left.items()))
    merged = dict(left)
    merged.update(right)
    return tuple(sorted(merged.items()))


def _relational_oracle(case):
    return _relational_apply(("equal", "merge"), case)


def _overlap_count(case) -> int:
    left, right = map(dict, case)
    return len(left.keys() & right.keys())


def relational_recovery_certificate() -> dict[str, Any]:
    expected = tuple(_relational_oracle(case) for case in RELATIONAL_CASES)
    exact = []
    for candidate in RELATIONAL_CANDIDATES:
        outputs = tuple(_relational_apply(candidate, case) for case in RELATIONAL_CASES)
        if outputs == expected:
            # Equality dispatch costs one per case plus one per actual overlap;
            # unconditional acceptance needs neither operation.
            comparisons = len(RELATIONAL_CASES) + sum(_overlap_count(case) for case in RELATIONAL_CASES)
            cost = comparisons if candidate[0] == "equal" else 0
            cost += sum(len(case[0]) + (len(case[1]) if candidate[1] == "merge" else 0) for case in RELATIONAL_CASES)
            exact.append((cost, candidate))
    disjoint = (RELATIONAL_CASES[2], ((('x', 0),), (('y', 1),)))
    twin_expected = tuple(_relational_oracle(case) for case in disjoint)
    twin_exact = []
    for candidate in RELATIONAL_CANDIDATES:
        if tuple(_relational_apply(candidate, case) for case in disjoint) == twin_expected:
            cost = sum(len(case[0]) + len(case[1]) for case in disjoint)
            cost += (len(disjoint) + sum(_overlap_count(case) for case in disjoint)) if candidate[0] == "equal" else 0
            twin_exact.append((cost, candidate))
    winner = _select(exact)
    twin_winner = _select(twin_exact)
    return {
        "candidate_count": len(RELATIONAL_CANDIDATES),
        "exact_count": len(exact),
        "winner": winner[1],
        "winner_cost": winner[0],
        "twin_exact_count": len(twin_exact),
        "twin_winner": twin_winner[1],
    }


# Shared local update ---------------------------------------------------------
LOCAL_CANDIDATES = tuple(product(("triple", "configuration"), ("shared", "site"), ("snapshot", "inplace")))


def _eca(rule: int, left: int, centre: int, right: int) -> int:
    return (rule >> (4 * left + 2 * centre + right)) & 1


def _target_step(state: tuple[int, ...], rules: tuple[int, ...]) -> tuple[int, ...]:
    length = len(state)
    return tuple(_eca(rules[index], state[index - 1], state[index], state[(index + 1) % length]) for index in range(length))


def _feature(state: tuple[int, ...], site: int, kind: str) -> tuple[int, ...]:
    if kind == "triple":
        return state[site - 1], state[site], state[(site + 1) % len(state)]
    return state


def _fit_local_candidate(candidate: tuple[str, str, str], rules: tuple[int, ...]):
    feature, address, _clock = candidate
    states = tuple(product((0, 1), repeat=len(rules)))
    table: dict[tuple[Any, ...], int] = {}
    for state in states:
        target = _target_step(state, rules)
        for site, value in enumerate(target):
            key = ((site,) if address == "site" else ()) + _feature(state, site, feature)
            if key in table and table[key] != value:
                return None, states
            table[key] = value
    return table, states


def _candidate_step(state: tuple[int, ...], candidate: tuple[str, str, str], table) -> tuple[int, ...]:
    feature, address, clock = candidate
    current = list(state)
    snapshot = tuple(state)
    output = list(state)
    for site in range(len(state)):
        source = snapshot if clock == "snapshot" else tuple(output)
        key = ((site,) if address == "site" else ()) + _feature(source, site, feature)
        if key not in table:
            return ()
        output[site] = table[key]
    return tuple(output)


def _local_exact(candidate: tuple[str, str, str], rules: tuple[int, ...]) -> tuple[bool, int]:
    table, states = _fit_local_candidate(candidate, rules)
    if table is None:
        return False, 10**9
    for state in states:
        expected = _target_step(_target_step(state, rules), rules)
        first = _candidate_step(state, candidate, table)
        if not first or _candidate_step(first, candidate, table) != expected:
            return False, len(table)
    return True, len(table)


def local_recovery_certificate() -> dict[str, Any]:
    uniform = (90,) * 5
    alternating = tuple(90 if site % 2 == 0 else 150 for site in range(5))
    exact = [(cost, candidate) for candidate in LOCAL_CANDIDATES if (result := _local_exact(candidate, uniform))[0] for cost in (result[1],)]
    twin_exact = [(cost, candidate) for candidate in LOCAL_CANDIDATES if (result := _local_exact(candidate, alternating))[0] for cost in (result[1],)]
    winner = _select(exact)
    twin_winner = _select(twin_exact)
    return {
        "candidate_count": len(LOCAL_CANDIDATES),
        "state_count": 32,
        "exact_count": len(exact),
        "winner": winner[1],
        "winner_entries": winner[0],
        "twin_exact_count": len(twin_exact),
        "twin_winner": twin_winner[1],
        "twin_entries": twin_winner[0],
    }


# Iterative product feedback --------------------------------------------------
CONSTRUCTIVE_CANDIDATES = tuple(product((False, True), range(5)))
SEEDS = frozenset({"01", "110"})


def _construct(candidate: tuple[bool, int]) -> tuple[frozenset[str], int]:
    feedback, rounds = candidate
    built = set(SEEDS)
    work = 0
    for _ in range(rounds):
        source = tuple(built if feedback else SEEDS)
        products = set()
        for left in source:
            for right in source:
                work += 1
                if len(left) + len(right) <= 8:
                    products.add(left + right)
        built.update(products)
    return frozenset(built), work


def _universe() -> tuple[str, ...]:
    return tuple("".join(bits) for length in range(1, 9) for bits in product("01", repeat=length))


def constructive_recovery_certificate() -> dict[str, Any]:
    universe = _universe()
    target, _ = _construct((True, 4))
    expected = tuple(item in target for item in universe)
    exact = []
    for candidate in CONSTRUCTIVE_CANDIDATES:
        result, cost = _construct(candidate)
        if tuple(item in result for item in universe) == expected:
            exact.append((cost, candidate))
    twin_queries = ("01", "110", "0", "1", "111", "000")
    twin_expected = tuple(item in SEEDS for item in twin_queries)
    twin_exact = []
    for candidate in CONSTRUCTIVE_CANDIDATES:
        result, cost = _construct(candidate)
        if tuple(item in result for item in twin_queries) == twin_expected:
            twin_exact.append((cost, candidate))
    winner = _select(exact)
    twin_winner = _select(twin_exact)
    return {
        "candidate_count": len(CONSTRUCTIVE_CANDIDATES),
        "query_count": len(universe),
        "closure_size": len(target),
        "exact_count": len(exact),
        "winner": winner[1],
        "winner_work": winner[0],
        "twin_exact_count": len(twin_exact),
        "twin_winner": twin_winner[1],
    }


def validate_closure() -> dict[str, Any]:
    ledger = json.loads((HERE / "DOMAIN_NEUTRAL_RECOVERY_LEDGER_V1.json").read_text(encoding="utf-8"))
    if len(ledger["rows"]) != 3 or any(row["task"] != "Neutral recovery." or row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("domain-neutral ledger drifted")
    if len({row["domain"] for row in ledger["rows"]}) != 3:
        raise ValueError("domain-neutral ledger domain count drifted")
    for row in ledger["rows"]:
        if not (REPO / row["evidence"].split("#", 1)[0]).is_file():
            raise ValueError(f"missing evidence: {row['evidence']}")
    serialized = repr((RELATIONAL_CANDIDATES, LOCAL_CANDIDATES, CONSTRUCTIVE_CANDIDATES)).lower()
    forbidden = ("sheaf", "cellular", "field", "autocatalytic", "closure", "gnn", "nca")
    if any(token in serialized for token in forbidden):
        raise ValueError("candidate grammar leaks a domain/family label")
    relational = relational_recovery_certificate()
    local = local_recovery_certificate()
    constructive = constructive_recovery_certificate()
    if relational["winner"] != ("equal", "merge") or relational["twin_winner"] == relational["winner"]:
        raise ValueError("relational recovery/twin drifted")
    if local["winner"] != ("triple", "shared", "snapshot") or local["twin_winner"] != ("triple", "site", "snapshot"):
        raise ValueError("local recovery/twin drifted")
    if constructive["winner"] != (True, 2) or constructive["twin_winner"] != (False, 0):
        raise ValueError("constructive recovery/twin drifted")
    return {"ledger_rows": 3, "family_label_free": True, "relational": relational, "local": local, "constructive": constructive}


if __name__ == "__main__":
    result = validate_closure()
    print("GMI_DOMAIN_NEUTRAL_RECOVERY_V1_VALID")
    print(json.dumps(result, sort_keys=True))
