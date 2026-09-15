from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Dict, Mapping, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDICTOR_PATH = ROOT / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"
EXPECTED_COUNTS = {
    "memory_exact": 4132,
    "planning_exact": 4382,
    "coordination_exact": 4132,
    "verified_tool_exact": 4382,
}


def _load_predictor_module():
    spec = importlib.util.spec_from_file_location("gmi_dev_predictor_v1", PREDICTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned predictor")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _raw_points() -> Tuple[Tuple[int, ...], ...]:
    points = []
    for point in itertools.product(range(-3, 4), repeat=5):
        if all(value in (-1, 0, 1) for value in point):
            continue
        points.append(tuple(point))
    if len(points) != 16564:
        raise AssertionError("raw candidate universe drift")
    return tuple(points)


def _fast_predictions(mod, predictor, point: Tuple[int, ...]) -> Dict[str, object]:
    query = dict(zip(mod.AXES, point))
    positive = {target: False for target in mod.TARGETS}
    negative = {target: False for target in mod.TARGETS}
    for record in predictor.records:
        rp = {axis: int(record[axis]) for axis in mod.AXES}
        below = all(rp[axis] <= query[axis] for axis in mod.AXES)
        above = all(query[axis] <= rp[axis] for axis in mod.AXES)
        caps = record["capabilities"]
        if below:
            for target in mod.TARGETS:
                if int(caps[target]) == 1:
                    positive[target] = True
        if above:
            for target in mod.TARGETS:
                if int(caps[target]) == 0:
                    negative[target] = True
    out: Dict[str, object] = {}
    for target in mod.TARGETS:
        if positive[target] and negative[target]:
            raise AssertionError("monotone envelope conflict")
        if positive[target]:
            out[target] = 1
        elif negative[target]:
            out[target] = 0
        else:
            out[target] = mod.CANNOT_IDENTIFY
    return out


def build_manifest() -> Mapping[str, object]:
    mod = _load_predictor_module()
    predictor = mod.fit_registered_development_predictor()
    raw = _raw_points()
    determinate = {target: [] for target in mod.TARGETS}
    for point in raw:
        preds = _fast_predictions(mod, predictor, point)
        for target in mod.TARGETS:
            if preds[target] != mod.CANNOT_IDENTIFY:
                payload = "T602-M5-AUDIT-V2|" + target + "|" + ",".join(map(str, point))
                digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                determinate[target].append((digest, point))

    coordinate_populations = {}
    for target in mod.TARGETS:
        rows = sorted(determinate[target], key=lambda item: (item[0], item[1]))
        if len(rows) != EXPECTED_COUNTS[target]:
            raise AssertionError(f"determinate-pool count drift for {target}")
        selected = rows[:128]
        ids = ["ACP2_" + digest[:16] for digest, _ in selected]
        if len(set(ids)) != 128:
            raise AssertionError("opaque specimen id collision")
        coordinate_populations[target] = {
            "determinate_pool_count": len(rows),
            "population_count": 128,
            "rows": [[sid, *point] for sid, (_, point) in zip(ids, selected)],
        }

    return {
        "schema": "CapabilityCalibrationPopulationV2",
        "issue": 764,
        "predictor_base_commit": "7e1103f1a5d1f453e7fd305e23824eacd61f7992",
        "predictor_blob_sha": "937b91f6a3787ff04c2b5209c81d249518406859",
        "raw_candidate_values": [-3, -2, -1, 0, 1, 2, 3],
        "excluded_development_cube_values": [-1, 0, 1],
        "raw_candidate_count": 16564,
        "columns": ["specimen_id", *mod.AXES],
        "oracle_outcomes_included": False,
        "predictor_binary_predictions_included": False,
        "generator": "coordinate-determinate-filter-then-sha256-sort-first-128",
        "domain_separator": "T602-M5-AUDIT-V2|<coordinate>|",
        "coordinate_populations": coordinate_populations,
    }


if __name__ == "__main__":
    print(json.dumps(build_manifest(), sort_keys=True, separators=(",", ":")))
