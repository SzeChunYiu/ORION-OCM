"""Fixed launch data and source-copy preflight controls, without profile dispatch."""
import os
from pathlib import Path
import pytest
import unary_assay_launch_contract as L
import unary_assay_launch_profile as P
import unary_assay_launch as A
import unary_method_outer as D
RUNTIME=Path("/home/billy/orion-director-work/20260907/unary-assay-runtime-snapshot-v1")


@pytest.fixture(autouse=True)
def restore_resource_registry():
    import sys
    names=P.RESOURCE;before={name:sys.modules.get(name) for name in names}
    try:yield
    finally:
        for name,value in before.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value

def sample():
    return {"schema":"ocm.unary-launch-plan.v1","run_id":"authored-profile-control","mode":"AUTHORED_PROBE",
        "duration_ns":20000000000,"cpu":min(os.sched_getaffinity(0)),"sources":{"source.py":"a"*64},
        "input":{"sha256":"b"*64,"bytes":20},"runtime_seal":L.SNAPSHOT_SEAL,"mapping_seal":L.MAPPING_SEAL,"python":L.B.DEFAULT}

@pytest.mark.parametrize("fault",["mode","cpu","duration","registered_input","registered_clock","source_escape","source_dot","python","runtime","input_bool"])
def test_strict_fixed_launch_data_clean_and_refusal(fault):
    value=sample();assert L.plan(value)==value
    if fault=="mode":value["mode"]="callback"
    elif fault=="cpu":value["cpu"]=True
    elif fault=="duration":value["duration_ns"]=True
    elif fault=="registered_input":value.update(mode="REGISTERED",duration_ns=L.DURATION)
    elif fault=="registered_clock":value.update(mode="REGISTERED",input=None)
    elif fault=="source_escape":value["sources"]={"../source.py":"a"*64}
    elif fault=="source_dot":value["sources"]={".":"a"*64}
    elif fault=="python":value["python"]={**value["python"],"executable":"/alternate"}
    elif fault=="runtime":value["mapping_seal"]="c"*64
    else:value["input"]["bytes"]=True
    with pytest.raises(ValueError):L.plan(value)

def test_consumed_plan_bytes_must_match_observed_hash(tmp_path,monkeypatch):
    path=tmp_path/"input";r=L.write(path,{"clean":True});assert L.read(path,r["sha256"])=={"clean":True}
    original=Path.open;calls=[]
    class Changed:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,n):return b'{"evil":true}'
    def opened(p,*args,**kwargs):
        if p==path and args==("rb",):
            calls.append(1)
            if len(calls)==1:return Changed()
        return original(p,*args,**kwargs)
    monkeypatch.setattr(Path,"open",opened)
    with pytest.raises(ValueError,match="CONSUMED"):L.read(path,r["sha256"])

def test_create_only_durable_record_and_alias_refusal(tmp_path):
    p=tmp_path/"record";r=L.write(p,{"v":1});assert L.read(p,r["sha256"])=={"v":1}
    with pytest.raises(FileExistsError):L.write(p,{"v":2})
    (tmp_path/"alias").hardlink_to(p)
    with pytest.raises(ValueError,match="REGULAR"):L.stamp(p)

@pytest.mark.skipif(not RUNTIME.exists(),reason="Exact reviewed laptop runtime snapshot is host-specific")
def test_real_prepare_copy_and_no_start_after_source_drift(tmp_path,monkeypatch):
    review=L.write(tmp_path/"review.json",{"scope":"AUTHORED_SOURCE_CONTRACT_CONTROL","sources":D.sources()});source=D.sources()
    ready=P.prepare(tmp_path/"prepared",RUNTIME,run_id="authored-preflight-control",mode="AUTHORED_PROBE",
        duration_ns=20000000000,cpu=min(os.sched_getaffinity(0)),input_value={"case":"normal"},review=review)
    copied=Path(ready["template"]["materials"][0]["path"])
    assert {str(p.relative_to(copied)):L.stamp(p)["sha256"] for p in copied.rglob("*") if p.is_file()}==source
    assert ready["template"]["aa_exec"]["path"].endswith("/payload/usr/bin/aa-exec")
    assert all(f["guest"]!="/usr/bin/aa-exec" for f in ready["template"]["files"])
    assert D.sources()==source
    landmark=ready["template"]["materials"][1]
    assert landmark["guest"].endswith("/lib/python3.11")
    assert list((Path(landmark["path"])/"lib-dynload").iterdir())==[]
    inventory=L.read(landmark["inventory"]["path"],landmark["inventory"]["sha256"])
    assert sum(v["type"]=="file" for v in inventory.values())==734
    assert inventory["lib-dynload"]=={"type":"directory"}
    lineage=L.read(ready["stdlib_copy"]["path"],ready["stdlib_copy"]["sha256"])
    assert len(lineage["copied_sha256"])==734
    monkeypatch.setattr(D,"sources",lambda:{"wrong":"0"*64})
    result=A.launch(L.stamp(tmp_path/"prepared/PREPARED.json"))
    assert result["terminal"]=="LAUNCH_REFUSED" and result["started"] is None and result["dispatch"] is None
    assert "SOURCE_DRIFT" in result["error"]["message"]
    assert not (tmp_path/"prepared/STARTED.json").exists()

def test_oversized_launch_record_refuses_before_body_read(tmp_path,monkeypatch):
    path=tmp_path/"oversized";path.write_bytes(b"x"*(L.D.MAX_BYTES+1))
    original=Path.open
    def opened(p,*args,**kwargs):
        if p==path:pytest.fail("oversized record body was opened")
        return original(p,*args,**kwargs)
    monkeypatch.setattr(Path,"open",opened)
    with pytest.raises(ValueError,match="DATA_BOUND"):L.read(path,"0"*64)
