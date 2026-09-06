"""Fixed Stanza successor binding for the existing two-arm capture."""
from datetime import datetime
import json
from pathlib import Path
import g1_stanza_profile as P

PREDECESSOR_SHA = "b1175b39f06f8399dd96884f8013195062a44a64c76cb5d0bb7df36984f928c6"

FIXED_FIELDS = ("public_items_sha256", "selection_sha256", "forms_only_source_sha256",
    "freeze_source_sha256", "syntax_count", "clia_count", "order",
    "restart_after_every_items", "chunks", "outer_seconds_per_chunk",
    "native_bounds", "arm_order", "retries")


def bind(plan_dir, plan, model, training_path, profile_path):
    profile = P.validate(json.loads(profile_path.read_text()))
    predecessor = plan_dir/"predecessor-plan.json"
    P.require_hash(predecessor, PREDECESSOR_SHA)
    old = json.loads(predecessor.read_text())
    if plan.get("predecessor_plan_sha256") != P.digest_bytes(predecessor.read_bytes()):
        raise ValueError("successor predecessor binding")
    if any(plan.get(k) != old[k] for k in FIXED_FIELDS):
        raise ValueError("fixed public stream, cadence or donor allowances changed")
    if datetime.fromisoformat(plan["registered_utc"]) <= datetime.fromisoformat(old["registered_utc"]):
        raise ValueError("successor needs a new prospective registration")
    if (plan.get("donor") != "stanza-recurrent" or
        plan.get("donor_profile_id") != profile["id"] or
        plan.get("model_role") != "IMPORTED_FIXED_RECURRENT_DONOR" or
        plan.get("training_lineage_sha256") != P.LINEAGE_SHA):
        raise ValueError("fixed successor role/profile binding")
    if "TRAIN-only UDPipe" in plan.get("required_model", ""):
        raise ValueError("successor must not inherit the UDPipe training claim")
    P.require_hash(training_path, P.LINEAGE_SHA)
    models = P.verify_models(model, profile)
    training = {"model_sha256": profile["model_sha256"],
        "role": "IMPORTED_STANZA_TRAINING_LINEAGE", "lineage_sha256": P.LINEAGE_SHA,
        "lineage": json.loads(training_path.read_text()),
        "original_training_costs": "UNKNOWN", "training_reproduced_here": False}
    return profile, training, {"donor": "stanza-recurrent", "donor_profile": profile,
        "model_file_inventory": models,
        "model_bytes": sum(v["bytes"] for v in models.values()),
        "profile_bytes": len(P.encoded(profile)),
        "model_bytes_scope": "Four checkpoints plus resources; archived profile counted separately.",
        "training_manifest_content_sha256": P.digest(training)}


def stable_files(model, training_path, profile_path, profile):
    P.verify_models(model, profile)
    return {str(training_path): P.digest_bytes(training_path.read_bytes()),
            str(profile_path): P.digest_bytes(profile_path.read_bytes())}
