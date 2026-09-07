"""A core commitment cannot silently disappear from the separate use journal."""
import pytest
from ocm.runtime.ocm_runtime import OCMRuntime
from unary_contract import InputRefused
from unary_method_store import MethodStore
from test_unary_method_store import populated
from test_unary_method_runtime import bridge,fresh

def test_committed_core_missing_use_refuses_cold_restore(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path);b=bridge(store);append=store._append
    def stop(kind,body):
        if kind=="USE":raise OSError("authored interruption before USE append")
        return append(kind,body)
    monkeypatch.setattr(store,"_append",stop)
    with pytest.raises(OSError,match="authored interruption"):b.solve(fresh())
    assert rt.events[-1].event_type.value=="CHECKER_RESULT" and rt.events[-1].status.value=="PASS"
    with pytest.raises(InputRefused,match="INCOMPLETE_USE"):MethodStore(OCMRuntime(rt.root))

def test_successful_use_finishes_intent_and_counts_outer_return(tmp_path):
    rt,store,_=populated(tmp_path);receipt=bridge(store).solve(fresh())
    observed=receipt["return_observation"]
    assert observed["total_wall_s"]>=receipt["solve_wall_s"]+observed["journal_wall_s"]
    assert observed["journal_wall_s"]>0 and "return_observation" not in store.uses[-1]["receipt"]
    cold=MethodStore(OCMRuntime(rt.root))
    assert len(cold.uses)==len(cold.attempts)==1

def test_refused_native_callback_has_a_completed_attempt(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path)
    import unary_method_runtime as M
    def unavailable(*a):raise InputRefused("AUTHORED_UNAVAILABLE")
    monkeypatch.setattr(M,"apply_rule",unavailable)
    result=bridge(store).solve(fresh())
    assert result["terminal"]=="CANNOT_CHECK"
    cold=MethodStore(OCMRuntime(rt.root))
    assert not cold.uses and len(cold.attempts)==1
    assert cold.attempts[0]["receipt"]["backend_failure"]=="AUTHORED_UNAVAILABLE"


def test_refusal_keeps_preparation_and_attempted_matching_work(tmp_path,monkeypatch):
    rt,store,_=populated(tmp_path)
    import unary_method_runtime as M
    def unavailable(*a):raise InputRefused("AUTHORED_UNAVAILABLE")
    monkeypatch.setattr(M,"apply_rule",unavailable)
    result=bridge(store).solve(fresh());work=result["execution_observation"]
    assert work is not None
    assert work["preparations"]==1 and work["candidate_attempts"]==store.method_ids
    assert work["index"]["index_probes"]==1 and work["parent_semantic_total"]["constraints_checked"]>0
    assert work["matching"][-1]["counters"] is None
    assert work["matching"][-1]["terminal"]=="PARTIAL_WORK_UNAVAILABLE"
