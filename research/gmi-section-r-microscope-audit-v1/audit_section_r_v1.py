from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
MANIFEST_PATH = HERE / "MANIFEST_V1.json"

EXPECTED_IDS = (
    "architecture_derivation",
    "learning_law",
    "memory_differentiation",
    "concept_formation",
    "planning",
    "causal",
    "social_theory_of_mind",
    "teaching",
    "culture",
    "multi_species_ecology",
    "domain_collision",
    "capability_ceiling",
    "development_evolvability",
    "reachability_search_bias",
)


class AuditError(ValueError):
    pass


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuditError(f"{label} must be a non-empty string")
    return value.strip()


def _status(block: Mapping[str, Any], label: str) -> str:
    status = block.get("status")
    if status not in {"PASS", "GAP"}:
        raise AuditError(f"{label}.status must be PASS or GAP")
    return str(status)


def _validate_path(path_text: str, label: str) -> None:
    path = REPO_ROOT / path_text
    if not path.is_file():
        raise AuditError(f"{label} references missing file: {path_text}")


def validate_manifest(manifest: Mapping[str, Any]) -> Dict[str, Any]:
    if manifest.get("schema") != "GMI_SECTION_R_MICROSCOPE_AUDIT_V1":
        raise AuditError("wrong audit schema")
    if manifest.get("issue") != 809 or manifest.get("parent_issue") != 602:
        raise AuditError("wrong issue custody")
    if manifest.get("freeze_commit") != "74f1037102ddde7cad6d8eb66505f78109dfa74f":
        raise AuditError("freeze commit drift")

    registered = manifest.get("expected_class_ids")
    if registered != list(EXPECTED_IDS):
        raise AuditError("registered 14-class universe drift")

    classes = manifest.get("classes")
    if not isinstance(classes, list):
        raise AuditError("classes must be a list")
    ids = [entry.get("class_id") if isinstance(entry, Mapping) else None for entry in classes]
    if len(ids) != len(EXPECTED_IDS):
        raise AuditError("audit must contain exactly 14 class entries")
    if len(set(ids)) != len(ids):
        raise AuditError("duplicate class id or alias")
    if set(ids) != set(EXPECTED_IDS):
        raise AuditError("audit omits or adds a registered class")

    enum_pass: List[str] = []
    twin_pass: List[str] = []
    per_class: List[Dict[str, Any]] = []

    for entry in classes:
        if not isinstance(entry, Mapping):
            raise AuditError("each class entry must be an object")
        class_id = str(entry["class_id"])
        _nonempty(entry.get("claim_scope"), f"{class_id}.claim_scope")
        artifact = entry.get("canonical_artifact")
        if artifact is not None:
            artifact = _nonempty(artifact, f"{class_id}.canonical_artifact")
            _validate_path(artifact, f"{class_id}.canonical_artifact")

        enum = entry.get("enumerability")
        twin = entry.get("minimal_twin")
        if not isinstance(enum, Mapping) or not isinstance(twin, Mapping):
            raise AuditError(f"{class_id} must contain enumerability and minimal_twin blocks")

        enum_status = _status(enum, f"{class_id}.enumerability")
        twin_status = _status(twin, f"{class_id}.minimal_twin")

        if enum_status == "PASS":
            if artifact is None:
                raise AuditError(f"{class_id} enumerability PASS requires canonical artifact")
            finite = _nonempty(
                enum.get("finite_universe_definition"),
                f"{class_id}.enumerability.finite_universe_definition",
            )
            _nonempty(
                enum.get("certificate_or_exact_oracle"),
                f"{class_id}.enumerability.certificate_or_exact_oracle",
            )
            _nonempty(enum.get("replay"), f"{class_id}.enumerability.replay")
            evidence = _nonempty(enum.get("evidence_class"), f"{class_id}.enumerability.evidence_class")
            if evidence not in {"P2", "P1+P2"}:
                raise AuditError(f"{class_id} enumerability PASS must be P2 or P1+P2")
            lowered = finite.lower()
            if not any(token in lowered for token in ("all ", "every ", "exhaust", "complete")):
                raise AuditError(f"{class_id} PASS does not state a complete finite universe")
            enum_pass.append(class_id)
        else:
            _nonempty(enum.get("reason"), f"{class_id}.enumerability.reason")

        if twin_status == "PASS":
            twin_artifact = _nonempty(twin.get("twin_artifact"), f"{class_id}.minimal_twin.twin_artifact")
            _validate_path(twin_artifact, f"{class_id}.minimal_twin.twin_artifact")
            intervention = twin.get("intervention")
            if not isinstance(intervention, Mapping):
                raise AuditError(f"{class_id} minimal twin PASS requires intervention object")
            changed = intervention.get("changed_coordinates")
            if not isinstance(changed, list) or len(changed) != 1:
                if intervention.get("joint_intervention_is_atomic") is not True:
                    raise AuditError(
                        f"{class_id} minimal twin changes multiple/uncontrolled coordinates without atomic proof"
                    )
            order = twin.get("minimality_order")
            if not isinstance(order, Mapping) or order.get("finite") is not True:
                raise AuditError(f"{class_id} minimal twin PASS requires explicit finite minimality order")
            _nonempty(twin.get("minimality_proof"), f"{class_id}.minimal_twin.minimality_proof")
            twin_pass.append(class_id)
        else:
            _nonempty(twin.get("reason"), f"{class_id}.minimal_twin.reason")

        per_class.append(
            {
                "class_id": class_id,
                "enumerability": enum_status,
                "minimal_twin": twin_status,
            }
        )

    per_class.sort(key=lambda row: EXPECTED_IDS.index(row["class_id"]))
    enum_pass.sort(key=EXPECTED_IDS.index)
    twin_pass.sort(key=EXPECTED_IDS.index)
    enum_gaps = [cid for cid in EXPECTED_IDS if cid not in enum_pass]
    twin_gaps = [cid for cid in EXPECTED_IDS if cid not in twin_pass]

    result = {
        "schema": "GMI_SECTION_R_MICROSCOPE_AUDIT_RESULT_V1",
        "issue": 809,
        "parent_issue": 602,
        "freeze_commit": manifest["freeze_commit"],
        "claim_ceiling": manifest["claim_ceiling"],
        "registered_classes": len(EXPECTED_IDS),
        "enumerability": {
            "pass_count": len(enum_pass),
            "gap_count": len(enum_gaps),
            "pass_classes": enum_pass,
            "gap_classes": enum_gaps,
            "section_r_row_earned": len(enum_pass) == len(EXPECTED_IDS),
        },
        "minimal_negative_twin": {
            "pass_count": len(twin_pass),
            "gap_count": len(twin_gaps),
            "pass_classes": twin_pass,
            "gap_classes": twin_gaps,
            "section_r_row_earned": len(twin_pass) == len(EXPECTED_IDS),
        },
        "per_class": per_class,
        "historical_baseline": {
            "commit": "c1634aba8ce55da4811db14b9dd4bc554c602dd7",
            "world_types_with_any_witness": 11,
            "world_types_registered": 14,
            "families_with_any_negative_twin": 11,
            "families_audited_for_protocol": 19,
            "worked_enumerability_certificate_instances": 1,
            "scope": "stale presence-level audit used only as a hostile/conservative baseline, not current closure authority",
        },
        "ledger_policy": {
            "reconcile_enumerability_only_if_14_of_14": True,
            "reconcile_minimal_twin_only_if_14_of_14": True,
            "current_reconciliation_required": False,
        },
        "forbidden_promotions": list(manifest.get("forbidden_promotions", [])),
    }
    return result


def load_manifest(path: Path = MANIFEST_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise AuditError("manifest root must be an object")
    return data


def render_result(manifest: Mapping[str, Any] | None = None) -> str:
    data = load_manifest() if manifest is None else dict(manifest)
    result = validate_manifest(data)
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main() -> None:
    print(render_result(), end="")


if __name__ == "__main__":
    main()
