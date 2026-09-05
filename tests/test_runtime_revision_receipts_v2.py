"""Second successors verify frozen parent code without reusing old runtime authority."""
from __future__ import annotations

import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("receipt_revision_v2_tests", ROOT / "tools/runtime_revision_receipts_v2.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def save(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def refresh_replay(root):
    config = R.read_json(root, R.CONFIG_PATH)
    artifacts, executions = {}, []
    for label, spec in config["validation_requirements"].items():
        count = spec["minimum_tests"]
        cases = "".join(f'<testcase classname="fixture_only" name="synthetic_{i}" />' for i in range(count))
        report = (f'<testsuites><testsuite name="fixture_only" tests="{count}" failures="0" errors="0" skipped="0">'
                  + cases + '</testsuite></testsuites>')
        path = root / spec["artifact_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report)
        artifacts[spec["artifact_path"]] = R.sha(root, spec["artifact_path"])
        executions.append({"label": label, "argv": spec["argv"], "exit_code": 0,
                           "artifact_path": spec["artifact_path"], "fixture_only": True})
    save(root, config["engineering_replay_path"], {
        "schema": "ocm.engineering-replay.v2", "revision": R.REVISION,
        "status": "ENGINEERING_REGRESSION_ONLY", "protected_reevaluation": "NOT_RUN",
        "scientific_promotion": "NOT_ESTABLISHED", "independent_replication": "NOT_RUN",
        "current_source_inventory": R.source_inventory(root),
        "executions": executions, "validation_artifacts": artifacts,
    })


@pytest.fixture(scope="module")
def baseline(tmp_path_factory):
    root = tmp_path_factory.mktemp("receipt-v2-parent")
    config = R.read_json(ROOT, R.CONFIG_PATH)
    manifest = R.read_json(ROOT, config["parent_manifest"]["path"])
    for rel in (R.CONFIG_PATH, config["parent_manifest"]["path"], manifest["archive"]["path"]):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, path)
    # Fixture setup copies only the already validated, repository-authored safe paths.
    with zipfile.ZipFile(ROOT / manifest["archive"]["path"]) as archive:
        for rel in manifest["entries"]:
            path = R.path_in(root, rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(rel))
    refresh_replay(root)
    for i in range(1, 13):
        R.CurrentReceipts(root).write(i)
    return root


@pytest.fixture
def evidence(tmp_path, baseline):
    root = tmp_path / "repo"
    shutil.copytree(baseline, root)
    return root


def successor(root, i=12):
    return R.read_json(root, R.CONFIG_PATH)["milestones"][str(i)]["successor_path"]


def repin_test_manifest(root, monkeypatch, manifest):
    """Reach internal proof checks under a test-only changed config anchor."""
    config = R.read_json(root, R.CONFIG_PATH)
    rel = config["parent_manifest"]["path"]
    save(root, rel, manifest)
    config["parent_manifest"]["sha256"] = R.sha(root, rel)
    save(root, R.CONFIG_PATH, config)
    monkeypatch.setattr(R, "CONFIG_SHA256", R.sha(root, R.CONFIG_PATH))
    return config


def test_complete_chain_binds_archive_and_current_sources(evidence):
    R.CurrentReceipts(evidence).verify(12)
    receipt = R.read_json(evidence, successor(evidence))
    assert receipt["legacy_recipe_execution"] == "NOT_EXECUTED"
    assert receipt["predecessor"]["parent_commit"] == R.PARENT_COMMIT
    assert receipt["current_source_inventory"] == R.source_inventory(evidence)
    assert receipt["current_engineering_replay"]["protected_reevaluation"] == "NOT_RUN"
    assert receipt["current_dependencies"]


@pytest.mark.parametrize("which", ["parent_archive", "parent_manifest", "old_receipt", "current_receipt", "source", "replay"])
def test_missing_required_inputs_never_fall_back(evidence, which):
    config = R.read_json(evidence, R.CONFIG_PATH)
    manifest = R.read_json(evidence, config["parent_manifest"]["path"])
    rel = {"parent_archive": manifest["archive"]["path"],
           "parent_manifest": config["parent_manifest"]["path"],
           "old_receipt": config["milestones"]["12"]["predecessor_path"],
           "current_receipt": successor(evidence),
           "source": "src/ocm/kso/space.py", "replay": config["engineering_replay_path"]}[which]
    (evidence / rel).unlink()
    with pytest.raises(R.ReceiptError):
        R.CurrentReceipts(evidence).verify(12)


@pytest.mark.parametrize("field,value", [("terminal", "FULL_RESIDUAL_SUPPORTED"),
                                         ("revision", "prior_revision"),
                                         ("legacy_recipe_execution", "CURRENT_CODE_RECHECK"),
                                         ("dependency_aliases", {})])
def test_relabelled_current_receipt_is_rejected(evidence, field, value):
    rel = successor(evidence)
    receipt = R.read_json(evidence, rel)
    receipt[field] = value
    save(evidence, rel, receipt)
    with pytest.raises(R.ReceiptError, match="successor DRIFT"):
        R.CurrentReceipts(evidence).verify(12)


@pytest.mark.parametrize("field,value", [("status", "PROTECTED_REEVALUATION"),
                                         ("protected_reevaluation", "PASS"),
                                         ("scientific_promotion", "SUPPORTED"),
                                         ("independent_replication", "COMPLETE"),
                                         ("executions", []), ("validation_artifacts", {})])
def test_replay_cannot_inherit_historical_scientific_authority(evidence, field, value):
    rel = R.read_json(evidence, R.CONFIG_PATH)["engineering_replay_path"]
    replay = R.read_json(evidence, rel)
    replay[field] = value
    save(evidence, rel, replay)
    with pytest.raises(R.ReceiptError):
        R.CurrentReceipts(evidence).verify(12)


@pytest.mark.parametrize("mutation", ["new_source", "new_resource", "source_drift", "validation_drift", "predecessor_drift"])
def test_exact_inventory_and_immutable_history_are_enforced(evidence, mutation):
    paths = {"new_source": "src/ocm/new_unbound.py", "new_resource": "src/ocm/data/new_resource.json",
             "source_drift": "src/ocm/kso/space.py",
             "validation_drift": f"docs/provenance/{R.REVISION}/FULL_SUITE.xml",
             "predecessor_drift": "docs/provenance/M1_RECEIPT_V1.json"}
    path = evidence / paths[mutation]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("changed\n")
    with pytest.raises(R.ReceiptError):
        R.CurrentReceipts(evidence).verify(12)


def test_memoized_object_rechecks_after_source_change(evidence):
    current = R.CurrentReceipts(evidence)
    current.verify(12)
    (evidence / "src/ocm/kso/space.py").write_text("later source\n")
    with pytest.raises(R.ReceiptError):
        current.verify(12)


def test_no_recipe_execution_and_exclusive_idempotent_creation(evidence):
    recipe = evidence / "tools/m1_receipt.py"
    recipe.write_text("raise RuntimeError('this historical recipe must never execute')\n")
    refresh_replay(evidence)
    config = R.read_json(evidence, R.CONFIG_PATH)
    for item in config["milestones"].values():
        (evidence / item["successor_path"]).unlink()
    historical = {p: (evidence / p).read_bytes() for p in (
        "docs/provenance/M1_RECEIPT_V1.json", config["milestones"]["1"]["predecessor_path"])}
    for i in range(1, 13):
        R.CurrentReceipts(evidence).write(i)
    path = evidence / successor(evidence)
    before = path.read_bytes()
    R.CurrentReceipts(evidence).write(12)
    assert path.read_bytes() == before
    assert all((evidence / p).read_bytes() == data for p, data in historical.items())
    (evidence / "src/ocm/kso/space.py").write_text("new engine\n")
    with pytest.raises(R.ReceiptError):
        R.CurrentReceipts(evidence).write(12)
    assert path.read_bytes() == before


def test_no_argument_command_refuses_historical_writes(evidence):
    assert R.revision_main(evidence, [], 1) == 2


@pytest.mark.parametrize("which", ["duplicate", "extra", "missing", "traversal", "changed_blob", "symlink_mode"])
def test_archive_entry_attacks_fail_without_extraction(evidence, monkeypatch, which):
    config = R.read_json(evidence, R.CONFIG_PATH)
    manifest = R.read_json(evidence, config["parent_manifest"]["path"])
    rel = manifest["archive"]["path"]
    with zipfile.ZipFile(evidence / rel) as original:
        contents = {x.filename: original.read(x) for x in original.infolist()}
    first = sorted(contents)[0]
    with zipfile.ZipFile(evidence / rel, "w") as archive:
        for path, content in contents.items():
            if which == "missing" and path == first:
                continue
            info = zipfile.ZipInfo(path)
            info.external_attr = int(manifest["entries"][path]["mode"], 8) << 16
            if which == "symlink_mode" and path == first:
                info.external_attr = 0o120777 << 16
            archive.writestr(info, b"tampered" if which == "changed_blob" and path == first else content)
        if which == "duplicate":
            with pytest.warns(UserWarning, match="Duplicate name"):
                archive.writestr(first, contents[first])
        if which == "extra":
            archive.writestr("extra.txt", b"extra")
        if which == "traversal":
            archive.writestr("../outside.txt", b"outside")
    manifest["archive"]["sha256"] = R.sha(evidence, rel)
    config = repin_test_manifest(evidence, monkeypatch, manifest)
    with pytest.raises(R.ReceiptError):
        R.ParentSnapshot(evidence, config)
    assert not (evidence.parent / "outside.txt").exists()


def test_forged_parent_commit_label_fails_git_proof(evidence, monkeypatch):
    config = R.read_json(evidence, R.CONFIG_PATH)
    manifest = R.read_json(evidence, config["parent_manifest"]["path"])
    manifest["git_commit_object_base64"] = "Zm9yZ2VkIGNvbW1pdAo="
    config = repin_test_manifest(evidence, monkeypatch, manifest)
    with pytest.raises(R.ReceiptError, match="commit proof failed"):
        R.ParentSnapshot(evidence, config)


def test_archive_source_membership_is_verified_against_git_tree(evidence, monkeypatch):
    config = R.read_json(evidence, R.CONFIG_PATH)
    manifest = R.read_json(evidence, config["parent_manifest"]["path"])
    manifest["entries"]["src/ocm/kso/space.py"]["git_blob"] = "0" * 40
    config = repin_test_manifest(evidence, monkeypatch, manifest)
    with pytest.raises(R.ReceiptError, match="Git membership proof"):
        R.ParentSnapshot(evidence, config)


def test_wrapper_dispatch_has_explicit_successor_without_recipe_loading():
    for i in range(1, 13):
        text = (ROOT / f"tools/m{i}_receipt.py").read_text()
        assert "from runtime_revision_receipts_v" in text and "import revision_main" in text
        assert f"revision_main(ROOT, argv, {i})" in text


def test_direct_build_rechecks_parent_evidence_on_each_call(evidence):
    current = R.CurrentReceipts(evidence)
    current.build(1)
    (evidence / "docs/provenance/M1_RECEIPT_V1.json").write_text("changed original receipt\n")
    with pytest.raises(R.ReceiptError, match="immutable predecessor"):
        current.build(1)


@pytest.mark.parametrize("milestone", [3, 4, 6, 9, 11])
def test_missing_current_dependency_refuses_without_historical_fallback(evidence, milestone):
    (evidence / successor(evidence, milestone)).unlink()
    with pytest.raises(R.ReceiptError, match="MISSING required evidence"):
        R.CurrentReceipts(evidence).verify(12)


def update_replay_artifact_hash(root, path):
    replay_path = R.read_json(root, R.CONFIG_PATH)["engineering_replay_path"]
    replay = R.read_json(root, replay_path)
    replay["validation_artifacts"][path] = R.sha(root, path)
    save(root, replay_path, replay)


def test_successful_true_command_cannot_substitute_for_required_regressions(evidence):
    path = R.read_json(evidence, R.CONFIG_PATH)["engineering_replay_path"]
    replay = R.read_json(evidence, path)
    replay["executions"] = [{"label": "full_suite", "argv": ["true"], "exit_code": 0,
                             "artifact_path": "unrelated.txt"}]
    save(evidence, path, replay)
    with pytest.raises(R.ReceiptError, match="declared gate"):
        R.CurrentReceipts(evidence).verify(12)


@pytest.mark.parametrize("mutation", ["missing_gate", "duplicate_gate", "wrong_command", "missing_junit"])
def test_required_named_validation_inventory_is_exact(evidence, mutation):
    path = R.read_json(evidence, R.CONFIG_PATH)["engineering_replay_path"]
    replay = R.read_json(evidence, path)
    if mutation == "missing_gate":
        replay["executions"].pop()
    elif mutation == "duplicate_gate":
        replay["executions"].append(copy.deepcopy(replay["executions"][0]))
    elif mutation == "wrong_command":
        replay["executions"][0]["argv"] = ["python", "-m", "pytest", "tests", "-k", "tiny_subset"]
    else:
        replay["validation_artifacts"].pop(replay["executions"][0]["artifact_path"])
    save(evidence, path, replay)
    with pytest.raises(R.ReceiptError):
        R.CurrentReceipts(evidence).verify(12)


@pytest.mark.parametrize("mutation", ["plain_text", "no_cases", "too_few", "failed", "error", "all_skipped", "mismatched_count"])
def test_required_junit_must_contain_sufficient_passing_cases(evidence, mutation):
    config = R.read_json(evidence, R.CONFIG_PATH)
    spec = config["validation_requirements"]["full_suite"]
    path = spec["artifact_path"]
    count = spec["minimum_tests"]
    text = (evidence / path).read_text()
    if mutation == "plain_text":
        text = "No tests were run.\n"
    elif mutation == "no_cases":
        text = '<testsuites><testsuite tests="0" failures="0" errors="0" skipped="0" /></testsuites>'
    elif mutation == "too_few":
        text = '<testsuites><testsuite tests="1" failures="0" errors="0" skipped="0"><testcase name="tiny" /></testsuite></testsuites>'
    elif mutation == "failed":
        text = text.replace('failures="0"', 'failures="1"').replace('name="synthetic_0" />', 'name="synthetic_0"><failure /></testcase>')
    elif mutation == "error":
        text = text.replace('errors="0"', 'errors="1"').replace('name="synthetic_0" />', 'name="synthetic_0"><error /></testcase>')
    elif mutation == "all_skipped":
        text = text.replace('skipped="0"', f'skipped="{count}"').replace(' />', '><skipped /></testcase>')
    else:
        text = text.replace(f'tests="{count}"', f'tests="{count + 1}"')
    (evidence / path).write_text(text)
    update_replay_artifact_hash(evidence, path)
    with pytest.raises(R.ReceiptError, match="JUnit"):
        R.CurrentReceipts(evidence).verify(12)
