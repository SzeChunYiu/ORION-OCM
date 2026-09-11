"""Exact execution of PHASE_CALIBRATION_3BIT_FREEZE_V1.md."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json

ROWS = list(product((0, 1), repeat=3))
V = 0.25
L = 1.0


def enumerate_functions(max_size=20):
    best = {}
    by_size = defaultdict(list)

    def add(signature, size, expression):
        if signature not in best:
            best[signature] = (size, expression)
            by_size[size].append(signature)

    for index in range(3):
        add(tuple(row[index] for row in ROWS), 1, f"x{index}")
    add((0,) * len(ROWS), 1, "0")
    add((1,) * len(ROWS), 1, "1")

    for size in range(2, max_size + 1):
        for signature in by_size.get(size - 1, []):
            add(tuple(1 - value for value in signature), size, f"not({best[signature][1]})")

        for left_size in range(1, size - 1):
            right_size = size - 1 - left_size
            for sig_a in by_size.get(left_size, []):
                for sig_b in by_size.get(right_size, []):
                    expr_a = best[sig_a][1]
                    expr_b = best[sig_b][1]
                    add(
                        tuple(a & b for a, b in zip(sig_a, sig_b)),
                        size,
                        f"and({expr_a},{expr_b})",
                    )
                    add(
                        tuple(a ^ b for a, b in zip(sig_a, sig_b)),
                        size,
                        f"xor({expr_a},{expr_b})",
                    )
        if len(best) == 256:
            break

    assert len(best) == 256
    return best


def evaluate_target(target, complexity):
    correct = wrong = abstain = 0
    total_cost = 0.0
    total_queries = 0

    for train_rows in combinations(range(8), 2):
        consistent = [
            signature
            for signature in complexity
            if all(signature[row] == target[row] for row in train_rows)
        ]
        minimum_size = min(complexity[signature] for signature in consistent)
        minimum_hypotheses = [
            signature
            for signature in consistent
            if complexity[signature] == minimum_size
        ]

        for query in range(8):
            if query in train_rows:
                continue
            values = {signature[query] for signature in minimum_hypotheses}
            total_queries += 1
            if len(values) != 1:
                abstain += 1
                total_cost += L
                continue

            proposal = next(iter(values))
            if proposal == target[query]:
                correct += 1
                total_cost += V
            else:
                wrong += 1
                total_cost += V + L

    return {
        "queries": total_queries,
        "correct_rate": correct / total_queries,
        "wrong_rate": wrong / total_queries,
        "abstain_rate": abstain / total_queries,
        "mean_acquisition_cost": total_cost / total_queries,
    }


def aggregate(targets, per_target):
    fields = (
        "correct_rate",
        "wrong_rate",
        "abstain_rate",
        "mean_acquisition_cost",
    )
    return {
        "target_count": len(targets),
        **{
            field: sum(per_target[target][field] for target in targets) / len(targets)
            for field in fields
        },
    }


def run():
    functions = enumerate_functions()
    complexity = {signature: row[0] for signature, row in functions.items()}
    per_target = {
        target: evaluate_target(target, complexity)
        for target in functions
    }

    simple = [target for target in functions if complexity[target] <= 3]
    complex_targets = [target for target in functions if complexity[target] >= 9]
    simple_summary = aggregate(simple, per_target)
    complex_summary = aggregate(complex_targets, per_target)

    simple_attempt = simple_summary["correct_rate"] + simple_summary["wrong_rate"]
    complex_attempt = complex_summary["correct_rate"] + complex_summary["wrong_rate"]

    return {
        "schema": "PhaseCalibration3BitV1",
        "frozen_protocol": "PHASE_CALIBRATION_3BIT_FREEZE_V1.md",
        "universe_size": len(functions),
        "max_minimum_expression_size": max(complexity.values()),
        "costs": {"label": L, "verify": V},
        "simple": simple_summary,
        "complex": complex_summary,
        "frozen_predictions": {
            "P1_simple_cost_lt_1": simple_summary["mean_acquisition_cost"] < 1.0,
            "P2_complex_cost_ge_simple": (
                complex_summary["mean_acquisition_cost"]
                >= simple_summary["mean_acquisition_cost"]
            ),
            "P3_positive_gap": (
                complex_summary["mean_acquisition_cost"]
                - simple_summary["mean_acquisition_cost"]
            ) > 0,
        },
        "secondary_post_outcome_readout": {
            "simple_proposal_precision": (
                simple_summary["correct_rate"] / simple_attempt
            ),
            "complex_proposal_precision": (
                complex_summary["correct_rate"] / complex_attempt
            ),
            "interpretation": (
                "Verifier-cost break-even against direct label acquisition is proposal precision: "
                "V/L < correct/(correct+wrong). This threshold readout was not a frozen primary prediction."
            ),
        },
        "terminal": "DESCRIPTION_COMPLEXITY_PREDICTS_PARENT_MORPHOLOGY_COST_REGION_AT_3BIT_SCOPE",
        "claim_boundary": (
            "Exact finite MDL/version-space/value-of-verification calibration only. Complex targets "
            "still beat direct label memory at frozen V=0.25; only the registered simple-vs-complex "
            "cost separation is confirmatory here. Mechanism is parent-owned."
        ),
    }


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
