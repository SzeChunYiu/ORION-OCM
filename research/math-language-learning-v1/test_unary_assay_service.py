"""Authored presented calls; never draw registered study rows."""
import copy,importlib,importlib.util,time
import pytest
from unary_contract import InputRefused,task_digest
from unary_language import realize
from unary_verify import verify_result
from test_unary_method_runtime import fresh
from assay_test_support import authored_only,chain

def api(name):
    assert importlib.util.find_spec(name),"missing "+name
    return importlib.import_module(name)

def rows(task=None):
    t=fresh() if task is None else task
    return [{"observation_id":"text-first","row_id":"authored/non-numeric","presentation":"text",
             "payload":realize(t),"task_sha256":task_digest(t)},
            {"observation_id":"ast-second","row_id":"authored/non-numeric","presentation":"ast",
             "payload":t,"task_sha256":task_digest(t)}]

def run(value,runtime=None,observation=None):
    s=api("unary_assay_service")
    rt=api("unary_assay_exact").ExactRuntime() if runtime is None else runtime
    return s.run(rt,value,deadline=time.monotonic()+30,observation=observation)

def test_text_first_warm_exact_and_reset_aware_totals():
    out=run(rows())
    assert out["terminal"]=="CHECKED" and out["unreached_rows"]==[]
    a,b=out["rows"]
    assert a["parse"]["parse_calls"]==1 and b["parse"]["ast_validation_calls"]==1
    assert a["parse"]["task_sha256"]==b["parse"]["task_sha256"]==task_digest(fresh())
    assert not a["result"]["execution_observation"]["engine_cache_reused"]
    assert b["result"]["execution_observation"]["engine_cache_reused"]
    assert a["call_totals"]["semantic"]["cache_misses"]>0
    assert b["call_totals"]["semantic"]["cache_misses"]==0
    assert b["call_totals"]["semantic"]["cache_key_nodes"]>0
    for group in ("semantic","binding"):
        assert out["totals"][group]=={k:a["call_totals"][group][k]+b["call_totals"][group][k]
                                      for k in a["call_totals"][group]}
    assert out["totals"]["preparations"]==out["totals"]["parent_completions"]==2
    assert all(verify_result(fresh(),r["result"]["packet"]["result"]) for r in out["rows"])

@pytest.mark.parametrize("fault,reason",[("text","TRAILING_INPUT"),("digest","PRESENTED_TASK_DIGEST"),
    ("ast","UNUSED_PREDICATE_REGISTRY_ENTRY")])
