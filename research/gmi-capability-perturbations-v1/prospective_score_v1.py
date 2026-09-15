from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FREEZE_COMMIT = "0fbd39d4e4848cd18d56552725e6c87412d041bf"
FREEZE_PATH = HERE / "FROZEN_CASES_V1.json"
CLAIM = "PROSPECTIVE_CAPABILITY_PERTURBATIONS_VALIDATED_AT_REGISTERED_SYNTHETIC_SCOPE"
CANNOT_IDENTIFY = "CANNOT_IDENTIFY"
EXPECTED_AXES = (
    "memory_margin",
    "planning_margin",
    "communication_margin",
    "routing_margin",
    "verification_margin",
)
EXPECTED_TARGETS = (
    "memory_exact",
    "planning_exact",
    "coordination_exact",
    "verified_tool_exact",
)


def load_freeze(path: Path = FREEZE_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _point_dict(values: Sequence[int]) -> Dict[str, int]:
    if len(values) != len(EXPECTED_AXES):
        raise ValueError("held point must contain exactly five registered margins")
    point: Dict[str, int] = {}
    for axis, value in zip(EXPECTED_AXES, values):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("held margins must be non-boolean integers")
        point[axis] = value
    return point


def independent_oracle(point: Mapping[str, int]) -> Dict[str, int]:
    if tuple(point) != EXPECTED_AXES:
        raise ValueError("independent oracle received wrong axis order")
    return {
        "memory_exact": int(point["memory_margin"] >= 0),
        "planning_exact": int(point["memory_margin"] >= 0 and point["planning_margin"] >= 0),
        "coordination_exact": int(point["communication_margin"] >= 0),
        "verified_tool_exact": int(point["routing_margin"] >= 0 and point["verification_margin"] >= 0),
    }


def _case_map(freeze: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    rows = freeze.get("cases")
    if not isinstance(rows, list):
        raise ValueError("freeze cases must be a list")
    out: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("id"), str):
            raise ValueError("malformed frozen case")
        case_id = str(row["id"])
        if case_id in out:
            raise ValueError("duplicate frozen case id")
        out[case_id] = row
    return out


def validate_freeze(freeze: Mapping[str, Any]) -> None:
    if freeze.get("schema") != "GMI_CAPABILITY_PERTURBATION_FREEZE_V1":
        raise ValueError("freeze schema mismatch")
    if freeze.get("issue") != 784 or freeze.get("parent_issue") != 602:
        raise ValueError("freeze issue identity mismatch")
    if freeze.get("claim_ceiling") != CLAIM:
        raise ValueError("freeze claim ceiling mismatch")
    if tuple(freeze.get("axis_order", ())) != EXPECTED_AXES:
        raise ValueError("freeze axis order mismatch")
    if tuple(freeze.get("target_order", ())) != EXPECTED_TARGETS:
        raise ValueError("freeze target order mismatch")
    if freeze.get("cannot_identify") != CANNOT_IDENTIFY:
        raise ValueError("freeze abstention terminal mismatch")

    cases = _case_map(freeze)
    required_cases = {
        "A_pre", "A_post", "A_safe_pre", "A_safe_post",
        "R_pre", "R_post", "R_safe_pre", "R_safe_post",
        "D_pre", "D_post", "D_safe_pre", "D_safe_post",
    }
    if set(cases) != required_cases:
        raise ValueError("frozen case census mismatch")

    for row in cases.values():
        _point_dict(row.get("point", ()))
        oracle = row.get("oracle")
        predictor = row.get("predictor")
        if not isinstance(oracle, list) or len(oracle) != 4 or any(v not in (0, 1) or isinstance(v, bool) for v in oracle):
            raise ValueError("frozen oracle vector malformed")
        if not isinstance(predictor, list) or len(predictor) != 4:
            raise ValueError("frozen predictor vector malformed")
        if any((v not in (0, 1, CANNOT_IDENTIFY)) or isinstance(v, bool) for v in predictor):
            raise ValueError("frozen predictor vector contains invalid value")

    transformations = freeze.get("transformations")
    if not isinstance(transformations, Mapping):
        raise ValueError("missing transformations")

    def points(pair: Mapping[str, Any]) -> tuple[List[int], List[int]]:
        pre = list(cases[str(pair["pre"])]["point"])
        post = list(cases[str(pair["post"])]["point"])
        return pre, post

    # Ablation controls: exactly one axis changes and the frozen from/to values agree.
    memory_index = EXPECTED_AXES.index("memory_margin")
    for name in ("ablation_main", "ablation_safe"):
        pair = transformations.get(name)
        if not isinstance(pair, Mapping) or pair.get("changed_axis") != "memory_margin":
            raise ValueError(f"{name}: malformed ablation registration")
        pre, post = points(pair)
        if pre[memory_index] != pair.get("from") or post[memory_index] != pair.get("to"):
            raise ValueError(f"{name}: ablation endpoints drifted")
        if any(pre[i] != post[i] for i in range(5) if i != memory_index):
            raise ValueError(f"{name}: ablation changed an unrelated axis")

    # Repricing controls reconstruct the held routing margins from B - price*d.
    route_index = EXPECTED_AXES.index("routing_margin")
    for name in ("repricing_main", "repricing_safe"):
        pair = transformations.get(name)
        if not isinstance(pair, Mapping):
            raise ValueError(f"{name}: malformed repricing registration")
        budget = pair.get("budget")
        demand = pair.get("demand")
        p0 = pair.get("price_from")
        p1 = pair.get("price_to")
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (budget, demand, p0, p1)):
            raise ValueError(f"{name}: repricing quantities must be integers")
        pre, post = points(pair)
        if pre[route_index] != budget - p0 * demand or post[route_index] != budget - p1 * demand:
            raise ValueError(f"{name}: repricing arithmetic does not reproduce frozen points")
        if any(pre[i] != post[i] for i in range(5) if i != route_index):
            raise ValueError(f"{name}: repricing changed an unrelated axis")

    # Drift controls reconstruct communication margin_after = margin_before - shock.
    comm_index = EXPECTED_AXES.index("communication_margin")
    for name in ("drift_main", "drift_safe"):
        pair = transformations.get(name)
        if not isinstance(pair, Mapping):
            raise ValueError(f"{name}: malformed drift registration")
        shock = pair.get("shock")
        if isinstance(shock, bool) or not isinstance(shock, int):
            raise ValueError(f"{name}: drift shock must be an integer")
        pre, post = points(pair)
        if post[comm_index] != pre[comm_index] - shock:
            raise ValueError(f"{name}: drift arithmetic does not reproduce frozen point")
        if any(pre[i] != post[i] for i in range(5) if i != comm_index):
            raise ValueError(f"{name}: drift changed an unrelated axis")

    # Main post points must remain genuinely outside the development cube on the changed axis.
    for case_id, axis in (("A_post", memory_index), ("R_post", route_index), ("D_post", comm_index)):
        point = list(cases[case_id]["point"])
        if point[axis] != -2 or all(-1 <= value <= 1 for value in point):
            raise ValueError("main post point was substituted back inside development grid")


