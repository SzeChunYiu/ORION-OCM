"""Prospective policy arithmetic and continuation controls, with explicit fake dispatch."""
import copy,time
from pathlib import Path
import pytest
from assay_test_support import authored_only
from unary_method_profile import observe
from unary_assay_controls import decide,overall,role_transition
from unary_assay_economics import horizon,break_even,evaluate
from unary_assay_phase import ARMS,Session
from unary_assay_schedule import expected,episode
from unary_assay_coordinator import authored_partitions
from test_unary_assay_coordinator import fixture

def use(row,key="r",*,presentation="ast",terminal="CHECKED"):
    return {"row_id":row,"presentation":presentation,"terminal":terminal,"use":{"recipes_applied":1,"rule_id":key}}

def verdict(**changes):
    values=dict(unavailable=False,selection="SELECTED",ocm_rows=[use("a"),use("b")],
        parent_rows=[use("a"),use("b")],knockout_rows=[],semantic_keys={"a":"x","b":"y"},selected=["r"])
    values.update(changes);return decide(**values)

def test_two_semantic_rows_same_rule_and_parent_sufficiency():
    d=verdict()
    assert d["terminal"]=="CHECKED_CAUSAL_REUSE_APPARATUS" and d["comparison"]=="PARENT_SUFFICIENT"
    assert overall([dict(episode=i,**d) for i in range(4)])["complete_count"]==4
    assert overall([d])["terminal"]=="CANNOT_CHECK"

@pytest.mark.parametrize("change",[
    {"ocm_rows":[use("a"),use("a",presentation="text")]},
    {"semantic_keys":{"a":"x","b":"x"}},
    {"ocm_rows":[use("a"),use("b",terminal="CANNOT_CHECK")]},
    {"ocm_rows":[use("a"),use("b","s")],"selected":["r","s"]}])
def test_repeated_presentation_alpha_equivalence_partial_and_different_rules_do_not_qualify(change):
    assert verdict(**change)["terminal"]=="NO_CAUSAL_USE"

@pytest.mark.parametrize("kw,want",[
    ({"selection":"NO_METHOD_ACQUIRED"},"NO_METHOD_ACQUIRED"),
    ({"selection":"NO_DEVELOPMENT_BENEFIT"},"NO_DEVELOPMENT_BENEFIT"),
    ({"selection":"NO_METHOD_ACQUIRED","unavailable":True},"CANNOT_CHECK"),
    ({"unavailable":True,"control_failure":True},"SEMANTIC_CONTROL_FAILED"),
    ({"knockout_rows":[use("a")]},"SEMANTIC_CONTROL_FAILED")])
def test_registered_precedence(kw,want):assert verdict(**kw)["terminal"]==want

@pytest.mark.parametrize("arm,dead",[("ADAPTIVE_PARENT","REVOKED"),("OCM_ENABLED","DEAD")])
def test_role_warrant_states_keep_unknown_distinct(arm,dead):
    f={"terminal":"CHECKED","rows":[],"methods":{"m":{"correctness":dead,"selection":"LIVE","eligible":False}}}
    role_transition(f,"schema_environment","withdrawn",arm,"m")
    f["methods"]["m"]["correctness"]="UNKNOWN"
    with pytest.raises(ValueError,match="ROLE_WARRANT_TRANSITION"):role_transition(f,"schema_environment","withdrawn",arm,"m")

def cost(arm,phase,total,rows=()):
    return {"slot":"e0--"+phase+"--"+arm,"arm":arm,"mode":"acquire_selected" if phase=="A" else "presented_batch",
      "launch_return_wall_s":float(total),"launch_return_own_cpu_s":0.0,
      "facts":{"terminal":"CHECKED","process":{"waited_child_user_s":float(total),"waited_child_system_s":0.0},
       "rows":[{"wall_s":float(x),"cpu_s":float(x),"sink_wall_s":0.0,"sink_cpu_s":0.0} for x in rows]}}

def test_endpoint_observation_never_invents_intermediate_crossing():
    left=horizon(cost("OCM_ENABLED","A",1),cost("OCM_ENABLED","B",8,[1,1]))
    right=horizon(None,cost("EXACT_PARENT","B",7,[3,3]))
    b=break_even(left,right,"wall_s")
    assert b["terminal"]=="ENDPOINT_NOT_BENEFICIAL" and b["earliest_crossing"]=="UNAVAILABLE"
    assert "not observed" in left["allocation"]
    assert break_even(right,left,"wall_s")["terminal"]=="OBSERVED_AT_HORIZON"

