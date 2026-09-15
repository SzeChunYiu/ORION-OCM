from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Dict, Mapping, Sequence, Tuple, Union

PINNED_PREDICTOR_BLOB = "937b91f6a3787ff04c2b5209c81d249518406859"
FREEZE_COMMIT = "ee62a2ae888ebddbc925972bc149468884e24ba5"
CLAIM_CEILING = "PROSPECTIVE_CAPABILITY_PERTURBATIONS_VALIDATED_AT_REGISTERED_SYNTHETIC_SCOPE"
CANNOT_IDENTIFY = "CANNOT_IDENTIFY"

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

PREDICTOR_PATH = (
    Path(__file__).resolve().parent.parent
    / "gmi-capability-predictor-dev-v1"
    / "dev_predictor_v1.py"
)

FORBIDDEN_CLAIMS = [
    "UNIVERSAL_CAPABILITY_PREDICTOR",
    "REAL_WORLD_PERTURBATION_CALIBRATION",
    "CAUSAL_EFFECT_IDENTIFIED_OUTSIDE_REGISTERED_ORACLE",
    "G6_UNIVERSAL",
    "COMPLETE_GMI",
]

CASES: Dict[str, Dict[str, object]] = {
    "A0": {
        "kind": "ablation",
        "pre": (2, 0, 0, 0, 0),
        "frozen_post": (-2, 0, 0, 0, 0),
        "transform": {"axis": "memory_margin", "after": -2},
        "expected_pre_oracle": (1, 1, 1, 1),
        "expected_post_oracle": (0, 0, 1, 1),
        "expected_pre_predictor": (1, 1, 1, 1),
        "expected_post_predictor": (0, 0, CANNOT_IDENTIFY, CANNOT_IDENTIFY),
        "expected_direct_deficits": ("memory_exact", "planning_exact"),
        "expected_abstentions": ("coordination_exact", "verified_tool_exact"),
        "safe_control": False,
    },
    "A1": {
        "kind": "ablation",
        "pre": (3, 0, 0, 0, 0),
        "frozen_post": (2, 0, 0, 0, 0),
        "transform": {"axis": "memory_margin", "after": 2},
        "expected_pre_oracle": (1, 1, 1, 1),
        "expected_post_oracle": (1, 1, 1, 1),
        "expected_pre_predictor": (1, 1, 1, 1),
        "expected_post_predictor": (1, 1, 1, 1),
        "expected_direct_deficits": (),
        "expected_abstentions": (),
        "safe_control": True,
    },
    "R0": {
        "kind": "repricing",
        "pre": (0, 0, 0, 2, 0),
        "frozen_post": (0, 0, 0, -2, 0),
        "transform": {
            "budget": 5,
            "demand": 1,
            "price_before": 3,
            "price_after": 7,
        },
        "expected_pre_oracle": (1, 1, 1, 1),
        "expected_post_oracle": (1, 1, 1, 0),
        "expected_pre_predictor": (1, 1, 1, 1),
        "expected_post_predictor": (
            CANNOT_IDENTIFY,
            CANNOT_IDENTIFY,
            CANNOT_IDENTIFY,
            0,
        ),
        "expected_direct_deficits": ("verified_tool_exact",),
        "expected_abstentions": (
            "memory_exact",
            "planning_exact",
            "coordination_exact",
        ),
        "safe_control": False,
    },
    "R1": {
        "kind": "repricing",
        "pre": (0, 0, 0, 3, 0),
        "frozen_post": (0, 0, 0, 2, 0),
        "transform": {
            "budget": 5,
            "demand": 1,
            "price_before": 2,
            "price_after": 3,
        },
        "expected_pre_oracle": (1, 1, 1, 1),
        "expected_post_oracle": (1, 1, 1, 1),
        "expected_pre_predictor": (1, 1, 1, 1),
        "expected_post_predictor": (1, 1, 1, 1),
        "expected_direct_deficits": (),
        "expected_abstentions": (),
        "safe_control": True,
    },
    "D0": {
        "kind": "drift",
        "pre": (0, 0, 2, 0, 0),
        "frozen_post": (0, 0, -2, 0, 0),
        "transform": {"shock": 4},
        "expected_pre_oracle": (1, 1, 1, 1),
        "expected_post_oracle": (1, 1, 0, 1),
        "expected_pre_predictor": (1, 1, 1, 1),
        "expected_post_predictor": (
            CANNOT_IDENTIFY,
            CANNOT_IDENTIFY,
            0,
            CANNOT_IDENTIFY,
        ),
        "expected_direct_deficits": ("coordination_exact",),
        "expected_abstentions": (
            "memory_exact",
            "planning_exact",
            "verified_tool_exact",
        ),
        "safe_control": False,
    },
    "D1": {
        "kind": "drift",
        "pre": (0, 0, 3, 0, 0),
        "frozen_post": (0, 0, 2, 0, 0),
        "transform": {"shock": 1},
        "expected_pre_oracle": (1, 1, 1, 1),
        "expected_post_oracle": (1, 1, 1, 1),
        "expected_pre_predictor": (1, 1, 1, 1),
        "expected_post_predictor": (1, 1, 1, 1),
        "expected_direct_deficits": (),
        "expected_abstentions": (),
        "safe_control": True,
    },
}


