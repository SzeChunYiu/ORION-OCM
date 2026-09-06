"""Prelaunch review regressions; synthetic records and package metadata only."""
import copy
from pathlib import Path
import pytest
import trial_common as C
from trial_grade import adjudicate, grade
from test_trial import paired
from test_trial_capture import emit, replace, seal

def altered_capture(root, change, timeout=False):
    mh=emit(root);folder=root/"case-01";worker=C.read(folder/"stdout")
    for i in range(2):
        path=folder/f"call-{i}.json";p=C.read(path)
        if change=="value":
            p["result"]["consumer"]["answer"]["value"]=25
            p["invocations"][0]["result"]["value"]=25
        else:p["result"]["vectors"][0]["values"]["synthetic-a"]="3/4"
        replace(path,p);worker["calls"][i]["sha256"]=C.sha(path)
    replace(folder/"stdout",worker);replace(folder/"captured-worker.json",worker)
    process=C.read(folder/"process.json");process["worker"]=worker;process["stdout_sha256"]=C.sha(folder/"stdout")
    replace(folder/"process.json",process)
    if timeout:
        path=root/"case-02/process.json";p=C.read(path);p["timed_out"]=True;replace(path,p)
    seal(root);return mh

@pytest.mark.parametrize("change",["value","vector"])
def test_established_semantic_discrepancy_is_refine_required(tmp_path,change):
    root=tmp_path/"SYNTHETIC";mh=altered_capture(root,change)
    result=grade(root,mh)
    assert result["functional_terminal"]=="REFINE_REQUIRED"

def test_semantic_discrepancy_and_incomplete_cost_are_separate(tmp_path):
    root=tmp_path/"SYNTHETIC";mh=altered_capture(root,"value",True)
    result=grade(root,mh)
    assert result["functional_terminal"]=="REFINE_REQUIRED"
    assert result["semantic_discrepancies"] and not result["cost_evidence_complete"]
    assert result["warm_median_ratio"] is None and result["total_two_call_median_ratio"] is None

def test_registered_terminals_and_no_incomplete_medians():
    values,assignments=paired()
    assert adjudicate(values,assignments,[])["component_gate"]=="ADOPTION_CANDIDATE"
    for a in assignments:
        if a["arm"]=="sympy":values[a["index"]].update(warm_ns=95,cold_ns=1100)
    assert adjudicate(values,assignments,[])["component_gate"]=="WARM_GAIN_ONLY_COLD_COST_UNRESOLVED"
    for a in assignments:
        if a["arm"]=="sympy":values[a["index"]].update(warm_ns=95,cold_ns=900)
    assert adjudicate(values,assignments,[])["component_gate"]=="NO_PRACTICAL_GAIN"
    result=adjudicate(values,assignments,[{"reason":"PID_REUSE_NOT_INDEPENDENTLY_RESOLVED"}])
    assert result["component_gate"]=="CANNOT_CHECK" and result["warm_median_ratio"] is None

def test_manifest_binds_real_solver_python_contents():
    m=C.read(Path(__file__).with_name("MANIFEST.json"))
    base=Path(m["runtime_modules"]["sympy"]["path"]).parent
    for rel in ("polys/matrices/domainmatrix.py","polys/matrices/rref.py","polys/matrices/sdm.py","polys/domains/rationalfield.py"):
        path=base/rel
        assert str(path) in m["runtime_files"] and m["runtime_files"][str(path)]==C.sha(path)

def test_record_unchanged_does_not_hide_changed_python_content(tmp_path):
    import base64,hashlib
    package=tmp_path/"package";package.mkdir();source=package/"solver.py";source.write_bytes(b"original")
    h=base64.urlsafe_b64encode(hashlib.sha256(source.read_bytes()).digest()).decode().rstrip("=")
    record=package/"RECORD";record.write_text("solver.py,sha256="+h+",8\n")
    observed=C.record_files(package,record)
    assert observed[str(source)]==C.sha(source)
    record_sha=C.sha(record);source.write_bytes(b"tampered")
    assert C.sha(record)==record_sha
    with pytest.raises(ValueError,match="DISTRIBUTION_CONTENT_DRIFT"):C.record_files(package,record)
