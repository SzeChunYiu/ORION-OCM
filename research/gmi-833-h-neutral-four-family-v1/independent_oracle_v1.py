#!/usr/bin/env python3
"""Source-separated formula/residual oracle for the frozen blind obligations."""

from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FIELD = (0, 1, 2)


def points(arity):
    return tuple(product(FIELD, repeat=arity))


def affine(table, arity):
    table = tuple(table)
    for coefficients in product(FIELD, repeat=arity + 1):
        response = tuple(
            (coefficients[0] + sum(coefficients[i + 1] * point[i] for i in range(arity))) % 3
            for point in points(arity)
        )
        if response == table:
            return True
    return False


def zero_affine(table, arity):
    table = tuple(table)
    for coefficients in product(FIELD, repeat=arity + 1):
        score = tuple(
            (coefficients[0] + sum(coefficients[i + 1] * point[i] for i in range(arity))) % 3
            for point in points(arity)
        )
        if tuple(int(value == 0) for value in score) == table:
            return True
    return False


def interaction(table):
    table = tuple(table)
    at = lambda x, y: table[3 * x + y]
    return any((at(x, y) - at(x, 0) - at(0, y) + at(0, 0)) % 3 for x in FIELD for y in FIELD)


def classify_static(table, arity):
    if affine(table, arity):
        return "AFFINE_SHARED_RESPONSE" if arity == 1 else "ADDITIVELY_SEPARABLE_RESPONSE"
    if zero_affine(table, arity):
        return "BINARY_DECISION_ON_AFFINE_SCORE"
    if arity == 1:
        return "NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE"
    if interaction(table):
        return "CROSS_COORDINATE_LIFTED_INTERACTION"
    return "UNCLASSIFIED_FINITE_RESPONSE"


def classify_sequence(obligation):
    traces = {tuple(row["input"]): tuple(row["output"]) for row in obligation["protected_traces"]}
    residuals = tuple(traces[(prefix, 0)][1] for prefix in FIELD)
    if len(set(residuals)) == 3:
        realized = all(
            tuple(sum(word[: index + 1]) % 3 for index in range(len(word))) == output
            for word, output in traces.items()
        )
        if realized:
            return "PERSISTENT_THREE_CLASS_FUTURE_RESPONSE_QUOTIENT", residuals
    memoryless = all(tuple(word) == output for word, output in traces.items())
    if memoryless:
        return "MEMORYLESS_PROJECTION", residuals
    return "UNCLASSIFIED_SEQUENTIAL_RESPONSE", residuals


def canonical(value):
    return json.dumps(value, sort_keys=True, indent=2) + "\n"


def build():
    obligations = json.loads((HERE / "FROZEN_OBLIGATIONS_V1.json").read_text())
    predictions = json.loads((HERE / "FROZEN_PREDICTIONS_V1.json").read_text())
    aliases = {
        "AFFINE_SHARED_COEFFICIENT_RESPONSE": "AFFINE_SHARED_RESPONSE",
        "NON_AFFINE_UNARY_RESPONSE": "NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE",
        "AFFINE_RESPONSE_WITHOUT_LINK": "AFFINE_SHARED_RESPONSE",
    }
    expected = {
        row["obligation"]: aliases.get(row["property"].upper(), row["property"].upper())
        for row in predictions["predictions"]
    }
    expected["O0_POS"] = "PERSISTENT_THREE_CLASS_FUTURE_RESPONSE_QUOTIENT"
    recovered = {}
    residuals = {}
    for row in obligations["obligations"]:
        if row["interface"] == "one_symbol":
            recovered[row["id"]] = classify_static(row["table"], 1)
        elif row["interface"] == "two_symbol":
            recovered[row["id"]] = classify_static(row["table"], 2)
        else:
            recovered[row["id"]], residuals[row["id"]] = classify_sequence(row)
    return {
        "schema": "GMI833HIndependentOracleV1",
        "implementation": "source-separated direct formula and residual census",
        "imports_primary_checker": False,
        "recovered": recovered,
        "expected": expected,
        "sequence_residuals": residuals,
        "all_match": recovered == expected,
        "verdict": "GREEN" if recovered == expected else "RED",
    }


if __name__ == "__main__":
    print(canonical(build()), end="")
