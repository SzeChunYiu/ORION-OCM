from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
POP_PATH = HERE / "AUDIT_POPULATION_V1.json"
SAMPLE_PATH = HERE / "AUDIT_SAMPLE_V1.json"
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
N = 128
n = 64
DELTA_TOTAL = F(1, 20)
DELTA_COORD = F(1, 80)
EPSILON = F(1, 20)
FORBIDDEN_SAMPLE_KEYS = {
    "oracle",
    "outcome",
    "outcomes",
    "correct",
    "correctness",
    "error",
    "errors",
    "label",
    "labels",
}


def fstr(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _load_predictor_module():
    spec = importlib.util.spec_from_file_location("gmi_dev_predictor_v1", PREDICTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned predictor")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def expected_population_rows() -> List[List[object]]:
    rows = []
    for values in itertools.product((-3, -2, 2, 3), repeat=5):
        raw = "T602-M5-AUDIT-V1|" + ",".join(map(str, values))
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        rows.append((digest, values))
    rows.sort(key=lambda item: (item[0], item[1]))
    return [["ACP_" + digest[:16], *values] for digest, values in rows[:N]]


def load_population(path: Path = POP_PATH) -> Dict[str, Mapping[str, int]]:
    payload = json.loads(path.read_text())
    if payload.get("schema") != "CapabilityCalibrationPopulationV1":
        raise ValueError("wrong population schema")
    if payload.get("oracle_outcomes_included") is not False:
        raise ValueError("population must contain no oracle outcomes")
    if payload.get("population_count") != N or payload.get("candidate_count") != 1024:
        raise ValueError("population size mismatch")
    if payload.get("axes") != list(AXES):
        raise ValueError("population axes mismatch")
    if payload.get("columns") != ["specimen_id", *AXES]:
        raise ValueError("population columns mismatch")
    rows = payload.get("rows")
    if rows != expected_population_rows():
        raise ValueError("population does not reproduce frozen generator")
    out: Dict[str, Mapping[str, int]] = {}
    for row in rows:
        specimen_id = row[0]
        if specimen_id in out:
            raise ValueError("duplicate specimen id")
        out[specimen_id] = dict(zip(AXES, row[1:]))
    return out


def load_sample(population: Mapping[str, object], path: Path = SAMPLE_PATH) -> Dict[str, Tuple[str, ...]]:
    payload = json.loads(path.read_text())
    if payload.get("schema") != "CapabilityCalibrationAuditSampleV1":
        raise ValueError("wrong sample schema")
    if payload.get("oracle_outcomes_included") is not False:
        raise ValueError("sample must contain no oracle outcomes")
    if payload.get("outcomes_seen_before_sample_commit") is not False:
        raise ValueError("sample custody says outcomes were seen")
    if payload.get("population_size_per_coordinate") != N or payload.get("sample_size_per_coordinate") != n:
        raise ValueError("sample size contract mismatch")
    if payload.get("coordinates") != list(TARGETS):
        raise ValueError("coordinate contract mismatch")
    forbidden = FORBIDDEN_SAMPLE_KEYS.intersection(payload.keys())
    if forbidden:
        raise ValueError("outcome-like sample fields present: %s" % sorted(forbidden))
    samples = payload.get("samples")
    if not isinstance(samples, dict) or set(samples) != set(TARGETS):
        raise ValueError("sample coordinates mismatch")
    allowed = set(population)
    result = {}
    for target in TARGETS:
        ids = tuple(samples[target])
        if len(ids) != n or len(set(ids)) != n:
            raise ValueError("sample must contain 64 unique ids")
        if not set(ids).issubset(allowed):
            raise ValueError("sample id outside population")
        if tuple(sorted(ids)) != ids:
            raise ValueError("sample ids must be canonical sorted realization")
        result[target] = ids
    return result


def hypergeom_pmf(N_: int, K: int, n_: int, x: int) -> F:
    if not (0 <= K <= N_ and 0 <= n_ <= N_):
        raise ValueError("invalid hypergeometric dimensions")
    lo = max(0, n_ - (N_ - K))
    hi = min(n_, K)
    if x < lo or x > hi:
        return F(0)
    return F(math.comb(K, x) * math.comb(N_ - K, n_ - x), math.comb(N_, n_))


def hypergeom_cdf(N_: int, K: int, n_: int, x: int) -> F:
    if not isinstance(x, int):
        raise TypeError("x must be int")
    return sum((hypergeom_pmf(N_, K, n_, j) for j in range(0, x + 1)), F(0))


def upper_error_count(N_: int, n_: int, x: int, delta: F) -> int:
    if not isinstance(delta, F):
        raise TypeError("delta must be Fraction")
    if not (F(0) < delta < F(1)):
        raise ValueError("delta must be in (0,1)")
    if not (0 <= x <= n_ <= N_):
        raise ValueError("invalid N/n/x")
    admissible = [K for K in range(N_ + 1) if hypergeom_cdf(N_, K, n_, x) > delta]
    if not admissible:
        raise AssertionError("K=0 must always be admissible")
    return max(admissible)


def dp_subset_error_counts(N_: int, K: int, n_: int) -> Mapping[int, int]:
    """Independent subset-count DP: coefficient counts, no hypergeom closed form."""
    if not (0 <= K <= N_ and 0 <= n_ <= N_):
        raise ValueError("invalid dimensions")
    dp = {(0, 0): 1}
    for is_error in ([1] * K + [0] * (N_ - K)):
        nxt = dict(dp)
        for (taken, errors), count in dp.items():
            if taken < n_:
                key = (taken + 1, errors + is_error)
                nxt[key] = nxt.get(key, 0) + count
        dp = nxt
    return {errors: count for (taken, errors), count in dp.items() if taken == n_}


def exhaustive_small_theorem_check(max_N: int = 20) -> Mapping[str, object]:
    deltas = (F(1, 2), F(1, 5), F(1, 20), F(1, 80))
    pmf_cases = 0
    coverage_cases = 0
    for N_ in range(1, max_N + 1):
        for n_ in range(1, N_ + 1):
            denominator = math.comb(N_, n_)
            for K in range(N_ + 1):
                dp = dp_subset_error_counts(N_, K, n_)
                feasible = range(max(0, n_ - (N_ - K)), min(n_, K) + 1)
                for x in feasible:
                    expected = F(dp.get(x, 0), denominator)
                    if hypergeom_pmf(N_, K, n_, x) != expected:
                        raise AssertionError("PMF mismatch", N_, n_, K, x)
                    pmf_cases += 1
                for delta in deltas:
                    coverage = F(0)
                    for x in feasible:
                        U = upper_error_count(N_, n_, x, delta)
                        if K <= U:
                            coverage += F(dp.get(x, 0), denominator)
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


def _predict_all(population: Mapping[str, Mapping[str, int]]):
    mod = _load_predictor_module()
    predictor = mod.fit_registered_development_predictor()
    predictions = {}
    truths = {}
    for specimen_id, point in population.items():
        predictions[specimen_id] = predictor.predict_vector(point)
        truths[specimen_id] = mod.capability_oracle(point)
    return mod, predictions, truths


def _coordinate_stats(target: str, population, sample_ids, predictions, truths):
    determinate = [sid for sid in sorted(population) if predictions[sid][target] in (0, 1)]
    if not determinate:
        return {"terminal": "CANNOT_CALIBRATE_NO_DETERMINATE_CELLS", "determinate": 0}
    determinate_set = set(determinate)
    if not set(sample_ids).issubset(determinate_set):
        raise ValueError("frozen audit sample contains non-determinate prediction")
    if len(determinate) != N:
        raise ValueError("V1 frozen audit requires 128 determinate cells per coordinate")
    sample_errors = sum(int(predictions[sid][target] != truths[sid][target]) for sid in sample_ids)
    total_errors = sum(int(predictions[sid][target] != truths[sid][target]) for sid in determinate)
    U = upper_error_count(N, n, sample_errors, DELTA_COORD)
    upper_rate = F(U, N)
    terminal = (
        "CALIBRATED_AT_REGISTERED_FINITE_POPULATION"
        if upper_rate <= EPSILON
        else "CANNOT_CERTIFY_ERROR_RATE"
    )
    return {
        "terminal": terminal,
        "population": N,
        "sample": n,
        "sample_errors": sample_errors,
        "upper_error_count": U,
        "upper_error_rate": fstr(upper_rate),
        "epsilon": fstr(EPSILON),
        "delta": fstr(DELTA_COORD),
        "true_total_errors_post_certificate_census": total_errors,
        "truth_covered": total_errors <= U,
        "determinate_coverage": fstr(F(len(determinate), len(population))),
    }


def _corrupted_prediction(specimen_id: str, pred):
    if pred not in (0, 1):
        return pred
    first_nibble = specimen_id.split("_", 1)[1][0]
    if first_nibble in {"0", "1", "2", "3"}:
        return 1 - pred
    return pred


def corrupted_control(target, population, sample_ids, predictions, truths):
    corrupted = {
        sid: _corrupted_prediction(sid, predictions[sid][target])
        for sid in population
    }
    determinate = [sid for sid in sorted(population) if corrupted[sid] in (0, 1)]
    sample_errors = sum(int(corrupted[sid] != truths[sid][target]) for sid in sample_ids)
    total_errors = sum(int(corrupted[sid] != truths[sid][target]) for sid in determinate)
    U = upper_error_count(N, n, sample_errors, DELTA_COORD)
    rate = F(U, N)
    return {
        "sample_errors": sample_errors,
        "upper_error_count": U,
        "upper_error_rate": fstr(rate),
        "true_total_errors": total_errors,
        "certified": rate <= EPSILON,
    }


def abstention_accounting_control(target, population, predictions, truths):
    ordered = sorted(population)
    wrapped = dict((sid, predictions[sid][target]) for sid in ordered)
    for index, sid in enumerate(ordered):
        if index % 7 == 0 and wrapped[sid] in (0, 1):
            wrapped[sid] = "CANNOT_IDENTIFY"
    determinate = [sid for sid in ordered if wrapped[sid] in (0, 1)]
    abstentions = [sid for sid in ordered if wrapped[sid] == "CANNOT_IDENTIFY"]
    errors = sum(int(wrapped[sid] != truths[sid][target]) for sid in determinate)
    return {
        "total": len(ordered),
        "determinate": len(determinate),
        "abstentions": len(abstentions),
        "determinate_error_count": errors,
        "determinate_coverage": fstr(F(len(determinate), len(ordered))),
        "abstentions_counted_as_correct": False,
    }


def dependence_hostile():
    atoms = set(range(80))
    failure_sets = [{i} for i in range(4)]
    success_sets = [atoms - failures for failures in failure_sets]
    joint_good = set.intersection(*success_sets)
    marginal = F(79, 80)
    product = marginal ** 4
    actual = F(len(joint_good), 80)
    bound = F(1) - 4 * F(1, 80)
    return {
        "marginal_success_each": fstr(marginal),
        "actual_joint_success": fstr(actual),
        "union_bound_lower": fstr(bound),
        "independence_product": fstr(product),
        "actual_equals_bound": actual == bound,
        "independence_product_differs": product != actual,
        "independence_used": False,
    }


def build_receipt():
    population = load_population()
    samples = load_sample(population)
    mod, predictions, truths = _predict_all(population)
    coordinates = {
        target: _coordinate_stats(target, population, samples[target], predictions, truths)
        for target in TARGETS
    }
    corrupt = {
        target: corrupted_control(target, population, samples[target], predictions, truths)
        for target in TARGETS
    }
    abstention = abstention_accounting_control("memory_exact", population, predictions, truths)
    small = exhaustive_small_theorem_check(20)
    simultaneous_lower = F(1) - sum((DELTA_COORD for _ in TARGETS), F(0))
    return {
        "schema": "GMICapabilityCalibrationResultV1",
        "issue": 764,
        "claim_ceiling": "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE",
        "predictor_blob_sha": "937b91f6a3787ff04c2b5209c81d249518406859",
        "population_count": N,
        "sample_count_per_coordinate": n,
        "delta_total": fstr(DELTA_TOTAL),
        "delta_per_coordinate": fstr(DELTA_COORD),
        "simultaneous_coverage_lower_bound": fstr(simultaneous_lower),
        "epsilon": fstr(EPSILON),
        "coordinates": coordinates,
        "all_principal_coordinates_certified": all(
            row["terminal"] == "CALIBRATED_AT_REGISTERED_FINITE_POPULATION"
            for row in coordinates.values()
        ),
        "all_post_certificate_truths_covered": all(row["truth_covered"] for row in coordinates.values()),
        "corrupted_predictor_control": corrupt,
        "corrupted_control_has_failure": any(not row["certified"] for row in corrupt.values()),
        "abstention_accounting_control": abstention,
        "dependence_hostile": dependence_hostile(),
        "exhaustive_small_theorem_check": small,
        "iid_assumption": False,
        "replacement_sampling": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_receipt(), sort_keys=True, indent=2))
