from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

CLAIM_CEILING = "GMI_REAL_SYSTEM_TRANSITION_VALIDATION_PROTOCOL_MACHINE_CHECKABLE"
REQUIRED = (
    "system_id", "system_version", "implementation_ref", "prediction_ref",
    "prediction_frozen_before_outcome", "evidence_kind", "task_or_workload_id",
    "before_context", "after_context", "predicted_before_property", "predicted_after_property",
    "observed_before_property", "observed_after_property", "classification_blind_to_target_family",
    "resources_before", "resources_after", "run_id_before", "run_id_after",
    "artifact_hash_before", "artifact_hash_after", "protected_outcome_leakage",
    "classification_identified",
)


def _nonempty(x: Any) -> bool:
    return x not in (None, "", [], {}, ())


def shape_errors(r: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = [k for k in REQUIRED if k not in r]
    if missing:
        errors.append("MISSING_FIELDS:" + ",".join(sorted(missing)))
        return errors
    for k in (
        "system_id", "system_version", "implementation_ref", "prediction_ref", "task_or_workload_id",
        "before_context", "after_context", "predicted_before_property", "predicted_after_property",
        "observed_before_property", "observed_after_property", "run_id_before", "run_id_after",
        "artifact_hash_before", "artifact_hash_after",
    ):
        if not _nonempty(r[k]):
            errors.append(f"EMPTY:{k}")
    for k in ("resources_before", "resources_after"):
        v = r[k]
        if not isinstance(v, list) or not v or any(not isinstance(x, (int, float)) or x < 0 for x in v):
            errors.append(f"INVALID:{k}")
    return errors


def real_receipt_errors(r: Mapping[str, Any]) -> list[str]:
    errors = shape_errors(r)
    if errors:
        return errors
    if r["evidence_kind"] != "REAL_SYSTEM":
        errors.append("NOT_REAL_SYSTEM_EVIDENCE")
    if r["prediction_frozen_before_outcome"] is not True:
        errors.append("PREDICTION_NOT_PREOUTCOME")
    if r["classification_blind_to_target_family"] is not True:
        errors.append("TARGET_FAMILY_VISIBLE_TO_CLASSIFIER")
    if r["protected_outcome_leakage"] is not False:
        errors.append("PROTECTED_OUTCOME_LEAKAGE")
    if r["classification_identified"] is not True:
        errors.append("MORPHOLOGY_NOT_IDENTIFIED")
    if r["predicted_before_property"] == r["predicted_after_property"]:
        errors.append("NO_PREDICTED_TRANSITION")
    if r["observed_before_property"] == r["observed_after_property"]:
        errors.append("NO_OBSERVED_TRANSITION")
    if r["predicted_before_property"] != r["observed_before_property"] or r["predicted_after_property"] != r["observed_after_property"]:
        errors.append("PREDICTION_OBSERVATION_MISMATCH")
    return errors


def evaluate(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    accepted: list[str] = []
    rejected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, r in enumerate(receipts):
        errors = real_receipt_errors(r)
        sid = str(r.get("system_id", ""))
        if not errors and sid in seen:
            errors = ["DUPLICATE_SYSTEM_ID"]
        if errors:
            rejected.append({"index": i, "system_id": sid, "reasons": errors})
        else:
            accepted.append(sid)
            seen.add(sid)
    terminal = (
        "REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE"
        if len(accepted) >= 5
        else "INSUFFICIENT_REAL_SYSTEM_EVIDENCE"
    )
    return {
        "terminal": terminal,
        "qualifying_count": len(accepted),
        "qualifying_system_ids": accepted,
        "rejected": rejected,
    }


def protocol_fixture(i: int, evidence_kind: str = "PROTOCOL_FIXTURE") -> dict[str, Any]:
    return {
        "system_id": f"fixture-{i}",
        "system_version": "v1",
        "implementation_ref": f"fixture://impl/{i}",
        "prediction_ref": f"fixture://prediction/{i}",
        "prediction_frozen_before_outcome": True,
        "evidence_kind": evidence_kind,
        "task_or_workload_id": f"fixture-task-{i}",
        "before_context": {"resource_price": 1},
        "after_context": {"resource_price": 2},
        "predicted_before_property": "A",
        "predicted_after_property": "B",
        "observed_before_property": "A",
        "observed_after_property": "B",
        "classification_blind_to_target_family": True,
        "resources_before": [1, 2, 3],
        "resources_after": [2, 2, 3],
        "run_id_before": f"run-before-{i}",
        "run_id_after": f"run-after-{i}",
        "artifact_hash_before": f"hash-before-{i}",
        "artifact_hash_after": f"hash-after-{i}",
        "protected_outcome_leakage": False,
        "classification_identified": True,
    }


def finite_certificate() -> dict[str, Any]:
    checks: dict[str, bool] = {}
    fixture = protocol_fixture(0)
    checks["protocol_fixture_shape_valid"] = shape_errors(fixture) == []
    checks["protocol_fixture_never_counts_as_real"] = evaluate([fixture])["qualifying_count"] == 0

    five_fake_real = [protocol_fixture(i, "REAL_SYSTEM") for i in range(5)]
    checks["validator_positive_logic_fixture"] = evaluate(five_fake_real)["terminal"] == "REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE"

    hostiles = {}
    mutations = {
        "synthetic": lambda r: r.update(evidence_kind="SYNTHETIC"),
        "postoutcome": lambda r: r.update(prediction_frozen_before_outcome=False),
        "missing_resources": lambda r: r.update(resources_after=[]),
        "family_visible": lambda r: r.update(classification_blind_to_target_family=False),
        "leakage": lambda r: r.update(protected_outcome_leakage=True),
        "unidentified": lambda r: r.update(classification_identified=False),
        "no_transition": lambda r: r.update(observed_after_property="A", predicted_after_property="A"),
        "mismatch": lambda r: r.update(observed_after_property="C"),
    }
    for name, mutate in mutations.items():
        r = protocol_fixture(100, "REAL_SYSTEM")
        mutate(r)
        hostiles[name] = bool(real_receipt_errors(r))
    checks["all_registered_hostiles_rejected"] = all(hostiles.values())

    duplicate = [protocol_fixture(1, "REAL_SYSTEM"), protocol_fixture(1, "REAL_SYSTEM")]
    dup_eval = evaluate(duplicate)
    checks["duplicate_system_rejected"] = dup_eval["qualifying_count"] == 1 and any(
        "DUPLICATE_SYSTEM_ID" in x["reasons"] for x in dup_eval["rejected"]
    )

    current = evaluate([])
    checks["zero_real_receipts_fails_closed"] = current["terminal"] == "INSUFFICIENT_REAL_SYSTEM_EVIDENCE" and current["qualifying_count"] == 0

    if not all(checks.values()):
        raise AssertionError(checks)
    return {
        "schema": "GMI_833_REAL_TRANSITION_PROTOCOL_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "checks": checks,
        "current_scientific_evidence": current,
        "hostiles": hostiles,
        "scientific_row_earned": False,
        "forbidden_promotions": [
            "FIVE_REAL_SYSTEM_TRANSITIONS_VALIDATED",
            "REAL_SYSTEM_MORPHOLOGY_TRANSITIONS_VALIDATED",
            "COMPLETE_GMI",
        ],
    }


def main() -> None:
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
