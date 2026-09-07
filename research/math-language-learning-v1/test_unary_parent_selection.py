"""Authored real mining/development selection; no scientific task generator."""
import importlib,importlib.util
import pytest
from learning_test_support import training
from test_unary_method_runtime import fresh
from unary_contract import InputRefused
def selection():
    assert importlib.util.find_spec("unary_method_selection"),"missing real development selector"
    return importlib.import_module("unary_method_selection")
def selected():
    m=selection();return m.acquire_selected([training("B")["task"],training("C")["task"]],[fresh()],m.contract(2,1,authored=True))
def test_actual_mining_ranking_and_positive_library():
    r=selected();assert r["terminal"]=="SELECTED" and r["selected"]
    assert all(len(x["rule"]["premises"])==2 for x in r["acquisition"]["rules"])
    assert len(r["training"])==2 and r["ranking"][0]["benefit"]>0
    assert r["training"][1]["observation"]["engine_cache_reused"]
    assert all(x["observation"]["engine_cache_reused"] is False for x in r["baseline"])
    assert r["selected"]==sorted(r["selected"],key=lambda x:x["rule_id"])
    selection().validate_receipt(r)
def test_no_development_benefit_is_real_empty_library():
    m=selection();t=training("B")["task"]
    r=m.acquire_selected([t,training("C")["task"]],[{"schema":t["schema"],"predicates":["A","B"],"premises":[],"query":{"kind":"some","left":["pred","A"],"right":["pred","B"]}}],m.contract(2,1,authored=True))
    assert r["terminal"]=="NO_DEVELOPMENT_BENEFIT" and not r["selected"]
@pytest.mark.parametrize("change",["selected","ranking","source","policy"])
def test_selection_tamper_refuses(change):
    r=selected()
    if change=="selected":r["selected"]=[]
    elif change=="ranking":r["ranking"][0]["benefit"]+=1
    elif change=="source":r["sources_sha256"]="0"*64
    else:r["contract"]["schema"]="authored-selected.v1"
    with pytest.raises(InputRefused):selection().validate_receipt(r)
def test_missing_training_is_not_successful_subset():
    m=selection()
    with pytest.raises(InputRefused,match="SELECTION_COUNTS"):
        m.acquire_selected([training("B")["task"]],[fresh()],m.contract(2,1,authored=True))
def test_trial_error_preserves_reached_work(monkeypatch):
    m=selection();observed={}
    monkeypatch.setattr(m,"apply_rule",lambda *a:(_ for _ in ()).throw(RuntimeError("authored matcher failure")))
    with pytest.raises(RuntimeError):
        m.acquire_selected([training("B")["task"],training("C")["task"]],[fresh()],m.contract(2,1,authored=True),observation=observed)
    assert observed["stage"]=="DEVELOPMENT_CANDIDATE"
    assert observed["trials"][-1]["observation"]["prepared_binding_total"]["bytes_hashed"]>0
    assert observed["trials"][-1]["terminal"]=="CANNOT_CHECK"