def git_blob_sha1(raw: bytes) -> str:
    prefix = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(prefix + raw).hexdigest()


def verify_predictor_bytes(raw: bytes) -> str:
    actual = git_blob_sha1(raw)
    if actual != PINNED_PREDICTOR_BLOB:
        raise RuntimeError(
            f"pinned predictor blob mismatch: expected {PINNED_PREDICTOR_BLOB}, got {actual}"
        )
    return actual


def verify_predictor_blob(path: Path = PREDICTOR_PATH) -> str:
    if not path.is_file():
        raise RuntimeError(f"pinned predictor source missing: {path}")
    return verify_predictor_bytes(path.read_bytes())


def load_predictor_module(path: Path = PREDICTOR_PATH):
    verify_predictor_blob(path)
    spec = importlib.util.spec_from_file_location("gmi_pinned_dev_predictor_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot construct predictor import specification")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if tuple(mod.AXES) != AXES or tuple(mod.TARGETS) != TARGETS:
        raise RuntimeError("pinned predictor registry differs from frozen axis/target contract")
    if mod.CANNOT_IDENTIFY != CANNOT_IDENTIFY:
        raise RuntimeError("pinned predictor abstention terminal differs from freeze")
    return mod


def point(values: Sequence[int]) -> Dict[str, int]:
    if len(values) != len(AXES):
        raise ValueError("point must have exactly five registered margins")
    result = dict(zip(AXES, values))
    for value in result.values():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("all registered margins must be integers")
    return result


def vector_tuple(vector: Mapping[str, Union[int, str]]) -> Tuple[Union[int, str], ...]:
    if set(vector) != set(TARGETS):
        raise ValueError("capability vector must contain exactly registered targets")
    return tuple(vector[target] for target in TARGETS)


def independent_oracle(p: Mapping[str, int]) -> Dict[str, int]:
    if set(p) != set(AXES):
        raise ValueError("oracle point must contain exactly registered axes")
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


def reconstruct_post(case: Mapping[str, object]) -> Dict[str, int]:
    pre = point(case["pre"])  # type: ignore[arg-type]
    transform = case["transform"]
    if not isinstance(transform, Mapping):
        raise ValueError("transform must be a mapping")
    kind = case["kind"]

    post = dict(pre)
    if kind == "ablation":
        if set(transform) != {"axis", "after"}:
            raise ValueError("ablation transform schema mismatch")
        axis = transform["axis"]
        after = transform["after"]
        if axis != "memory_margin":
            raise ValueError("registered ablation may change only memory_margin")
        if isinstance(after, bool) or not isinstance(after, int):
            raise ValueError("ablation after-value must be an integer")
        post[axis] = after
    elif kind == "repricing":
        if set(transform) != {"budget", "demand", "price_before", "price_after"}:
            raise ValueError("repricing transform schema mismatch")
        B = transform["budget"]
        d = transform["demand"]
        p0 = transform["price_before"]
        p1 = transform["price_after"]
        if any(isinstance(x, bool) or not isinstance(x, int) for x in (B, d, p0, p1)):
            raise ValueError("repricing values must be integers")
        if d <= 0:
            raise ValueError("routing demand must be positive")
        before_margin = B - p0 * d
        after_margin = B - p1 * d
        if pre["routing_margin"] != before_margin:
            raise ValueError("frozen pre routing margin disagrees with repricing map")
        post["routing_margin"] = after_margin
    elif kind == "drift":
        if set(transform) != {"shock"}:
            raise ValueError("drift transform schema mismatch")
        shock = transform["shock"]
        if isinstance(shock, bool) or not isinstance(shock, int) or shock < 0:
            raise ValueError("drift shock must be a nonnegative integer")
        post["communication_margin"] = pre["communication_margin"] - shock
    else:
        raise ValueError(f"unknown perturbation kind: {kind!r}")
    return post


