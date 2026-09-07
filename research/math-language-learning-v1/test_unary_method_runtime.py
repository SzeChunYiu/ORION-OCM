"""Actual registered operator/SV execution with checked method and parent routes."""
import importlib,importlib.util
import pytest
from unary_contract import InputRefused
from unary_verify import verify_result
from unary_solver import RegionSolver
from unary_test_support import task,statement as s,pred
from test_unary_method_store import populated

def bridge(store):
    assert importlib.util.find_spec("unary_method_runtime"),"missing actual runtime bridge"
    return importlib.import_module("unary_method_runtime").MethodRuntime(store)

def fresh():
    x=["and",pred("A"),pred("D")]
    return task([s("every",x,"B"),s("no","B","C"),s("some","D","D")],s("no",x,"C"))

def test_actual_recipe_without_hidden_query_solve(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path);b=bridge(store)
    monkeypatch.setattr(RegionSolver,"complete",lambda *a:pytest.fail("hidden parent query solve"))
    out=b.solve(fresh())
    assert out["terminal"]=="CHECKED" and out["packet"]["use"]["recipes_applied"]==1
    assert out["packet"]["use"]["method_id"] in store.method_ids
    assert verify_result(fresh(),out["packet"]["result"])
    assert out["trace"]["stages"][-1]["stage"]=="COMMITMENT"
    assert out["trace"]["stages"][-1]["status"]=="PASS"
    assert b.dispatches==1 and b.checks==1

def test_same_store_knockout_and_fresh_request_registry(tmp_path):
    rt,store,_=populated(tmp_path);b=bridge(store)
    yes=b.solve(fresh());no=b.solve(fresh(),invoke=False)
    assert yes["terminal"]==no["terminal"]=="CHECKED"
    assert yes["packet"]["result"]["status"]==no["packet"]["result"]["status"]
    assert no["packet"]["use"]["recipes_applied"]==0
    assert no["packet"]["execution"]["parent_completions"]==1
    assert yes["qid"]!=no["qid"] and len(store.uses)==2

@pytest.mark.parametrize("kind",["unknown","inconsistent","no_match"])
def test_semantic_outcomes_are_not_checking_failure(tmp_path,kind):
    rt,store,_=populated(tmp_path);b=bridge(store)
    if kind=="unknown":t=task([],s("every","A","B"));expected="UNKNOWN"
    elif kind=="inconsistent":t=task([s("some","A","A"),s("no","A","A")],s("no","A","B"));expected="INCONSISTENT"
    else:t=task([s("no","A","B")],s("no","A","B"));expected="ENTAILED"
    out=b.solve(t)
    assert out["terminal"]=="CHECKED" and out["packet"]["result"]["status"]==expected
    assert out["packet"]["use"]["recipes_applied"]==0 and verify_result(t,out["packet"]["result"])

def test_used_support_removal_and_restore(tmp_path):
    rt,store,_=populated(tmp_path);b=bridge(store);t=fresh()
    old=b.solve(t);t["premises"].pop(old["packet"]["use"]["cover"][0])
    removed=b.solve(t);restored=b.solve(fresh())
    assert removed["packet"]["use"]["recipes_applied"]==0
    assert restored["packet"]["use"]["recipes_applied"]==1
    assert len({x["qid"] for x in (old,removed,restored)})==3

@pytest.mark.parametrize("role,terminal,recipes",[("discovery","CHECKED",1),("utility","CHECKED",0),
    ("schema_environment","CHECKED",0),("answer_environment","CANNOT_CHECK",None),("semantics","CANNOT_CHECK",None)])
def test_revision_has_independent_warrants(tmp_path,role,terminal,recipes):
    rt,store,_=populated(tmp_path);b=bridge(store)
    eid=store.read(store.method_ids[0])["envelope"][role];rt.revoke([eid])
    out=b.solve(fresh());assert out["terminal"]==terminal
    if recipes is not None:assert out["packet"]["use"]["recipes_applied"]==recipes
    else:assert b.dispatches==0
    rt.reinstate([eid]);assert b.solve(fresh())["packet"]["use"]["recipes_applied"]==1
