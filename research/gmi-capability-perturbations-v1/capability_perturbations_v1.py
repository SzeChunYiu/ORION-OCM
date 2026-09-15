from __future__ import annotations

import importlib.util
import pathlib
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


def _require_int(value: int, name: str, *, minimum: int | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


def capability_oracle(point: Mapping[str, int]) -> Dict[str, int]:
    _validate_point(point)
    return predictor_mod.capability_oracle(point)


def reprice_margin(*, spend: int, old_price: int, new_price: int, requirement: int) -> tuple[int, int]:
    _require_int(spend, "spend", minimum=0)
    _require_int(old_price, "old_price", minimum=1)
    _require_int(new_price, "new_price", minimum=1)
    _require_int(requirement, "requirement", minimum=0)
    old_margin = spend // old_price - requirement
    new_margin = spend // new_price - requirement
    return old_margin, new_margin


def ablate(point: Mapping[str, int], axis: str, removed_capacity: int) -> Dict[str, int]:
    _validate_point(point)
    _require_int(removed_capacity, "removed_capacity", minimum=0)
    if axis not in AXES:
        raise ValueError("invalid ablation axis")
    out = dict(point)
    out[axis] -= removed_capacity
    return out


def drift_requirement(point: Mapping[str, int], axis: str, added_requirement: int) -> Dict[str, int]:
    _validate_point(point)
    _require_int(added_requirement, "added_requirement", minimum=0)
    if axis not in AXES:
        raise ValueError("invalid drift axis")
    out = dict(point)
    out[axis] -= added_requirement
    return out


def apply_repricing(point: Mapping[str, int], axis: str, *, spend: int, old_price: int, new_price: int, requirement: int) -> Dict[str, int]:
    _validate_point(point)
    if axis not in AXES:
        raise ValueError("unknown axis")
    old_margin, new_margin = reprice_margin(
        spend=spend, old_price=old_price, new_price=new_price, requirement=requirement
    )
    if point[axis] != old_margin:
        raise ValueError("base point does not match declared old price/spend/requirement")
    out = dict(point)
    out[axis] = new_margin
    return out


def build_predictor():
    return predictor_mod.fit_registered_development_predictor()


def predict(point: Mapping[str, int]):
    _validate_point(point)
    return build_predictor().predict_vector(point)


def identification_certificate(point: Mapping[str, int], target: str) -> Dict[str, object]:
    """Return the exact monotone-witness certificate for one target.

    A positive development world below the query forces 1 by monotonicity.
    A negative development world above the query forces 0. If neither exists,
    the registered development corpus does not identify the target and the only
    admissible output is CANNOT_IDENTIFY.
    """
    _validate_point(point)
    if target not in TARGETS:
        raise ValueError("unknown capability target")

    def leq(left: Mapping[str, int], right: Mapping[str, int]) -> bool:
        return all(left[axis] <= right[axis] for axis in AXES)

    positive_below = False
    negative_above = False
    for record in predictor_mod.generate_development_worlds():
        rp = {axis: int(record[axis]) for axis in AXES}
        value = int(record["capabilities"][target])
        if value == 1 and leq(rp, point):
            positive_below = True
        if value == 0 and leq(point, rp):
            negative_above = True

    if positive_below and negative_above:
        raise AssertionError("monotone witness conflict")
    if positive_below:
        prediction = 1
    elif negative_above:
        prediction = 0
    else:
        prediction = CANNOT_IDENTIFY
    return {
        "positive_below_witness_exists": positive_below,
        "negative_above_witness_exists": negative_above,
        "prediction": prediction,
    }


def calibration_probe(radius: int = 2) -> Dict[str, int]:
    """Exhaustively score predictor identifiability on [-radius, radius]^5.

    Determinate outputs are checked against the independent exact capability
    oracle. Abstentions remain explicit and are never coerced to binary labels.
    """
    _require_int(radius, "radius", minimum=1)
    predictor = build_predictor()
    total = 0
    determinate = 0
    abstentions = 0
    incorrect = 0
    for values in product(range(-radius, radius + 1), repeat=len(AXES)):
        point = dict(zip(AXES, values))
        truth = capability_oracle(point)
        predicted = predictor.predict_vector(point)
        for target in TARGETS:
            total += 1
            value = predicted[target]
            if value == CANNOT_IDENTIFY:
                abstentions += 1
            else:
                determinate += 1
                if value != truth[target]:
                    incorrect += 1
    return {
        "radius": radius,
        "total_cells": total,
        "determinate_cells": determinate,
        "abstention_cells": abstentions,
        "incorrect_determinate_cells": incorrect,
    }


def _validate_point(point: Mapping[str, int]) -> None:
    if set(point) != set(AXES):
        raise ValueError("point must contain exactly the registered margins")
    for value in point.values():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("margins must be integer")
