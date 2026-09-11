#!/usr/bin/env python3
"""Exact finite witness: current behavior equivalence != developmental equivalence.

Two tiny learners have identical pre-experience input/output behavior over the
complete finite input set {0,1}. They differ only in the registered update law.
After the same supervised event (x=1, y=1), their behaviors diverge.

This proves only the finite counterexample needed for GMI-T4. It is not an
intelligence or morphology-novelty result.
"""

from dataclasses import dataclass
from typing import Literal, Tuple

UpdateRule = Literal["NO_OP", "SUPERVISED_MEMORIZE"]


@dataclass(frozen=True)
class TinyLearner:
    table: Tuple[int, int]
    update_rule: UpdateRule

    def predict(self, x: int) -> int:
        if x not in (0, 1):
            raise ValueError("registered input universe is {0,1}")
        return self.table[x]

    def truth_table(self) -> tuple[int, int]:
        return (self.predict(0), self.predict(1))

    def update(self, x: int, y: int) -> "TinyLearner":
        if x not in (0, 1) or y not in (0, 1):
            raise ValueError("registered supervised event is binary")
        if self.update_rule == "NO_OP":
            return self
        values = list(self.table)
        values[x] = y
        return TinyLearner(tuple(values), self.update_rule)


def build_witness() -> dict:
    static = TinyLearner((0, 0), "NO_OP")
    adaptive = TinyLearner((0, 0), "SUPERVISED_MEMORIZE")
    event = (1, 1)

    pre_static = static.truth_table()
    pre_adaptive = adaptive.truth_table()
    post_static = static.update(*event).truth_table()
    post_adaptive = adaptive.update(*event).truth_table()

    assert pre_static == pre_adaptive
    assert post_static != post_adaptive

    return {
        "terminal": "CURRENT_BEHAVIOR_EQUIVALENCE_DOES_NOT_IMPLY_DEVELOPMENTAL_EQUIVALENCE_EXACT",
        "input_universe": [0, 1],
        "experience": {"x": event[0], "label": event[1]},
        "machine_static": {
            "update_rule": static.update_rule,
            "pre_behavior": list(pre_static),
            "post_behavior": list(post_static),
        },
        "machine_adaptive": {
            "update_rule": adaptive.update_rule,
            "pre_behavior": list(pre_adaptive),
            "post_behavior": list(post_adaptive),
        },
        "exact_claim": (
            "The machines are extensionally identical on every input in the "
            "registered finite universe before experience but diverge after the "
            "same registered experience because their update laws differ."
        ),
        "claim_boundary": (
            "Finite counterexample only; does not establish a universal taxonomy "
            "of intelligence morphologies."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_witness(), indent=2, sort_keys=True))
