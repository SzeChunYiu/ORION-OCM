from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
from typing import Dict, Mapping

ROOT = pathlib.Path(__file__).resolve().parent
PREDICTOR_PATH = ROOT.parent / "gmi-capability-predictor-dev-v1" / "dev_predictor_v1.py"
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", PREDICTOR_PATH)
predictor_mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development predictor")
SPEC.loader.exec_module(predictor_mod)

AXES = predictor_mod.AXES
CANNOT_IDENTIFY = predictor_mod.CANNOT_IDENTIFY
SYSTEM_CAPACITY = {axis: 3 for axis in AXES}
SOURCE_REQUIREMENTS = {axis: 3 for axis in AXES}
HELD_TASK_REQUIREMENTS = {
    "HTF_001": dict(SOURCE_REQUIREMENTS),
    "HTF_002": {**SOURCE_REQUIREMENTS, "memory_margin": 5},
    "HTF_003": {**SOURCE_REQUIREMENTS, "communication_margin": 5},
    "HTF_004": {**SOURCE_REQUIREMENTS, "routing_margin": 5},
    "HTF_005": {**SOURCE_REQUIREMENTS, "verification_margin": 5},
    "HTF_006": {**SOURCE_REQUIREMENTS, "memory_margin": 1, "planning_margin": 5},
}
OUTCOME_FIELDS = {"observed_capabilities", "observed_outcome", "score", "pass_fail"}


def _validate_vector(values: Mapping[str, int], name: str) -> Dict[str, int]:
    if set(values) != set(AXES):
        raise ValueError(f"{name} must contain exactly the registered axes")
    out: Dict[str, int] = {}
    for axis in AXES:
        value = values[axis]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name}.{axis} must be a nonnegative integer")
        out[axis] = value
    return out


def margins(capacity: Mapping[str, int], requirements: Mapping[str, int]) -> Dict[str, int]:
    c = _validate_vector(capacity, "capacity")
    r = _validate_vector(requirements, "requirements")
    return {axis: c[axis] - r[axis] for axis in AXES}


def _canonical_digest(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_freeze_manifest() -> Dict[str, object]:
    predictor = predictor_mod.fit_registered_development_predictor()
    source_margins = margins(SYSTEM_CAPACITY, SOURCE_REQUIREMENTS)
    source_prediction = predictor.predict_vector(source_margins)

    targets = []
    for family_id in sorted(HELD_TASK_REQUIREMENTS):
        if re.fullmatch(r"HTF_\d{3}", family_id) is None:
            raise ValueError("held task-family IDs must be opaque HTF_### identifiers")
        requirements = HELD_TASK_REQUIREMENTS[family_id]
        target_margins = margins(SYSTEM_CAPACITY, requirements)
        row = {
            "task_family_id": family_id,
            "requirements": requirements,
            "margins": target_margins,
            "frozen_prediction": predictor.predict_vector(target_margins),
        }
        row["family_digest"] = _canonical_digest(row)
        targets.append(row)

    manifest: Dict[str, object] = {
        "schema_version": "1.0",
        "issue": 602,
        "section": "F4 capability predictor",
        "ledger_row": "Predict transfer across task families.",
        "scope": "prospective transfer predictions for one fixed structural system evaluated on six opaque target task families whose obligations are represented only by registered requirement vectors",
        "assumptions": [
            "the system capacity vector is fixed across source and target task families",
            "target task requirements are frozen before target outcomes are computed",
            "task-family IDs are opaque and unavailable to the predictor",
            "transfer is mediated only by target signed margins capacity-requirement",
            "CANNOT_IDENTIFY is a valid frozen transfer prediction and may not be edited after scoring",
        ],
        "evidence_class": ["P1", "P2"],
        "claim_ceiling": "G2",
        "status": "FROZEN_NOT_YET_SCORED",
        "outcomes_present": False,
        "outcome_fields_forbidden": sorted(OUTCOME_FIELDS),
        "strongest_parent": "task transfer under sufficient statistics / invariant risk structure / protected holdout evaluation",
        "negative_twin": "HTF_001 is an opaque task-family remint with exactly the source requirements; its frozen capability vector must be invariant",
        "nearest_counterexample": "if task identity carries causal information not represented in requirements, or transfer changes morphology/development state, target margins are not sufficient and this transfer law fails",
        "falsifier": "Any frozen prediction uses a task-family name, any target outcome is present before scoring, any target prediction differs from the already-fitted development predictor applied to target margins, HTF_001 changes under reminting, or the freeze receipt is edited after scoring",
        "system_capacity": SYSTEM_CAPACITY,
        "source_task": {
            "task_family_id": "SOURCE_DEV_TASK",
            "requirements": SOURCE_REQUIREMENTS,
            "margins": source_margins,
            "source_prediction": source_prediction,
        },
        "target_task_families": targets,
    }
    manifest["freeze_digest"] = _canonical_digest(manifest)
    return manifest


def validate_clean_freeze(manifest: Mapping[str, object]) -> None:
    if manifest.get("outcomes_present") is not False:
        raise ValueError("outcomes must not be present in the freeze")
    text = json.dumps(manifest, sort_keys=True).lower()
    for field in OUTCOME_FIELDS:
        # The allowlisted declaration of forbidden fields is permitted; actual
        # nested outcome values are not.
        if f'"{field}":' in text:
            raise ValueError(f"outcome field leaked before scoring: {field}")
    targets = manifest["target_task_families"]
    if len(targets) != 6:
        raise ValueError("exactly six held task families are registered")


def render_manifest() -> str:
    return json.dumps(build_freeze_manifest(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    print(render_manifest(), end="")
