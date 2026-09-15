from __future__ import annotations

import importlib.util
import pathlib
from itertools import product
from typing import Dict, Mapping, Tuple, Union

ROOT = pathlib.Path(__file__).resolve().parent
PREDICTOR_PATH = ROOT.parent / "gmi-capability-predictor-dev-v1" / "dev_predictor_v1.py"
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", PREDICTOR_PATH)
predictor_mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development predictor")
SPEC.loader.exec_module(predictor_mod)

AXES: Tuple[str, ...] = predictor_mod.AXES
TARGETS: Tuple[str, ...] = predictor_mod.TARGETS
CANNOT_IDENTIFY = predictor_mod.CANNOT_IDENTIFY


def _validate_int(value: int, *, name: str, minimum: int | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


def _validated_point(point: Mapping[str, int]) -> Dict[str, int]:
    if set(point) != set(AXES):
        raise ValueError("point must contain exactly the registered signed-margin axes")
    out = dict(point)
    for axis in AXES:
        _validate_int(out[axis], name=axis)
    return out


def _validate_axis(axis: str) -> None:
    if axis not in AXES:
        raise ValueError("unknown signed-margin axis")


def reprice_fixed_spend(
    point: Mapping[str, int],
    *,
    axis: str,
    spend: int,
    old_price: int,
    new_price: int,
    requirement: int,
) -> Dict[str, int]:
    """Recompute one margin after a price change at fixed spend.

    Capacity is floor(spend / price), so the signed margin is
    floor(spend / price) - requirement. The baseline point must agree with
    the declared old-price economics or the counterfactual is refused.
    """
    out = _validated_point(point)
    _validate_axis(axis)
    _validate_int(spend, name="spend", minimum=0)
    _validate_int(old_price, name="old_price", minimum=1)
    _validate_int(new_price, name="new_price", minimum=1)
    _validate_int(requirement, name="requirement", minimum=0)
    expected_old_margin = spend // old_price - requirement
    if out[axis] != expected_old_margin:
        raise ValueError("baseline margin is inconsistent with old-price economics")
    out[axis] = spend // new_price - requirement
    return out


def ablate_capacity(
    point: Mapping[str, int], *, axis: str, lost_capacity: int
) -> Dict[str, int]:
    """Remove usable capacity while holding the requirement fixed."""
    out = _validated_point(point)
    _validate_axis(axis)
    _validate_int(lost_capacity, name="lost_capacity", minimum=0)
    out[axis] -= lost_capacity
    return out


def drift_requirement(
    point: Mapping[str, int], *, axis: str, requirement_delta: int
) -> Dict[str, int]:
    """Change the environmental requirement while holding capacity fixed.

    Positive delta means a harder environment; negative delta is relaxation.
    """
    out = _validated_point(point)
    _validate_axis(axis)
    _validate_int(requirement_delta, name="requirement_delta")
    out[axis] -= requirement_delta
    return out


def independent_oracle(point: Mapping[str, int]) -> Dict[str, int]:
    p = _validated_point(point)
    return {
        "memory_exact": int(p["memory_margin"] >= 0),
        "planning_exact": int(
            p["memory_margin"] >= 0 and p["planning_margin"] >= 0
        ),
        "coordination_exact": int(p["communication_margin"] >= 0),
        "verified_tool_exact": int(
            p["routing_margin"] >= 0 and p["verification_margin"] >= 0
        ),
    }


def predict(point: Mapping[str, int]) -> Dict[str, Union[int, str]]:
    return predictor_mod.fit_registered_development_predictor().predict_vector(
        _validated_point(point)
    )


def calibration_probe(radius: int = 2) -> Dict[str, int]:
    _validate_int(radius, name="radius", minimum=1)
    predictor = predictor_mod.fit_registered_development_predictor()
    determinate = 0
    abstentions = 0
    incorrect = 0
    total = 0
    for values in product(range(-radius, radius + 1), repeat=len(AXES)):
        point = dict(zip(AXES, values))
        oracle = independent_oracle(point)
        predicted = predictor.predict_vector(point)
        for target in TARGETS:
            total += 1
            value = predicted[target]
            if value == CANNOT_IDENTIFY:
                abstentions += 1
            else:
                determinate += 1
                if value != oracle[target]:
                    incorrect += 1
    return {
        "radius": radius,
        "total_cells": total,
        "determinate_cells": determinate,
        "abstention_cells": abstentions,
        "incorrect_determinate_cells": incorrect,
    }
