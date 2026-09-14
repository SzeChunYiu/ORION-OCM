from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
from typing import Dict, List, Mapping

ROOT = pathlib.Path(__file__).resolve().parent
PREDICTOR_PATH = ROOT.parent / "gmi-capability-predictor-dev-v1" / "dev_predictor_v1.py"
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", PREDICTOR_PATH)
predictor_mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development predictor")
SPEC.loader.exec_module(predictor_mod)

CANNOT_IDENTIFY = predictor_mod.CANNOT_IDENTIFY

HELD_FAMILY_POINTS = {
    "HF_UPPER_RAY": [
        {"memory_margin": 2, "planning_margin": 0, "communication_margin": 0, "routing_margin": 0, "verification_margin": 0},
        {"memory_margin": 3, "planning_margin": 1, "communication_margin": 1, "routing_margin": 1, "verification_margin": 1}
    ],
    "HF_STATE_DEFICIT": [
        {"memory_margin": -2, "planning_margin": 0, "communication_margin": 0, "routing_margin": 0, "verification_margin": 0},
        {"memory_margin": -3, "planning_margin": 1, "communication_margin": 1, "routing_margin": 1, "verification_margin": 1}
    ],
    "HF_PLAN_DEFICIT": [
        {"memory_margin": 0, "planning_margin": -2, "communication_margin": 0, "routing_margin": 0, "verification_margin": 0},
        {"memory_margin": 1, "planning_margin": -3, "communication_margin": 1, "routing_margin": 1, "verification_margin": 1}
    ],
    "HF_COMM_DEFICIT": [
        {"memory_margin": 0, "planning_margin": 0, "communication_margin": -2, "routing_margin": 0, "verification_margin": 0},
        {"memory_margin": 1, "planning_margin": 1, "communication_margin": -3, "routing_margin": 1, "verification_margin": 1}
    ],
    "HF_ROUTE_DEFICIT": [
        {"memory_margin": 0, "planning_margin": 0, "communication_margin": 0, "routing_margin": -2, "verification_margin": 0},
        {"memory_margin": 1, "planning_margin": 1, "communication_margin": 1, "routing_margin": -3, "verification_margin": 1}
    ],
    "HF_VERIFY_DEFICIT": [
        {"memory_margin": 0, "planning_margin": 0, "communication_margin": 0, "routing_margin": 0, "verification_margin": -2},
        {"memory_margin": 1, "planning_margin": 1, "communication_margin": 1, "routing_margin": 1, "verification_margin": -3}
    ]
}


def _canonical_digest(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _walk_keys(value):
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def build_freeze_manifest() -> Dict[str, object]:
    predictor = predictor_mod.fit_registered_development_predictor()
    families: List[Dict[str, object]] = []
    for family_id in sorted(HELD_FAMILY_POINTS):
        members = []
        for index, point in enumerate(HELD_FAMILY_POINTS[family_id]):
            prediction = predictor.predict_vector(point)
            members.append({
                "member_id": f"{family_id}_{index}",
                "descriptor_margins": dict(point),
                "frozen_prediction": prediction,
            })
        family_payload = {"family_id": family_id, "members": members}
        family_payload["family_digest"] = _canonical_digest(family_payload)
        families.append(family_payload)

    manifest: Dict[str, object] = {
        "schema_version": "1.0",
        "issue": 602,
        "section": "F4 capability predictor",
        "ledger_row": "Freeze held-family predictions.",
        "scope": "six opaque held morphology families, each disjoint from the {-1,0,1}^5 development cube",
        "assumptions": [
            "held-family generator points are fixed before any held outcome computation",
            "the fitted predictor is exactly the development-only predictor from research/gmi-capability-predictor-dev-v1",
            "family IDs are opaque and carry no architecture semantics",
            "CANNOT_IDENTIFY is a valid frozen prediction and may not be replaced after outcomes are seen"
        ],
        "evidence_class": ["P1", "P2"],
        "claim_ceiling": "G2",
        "status": "FROZEN_NOT_YET_SCORED",
        "outcomes_present": False,
        "outcome_fields_forbidden": ["observed_capabilities", "observed_outcome", "score", "pass_fail"],
        "strongest_parent": "prospective preregistration / protected holdout evaluation",
        "negative_twin": "add an observed held outcome before freezing; the freeze validator must reject the manifest",
        "nearest_counterexample": "a post-outcome prediction file can match perfectly without predictive content and therefore does not count",
        "falsifier": "Any family overlaps the development cube, any held outcome is present before scoring, any frozen prediction differs from the already-fitted predictor, or predictions are edited after the freeze receipt.",
        "families": families,
    }
    manifest["freeze_digest"] = _canonical_digest(manifest)
    return manifest


def validate_freeze_manifest(manifest: Mapping[str, object]) -> None:
    required = {
        "scope", "assumptions", "evidence_class", "strongest_parent", "negative_twin",
        "nearest_counterexample", "falsifier", "claim_ceiling", "status", "families",
        "freeze_digest", "outcomes_present", "outcome_fields_forbidden"
    }
    if not required.issubset(manifest):
        raise ValueError("freeze manifest missing claim-gate metadata")
    if manifest["outcomes_present"] is not False:
        raise ValueError("held outcomes must be absent at freeze time")
    forbidden = set(manifest["outcome_fields_forbidden"])
    used_keys = set(_walk_keys(manifest)) - {"outcome_fields_forbidden"}
    leaked = forbidden.intersection(used_keys)
    if leaked:
        raise ValueError(f"held outcome fields leaked into freeze: {sorted(leaked)}")

    predictor = predictor_mod.fit_registered_development_predictor()
    for family in manifest["families"]:
        family_without_digest = dict(family)
        claimed_family_digest = family_without_digest.pop("family_digest")
        if _canonical_digest(family_without_digest) != claimed_family_digest:
            raise ValueError("family digest mismatch")
        family_id = family["family_id"]
        if not isinstance(family_id, str) or not family_id.startswith("HF_"):
            raise ValueError("held family IDs must be opaque HF_ identifiers")
        for member in family["members"]:
            point = member["descriptor_margins"]
            if not any(abs(int(value)) > 1 for value in point.values()):
                raise ValueError("held member overlaps the development cube")
            expected = predictor.predict_vector(point)
            if member["frozen_prediction"] != expected:
                raise ValueError("frozen prediction does not match prefit predictor")

    without_freeze_digest = dict(manifest)
    claimed_freeze_digest = without_freeze_digest.pop("freeze_digest")
    if _canonical_digest(without_freeze_digest) != claimed_freeze_digest:
        raise ValueError("freeze digest mismatch")


def render_manifest() -> str:
    return json.dumps(build_freeze_manifest(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    built = build_freeze_manifest()
    validate_freeze_manifest(built)
    print(json.dumps(built, indent=2, sort_keys=True))
