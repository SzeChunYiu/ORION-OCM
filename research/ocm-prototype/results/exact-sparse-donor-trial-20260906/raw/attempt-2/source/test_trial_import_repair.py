"""Early-error reporting controls; no loader, binding or consumer."""
import json
from pathlib import Path
import sys
from trial_common import read, sha
from test_trial_capture import emit, replace, seal

def test_actual_worker_error_contains_input_manifest_binding(tmp_path,monkeypatch,capsys):
    import trial_worker as W
    manifest=tmp_path/"manifest.json";manifest.write_text("{}")
    case=tmp_path/"input.json";case.write_text(json.dumps({"manifest":str(manifest),"assignment":{"index":0,"arm":"reference"}}))
    def failure(*_):raise ModuleNotFoundError("No module named 'vendor'")
    monkeypatch.setattr(W,"run",failure);monkeypatch.setattr(sys,"argv",["trial_worker.py","--case",str(case)])
    assert W.main()==2
    result=json.loads(capsys.readouterr().out)
    assert result["manifest_sha256"]==sha(manifest) and result["assignment"]["index"]==0
    assert result["type"]=="ModuleNotFoundError" and result["assigned_calls"]==2

def test_original_error_shape_retains_raw_reason_without_qualification(tmp_path):
    from trial_grade import grade
    root=tmp_path/"SYNTHETIC";mh=emit(root);folder=root/"case-00"
    original=read(Path(__file__).parent/"capture-v1/case-00/stdout")
    error=dict(original,pid=1000,case_sha256=sha(folder/"input.json"))
    replace(folder/"stdout",error);replace(folder/"captured-worker.json",error)
    process=read(folder/"process.json");process.update(worker=error,exit_code=2,stdout_sha256=sha(folder/"stdout"))
    replace(folder/"process.json",process);seal(root)
    result=grade(root,mh)
    assert result["functional_terminal"]=="CANNOT_CHECK" and result["qualified_calls"]==26
    assert result["errors"][0]["worker_error"]["type"]=="ModuleNotFoundError"
    assert result["errors"][0]["worker_error"]["message"]=="No module named 'vendor'"
    assert result["warm_median_ratio"] is None
