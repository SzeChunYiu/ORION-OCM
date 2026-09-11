"""Label-free exact acquisition over the common Stage D-v0 microbasis.

The target architecture class is never supplied to the learner. Frozen teaching rows
identify a semantic prediction/update target within the bounded expression class.
This is version-space / enumerative-synthesis calibration, not GMI novelty.
"""

from __future__ import annotations

import json

from micro_derivation_search import (
    PRED_ROWS,
    UPD_ROWS,
    enumerate_semantics,
    targets,
)

# Exact minimum-cardinality distinguishing row sets computed exhaustively over the
# registered size<=6 semantic classes before this acquisition receipt was frozen.
TEACHING_ROWS = {
    "NEURAL_LIKE_DISCRETE_THRESHOLD_LEARNER": {
        "prediction": [4, 5, 6, 7, 8],
        "update": [1, 8, 9, 16],
    },
    "SYMBOLIC_RULE_MICRO": {
        "prediction": [0, 2, 3, 4, 6, 9, 11],
        "update": [1, 4, 17, 20, 21],
    },
    "EVIDENCE_ACCUMULATOR_MICRO": {
        "prediction": [0, 3, 5, 6, 8, 11],
        "update": [0, 1, 7, 14, 15, 16],
    },
    "PROGRAMMATIC_REGISTER_MICRO": {
        "prediction": [0, 1, 3, 4, 6, 10],
        "update": [0, 5, 11, 12, 19, 23],
    },
}


def consistent(signatures, target_signature, row_ids):
    return [
        signature
        for signature in signatures
        if all(signature[row] == target_signature[row] for row in row_ids)
    ]


def run():
    prediction_semantics = enumerate_semantics(PRED_ROWS, ("s", "x0", "x1"), 6)
    update_semantics = enumerate_semantics(UPD_ROWS, ("s", "x0", "x1", "l"), 6)

    result = {}
    for name, (predict_fn, update_fn) in targets().items():
        pred_target = tuple(predict_fn(*row) for row in PRED_ROWS)
        update_target = tuple(update_fn(*row) for row in UPD_ROWS)
        pred_rows = TEACHING_ROWS[name]["prediction"]
        update_rows = TEACHING_ROWS[name]["update"]

        pred_consistent = consistent(prediction_semantics, pred_target, pred_rows)
        update_consistent = consistent(update_semantics, update_target, update_rows)

        pred_exact = prediction_semantics[pred_target]
        update_exact = update_semantics[update_target]
        result[name] = {
            "architecture_label_visible_to_learner": False,
            "prediction_teaching_examples": len(pred_rows),
            "prediction_total_rows": len(PRED_ROWS),
            "prediction_consistent_semantic_classes": len(pred_consistent),
            "prediction_recovered_expression": pred_exact[1],
            "update_teaching_examples": len(update_rows),
            "update_total_rows": len(UPD_ROWS),
            "update_consistent_semantic_classes": len(update_consistent),
            "update_recovered_expression": update_exact[1],
            "exact_target_semantics_recovered": (
                pred_consistent == [pred_target] and update_consistent == [update_target]
            ),
        }

    return {
        "schema": "BlindMicroAcquisitionV0",
        "basis": "same frozen common microbasis as EXACT_MICRO_DERIVATIONS_V0",
        "selection": "exact version-space elimination over size<=6 semantic classes",
        "targets": result,
        "all_targets_exactly_identified": all(
            row["exact_target_semantics_recovered"] for row in result.values()
        ),
        "terminal": "LABEL_FREE_MICRO_D2_ACQUISITION_EXACT__ENUMERATIVE_SYNTHESIS_PARENT_SUFFICIENT",
        "claim_boundary": (
            "Architecture labels are absent from acquisition, but teaching rows were selected "
            "with exact target knowledge to identify the target concept within the bounded class. "
            "This is a teaching-dimension/version-space/program-synthesis calibration, not natural "
            "morphogenesis and not a general D2 result."
        ),
    }


def main():
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
