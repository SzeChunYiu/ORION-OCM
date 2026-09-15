from __future__ import annotations

import csv
import functools
import hashlib
import importlib.util
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
from typing import Dict, Mapping, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FRAME_CSV = HERE / "DETERMINATE_FRAME_SHARED_V2.csv"
FRAME_MANIFEST = HERE / "DETERMINATE_FRAME_V2.json"
SAMPLE_PATH = HERE / "AUDIT_SAMPLE_V2.json"
BUILDER_PATH = HERE / "build_determinate_frame_v2.py"
PREDICTOR_PATH = REPO / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"

TARGETS = (
    "memory_exact",
    "planning_exact",
    "coordination_exact",
    "verified_tool_exact",
)
AXES = (
    "memory_margin",
    "planning_margin",
    "communication_margin",
    "routing_margin",
    "verification_margin",
)
PINNED_PREDICTOR_BLOB = "937b91f6a3787ff04c2b5209c81d249518406859"
FRAME_SHA256 = "8c9e14262c136e5a821842f880f6f36f984ab9aba9a874647cb8b93c6b9a8adf"
N = 64
SAMPLE_N = 48
CANDIDATE_N = 1024
DELTA_TOTAL = F(1, 20)
DELTA_COORD = F(1, 80)
EPSILON = F(1, 20)


