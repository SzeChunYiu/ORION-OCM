from __future__ import annotations

import importlib.util
import pathlib
from fractions import Fraction
from itertools import product
from typing import Dict, Mapping

ROOT = pathlib.Path(__file__).resolve().parent
PREDICTOR_PATH = ROOT.parent / "gmi-capability-predictor-dev-v1" / "dev_predictor_v1.py"
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", PREDICTOR_PATH)
predictor_mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development predictor")
SPEC.loader.exec_module(predictor_mod)

AXES = predictor_mod.AXES
TARGETS = predictor_mod.TARGETS
CANNOT_IDENTIFY = predictor_mod.CANNOT_IDENTIFY

TASK_FAMILIES = {
    "TF_ALPHA": {
        "memory_margin": 3,
        "planning_margin": 4,
        "communication_margin": 3,
        "routing_margin": 3,
        "verification_margin": 3,
    },
    "TF_BETA": {
        "memory_margin": 7,
        "planning_margin": 9,
        "communication_margin": 5,
        "routing_margin": 8,
        "verification_margin": 10,
    },
}


def exact_oracle(margins: Mapping[str, int]) -> Dict[str, int]:
    return predictor_mod.capability_oracle(margins)


def build_raw_task(family_id: str, margins: Mapping[str, int]) -> Dict[str, object]:
    if family_id not in TASK_FAMILIES:
        raise ValueError("unknown task family")
    if set(margins) != set(AXES):
        raise ValueError("wrong margin coordinates")
    requirements = TASK_FAMILIES[family_id]
    capacities = {axis: requirements[axis] + int(margins[axis]) for axis in AXES}
    if any(value < 0 for value in capacities.values()):
        raise ValueError("negative capacity")
    derived = {axis: capacities[axis] - requirements[axis] for axis in AXES}
    if derived != dict(margins):
        raise AssertionError("margin derivation mismatch")
    return {
        "family_id": family_id,
        "requirements": dict(requirements),
        "capacities": capacities,
        "derived_margins": derived,
    }


def transfer_grid():
    for family_id in sorted(TASK_FAMILIES):
        for values in product((-2, 0, 2), repeat=len(AXES)):
            margins = dict(zip(AXES, values))
            yield build_raw_task(family_id, margins)


def audit_transfer() -> Dict[str, object]:
    predictor = predictor_mod.fit_registered_development_predictor()
    total = determinate = correct = abstentions = 0
    per_target = {target: {"determinate": 0, "correct": 0, "abstain": 0} for target in TARGETS}
    per_family = {family_id: {"total": 0, "determinate": 0, "correct": 0, "abstain": 0} for family_id in TASK_FAMILIES}

    for task in transfer_grid():
        margins = task["derived_margins"]
        predicted = predictor.predict_vector(margins)
        truth = exact_oracle(margins)
        family = per_family[task["family_id"]]
        for target in TARGETS:
            total += 1
            family["total"] += 1
            value = predicted[target]
            if value == CANNOT_IDENTIFY:
                abstentions += 1
                family["abstain"] += 1
                per_target[target]["abstain"] += 1
            else:
                determinate += 1
                family["determinate"] += 1
                per_target[target]["determinate"] += 1
                if value == truth[target]:
                    correct += 1
                    family["correct"] += 1
                    per_target[target]["correct"] += 1
    return {
        "task_families": len(TASK_FAMILIES),
        "members_per_family": 3 ** len(AXES),
        "total_cells": total,
        "determinate_cells": determinate,
        "correct_determinate_cells": correct,
        "incorrect_determinate_cells": determinate - correct,
        "abstention_cells": abstentions,
        "coverage_fraction": str(Fraction(determinate, total)),
        "abstention_fraction": str(Fraction(abstentions, total)),
        "determinate_accuracy_fraction": str(Fraction(correct, determinate)),
        "per_target": per_target,
        "per_family": per_family,
    }
