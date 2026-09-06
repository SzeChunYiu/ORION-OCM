"""V5 verification is historical custody only; no original artifact is rewritten."""
from __future__ import annotations

import importlib
import io
import json
import os
from pathlib import Path
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
W = importlib.import_module("m12_paired_v5_receipt")


@pytest.mark.parametrize("argv", [[], ["--write"], ["--verify", "--write"], ["--out", "new.json"]])
def test_generation_refused_before_historical_recipe(argv, monkeypatch, tmp_path):
    frozen = tmp_path / "historical.json"
    frozen.write_bytes(b"HISTORICAL_SENTINEL\n")
    monkeypatch.setattr(W, "RECEIPT", frozen)
    def forbidden():
        raise AssertionError("historical regeneration must not run")
    monkeypatch.setattr(W, "fresh", forbidden, raising=False)
    assert W.main(argv) == 2
    assert frozen.read_bytes() == b"HISTORICAL_SENTINEL\n"


@pytest.fixture
def custody(monkeypatch):
    # Optional read-only dependency root while PR80 is pending; normal CI uses ROOT.
    root = Path(os.environ.get("OCM_V5_PREDECESSOR_ROOT", str(ROOT)))
    P = importlib.import_module("engineering_predecessor")
    monkeypatch.setattr(W, "ROOT", root)
    before = {p: P.V4.sha(root, p) for p in P.V4.read_json(root, P.MANIFEST)["frozen_files"]}
    yield P, root
    assert {p: P.V4.sha(root, p) for p in before} == before


def test_real_archive_verifies_without_current_recipe(custody, monkeypatch, capsys):
    P, root = custody
    def forbidden():
        raise AssertionError("verification must not regenerate a historical receipt")
    monkeypatch.setattr(W, "fresh", forbidden, raising=False)
    assert W.main(["--verify"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "ARCHIVED_V5_CUSTODY_VERIFIED"
    assert result["current_scientific_promotion"] == "NOT_ESTABLISHED"
    assert result["protected_reevaluation"] == "NOT_RUN"
    assert result["legacy_recipe_execution"] == "NOT_EXECUTED"
    assert result["predecessor"]["source_files"] == 302
    assert "terminal" not in result


@pytest.mark.parametrize("target", ["receipt", "prereg", "anchor", "archive"])
def test_real_custody_drift_fails_closed(custody, monkeypatch, capsys, target):
    P, root = custody
    paths = {"receipt": P.PROTECTED, "prereg": "research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V5.md",
             "anchor": P.MANIFEST, "archive": P.ARCHIVE}
    original = P.V4.raw
    def changed(base, relative):
        data = original(base, relative)
        return data + b"CUSTODY_NEGATIVE_CONTROL" if relative == paths[target] else data
    with monkeypatch.context() as patch:
        patch.setattr(P.V4, "raw", changed)
        assert W.main(["--verify"]) == 1
        assert "REFUSED" in capsys.readouterr().out


@pytest.mark.parametrize("source", ["streams.py", "m12_paired_eval.py", "phases.py", "machine.py"])
def test_each_v5_archived_source_is_bound(custody, monkeypatch, capsys, source):
    P, root = custody
    original = P.V4.raw
    data = original(root, P.ARCHIVE)
    result = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as old, zipfile.ZipFile(result, "w") as new:
        matches = [n for n in old.namelist() if n.endswith("/" + source)]
        assert len(matches) == 1
        for name in old.namelist():
            new.writestr(name, old.read(name) + (b"\n# CUSTODY_NEGATIVE_CONTROL\n" if name == matches[0] else b""))
    with monkeypatch.context() as patch:
        patch.setattr(P.V4, "raw", lambda base, relative: result.getvalue() if relative == P.ARCHIVE else original(base, relative))
        assert W.main(["--verify"]) == 1
        assert "REFUSED" in capsys.readouterr().out
