"""Empty-library no-alarm, retained partial work, and explicit replay boundaries."""
import pytest
from ocm.runtime.ocm_runtime import OCMRuntime
from unary_method_store import MethodStore
from unary_method_runtime import MethodRuntime
from unary_parent_store import ParentStore
from unary_parent_runtime import ParentRuntime,ParentIndex
from unary_method_selection import contract
from unary_contract import InputRefused
from unary_solver import RegionSolver
from learning_test_support import training
from test_unary_method_runtime import fresh
from test_unary_parent_runtime import populated
import unary_method_data as O
import unary_method_plain as D

@pytest.mark.parametrize("arm",["conventional","ocm"])
@pytest.mark.parametrize("empty",["pool","positive"])
def test_empty_selected_library_is_durable_and_falls_back(tmp_path,arm,empty):
    rows=[training("B")["task"],training("C" if empty=="positive" else "B")["task"]]
    dev=fresh()
    if empty=="positive":
        dev={"schema":dev["schema"],"predicates":["A","B"],"premises":[],
             "query":{"kind":"some","left":["pred","A"],"right":["pred","B"]}}
    if arm=="conventional":store=ParentStore(tmp_path/"s",create=True)
    else:store=MethodStore(OCMRuntime(tmp_path/"s"),create=True)
    r=store.acquire_selected(rows,[dev],contract(2,1,authored=True))
    assert r["terminal"]==("NO_METHOD_ACQUIRED" if empty=="pool" else "NO_DEVELOPMENT_BENEFIT")
    assert not store.method_ids
    if arm=="conventional":
        store.persist();cold=ParentStore(store.root);b=ParentRuntime(cold)
    else:
        store.rt.persist();cold=MethodStore(OCMRuntime(store.rt.root));b=MethodRuntime(cold)
    out=b.solve(fresh());assert out["terminal"]=="CHECKED" and out["packet"]["use"]["recipes_applied"]==0

def test_partial_matcher_work_and_refusal_survive_cold_restore(tmp_path,monkeypatch):
    p=populated(tmp_path)
    def unavailable(*a):raise InputRefused("AUTHORED_RECIPE_UNAVAILABLE")
    monkeypatch.setattr(RegionSolver,"result_from_certificates",unavailable)
    r=ParentRuntime(p).solve(fresh())
    assert r["terminal"]=="CANNOT_CHECK" and r["packet"] is None
    e=r["execution_observation"]
    assert e["candidate_attempts"] and e["matching"][0]["terminal"]=="PARTIAL_WORK_UNAVAILABLE"
    assert e["matching"][0]["counters"] is None and e["parent_semantic_total"]["cache_key_nodes"]>0
    assert e["prepared_binding_total"]["bytes_hashed"]>0
    cold=ParentStore(p.root)
    assert not cold.uses and len(cold.attempts)==1

def test_index_guard_and_posting_cache_invalidate_on_revision(tmp_path):
    p=populated(tmp_path);old=ParentIndex(p);mid=p.method_ids[0]
    assert old.select("no")
    p.revise("utility","REVOKED",mid=mid)
    with pytest.raises(InputRefused,match="STALE_INDEX"):old.select("no")
    new=ParentIndex(p);assert not new.select("no") and new.work["posting_cache_misses"]==1

def test_each_actual_selection_revalidation_pass_has_observed_work(tmp_path):
    p=populated(tmp_path)
    assert p.work["selection_receipt_validations"]>=2
    assert p.work["selection_answer_revalidations"]>0 and p.work["semantic_worlds"]>=255*6*2
    rt=OCMRuntime(tmp_path/"ocm");s=MethodStore(rt,create=True)
    s.acquire_selected([training("B")["task"],training("C")["task"]],[fresh()],contract(2,1,authored=True))
    assert s.work["selection_receipt_validations"]>=2 and s.work["selection_schema_revalidations"]>0

def test_persist_rejects_new_owned_payload_even_with_unchanged_journal(tmp_path):
    p=populated(tmp_path);(p.payloads/("a"*64+".json")).write_bytes(b"{}")
    with pytest.raises(InputRefused,match="UNREFERENCED"):p.persist()

@pytest.mark.parametrize("arm",["conventional","ocm"])
def test_failed_use_write_retains_prejournal_work_and_unreached_rows(tmp_path,monkeypatch,arm):
    from unary_method_arm import run
    root=tmp_path/"store"
    if arm=="conventional":store=ParentStore(root,create=True)
    else:store=MethodStore(OCMRuntime(root),create=True)
    store.acquire_selected([training("B")["task"],training("C")["task"]],[fresh()],contract(2,1,authored=True))
    if arm=="conventional":store.persist();cls=ParentStore
    else:store.rt.persist();cls=MethodStore
    original=cls._append
    def fail(self,kind,body):
        if kind=="USE":raise OSError("authored final use write")
        return original(self,kind,body)
    monkeypatch.setattr(cls,"_append",fail)
    observed={}
    with pytest.raises(OSError,match="authored final use write"):
        run(arm,"batch",{"store":str(root),"tasks":[fresh(),fresh()],"invoke":True},observation=observed)
    assert observed["unreached_rows"]==[1]
    row=observed["rows"][0]
    assert row["terminal"]=="CANNOT_CHECK"
    known=row["pre_journal_observation"]
    assert known["dispatches"]==known["checks"]==1 and known["packet"]["use"]["recipes_applied"]==1
    assert known["execution_observation"]["prepared_binding_total"]["bytes_hashed"]>0
    with pytest.raises(InputRefused,match="INCOMPLETE_USE"):
        if arm=="conventional":ParentStore(root)
        else:MethodStore(OCMRuntime(root))