def test_knockout_acquisition_is_allocated_not_physically_double_counted():
    calls=[cost("ADAPTIVE_PARENT","A",3),cost("OCM_ENABLED","A",5)]
    calls += [cost(arm,"B",6,[1,1]) for arm in ARMS]
    d=evaluate(calls,physical=None)
    assert d["physical_call_totals"]["wall_s"]==32
    assert d["arms"]["OCM_KNOCKOUT"]["acquisition"]["wall_s"]==5
    assert d["arms"]["OCM_KNOCKOUT"]["A_allocation"]=="COUNTERFACTUAL_REUSE"
    assert d["terminal"]=="ECONOMICS_CANNOT_CHECK"
    calls[0]["launch_return_wall_s"]=None
    assert evaluate(calls,physical=None)["terminal"]=="ECONOMICS_CANNOT_CHECK"

@pytest.mark.parametrize("fail_phase,expected_phases",[("A",["A"]*2),("B",["A"]*2+["B"]*4),("C",["A"]*2+["B"]*4+["C"]*4)])
def test_operational_phase_continuation_has_zero_retry(tmp_path,monkeypatch,fail_phase,expected_phases):
    session=Session(tmp_path/"run",deadline=time.monotonic()+20,profile=observe());seen=[]
    def call(slot,arm,mode,request):
        phase=slot.split("--")[1];seen.append((phase,arm))
        if mode=="acquire_selected":
            Path(request["store"]).mkdir()
            facts={"terminal":"CHECKED","selection":{"terminal":"NO_METHOD_ACQUIRED",
                "pool_sha256":"p","ranking_sha256":"r","library_sha256":"l"},"selected_rule_ids":[]}
        else:
            facts={"terminal":"CHECKED","rows":[]}
            for i,row in enumerate(request["rows"]):
                facts["rows"].append({"index":i,"observation_id":row["observation_id"],"row_id":row["row_id"],
                    "presentation":row["presentation"],"task_sha256":row["task_sha256"],"status":"ENTAILED",
                    "use":{"recipes_applied":0,"cover":[]}})
        if phase==fail_phase and arm=="ADAPTIVE_PARENT":facts["terminal"]="CANNOT_CHECK"
        session.mark(slot,"ATTEMPTED",None);session.mark(slot,"COMPLETED" if facts["terminal"]=="CHECKED" else "UNAVAILABLE",None)
        return {"slot":slot,"request":request,"facts":facts}
    monkeypatch.setattr(session,"call",call)
    expected(session,0,2);g=authored_partitions(fixture(),0,{})
    out=episode(session,0,g,authored=True)
    assert [p for p,a in seen]==expected_phases and out["reason"]==fail_phase+"_INCOMPLETE"
    if fail_phase!="A":assert [a for p,a in seen if p=="B"]==list(ARMS)

@pytest.mark.parametrize("phase",["A","B","C"])
@pytest.mark.parametrize("failure",["inspect","signal","refused"])
def test_missing_child_facts_preserve_unavailable_cost(tmp_path,monkeypatch,phase,failure):
    import unary_assay_phase as p
    process={"terminal":"CANNOT_CHECK" if failure=="refused" else "COMPLETED",
             "returncode":-15 if failure=="signal" else (None if failure=="refused" else 0)}
    monkeypatch.setattr(p,"launch",lambda *a,**kw:process)
    def unavailable(*a,**kw):raise p.A.CustodyFailure("AUTHORED_"+failure.upper())
    monkeypatch.setattr(p.A,"inspect",unavailable)
    session=Session(tmp_path/"failed-call",deadline=time.monotonic()+20,profile=observe())
    slot="e0--"+phase+"--ADAPTIVE_PARENT"
    session.expect(slot,{"episode":0,"phase":phase,"arm":"ADAPTIVE_PARENT"})
    record=session.call(slot,"ADAPTIVE_PARENT","acquire_selected" if phase=="A" else "presented_batch",{})
    assert record["facts"] is None and session.slots[slot]["state"]=="UNAVAILABLE"
    calls=[cost(arm,"A",1) for arm in ("ADAPTIVE_PARENT","OCM_ENABLED")]
    calls += [cost(arm,"B",1,[.25]) for arm in ARMS]
    calls += [cost(arm,"C",1) for arm in ARMS]
    calls=[record if c["slot"]==slot else c for c in calls]
    result=evaluate(calls,physical=None)
    assert result["terminal"]=="ECONOMICS_CANNOT_CHECK"
    assert result["reason"]=="UNAVAILABLE_COST"
    assert "physical_call_totals" not in result
