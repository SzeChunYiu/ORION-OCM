"""Authored acquisition controls; no real dependency/network acquisition."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).with_name("acquisition_git.py")


def load(source=SOURCE):
    assert source.is_file(), "The pinned acquisition worker has not been implemented"
    spec = importlib.util.spec_from_file_location("acquisition_under_test", source)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lock(rev="a" * 40):
    return {"version": "1.2.0", "packages": [
        {"name": "p" + str(i), "url": "https://github.com/authored/r" + str(i),
         "type": "git", "subDir": None, "rev": rev, "inputRev": "main"}
        for i in range(9)]}


def encoded(value):
    return json.dumps(value).encode()


def validation(m, raw):
    return m._validate(raw, hashlib.sha256(raw).hexdigest())


def run_fixture(m, tmp_path, transport, raw=None):
    raw = encoded(lock()) if raw is None else raw
    path = tmp_path / "lock.json"
    path.write_bytes(raw)
    return m._acquire(path, tmp_path / "out", transport,
                      lambda data: validation(m, data))


def test_fixed_production_authority():
    m = load()
    with pytest.raises(ValueError, match="LOCK_IDENTITY"):
        m.validate_lock(encoded(lock()))
    assert m.LOCK_SHA256 == "435fe2ab2550e2b82c0a93fd421c96d197d6dd55bc739481e2a4a07e04b979bf"


@pytest.mark.parametrize("field,value", [
    ("type", "path"), ("subDir", "src"), ("rev", "main"),
    ("rev", "a" * 40 + "\n"), ("url", "file:///tmp/a"),
    ("url", "https://user:secret@github.com/a/b"),
    ("url", "https://github.com/a/b\n-c"),
    ("url", "https://github.com/a/b?ref=main"),
    ("url", "http://github.com/a/b"), ("name", "../outside"),
])
def test_refuse_nonfixed_transport_and_rows(field, value):
    m = load()
    data = lock()
    data["packages"][0][field] = value
    with pytest.raises(ValueError):
        validation(m, encoded(data))


def test_duplicate_keys_names_and_denominator():
    m = load()
    raw = b'{"packages":[],"packages":[]}'
    with pytest.raises(ValueError):
        validation(m, raw)
    data = lock()
    data["packages"][1]["name"] = "p0"
    with pytest.raises(ValueError):
        validation(m, encoded(data))
    with pytest.raises(ValueError):
        validation(m, encoded({"packages": lock()["packages"][:8]}))


def test_normalization_uses_resolved_rev_not_input_label():
    m = load()
    rows = validation(m, encoded(lock()))
    assert rows == [{"name": "p" + str(i), "url": "https://github.com/authored/r" + str(i),
                     "rev": "a" * 40} for i in range(9)]


def failing_transport(argv, env, stdout, stderr):
    if argv[-1] == "--version":
        stdout.write(b"git version 2.25.1\n")
        return 0
    if "fetch" in argv:
        stderr.write(b"authored fetch failure\n")
        return 17
    return 0


def test_failure_retains_raw_stops_remainder_and_never_retries(tmp_path):
    m = load()
    result = run_fixture(m, tmp_path, failing_transport)
    assert result["terminal"] == "ACQUISITION_FAILED"
    assert [p["state"] for p in result["packages"]] == ["FAILED"] + ["NOT_RUN"] * 8
    fetches = [c for c in result["commands"] if "fetch" in c["argv"]]
    assert len(fetches) == 1 and fetches[0]["returncode"] == 17
    root = tmp_path / "out"
    assert (root / fetches[0]["stderr"]["path"]).read_bytes() == b"authored fetch failure\n"
    assert json.loads((root / "RESULT.json").read_bytes()) == result
    with pytest.raises(FileExistsError):
        m.acquire(tmp_path / "lock.json", root)


def test_wrong_returned_commit_is_not_accepted(tmp_path):
    m = load()
    def transport(argv, env, stdout, stderr):
        if argv[-1] == "--version":
            stdout.write(b"git version 2.25.1\n")
        if "rev-parse" in argv:
            stdout.write(b"b" * 40 + b"\n")
        return 0
    result = run_fixture(m, tmp_path, transport)
    assert "COMMIT_IDENTITY" in result["error"]
    assert result["packages"][0]["state"] == "FAILED"
    assert not any("cat-file" in c["argv"] for c in result["commands"])


def test_exception_retains_attempt_and_empty_raw_spools(tmp_path):
    m = load()
    def transport(argv, env, stdout, stderr):
        raise OSError("authored launch uncertainty")
    result = run_fixture(m, tmp_path, transport)
    assert result["terminal"] == "ACQUISITION_FAILED"
    c = result["commands"][0]
    assert c["attempted"] and c["returncode"] is None and c["error"]
    assert c["stdout"]["bytes"] == c["stderr"]["bytes"] == 0


@pytest.mark.parametrize("fault", [None, "commit", "tree", "late_material", "lock", "fsck"])
def test_real_git_bare_fixture_and_production_command_contract(tmp_path, fault):
    m = load()
    if subprocess.check_output(["/usr/bin/git", "--version"]) != b"git version 2.25.1\n":
        pytest.skip("The authored real-Git control requires qualified Git 2.25.1")
    home = tmp_path / "fixture-home"
    home.mkdir()
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C",
           "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
    donor = tmp_path / "donor.git"
    def git(*args, data=None):
        return subprocess.check_output(["/usr/bin/git", *args], env=env, input=data,
                                       stderr=subprocess.PIPE)
    git("init", "--bare", str(donor))
    blob = git("-C", str(donor), "hash-object", "-w", "--stdin", data=b"authored\n").strip()
    tree = git("-C", str(donor), "mktree", data=b"100644 blob " + blob + b"\tfixture\n").strip()
    rev = git("-C", str(donor), "commit-tree", tree.decode(), data=b"fixture commit\n").strip()
    git("-C", str(donor), "update-ref", "refs/heads/fixture", rev.decode())
    seen = []
    def local_transport(argv, child_env, stdout, stderr):
        seen.append((argv[:], child_env.copy()))
        actual = [a.replace("protocol.https.allow=always", "protocol.file.allow=always")
                  for a in argv]
        if "fetch" in actual:
            actual[-2] = str(donor)
        fixture_env = {**child_env, "GIT_ALLOW_PROTOCOL": "file" if "fetch" in actual else ""}
        code = subprocess.run(actual, env=fixture_env, stdin=subprocess.DEVNULL,
                              stdout=stdout, stderr=stderr, cwd=home).returncode
        if fault in ("commit", "tree") and "cat-file" in actual and actual[-2] == fault:
            stdout.seek(0); stdout.write(b"x")
        if fault == "fsck" and "fsck" in actual: return 19
        if fault == "late_material" and "fetch" in actual and "p1.git" in actual[actual.index("-C")+1]:
            config = tmp_path / "out" / "p0.git" / "config"
            config.write_bytes(config.read_bytes() + b"\n# authored late alteration\n")
        if fault == "lock" and argv[-1] == "--version":
            path = tmp_path / "lock.json"; path.write_bytes(path.read_bytes() + b"\n")
        return code
    result = run_fixture(m, tmp_path, local_transport, encoded(lock(rev.decode())))
    if fault is not None:
        assert result["terminal"] == "ACQUISITION_FAILED"
        expected = {"commit": "COMMIT_OBJECT_IDENTITY", "tree": "TREE_OBJECT_IDENTITY",
                    "late_material": "MATERIAL_DRIFT", "lock": "LOCK_SOURCE_DRIFT", "fsck": "COMMAND_FAILED"}
        assert expected[fault] in result["error"]
        return
    assert result["terminal"] == "ACQUIRED"
    assert len(result["packages"]) == 9
    assert all(p["commit"] == rev.decode() and p["tree"] == tree.decode()
               and p["state"] == "ACQUIRED" for p in result["packages"])
    assert all(argv[0] == "/usr/bin/git" for argv, _ in seen)
    fetches = [argv for argv, _ in seen if "fetch" in argv]
    assert len(fetches) == 9 and all("--depth=1" in a and "--no-auto-gc" in a
        and "--no-tags" in a and "--no-recurse-submodules" in a for a in fetches)
    assert all("http.followRedirects=false" in a and "http.sslVerify=true" in a for a in fetches)
    assert all(e["GIT_CONFIG_NOSYSTEM"] == "1" and e["GIT_TERMINAL_PROMPT"] == "0"
               and e["GIT_NO_REPLACE_OBJECTS"] == "1" for _, e in seen)
    assert all("GIT_CONFIG_COUNT" not in e and "SSH_AUTH_SOCK" not in e for _, e in seen)
    assert all(e["GIT_ALLOW_PROTOCOL"] == "" and "protocol.https.allow=never" in a
               for a, e in seen if "fetch" not in a)
    assert len([a for a, _ in seen if "fsck" in a]) == 9
    assert result["transport"] == "INJECTED_TEST_TRANSPORT"
    m.validate_lock = lambda raw: validation(m, raw)  # Private fixture authority only.
    assert m._verify(result, tmp_path / "out", m.validate_lock, False)["packages"] == 9
    changed = json.loads(json.dumps(result))
    changed["packages"][0]["tree"] = "f" * 40
    with pytest.raises(ValueError, match="RESULT_BINDING"):
        m.revalidate(changed, tmp_path / "out")
    config = Path(result["packages"][0]["bare_path"]) / "config"
    config.write_bytes(config.read_bytes() + b"\n# changed fixture\n")
    with pytest.raises(ValueError, match="MATERIAL_DRIFT"):
        m._verify(result, tmp_path / "out", m.validate_lock, False)

def test_inventory_rejects_nonregular_entry(tmp_path):
    m = load()
    os.mkfifo(tmp_path / "pipe")
    with pytest.raises(ValueError, match="MATERIAL_KIND"):
        m._files(tmp_path)


def test_inventory_does_not_hide_unreadable_directory(tmp_path):
    m = load()
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "value").write_bytes(b"authored")
    hidden.chmod(0)
    try:
        with pytest.raises(PermissionError):
            m._files(tmp_path)
    finally:
        hidden.chmod(0o700)

def test_helper_bytes_are_bound_without_ambient_import(tmp_path):
    import sys
    from types import SimpleNamespace
    m = load()
    helper = SOURCE.with_name("acquisition_git_custody.py")
    assert m.CUSTODY_SOURCE_STAMP["sha256"] == hashlib.sha256(helper.read_bytes()).hexdigest()
    previous = sys.modules.get("acquisition_git_custody")
    sys.modules["acquisition_git_custody"] = SimpleNamespace(_files=lambda path: {"poison": True})
    try:
        assert load()._files(tmp_path) == {}
    finally:
        if previous is None: sys.modules.pop("acquisition_git_custody")
        else: sys.modules["acquisition_git_custody"] = previous
    (tmp_path / SOURCE.name).write_bytes(SOURCE.read_bytes())
    (tmp_path / helper.name).write_bytes(b"raise RuntimeError('must not execute')\n")
    with pytest.raises(ValueError, match="CUSTODY_SOURCE_IDENTITY"):
        load(tmp_path / SOURCE.name)
