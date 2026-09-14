from __future__ import annotations

import importlib.util
import pathlib
from typing import Dict, Mapping

ROOT = pathlib.Path(__file__).resolve().parent
PREDICTOR_PATH = ROOT.parent / "gmi-capability-predictor-dev-v1" / "dev_predictor_v1.py"
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", PREDICTOR_PATH)
predictor_mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development predictor")
SPEC.loader.exec_module(predictor_mod)

AXES = predictor_mod.AXES


def capability_oracle(point: Mapping[str, int]) -> Dict[str, int]:
    return predictor_mod.capability_oracle(point)


def reprice_margin(*, spend: int, old_price: int, new_price: int, requirement: int) -> tuple[int, int]:
    if spend < 0 or old_price <= 0 or new_price <= 0 or requirement < 0:
        raise ValueError("invalid repricing parameters")
    old_margin = spend // old_price - requirement
    new_margin = spend // new_price - requirement
    return old_margin, new_margin


def ablate(point: Mapping[str, int], axis: str, removed_capacity: int) -> Dict[str, int]:
    _validate_point(point)
    if axis not in AXES or removed_capacity < 0:
        raise ValueError("invalid ablation")
    out = dict(point)
    out[axis] -= removed_capacity
    return out


def drift_requirement(point: Mapping[str, int], axis: str, added_requirement: int) -> Dict[str, int]:
    _validate_point(point)
    if axis not in AXES or added_requirement < 0:
        raise ValueError("invalid drift")
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


def predict(point: Mapping[str, int]):
    _validate_point(point)
    predictor = predictor_mod.fit_registered_development_predictor()
    return predictor.predict_vector(point)


def _validate_point(point: Mapping[str, int]) -> None:
    if set(point) != set(AXES):
        raise ValueError("point must contain exactly the registered margins")
    for value in point.values():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("margins must be integer")