def require_held_point(p: Mapping[str, int]) -> None:
    if not any(abs(p[axis]) >= 2 for axis in AXES):
        raise ValueError("held point silently fell inside development grid {-1,0,1}^5")


def require_frozen_post(case: Mapping[str, object], post: Mapping[str, int]) -> None:
    expected = point(case["frozen_post"])  # type: ignore[arg-type]
    if dict(post) != expected:
        raise ValueError(f"reconstructed post point disagrees with freeze: {post} != {expected}")


def _expected_tuple(case: Mapping[str, object], key: str) -> Tuple[Union[int, str], ...]:
    raw = case[key]
    if not isinstance(raw, tuple) or len(raw) != len(TARGETS):
        raise ValueError(f"{key} must be a frozen four-cell tuple")
    return raw


def evaluate_case(
    case_id: str,
    case: Mapping[str, object],
    predictor,
) -> Dict[str, object]:
    pre = point(case["pre"])  # type: ignore[arg-type]
    post = reconstruct_post(case)
    require_held_point(pre)
    require_held_point(post)
    require_frozen_post(case, post)

    pre_oracle = independent_oracle(pre)
    post_oracle = independent_oracle(post)
    pre_pred = predictor.predict_vector(pre)
    post_pred = predictor.predict_vector(post)

    actual_pre_oracle = vector_tuple(pre_oracle)
    actual_post_oracle = vector_tuple(post_oracle)
    actual_pre_pred = vector_tuple(pre_pred)
    actual_post_pred = vector_tuple(post_pred)

    frozen_pairs = (
        ("expected_pre_oracle", actual_pre_oracle),
        ("expected_post_oracle", actual_post_oracle),
        ("expected_pre_predictor", actual_pre_pred),
        ("expected_post_predictor", actual_post_pred),
    )
    for key, actual in frozen_pairs:
        expected = _expected_tuple(case, key)
        if actual != expected:
            raise ValueError(f"{case_id} {key} mismatch: got {actual}, expected {expected}")

    determinate = 0
    correct = 0
    abstentions = 0
    for predicted, truth in zip(actual_pre_pred + actual_post_pred, actual_pre_oracle + actual_post_oracle):
        if predicted == CANNOT_IDENTIFY:
            abstentions += 1
            continue
        determinate += 1
        if predicted != truth:
            raise ValueError(
                f"{case_id} determinate predictor cell disagrees with independent oracle"
            )
        correct += 1

    direct_deficits = tuple(
        target
        for target, before, after in zip(TARGETS, actual_pre_pred, actual_post_pred)
        if before == 1 and after == 0
    )
    abstention_set = tuple(
        target
        for target, after in zip(TARGETS, actual_post_pred)
        if after == CANNOT_IDENTIFY
    )

    if direct_deficits != tuple(case["expected_direct_deficits"]):
        raise ValueError(
            f"{case_id} direct deficit set mismatch: {direct_deficits}"
        )
    if abstention_set != tuple(case["expected_abstentions"]):
        raise ValueError(f"{case_id} abstention set mismatch: {abstention_set}")

    safe = bool(case["safe_control"])
    if safe:
        ones = (1, 1, 1, 1)
        if any(v != ones for v in (actual_pre_oracle, actual_post_oracle, actual_pre_pred, actual_post_pred)):
            raise ValueError(f"{case_id} safe control changed or abstained")

    return {
        "case_id": case_id,
        "kind": case["kind"],
        "safe_control": safe,
        "pre_point": pre,
        "transform": dict(case["transform"]),  # type: ignore[arg-type]
        "reconstructed_post_point": post,
        "oracle": {
            "pre": dict(zip(TARGETS, actual_pre_oracle)),
            "post": dict(zip(TARGETS, actual_post_oracle)),
        },
        "predictor": {
            "pre": dict(zip(TARGETS, actual_pre_pred)),
            "post": dict(zip(TARGETS, actual_post_pred)),
        },
        "determinate_cells": determinate,
        "determinate_correct": correct,
        "abstention_cells": abstentions,
        "direct_deficit_set": list(direct_deficits),
        "post_abstention_set": list(abstention_set),
    }


