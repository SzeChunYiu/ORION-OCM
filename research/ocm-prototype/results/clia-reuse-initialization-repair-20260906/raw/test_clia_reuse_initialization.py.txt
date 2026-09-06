"""Acquisition freshness controls halt before every donor; no prospective query executes."""
import json
from pathlib import Path

import pytest
import clia_reuse_study_worker as W
from clia_reuse_study_common import source_files, write
from clia_reuse_study_state import Actor


def config(tmp_path):
    model = tmp_path / "UNIT_PLACEHOLDER_NOT_A_MODEL"
    model.write_bytes(b"UNIT_ONLY_NO_DONOR")
    return {"phase": "acquire", "arm": "ocm", "state": str(tmp_path / "state"),
        "source_files": source_files(), "f0_sha256": "UNIT_FIXTURE", "model": str(model),
        "training_manifest": {"scope": "UNIT_FIXTURE_NO_TRAINING"},
        "rows": str(tmp_path / "rows.jsonl"), "events": str(tmp_path / "events.jsonl"),
        "tasks": {}}


def test_actual_fresh_ocm_constructor_is_not_mistaken_for_prior_state(tmp_path):
    cfg = config(tmp_path); path = tmp_path / "input.json"; write(path, cfg)
    assert not Path(cfg["state"]).exists()
    receipt = W.execute(cfg, path)
    assert receipt["status"] == "CANNOT_CHECK_STAGE"
    assert receipt["error"] == "ValueError:TASK_BINDING_CHANGED"
    assert receipt["row_count"] == 0 and not receipt["invocations"]
    assert receipt["entry_audit"]["model_liveness"] == "LIVE"
    assert (Path(cfg["state"]) / "ledger.jsonl").is_file()
    write(tmp_path / "actual-constructor-receipt.json", receipt)


def test_genuinely_prepopulated_ocm_state_is_refused_before_constructor(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    actor = Actor(cfg["state"], "ocm")
    actor.evidence({"UNIT_FIXTURE": "persisted prior observation"}, "history")
    actor.persist()
    root = Path(cfg["state"])
    before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert before["ledger.jsonl"]
    path = tmp_path / "input.json"; write(path, cfg)
    def forbidden(*args, **kwargs): raise AssertionError("constructor ran on prepopulated acquisition state")
    monkeypatch.setattr(W, "Actor", forbidden)
    with pytest.raises(ValueError, match="ACQUISITION_STATE_NOT_FRESH"):
        W.execute(cfg, path)
    after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert after == before
