"""Prepared consistency is immutable/bound and contains no completed query result."""
from dataclasses import FrozenInstanceError,replace
from copy import deepcopy
import pytest
from unary_test_support import api,statement as s,task


def engine(value):
    x=api("unary_solver").RegionSolver(value["predicates"])
    assert hasattr(x,"prepare") and hasattr(x,"complete"),"prepared exact parent missing"
    return x


def test_prepare_contains_only_premise_work_and_reuses_aggregate(monkeypatch):
    value=task([s("every","A","A")],s("some","B","B"));x=engine(value)
    prepared=x.prepare(value)
    assert not any("B" in repr(k) for k in x.cache)
    assert prepared.base[0]=="model" and not hasattr(prepared,"query_true")
    with pytest.raises(FrozenInstanceError):prepared.allowed=0
    def forbidden(*a):raise AssertionError("premises must not be aggregated again")
    monkeypatch.setattr(x,"_aggregate",forbidden)
    result=x.complete(prepared)
    assert result["status"]=="UNKNOWN" and api("unary_verify").verify_result(value,result)
    assert result["counters"]["constraints_checked"]==2
    assert x.counters["constraints_checked"]==len(value["premises"])+2


@pytest.mark.parametrize("change",["copy","other_engine","stale","mutation","task"])
def test_prepared_reuse_refuses_wrong_binding(change):
    c=api("unary_contract");value=task([s("every")],s("some"));x=engine(value);p=x.prepare(value)
    if change=="copy":p=replace(p)
    elif change=="other_engine":x=engine(value)
    elif change=="stale":x.prepare(value)
    elif change=="mutation":object.__setattr__(p,"allowed",0)
    else:
        value=deepcopy(value);value["query"]["kind"]="no"
    with pytest.raises(c.InputRefused):x.inspect_prepared(p,value)


@pytest.mark.parametrize("premises",[[],[s("every")],[s("some"),s("no")],
                                      [s("some","A","B"),s("some","A",["not",["pred","B"]])]])
def test_prepared_complete_preserves_certificates(premises):
    value=task(premises,s("some"));x=engine(value);p=x.prepare(value)
    first=x.complete(p);again=x.complete(p)
    assert first["status"]==again["status"]
    assert api("unary_verify").verify_result(value,first)
    assert api("unary_verify").verify_result(value,again)
    assert x.binding_work["bytes_hashed"]>0

@pytest.mark.parametrize("field,value",[("allowed",b"hidden"),("task_bytes",b"\xff")])
def test_corrupted_prepared_bytes_refuse_as_input(field,value):
    t=task([s("every","A","B")],s("some","A","B"))
    e=engine(t);p=e.prepare(t)
    object.__setattr__(p,field,value)
    with pytest.raises(api("unary_contract").InputRefused):e.inspect_prepared(p)
