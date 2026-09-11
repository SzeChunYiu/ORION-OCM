"""Validate private H1 coding-K1 task custody manifests before execution.

The manifest itself may remain in protected evaluator custody.  This validator is
public so the admission rule is frozen before any protected outcome access.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

from code_k1_localization_metrics import canonical_repo_path


SCHEMA = "ocm.gmi-e3.code-k1-task-manifest.v1"
FAMILIES = {
    "F1_INTERFACE_SCHEMA_MIGRATION",
    "F2_STALE_DERIVED_STATE",
    "F3_FAILURE_CLEANUP_LIFECYCLE",
}
ROLES = {"DEVELOPMENT", "PROTECTED"}
REQUIRED_TOP = {
    "schema",
    "protocol_version",
    "model_identity_digest",
    "harness_identity_digest",
    "verifier_environment_digest",
    "generic_identifier_allowlist",
    "tasks",
}
REQUIRED_TASK = {
    "task_id",
    "family_id",
    "role",
    "author_or_generator_id",
    "base_repo_digest",
    "mutated_repo_digest",
    "task_statement_digest",
    "public_test_digest",
    "protected_test_digest",
    "mutation_receipt_digest",
    "fault_operator_id",
    "fault_files",
    "fault_regions_digest",
    "mutation_patch_digest",
    "reference_repair_digest",
    "exposed_identifiers",
    "exposed_artifact_digests",
    "base_full_suite_passed",
    "mutated_full_suite_failed",
    "solver_visible_family_label",
    "solver_visible_mutation_receipt",
    "solver_visible_protected_tests",
    "solver_visible_reference_repair",
}
HIDDEN_FLAGS = {
    "solver_visible_family_label",
    "solver_visible_mutation_receipt",
    "solver_visible_protected_tests",
    "solver_visible_reference_repair",
}


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def _duplicates(values: list[str]) -> set[str]:
    return {value for value, count in Counter(values).items() if count > 1}


def validate_manifest(manifest: Mapping[str, Any], *, enforce_h1a_minimum: bool = True) -> list[str]:
    errors: list[str] = []

    missing_top = REQUIRED_TOP - set(manifest)
    if missing_top:
        errors.append(f"missing top-level fields: {sorted(missing_top)}")

    if manifest.get("schema") != SCHEMA:
        errors.append(f"expected schema {SCHEMA!r}")

    for field in (
        "protocol_version",
        "model_identity_digest",
        "harness_identity_digest",
        "verifier_environment_digest",
    ):
        if field in manifest and not _nonempty(manifest[field]):
            errors.append(f"{field} must be nonempty")

    allowlist_raw = manifest.get("generic_identifier_allowlist", [])
    if not isinstance(allowlist_raw, list):
        errors.append("generic_identifier_allowlist must be a list")
        allowlist: set[str] = set()
    else:
        allowlist = {str(value) for value in allowlist_raw}

    tasks = manifest.get("tasks")
    if not isinstance(tasks, list):
        return errors + ["tasks must be a list"]
    if not tasks:
        return errors + ["tasks must be nonempty"]

    task_ids: list[str] = []
    mutated_digests: list[str] = []
    statement_digests: list[str] = []
    role_counts: dict[str, Counter] = defaultdict(Counter)
    development_identifiers: set[str] = set()
    protected_identifiers: set[str] = set()
    development_artifacts: set[str] = set()
    protected_secret_digests: set[str] = set()

    for index, task in enumerate(tasks):
        prefix = f"task[{index}]"
        if not isinstance(task, Mapping):
            errors.append(f"{prefix} must be a mapping")
            continue

        missing = REQUIRED_TASK - set(task)
        if missing:
            errors.append(f"{prefix} missing fields: {sorted(missing)}")
            continue

        for field in REQUIRED_TASK - HIDDEN_FLAGS - {
            "exposed_identifiers",
            "exposed_artifact_digests",
        }:
            if not _nonempty(task.get(field)):
                errors.append(f"{prefix}.{field} must be nonempty")

        family = task.get("family_id")
        role = task.get("role")
        if family not in FAMILIES:
            errors.append(f"{prefix}.family_id not in frozen family set: {family!r}")
        if role not in ROLES:
            errors.append(f"{prefix}.role invalid: {role!r}")

        if family in FAMILIES and role in ROLES:
            role_counts[family][role] += 1

        if task.get("base_repo_digest") == task.get("mutated_repo_digest"):
            errors.append(f"{prefix}: base_repo_digest equals mutated_repo_digest")
        if task.get("base_full_suite_passed") is not True:
            errors.append(f"{prefix}: base repository must pass full evaluator before mutation")
        if task.get("mutated_full_suite_failed") is not True:
            errors.append(f"{prefix}: mutated repository must fail full evaluator after mutation")

        for flag in HIDDEN_FLAGS:
            if task.get(flag) is not False:
                errors.append(f"{prefix}.{flag} must be false")

        fault_files = task.get("fault_files")
        if not isinstance(fault_files, list) or not fault_files:
            errors.append(f"{prefix}.fault_files must be a nonempty list")
        else:
            try:
                canonical = [canonical_repo_path(value) for value in fault_files]
                if len(set(canonical)) != len(canonical):
                    errors.append(f"{prefix}.fault_files contain duplicate canonical paths")
            except (TypeError, ValueError) as exc:
                errors.append(f"{prefix}.fault_files invalid: {exc}")

        exposed_ids = task.get("exposed_identifiers")
        if not isinstance(exposed_ids, list):
            errors.append(f"{prefix}.exposed_identifiers must be a list")
            exposed_ids = []
        exposed_ids_set = {str(value) for value in exposed_ids}
        if role == "DEVELOPMENT":
            development_identifiers |= exposed_ids_set
        elif role == "PROTECTED":
            protected_identifiers |= exposed_ids_set

        exposed_artifacts = task.get("exposed_artifact_digests")
        if not isinstance(exposed_artifacts, list):
            errors.append(f"{prefix}.exposed_artifact_digests must be a list")
            exposed_artifacts = []
        if role == "DEVELOPMENT":
            development_artifacts |= {str(value) for value in exposed_artifacts}
        elif role == "PROTECTED":
            protected_secret_digests |= {
                str(task.get("mutation_patch_digest")),
                str(task.get("reference_repair_digest")),
                str(task.get("protected_test_digest")),
                str(task.get("mutation_receipt_digest")),
            }

        task_ids.append(str(task.get("task_id")))
        mutated_digests.append(str(task.get("mutated_repo_digest")))
        statement_digests.append(str(task.get("task_statement_digest")))

    for label, values in (
        ("task_id", task_ids),
        ("mutated_repo_digest", mutated_digests),
        ("task_statement_digest", statement_digests),
    ):
        duplicates = _duplicates(values)
        if duplicates:
            errors.append(f"duplicate {label}: {sorted(duplicates)}")

    identifier_overlap = (development_identifiers & protected_identifiers) - allowlist
    if identifier_overlap:
        errors.append(
            "protected identifiers overlap development artifacts outside allowlist: "
            f"{sorted(identifier_overlap)}"
        )

    leaked_digests = development_artifacts & protected_secret_digests
    if leaked_digests:
        errors.append(
            "protected mutation/reference/test receipt digest exposed in development artifacts: "
            f"{sorted(leaked_digests)}"
        )

    if enforce_h1a_minimum:
        total_protected = 0
        for family in sorted(FAMILIES):
            dev = role_counts[family]["DEVELOPMENT"]
            protected = role_counts[family]["PROTECTED"]
            total_protected += protected
            if dev < 4:
                errors.append(f"{family}: requires >=4 DEVELOPMENT tasks, got {dev}")
            if protected < 4:
                errors.append(f"{family}: requires >=4 PROTECTED tasks, got {protected}")
        if total_protected < 12:
            errors.append(f"H1a requires >=12 protected tasks total, got {total_protected}")

    return errors


def load_and_validate(path: str | Path, *, enforce_h1a_minimum: bool = True) -> list[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return validate_manifest(manifest, enforce_h1a_minimum=enforce_h1a_minimum)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--no-h1a-minimum", action="store_true")
    args = parser.parse_args()
    errors = load_and_validate(
        args.manifest,
        enforce_h1a_minimum=not args.no_h1a_minimum,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("GMI_E3_CODE_K1_TASK_CUSTODY_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