def fstr(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_predictor_module():
    return _load_module(PREDICTOR_PATH, "gmi_dev_predictor_v1")


def load_frame_rows() -> Dict[str, Mapping[str, int]]:
    if hashlib.sha256(FRAME_CSV.read_bytes()).hexdigest() != FRAME_SHA256:
        raise ValueError("determinate frame content hash drift")
    manifest = json.loads(FRAME_MANIFEST.read_text())
    if manifest.get("schema") != "CapabilityCalibrationDeterminateFrameManifestV2":
        raise ValueError("wrong frame manifest schema")
    if manifest.get("oracle_outcomes_included") is not False:
        raise ValueError("oracle outcomes forbidden in frame manifest")
    if manifest.get("correctness_fields_included") is not False:
        raise ValueError("correctness fields forbidden in frame manifest")
    if manifest.get("shared_frame_sha256") != FRAME_SHA256:
        raise ValueError("frame manifest hash mismatch")
    for target in TARGETS:
        row = manifest["coordinates"][target]
        if row["determinate_count"] != N or row["candidate_grid_coverage"] != "1/16":
            raise ValueError("frame count/coverage drift")

    rows = {}
    with FRAME_CSV.open(newline="") as handle:
        reader = csv.DictReader(handle)
        expected = ["specimen_id", *AXES, "frozen_prediction"]
        if reader.fieldnames != expected:
            raise ValueError("frame columns drift")
        for row in reader:
            sid = row["specimen_id"]
            if sid in rows:
                raise ValueError("duplicate frame specimen id")
            point = {axis: int(row[axis]) for axis in AXES}
            prediction = int(row["frozen_prediction"])
            if prediction not in (0, 1):
                raise ValueError("frame prediction must be binary")
            rows[sid] = {**point, "frozen_prediction": prediction}
    if len(rows) != N:
        raise ValueError("frame must contain 64 rows")

    builder = _load_module(BUILDER_PATH, "gmi_capability_frame_builder_v2")
    generated = builder.build_frame()
    for target in TARGETS:
        generated_rows = generated["coordinate_frames"][target]["rows"]
        expected_rows = [
            [sid, *(rows[sid][axis] for axis in AXES), rows[sid]["frozen_prediction"]]
            for sid in sorted(rows)
        ]
        if generated_rows != expected_rows:
            raise ValueError(f"outcome-free builder/frame mismatch for {target}")
    return rows


def load_samples(frame_rows: Mapping[str, object]) -> Dict[str, Tuple[str, ...]]:
    payload = json.loads(SAMPLE_PATH.read_text())
    if payload.get("schema") != "CapabilityCalibrationAuditSampleV2":
        raise ValueError("wrong sample schema")
    if payload.get("oracle_outcomes_included") is not False:
        raise ValueError("sample contains oracle outcomes")
    if payload.get("outcomes_seen_before_sample_commit") is not False:
        raise ValueError("sample custody indicates outcome access")
    if payload.get("population_size_per_coordinate") != N:
        raise ValueError("sample population size drift")
    if payload.get("sample_size_per_coordinate") != SAMPLE_N:
        raise ValueError("sample size drift")
    if payload.get("frame_sha256") != FRAME_SHA256:
        raise ValueError("sample frame hash mismatch")
    if payload.get("coordinates") != list(TARGETS):
        raise ValueError("sample target list drift")
    forbidden_fragments = ("oracle", "correct", "error", "outcome", "label")
    for key in payload:
        if any(fragment in key.lower() for fragment in forbidden_fragments):
            if key not in {"oracle_outcomes_included", "outcomes_seen_before_sample_commit"}:
                raise ValueError("unexpected outcome-like sample field")
    samples = payload.get("samples")
    if not isinstance(samples, dict) or set(samples) != set(TARGETS):
        raise ValueError("sample map drift")
    allowed = set(frame_rows)
    result = {}
    for target in TARGETS:
        ids = tuple(samples[target])
        if len(ids) != SAMPLE_N or len(set(ids)) != SAMPLE_N:
            raise ValueError("sample must contain 48 unique ids")
        if tuple(sorted(ids)) != ids:
            raise ValueError("sample ids must be canonical sorted realization")
        if not set(ids).issubset(allowed):
            raise ValueError("sample id outside determinate frame")
        result[target] = ids
    return result


def hypergeom_pmf(N_: int, K: int, n_: int, x: int) -> F:
    if not (0 <= K <= N_ and 0 <= n_ <= N_):
        raise ValueError("invalid hypergeometric dimensions")
    lo = max(0, n_ - (N_ - K))
    hi = min(n_, K)
    if x < lo or x > hi:
        return F(0)
    return F(
        math.comb(K, x) * math.comb(N_ - K, n_ - x),
        math.comb(N_, n_),
    )


@functools.lru_cache(maxsize=None)
def hypergeom_cdf(N_: int, K: int, n_: int, x: int) -> F:
    if not isinstance(x, int):
        raise TypeError("x must be int")
    if x < 0:
        return F(0)
    return sum((hypergeom_pmf(N_, K, n_, j) for j in range(x + 1)), F(0))


@functools.lru_cache(maxsize=None)
def _upper_cached(N_: int, n_: int, x: int, delta_num: int, delta_den: int) -> int:
    delta = F(delta_num, delta_den)
    candidates = [K for K in range(N_ + 1) if hypergeom_cdf(N_, K, n_, x) > delta]
    if not candidates:
        raise AssertionError("K=0 must be admissible")
    return max(candidates)


def upper_error_count(N_: int, n_: int, x: int, delta: F) -> int:
    if not isinstance(delta, F):
        raise TypeError("delta must be Fraction")
    if not (F(0) < delta < F(1)):
        raise ValueError("delta must lie in (0,1)")
    if not (0 <= x <= n_ <= N_):
        raise ValueError("invalid N/n/x")
    return _upper_cached(N_, n_, x, delta.numerator, delta.denominator)


def independent_subset_error_counts(N_: int, K: int, n_: int) -> Mapping[int, int]:
    """Independent dynamic programme over subset choices, not hypergeom formula."""
    if not (0 <= K <= N_ and 0 <= n_ <= N_):
        raise ValueError("invalid dimensions")
    dp = {(0, 0): 1}
    for item in range(N_):
        is_error = int(item < K)
        next_dp = dict(dp)
        for (taken, errors), count in dp.items():
            if taken < n_:
                key = (taken + 1, errors + is_error)
                next_dp[key] = next_dp.get(key, 0) + count
        dp = next_dp
    return {errors: count for (taken, errors), count in dp.items() if taken == n_}


def exhaustive_small_theorem_check(max_N: int = 20) -> Mapping[str, object]:
    deltas = (F(1, 2), F(1, 5), F(1, 20), F(1, 80))
    pmf_cases = 0
    coverage_cases = 0
    for N_ in range(1, max_N + 1):
        for n_ in range(1, N_ + 1):
            denominator = math.comb(N_, n_)
            for K in range(N_ + 1):
                counts = independent_subset_error_counts(N_, K, n_)
                lo = max(0, n_ - (N_ - K))
                hi = min(n_, K)
                for x in range(lo, hi + 1):
                    exact = F(counts.get(x, 0), denominator)
                    if hypergeom_pmf(N_, K, n_, x) != exact:
                        raise AssertionError("PMF mismatch", N_, n_, K, x)
                    pmf_cases += 1
                for delta in deltas:
                    coverage = F(0)
                    for x in range(lo, hi + 1):
                        if K <= upper_error_count(N_, n_, x, delta):
                            coverage += F(counts[x], denominator)
                    if coverage < F(1) - delta:
                        raise AssertionError("coverage failure", N_, n_, K, delta, coverage)
                    coverage_cases += 1
    return {
        "max_N": max_N,
        "deltas": [fstr(d) for d in deltas],
        "pmf_cases": pmf_cases,
        "coverage_cases": coverage_cases,
        "status": "PASS",
    }


def _score_principal(frame_rows, samples):
    mod = load_predictor_module()
    predictor = mod.fit_registered_development_predictor()
    results = {}
    truths = {}
    for sid, row in frame_rows.items():
        point = {axis: row[axis] for axis in AXES}
        truths[sid] = mod.capability_oracle(point)
        for target in TARGETS:
            predicted = predictor.predict_one(point, target)
            if predicted not in (0, 1):
                raise AssertionError("frame contains non-determinate current prediction")
            if predicted != row["frozen_prediction"]:
                raise AssertionError("frozen/current predictor drift")

    for target in TARGETS:
        sample_ids = samples[target]
        sample_errors = sum(
            int(frame_rows[sid]["frozen_prediction"] != truths[sid][target])
            for sid in sample_ids
        )
        U = upper_error_count(N, SAMPLE_N, sample_errors, DELTA_COORD)
        upper_rate = F(U, N)
        terminal = (
            "CALIBRATED_AT_REGISTERED_DETERMINATE_FRAME"
            if upper_rate <= EPSILON
            else "CANNOT_CERTIFY_ERROR_RATE"
        )
        # Census is evaluated only after the sample-derived U is fixed above.
        total_errors = sum(
            int(frame_rows[sid]["frozen_prediction"] != truths[sid][target])
            for sid in frame_rows
        )
        results[target] = {
            "sample_errors": sample_errors,
            "upper_error_count": U,
            "upper_error_rate": fstr(upper_rate),
            "epsilon": fstr(EPSILON),
            "delta": fstr(DELTA_COORD),
            "terminal": terminal,
            "candidate_grid_count": CANDIDATE_N,
            "determinate_frame_count": N,
            "candidate_grid_coverage": fstr(F(N, CANDIDATE_N)),
            "true_total_errors_post_certificate_census": total_errors,
            "truth_covered": total_errors <= U,
        }
    return results, truths


def complement_control(frame_rows, samples, truths):
    result = {}
    for target in TARGETS:
        sample_errors = sum(
            int((1 - frame_rows[sid]["frozen_prediction"]) != truths[sid][target])
            for sid in samples[target]
        )
        U = upper_error_count(N, SAMPLE_N, sample_errors, DELTA_COORD)
        rate = F(U, N)
        total_errors = sum(
            int((1 - row["frozen_prediction"]) != truths[sid][target])
            for sid, row in frame_rows.items()
        )
        result[target] = {
            "sample_errors": sample_errors,
            "upper_error_count": U,
            "upper_error_rate": fstr(rate),
            "true_total_errors": total_errors,
            "certified": rate <= EPSILON,
        }
    return result


def abstention_control(frame_rows, truths, target="memory_exact"):
    ordered = sorted(frame_rows)
    abstain = set(ordered[::7])
    determinate = [sid for sid in ordered if sid not in abstain]
    errors = sum(
        int(frame_rows[sid]["frozen_prediction"] != truths[sid][target])
        for sid in determinate
    )
    return {
        "target": target,
        "frame_count": len(ordered),
        "abstentions": len(abstain),
        "determinate": len(determinate),
        "determinate_coverage": fstr(F(len(determinate), len(ordered))),
        "determinate_error_count": errors,
        "abstentions_counted_as_correct": False,
    }


def dependence_hostile():
    atoms = set(range(80))
    failure_sets = [{i} for i in range(4)]
    good_sets = [atoms - failures for failures in failure_sets]
    joint_good = set.intersection(*good_sets)
    actual = F(len(joint_good), 80)
    bound = F(1) - 4 * F(1, 80)
    product = F(79, 80) ** 4
    return {
        "marginal_success_each": "79/80",
        "actual_joint_success": fstr(actual),
        "union_bound_lower": fstr(bound),
        "independence_product": fstr(product),
        "actual_equals_union_bound": actual == bound,
        "independence_product_differs": product != actual,
        "independence_used": False,
    }


def build_receipt():
    frame_rows = load_frame_rows()
    samples = load_samples(frame_rows)
    principal, truths = _score_principal(frame_rows, samples)
    complement = complement_control(frame_rows, samples, truths)
    theorem_check = exhaustive_small_theorem_check(20)
    simultaneous = F(1) - len(TARGETS) * DELTA_COORD
    return {
        "schema": "GMICapabilityCalibrationResultV2",
        "issue": 766,
        "claim_ceiling": "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME",
        "predictor_blob_sha": PINNED_PREDICTOR_BLOB,
        "candidate_grid_count": CANDIDATE_N,
        "determinate_frame_count_per_coordinate": N,
        "candidate_grid_coverage_per_coordinate": fstr(F(N, CANDIDATE_N)),
        "sample_count_per_coordinate": SAMPLE_N,
        "delta_total": fstr(DELTA_TOTAL),
        "delta_per_coordinate": fstr(DELTA_COORD),
        "simultaneous_coverage_lower_bound": fstr(simultaneous),
        "epsilon": fstr(EPSILON),
        "principal": principal,
        "all_principal_coordinates_certified": all(
            row["terminal"] == "CALIBRATED_AT_REGISTERED_DETERMINATE_FRAME"
            for row in principal.values()
        ),
        "all_post_certificate_truths_covered": all(row["truth_covered"] for row in principal.values()),
        "complement_predictor_control": complement,
        "complement_control_fails_all_coordinates": all(not row["certified"] for row in complement.values()),
        "abstention_accounting_control": abstention_control(frame_rows, truths),
        "dependence_hostile": dependence_hostile(),
        "exhaustive_small_theorem_check": theorem_check,
        "iid_assumption": False,
        "replacement_sampling": False,
        "oracle_used_for_frame_construction": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_receipt(), sort_keys=True, indent=2))
