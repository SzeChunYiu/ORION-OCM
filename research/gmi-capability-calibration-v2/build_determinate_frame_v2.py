from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREDICTOR_PATH = REPO / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"

AXES = (
    "memory_margin",
    "planning_margin",
    "communication_margin",
    "routing_margin",
    "verification_margin",
)
TARGETS = (
    "memory_exact",
    "planning_exact",
    "coordination_exact",
    "verified_tool_exact",
)
VALUES = (-3, -2, 2, 3)
DOMAIN_SEPARATOR = "T602-M5B-AUDIT-V2|"
PINNED_PREDICTOR_BLOB = "937b91f6a3787ff04c2b5209c81d249518406859"
PINNED_BASE = "7e1103f1a5d1f453e7fd305e23824eacd61f7992"


def _load_predictor_module():
    spec = importlib.util.spec_from_file_location("gmi_dev_predictor_v1", PREDICTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load predictor")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def specimen_id(values):
    raw = DOMAIN_SEPARATOR + ",".join(map(str, values))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return "AC2_" + digest[:16]


def build_frame():
    mod = _load_predictor_module()
    predictor = mod.fit_registered_development_predictor()
    frames = {}
    for target in TARGETS:
        rows = []
        for values in itertools.product(VALUES, repeat=len(AXES)):
            point = dict(zip(AXES, values))
            prediction = predictor.predict_one(point, target)
            if prediction in (0, 1):
                rows.append([specimen_id(values), *values, prediction])
            elif prediction != mod.CANNOT_IDENTIFY:
                raise AssertionError("unexpected predictor output")
        rows.sort(key=lambda row: row[0])
        if len(rows) != 64:
            raise RuntimeError("CANNOT_CHECK_DETERMINATE_FRAME_DRIFT: %s=%d" % (target, len(rows)))
        frames[target] = {
            "candidate_count": len(VALUES) ** len(AXES),
            "determinate_count": len(rows),
            "rows": rows,
        }
    return {
        "schema": "CapabilityCalibrationDeterminateFrameV2",
        "issue": 766,
        "predictor_base_commit": PINNED_BASE,
        "predictor_blob_sha": PINNED_PREDICTOR_BLOB,
        "candidate_grid_values": list(VALUES),
        "candidate_count": len(VALUES) ** len(AXES),
        "domain_separator": DOMAIN_SEPARATOR,
        "axes": list(AXES),
        "columns": ["specimen_id", *AXES, "frozen_prediction"],
        "oracle_outcomes_included": False,
        "correctness_fields_included": False,
        "coordinate_frames": frames,
    }


if __name__ == "__main__":
    print(json.dumps(build_frame(), sort_keys=True, separators=(",", ":")))
