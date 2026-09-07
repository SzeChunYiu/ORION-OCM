"""Actual tiny Git custody and source-byte loader controls; no Lean dispatch."""
from copy import deepcopy
from hashlib import sha256
import importlib._bootstrap_external as bytecode
import json
from pathlib import Path
import subprocess
import sys
import pytest
from registration_fixture import boot, custody, git_metadata, inputs, population


def test_real_toy_git_metadata_without_blob_reads(tmp_path, monkeypatch):
    source, graph, solutions, bare = git_metadata(tmp_path)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    def no_bodies(*args, **kwargs): raise AssertionError("proof blob bodies must not be read")
    monkeypatch.setattr(custody.Snapshot, "blobs", no_bodies)
    receipt = custody.verify_git(source, bare, evidence)
    assert receipt["files"] == receipt["unique_blobs"] == 4
    assert receipt["metrics"]["blob_bytes_read"] == 0
    assert receipt["returncode"] == 0
    process = json.loads((evidence / "git-process.json").read_bytes())
    assert process["evidence_complete"] is True and process["error"] is None
    assert process["stdout_available"] is process["stderr_available"] is True
    assert (evidence / "git-objects.stderr").read_bytes() == b""
    assert sha256((evidence / "git-objects.stdout").read_bytes()).hexdigest() == receipt["metadata_stdout_sha256"]
    assert len(population.validate_population(source, graph, solutions, 2)) == 2


@pytest.mark.parametrize("kind,reason", [("size", "Git blob identity/size"), ("oid", "Git entry differs"),
                                        ("tree", "Git tree payloads differ"), ("membership", "Git file membership")])
def test_real_git_tamper_refusal(tmp_path, kind, reason):
    source, _, _, bare = git_metadata(tmp_path)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    path = next(iter(source["files"]))
    if kind == "size": source["files"][path]["bytes"] += 1
    elif kind == "oid": source["files"][path]["oid"] = "f" * 40
    elif kind == "tree": next(iter(source["verified_tree_objects"].values()))["sha256"] = "f" * 64
    else: source["files"].pop(path)
    with pytest.raises(ValueError, match=reason): custody.verify_git(source, bare, evidence)


def test_git_evidence_create_only_preserves_existing_bytes(tmp_path):
    source, _, _, bare = git_metadata(tmp_path)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    sentinel = evidence / "git-objects.stdout"; sentinel.write_bytes(b"prior evidence\n")
    with pytest.raises((ValueError, FileExistsError)):
        custody.verify_git(source, bare, evidence)
    assert sentinel.read_bytes() == b"prior evidence\n"
    assert not (evidence / "git-objects.stdin").exists()


def test_git_store_symlink_refused(tmp_path):
    source, _, _, bare = git_metadata(tmp_path)
    alias = tmp_path / "alias.git"; alias.symlink_to(bare, target_is_directory=True)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    with pytest.raises(ValueError, match="canonical Git store"):
        custody.verify_git(source, alias, evidence)


def test_source_loader_checks_hash_before_execution_and_rejects_link(tmp_path):
    path = tmp_path / "unit.py"; path.write_text("VALUE = 'registered'\n")
    old = sha256(path.read_bytes()).hexdigest()
    assert boot.load_module("authored_unit", path, old).VALUE == "registered"
    path.write_text("raise AssertionError('must not execute changed source')\n")
    with pytest.raises(ValueError, match="parent source differs"):
        boot.load_module("authored_unit", path, old)
    alias = tmp_path / "alias.py"; alias.symlink_to(path)
    with pytest.raises(ValueError, match="noncanonical source"):
        boot.load_module("authored_unit", alias)


