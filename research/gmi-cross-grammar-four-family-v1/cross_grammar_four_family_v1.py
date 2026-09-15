#!/usr/bin/env python3
"""Two finite grammars neutrally recovering four known morphology classes."""

from __future__ import annotations

import json
from itertools import combinations_with_replacement, product
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def _pick(scored: list[tuple[int, str, Any]]) -> tuple[int, Any]:
    if not scored:
        raise ValueError("no exact candidate")
    cost, _stable, raw = min(scored)
    return cost, raw


def _score(candidates, exact: Callable[[Any], bool], cost: Callable[[Any], int]):
    rows = [(cost(candidate), repr(candidate), candidate) for candidate in candidates if exact(candidate)]
    winner_cost, winner = _pick(rows)
    return {"candidate_count": len(candidates), "exact_count": len(rows), "winner": winner, "cost": winner_cost}


# 1. Unary state --------------------------------------------------------------
def _state_a_candidates():
    rows = []
    for count in (1, 2):
        for transition in product(range(count), repeat=count):
            for output in product((0, 1), repeat=count):
                rows.append((count, transition, output))
    return tuple(rows)


def _state_a_trace(candidate, length=7):
    count, transition, output = candidate
    state = 0
    trace = [output[state]]
    for _ in range(length - 1):
        state = transition[state]
        trace.append(output[state])
    return tuple(trace)


STATE_EXPRESSIONS = ("zero", "one", "s", "not_s")


def _state_expr(name, state):
    return {"zero": 0, "one": 1, "s": state, "not_s": 1 - state}[name]


def _state_b_trace(candidate, length=7):
    update, read = candidate
    state = 0
    trace = [_state_expr(read, state)]
    for _ in range(length - 1):
        state = _state_expr(update, state)
        trace.append(_state_expr(read, state))
    return tuple(trace)


def recover_state():
    positive = tuple(int(length % 2 == 0) for length in range(7))
    twin = (1,) * 7
    a = _state_a_candidates()
    b = tuple(product(STATE_EXPRESSIONS, repeat=2))
    cost_a = lambda candidate: 2 * candidate[0]
    cost_b = lambda candidate: sum(name.startswith("not_") for name in candidate)
    return {
        "A": _score(a, lambda candidate: _state_a_trace(candidate) == positive, cost_a),
        "A_twin": _score(a, lambda candidate: _state_a_trace(candidate) == twin, cost_a),
        "B": _score(b, lambda candidate: _state_b_trace(candidate) == positive, cost_b),
        "B_twin": _score(b, lambda candidate: _state_b_trace(candidate) == twin, cost_b),
    }


# 2. Shared local operation ---------------------------------------------------
RING_STATES = tuple(product((0, 1), repeat=4))


def _local_target(state, alternating=False):
    out = []
    for site in range(4):
        left, centre = state[site - 1], state[site]
        out.append((left | centre) if alternating and site % 2 else (left & centre))
    return tuple(out)


def _local_a_fit(candidate, alternating=False):
    feature, address = candidate
    table = {}
    for state in RING_STATES:
        target = _local_target(state, alternating)
        for site, value in enumerate(target):
            observed = (state[site - 1], state[site], state[(site + 1) % 4]) if feature == "triple" else state
            key = ((site,) if address == "site" else ()) + observed
            if key in table and table[key] != value:
                return None
            table[key] = value
    return table


VARIABLES = ("l", "c", "r")
LOCAL_EXPRESSIONS = VARIABLES + tuple(
    (operation, left, right)
    for operation in ("and", "or")
    for left, right in combinations_with_replacement(VARIABLES, 2)
)


def _eval_local_expr(expression, left, centre, right):
    values = {"l": left, "c": centre, "r": right}
    if isinstance(expression, str):
        return values[expression]
    operation, a, b = expression
    return (values[a] & values[b]) if operation == "and" else (values[a] | values[b])


def _local_b_exact(candidate, alternating=False):
    scope, expressions = candidate
    for state in RING_STATES:
        result = tuple(
            _eval_local_expr(expressions[0] if scope == "shared" else expressions[site], state[site - 1], state[site], state[(site + 1) % 4])
            for site in range(4)
        )
        if result != _local_target(state, alternating):
            return False
    return True


