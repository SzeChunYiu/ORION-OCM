from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

HERE = Path(__file__).resolve().parent


def _read(name: str):
    return json.loads((HERE / name).read_text())


def build_result() -> Mapping[str, object]:
    v1 = _read("V1_PREOUTCOME_CENSUS.json")
    population = _read("AUDIT_POPULATION_V2.json")
    sample = _read("AUDIT_SAMPLE_V2.json")
    cert = _read("SAMPLE_CERTIFICATE_V2.json")
    census = _read("FULL_POPULATION_CENSUS_V2.json")

    if v1["terminal"] != "CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL":
        raise AssertionError("V1 negative terminal drift")
    if v1["sample_manifest_is_valid_under_frozen_determinate_rule"] is not False:
        raise AssertionError("V1 invalid-sample boundary drift")
    if sample["sample_size_per_coordinate"] != 64:
        raise AssertionError("V2 sample-size drift")
    if cert["simultaneous_coverage_lower_bound"] != "19/20":
        raise AssertionError("simultaneous coverage drift")
    if not census["all_coordinates_covered"]:
        raise AssertionError("post-certificate census failed")

    coordinates = {}
    for target in sorted(cert["coordinates"]):
        sample_row = cert["coordinates"][target]
        census_row = census["coordinates"][target]
        if sample_row["terminal"] != "CALIBRATED_AT_REGISTERED_FINITE_POPULATION":
            raise AssertionError(f"principal coordinate did not certify: {target}")
        if not census_row["certificate_covers_true_error_count"]:
            raise AssertionError(f"full census escaped certificate: {target}")
        coordinates[target] = {
            "determinate_pool_count": population["coordinate_populations"][target]["determinate_pool_count"],
            "selected_population_n": population["coordinate_populations"][target]["population_count"],
            "sample_n": sample_row["sample_n"],
            "sample_errors": sample_row["sample_errors"],
            "upper_error_count": sample_row["upper_error_count"],
            "upper_error_rate": sample_row["upper_error_rate"],
            "true_population_error_count_post_certificate": census_row["true_error_count"],
            "terminal": sample_row["terminal"],
        }

    corrupted_fail_closed = all(
        row["terminal"] == "CANNOT_CERTIFY_ERROR_RATE"
        for row in cert["corrupted_predictor_control"].values()
    )
    if not corrupted_fail_closed:
        raise AssertionError("corrupted-predictor control did not fail closed")

    return {
        "schema": "GMICapabilityCalibrationResultV2",
        "issue": 764,
        "parent_issue": 602,
        "v1_disposition": v1["terminal"],
        "v1_outcome_free_sample_preserved_but_invalid": True,
        "v2_raw_candidate_count": population["raw_candidate_count"],
        "v2_sample_authority_commit": cert["sample_authority_commit"],
        "v2_sample_certificate_commit": census["sample_certificate_authority_commit"],
        "delta_total": cert["delta_total"],
        "delta_per_coordinate": cert["delta_per_coordinate"],
        "simultaneous_coverage_lower_bound": cert["simultaneous_coverage_lower_bound"],
        "epsilon": cert["epsilon"],
        "coordinates": coordinates,
        "corrupted_predictor_control_fail_closed": corrupted_fail_closed,
        "abstentions_counted_as_correct": False,
        "dependence_independence_assumption": False,
        "exhaustive_small_oracle_cases": 12320,
        "full_population_census_after_sample_certificate": True,
        "claim_ceiling": "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE",
        "section_m_disposition": "CALIBRATE_CAPABILITY_PREDICTION_UNCERTAINTY_SUPPORTED_AT_REGISTERED_FINITE_SCOPE",
        "nonclaims": [
            "PER_EXAMPLE_PROBABILITIES_CALIBRATED",
            "IID_GENERALIZATION",
            "REAL_WORLD_CAPABILITY_CALIBRATION",
            "UNIVERSAL_G6",
            "COMPLETE_GMI"
        ]
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), sort_keys=True, indent=2))
