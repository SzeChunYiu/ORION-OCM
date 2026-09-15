from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAMPLE_CERT_PATH = HERE / "SAMPLE_CERTIFICATE_V2.json"
PREDICTOR_PATH = ROOT / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_full_census() -> Mapping[str, object]:
    cal = _load("cal_v2_for_census", HERE / "capability_calibration_v2.py")
    pop = _load("pop_v2_for_census", HERE / "materialize_population_v2.py")
    pred = _load("predictor_v1_for_census", PREDICTOR_PATH)

    committed_sample_certificate = json.loads(SAMPLE_CERT_PATH.read_text())
    regenerated_sample_certificate = cal.build_sample_certificate()
    if committed_sample_certificate != regenerated_sample_certificate:
        raise ValueError("sample certificate drift before full census")
    if committed_sample_certificate.get("full_population_census_performed") is not False:
        raise ValueError("sample certificate must predate full census")

    predictor = pred.fit_registered_development_predictor()
    points = pop.point_index()
    rows = {}
    for target in pred.TARGETS:
        errors = 0
        for sid, point_tuple in points[target].items():
            point = dict(zip(pred.AXES, point_tuple))
            prediction = predictor.predict_one(point, target)
            if prediction == pred.CANNOT_IDENTIFY:
                raise AssertionError("frozen V2 population contains an abstention")
            truth = pred.capability_oracle(point)[target]
            errors += int(int(prediction) != int(truth))
        upper = int(committed_sample_certificate["coordinates"][target]["upper_error_count"])
        rows[target] = {
            "population_n": 128,
            "true_error_count": errors,
            "sample_certificate_upper_error_count": upper,
            "certificate_covers_true_error_count": errors <= upper,
        }
        if errors > upper:
            raise AssertionError("sample certificate failed to cover full-population truth")

    return {
        "schema": "CapabilityCalibrationFullPopulationCensusV2",
        "issue": 764,
        "parent_issue": 602,
        "sample_certificate_authority_commit": "1f7c29a3ef470957add504adfbe1ab375b933261",
        "coordinates": rows,
        "all_coordinates_covered": all(row["certificate_covers_true_error_count"] for row in rows.values()),
        "statistical_inputs_changed_after_census": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_full_census(), sort_keys=True, indent=2))
