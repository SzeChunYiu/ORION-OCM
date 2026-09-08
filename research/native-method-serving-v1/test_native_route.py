"""Actual OCM route with explicit computation/check doubles only."""
from dataclasses import replace
import pytest
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.kso.nogoods import NogoodSet
from native_contract import InputRefused,CONTEXT
from native_store import NativeStore
from native_runtime import NativeRuntime
from native_request import read_request
import native_data as D
from control_support import populated,RouteDouble,TASK,MID

def test_actual_registry_solve_commit_and_cold_use_replay(tmp_path):
    rt,store,runtime,engine=populated(tmp_path);out=runtime.solve(TASK,[MID])
    assert out["terminal"]=="CHECKED" and out["dispatches"]==out["checks"]==1
    assert engine.seen and engine.seen_checks and out["trace"]["stages"][-1]["stage"]=="COMMITMENT"
    assert rt.state.operators.operators[runtime.registry_key] is runtime.op
    assert runtime.op.checker==runtime._check and runtime.active is None and not store.pending
    assert len(store.uses)==1 and store.uses[0]["core_events"]
    cold_engine=RouteDouble();cold=NativeStore(OCMRuntime(rt.root),cold_engine)
    assert len(cold.uses)==1 and len(cold_engine.seen_checks)==1

@pytest.mark.parametrize("role",["proof","applicability"])
def test_method_revocation_falls_back_and_restores(tmp_path,role):
    rt,store,runtime,engine=populated(tmp_path);eid=store.records[MID][role]
    rt.revoke([eid]);out=runtime.solve(TASK,[MID]);assert out["terminal"]=="CHECKED" and engine.seen[-1]["eligible_ids"]==[]
    rt.reinstate([eid]);out=runtime.solve(TASK,[MID]);assert out["packet"]["selected_proof_method_ids"]==[MID]

@pytest.mark.parametrize("role",["source_environment","library_environment","checker_environment"])
def test_environment_revocation_refuses_before_dispatch(tmp_path,role):
    rt,store,runtime,engine=populated(tmp_path);eid=store.environment[role];rt.revoke([eid])
    assert runtime.solve(TASK,[MID])["terminal"]=="CANNOT_CHECK" and not engine.seen
    rt.reinstate([eid]);assert runtime.solve(TASK,[MID])["terminal"]=="CHECKED"

@pytest.mark.parametrize("location",["runtime","evidence"])
def test_cross_support_nogood_disables_method_only(tmp_path,location):
    rt,store,runtime,engine=populated(tmp_path)
    ng=NogoodSet.of({store.environment["checker_environment"],store.records[MID]["proof"]})
    if location=="runtime":rt.state.nogoods=ng
    else:rt.state.evidence.nogoods=ng
    out=runtime.solve(TASK,[MID]);assert out["terminal"]=="CHECKED" and engine.seen[-1]["eligible_ids"]==[]

@pytest.mark.parametrize("when",["before","during"])
def test_same_fingerprint_registry_replacement_refuses(tmp_path,when,monkeypatch):
    rt,store,runtime,engine=populated(tmp_path)
    replacement=replace(runtime.op,backend=lambda ks,inputs:{"forged":True})
    assert replacement.fingerprint==runtime.op.fingerprint
    if when=="before":
        rt.state.operators.operators[runtime.registry_key]=replacement
        with pytest.raises(InputRefused,match="REGISTERED_DISPATCHER_CHANGED"):runtime.solve(TASK,[MID])
        assert not engine.seen
    else:
        prior=engine.propose
        def changed(request):
            packet=prior(request);rt.state.operators.operators[runtime.registry_key]=replacement;return packet
        monkeypatch.setattr(engine,"propose",changed)
        assert runtime.solve(TASK,[MID])["terminal"]=="CANNOT_CHECK"
    assert runtime.active is None

@pytest.mark.parametrize("what",["request","packet","warrant"])
def test_changed_active_binding_refuses(tmp_path,what,monkeypatch):
    rt,store,runtime,engine=populated(tmp_path);prior=engine.propose
    def changed(request):
        packet=prior(request)
        if what=="request":
            qid=runtime.active["qid"];atom=rt.state.ks.atom_view[qid]
            bad=replace(atom,content_ref="0"*64)
            rt.state.ks=replace(rt.state.ks,atoms=tuple(bad if a.atom_id==qid else a for a in rt.state.ks.atoms))
        elif what=="packet":packet["normal_proof"]=["search-hyp-1"]
        else:rt.revoke([store.records[MID]["proof"]])
        return packet
    monkeypatch.setattr(engine,"propose",changed)
    # Invalid recorded request may make durable receipt validation fail closed.
    try:out=runtime.solve(TASK,[MID]);assert out["terminal"]=="CANNOT_CHECK"
    except InputRefused:assert store.pending
    assert runtime.active is None and not store.uses

def test_detached_request_context_and_library(tmp_path):
    engine=RouteDouble();bad=engine.request(TASK,[MID]);bad["context"]["ambient_dv"].append(["A","B"])
    bad["library"]["TEST_ONLY"]="changed"
    with pytest.raises(InputRefused,match="REQUEST_BINDING"):engine.validate_request(bad)
    clean=engine.request(TASK,[MID]);assert clean["context"]==CONTEXT and clean["context"]["ambient_dv"]==[]
    assert clean["library"]["TEST_ONLY"]=="NO_NATIVE_QUALIFICATION"

@pytest.mark.parametrize("what",["source","payload"])
def test_source_or_kso_payload_tamper(tmp_path,what,monkeypatch):
    rt,store,runtime,engine=populated(tmp_path)
    if what=="source":monkeypatch.setattr(D,"sources",lambda work=None:{"changed":"source"})
    else:
        mid="native:method:"+MID;atom=rt.state.ks.atom_view[mid];bad=replace(atom,content_ref="0"*64)
        rt.state.ks=replace(rt.state.ks,atoms=tuple(bad if a.atom_id==mid else a for a in rt.state.ks.atoms))
    with pytest.raises(InputRefused):runtime.solve(TASK,[MID])
    assert not engine.seen