def recover_local():
    a = tuple(product(("triple", "configuration"), ("shared", "site")))
    shared = tuple(("shared", (expression,)) for expression in LOCAL_EXPRESSIONS)
    site = tuple(("site", expressions) for expressions in product(LOCAL_EXPRESSIONS, repeat=4))
    b = shared + site
    score_a = lambda alternating: _score(
        a,
        lambda candidate: _local_a_fit(candidate, alternating) is not None,
        lambda candidate: len(_local_a_fit(candidate, alternating) or {}),
    )
    score_b = lambda alternating: _score(
        b,
        lambda candidate: _local_b_exact(candidate, alternating),
        lambda candidate: sum(0 if isinstance(expr, str) else 1 for expr in candidate[1]),
    )
    return {"A": score_a(False), "A_twin": score_a(True), "B": score_b(False), "B_twin": score_b(True)}


# 3. Input-indexed read -------------------------------------------------------
ROUTING_CASES = tuple((pointer, data) for pointer in range(4) for data in product((0, 1), repeat=4))


def recover_routing():
    a = ((0,), (1,), (2,), (3,), ("from_input",))
    b = tuple(("read", index) for index in range(4)) + tuple(("branches", leaves) for leaves in product(range(4), repeat=4))

    def apply_a(candidate, pointer, data):
        return data[pointer] if candidate[0] == "from_input" else data[candidate[0]]

    def apply_b(candidate, pointer, data):
        return data[candidate[1][pointer]] if candidate[0] == "branches" else data[candidate[1]]

    positive_a = lambda candidate: all(apply_a(candidate, pointer, data) == data[pointer] for pointer, data in ROUTING_CASES)
    positive_b = lambda candidate: all(apply_b(candidate, pointer, data) == data[pointer] for pointer, data in ROUTING_CASES)
    twin_cases = tuple((0, data) for data in product((0, 1), repeat=4))
    twin_a = lambda candidate: all(apply_a(candidate, pointer, data) == data[0] for pointer, data in twin_cases)
    twin_b = lambda candidate: all(apply_b(candidate, pointer, data) == data[0] for pointer, data in twin_cases)
    return {
        "A": _score(a, positive_a, lambda candidate: 3 if candidate[0] == "from_input" else 1),
        "A_twin": _score(a, twin_a, lambda candidate: 3 if candidate[0] == "from_input" else 1),
        "B": _score(b, positive_b, lambda candidate: 3 if candidate[0] == "branches" else 1),
        "B_twin": _score(b, twin_b, lambda candidate: 3 if candidate[0] == "branches" else 1),
    }


# 4. Keyed storage ------------------------------------------------------------
KEYS = tuple(product((0, 1), repeat=3))
UNSTRUCTURED = tuple(map(int, "01101001"))


def _boolean_program_signatures():
    base = {(0,) * 8, (1,) * 8, *(tuple(key[index] for key in KEYS) for index in range(3))}
    reachable = set(base)
    pools = {tuple(sorted(base))}
    for _ in range(2):
        next_pools = set()
        for packed in pools:
            pool = set(packed)
            generated = {tuple(1 - bit for bit in value) for value in pool}
            for left in pool:
                for right in pool:
                    generated.update((tuple(a & b for a, b in zip(left, right)), tuple(a | b for a, b in zip(left, right))))
            for value in generated:
                reachable.add(value)
                next_pools.add(tuple(sorted(pool | {value})))
        pools = next_pools
    return reachable


def recover_storage():
    weighted = tuple(("weighted", weights, bias) for weights in product(range(-2, 3), repeat=3) for bias in range(-2, 3))
    rows = tuple(("rows", values) for values in product((0, 1), repeat=8))
    a = weighted + rows
    programs = tuple(("expression", values) for values in _boolean_program_signatures())
    leaves = tuple(("leaves", values) for values in product((0, 1), repeat=8))
    b = programs + leaves

    def output_a(candidate):
        if candidate[0] == "rows":
            return candidate[1]
        _kind, weights, bias = candidate
        return tuple(int(sum(x * w for x, w in zip(key, weights)) + bias >= 0) for key in KEYS)

    output_b = lambda candidate: candidate[1]
    twin = tuple(key[0] for key in KEYS)
    return {
        "A": _score(a, lambda candidate: output_a(candidate) == UNSTRUCTURED, lambda candidate: 8 if candidate[0] == "rows" else 4),
        "A_twin": _score(a, lambda candidate: output_a(candidate) == twin, lambda candidate: 8 if candidate[0] == "rows" else 4),
        "B": _score(b, lambda candidate: output_b(candidate) == UNSTRUCTURED, lambda candidate: 8 if candidate[0] == "leaves" else 2),
        "B_twin": _score(b, lambda candidate: output_b(candidate) == twin, lambda candidate: 8 if candidate[0] == "leaves" else 2),
    }


