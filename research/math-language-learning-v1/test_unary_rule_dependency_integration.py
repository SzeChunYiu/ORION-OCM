"""Actual selected donor persistence/application in both unchanged authority adapters."""
import copy
import pytest
from unary_contract import InputRefused
from unary_solver import RegionSolver
from unary_verify import verify_result
from learning_test_support import pred,s,task
from test_unary_rule_dependency import donors
from unary_method_selection import acquire_selected,contract,validate_receipt

def fresh():
    x=["and",pred("A"),pred("D")]
    return task([s("every",x,"B"),s("no",x,"B"),s("some","C","C")],s("no",x,"C"))

def test_selector_requires_actual_development_benefit():
    training=[x["task"] for x in donors()]
    r=acquire_selected(training,[fresh()],contract(2,1,authored=True),dependency_donor=True)
    assert r["terminal"]=="SELECTED" and len(r["selected"])==1
    assert r["ranking"][0]["benefit"]>0 and r["trials"][0]["application"]["dependency"]
    validate_receipt(r)
    unknown=task([],s("some","A","B"))
    no=acquire_selected(training,[unknown],contract(2,1,authored=True),dependency_donor=True)
    assert no["terminal"]=="NO_DEVELOPMENT_BENEFIT" and not no["selected"]
    assert no["acquisition"]["rules"] and no["trials"][0]["application"]["terminal"]=="NO_MATCH"
    off=acquire_selected(training,[fresh()],contract(2,1,authored=True),dependency_donor=False)
    assert off["terminal"]=="NO_METHOD_ACQUIRED"

@pytest.mark.parametrize("field",["resolvent","semantic_key"])
def test_resealed_bad_support_is_not_selection_authority(field):
    import unary_method_plain as D
    r=acquire_selected([x["task"] for x in donors()],[fresh()],contract(2,1,authored=True),dependency_donor=True)
    support=r["acquisition"]["rules"][0]["supports"][0]
    if field=="resolvent":support["dependency"]["resolvent"]=[pred("B")]
    else:support["semantic_key"]="0"*64
    r.pop("receipt_sha256");r["receipt_sha256"]=D.hashed(r)
    with pytest.raises(InputRefused):validate_receipt(r)

@pytest.mark.parametrize("arm",["conventional","ocm"])
def test_both_adapters_admit_replay_use_and_respect_roles(tmp_path,monkeypatch,arm):
    from ocm.runtime.ocm_runtime import OCMRuntime
    from unary_method_store import MethodStore
    from unary_method_runtime import MethodRuntime
    from unary_parent_store import ParentStore
    from unary_parent_runtime import ParentRuntime
    if arm=="conventional":
        store=ParentStore(tmp_path/arm,create=True);runtime=None
    else:
        runtime=OCMRuntime(tmp_path/arm);store=MethodStore(runtime,create=True)
    r=store.acquire_selected([x["task"] for x in donors()],[fresh()],contract(2,1,authored=True),dependency_donor=True)
    assert r["terminal"]=="SELECTED" and len(store.method_ids)==1
    mid=store.method_ids[0]
    if runtime is not None:
        runtime.persist();cold=MethodStore(OCMRuntime(runtime.root));b=MethodRuntime(cold)
    else:store.persist();cold=ParentStore(store.root);b=ParentRuntime(cold)
    complete=RegionSolver.complete
    monkeypatch.setattr(RegionSolver,"complete",lambda *a:pytest.fail("hidden query solve"))
    result=b.solve(fresh())
    assert result["terminal"]=="CHECKED" and result["packet"]["use"]["dependency"]
    assert verify_result(fresh(),result["packet"]["result"])
    assert result["packet"]["execution"]["parent_completions"]==0
    monkeypatch.setattr(RegionSolver,"complete",complete)
    if arm=="conventional":cold.revise("utility","UNKNOWN",mid=mid)
    else:cold.rt.revoke([cold.read(mid)["envelope"]["utility"]])
    refused=b.solve(fresh())
    assert refused["terminal"]=="CHECKED" and refused["packet"]["use"]["recipes_applied"]==0
    if arm=="conventional":
        cold.revise("utility","LIVE",mid=mid);restored=ParentStore(cold.root)
    else:
        cold.rt.reinstate([cold.read(mid)["envelope"]["utility"]]);cold.rt.persist()
        restored=MethodStore(OCMRuntime(cold.rt.root))
    assert len(restored.uses)==2 and restored.read(mid)["eligible"]

def test_shared_postings_keep_order_eligibility_cache_and_probe_costs():
    from unary_method_postings import contents
    class Store:
        method_ids=["a","b","c"]
        def read(self,mid):
            return {"eligible":mid!="b","correctness":"LIVE","selection":"UNKNOWN" if mid=="b" else "LIVE",
                    "envelope":{"rule":{"conclusion":{"kind":"every" if mid=="a" else "no"}}}}
    store=Store();work={};postings,refusals=contents(store,"version",work)
    assert postings=={"every":("a","c"),"no":("a","c")}
    assert [x["method_id"] for x in refusals]==["b"]
    assert work["postings_built"]==4
    assert contents(store,"version",work)==(postings,refusals) and work["posting_cache_hits"]==1

def test_all_new_helpers_are_in_both_declared_closures():
    import unary_method_plain as D
    import unary_parent_sources as P
    import unary_method_outer as O
    names={"unary_rule_clauses.py","unary_rule_clause_apply.py","unary_rule_dependency.py","unary_rule_dependency_check.py"}
    for source in (D.sources(),P.sources(),O.sources()):
        assert names <= {p.rsplit("/",1)[-1] for p in source}
