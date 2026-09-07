"""Authored local trees only; no corpus preparation, Lake, network or profile dispatch."""
import copy,hashlib,importlib.util,json,os,time
from pathlib import Path
import pytest
import materialize_git as M
from test_materialize_git import fixture,command,run

def subject():
 assert importlib.util.find_spec("corpus_layout") is not None,"offline corpus layout helper missing"
 import corpus_layout as c
 return c

def rec(p):
 b=p.read_bytes();return {"path":str(p),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}

def inputs(tmp_path):
 rows=[{"name":n,"rev":"pending"} for n in ("alpha","beta")]
 root=tmp_path/"input";root.mkdir();materials=[]
 for name in ("corpus","alpha","beta"):
  place=root/name;place.mkdir()
  files={"lakefile.lean":("100644",b"import Lake\nopen Lake DSL\npackage authored\n"),
         "Example.lean":("100644",b"theorem authored (n : Nat) : n = n := rfl\n"),
         "plain":("100644",b"exact\r\nbytes"),"alias":("120000",b"plain"),
         "script":("100755",b"#!/never/execute\n"),"widget.js":("100644",b"retained data\n"),
         "lake.trace":("100644",b"retained trace\n")}
  if name=="corpus":
   # Lock bytes are inserted after dependency pins are available, so corpus goes last.
   continue
  bare,commit,tree,_=fixture(place,files);r=run(M,bare,commit,tree,place/"material")
  assert r["terminal"]=="MATERIALIZED"
  rows[0 if name=="alpha" else 1]["rev"]=commit
  materials.append({"name":name,"commit":commit,"tree":tree,"receipt":rec(place/"material/RESULT.json")})
 lock=json.dumps({"version":"1.2.0","packagesDir":".lake/packages","packages":rows},sort_keys=True).encode()
 place=root/"corpus";files["lake-manifest.json"]=("100644",lock)
 bare,commit,tree,_=fixture(place,files);r=run(M,bare,commit,tree,place/"material")
 assert r["terminal"]=="MATERIALIZED"
 materials.insert(0,{"name":"corpus","commit":commit,"tree":tree,"receipt":rec(place/"material/RESULT.json")})
 return materials,rec(Path(r["workspace"])/"lake-manifest.json"),rows

def launch(c,data,out,**kw):
 materials,lock,rows=data
 return c._prepare(materials,lock,out,deadline_monotonic=time.monotonic()+20,
                   lock_validator=lambda raw:rows,authority_scope="AUTHORED_LAYOUT_ONLY",**kw)

def test_independent_faithful_mount_layout(tmp_path):
 c=subject();data=inputs(tmp_path);r=launch(c,data,tmp_path/"layout")
 assert r["terminal"]=="LAYOUT_READY",r
 assert r["authority_scope"]=="AUTHORED_LAYOUT_ONLY" and len(r["material_mounts"])==3
 assert len(r["writable"])==6 and all(not Path(x["path"]).is_symlink() for x in r["writable"])
 for item in data[0]:
  source=Path(json.loads(Path(item["receipt"]["path"]).read_bytes())["workspace"])
  dest=Path(r["workspaces"][item["name"]])
  assert (dest/"plain").read_bytes()==b"exact\r\nbytes"
  assert (dest/"script").stat().st_mode&0o777==0o755
  assert os.readlink(dest/"alias")=="plain"
  assert command(dest/".git","rev-parse","HEAD").decode().strip()==item["commit"]
  assert (dest/".git/HEAD").read_bytes()==(source/".git/HEAD").read_bytes()
  assert (dest/"plain").stat().st_ino!=(source/"plain").stat().st_ino
  assert c.snapshot(source,time.monotonic()+10)==r["source_before"][item["name"]]
  assert r["source_before"][item["name"]]==r["source_after"][item["name"]]
 assert set(r["added_directories"]["corpus"])=={".lake",".lake/config",".lake/build",".lake/cache",".lake/packages",".lake/packages/alpha",".lake/packages/beta"}
 assert all(list(Path(x["path"]).iterdir())==[] for x in r["writable"] if x["guest"]!="/work")
 assert not r.get("code_audit") and "code_audit" not in r

