"""Actual OCM and conventional parity, with no generated study tasks."""
import copy
import pytest
from ocm.runtime.ocm_runtime import OCMRuntime
from unary_method_store import MethodStore
from unary_method_runtime import MethodRuntime
from unary_parent_store import ParentStore
from unary_parent_runtime import ParentRuntime
from unary_method_selection import contract
from learning_test_support import training
from test_unary_method_runtime import fresh
from unary_solver import RegionSolver
from unary_verify import verify_result
from unary_contract import InputRefused
import unary_method_data as D

def both(tmp_path):
    parent=ParentStore(tmp_path/"parent",create=True)
    rt=OCMRuntime(tmp_path/"ocm");ocm=MethodStore(rt,create=True)
    rows=[training("B")["task"],training("C")["task"]];c=contract(2,1,authored=True)
    left=parent.acquire_selected(rows,[fresh()],c);right=ocm.acquire_selected(rows,[fresh()],c)
    for key in ("pool_sha256","ranking_sha256","library_sha256"):assert left[key]==right[key]
    return parent,ocm

def test_matched_actual_selected_rules_without_hidden_completion(tmp_path,monkeypatch):
    p,o=both(tmp_path);a=ParentRuntime(p);b=MethodRuntime(o)
    monkeypatch.setattr(RegionSolver,"complete",lambda *a:pytest.fail("hidden query completion"))
    x=a.solve(fresh());y=b.solve(fresh())
    assert x["terminal"]==y["terminal"]=="CHECKED" and y["checks"]==x["checks"]==1
    assert x["packet"]["use"]==y["packet"]["use"]
    assert verify_result(fresh(),y["packet"]["result"])
    assert o.read(o.method_ids[0])["envelope"]["utility"]
    assert o.selection["receipt"]["contract"]["schema"]!="authored-selected.v1"

def test_actual_ocm_warm_cache_and_selection_cold_restore(tmp_path):
    p,o=both(tmp_path);b=MethodRuntime(o);a=b.solve(fresh());c=b.solve(fresh())
    assert c["packet"]["execution"]["engine_cache_reused"]
    assert c["packet"]["execution"]["index"]["posting_cache_hits"]==1
    assert c["packet"]["execution"]["parent_semantic_total"]["cache_misses"]<a["packet"]["execution"]["parent_semantic_total"]["cache_misses"]
    o.rt.persist();cold=MethodStore(OCMRuntime(o.rt.root))
    assert cold.selection==o.selection and len(cold.uses)==2

@pytest.mark.parametrize("role,expected",[("schema_environment",0),("discovery",1),("utility",0)])
def test_matched_role_withdrawal_restart_and_reinstate(tmp_path,role,expected):
    p,o=both(tmp_path);mid=p.method_ids[0];p.revise(role,"REVOKED",mid=mid)
    eid=o.read(mid)["envelope"][role];o.rt.revoke([eid]);o.rt.persist()
    p=ParentStore(p.root);o=MethodStore(OCMRuntime(o.rt.root))
    for bridge in (ParentRuntime(p),MethodRuntime(o)):
        r=bridge.solve(fresh());assert r["terminal"]=="CHECKED" and r["packet"]["use"]["recipes_applied"]==expected
    p.revise(role,"LIVE",mid=mid);o.rt.reinstate([eid])
    assert ParentRuntime(p).solve(fresh())["packet"]["use"]["recipes_applied"]==1
    assert MethodRuntime(o).solve(fresh())["packet"]["use"]["recipes_applied"]==1

def test_parent_source_check_once_per_public_solve_and_no_final_cache(tmp_path,monkeypatch):
    p,_=both(tmp_path)
    import unary_parent_sources as S
    actual=S.sources;calls=[]
    def counted(work=None):calls.append(1);return actual(work)
    monkeypatch.setattr(S,"sources",counted)
    b=ParentRuntime(p);one=b.solve(fresh());two=b.solve(fresh())
    assert len(calls)==2
    assert one["qid"]!=two["qid"] and two["packet"]["execution"]["preparations"]==1

def test_parent_wrong_candidate_is_independently_rejected(tmp_path,monkeypatch):
    p,_=both(tmp_path)
    import unary_method_execution as E
    original=E.propose
    def forged(*a,**k):
        out=original(*a,**k);out["result"]["status"]="UNKNOWN";return out
    monkeypatch.setattr(E,"propose",forged)
    r=ParentRuntime(p).solve(fresh())
    assert r["terminal"]=="CANNOT_CHECK" and r["packet"] is None
    assert "ANSWER_CERTIFICATE" in r["backend_failure"]
    assert len(ParentStore(p.root).attempts)==1

def test_parent_admission_payload_failure_is_durable_pending(tmp_path,monkeypatch):
    import unary_parent_payloads as P
    p=ParentStore(tmp_path/"parent",create=True)
    monkeypatch.setattr(P,"put",lambda *a:(_ for _ in ()).throw(OSError("authored payload failure")))
    with pytest.raises(OSError):
        p.acquire_selected([training("B")["task"],training("C")["task"]],[fresh()],contract(2,1,authored=True))
    with pytest.raises(InputRefused,match="INCOMPLETE_ADMISSION"):ParentStore(p.root)
