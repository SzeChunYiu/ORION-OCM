"""Actual selection/use revalidation counts and explicit internal accumulation."""
import pytest
from unary_contract import InputRefused
from unary_verify import verify_result
import unary_method_selection_check as C
import unary_method_verify_use as V
from unary_method_selection import validate_receipt
from unary_parent_store import ParentStore
from unary_parent_runtime import ParentRuntime
from test_unary_parent_selection import selected
from test_unary_parent_runtime import populated
from test_unary_method_runtime import fresh


def rule_nodes(rule):
    def expr(e):
        return 1 + sum(expr(x) for x in e[1:] if type(x) is list)
    return sum(expr(s[k]) for s in [*rule["premises"],rule["conclusion"]] for k in ("left","right"))


@pytest.mark.parametrize("api",["verify_use","verify_answer","validate_receipt"])
@pytest.mark.parametrize("supplied",[False,True])
def test_internal_verifiers_require_actual_accumulator(api,supplied):
    f=getattr(C if api=="validate_receipt" else V,api,None)
    assert f is not None,"missing counted answer boundary"
    args=({},) if api=="validate_receipt" else ({},{}) if api=="verify_answer" else ({},{},lambda _:None)
    kwargs={"counter":"authored_answer_checks"} if api=="verify_answer" else {}
    if supplied:kwargs["work"]=None
    with pytest.raises(TypeError,match="work"):f(*args,**kwargs)


def test_selection_revalidation_counts_each_actual_binding_traversal():
    r=selected();rules={x["rule_id"]:x for x in r["selected"]}
    expected=sum(rule_nodes(rules[row["rule_id"]]) for row in r["trials"] if row["application"]["terminal"]=="PROPOSED")
    assert expected>0
    work={"binding_expression_nodes":7}
    for run in (1,2):
        assert validate_receipt(r,work=work)["selected"]==r["selected"]
        assert work["binding_expression_nodes"]==7+run*expected


def test_cold_use_revalidation_counts_real_work_on_each_restore(tmp_path,monkeypatch):
    store=populated(tmp_path);before=ParentStore(store.root)
    baseline=before.work.get("binding_expression_nodes",0)
    result=ParentRuntime(store).solve(fresh())
    assert result["terminal"]=="CHECKED" and result["packet"]["use"]["recipes_applied"]==1
    expected=rule_nodes(store.read(result["packet"]["use"]["method_id"])["envelope"]["rule"])
    def forbidden(*a,**k):pytest.fail("cold replay redispatched acquisition/query completion")
    monkeypatch.setattr("unary_method_selection.acquire_selected",forbidden)
    monkeypatch.setattr("unary_solver.RegionSolver.complete",forbidden)
    for _ in range(2):
        cold=ParentStore(store.root)
        assert len(cold.uses)==1
        assert cold.work.get("use_answer_revalidations",0)==1
        assert cold.work["binding_expression_nodes"]==baseline+expected


def test_counted_answer_keeps_clean_and_failed_calls():
    r=selected()["baseline"][0];work={}
    checker=getattr(V,"verify_answer",None)
    assert checker is not None,"missing counted answer boundary"
    assert checker(r["task"],r["result"],work=work,counter="authored_answer_checks")
    assert not checker(r["task"],{},work=work,counter="authored_answer_checks")
    assert work=={"authored_answer_checks":2}