@pytest.mark.parametrize("change",["missing","duplicate","extra","wrong_pin"])
def test_exact_lock_membership(tmp_path,change):
 c=subject();data=inputs(tmp_path);items=data[0]
 if change=="missing":items.pop()
 if change=="duplicate":items[2]=copy.deepcopy(items[1])
 if change=="extra":items.append(copy.deepcopy(items[1]))
 if change=="wrong_pin":items[1]["commit"]="f"*40
 r=launch(c,data,tmp_path/"layout")
 assert r["terminal"]=="LAYOUT_REFUSED" and "MATERIAL_IDENTITY" in r["error"]

def test_production_requires_original_lock(tmp_path):
 c=subject();data=inputs(tmp_path)
 r=c.prepare_layout(data[0],data[1],tmp_path/"layout",deadline_monotonic=time.monotonic()+20)
 assert r["terminal"]=="LAYOUT_REFUSED" and "LOCK_IDENTITY" in r["error"]

@pytest.mark.parametrize("change",["bytes","mode","extra","metadata","symlink_escape","metadata_alias"])
def test_source_or_metadata_mutation_refuses(tmp_path,change):
 c=subject();data=inputs(tmp_path);ws=Path(json.loads(Path(data[0][1]["receipt"]["path"]).read_bytes())["workspace"])
 if change=="bytes":(ws/"plain").write_bytes(b"changed")
 if change=="mode":(ws/"script").chmod(0o644)
 if change=="extra":(ws/"extra").write_text("extra")
 if change=="metadata":
  (ws/".git/HEAD").chmod(0o644);(ws/".git/HEAD").write_text("f"*40+"\n")
 if change=="symlink_escape":
  (ws/"alias").unlink();(ws/"alias").symlink_to(tmp_path)
 if change=="metadata_alias":os.link(ws/".git/HEAD",tmp_path/"metadata-alias")
 r=launch(c,data,tmp_path/"layout")
 assert r["terminal"]=="LAYOUT_REFUSED" and not r.get("material_mounts")

def test_input_receipt_mutation_refuses(tmp_path):
 c=subject();data=inputs(tmp_path);p=Path(data[0][1]["receipt"]["path"]);p.write_text("{}")
 with pytest.raises(ValueError,match="RECORD_IDENTITY"):launch(c,data,tmp_path/"layout")
 assert not (tmp_path/"layout").exists()

def test_existing_and_overlapping_outputs_refuse(tmp_path):
 c=subject();data=inputs(tmp_path);out=tmp_path/"existing";out.mkdir();(out/"keep").write_text("safe")
 with pytest.raises(FileExistsError):launch(c,data,out)
 assert (out/"keep").read_text()=="safe"
 ws=Path(json.loads(Path(data[0][0]["receipt"]["path"]).read_bytes())["workspace"])
 with pytest.raises(ValueError,match="OUTPUT_OVERLAP"):launch(c,data,ws/"new")

def test_deadline_and_post_copy_drift_preserved(tmp_path,monkeypatch):
 c=subject();data=inputs(tmp_path)
 with pytest.raises(TimeoutError,match="LAYOUT_DEADLINE"):
  c._prepare(data[0],data[1],tmp_path/"expired",deadline_monotonic=time.monotonic()-1,
              lock_validator=lambda raw:data[2],authority_scope="AUTHORED_LAYOUT_ONLY")
 assert not (tmp_path/"expired").exists()
 original=c.copy_workspace
 def alter(source,*args):
  value=original(source,*args);(source/"plain").write_text("after copy");return value
 monkeypatch.setattr(c,"copy_workspace",alter)
 r=launch(c,data,tmp_path/"drift")
 assert r["terminal"]=="LAYOUT_REFUSED" and "SOURCE_POST_DRIFT" in r["error"]
 assert (tmp_path/"drift/RESULT.json").exists()

def test_nonempty_overlay_and_package_override_refuse(tmp_path):
 c=subject();data=inputs(tmp_path)
 ws=Path(json.loads(Path(data[0][0]["receipt"]["path"]).read_bytes())["workspace"])
 # A trusted materializer receipt may include ordinary tracked .lake content; it must not be hidden.
 (ws/".lake").mkdir();(ws/".lake/build").mkdir();(ws/".lake/build/tracked").write_text("keep")
 receipt=Path(data[0][0]["receipt"]["path"]);r=json.loads(receipt.read_bytes())
 for name in (".lake",".lake/build"):
  r["entries"][name]={"mode":"40000","oid":"a"*40}
 b=b"keep";r["entries"][".lake/build/tracked"]={"mode":"100644","oid":hashlib.sha1(b"blob 4\0"+b).hexdigest(),"sha256":hashlib.sha256(b).hexdigest(),"bytes":4}
 receipt.write_text(json.dumps(r));data[0][0]["receipt"]=rec(receipt)
 result=launch(c,data,tmp_path/"layout")
 assert result["terminal"]=="LAYOUT_REFUSED" and "NONEMPTY_OVERLAY" in result["error"]

