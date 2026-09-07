"""Tampered proposals, current liveness, and durable use custody."""
from dataclasses import replace
import json
import pytest
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from unary_contract import InputRefused
from unary_method_store import MethodStore
from unary_method_check import check_packet
import unary_method_data as D
from test_unary_method_store import populated
from test_unary_method_runtime import bridge,fresh

@pytest.mark.parametrize("part",["task","certificate","rule","support","recipe"])
def test_independent_packet_binding_rejects_changes(tmp_path,part):
    rt,store,_=populated(tmp_path);b=bridge(store);receipt=b.solve(fresh())
    packet=D.parse(D.raw(receipt["packet"]));body=store.uses[-1]
    if part=="task":packet["task_sha256"]="0"*64
    elif part=="certificate":packet["result"]["status"]="UNKNOWN"
    elif part=="rule":packet["use"]["method_id"]="forged"
    elif part=="support":packet["use"]["cover"]=[1,2]
    else:packet["use"]["recipes_applied"]=False
    with pytest.raises(InputRefused):check_packet(store,body["qid"],body["request"],packet)
    assert check_packet(store,body["qid"],body["request"],receipt["packet"])

def test_returned_proposal_is_bound_to_actual_backend_packet(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path);b=bridge(store);old=b.op.backend
    def corrupt(ks,request):
        out=old(ks,request);out["execution"]["parent_completions"]=999;return out
    replacement=replace(b.op,backend=corrupt)
    rt.register_operator(replacement)
    with pytest.raises(InputRefused,match="REGISTERED_DISPATCHER_CHANGED"):b.solve(fresh())
    assert b.dispatches==0

def test_unknown_method_liveness_refuses_instead_of_fallback(tmp_path):
    rt,store,_=populated(tmp_path);mid=store.method_ids[0]
    a=rt.state.ks.atom_view[mid];bad=replace(a,warrant=WarrantProfile.partial(()))
    rt.state.ks=replace(rt.state.ks,atoms=tuple(bad if x.atom_id==mid else x for x in rt.state.ks.atoms))
    with pytest.raises(InputRefused,match="UNKNOWN_METHOD_WARRANT"):bridge(store).solve(fresh())

def test_unissued_exact_checker_atom_is_never_a_method(tmp_path):
    rt,store,_=populated(tmp_path);mid=store.method_ids[0];a=rt.state.ks.atom_view[mid]
    fake=replace(a,atom_id="forged",quarantined=True)
    rt.admit_object(fake,(),"EXACT_CHECKER")
    assert "forged" not in store.method_ids
    with pytest.raises(InputRefused,match="UNISSUED_METHOD"):store.read("forged")
    assert bridge(store).solve(fresh())["packet"]["use"]["method_id"]==mid

@pytest.mark.parametrize("part",["event","query","packet","commitment"])
def test_cold_use_journal_requires_actual_core_linkage(tmp_path,part):
    rt,store,_=populated(tmp_path);bridge(store).solve(fresh())
    body=D.parse(D.raw(store.uses[-1]))
    if part=="event":body["core_events"][-1]["hash"]="0"*64
    elif part=="query":body["qid"]="fake"
    elif part=="packet":body["receipt"]["packet"]["use"]["cover"]=[1,2]
    else:body["receipt"]["trace"]["stages"][-1]["status"]="FAIL"
    from unary_method_journal import validate_receipt
    with pytest.raises(InputRefused):validate_receipt(store,body,store.intents[store.uses[-1]["qid"]])
    store._append("USE",body)
    with pytest.raises(InputRefused):MethodStore(OCMRuntime(rt.root))

def test_cold_history_never_implicitly_solves_or_rebinds(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path);bridge(store).solve(fresh())
    rt.revoke([store.environment["schema_environment"]])
    monkeypatch.setattr(OCMRuntime,"solve",lambda *a,**k:pytest.fail("implicit solve"))
    cold=OCMRuntime(rt.root);restored=MethodStore(cold)
    assert len(restored.uses)==1 and not cold._host_operators
    assert restored.read(restored.method_ids[0])["correctness"]=="DEAD"

def test_unavailable_backend_is_retained_as_cannot_check(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path);b=bridge(store)
    import unary_method_runtime as M
    monkeypatch.setattr(M,"apply_rule",lambda *a: (_ for _ in ()).throw(InputRefused("AUTHORED_UNAVAILABLE")))
    out=b.solve(fresh())
    assert out["terminal"]=="CANNOT_CHECK" and out["backend_failure"]=="AUTHORED_UNAVAILABLE"
    assert out["packet"] is None and not store.uses

@pytest.mark.parametrize("bad",[b'{"x":1,"x":2}',b'{"x":NaN}',b'{ "x":1}',b'{}\n'])
def test_plain_canonical_data_refusals(bad):
    with pytest.raises(InputRefused):D.parse(bad)
    assert D.parse(b'{"x":1}')=={"x":1}

def test_string_comparison_hooks_never_run():
    class Hook(str):
        def __eq__(self,other):pytest.fail("comparison hook ran")
    with pytest.raises(InputRefused):D.raw({"schema":Hook("anything")})
