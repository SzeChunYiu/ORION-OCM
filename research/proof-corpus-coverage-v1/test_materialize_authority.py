"""Toy independent pin authority; no production metadata or material is reopened."""
import copy
from pathlib import Path
import sys
import time
import pytest
from test_materialize_phase import modules, clean_receipt


def fixture(tmp_path, monkeypatch):
    loaded = modules(); p = loaded["materialize_phase"]; c = loaded["acquisition_contract"]
    # Authored unit-test authority only; production constants and dispatch stay unchanged.
    monkeypatch.setattr(c, "PYTHON", c.record(Path(sys.executable).resolve())["sha256"])
    monkeypatch.setattr(p, "GIT", c.record("/usr/bin/git")["sha256"])
    reg, episode, bare = [tmp_path / name for name in ("reg", "episode", "bare")]
    for path in (reg, episode, bare): path.mkdir()
    (episode / "materials").mkdir()
    start = dict(boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                 monotonic_seconds=time.monotonic(), whole_deadline_monotonic=time.monotonic() + 90,
                 registration_seal_sha256=c.SEAL)
    monkeypatch.setattr(p, "DEADLINE", start["whole_deadline_monotonic"])
    git = dict(commit=c.COMMIT, tree=p.TREE, argv=["/usr/bin/git", "-C", str(bare)])
    c.write(reg / "GIT.json", git)
    g = c.record(reg / "GIT.json")
    c.write(reg / "SEAL.json", dict(files={"GIT.json": {k: g[k] for k in ("sha256", "bytes")}}))
    seal = c.record(reg / "SEAL.json")
    assigned = dict(denominator=4, continuation_cursor=4, rows=[dict(key=str(i)) for i in range(4)])
    policy = dict(limits={})
    monkeypatch.setattr(c, "registration", lambda path: (seal, assigned, policy))
    worker = dict(packages=[dict(name="dependency"+str(i), bare_path=str(bare), commit=c.COMMIT,
                                tree=p.TREE, files={}) for i in range(9)])
    c.write(episode / "materials/RESULT.json", worker)
    monkeypatch.setattr(p, "acquired", lambda *a: (worker, c.record(episode / "materials/RESULT.json")))
    receipt = clean_receipt(); receipt["raw"] = {}
    values = {name: {} for name in p.PINS}
    values.update({"STARTED.json": start,
                   "ACQUISITION.json": dict(terminal="MATERIAL_READY", resource=receipt, worker=worker),
                   "SOURCE-FREEZE.json": dict(sources={}, interpreter=c.record(Path(sys.executable).resolve())),
                   "REGISTRATION-REFERENCE.json": dict(seal=seal, assignments=assigned, policy=policy)})
    pins = {}
    for name, value in values.items():
        c.write(episode / name, value); pins[name] = c.record(episode / name)["sha256"]
    monkeypatch.setattr(p, "PINS", pins)
    return loaded, (reg, episode, bare), values


def test_authorized_population_is_exact_corpus_plus_nine(tmp_path, monkeypatch):
    loaded, args, values = fixture(tmp_path, monkeypatch)
    value = loaded["materialize_phase"].authorize(*args)
    assert [r["name"] for r in value["materials"]] == ["corpus"] + ["dependency"+str(i) for i in range(9)]
    assert value["start"] == values["STARTED.json"] and value["assignments"]["continuation_cursor"] == 4


@pytest.mark.parametrize("name", ["STARTED.json", "ACQUISITION.json", "SOURCE-FREEZE.json",
                                   "REGISTRATION-REFERENCE.json", "LOCK-INPUT.json", "ROWS-DECLARED.json"])
def test_original_input_pin_tamper_refuses(tmp_path, monkeypatch, name):
    loaded, args, _ = fixture(tmp_path, monkeypatch)
    with (args[1] / name).open("ab") as stream: stream.write(b" ")
    with pytest.raises(ValueError, match="INPUT_IDENTITY"):
        loaded["materialize_phase"].authorize(*args)


def test_other_registration_cannot_replace_rows(tmp_path, monkeypatch):
    loaded, args, values = fixture(tmp_path, monkeypatch)
    values["REGISTRATION-REFERENCE.json"]["assignments"]["rows"][0]["key"] = "replacement"
    c = loaded["acquisition_contract"]; p = loaded["materialize_phase"]
    original = c.registration(args[0]); replacement = copy.deepcopy(original)
    replacement[1]["rows"][0]["key"] = "different"
    monkeypatch.setattr(c, "registration", lambda path: replacement)
    with pytest.raises(ValueError, match="REGISTRATION_REFERENCE"): p.authorize(*args)


def test_wrong_corpus_path_refuses(tmp_path, monkeypatch):
    loaded, args, _ = fixture(tmp_path, monkeypatch)
    other = tmp_path / "other"; other.mkdir()
    with pytest.raises(ValueError, match="REGISTERED_CORPUS"):
        loaded["materialize_phase"].authorize(args[0], args[1], other)


@pytest.mark.parametrize("pin", ["python", "git"])
def test_authored_wrong_host_pin_refuses(tmp_path, monkeypatch, pin):
    loaded, args, _ = fixture(tmp_path, monkeypatch)
    if pin == "python": monkeypatch.setattr(loaded["acquisition_contract"], "PYTHON", "0" * 64)
    else: monkeypatch.setattr(loaded["materialize_phase"], "GIT", "0" * 64)
    with pytest.raises(ValueError, match="TOOL_IDENTITY"):
        loaded["materialize_phase"].authorize(*args)
