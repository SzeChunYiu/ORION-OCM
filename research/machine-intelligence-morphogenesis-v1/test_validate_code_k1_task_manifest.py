import copy

from validate_code_k1_task_manifest import FAMILIES, validate_manifest


def _task(family: str, role: str, index: int) -> dict:
    prefix = "dev" if role == "DEVELOPMENT" else "prot"
    tag = f"{prefix}-{family}-{index}"
    return {
        "task_id": f"task-{tag}",
        "family_id": family,
        "role": role,
        "author_or_generator_id": f"author-{prefix}-{index}",
        "base_repo_digest": f"base-{tag}",
        "mutated_repo_digest": f"mut-{tag}",
        "task_statement_digest": f"statement-{tag}",
        "public_test_digest": f"public-tests-{tag}",
        "protected_test_digest": f"protected-tests-{tag}",
        "mutation_receipt_digest": f"mutation-receipt-{tag}",
        "fault_operator_id": f"fault-op-{family}",
        "fault_files": [f"src/{tag}/fault.py"],
        "fault_regions_digest": f"fault-region-{tag}",
        "mutation_patch_digest": f"mutation-patch-{tag}",
        "reference_repair_digest": f"reference-repair-{tag}",
        "exposed_identifiers": [f"{prefix}_identifier_{family}_{index}"],
        "exposed_artifact_digests": [f"exposed-artifact-{tag}"],
        "base_full_suite_passed": True,
        "mutated_full_suite_failed": True,
        "solver_visible_family_label": False,
        "solver_visible_mutation_receipt": False,
        "solver_visible_protected_tests": False,
        "solver_visible_reference_repair": False,
    }


def manifest_fixture() -> dict:
    tasks = []
    for family in sorted(FAMILIES):
        for index in range(4):
            tasks.append(_task(family, "DEVELOPMENT", index))
            tasks.append(_task(family, "PROTECTED", index))
    return {
        "schema": "ocm.gmi-e3.code-k1-task-manifest.v1",
        "protocol_version": "GMI_E3_CODE_K1_V1",
        "model_identity_digest": "model-digest",
        "harness_identity_digest": "harness-digest",
        "verifier_environment_digest": "verifier-env-digest",
        "generic_identifier_allowlist": ["__init__", "main"],
        "tasks": tasks,
    }


def test_valid_three_family_h1a_manifest_is_green():
    assert validate_manifest(manifest_fixture()) == []


def test_identifier_overlap_between_development_and_protected_is_rejected():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    dev = next(task for task in manifest["tasks"] if task["role"] == "DEVELOPMENT")
    protected = next(task for task in manifest["tasks"] if task["role"] == "PROTECTED")
    protected["exposed_identifiers"] = list(dev["exposed_identifiers"])
    errors = validate_manifest(manifest)
    assert any("protected identifiers overlap" in error for error in errors)


def test_generic_allowlist_can_permit_deliberate_shared_vocabulary():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    for task in manifest["tasks"]:
        task["exposed_identifiers"].append("main")
    assert validate_manifest(manifest) == []


def test_protected_reference_digest_exposed_in_development_is_rejected():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    protected = next(task for task in manifest["tasks"] if task["role"] == "PROTECTED")
    dev = next(task for task in manifest["tasks"] if task["role"] == "DEVELOPMENT")
    dev["exposed_artifact_digests"].append(protected["reference_repair_digest"])
    errors = validate_manifest(manifest)
    assert any("protected mutation/reference/test receipt digest exposed" in error for error in errors)


def test_family_label_must_be_solver_hidden():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    manifest["tasks"][0]["solver_visible_family_label"] = True
    errors = validate_manifest(manifest)
    assert any("solver_visible_family_label must be false" in error for error in errors)


def test_correct_base_must_pass_before_mutation():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    manifest["tasks"][0]["base_full_suite_passed"] = False
    errors = validate_manifest(manifest)
    assert any("base repository must pass" in error for error in errors)


def test_mutated_repo_digest_must_be_unique():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    manifest["tasks"][1]["mutated_repo_digest"] = manifest["tasks"][0]["mutated_repo_digest"]
    errors = validate_manifest(manifest)
    assert any("duplicate mutated_repo_digest" in error for error in errors)


def test_h1a_minimum_is_enforced():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    victim_family = sorted(FAMILIES)[0]
    removed = False
    kept = []
    for task in manifest["tasks"]:
        if (
            not removed
            and task["family_id"] == victim_family
            and task["role"] == "PROTECTED"
        ):
            removed = True
            continue
        kept.append(task)
    manifest["tasks"] = kept
    errors = validate_manifest(manifest)
    assert any(f"{victim_family}: requires >=4 PROTECTED tasks" in error for error in errors)
    assert any("H1a requires >=12 protected tasks total" in error for error in errors)


def test_fault_path_cannot_escape_repository():
    manifest = manifest_fixture()
    manifest = copy.deepcopy(manifest)
    manifest["tasks"][0]["fault_files"] = ["../secret.py"]
    errors = validate_manifest(manifest)
    assert any("fault_files invalid" in error for error in errors)
