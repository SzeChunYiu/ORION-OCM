"""Actual presented A/B/C processes, with explicit authored rows only."""
import copy,json,shutil,time
import pytest
from unary_contract import task_digest
from unary_method_process import launch
from unary_method_profile import observe
from unary_method_selection import contract
from learning_test_support import training
from test_unary_method_runtime import fresh
from test_unary_assay_service import rows
from assay_test_support import authored_only

def child(root,arm,mode,request,*,completed=True,seconds=25):
    deadline=time.monotonic()+seconds
    if mode=="presented_batch":request={**request,"deadline_monotonic":deadline}
    p=launch(root,mode,request,arm=arm,profile=observe(),deadline=deadline,timeout=seconds)
    assert p["terminal"]==("COMPLETED" if completed else "PROCESS_REFUSED"),p
    assert p["reaped"] and p["group_absent"] and p["returncode"]==(0 if completed else 2)
    value=json.loads((root/"result.json").read_bytes())
    assert value["pid"]==p["pid"] and value["profile"]==p["profile"]
    if arm!="ocm":
        assert not any(n=="ocm" or n.startswith(("ocm.","orion_v2.")) for n in value["imports"])
    if arm=="exact":
        assert not any(n.startswith(("unary_parent_","_unary_conventional_ledger","unary_method_store",
                                   "unary_method_journal","unary_method_runtime")) for n in value["imports"])
    if mode=="presented_batch":
        from unary_assay_rows import read_row
        assert p["row_custody"]["terminal"]=="ROW_CUSTODY_PASS"
        refs=value["outcome"]["rows"]
        value["outcome"]["rows"]=[read_row(root,ref,request["rows"][i],pid=p["pid"],work={})
                                   for i,ref in enumerate(refs)]
    return p,value

def test_actual_presented_selection_restart_support_roles_and_exact(tmp_path):
    all_processes=[];libraries=[];answers=[]
    for arm in ("conventional","ocm"):
        store=tmp_path/(arm+"-A-store")
        a,av=child(tmp_path/(arm+"-A"),arm,"acquire_selected",
            {"store":str(store),"training":[training("B")["task"],training("C")["task"]],
             "development":[fresh()],"contract":contract(2,1,authored=True)})
        all_processes.append(a);libraries.append(av["outcome"]["library_sha256"])
        bstore=tmp_path/(arm+"-B-store");shutil.copytree(store,bstore)
        b,bv=child(tmp_path/(arm+"-B"),arm,"presented_batch",{"store":str(bstore),"rows":rows(),"invoke":True})
        all_processes.append(b);out=bv["outcome"];answers.append(out["rows"][0]["result"]["packet"]["result"]["status"])
        assert bv["prior_uses"]==0 and out["terminal"]=="CHECKED"
        assert all(x["pid"]==b["pid"] for x in out["rows"])
        assert out["rows"][0]["parse"]["parse_calls"]==1
        assert all(x["parse"]["task_sha256"]==task_digest(fresh()) for x in out["rows"])
        assert all(x["result"]["packet"]["use"]["recipes_applied"]==1 for x in out["rows"])
        assert out["rows"][1]["result"]["execution_observation"]["engine_cache_reused"]
        assert out["totals"]["preparations"]==2
        mid=out["rows"][0]["result"]["packet"]["use"]["method_id"]
        cover=out["rows"][0]["result"]["packet"]["use"]["cover"]
        changed=fresh();changed["premises"].pop(cover[0])
        variants=[rows(changed)[0],rows()[1]]
        cstore=tmp_path/(arm+"-C-store");shutil.copytree(store,cstore)
        c,cv=child(tmp_path/(arm+"-C"),arm,"presented_batch",{"store":str(cstore),"rows":variants,"invoke":True})
        all_processes.append(c)
        assert [r["result"]["packet"]["use"]["recipes_applied"] for r in cv["outcome"]["rows"]]==[0,1]
        rev,_=child(tmp_path/(arm+"-withdraw"),arm,"revise",
                    {"store":str(bstore),"role":"utility","state":"REVOKED","method_id":mid})
        all_processes.append(rev)
        after,afterv=child(tmp_path/(arm+"-after"),arm,"presented_batch",{"store":str(bstore),"rows":rows(),"invoke":True})
        all_processes.append(after)
        assert all(r["result"]["packet"]["use"]["recipes_applied"]==0 for r in afterv["outcome"]["rows"])
        rein,_=child(tmp_path/(arm+"-reinstate"),arm,"revise",
                     {"store":str(bstore),"role":"utility","state":"LIVE","method_id":mid})
        all_processes.append(rein)
        end,endv=child(tmp_path/(arm+"-end"),arm,"presented_batch",{"store":str(bstore),"rows":rows(),"invoke":True})
        all_processes.append(end)
        assert all(r["result"]["packet"]["use"]["recipes_applied"]==1 for r in endv["outcome"]["rows"])
    exact,ev=child(tmp_path/"exact-B","exact","presented_batch",{"rows":rows()});all_processes.append(exact)
    answers.append(ev["outcome"]["rows"][0]["result"]["packet"]["result"]["status"])
    assert len(set(answers))==1 and libraries[0]==libraries[1]
    assert ev["outcome"]["rows"][1]["result"]["execution_observation"]["engine_cache_reused"]
    assert ev["outcome"]["totals"]["parent_completions"]==2
    assert len({p["pid"] for p in all_processes})==len(all_processes)
    assert all(a["ended_monotonic"]<=b["started_monotonic"] for a,b in zip(all_processes,all_processes[1:]))

