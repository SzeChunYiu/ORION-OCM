"""Resealed data and cache-boundary falsifiers, not merely digest mismatch tests."""
import copy
import pytest
from unary_contract import InputRefused
import unary_method_plain as D
import unary_parent_sources as S
from unary_method_selection import validate_receipt
from test_unary_parent_selection import selected
from test_unary_parent_runtime import populated
from unary_parent_runtime import ParentRuntime
from test_unary_method_runtime import fresh

def reseal(r):
    r.pop("receipt_sha256");r["receipt_sha256"]=D.hashed(r);return r

@pytest.mark.parametrize("change,reason",[("support","SELECTION_SUPPORT_SEMANTICS"),("task","SELECTION_SUPPORT_TASK"),
    ("cover","SELECTION_SUPPORT_COVER"),("certificate","SELECTION_RULE_CERTIFICATE"),("query_delta","SELECTION_QUERY_DELTA"),
    ("ranking","SELECTION_DECISION"),("selected","SELECTION_DECISION")])
def test_resealed_receipt_reaches_actual_validation(change,reason):
    r=selected()
    if change=="support":r["acquisition"]["rules"][0]["supports"][0]["semantic_key"]="0"*64
    elif change=="task":r["acquisition"]["rules"][0]["supports"][0]["task_sha256"]="0"*64
    elif change=="cover":r["acquisition"]["rules"][0]["supports"][0]["cover"]=[0,0]
    elif change=="certificate":r["acquisition"]["rules"][0]["schema_certificate"]["truth_table"][0]=False
    elif change=="query_delta":r["trials"][0]["observation"]["query_constraints"]+=1
    elif change=="ranking":r["ranking"][0]["benefit"]+=1
    else:r["selected"]=[]
    with pytest.raises(InputRefused,match=reason):validate_receipt(reseal(r))

def test_schema_mathematics_exact_while_prior_zero_counter_keys_are_retained():
    r=selected();cert=r["acquisition"]["rules"][0]["schema_certificate"]
    cert["counters"]["authored_preexisting_counter"]=0
    assert validate_receipt(reseal(r))["selected"]
    cert=r["acquisition"]["rules"][0]["schema_certificate"]
    cert["counters"]["authored_preexisting_counter"]=-1
    with pytest.raises(InputRefused,match="SELECTION_COUNTER"):validate_receipt(reseal(r))

def test_conventional_source_closure_and_decoded_reads(tmp_path,monkeypatch):
    p=populated(tmp_path);paths=p.source_map
    assert "src/ocm/store/ledger.py" in paths and "src/ocm/store/canonical.py" in paths
    assert not any(k.startswith("src/orion_v2/") or k.startswith("src/ocm/runtime/") for k in paths)
    assert not any("plan-CORE.md" in k for k in paths)
    assert any(k.endswith("unary_parent_sources.py") for k in paths)
    def no_json(*a):pytest.fail("cached method read reparsed JSON")
    monkeypatch.setattr(D,"parse",no_json)
    a=p.read(p.method_ids[0]);a["envelope"]["rule"]["parameters"][0]="changed"
    b=p.read(p.method_ids[0])
    assert b["envelope"]["rule"]["parameters"][0]!="changed"

def test_own_source_change_refuses_before_direct_dispatch(tmp_path,monkeypatch):
    p=populated(tmp_path);original=S.sources
    def changed(work=None):return {**original(work),"changed-owned-helper":"0"*64}
    monkeypatch.setattr(S,"sources",changed)
    b=ParentRuntime(p)
    with pytest.raises(InputRefused,match="PARENT_SOURCE"):b.solve(fresh())
    assert b.dispatches==0

def test_unknown_rule_is_never_live_and_answer_unknown_is_distinct(tmp_path):
    p=populated(tmp_path);mid=p.method_ids[0];p.revise("utility","UNKNOWN",mid=mid)
    r=ParentRuntime(p).solve(fresh())
    assert r["terminal"]=="CHECKED" and r["packet"]["use"]["recipes_applied"]==0
    p.revise("answer_environment","UNKNOWN")
    r=ParentRuntime(p).solve(fresh())
    assert r["terminal"]=="CANNOT_CHECK" and r["packet"] is None and r["dispatches"]==0
