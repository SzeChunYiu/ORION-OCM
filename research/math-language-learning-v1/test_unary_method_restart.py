"""Fresh -I -S process A/B; B gets no training or fixture generator."""
import importlib,importlib.util,json
from pathlib import Path
import pytest
from learning_test_support import training
from test_unary_method_runtime import fresh

def launch(root,mode,request):
    assert importlib.util.find_spec("unary_method_process"),"missing actual process entry"
    return importlib.import_module("unary_method_process").launch(root,mode,request,
        profile=importlib.import_module("unary_method_profile").observe())

def test_real_acquisition_exit_restart_causal_use(tmp_path):
    store=tmp_path/"stored"
    a=launch(tmp_path/"A","acquire",{"store":str(store),"training":[training("B"),training("C")]})
    assert a["terminal"]=="COMPLETED",a
    assert a["argv"][0]==a["profile"]["executable"]
    ar=json.loads((tmp_path/"A/result.json").read_bytes())
    assert ar["outcome"]["method_ids"] and ar["callbacks_on_restore"]==0
    b=launch(tmp_path/"B","solve",{"store":str(store),"task":fresh(),"invoke":True})
    assert b["terminal"]=="COMPLETED",b
    br=json.loads((tmp_path/"B/result.json").read_bytes())
    assert ar["profile"]==br["profile"]==a["profile"]==b["profile"]
    assert a["pid"]!=b["pid"] and a["ended_monotonic"]<=b["started_monotonic"]
    assert a["reaped"] and b["reaped"] and a["group_absent"] and b["group_absent"]
    assert br["outcome"]["terminal"]=="CHECKED"
    assert br["outcome"]["packet"]["use"]["recipes_applied"]==1
    assert br["callbacks_on_restore"]==0 and br["prior_uses"]==0
    assert not any("test" in n or "fixture" in n for n in br["imports"])
    c=launch(tmp_path/"C","solve",{"store":str(store),"task":fresh(),"invoke":False})
    assert c["terminal"]=="COMPLETED",c
    cr=json.loads((tmp_path/"C/result.json").read_bytes())
    assert cr["prior_uses"]==1 and cr["outcome"]["packet"]["use"]["recipes_applied"]==0
    assert cr["outcome"]["packet"]["result"]["status"]==br["outcome"]["packet"]["result"]["status"]
    assert br["source_before"]==br["source_after"]==ar["source_after"]

def test_cold_cannot_reconstruct_missing_issuer(tmp_path):
    out=launch(tmp_path/"missing","solve",{"store":str(tmp_path/"missing-store"),"task":fresh(),"invoke":True})
    assert out["terminal"]=="PROCESS_REFUSED" and out["returncode"]!=0
    data=json.loads((tmp_path/"missing/result.json").read_bytes())
    assert data["terminal"]=="CANNOT_CHECK" and "MISSING" in data["reason"]
    assert out["reaped"] and out["group_absent"]

def test_bad_process_request_retains_raw(tmp_path):
    out=launch(tmp_path/"bad","solve",{"store":str(tmp_path/"store"),"task":fresh(),"invoke":True,"code":"no"})
    assert out["terminal"]=="PROCESS_REFUSED"
    assert (tmp_path/"bad/request.json").is_file() and (tmp_path/"bad/PROCESS.json").is_file()
    assert (tmp_path/"bad/stdout.bin").read_bytes()
