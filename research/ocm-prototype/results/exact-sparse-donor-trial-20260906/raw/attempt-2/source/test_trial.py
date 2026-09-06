"""Synthetic non-actor controls only. No G1 loader, SV, model or donor is executed."""
import copy
import json
import os
from pathlib import Path
import sys
import pytest
from trial_common import digest, write
from trial_capture import run_process
from trial_grade import adjudicate, check_process, semantic_call

def synthetic(arm="reference"):
    ids=["synthetic-a","synthetic-b"]; catalog=["syntax:udpipe1","procedure:cvc5","apply:max","apply:guard"]
    request={"kind":"clia_apply","program_id":"max","arguments":[-28,7,24]}
    state={"N":2,"edges":1,"kso_state_hash":"SYNTHETIC","registry_revision":"R","evidence_epoch":"E","ks_digest":"K","revoked":[]}
    expected={"state":state,"ids":ids,"alpha":"1/3","query_seed":["1/1","0/1"],"uniform_seed":["1/2","1/2"],
              "request":request,"program_sha256":"P","catalogue":catalog,"descriptor_ids":["max","guard"]}
    answer={"status":"APPLIED","program_id":"max","program_sha256":"P","arguments":[-28,7,24],"value":24,"application_wall_s":.01}
    vectors=[{"mode":mode,"alpha":"1/3","revoked":[],"seed":expected["query_seed" if i<2 else "uniform_seed"],"values":dict.fromkeys(ids,"1/2")}
             for i,mode in enumerate(("WARRANTED","EXPLORATORY","WARRANTED","EXPLORATORY"))]
    check={"route":"CURRENT_FRACTION_REFERENCE","donor_solve_calls":0,"independent_residual":"ORIGINAL_BEHAVIOR_NO_ADDED_CHECK"}
    if arm=="sympy": check={"route":"SYMPY_QQ_RREF","donor_solve_calls":1,"independent_residual":"EXACT_ZERO","checker_dense_cells":4,
                           "full_output_entries":2,"candidate_assembly":"DIRECT_SPARSE","donor_method":"DomainMatrix.solve_den(method='rref')"}
    result={"arm":arm,"consumer":{"status":"COMPLETED","decision":"ANSWER","committed":True,"answer":answer,"trace":{"fixture":"SYNTHETIC"}},
            "vectors":vectors,"logical_fixed_point_calls":4,"checks":[copy.deepcopy(check) for _ in range(4)],"surprise":[],"stage_counts":{}}
    app=[]
    for op in catalog:
        c={"operator":op,"phase":"solve","status":"FAIL","reason":"NOT_APPLICABLE"}
        if op=="apply:max": c.update(status="PASS",reason="POINTWISE_VALUE_MATCH",value=24,arguments=[-28,7,24],check_wall_s=.02)
        app.append(c)
    assignment={"index":0,"pair":0,"arm":arm}
    payload={"index":0,"assignment":assignment,"state_before":state,"state_after":state,"result":result,"application_checks":app,
             "counter_delta":{"catalogue_visits":catalog,"application_calls":1,"pointwise_checks":1,"synthesis_dispatches":0},
             "invocations":[{"index":0,"action":"application","payload_sha256":digest(request),"result":answer,"started_monotonic":0,"finished_monotonic":1}]}
    return payload,expected

def test_synthetic_no_alarm_and_named_duration_exclusion(tmp_path):
    p,e=synthetic(); original=semantic_call(p,e,"reference")
    write(tmp_path/"SYNTHETIC-no-alarm.json",p)
    p["result"]["consumer"]["answer"]["application_wall_s"]=.9
    p["application_checks"][2]["check_wall_s"]=.8
    assert semantic_call(p,e,"reference")==original
    p["application_checks"][0]["check_wall_s"]=.3
    assert semantic_call(p,e,"reference")!=original
    p["result"]["consumer"]["trace"]["check_wall_s"]=.4
    assert semantic_call(p,e,"reference")!=original

