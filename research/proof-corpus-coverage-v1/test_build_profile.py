import importlib.util,json
from hashlib import sha256
from pathlib import Path
import pytest
from resource_contract import record,write_json,canonical
def subject():
 assert importlib.util.find_spec("build_profile") is not None,"registered offline dispatcher missing"
 from resource_boot import load
 return load()["build_profile"]
def fixture(tmp_path):
 exe=tmp_path/"fixture";exe.write_bytes(b"not executed")
 inv=tmp_path/"inventory.json";source=tmp_path/"source";source.mkdir();(source/"x").write_text("x")
 from build_profile_policy import inventory
 write_json(inv,inventory(source))
 p={"schema":"ocm.f1.build-profile.v1","bwrap":record(exe),"aa_exec":record(exe),
 "files":[{"source":record(exe),"guest":"/tools/fixture","access":"executable"}],
 "materials":[{"path":str(source),"guest":"/source","inventory":record(inv)}],
 "writable":[{"path":str(tmp_path/"artifacts"),"guest":"/work"}],
 "argv":["/tools/fixture"],"environment":{}}
 evidence=tmp_path/"audit.txt";evidence.write_text("Authored fixture; not a native or closure qualification.")
 a=tmp_path/"audit.json";write_json(a,{"schema":"ocm.f1.build-code-audit.v1",
 "profile_payload_sha256":sha256(canonical(p)).hexdigest(),"non_neural_code_reviewed":True,
 "dynamic_code_scope":"REGISTERED_EXEC_AND_FILE_MAPPING_ONLY","evidence":[record(evidence)],
 "limitations":"Caller audit; format checks do not independently prove this review."})
 p["code_audit"]=record(a);return p
def test_bound_manifest_and_directory_inventory(tmp_path):
 m=subject();p=fixture(tmp_path);assert m.validate(p)
 (tmp_path/"source/x").write_text("drift")
 with pytest.raises(ValueError,match="inventory drift"):m.validate(p)
def test_reject_unregistered_dispatch_before_execution(tmp_path):
 m=subject();p=fixture(tmp_path);p["argv"][0]="/bin/sh"
 with pytest.raises(ValueError):m.validate(p)
def test_reject_writable_overlap_and_caller_audit_drift(tmp_path):
 m=subject();p=fixture(tmp_path);p["writable"][0]["guest"]="/tools"
 with pytest.raises(ValueError):m.validate(p)
def test_no_implicit_host_mounts(tmp_path):
 m=subject();p=fixture(tmp_path);args=m.command(p,"test-012345")
 assert "--unshare-all" in args and "--setenv" not in args
 assert "/" not in args and "/home/billy" not in args
 assert args[-4:]==["-p","ocm-f1-test-012345","--","/tools/fixture"]

def test_reject_host_write_alias_into_material(tmp_path):
 m=subject();p=fixture(tmp_path);p["writable"][0]["path"]=str(tmp_path/"source/artifacts")
 # Rebind the caller audit to isolate the mount-contract test.
 a=Path(p["code_audit"]["path"]);value=json.loads(a.read_bytes())
 value["profile_payload_sha256"]=sha256(canonical({k:v for k,v in p.items() if k!="code_audit"})).hexdigest()
 a.write_bytes(canonical(value));p["code_audit"]=record(a)
 with pytest.raises(ValueError,match="host overlaps"):m.validate(p)

def test_keep_policy_when_workload_cleanup_incomplete(tmp_path,monkeypatch):
 m=subject();p=fixture(tmp_path);calls=[]
 monkeypatch.setattr(m,"helper",lambda mode,*args:calls.append(mode) or {})
 monkeypatch.setattr(m.resource_runner,"run",lambda *a,**k:{"terminal":"CLEANUP_INCOMPLETE","cleanup":{"members_empty":False}})
 from test_resource_contract import limits
 r=m.run(p,limits(),tmp_path/"run")
 assert r["terminal"]=="CLEANUP_INCOMPLETE"
 assert calls==["policy-add"]
 assert r["policy_retained_until_empty"] is True

def test_post_dispatch_input_drift_never_passes(tmp_path,monkeypatch):
 m=subject();p=fixture(tmp_path)
 monkeypatch.setattr(m,"helper",lambda *args:{})
 def dispatch(*a,**k):
  (tmp_path/"source/x").write_text("changed")
  return {"terminal":"COMPLETED","cleanup":{"members_empty":True}}
 monkeypatch.setattr(m.resource_runner,"run",dispatch)
 from test_resource_contract import limits
 r=m.run(p,limits(),tmp_path/"run")
 assert r["terminal"]=="PROFILE_REFUSED" and "inventory drift" in r["error"]["message"]

@pytest.mark.parametrize("relation",["equal","ancestor","descendant"])
def test_workload_cannot_mount_supervisor_receipts(tmp_path,relation):
 m=subject();p=fixture(tmp_path);out=tmp_path/"run"
 paths={"equal":out,"ancestor":tmp_path,"descendant":out/"artifacts"}
 p["writable"][0]["path"]=str(paths[relation])
 from test_resource_contract import limits
 with pytest.raises(ValueError,match="output overlaps"):
  m.run(p,limits(),out)
 assert not out.exists()