def test_middle_input_refusal_preserves_unreached_and_no_old_engine_totals(fault,reason):
    value=rows();value.append({**copy.deepcopy(value[0]),"observation_id":"never"})
    value[1]["presentation"]="text";value[1]["payload"]=realize(fresh())
    if fault=="text":value[1]["payload"]+=" extra"
    elif fault=="digest":value[1]["task_sha256"]="0"*64
    else:
        value[1]["presentation"]="ast";value[1]["payload"]=chain()
        value[1]["payload"]["predicates"].append("Z")
    out=run(value)
    assert out["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[2]
    bad=out["rows"][1]
    assert reason in bad["reason"] and bad["result"] is None
    assert bad["call_totals"]["semantic"] is None and bad["call_totals"]["binding"] is None
    assert out["totals"]["semantic"]==out["rows"][0]["call_totals"]["semantic"]

@pytest.mark.parametrize("change",[lambda r:r[1].update(observation_id=r[0]["observation_id"]),
    lambda r:r[0].update(observation_id=True),lambda r:r[0].update(row_id=""),
    lambda r:r[0].update(presentation="code"),lambda r:r[0].update(task_sha256="z"*64),
    lambda r:r[0].update(extra="unbound")])
def test_invalid_metadata_refuses_before_any_solver_call(change):
    value=rows();change(value)
    class Never:
        def solve(self,*a,**k):pytest.fail("dispatched malformed metadata")
    with pytest.raises(InputRefused):run(value,Never())

def test_call_failure_retains_known_partial_execution_and_does_not_retry():
    class Failed:
        def solve(self,*a,**k):
            self.last_observation={"execution_observation":{"preparation_attempts":1,
                "preparations":1,"parent_completions":0,"parent_semantic_total":{"cache_key_nodes":7},
                "prepared_binding_total":{"bytes_hashed":9},"stage":"AUTHORED_FAILURE","matching":[]}}
            raise OSError("authored backend failure")
    out=run(rows(),Failed())
    assert out["unreached_rows"]==[1] and out["rows"][0]["call_totals"]["semantic"]=={"cache_key_nodes":7}
    assert out["totals"]["partial_calls"]==1 and "backend failure" in out["rows"][0]["reason"]

def test_deadline_before_first_row_preserves_all_original_slots():
    s=api("unary_assay_service");e=api("unary_assay_exact").ExactRuntime()
    out=s.run(e,rows(),deadline=time.monotonic()-1)
    assert out["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[0,1] and out["rows"]==[]
    assert e.engines.engines=={}

def test_known_answer_checker_failure_counts_attempt(monkeypatch):
    e=api("unary_assay_exact")
    monkeypatch.setattr(e,"verify_answer",lambda *a,work,counter:work.update({counter:1}) or False)
    out=run(rows(),e.ExactRuntime())
    assert out["rows"][0]["result"]["check"]["work"]["independent_answer_checks"]==1
    assert out["rows"][0]["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[1]


@pytest.mark.parametrize("late",[False,True])
def test_expiry_after_real_completion_retains_mathematical_result(monkeypatch,late):
    s=api("unary_assay_service");original=s.remaining;calls=0
    def limit(deadline):
        nonlocal calls
        calls+=1
        if late and calls==3:raise InputRefused("DEADLINE_EXPIRED")
        return original(deadline)
    monkeypatch.setattr(s,"remaining",limit)
    out=run(rows())
    first=out["rows"][0]
    assert first["result"]["terminal"]=="CHECKED"
    assert first["call_totals"]["semantic"]["cache_key_nodes"]>0
    if late:assert first["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[1]
    else:assert out["terminal"]=="CHECKED"

def test_post_solve_observation_failure_keeps_result_and_unreached(monkeypatch):
    s=api("unary_assay_service")
    def fail(*a):raise OSError("authored observation failure")
    monkeypatch.setattr(s.O,"aggregate",fail)
    out=run(rows())
    assert out["rows"][0]["result"]["terminal"]=="CHECKED"
    assert "observation failure" in out["rows"][0]["observation_error"]
    assert out["unreached_rows"]==[1] and out["totals_complete"] is False

def test_actual_issuer_write_failure_preserves_core_work_and_stops(tmp_path,monkeypatch):
    from test_unary_method_store import populated
    from unary_method_runtime import MethodRuntime
    rt,store,_=populated(tmp_path/"store");bridge=MethodRuntime(store)
    append=store.journal.append
    def fail(kind,*a,**k):
        if kind=="USE":raise OSError("authored USE write failure")
        return append(kind,*a,**k)
    monkeypatch.setattr(store.journal,"append",fail)
    out=run(rows(),bridge)
    first=out["rows"][0]
    assert first["terminal"]=="CANNOT_CHECK" and "USE write failure" in first["reason"]
    assert first["partial_observation"]["terminal"]=="CHECKED"
    assert first["call_totals"]["dispatches"]==first["call_totals"]["checks"]==1
    assert first["call_totals"]["semantic"]["cache_key_nodes"]>0
    assert out["unreached_rows"]==[1]

def test_actual_partial_match_refusal_keeps_known_work(tmp_path,monkeypatch):
    from test_unary_method_store import populated
    import unary_method_runtime as m
    rt,store,_=populated(tmp_path/"store")
    def fail(*a):raise InputRefused("AUTHORED_MATCH_UNAVAILABLE")
    monkeypatch.setattr(m,"apply_rule",fail)
    out=run(rows(),m.MethodRuntime(store));first=out["rows"][0]
    assert first["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[1]
    assert first["call_totals"]["partial_matching_attempts"]==1
    assert first["call_totals"]["matching"]=={}
    assert first["call_totals"]["semantic"]["cache_key_nodes"]>0
    assert first["result"]["execution_observation"]["matching"][0]["counters"] is None


def test_unclassified_store_metric_is_retained_before_aggregation():
    e=api("unary_assay_exact")
    class Store:work={"known":0,"authored_unclassified":0}
    class Runtime(e.ExactRuntime):
        store=Store()
        def solve(self,*a,**k):
            out=super().solve(*a,**k);self.store.work["authored_unclassified"]=.5
            return out
    out=run(rows(),Runtime());row=out["rows"][0]
    assert row["result"]["terminal"]=="CHECKED"
    assert row["store_work_before"]["authored_unclassified"]==0
    assert row["store_work_after"]["authored_unclassified"]==.5
    assert row["store_work_delta"]["authored_unclassified"]==.5
    assert "INVALID_STORE_OBSERVATION" in row["observation_error"]
    assert out["totals_complete"] is False and out["unreached_rows"]==[1]
