from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from fractions import Fraction as F
from math import comb
from pathlib import Path
from typing import Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
POPULATION_PATH = HERE / "AUDIT_POPULATION_V2.json"
SAMPLE_PATH = HERE / "AUDIT_SAMPLE_V2.json"
PREDICTOR_PATH = ROOT / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_predictor_module():
    return _load_module("gmi_dev_predictor_v1_calibration", PREDICTOR_PATH)


def _load_population_module():
    return _load_module("gmi_capability_population_v2", HERE / "materialize_population_v2.py")


def frac(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _check_dimensions(N: int, K: int, n: int) -> None:
    if any(type(v) is not int for v in (N, K, n)):
        raise ValueError("N,K,n must be exact integers")
    if N < 1 or n < 1 or n > N or K < 0 or K > N:
        raise ValueError("invalid finite-population dimensions")


def hypergeom_count(N: int, K: int, n: int, x: int) -> int:
    _check_dimensions(N, K, n)
    if type(x) is not int:
        raise ValueError("x must be exact integer")
    lo = max(0, n - (N - K))
    hi = min(n, K)
    if x < lo or x > hi:
        return 0
    return comb(K, x) * comb(N - K, n - x)


def hypergeom_pmf(N: int, K: int, n: int, x: int) -> F:
    return F(hypergeom_count(N, K, n, x), comb(N, n))


def hypergeom_cdf(N: int, K: int, n: int, x: int) -> F:
    _check_dimensions(N, K, n)
    if type(x) is not int:
        raise ValueError("x must be exact integer")
    if x < 0:
        return F(0)
    hi = min(x, n, K)
    lo = max(0, n - (N - K))
    if hi < lo:
        return F(0)
    return F(sum(hypergeom_count(N, K, n, j) for j in range(lo, hi + 1)), comb(N, n))


def upper_error_count(N: int, n: int, x: int, delta: F) -> int:
    if type(delta) is not F or not F(0) < delta < F(1):
        raise ValueError("delta must be exact Fraction in (0,1)")
    if type(x) is not int or x < 0 or x > n:
        raise ValueError("x outside sample range")
    admissible = [K for K in range(N + 1) if hypergeom_cdf(N, K, n, x) > delta]
    if not admissible:
        raise AssertionError("upper-bound inversion unexpectedly empty")
    return max(admissible)


def validate_manifests(population: Mapping[str, object], sample: Mapping[str, object], *, verify_population=True):
    if population.get("schema") != "CapabilityCalibrationPopulationV2":
        raise ValueError("wrong population schema")
    if sample.get("schema") != "CapabilityCalibrationSampleV2":
        raise ValueError("wrong sample schema")
    if verify_population:
        popmod = _load_population_module()
        if population != popmod.build_manifest():
            raise ValueError("committed V2 population does not match frozen generator")
    if population.get("oracle_outcomes_included") is not False:
        raise ValueError("population contains oracle outcomes")
    if population.get("predictor_binary_predictions_included") is not False:
        raise ValueError("population contains predictor values")
    if sample.get("outcomes_included") is not False:
        raise ValueError("sample contains outcomes")
    if sample.get("predictor_values_included") is not False:
        raise ValueError("sample contains predictor values")
    if sample.get("correctness_or_error_fields_included") is not False:
        raise ValueError("sample contains correctness/error fields")
    if sample.get("population_commit") != "282b7124fcabf93e5be8e2c77c9d7dce896f8d70":
        raise ValueError("sample points to wrong population commit")
    if sample.get("population_blob_sha") != "aaf0a6bce8f2dac4cf247b3c0e0b12d90c85bdd0":
        raise ValueError("sample points to wrong population blob")
    if sample.get("sampling_method") != "secrets.SystemRandom().sample" or sample.get("os_entropy") is not True:
        raise ValueError("sample method/custody metadata mismatch")
    if sample.get("reproducible_seed_recorded") is not False:
        raise ValueError("V2 sample must not expose an alternative seeded authority")

    populations = population["coordinate_populations"]
    samples = sample["coordinate_samples"]
    if set(populations) != set(samples):
        raise ValueError("coordinate mismatch between population and sample")
    for target, entry in populations.items():
        ids = entry["specimen_ids"]
        chosen = samples[target]
        if entry["population_count"] != 128 or len(ids) != 128 or len(set(ids)) != 128:
            raise ValueError("invalid fixed finite population")
        if len(chosen) != 64 or len(set(chosen)) != 64:
            raise ValueError("sample must contain 64 distinct ids")
        if not set(chosen).issubset(ids):
            raise ValueError("sample id outside frozen population")
    return True


def validate_custody():
    population = json.loads(POPULATION_PATH.read_text())
    sample = json.loads(SAMPLE_PATH.read_text())
    validate_manifests(population, sample, verify_population=True)
    return population, sample, _load_population_module()


def dependence_hostile() -> Mapping[str, object]:
    atoms = set(range(80))
    failures = ({0}, {1}, {2}, {3})
    union = set().union(*failures)
    actual_good = F(len(atoms - union), len(atoms))
    union_good = F(1) - 4 * F(1, 80)
    product_good = F(79, 80) ** 4
    if actual_good != union_good or actual_good == product_good:
        raise AssertionError("dependence hostile drift")
    return {
        "atoms": 80,
        "marginal_failure": "1/80",
        "actual_simultaneous_good": frac(actual_good),
        "union_bound_good": frac(union_good),
        "independence_product": frac(product_good),
        "independence_used": False,
    }


def build_sample_certificate() -> Mapping[str, object]:
    population, sample, popmod = validate_custody()
    predmod = _load_predictor_module()
    predictor = predmod.fit_registered_development_predictor()
    points = popmod.point_index()
    delta = F(1, 80)
    epsilon = F(1, 20)
    by_target = {}
    corrupted = {}
    abstention_accounting = {}

    for target in predmod.TARGETS:
        errors = 0
        chosen = sample["coordinate_samples"][target]
        for sid in chosen:
            point_tuple = points[target][sid]
            point = dict(zip(predmod.AXES, point_tuple))
            prediction = predictor.predict_one(point, target)
            if prediction == predmod.CANNOT_IDENTIFY:
                raise AssertionError("sample contains an abstaining point")
            truth = predmod.capability_oracle(point)[target]
            errors += int(int(prediction) != int(truth))

        upper = upper_error_count(128, 64, errors, delta)
        rate = F(upper, 128)
        terminal = (
            "CALIBRATED_AT_REGISTERED_FINITE_POPULATION"
            if rate <= epsilon
            else "CANNOT_CERTIFY_ERROR_RATE"
        )
        by_target[target] = {
            "sample_n": 64,
            "sample_errors": errors,
            "delta": "1/80",
            "upper_error_count": upper,
            "upper_error_rate": frac(rate),
            "epsilon": "1/20",
            "terminal": terminal,
        }

        corrupt_errors = 64
        corrupt_upper = upper_error_count(128, 64, corrupt_errors, delta)
        corrupt_rate = F(corrupt_upper, 128)
        corrupted[target] = {
            "sample_errors": corrupt_errors,
            "upper_error_count": corrupt_upper,
            "upper_error_rate": frac(corrupt_rate),
            "terminal": (
                "CALIBRATED_AT_REGISTERED_FINITE_POPULATION"
                if corrupt_rate <= epsilon
                else "CANNOT_CERTIFY_ERROR_RATE"
            ),
        }

        ordered = sorted(population["coordinate_populations"][target]["specimen_ids"])
        replaced = {sid for i, sid in enumerate(ordered, 1) if i % 7 == 0}
        abstention_accounting[target] = {
            "population_n": 128,
            "synthetic_abstentions": len(replaced),
            "remaining_determinate_denominator": 128 - len(replaced),
            "abstentions_counted_correct": False,
        }

    numeric_control = upper_error_count(128, 64, 0, F(1, 80))
    if numeric_control != 6:
        raise AssertionError("frozen U_delta(0)=6 control failed")
    if not all(row["terminal"] == "CANNOT_CERTIFY_ERROR_RATE" for row in corrupted.values()):
        raise AssertionError("corrupted-predictor sensitivity control failed")

    return {
        "schema": "CapabilityCalibrationSampleCertificateV2",
        "issue": 764,
        "parent_issue": 602,
        "sample_authority_commit": "5737a9efd113e8302810d21e4f798b82f1e4ecc0",
        "claim_ceiling": "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE",
        "N": 128,
        "n": 64,
        "delta_total": "1/20",
        "delta_per_coordinate": "1/80",
        "epsilon": "1/20",
        "simultaneous_coverage_lower_bound": "19/20",
        "coordinates": by_target,
        "numeric_control_U_at_zero": numeric_control,
        "corrupted_predictor_control": corrupted,
        "abstention_accounting_control": abstention_accounting,
        "dependence_hostile": dependence_hostile(),
        "full_population_census_performed": False,
    }


def custody_mutants_for_tests():
    population = json.loads(POPULATION_PATH.read_text())
    sample = json.loads(SAMPLE_PATH.read_text())
    duplicate = deepcopy(sample)
    target = sorted(duplicate["coordinate_samples"])[0]
    duplicate["coordinate_samples"][target][-1] = duplicate["coordinate_samples"][target][0]
    outsider = deepcopy(sample)
    outsider["coordinate_samples"][target][0] = "ACP2_NOT_IN_POPULATION"
    short = deepcopy(sample)
    short["coordinate_samples"][target] = short["coordinate_samples"][target][:-1]
    outcome = deepcopy(sample)
    outcome["outcomes_included"] = True
    return population, (duplicate, outsider, short, outcome)


if __name__ == "__main__":
    print(json.dumps(build_sample_certificate(), sort_keys=True, indent=2))
