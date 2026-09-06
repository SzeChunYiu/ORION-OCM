"""Functional controls for gate interpreter selection and refused-attempt custody."""
from pathlib import Path
import importlib
import json
import os
import sys
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
R = importlib.import_module("record_engineering_revision")


def test_differently_named_recorder_cannot_run_a_decoy_python(tmp_path, monkeypatch):
    selected = tmp_path / "selected-python3"
    selected.symlink_to(sys.executable)
    decoy = tmp_path / "python"
    decoy.write_text("#!/bin/sh\necho WRONG_INTERPRETER\nexit 17\n")
    decoy.chmod(0o755)
    monkeypatch.setattr(R.sys, "executable", str(selected))
    env = dict(os.environ)
    env["PATH"] = str(tmp_path)
    log = tmp_path / "gate.log"
    with log.open("wb") as output:
        result = R.execute_gate(["python", "-c", "print('SELECTED_INTERPRETER')"], tmp_path, env, output)
    assert result.returncode == 0
    assert log.read_text().strip() == "SELECTED_INTERPRETER"


@pytest.mark.parametrize("mode", ["skipped", "missing", "malformed"])
def test_zero_exit_invalid_junit_is_retained_without_receipt_or_selection(tmp_path, monkeypatch, mode):
    for name in ("src", "tests", "tools"): (tmp_path / name).mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    config = tmp_path / R.E.V4.CONFIG_PATH
    config.parent.mkdir(parents=True)
    config.write_bytes((ROOT / R.E.V4.CONFIG_PATH).read_bytes())
    pointer = tmp_path / R.E.CURRENT
    pointer.parent.mkdir(parents=True)
    pointer.write_text("UNCHANGED_PRIOR_POINTER")
    monkeypatch.setattr(R.E.P, "verify", lambda _: {"fixture_only": True})
    def fake_gate(argv, root, env, log):
        path = Path(next(x.split("=", 1)[1] for x in argv if x.startswith("--junitxml=")))
        path = root / path
        if mode == "malformed": path.write_text("not XML")
        elif mode == "skipped":
            count = 125
            cases = '<testcase name="skipped"><skipped/></testcase>' + '<testcase name="fixture"/>' * (count - 1)
            path.write_text('<testsuites><testsuite tests="125" errors="0" failures="0" skipped="1">'
                            + cases + '</testsuite></testsuites>')
        log.write(b"Test fixture only; no process execution claimed.\n")
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(R, "execute_gate", fake_gate)
    assert R.record(tmp_path) == 1
    runs = tmp_path / R.E.DIRECTORY / "runs"
    failed = list(runs.glob("*/*/FAILED.json"))
    assert len(failed) == 1
    report = json.loads(failed[0].read_text())
    assert report["executions"][0]["exit_code"] == 0
    assert report["reason"]
    assert report["current_selection_updated"] is False
    assert pointer.read_text() == "UNCHANGED_PRIOR_POINTER"
    assert not list(runs.glob("*/*/RECEIPT.json"))
