"""Whole promised-artifact boundary and observed-exit ordering."""
import copy,time
import pytest
from assay_test_support import authored_only
from unary_method_profile import observe
from test_unary_assay_coordinator_boundaries import batch,alter_row
import unary_method_plain as D

@pytest.mark.parametrize("fault",["stdout_missing","missing_field","row_changed"])
def test_every_promised_artifact_failure_is_custody(tmp_path,fault):
    import unary_assay_auth as a
    root,request,kw=batch(tmp_path)
    assert a.inspect(root,work={},**kw)["terminal"]=="CHECKED"
    if fault=="stdout_missing":(root/"stdout.bin").unlink()
    elif fault=="missing_field":
        p=D.parse((root/"PROCESS.json").read_bytes());del p["source_after"]
        (root/"PROCESS.json").write_bytes(D.raw(p))
    else:
        row=next((root/"rows").iterdir());row.write_bytes(b"{}")
    with pytest.raises(a.CustodyFailure):a.inspect(root,work={},**kw)

def test_refused_process_does_not_promise_optional_result(tmp_path):
    import unary_assay_auth as a
    root,request,kw=batch(tmp_path)
    p=D.parse((root/"PROCESS.json").read_bytes());p["terminal"]="PROCESS_REFUSED";p["returncode"]=2
    p.pop("result",None);p.pop("result_after",None);(root/"PROCESS.json").write_bytes(D.raw(p))
    (root/"result.json").unlink()
    assert a.inspect(root,work={},**kw)["terminal"]=="CANNOT_CHECK"

def test_checked_partial_receipt_is_authenticated_without_causal_credit(tmp_path):
    import unary_assay_auth as a
    root,request,kw=batch(tmp_path)
    def change(row):
        row.update(partial_observation=row["result"],result=None,terminal="CANNOT_CHECK")
    alter_row(root,change,partial=True)
    facts=a.inspect(root,work={},**kw)
    assert facts["terminal"]=="CANNOT_CHECK"
    assert facts["rows"][0]["terminal"]=="CANNOT_CHECK" and facts["rows"][0]["use"]["recipes_applied"]==1

@pytest.mark.parametrize("code",[-9,2])
def test_observed_signal_precedes_optional_store_read(tmp_path,monkeypatch,code):
    import unary_assay_phase as p
    monkeypatch.setattr(p,"launch",lambda *a,**k:{"returncode":code,"terminal":"PROCESS_REFUSED"})
    monkeypatch.setattr(p.A,"inspect",lambda *a,**k:{"terminal":"CANNOT_CHECK","rows":[]})
    s=p.Session(tmp_path/"run",deadline=time.monotonic()+20,profile=observe())
    s.expect("A",{"phase":"A"})
    s.call("A","OCM_ENABLED","acquire_selected",{"store":str(tmp_path/"absent")})
    if code<0:assert s.abort["reason"]=="CHILD_SIGNAL"
    else:assert s.abort is None
    assert s.slots["A"]["state"]=="UNAVAILABLE"

def test_post_source_drift_marks_known_call_unavailable(tmp_path,monkeypatch):
    import unary_assay_phase as p
    n=0
    def sources(*a):
        nonlocal n
        n+=1
        return {"authored":"before" if n<3 else "changed"}
    monkeypatch.setattr(p.D,"sources",sources)
    monkeypatch.setattr(p,"launch",lambda *a,**k:{"returncode":0,"terminal":"COMPLETED"})
    monkeypatch.setattr(p.A,"inspect",lambda *a,**k:{"terminal":"CHECKED","rows":[]})
    s=p.Session(tmp_path/"run",deadline=time.monotonic()+20,profile=observe())
    s.expect("B",{"phase":"B"});s.call("B","EXACT_PARENT","presented_batch",{"rows":[]})
    assert s.abort["kind"]=="CANNOT_CHECK" and s.slots["B"]["state"]=="UNAVAILABLE"
