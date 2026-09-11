import copy

from test_validate_code_k1_task_manifest import manifest_fixture
from validate_code_k1_task_manifest import validate_manifest


def test_protected_base_repository_must_not_reuse_development_base():
    manifest = copy.deepcopy(manifest_fixture())
    dev = next(task for task in manifest["tasks"] if task["role"] == "DEVELOPMENT")
    protected = next(task for task in manifest["tasks"] if task["role"] == "PROTECTED")
    protected["base_repo_digest"] = dev["base_repo_digest"]
    errors = validate_manifest(manifest)
    assert any("protected base repositories overlap" in error for error in errors)
