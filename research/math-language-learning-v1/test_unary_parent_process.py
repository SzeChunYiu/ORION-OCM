"""Actual portable A/B/C processes; authored tasks only."""
import json,shutil
import pytest
from learning_test_support import training
from test_unary_method_runtime import fresh
from unary_method_selection import contract
from unary_method_process import launch
from unary_method_profile import observe
from unary_contract import InputRefused

def run(tmp_path,name,arm,mode,request):
    root=tmp_path/name
    receipt=launch(root,mode,request,arm=arm,profile=observe())
    assert receipt["terminal"]=="COMPLETED",receipt
    assert receipt["returncode"]==0 and receipt["reaped"] and receipt["group_absent"]
    value=json.loads((root/"result.json").read_bytes())
    assert value["arm"]==arm and value["profile"]==receipt["profile"]
    if arm=="conventional":
        assert not any(n=="ocm" or n.startswith(("ocm.","orion_v2.")) for n in value["imports"])
        assert "_unary_conventional_ledger.ledger" in value["imports"]
    return receipt,value

def test_actual_paired_acquisition_use_and_revision_lifetimes(tmp_path):
    receipts=[];digests=[]
    for arm in ("conventional","ocm"):
        base=tmp_path/(arm+"-A-store")
        req={"store":str(base),"training":[training("B")["task"],training("C")["task"]],
             "development":[fresh()],"contract":contract(2,1,authored=True)}
        a,av=run(tmp_path,arm+"-A",arm,"acquire_selected",req);receipts.append(a)
        digests.append([av["outcome"][x] for x in ("pool_sha256","ranking_sha256","library_sha256")])
        bstate=tmp_path/(arm+"-B-store");shutil.copytree(base,bstate)
        b,bv=run(tmp_path,arm+"-B",arm,"batch",{"store":str(bstate),"tasks":[fresh(),fresh()],"invoke":True});receipts.append(b)
        assert bv["prior_uses"]==0 and bv["callbacks_on_restore"]==0
        rows=bv["outcome"]["rows"]
        assert all(x["result"]["packet"]["use"]["recipes_applied"]==1 for x in rows)
        assert not rows[0]["result"]["packet"]["execution"]["engine_cache_reused"]
        assert rows[1]["result"]["packet"]["execution"]["engine_cache_reused"]
        mid=rows[0]["result"]["packet"]["use"]["method_id"]
        cstate=tmp_path/(arm+"-C-store");shutil.copytree(base,cstate)
        changed=fresh();changed["premises"].pop(0)
        c,cv=run(tmp_path,arm+"-C",arm,"batch",{"store":str(cstate),"tasks":[changed,fresh()],"invoke":True});receipts.append(c)
        assert cv["outcome"]["rows"][0]["result"]["packet"]["use"]["recipes_applied"]==0
        assert cv["outcome"]["rows"][1]["result"]["packet"]["use"]["recipes_applied"]==1
        audit,auditv=run(tmp_path,arm+"-audit",arm,"status",{"store":str(bstate)});receipts.append(audit)
        assert auditv["prior_uses"]==2
        rev,_=run(tmp_path,arm+"-withdraw",arm,"revise",{"store":str(bstate),"role":"utility","state":"REVOKED","method_id":mid});receipts.append(rev)
        after,afterv=run(tmp_path,arm+"-after",arm,"solve",{"store":str(bstate),"task":fresh(),"invoke":True});receipts.append(after)
        assert afterv["outcome"]["packet"]["use"]["recipes_applied"]==0
        rein,_=run(tmp_path,arm+"-reinstate",arm,"revise",{"store":str(bstate),"role":"utility","state":"LIVE","method_id":mid});receipts.append(rein)
        end,endv=run(tmp_path,arm+"-end",arm,"solve",{"store":str(bstate),"task":fresh(),"invoke":True});receipts.append(end)
        assert endv["outcome"]["packet"]["use"]["recipes_applied"]==1
    assert digests[0]==digests[1]
    assert len({x["pid"] for x in receipts})==len(receipts)
    assert all(a["ended_monotonic"]<=b["started_monotonic"] for a,b in zip(receipts,receipts[1:]))

@pytest.mark.parametrize("arm",["unknown",None,True])
def test_data_cannot_select_an_arbitrary_dispatch_arm(tmp_path,arm):
    with pytest.raises(InputRefused,match="PROCESS_ARM"):
        launch(tmp_path/"bad","status",{"store":str(tmp_path/"store")},arm=arm,profile=observe())
