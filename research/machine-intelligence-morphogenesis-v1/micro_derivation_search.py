"""Exact semantic search for tiny cross-paradigm Track-B derivations.

Calibration only. The basis deliberately contains no architecture-labelled primitives
such as NEURON, PRODUCTION_RULE, BAYES_UPDATE, PROGRAM_INTERPRETER or BACKPROP.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

D = (0, 1, 2)
PRED_ROWS = [(s, x0, x1) for s in D for x0 in (0, 1) for x1 in (0, 1)]
UPD_ROWS = [
    (s, x0, x1, label)
    for s in D
    for x0 in (0, 1)
    for x1 in (0, 1)
    for label in (0, 1)
]


def enumerate_semantics(rows, variable_names, max_size):
    best = {}
    by_size = defaultdict(list)

    def add(signature, size, expression):
        if signature not in best:
            best[signature] = (size, expression)
            by_size[size].append(signature)

    for index, name in enumerate(variable_names):
        add(tuple(row[index] for row in rows), 1, name)
    for constant in D:
        add((constant,) * len(rows), 1, str(constant))

    for size in range(2, max_size + 1):
        # Generic unary local transforms.
        for sig_a in tuple(by_size[size - 1]):
            expr_a = best[sig_a][1]
            unary = (
                (tuple(1 if x == 0 else 0 for x in sig_a), f"is0({expr_a})"),
                (tuple(1 if x == 2 else 0 for x in sig_a), f"is2({expr_a})"),
                (tuple(min(2, x + 1) for x in sig_a), f"inc({expr_a})"),
                (tuple(max(0, x - 1) for x in sig_a), f"dec({expr_a})"),
            )
            for signature, expression in unary:
                add(signature, size, expression)

        # Generic bounded composition transforms.
        for left_size in range(1, size - 1):
            right_size = size - 1 - left_size
            if right_size < 1:
                continue
            for sig_a in tuple(by_size[left_size]):
                expr_a = best[sig_a][1]
                for sig_b in tuple(by_size[right_size]):
                    expr_b = best[sig_b][1]
                    add(
                        tuple(min(2, a + b) for a, b in zip(sig_a, sig_b)),
                        size,
                        f"add({expr_a},{expr_b})",
                    )
                    add(
                        tuple(min(a, b) for a, b in zip(sig_a, sig_b)),
                        size,
                        f"min({expr_a},{expr_b})",
                    )

        # Generic conditional composition.
        for cond_size in range(1, size - 2):
            for yes_size in range(1, size - 1 - cond_size):
                no_size = size - 1 - cond_size - yes_size
                if no_size < 1:
                    continue
                for sig_c in tuple(by_size[cond_size]):
                    expr_c = best[sig_c][1]
                    for sig_a in tuple(by_size[yes_size]):
                        expr_a = best[sig_a][1]
                        for sig_b in tuple(by_size[no_size]):
                            expr_b = best[sig_b][1]
                            add(
                                tuple(
                                    yes if cond > 0 else no
                                    for cond, yes, no in zip(sig_c, sig_a, sig_b)
                                ),
                                size,
                                f"ite({expr_c},{expr_a},{expr_b})",
                            )

    return best


def targets():
    def neural_predict(s, x0, x1):
        # Tiny discrete parametric threshold unit: morphology-level analogy only.
        return 1 if min(2, s + x0 + x1) == 2 else 0

    def neural_update(s, x0, x1, label):
        # Label-directed bounded parameter update; not full gradient descent.
        return min(2, s + 1) if label else max(0, s - 1)

    def symbolic_predict(s, x0, x1):
        # State s acts as an enabled-rule flag; x0 is the condition.
        return min(s, x0)

    def symbolic_update(s, x0, x1, label):
        return 1 if min(x0, label) > 0 else s

    def evidence_predict(s, x0, x1):
        # Explicit evidence-count threshold. This is not a full Bayesian posterior.
        return 1 if s > 0 else 0

    def evidence_update(s, x0, x1, label):
        return min(2, s + label)

    def program_predict(s, x0, x1):
        # Explicit conditional register read.
        return s if x0 else x1

    def program_update(s, x0, x1, label):
        # Explicit conditional register write.
        return label if x0 else s

    return {
        "NEURAL_LIKE_DISCRETE_THRESHOLD_LEARNER": (neural_predict, neural_update),
        "SYMBOLIC_RULE_MICRO": (symbolic_predict, symbolic_update),
        "EVIDENCE_ACCUMULATOR_MICRO": (evidence_predict, evidence_update),
        "PROGRAMMATIC_REGISTER_MICRO": (program_predict, program_update),
    }


def run():
    prediction_semantics = enumerate_semantics(PRED_ROWS, ("s", "x0", "x1"), 6)
    update_semantics = enumerate_semantics(UPD_ROWS, ("s", "x0", "x1", "l"), 6)

    found = {}
    for name, (predict_fn, update_fn) in targets().items():
        pred_signature = tuple(predict_fn(*row) for row in PRED_ROWS)
        update_signature = tuple(update_fn(*row) for row in UPD_ROWS)
        pred = prediction_semantics.get(pred_signature)
        upd = update_semantics.get(update_signature)
        found[name] = {
            "prediction": None if pred is None else {"size": pred[0], "expression": pred[1]},
            "update": None if upd is None else {"size": upd[0], "expression": upd[1]},
        }

    return {
        "schema": "ExactMicroDerivationV0",
        "domain": {"state": list(D), "x0": [0, 1], "x1": [0, 1], "label": [0, 1]},
        "basis": {
            "leaves": ["state/input/label", "constants_0_1_2"],
            "unary": ["is0", "is2", "inc_saturating", "dec_saturating"],
            "binary": ["add_saturating", "min"],
            "ternary": ["if_then_else"],
            "forbidden_architecture_macros": [
                "NEURON",
                "PRODUCTION_RULE",
                "BAYES_UPDATE",
                "PROGRAM_INTERPRETER",
                "ATTENTION",
                "BACKPROP",
            ],
        },
        "search": {
            "prediction_max_expression_size": 6,
            "update_max_expression_size": 6,
            "prediction_semantic_classes": len(prediction_semantics),
            "update_semantic_classes": len(update_semantics),
        },
        "targets": found,
        "terminal": "COMMON_MICROBASIS_D1_COMPILES_FOUR_TOY_MORPHOLOGIES__UNIVERSALITY_NULL_OPEN",
        "claim_boundary": (
            "Finite bounded D1 compilation only. Targets are tiny analogues, not full neural, "
            "Bayesian, symbolic or program-learning systems. The basis is a small generic program "
            "algebra, so UNIVERSAL_COMPUTATION_ONLY/PARENT_FORMALISM_SUFFICIENT remain live nulls."
        ),
    }


def main():
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
