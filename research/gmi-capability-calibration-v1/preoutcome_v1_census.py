from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Dict, Mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDICTOR_PATH = ROOT / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"
POPULATION_PATH = HERE / "AUDIT_POPULATION_V1.json"
SAMPLE_PATH = HERE / "AUDIT_SAMPLE_V1.json"
V1_SAMPLE_COMMIT = "1f1da8f3c14df07736bc2f5053a706b2fb35e192"


def _load_predictor_module():
    spec = importlib.util.spec_from_file_location("gmi_dev_predictor_v1", PREDICTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned predictor")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_census() -> Mapping[str, object]:
    mod = _load_predictor_module()
    population = json.loads(POPULATION_PATH.read_text())
    sample = json.loads(SAMPLE_PATH.read_text())
    rows = population["rows"]
    columns = population["columns"]
    if population.get("oracle_outcomes_included") is not False:
        raise ValueError("V1 pre-outcome census refuses a population containing oracle outcomes")
    if sample.get("oracle_outcomes_included") is not False:
        raise ValueError("V1 sample is not outcome-free")
    if sample.get("outcomes_seen_before_sample_commit") is not False:
        raise ValueError("V1 sample custody reports outcome access")
    if columns != ["specimen_id", *mod.AXES]:
        raise ValueError("unexpected population columns")
    if sample.get("sample_size_per_coordinate") != 64:
        raise ValueError("unexpected V1 sample size")
    predictor = mod.fit_registered_development_predictor()
    by_target: Dict[str, object] = {}
    for target in mod.TARGETS:
        determinate = 0
        abstentions = 0
        zeros = 0
        ones = 0
        for row in rows:
            point = dict(zip(mod.AXES, row[1:]))
            pred = predictor.predict_one(point, target)
            if pred == mod.CANNOT_IDENTIFY:
                abstentions += 1
            else:
                determinate += 1
                if pred == 0:
                    zeros += 1
                elif pred == 1:
                    ones += 1
                else:
                    raise AssertionError("unexpected determinate prediction")
        if determinate != 10:
            raise AssertionError("V1 determinacy census drift")
        by_target[target] = {
            "determinate": determinate,
            "abstentions": abstentions,
            "predicted_zero": zeros,
            "predicted_one": ones,
            "required_determinate_sample_size": 64,
            "determinate_sample_possible": False,
            "minimum_abstentions_in_any_64_cell_sample": 54,
        }
    return {
        "schema": "CapabilityCalibrationV1PreOutcomeCensus",
        "issue": 764,
        "population_count": len(rows),
        "oracle_outcomes_read_by_census": False,
        "sample_manifest_exists": True,
        "sample_manifest_commit": V1_SAMPLE_COMMIT,
        "sample_manifest_outcome_free": True,
        "sample_manifest_is_valid_under_frozen_determinate_rule": False,
        "targets": by_target,
        "terminal": "CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL",
    }


if __name__ == "__main__":
    print(json.dumps(build_census(), indent=2, sort_keys=True))