@pytest.mark.parametrize("change",["value","vector","state","missing_check","synthesis","event","float_argument"])
def test_synthetic_changes_are_not_silently_accepted(change):
    p,e=synthetic("sympy"); before=semantic_call(p,e,"sympy")
    if change=="value": p["result"]["consumer"]["answer"]["value"]=25
    if change=="vector": p["result"]["vectors"][0]["values"]["synthetic-a"]="3/4"
    if change=="state": p["state_after"]=dict(p["state_after"],kso_state_hash="BAD")
    if change=="missing_check": p["result"]["checks"].pop()
    if change=="synthesis": p["counter_delta"]["synthesis_dispatches"]=1
    if change=="event": p["invocations"][0]["payload_sha256"]="BAD"
    if change=="float_argument": p["result"]["consumer"]["answer"]["arguments"]=[-28.0,7,24]
    try: after=semantic_call(p,e,"sympy")
    except ValueError: return
    assert after!=before

def paired():
    assignments=[]; observations={}
    for pair in range(7):
        for arm in (("reference","sympy") if pair%2==0 else ("sympy","reference")):
            i=len(assignments); assignments.append({"index":i,"pair":pair,"arm":arm})
            observations[i]={"semantic":"SYNTHETIC","bindings":"SYNTHETIC","warm_ns":100 if arm=="reference" else 80,
                             "cold_ns":1000 if arm=="reference" else 990,"pid":100+i}
    return observations,assignments

def test_synthetic_fixed_pair_gate_and_missing_arm():
    values,assignments=paired()
    result=adjudicate(values,assignments,[])
    assert result["component_gate"]=="ADOPTION_CANDIDATE" and result["warm_median_ratio"]==.8
    values.pop(13)
    assert adjudicate(values,assignments,[])["functional_terminal"]=="CANNOT_CHECK"

def test_synthetic_mismatch_and_failed_cost_gate():
    values,assignments=paired(); values[1]["semantic"]="WRONG"
    assert adjudicate(values,assignments,[])["functional_terminal"]=="REFINE_REQUIRED"
    values,assignments=paired()
    for a in assignments:
        if a["arm"]=="sympy": values[a["index"]]["cold_ns"]=1000
    assert adjudicate(values,assignments,[])["component_gate"]=="WARM_GAIN_ONLY_COLD_COST_UNRESOLVED"
    assert adjudicate(values,assignments,[{"reason":"TIMEOUT"}])["functional_terminal"]=="CANNOT_CHECK"

def test_synthetic_process_success_and_error_are_preserved(tmp_path):
    for name,code in (("success",0),("error",3)):
        out=tmp_path/name; out.mkdir()
        argv=[sys.executable,"-c",f"import json; print(json.dumps({{'fixture':'SYNTHETIC'}})); raise SystemExit({code})"]
        result=run_process(argv,out,seconds=2,cpu=None,address_bytes=None)
        assert result["exit_code"]==code and result["pid_absent"] and not result["timed_out"]
        assert result["wait4_raw"]["ru_utime"]>=0
        assert result["complete_tree_cpu_verified"] is False

def test_synthetic_timeout_terminates_process_group(tmp_path):
    out=tmp_path/"timeout";out.mkdir()
    child="import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)"
    parent="import subprocess,sys,time; p=subprocess.Popen([sys.executable,'-c',"+repr(child)+"]); print(p.pid,flush=True); time.sleep(30)"
    result=run_process([sys.executable,"-c",parent],out,seconds=.15,cpu=None,address_bytes=None)
    assert result["timed_out"] and result["pid_absent"] and result["exit_code"]!=0
    pid=int((out/"stdout").read_text().strip())
    stat=Path("/proc",str(pid),"stat")
    assert not stat.exists() or stat.read_text().split()[2]=="Z"

def test_trial_worker_is_only_compiled_not_run():
    source=Path(__file__).with_name("trial_worker.py").read_text()
    compile(source,"trial_worker.py","exec")
