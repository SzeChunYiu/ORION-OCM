"""Paired coordinator-boundary falsifiers; all source/tasks are authored."""
import copy,json,os,time
import pytest
from pathlib import Path
from assay_test_support import authored_only
from unary_contract import InputRefused
from unary_method_profile import observe
import unary_method_plain as D

def batch(tmp_path):
    from test_unary_assay_service_process import child
    from test_unary_assay_service import rows
    from learning_test_support import training
    from test_unary_method_runtime import fresh
    from unary_method_selection import contract
    store=tmp_path/"store"
    child(tmp_path/"A","conventional","acquire_selected",{"store":str(store),
        "training":[training("B")["task"],training("C")["task"]],"development":[fresh()],
        "contract":contract(2,1,authored=True)})
    p,v=child(tmp_path/"B","conventional","presented_batch",{"store":str(store),"rows":rows()[:1],"invoke":True})
    r=json.loads((tmp_path/"B/request.json").read_bytes())
    return tmp_path/"B",r,dict(arm="conventional",mode="presented_batch",request=r,sources=p["source_before"],
                              profile=p["profile"],deadline=p["deadline_monotonic"])

def alter_row(root,change,*,partial=False):
    from unary_method_process import stamp
    data=D.parse((root/"result.json").read_bytes());ref=data["outcome"]["rows"][0]
    path=root/ref["path"];row=D.parse(path.read_bytes());change(row)
    path.write_bytes(D.raw(row));st=stamp(path)
    ref.update(bytes=st["bytes"],sha256=st["sha256"],terminal=row["terminal"])
    if partial:data["outcome"]["terminal"]="CANNOT_CHECK"
    raw=D.raw(data);(root/"result.json").write_bytes(raw);(root/"stdout.bin").write_bytes(raw)
    p=D.parse((root/"PROCESS.json").read_bytes())
    for key,name in (("result","result.json"),("result_after","result.json"),("stdout","stdout.bin"),("stdout_after","stdout.bin")):
        p[key]=stamp(root/name)
    (root/"PROCESS.json").write_bytes(D.raw(p))

def test_known_committed_use_survives_operational_row_refusal(tmp_path):
    import unary_assay_auth as a
    root,r,kw=batch(tmp_path)
    assert a.inspect(root,work={},**kw)["terminal"]=="CHECKED"
    alter_row(root,lambda row:row.update(terminal="CANNOT_CHECK",observation_error="authored after solve"),partial=True)
    work={};facts=a.inspect(root,work=work,**kw)
    assert facts["terminal"]=="CANNOT_CHECK" and facts["rows"][0]["use"]["recipes_applied"]==1
    assert facts["rows"][0]["terminal"]=="CANNOT_CHECK"

def test_actual_replay_work_survives_later_answer_check_failure(tmp_path,monkeypatch):
    import unary_assay_auth as a
    root,r,kw=batch(tmp_path);work={}
    monkeypatch.setattr(a,"verify_answer",lambda *args,**kwargs:False)
    with pytest.raises(a.ControlFailure,match="INVALID_ACCEPTED_ANSWER"):a.inspect(root,work=work,**kw)
    assert work["replay_work"]["journal_rows_read"]>0
    assert work["retained_audit_wall_s"]>0

def test_load_truncation_is_global_custody(tmp_path):
    import unary_assay_auth as a
    p=tmp_path/"record.json";p.write_bytes(D.raw({"clean":True}))
    assert a.load(p,{})=={"clean":True}
    p.write_bytes(b'{"clean":')
    with pytest.raises(a.CustodyFailure):a.load(p,{})
    p.unlink()
    with pytest.raises(a.CustodyFailure):a.load(p,{})

def test_semantic_cause_survives_secondary_source_failure(tmp_path,monkeypatch):
    import unary_assay_phase as phase
    count=0
    def source(*args):
        nonlocal count
        count+=1
        if count>=3:raise OSError("authored secondary")
        return {"authored":"source"}
    monkeypatch.setattr(phase.D,"sources",source)
    monkeypatch.setattr(phase,"launch",lambda *args,**kwargs:{"returncode":0,"terminal":"COMPLETED"})
    def fail(*args,**kwargs):raise phase.A.ControlFailure("authored invalid accepted answer")
    monkeypatch.setattr(phase.A,"inspect",fail)
    s=phase.Session(tmp_path/"run",deadline=time.monotonic()+20,profile=observe())
    s.expect("e0--B--EXACT_PARENT",{"phase":"B"})
    s.call("e0--B--EXACT_PARENT","EXACT_PARENT","presented_batch",{"rows":[]})
    assert s.abort["kind"]=="SEMANTIC_CONTROL_FAILED"
    assert len(s.abort["causes"])==2

def test_post_generation_failure_does_not_relabel_generation(tmp_path,monkeypatch):
    import unary_assay_coordinator as c
    from test_unary_assay_coordinator import fixture
    def fail(*args,**kwargs):raise OSError("authored later phase")
    monkeypatch.setattr(c,"episode",fail)
    out=c.run_authored(tmp_path/"run",[fixture()],deadline=time.monotonic()+20,profile=observe())
    assert out["episodes"][0]["generation_terminal"]=="GENERATED"
    assert out["episodes"][0]["failed_stage"]=="EPISODE"

def test_copy_binds_root_mode_and_refuses_source_root_drift(tmp_path,monkeypatch):
    import unary_assay_ledger as l
    src=tmp_path/"source";src.mkdir();(src/"data").write_bytes(b"data");src.chmod(0o700)
    old=os.umask(0o022)
    try:
        copy=l.copy_store(src,tmp_path/"copy",deadline=time.monotonic()+20)
        assert (tmp_path/"copy").stat().st_mode&0o777==0o700
        assert copy["before"]["."]["mode"]==0o700
    finally:os.umask(old)
    original=l.sync_dir
    def sync(path):
        original(path)
        if path==tmp_path/"drift":src.chmod(0o755)
    monkeypatch.setattr(l,"sync_dir",sync)
    with pytest.raises(InputRefused,match="COPY_IDENTITY"):
        l.copy_store(src,tmp_path/"drift",deadline=time.monotonic()+20)