def test_actual_child_malformed_middle_input_retains_later_slots(tmp_path):
    value=rows();value.append({**copy.deepcopy(value[0]),"observation_id":"unreached"})
    value[1]["presentation"]="text";value[1]["payload"]="unsupported language"
    p,v=child(tmp_path/"bad-middle","exact","presented_batch",{"rows":value})
    out=v["outcome"]
    assert out["terminal"]=="CANNOT_CHECK" and out["unreached_rows"]==[2]
    assert out["rows"][1]["parse"]["parse_calls"]==1 and out["rows"][1]["pid"]==p["pid"]
    assert out["rows"][1]["call_totals"]["semantic"] is None

def test_parent_rejects_unbound_request_deadline_before_child(tmp_path):
    deadline=time.monotonic()+20
    p=launch(tmp_path/"deadline-mismatch","presented_batch",
             {"rows":rows(),"deadline_monotonic":deadline+1},arm="exact",profile=observe(),deadline=deadline)
    assert p["terminal"]=="PROCESS_REFUSED" and p["pid"] is None
    assert "PRESENTED_LAUNCH_DEADLINE" in p["error"]


@pytest.mark.parametrize("arm",["exact","conventional","ocm"])
def test_authored_64_call_capacity_without_registered_generation(tmp_path,arm):
    request={}
    if arm!="exact":
        store=tmp_path/"A-store"
        child(tmp_path/"A",arm,"acquire_selected",
              {"store":str(store),"training":[training("B")["task"],training("C")["task"]],
               "development":[fresh()],"contract":contract(2,1,authored=True)})
        request={"store":str(store),"invoke":True}
    value=[{**copy.deepcopy(rows()[i%2]),"observation_id":"authored-repeat-"+str(i)} for i in range(64)]
    p,v=child(tmp_path/"B",arm,"presented_batch",{**request,"rows":value})
    out=v["outcome"]
    assert out["terminal"]=="CHECKED" and len(out["rows"])==64
    assert out["totals"]["preparations"]==64 and out["unreached_rows"]==[]
    assert [r["observation_id"] for r in out["rows"]]==[r["observation_id"] for r in value]
    expected=sum(r["call_totals"]["semantic"]["cache_key_nodes"] for r in out["rows"])
    assert out["totals"]["semantic"]["cache_key_nodes"]==expected

@pytest.mark.parametrize("arm",["exact","conventional","ocm"])
def test_authored_128_call_c_capacity_in_one_fresh_process(tmp_path,arm):
    request={}
    if arm!="exact":
        store=tmp_path/"A-store"
        child(tmp_path/"A",arm,"acquire_selected",
              {"store":str(store),"training":[training("B")["task"],training("C")["task"]],
               "development":[fresh()],"contract":contract(2,1,authored=True)})
        request={"store":str(store),"invoke":True}
    changed=fresh();changed["premises"].pop(0)
    four=[rows(changed)[0],rows()[1],rows(changed)[0],rows()[1]]
    value=[{**copy.deepcopy(four[j]),"row_id":"authored-C-"+str(i),
            "observation_id":"authored-C-"+str(i)+"-"+str(j)} for i in range(32) for j in range(4)]
    p,v=child(tmp_path/"C",arm,"presented_batch",{**request,"rows":value},seconds=120)
    out=v["outcome"]
    assert out["terminal"]=="CHECKED" and len(out["rows"])==128 and out["unreached_rows"]==[]
    assert out["totals"]["preparations"]==128
    assert [r["observation_id"] for r in out["rows"]]==[r["observation_id"] for r in value]
    assert {r["pid"] for r in out["rows"]}=={p["pid"]}