def classify(family: str, grammar: str, raw: Any) -> str:
    if family == "state":
        if grammar == "A":
            return "RECURRENT_STATE" if raw[0] > 1 else "STATELESS_CONSTANT"
        return "RECURRENT_STATE" if "not_s" in raw else "STATELESS_CONSTANT"
    if family == "local":
        return "SHARED_LOCAL_UPDATE" if (raw[1] == "shared" if grammar == "A" else raw[0] == "shared") else "SITE_SPECIFIC_UPDATE"
    if family == "routing":
        return "INPUT_INDEXED_ROUTING" if (raw[0] == "from_input" if grammar == "A" else raw[0] == "branches" and len(set(raw[1])) > 1) else "FIXED_READ"
    if family == "storage":
        return "KEYED_STORAGE" if raw[0] in {"rows", "leaves"} else "COMPACT_RULE"
    raise ValueError("unknown post-run family")


def validate_closure() -> dict[str, Any]:
    ledger = json.loads((HERE / "CROSS_GRAMMAR_LEDGER_V1.json").read_text(encoding="utf-8"))
    receipt = json.loads((HERE / "RESULT_V1.json").read_text(encoding="utf-8"))
    if len(ledger["rows"]) != 2 or any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("cross-grammar task ledger drifted")
    recoveries = {"state": recover_state(), "local": recover_local(), "routing": recover_routing(), "storage": recover_storage()}
    expected = {"state": "RECURRENT_STATE", "local": "SHARED_LOCAL_UPDATE", "routing": "INPUT_INDEXED_ROUTING", "storage": "KEYED_STORAGE"}
    labels = {}
    flips = 0
    for family, result in recoveries.items():
        labels[family] = {}
        for grammar in ("A", "B"):
            positive = classify(family, grammar, result[grammar]["winner"])
            twin = classify(family, grammar, result[f"{grammar}_twin"]["winner"])
            if positive != expected[family] or twin == positive:
                raise ValueError(f"{family}/{grammar} recovery or twin drifted")
            labels[family][grammar] = positive
            flips += 1
    raw_spaces = repr((_state_a_candidates(), STATE_EXPRESSIONS, LOCAL_EXPRESSIONS, ("from_input", "branches"), ("weighted", "rows", "expression", "leaves"))).lower()
    forbidden = ("neural", "cnn", "rnn", "lstm", "transformer", "attention", "memory", "automaton")
    if any(token in raw_spaces for token in forbidden):
        raise ValueError("candidate serialization leaks family label")
    if len(set(expected.values())) != 4 or flips != 8:
        raise ValueError("four-family/twin coverage drifted")
    counts = {family: {grammar: result[grammar]["candidate_count"] for grammar in ("A", "B")}
              for family, result in recoveries.items()}
    if receipt["schema"] != "GMI_CROSS_GRAMMAR_FOUR_FAMILY_RESULT_V1" or receipt["status"] != "EXECUTED_FINITE_EXACT":
        raise ValueError("cross-grammar receipt schema/status drifted")
    if receipt["candidate_counts"] != counts or receipt["positive_labels"] != expected:
        raise ValueError("cross-grammar receipt result drifted")
    if (receipt["families"], receipt["grammars"], receipt["positive_twin_flips"]) != (4, 2, 8):
        raise ValueError("cross-grammar receipt coverage drifted")
    return {"families": 4, "grammars": 2, "positive_labels": labels, "positive_twin_flips": flips, "ledger_rows": 2, "recoveries": recoveries}


if __name__ == "__main__":
    print("GMI_CROSS_GRAMMAR_FOUR_FAMILY_V1_VALID")
    print(json.dumps(validate_closure(), sort_keys=True, default=list))