@pytest.mark.parametrize("change",["copy","inventory","artifact"])
def test_final_snapshot_rejects_late_layout_drift(tmp_path,monkeypatch,change):
 c=subject();data=inputs(tmp_path);out=tmp_path/"layout";original=c.snapshot
 def corrupt(root,deadline):
  if root==out:
   if change=="copy":(out/"materials/alpha/workspace/plain").write_text("late drift")
   elif change=="inventory":(out/"alpha-inventory.json").write_text("{}")
   else:(out/"artifacts/config/injected.olean").write_bytes(b"unexpected cache")
  return original(root,deadline)
 monkeypatch.setattr(c,"snapshot",corrupt)
 r=launch(c,data,out)
 assert r["terminal"]=="LAYOUT_REFUSED" and "FINAL_LAYOUT_DRIFT" in r["error"]

def test_output_parent_alias_refuses_before_writes(tmp_path):
 c=subject();data=inputs(tmp_path);alias=tmp_path/"alias";alias.symlink_to(tmp_path/"input",target_is_directory=True)
 with pytest.raises(ValueError,match="PATH_ALIAS"):launch(c,data,alias/"output")
 assert not (tmp_path/"input/output").exists()

def test_final_inventory_deadline_refuses(tmp_path,monkeypatch):
 c=subject();data=inputs(tmp_path);out=tmp_path/"layout";original=c.snapshot
 def expire(root,deadline):
  result=original(root,deadline)
  if root==out:monkeypatch.setattr(c.time,"monotonic",lambda:deadline+1)
  return result
 monkeypatch.setattr(c,"snapshot",expire)
 r=launch(c,data,out)
 assert r["terminal"]=="LAYOUT_REFUSED" and "LAYOUT_DEADLINE" in r["error"]

@pytest.mark.parametrize("changed",[False,True])
def test_read_record_binds_consumed_bytes(tmp_path,monkeypatch,changed):
 c=subject();p=tmp_path/"receipt.json";p.write_bytes(b'{"ok":1}')
 binding=rec(p);original=Path.read_bytes
 def read(path):
  return b'{"ok":2}' if path==p and changed else original(path)
 monkeypatch.setattr(Path,"read_bytes",read)
 if changed:
  with pytest.raises(ValueError,match="CONSUMED_RECORD_IDENTITY"):c.read_record(binding,time.monotonic()+10)
 else:assert c.read_record(binding,time.monotonic()+10)==b'{"ok":1}'

def test_read_record_checks_deadline_after_consumption(tmp_path,monkeypatch):
 c=subject();p=tmp_path/"receipt.json";p.write_bytes(b'{"ok":1}');binding=rec(p)
 deadline=time.monotonic()+10;original=Path.read_bytes
 def read(path):
  raw=original(path)
  if path==p:monkeypatch.setattr(c.time,"monotonic",lambda:deadline+1)
  return raw
 monkeypatch.setattr(Path,"read_bytes",read)
 with pytest.raises(TimeoutError,match="LAYOUT_DEADLINE"):c.read_record(binding,deadline)

@pytest.mark.parametrize("substituted",[False,True])
def test_preflight_uses_bound_receipt_before_creating_output(tmp_path,monkeypatch,substituted):
 c=subject();data=inputs(tmp_path);p=Path(data[0][0]["receipt"]["path"])
 receipt=json.loads(p.read_bytes());ws=Path(receipt["workspace"]);before=c.snapshot(ws,time.monotonic()+10)
 decoy=json.loads(Path(data[0][1]["receipt"]["path"]).read_bytes())["workspace"]
 original=Path.read_bytes;calls=0
 def read(path):
  nonlocal calls
  if path==p:
   calls+=1
   if substituted and calls==1:return json.dumps({**receipt,"workspace":decoy}).encode()
  return original(path)
 monkeypatch.setattr(Path,"read_bytes",read)
 with pytest.raises(ValueError,match="CONSUMED_RECORD_IDENTITY" if substituted else "OUTPUT_OVERLAP"):
  launch(c,data,ws/"layout")
 assert c.snapshot(ws,time.monotonic()+10)==before and not (ws/"layout").exists()
