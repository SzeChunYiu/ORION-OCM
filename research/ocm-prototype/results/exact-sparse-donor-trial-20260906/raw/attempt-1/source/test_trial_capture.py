"""Full sealed-capture grading controls with explicitly synthetic non-actor records."""
import copy
import json
from pathlib import Path
import pytest
from trial_common import canonical, read, sha, write
from trial_grade import grade
from test_trial import paired, synthetic

SCOPE="DIRECT_SV_SOLVE_WITH_COMMITMENT_DECISION; no durable query/result append; binder persistence included"

def emit(root):
    root.mkdir(); _,assignments=paired(); _,expected=synthetic()
    expected.update(task={"fixture":"SYNTHETIC"},config={"fixture":"SYNTHETIC"},
                    binding_receipts=[{"program_id":"guard","registry_key":"guard@SYNTHETIC"},
                                      {"program_id":"max","registry_key":"max@SYNTHETIC"}])
    names=["ocm.runtime.solve","ocm.kso.navigation","g1_vessel","clia_reuse_vessel","clia_reuse_apply",
           "exact_sparse_donor_consumer","exact_sparse_donor","exact_sparse_donor_check"]
    origins={n:{"path":"/SYNTHETIC/"+n,"sha256":"SYNTHETIC"} for n in names}
    runtime={n:{"path":"/SYNTHETIC/"+n,"sha256":"SYNTHETIC"} for n in ("z3","sympy")}
    manifest={"fixture":"SYNTHETIC_NON_ACTOR", "assignments":assignments,"expected":expected,
              "expected_module_origins":origins,"runtime_modules":runtime,"consumer_scope":SCOPE}
    write(root/"manifest.json",manifest); mh=sha(root/"manifest.json")
    write(root/"launch.json",{"manifest_sha256":mh,"root":str(root),"manifest_source":"/SYNTHETIC/MANIFEST.json"})
    reports=[]
    for a in assignments:
        prefix=f"case-{a['index']:02d}"; folder=root/prefix;folder.mkdir()
        case={"assignment":a,"manifest_sha256":mh,"output":str(folder),"manifest":"/SYNTHETIC/MANIFEST.json"}
        write(folder/"input.json",case)
        base={"modules":{n:origins[n] for n in names[:5]},"external":{"z3":runtime["z3"]},"sympy_imported":False,"sympy_module_count":0}
        prep={"state":expected["state"],"task":expected["task"],"config":expected["config"],
              "request":expected["request"],"catalogue":expected["catalogue"],"events":[],
              "binding_receipts":[dict(b,bind_wall_s=.01) for b in expected["binding_receipts"]],"origins":base}
        write(folder/"preparation.json",prep)
        calls=[]
        for i in range(2):
            payload,_=synthetic(a["arm"]);payload["assignment"]=a;payload["index"]=i;payload["invocations"][0]["index"]=i
            write(folder/f"call-{i}.json",payload)
            calls.append({"index":i,"path":f"call-{i}.json","sha256":sha(folder/f"call-{i}.json"),
                          "bytes":(folder/f"call-{i}.json").stat().st_size,"wall_ns":100 if a["arm"]=="reference" else 80})
        final=copy.deepcopy(base);final["modules"]["exact_sparse_donor_consumer"]=origins["exact_sparse_donor_consumer"]
        if a["arm"]=="sympy":
            final["external"]["sympy"]=runtime["sympy"];final["sympy_imported"]=True;final["sympy_module_count"]=1
            final["modules"].update({n:origins[n] for n in names[-2:]})
        worker={"status":"COMPLETED","assignment":a,"pid":1000+a["index"],"calls":calls,"assigned_calls":2,
                "consumer_scope":SCOPE,"case_sha256":sha(folder/"input.json"),"manifest_sha256":mh,
                "preparation_sha256":sha(folder/"preparation.json"),"origins":final,"final_state":expected["state"]}
        write(folder/"stdout",worker);(folder/"stderr").write_bytes(b"");write(folder/"captured-worker.json",worker)
        process={"pid":worker["pid"],"exit_code":0,"timed_out":False,"supervisor_error":None,
                 "pid_absent":True,"private_state_removed":True,"post_reap_group_required_kill":False,
                 "wait4_raw":{"ru_utime":.01},"worker":worker,"total_two_call_process_ns":1000 if a["arm"]=="reference" else 900,
                 "stdout_sha256":sha(folder/"stdout"),"stderr_sha256":sha(folder/"stderr")}
        write(folder/"process.json",process)
        reports.append({"assignment":a,"process":prefix+"/process.json","exit_code":0,"timed_out":False})
    write(root/"receipt.json",{"status":"SEALED","reports":reports,"assigned_processes":14,"assigned_calls":28,"manifest_sha256":mh})
    seal(root);return mh

def replace(path, obj):
    path.write_bytes(canonical(obj)+b"\n")

def seal(root):
    data={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob("*")) if p.is_file() and p.name!="SEAL.json"}
    replace(root/"SEAL.json",data)

def test_sealed_synthetic_no_alarm_and_portable_paths(tmp_path):
    root=tmp_path/"SYNTHETIC";mh=emit(root)
    result=grade(root,mh);write(tmp_path/"SYNTHETIC-grade.json",result)
    assert result["qualified_calls"]==28 and result["component_gate"]=="ADOPTION_CANDIDATE"
    moved=tmp_path/"RELOCATED";root.rename(moved)
    assert grade(moved,mh)==result

@pytest.mark.parametrize("change",["bad_vector","event_extra_pid","prep_event","missing_arm","timeout","changed_raw"])
def test_sealed_synthetic_negatives(tmp_path,change):
    root=tmp_path/"SYNTHETIC";mh=emit(root)
    if change in ("bad_vector","event_extra_pid"):
        path=root/"case-01/call-0.json";p=read(path)
        if change=="bad_vector":p["result"]["vectors"][0]["values"]["synthetic-a"]="3/4"
        else:p["invocations"][0]["pid"]=42
        replace(path,p)
        worker=read(root/"case-01/stdout");worker["calls"][0]["sha256"]=sha(path)
        replace(root/"case-01/stdout",worker);replace(root/"case-01/captured-worker.json",worker)
        process=read(root/"case-01/process.json");process["worker"]=worker;process["stdout_sha256"]=sha(root/"case-01/stdout")
        replace(root/"case-01/process.json",process)
    elif change=="prep_event":
        path=root/"case-01/preparation.json";p=read(path);p["events"]=[{"action":"SYNTHETIC_UNEXPECTED"}];replace(path,p)
    elif change=="missing_arm":
        path=root/"receipt.json";p=read(path);p["reports"].pop();replace(path,p)
    elif change=="timeout":
        path=root/"case-01/process.json";p=read(path);p["timed_out"]=True;replace(path,p)
    else:(root/"case-01/stderr").write_text("altered")
    if change!="changed_raw":seal(root)
    try:result=grade(root,mh)
    except ValueError:return
    assert result["functional_terminal"]!="EXACT_FUNCTIONAL_PARITY"