def _expect_failure(fn, label: str) -> str:
    try:
        fn()
    except (ValueError, RuntimeError):
        return "PASS_FAIL_CLOSED"
    raise RuntimeError(f"hostile did not fail closed: {label}")


def hostile_results(predictor) -> Dict[str, str]:
    import copy

    results: Dict[str, str] = {}

    raw = PREDICTOR_PATH.read_bytes()
    results["predictor_source_drift"] = _expect_failure(
        lambda: verify_predictor_bytes(raw + b"\n# hostile drift\n"),
        "predictor source drift",
    )

    bad_reprice = copy.deepcopy(CASES["R0"])
    bad_reprice["transform"]["price_after"] = 6  # type: ignore[index]
    results["repricing_arithmetic_mutation"] = _expect_failure(
        lambda: evaluate_case("R0", bad_reprice, predictor),
        "repricing arithmetic mutation",
    )

    bad_drift = copy.deepcopy(CASES["D0"])
    bad_drift["transform"]["shock"] = 3  # type: ignore[index]
    results["drift_arithmetic_mutation"] = _expect_failure(
        lambda: evaluate_case("D0", bad_drift, predictor),
        "drift arithmetic mutation",
    )

    grid_substitution = copy.deepcopy(CASES["A0"])
    grid_substitution["transform"]["after"] = -1  # type: ignore[index]
    grid_substitution["frozen_post"] = (-1, 0, 0, 0, 0)
    results["development_grid_substitution"] = _expect_failure(
        lambda: evaluate_case("A0", grid_substitution, predictor),
        "development-grid substitution",
    )

    bad_oracle = copy.deepcopy(CASES["A0"])
    bad_oracle["expected_post_oracle"] = (0, 1, 1, 1)
    results["expected_oracle_mutation"] = _expect_failure(
        lambda: evaluate_case("A0", bad_oracle, predictor),
        "expected oracle mutation",
    )

    launder = copy.deepcopy(CASES["A0"])
    launder["expected_post_predictor"] = (0, 0, 1, 1)
    results["abstention_laundering"] = _expect_failure(
        lambda: evaluate_case("A0", launder, predictor),
        "abstention laundering",
    )

    unsafe = copy.deepcopy(CASES["A1"])
    unsafe["expected_post_predictor"] = (1, 1, CANNOT_IDENTIFY, 1)
    results["safe_control_sensitivity"] = _expect_failure(
        lambda: evaluate_case("A1", unsafe, predictor),
        "safe control sensitivity",
    )

    return results


def build_receipt() -> Dict[str, object]:
    actual_blob = verify_predictor_blob()
    mod = load_predictor_module()
    predictor = mod.fit_registered_development_predictor()

    case_receipts = [
        evaluate_case(case_id, CASES[case_id], predictor)
        for case_id in ("A0", "A1", "R0", "R1", "D0", "D1")
    ]
    determinate = sum(int(row["determinate_cells"]) for row in case_receipts)
    correct = sum(int(row["determinate_correct"]) for row in case_receipts)
    abstentions = sum(int(row["abstention_cells"]) for row in case_receipts)
    if determinate != correct:
        raise RuntimeError("aggregate determinate accuracy is not exact")
    if determinate + abstentions != len(case_receipts) * 2 * len(TARGETS):
        raise RuntimeError("aggregate cell accounting mismatch")

    return {
        "schema": "GMI_PROSPECTIVE_CAPABILITY_PERTURBATIONS_V1",
        "issue": 784,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "pinned_predictor": {
            "path": str(PREDICTOR_PATH.relative_to(PREDICTOR_PATH.parents[1])),
            "git_blob": actual_blob,
        },
        "claim_ceiling": CLAIM_CEILING,
        "development_grid": "{-1,0,1}^5",
        "axis_order": list(AXES),
        "capability_order": list(TARGETS),
        "cases": case_receipts,
        "aggregate": {
            "total_cells": len(case_receipts) * 2 * len(TARGETS),
            "determinate_cells": determinate,
            "determinate_correct": correct,
            "determinate_accuracy": f"{correct}/{determinate}",
            "abstention_cells": abstentions,
            "abstentions_excluded_from_accuracy": True,
            "main_direct_deficits": {
                "A0": ["memory_exact", "planning_exact"],
                "R0": ["verified_tool_exact"],
                "D0": ["coordination_exact"],
            },
            "safe_controls_all_ones": True,
        },
        "hostiles": hostile_results(predictor),
        "forbidden_claims": FORBIDDEN_CLAIMS,
    }


def main() -> None:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