def load_pinned_predictor(freeze: Mapping[str, Any]):
    pinned = freeze.get("pinned_predictor")
    if not isinstance(pinned, Mapping):
        raise ValueError("missing pinned predictor registration")
    rel_path = pinned.get("path")
    expected_blob = pinned.get("git_blob_sha")
    if not isinstance(rel_path, str) or not isinstance(expected_blob, str):
        raise ValueError("malformed pinned predictor registration")
    path = ROOT / rel_path
    if git_blob_sha(path) != expected_blob:
        raise RuntimeError("PINNED_PREDICTOR_BLOB_DRIFT")
    spec = importlib.util.spec_from_file_location("gmi_pinned_dev_predictor_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned predictor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _vector(mapping: Mapping[str, Any]) -> List[Any]:
    return [mapping[target] for target in EXPECTED_TARGETS]


def _deficit_set(pre: Sequence[int], post: Sequence[int]) -> List[str]:
    return [
        target
        for target, before, after in zip(EXPECTED_TARGETS, pre, post)
        if before == 1 and after == 0
    ]


def score_freeze(freeze: Mapping[str, Any]) -> Dict[str, Any]:
    validate_freeze(freeze)
    predictor_module = load_pinned_predictor(freeze)
    predictor = predictor_module.fit_registered_development_predictor()
    cases = _case_map(freeze)

    scored: Dict[str, Any] = {}
    determinate_cells = 0
    determinate_correct = 0
    abstentions = 0

    for case_id in sorted(cases):
        row = cases[case_id]
        point = _point_dict(row["point"])
        oracle = independent_oracle(point)
        actual_oracle = _vector(oracle)
        actual_predictor = _vector(predictor.predict_vector(point))
        if actual_oracle != list(row["oracle"]):
            raise RuntimeError(f"FROZEN_ORACLE_VECTOR_MISMATCH:{case_id}")
        if actual_predictor != list(row["predictor"]):
            raise RuntimeError(f"FROZEN_PREDICTOR_VECTOR_MISMATCH:{case_id}")

        case_correct = 0
        case_abstentions = 0
        for pred, truth in zip(actual_predictor, actual_oracle):
            if pred == CANNOT_IDENTIFY:
                abstentions += 1
                case_abstentions += 1
            else:
                determinate_cells += 1
                if pred != truth:
                    raise RuntimeError(f"DETERMINATE_ORACLE_DISAGREEMENT:{case_id}")
                determinate_correct += 1
                case_correct += 1

        scored[case_id] = {
            "point": list(row["point"]),
            "oracle": actual_oracle,
            "predictor": actual_predictor,
            "determinate_correct": case_correct,
            "abstentions": case_abstentions,
        }

    transformations = freeze["transformations"]
    transform_receipt: Dict[str, Any] = {}
    for name in sorted(transformations):
        pair = transformations[name]
        pre = scored[str(pair["pre"])]["oracle"]
        post = scored[str(pair["post"])]["oracle"]
        deficits = _deficit_set(pre, post)
        expected = list(pair["expected_direct_deficit_set"])
        if deficits != expected:
            raise RuntimeError(f"DIRECT_DEFICIT_SET_MISMATCH:{name}")
        transform_receipt[name] = {
            "pre": pair["pre"],
            "post": pair["post"],
            "direct_deficit_set": deficits,
        }

    safe_names = ("ablation_safe", "repricing_safe", "drift_safe")
    for name in safe_names:
        pair = transformations[name]
        for case_id in (str(pair["pre"]), str(pair["post"])):
            if scored[case_id]["oracle"] != [1, 1, 1, 1] or scored[case_id]["predictor"] != [1, 1, 1, 1]:
                raise RuntimeError(f"SAFE_CONTROL_CHANGED:{name}:{case_id}")

    return {
        "schema": "GMI_CAPABILITY_PERTURBATION_RESULT_V1",
        "issue": 784,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM,
        "predictor_blob_sha": freeze["pinned_predictor"]["git_blob_sha"],
        "cases_scored": len(scored),
        "point_target_cells": len(scored) * len(EXPECTED_TARGETS),
        "determinate_cells": determinate_cells,
        "determinate_correct": determinate_correct,
        "abstentions": abstentions,
        "abstentions_count_as_success": False,
        "cases": scored,
        "transformations": transform_receipt,
        "forbidden_claims": list(freeze["forbidden_claims"]),
        "verdict": "PASS",
    }


def build_receipt() -> Dict[str, Any]:
    return score_freeze(load_freeze())


def main() -> int:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