def test_matching_header_bytecode_is_ignored_by_source_loader(tmp_path):
    source = tmp_path / "cacheprobe.py"; source.write_text("VALUE = 'SOURCE'\n")
    cache = Path(bytecode.cache_from_source(str(source))); cache.parent.mkdir()
    code = compile("VALUE = 'HARMLESS_CACHE_CONTROL'\n", str(source), "exec")
    cache.write_bytes(bytecode._code_to_timestamp_pyc(code, int(source.stat().st_mtime), source.stat().st_size))
    script = "import sys; sys.path.insert(0, sys.argv[1]); import cacheprobe; print(cacheprobe.VALUE)"
    result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", script, str(tmp_path)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    assert result.stdout == b"HARMLESS_CACHE_CONTROL\n" and result.stderr == b""
    loaded = boot.load_module("cacheprobe", source, sha256(source.read_bytes()).hexdigest())
    assert loaded.VALUE == "SOURCE"
    assert loaded.__source_record__ == {"path": str(source), "sha256": sha256(source.read_bytes()).hexdigest(), "bytes": source.stat().st_size}


@pytest.mark.parametrize("kind,reason", [("stderr", "Git batch process"), ("exit", "Git batch process"),
                                        ("extra", "Git object count"), ("type", "Git blob identity/size")])
def test_bad_git_reply_is_retained_and_refused(tmp_path, monkeypatch, kind, reason):
    source, _, _, bare = git_metadata(tmp_path)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    run = custody.subprocess.run
    def changed(argv, **kwargs):
        result = run(argv, **kwargs)
        if not any(arg.startswith("--batch-check=") for arg in argv): return result
        if kind == "stderr": result.stderr = b"authored diagnostic\n"
        elif kind == "exit": result.returncode = 2
        elif kind == "extra": result.stdout += b"extra record\n"
        else: result.stdout = result.stdout.replace(b" blob ", b" tree ", 1)
        return result
    monkeypatch.setattr(custody.subprocess, "run", changed)
    with pytest.raises(ValueError, match=reason): custody.verify_git(source, bare, evidence)
    assert (evidence / "git-objects.stdin").is_file()
    assert (evidence / "git-objects.stdout").is_file()
    assert (evidence / "git-objects.stderr").is_file()


def test_git_timeout_retains_available_partial_evidence(tmp_path, monkeypatch):
    source, _, _, bare = git_metadata(tmp_path)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    run = custody.subprocess.run
    def timeout(argv, **kwargs):
        if any(arg.startswith("--batch-check=") for arg in argv):
            raise subprocess.TimeoutExpired(argv, 60, output=b"partial metadata\n", stderr=b"timeout diagnostic\n")
        return run(argv, **kwargs)
    monkeypatch.setattr(custody.subprocess, "run", timeout)
    with pytest.raises(subprocess.TimeoutExpired): custody.verify_git(source, bare, evidence)
    assert (evidence / "git-objects.stdin").is_file()
    assert (evidence / "git-objects.stdout").read_bytes() == b"partial metadata\n"
    assert (evidence / "git-objects.stderr").read_bytes() == b"timeout diagnostic\n"
    process = json.loads((evidence / "git-process.json").read_bytes())
    assert process["evidence_complete"] is False and process["returncode"] is None
    assert process["error"] == "TimeoutExpired"
    assert process["stdout_available"] is process["stderr_available"] is True


def test_git_interrupt_distinguishes_unavailable_streams(tmp_path, monkeypatch):
    source, _, _, bare = git_metadata(tmp_path)
    evidence = tmp_path / "evidence"; evidence.mkdir()
    run = custody.subprocess.run
    def interrupt(argv, **kwargs):
        if any(arg.startswith("--batch-check=") for arg in argv): raise KeyboardInterrupt()
        return run(argv, **kwargs)
    monkeypatch.setattr(custody.subprocess, "run", interrupt)
    with pytest.raises(KeyboardInterrupt): custody.verify_git(source, bare, evidence)
    process = json.loads((evidence / "git-process.json").read_bytes())
    assert process["error"] == "KeyboardInterrupt" and process["returncode"] is None
    assert process["evidence_complete"] is process["stdout_available"] is process["stderr_available"] is False
    assert (evidence / "git-objects.stdout").read_bytes() == b""
    assert (evidence / "git-objects.stderr").read_bytes() == b""
