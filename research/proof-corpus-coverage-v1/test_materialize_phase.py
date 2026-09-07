"""Authored continuation controls; no production material or controller dispatch."""
import copy
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest


def modules():
    import materialize_boot
    return materialize_boot.load()


def start():
    return dict(boot_id="fixture-boot", monotonic_seconds=100.0,
                whole_deadline_monotonic=200.0)


@pytest.mark.parametrize("now,boot", [(99, "fixture-boot"), (200, "fixture-boot"),
                                      (201, "fixture-boot"), (120, "other-boot")])
def test_original_clock_refuses_bad_boundary(now, boot):
    p = modules()["materialize_phase"]
    with pytest.raises((ValueError, TimeoutError)):
        p.clock(start(), now=now, boot=boot)


def test_original_clock_never_restarts():
    p = modules()["materialize_phase"]
    assert p.clock(start(), now=150, boot="fixture-boot") == 50
    assert start()["whole_deadline_monotonic"] == 200


def clean_receipt():
    return dict(terminal="COMPLETED", returncode=0, evidence_complete=True,
                dispatch=dict(state="STARTED", attempted=True, pid=123),
                cleanup=dict(reaped=True, members_empty=True, controllers_removed=True))


@pytest.mark.parametrize("mutation", [
    ("returncode", True), ("returncode", 1), ("evidence_complete", False),
    ("dispatch.pid", True), ("dispatch.pid", 0), ("dispatch.attempted", False),
    ("cleanup.reaped", False), ("cleanup.members_empty", False),
    ("cleanup.controllers_removed", False)])
def test_process_refusal_is_not_readiness(mutation):
    p = modules()["materialize_phase"]; r = clean_receipt()
    key, value = mutation
    if "." in key:
        outer, inner = key.split("."); r[outer][inner] = value
    else: r[key] = value
    with pytest.raises(ValueError, match="PROCESS_CUSTODY"):
        p.process_ok(r)


def test_clean_process_receipt():
    modules()["materialize_phase"].process_ok(clean_receipt())


def test_exact_input_bytes_not_semantic_json(tmp_path):
    p = modules()["materialize_phase"]
    path = tmp_path / "input.json"; path.write_bytes(b"{\"a\":1}\n")
    value, binding = p.read(path)
    assert value == {"a": 1}
    path.write_bytes(b"{ \"a\": 1 }\n")
    with pytest.raises(ValueError, match="INPUT_DRIFT"):
        p.recheck([binding])


def test_noncanonical_input_path_refuses(tmp_path):
    p = modules()["materialize_phase"]
    path = tmp_path / "data"; path.write_text("{}")
    (tmp_path / "alias").symlink_to(path)
    with pytest.raises(ValueError): p.read(tmp_path / "alias")


def test_source_loader_ignores_ambient_module():
    import types
    fake = types.ModuleType("materialize_git"); fake.POISON = True
    sys.modules["materialize_git"] = fake
    loaded = modules()
    assert not hasattr(loaded["materialize_git"], "POISON")
    assert loaded["materialize_git"].__source_record__["sha256"]


def test_cli_refuses_without_isolated_flags(tmp_path):
    source = Path(__file__).with_name("materialize_run.py")
    result = subprocess.run([sys.executable, str(source)], capture_output=True, timeout=10)
    assert result.returncode != 0 and b"-I -S" in result.stderr
    assert list(tmp_path.iterdir()) == []


def test_cli_invalid_inputs_cannot_dispatch(tmp_path):
    source = Path(__file__).with_name("materialize_run.py")
    inputs = []
    for name in ("registration", "episode", "corpus"):
        path = tmp_path / name; path.mkdir(); inputs.append(str(path))
    out = tmp_path / "out"
    result = subprocess.run([str(Path(sys.executable).resolve()), "-I", "-S", str(source),
                             *inputs, str(out)], capture_output=True, timeout=10, env={})
    assert result.returncode == 2
    value = json.loads((out / "MATERIALIZATION.json").read_bytes())
    assert value["terminal"] == "CANNOT_CHECK" and value["resource"] == {}
    assert value["semantic_checks_reached"] == 0 and not (out / "resource").exists()


def test_expired_input_no_dispatch(tmp_path, monkeypatch):
    loaded = modules(); run = loaded["materialize_run"]; p = loaded["materialize_phase"]
    roots = [tmp_path / n for n in ("reg", "episode", "bare")]
    for path in roots: path.mkdir()
    def refuse(*args): raise TimeoutError("WHOLE_EPISODE_DEADLINE")
    monkeypatch.setattr(p, "authorize", refuse)
    monkeypatch.setattr(run, "host", lambda: {})
    monkeypatch.setattr(run, "dispatch", lambda *a: pytest.fail("dispatch"))
    result = run.run(*roots, tmp_path / "out")
    assert result["terminal"] == "CANNOT_CHECK"
    assert result["error"]["message"] == "WHOLE_EPISODE_DEADLINE"


def test_output_overlap_never_creates(tmp_path):
    run = modules()["materialize_run"]
    reg = tmp_path / "reg"; reg.mkdir()
    episode = tmp_path / "episode"; episode.mkdir()
    bare = tmp_path / "bare"; bare.mkdir()
    with pytest.raises(ValueError, match="overlaps"):
        run.run(reg, episode, bare, reg / "out")
    assert not (reg / "out").exists()


def test_executed_bootstrap_drift_refuses(tmp_path):
    import types
    from hashlib import sha256
    source = Path(__file__).with_name("materialize_boot.py"); raw = source.read_bytes()
    copied = tmp_path / source.name; copied.write_bytes(raw)
    module = types.ModuleType("authored_boot_drift"); module.__file__ = str(copied)
    module.__source_record__ = dict(path=str(copied), sha256=sha256(raw).hexdigest(), bytes=len(raw))
    sys.modules[module.__name__] = module
    exec(compile(raw, str(copied), "exec"), module.__dict__)
    copied.write_bytes(raw + b"\n# drift after load\n")
    try:
        with pytest.raises(ValueError, match="BOOT_LOADED_DRIFT"): module.load()
    finally:
        sys.modules.pop("materialize_boot", None); sys.modules.pop(module.__name__, None)
