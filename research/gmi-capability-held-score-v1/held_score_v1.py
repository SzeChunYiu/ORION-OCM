from __future__ import annotations

import hashlib
import json
import pathlib
from fractions import Fraction
from typing import Dict, Mapping

ROOT = pathlib.Path(__file__).resolve().parent
FREEZE_PATH = ROOT.parent / "gmi-capability-held-freeze-v1" / "HELD_FAMILY_PREDICTIONS_V1.json"
EXPECTED_FREEZE_DIGEST = "cee4b92e9ca524d8d57d6f60c8fe529529216f13602a8a1f1b633a8c8fa3106a"
CANNOT_IDENTIFY = "CANNOT_IDENTIFY"
TARGETS = (
    "memory_exact",
    "planning_exact",
    "coordination_exact",
    "verified_tool_exact",
)


def _canonical_digest(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_frozen_custody(manifest: Mapping[str, object]) -> None:
    if manifest.get("freeze_digest") != EXPECTED_FREEZE_DIGEST:
        raise ValueError("scoring refused: frozen receipt digest field changed")
    without_digest = dict(manifest)
    without_digest.pop("freeze_digest", None)
    if _canonical_digest(without_digest) != EXPECTED_FREEZE_DIGEST:
        raise ValueError("scoring refused: frozen receipt content changed")
    if manifest.get("status") != "FROZEN_NOT_YET_SCORED" or manifest.get("outcomes_present") is not False:
        raise ValueError("scoring refused: freeze is not a clean preregistration")


def held_oracle(point: Mapping[str, int]) -> Dict[str, int]:
    """Independent exact oracle from the registered obligation inequalities.

    This function does not import or call the fitted predictor.
    """
    required = {
        "memory_margin",
        "planning_margin",
        "communication_margin",
        "routing_margin",
        "verification_margin",
    }
    if set(point) != required:
        raise ValueError("held point has wrong coordinate set")
    for value in point.values():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("held margins must be integers")
    return {
        "memory_exact": int(point["memory_margin"] >= 0),
        "planning_exact": int(point["memory_margin"] >= 0 and point["planning_margin"] >= 0),
        "coordination_exact": int(point["communication_margin"] >= 0),
        "verified_tool_exact": int(point["routing_margin"] >= 0 and point["verification_margin"] >= 0),
    }


def load_frozen_manifest() -> Dict[str, object]:
    manifest = json.loads(FREEZE_PATH.read_text())
    validate_frozen_custody(manifest)
    return manifest


def score_frozen_manifest(manifest: Mapping[str, object]) -> Dict[str, object]:
    validate_frozen_custody(manifest)

    total = 0
    determinate = 0
    correct = 0
    incorrect = 0
    abstentions = 0
    family_rows = []

    for family in manifest["families"]:
        family_determinate = 0
        family_correct = 0
        strengths = set()
        weaknesses = set()
        member_rows = []
        for member in family["members"]:
            oracle = held_oracle(member["descriptor_margins"])
            frozen = member["frozen_prediction"]
            cell_rows = {}
            for target in TARGETS:
                total += 1
                prediction = frozen[target]
                truth = oracle[target]
                if prediction == CANNOT_IDENTIFY:
                    abstentions += 1
                    verdict = "ABSTAIN"
                else:
                    determinate += 1
                    family_determinate += 1
                    if prediction == truth:
                        correct += 1
                        family_correct += 1
                        verdict = "CORRECT"
                    else:
                        incorrect += 1
                        verdict = "INCORRECT"
                    if prediction == 1:
                        strengths.add(target)
                    elif prediction == 0:
                        weaknesses.add(target)
                cell_rows[target] = {
                    "frozen_prediction": prediction,
                    "oracle": truth,
                    "verdict": verdict,
                }
            member_rows.append({"member_id": member["member_id"], "cells": cell_rows})
        family_rows.append({
            "family_id": family["family_id"],
            "determinate_cells": family_determinate,
            "correct_determinate_cells": family_correct,
            "predicted_strengths": sorted(strengths),
            "predicted_weaknesses": sorted(weaknesses),
            "members": member_rows,
        })

    if determinate + abstentions != total:
        raise AssertionError("coverage accounting mismatch")
    return {
        "freeze_digest": EXPECTED_FREEZE_DIGEST,
        "total_cells": total,
        "determinate_cells": determinate,
        "correct_determinate_cells": correct,
        "incorrect_determinate_cells": incorrect,
        "abstention_cells": abstentions,
        "coverage_fraction": f"{Fraction(determinate, total).numerator}/{Fraction(determinate, total).denominator}",
        "determinate_accuracy_fraction": (
            f"{Fraction(correct, determinate).numerator}/{Fraction(correct, determinate).denominator}"
            if determinate else "UNDEFINED"
        ),
        "families": family_rows,
    }


def build_score_receipt() -> Dict[str, object]:
    score = score_frozen_manifest(load_frozen_manifest())
    return {
        "schema_version": "1.0",
        "issue": 602,
        "section": "F4 capability predictor",
        "ledger_rows": [
            "Predict known family strengths and weaknesses.",
            "Predict failure modes before testing.",
        ],
        "scope": "prospectively frozen exact capability predictions for six opaque held structural families outside the development cube",
        "assumptions": [
            "the freeze digest was committed before this scoring artifact",
            "the held oracle is computed independently from exact registered obligation inequalities and does not call the fitted predictor",
            "CANNOT_IDENTIFY is scored as abstention rather than success or failure",
            "claims concern the six registered structural families, not all named architecture families"
        ],
        "evidence_class": ["P2"],
        "claim_ceiling": "G3",
        "strongest_parent": "prospective holdout evaluation with selective prediction / abstention",
        "negative_twin": "score an edited or post-outcome freeze; digest custody must refuse it",
        "nearest_counterexample": "perfect accuracy on determinate cells with zero or trivial coverage would not establish a useful predictor; coverage is therefore reported separately",
        "falsifier": "Any determinate frozen prediction disagrees with the independent held oracle, the freeze digest changes, or abstentions are counted as correct predictions.",
        "status": "PASS" if score["incorrect_determinate_cells"] == 0 and score["determinate_cells"] > 0 else "FAIL",
        "score": score,
    }


if __name__ == "__main__":
    print(json.dumps(build_score_receipt(), indent=2, sort_keys=True))
