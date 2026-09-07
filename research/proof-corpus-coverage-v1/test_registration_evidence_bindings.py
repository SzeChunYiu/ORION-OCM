from pathlib import Path
import pytest
from registration_evidence_archive import canonical, identity
from registration_evidence_bindings import verify_source_bindings, verify_omissions

MAPPING = {name: "proof-corpus-coverage-v1/" + name + ".py" for name in ["coverage_boot", "coverage_git", "coverage_policy", "coverage_population", "coverage_register", "register"]}
MAPPING.update({name: "proof-corpus-v1/" + name + ".py" for name in ["corpus_contract", "corpus_git", "corpus_tree"]})
MAPPING["env_inputs"] = "proof-environment-v1/env_inputs.py"
DOCS = ["F1-CORPUS-COVERAGE-DESIGN.md", "F1-CORPUS-COVERAGE-EXECUTION.md"]
INPUTS = ["CORPUS_SOURCE.json", "GRAPH.json", "SOLUTIONS.json", "WRAPPERS.json"]


def bound_fixture(tmp_path):
    package = tmp_path / "proof-corpus-coverage-v1"; package.mkdir(parents=True)
    source = {"loaded_sources": {}, "documents": {}, "snapshots": {}, "inputs": {}, "input_snapshots": {}}
    files = {}
    for key, rel in MAPPING.items():
        path = tmp_path / rel; path.parent.mkdir(exist_ok=True); path.write_bytes(key.encode())
        record = dict(identity(path.read_bytes()), path="/registered/research/" + rel)
        source["loaded_sources"][key] = record
        source["snapshots"][key] = dict(record, path="/original/sources/" + path.name)
        files["sources/" + path.name] = path.read_bytes()
    for name in DOCS:
        raw = name.encode(); (package/name).write_bytes(raw)
        record = dict(identity(raw), path="/registered/research/proof-corpus-coverage-v1/" + name)
        source["documents"][name] = record
        source["snapshots"]["document_"+name] = dict(record, path="/original/sources/"+name)
        files["sources/"+name] = raw
    omitted = {"schema": "ocm.f1.registration-omissions.v1", "original_root": "/original", "files": {}, "prior_archive": {"path": "/prior.tar.gz", "sha256": "c1177f5a3725b21d91f74a52faf6c98839800052ababa254cc173bff154d27fb", "bytes": 61338019}}
    for name in INPUTS:
        record = identity(name.encode())
        source["inputs"][name] = dict(record, path="/inventory/"+name)
        source["input_snapshots"][name] = dict(record, path="/original/inputs/"+name)
        omitted["files"]["inputs/"+name] = dict(record, original="/inventory/"+name, sealed_copy="/original/inputs/"+name, prior_archive_member="inventory/"+name)
    files["SOURCE-FREEZE.json"] = canonical(source)
    seals = {name: identity(raw) for name, raw in files.items()}
    seals.update({name: {k: row[k] for k in ["sha256","bytes"]} for name,row in omitted["files"].items()})
    files["SEAL.json"] = canonical({"schema":"ocm.f1.registration-seal.v1", "state":"REGISTERED_NO_DISPATCH", "files":seals})
    return package, files, omitted, identity(files["SEAL.json"])["sha256"]


def test_all_twelve_source_bindings_match(tmp_path):
    package, files, _, _ = bound_fixture(tmp_path)
    assert verify_source_bindings(files, package) == 12


def test_exact_four_omissions_no_alarm(tmp_path):
    _, files, omitted, sha = bound_fixture(tmp_path)
    assert verify_omissions(files, omitted, sha) == 4


def test_source_drift_refuses(tmp_path):
    package, files, _, _ = bound_fixture(tmp_path)
    (package/"coverage_population.py").write_bytes(b"changed")
    with pytest.raises(ValueError): verify_source_bindings(files, package)


@pytest.mark.parametrize("change", ["extra", "missing", "hash", "snapshot", "prior", "member"])
def test_omission_tamper_refuses(tmp_path, change):
    _, files, omitted, sha = bound_fixture(tmp_path)
    key = "inputs/GRAPH.json"
    if change == "extra": omitted["files"]["sources/coverage_boot.py"] = omitted["files"][key]
    if change == "missing": del omitted["files"][key]
    if change == "hash": omitted["files"][key]["sha256"] = "f"*64
    if change == "snapshot": omitted["files"][key]["sealed_copy"] = "/wrong"
    if change == "prior": omitted["prior_archive"]["sha256"] = "f"*64
    if change == "member": files["sources/coverage_boot.py"] = b"changed"
    with pytest.raises(ValueError): verify_omissions(files, omitted, sha)


def test_source_directory_escape_refuses_even_matching_bytes(tmp_path):
    package, files, _, _ = bound_fixture(tmp_path/"research")
    original = package.parent/"proof-corpus-v1"
    outside = tmp_path/"outside"; original.rename(outside); original.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError): verify_source_bindings(files, package)
