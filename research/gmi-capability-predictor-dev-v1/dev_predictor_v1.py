from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple, Union

AXES: Tuple[str, ...] = (
    "memory_margin",
    "planning_margin",
    "communication_margin",
    "routing_margin",
    "verification_margin",
)
TARGETS: Tuple[str, ...] = (
    "memory_exact",
    "planning_exact",
    "coordination_exact",
    "verified_tool_exact",
)
FORBIDDEN_FIELDS = {
    "family_name",
    "architecture_name",
    "specimen_id",
    "source_ref",
    "held_family",
    "heldout_outcome",
    "test_outcome",
}
CANNOT_IDENTIFY = "CANNOT_IDENTIFY"


def capability_oracle(point: Mapping[str, int]) -> Dict[str, int]:
    _validate_point(point)
    return {
        "memory_exact": int(point["memory_margin"] >= 0),
        "planning_exact": int(
            point["memory_margin"] >= 0 and point["planning_margin"] >= 0
        ),
        "coordination_exact": int(point["communication_margin"] >= 0),
        "verified_tool_exact": int(
            point["routing_margin"] >= 0 and point["verification_margin"] >= 0
        ),
    }


def generate_development_worlds() -> List[Dict[str, object]]:
    worlds: List[Dict[str, object]] = []
    for values in product((-1, 0, 1), repeat=len(AXES)):
        point = dict(zip(AXES, values))
        worlds.append({**point, "capabilities": capability_oracle(point)})
    return worlds


def _validate_point(point: Mapping[str, int]) -> None:
    if set(point) != set(AXES):
        raise ValueError("query point must contain exactly the five registered axes")
    for axis in AXES:
        value = point[axis]
        if not isinstance(value, int):
            raise ValueError(f"{axis} must be an integer margin")


def _point_from_record(record: Mapping[str, object]) -> Dict[str, int]:
    return {axis: int(record[axis]) for axis in AXES}


def _leq(a: Mapping[str, int], b: Mapping[str, int]) -> bool:
    return all(a[axis] <= b[axis] for axis in AXES)


def validate_development_record(record: Mapping[str, object]) -> None:
    forbidden = set(record).intersection(FORBIDDEN_FIELDS)
    if forbidden:
        raise ValueError(f"forbidden fit fields present: {sorted(forbidden)}")
    expected = set(AXES) | {"capabilities"}
    if set(record) != expected:
        raise ValueError("development record must contain exactly registered fit fields")
    point = _point_from_record(record)
    _validate_point(point)
    caps = record["capabilities"]
    if not isinstance(caps, Mapping) or set(caps) != set(TARGETS):
        raise ValueError("capabilities must contain exactly the registered targets")
    for target in TARGETS:
        if caps[target] not in (0, 1):
            raise ValueError(f"{target} must be binary")


@dataclass(frozen=True)
class MonotoneDevelopmentPredictor:
    records: Tuple[Mapping[str, object], ...]

    @classmethod
    def fit(cls, records: Iterable[Mapping[str, object]]) -> "MonotoneDevelopmentPredictor":
        frozen = tuple(dict(r) for r in records)
        if not frozen:
            raise ValueError("at least one development world is required")
        for record in frozen:
            validate_development_record(record)
        cls._assert_monotone(frozen)
        return cls(frozen)

    @staticmethod
    def _assert_monotone(records: Sequence[Mapping[str, object]]) -> None:
        for left in records:
            lp = _point_from_record(left)
            lc = left["capabilities"]
            for right in records:
                rp = _point_from_record(right)
                if not _leq(lp, rp):
                    continue
                rc = right["capabilities"]
                for target in TARGETS:
                    if int(lc[target]) > int(rc[target]):
                        raise ValueError(
                            f"non-monotone development corpus for {target}: {lp} -> {rp}"
                        )

    def predict_one(self, point: Mapping[str, int], target: str) -> Union[int, str]:
        _validate_point(point)
        if target not in TARGETS:
            raise ValueError("unknown capability target")

        positive_below = False
        negative_above = False
        for record in self.records:
            rp = _point_from_record(record)
            value = int(record["capabilities"][target])
            if value == 1 and _leq(rp, point):
                positive_below = True
            if value == 0 and _leq(point, rp):
                negative_above = True

        if positive_below and negative_above:
            raise AssertionError("monotone envelopes conflict")
        if positive_below:
            return 1
        if negative_above:
            return 0
        return CANNOT_IDENTIFY

    def predict_vector(self, point: Mapping[str, int]) -> Dict[str, Union[int, str]]:
        return {target: self.predict_one(point, target) for target in TARGETS}


def fit_registered_development_predictor() -> MonotoneDevelopmentPredictor:
    return MonotoneDevelopmentPredictor.fit(generate_development_worlds())
