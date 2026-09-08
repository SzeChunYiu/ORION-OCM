"""Profile/CLI exact forwarding and read-only external clock authority."""
import json,subprocess,sys,time
from pathlib import Path
from hashlib import sha256
import pytest
from resource_contract import canonical,record
from deadline_test_support import started
from test_build_profile import subject,fixture
from test_resource_contract import limits

def mounted(root):
    p=fixture(root);b=started(root)
    p["files"].append({"source":b["record"],"guest":"/assay/STARTED.json","access":"read"})
    audit=Path(p["code_audit"]["path"]);a=json.loads(audit.read_bytes())
    a["profile_payload_sha256"]=sha256(canonical({k:v for k,v in p.items() if k!="code_audit"})).hexdigest()
    audit.write_bytes(canonical(a));p["code_audit"]=record(audit)
    return p,b

@pytest.mark.parametrize("bound",[False,True])
def test_exact_optional_forwarding_and_legacy_omission(tmp_path,monkeypatch,bound):
    m=subject();p,b=mounted(tmp_path);seen=[]
    monkeypatch.setattr(m,"helper",lambda *a:{})
    def dispatch(*a,**kw):
        seen.append(kw)
        return {"terminal":"COMPLETED","dispatch":{"state":"STARTED"},"cleanup":{"members_empty":True,"reaped":True}}
    monkeypatch.setattr(m.resource_runner,"run",dispatch)
    result=m.run(p,limits(),tmp_path/"out",**({"external_started":b} if bound else {}))
    assert result["terminal"]=="COMPLETED"
    assert ("external_started" in seen[0])==bound
    if bound:assert seen[0]["external_started"]==b==result["external_started"]["binding"]

@pytest.mark.parametrize("fault",["missing_mount","writable_clock","setup_expiry","final_expiry"])
def test_profile_deadline_and_readonly_boundary(tmp_path,monkeypatch,fault):
    m=subject();p,b=mounted(tmp_path);calls=[];dispatched=[]
    if fault=="missing_mount":p["files"].pop()
    elif fault=="writable_clock":p["writable"][0]["path"]=str(tmp_path)
    def helper(mode,*a):
        calls.append(mode)
        if fault=="setup_expiry" and mode=="policy-add":
            monkeypatch.setattr(m.Started.check.__globals__["time"],"monotonic_ns",lambda:10**18)
        return {}
    monkeypatch.setattr(m,"helper",helper)
    def dispatch(*a,**kw):
        dispatched.append(kw)
        if fault=="final_expiry":
            monkeypatch.setattr(m.Started.check.__globals__["time"],"monotonic_ns",lambda:10**18)
        return {"terminal":"COMPLETED","dispatch":{"state":"STARTED"},"cleanup":{"members_empty":True,"reaped":True}}
    monkeypatch.setattr(m.resource_runner,"run",dispatch)
    if fault=="writable_clock":
        # Keep the preexisting output-overlap guard separate from STARTED overlap.
        output=tmp_path.parent/(tmp_path.name+"-external-supervisor")
    else:output=tmp_path/"out"
    result=m.run(p,limits(),output,external_started=b)
    assert result["terminal"]!= "COMPLETED"
    if fault=="final_expiry":
        assert len(dispatched)==1 and result["dispatch"]["terminal"]=="COMPLETED"
        assert result["terminal"]=="POST_DISPATCH_CUSTODY_FAILED"
    else:assert not dispatched
    if fault in ("missing_mount","writable_clock"):assert calls==[]
    else:assert calls==["policy-add","policy-remove"]

def test_real_isolated_raw_source_cli_keeps_expired_authority(tmp_path):
    import resource_boot
    sources=tmp_path/"sources";sources.mkdir();here=Path(resource_boot.__file__).parent
    for name in (*resource_boot.MODULES,"resource_boot"):
        (sources/(name+".py")).write_bytes((here/(name+".py")).read_bytes())
    p,b=mounted(tmp_path);v=json.loads(Path(b["record"]["path"]).read_bytes())
    v["started_monotonic_ns"]=time.monotonic_ns()-6000000000
    v["deadline_monotonic_ns"]=v["started_monotonic_ns"]+b["duration_ns"]
    Path(b["record"]["path"]).write_bytes(canonical(v));b["record"]=record(b["record"]["path"])
    for name,data in (("profile.json",p),("limits.json",limits()),("binding.json",b)):
        (tmp_path/name).write_bytes(canonical(data))
    cmd=[sys.executable,"-I","-S","-B",str(sources/"resource_boot.py"),"run",
         "--profile",str(tmp_path/"profile.json"),"--limits",str(tmp_path/"limits.json"),
         "--output",str(tmp_path/"out"),"--started-binding",str(tmp_path/"binding.json")]
    run=subprocess.run(cmd,capture_output=True)
    (tmp_path/"CLI.stdout").write_bytes(run.stdout);(tmp_path/"CLI.stderr").write_bytes(run.stderr)
    (tmp_path/"CLI-command.json").write_bytes(canonical({"argv":cmd,"returncode":run.returncode}))
    assert run.returncode==2 and not run.stderr
    value=json.loads(run.stdout);retained=json.loads((tmp_path/"out/build-profile-receipt.json").read_bytes())
    assert value==retained and value["dispatch_state"]=="NOT_ATTEMPTED"
    assert value["external_started"]["binding"]==b
    assert "EXTERNAL_DEADLINE_EXPIRED" in value["error"]["message"]
    assert value["driver_sources"]["resource_deadline"]["sha256"]==record(sources/"resource_deadline.py")["sha256"]
