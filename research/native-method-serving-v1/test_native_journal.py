"""Retained-use custody and interrupted-write controls, never native evidence."""
import copy
import pytest
from ocm.runtime.ocm_runtime import OCMRuntime
from native_contract import InputRefused
from native_store import NativeStore
from native_journal import validate_receipt
from control_support import populated,RouteDouble,TASK,MID

@pytest.mark.parametrize("point",["intent_after_append","outcome_after_append"])
def test_uncertain_durable_write_refuses_same_process_and_restart(tmp_path,monkeypatch,point):
    rt,store,runtime,engine=populated(tmp_path);prior=store._append
    def interrupted(kind,body):
        result=prior(kind,body)
        if (point=="intent_after_append" and kind=="USE_PREPARE") or (point=="outcome_after_append" and kind=="USE"):
            raise OSError("injected after durable append")
        return result
    monkeypatch.setattr(store,"_append",interrupted)
    with pytest.raises(OSError):runtime.solve(TASK,[MID])
    assert runtime.active is None and store.pending
    before=len(engine.seen)
    with pytest.raises(InputRefused,match="INCOMPLETE_USE"):runtime.solve(TASK,[MID])
    assert len(engine.seen)==before
    if point=="intent_after_append":
        with pytest.raises(InputRefused,match="INCOMPLETE_USE"):NativeStore(OCMRuntime(rt.root),RouteDouble())
    else:
        # Outcome is durable and can recover only by full verified replay.
        restored=RouteDouble();cold=NativeStore(OCMRuntime(rt.root),restored)
        assert len(cold.uses)==1 and len(restored.seen_checks)==1

@pytest.mark.parametrize("what",["request_sha256","database","trace_sha256","core_hash","packet"])
def test_saved_checker_and_core_custody_are_bound(tmp_path,what):
    rt,store,runtime,engine=populated(tmp_path);runtime.solve(TASK,[MID])
    body=copy.deepcopy(store.uses[0]);intent=store.intents[body["qid"]]
    if what=="request_sha256":body["receipt"]["check"][what]="0"*64
    elif what in ("database","trace_sha256"):body["receipt"]["check"]["native"][what]="changed"
    elif what=="core_hash":body["core_events"][0]["hash"]="0"*64
    else:body["receipt"]["packet"]["normal_proof"]=["forged"]
    with pytest.raises(InputRefused):validate_receipt(store,body,intent,replay=True)

def test_checker_failure_clears_active_and_records_refusal(tmp_path,monkeypatch):
    rt,store,runtime,engine=populated(tmp_path)
    def fail(request,packet):raise RuntimeError("checker interrupted")
    monkeypatch.setattr(engine,"check",fail)
    out=runtime.solve(TASK,[MID])
    assert out["terminal"]=="CANNOT_CHECK" and runtime.active is None and not store.pending and len(store.attempts)==1
