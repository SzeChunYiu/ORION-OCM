"""Cold offline layout copies; profile fragments are not execution/code-audit authority."""
import hashlib,json,math,os,re,shutil,stat,time
from pathlib import Path
from acquisition_git import validate_lock
from build_profile_policy import guest_path

def remaining(deadline):
 if type(deadline) not in (int,float) or not math.isfinite(deadline) or time.monotonic()>=deadline:
  raise TimeoutError("LAYOUT_DEADLINE")

def canonical(path):
 p=Path(path).absolute()
 if p.resolve(strict=True)!=p:raise ValueError("PATH_ALIAS")
 return p

def hashed(path,deadline):
 h=hashlib.sha256();size=0
 with path.open("rb") as f:
  while True:
   remaining(deadline);b=f.read(1024**2)
   if not b:break
   h.update(b);size+=len(b)
 return {"bytes":size,"sha256":h.hexdigest()}

def snapshot(root,deadline):
 root=canonical(root);result={}
 def fail(e):raise e
 for base,dirs,files in os.walk(root,followlinks=False,onerror=fail):
  for name in sorted(dirs+files):
   remaining(deadline);p=Path(base)/name;rel=p.relative_to(root).as_posix();s=p.lstat()
   if stat.S_ISLNK(s.st_mode):
    target=os.readlink(p);resolved=p.resolve(strict=True)
    if Path(target).is_absolute() or not resolved.is_relative_to(root) or ".git" in Path(rel).parts or ".git" in Path(target).parts or ".git" in resolved.relative_to(root).parts:
     raise ValueError("SYMLINK_ESCAPE_OR_METADATA")
    value={"type":"symlink","target":target}
   elif stat.S_ISDIR(s.st_mode):value={"type":"directory"}
   elif stat.S_ISREG(s.st_mode):
    if s.st_nlink!=1:raise ValueError("FILE_ALIAS")
    value={"type":"file",**hashed(p,deadline)}
   else:raise ValueError("SPECIAL_FILE")
   result[rel]={**value,"mode":stat.S_IMODE(s.st_mode)}
 remaining(deadline);return result

def read_record(binding,deadline):
 if type(binding) is not dict or set(binding)!={"path","sha256","bytes"}:raise ValueError("RECORD_SCHEMA")
 p=canonical(binding["path"])
 if not p.is_file() or hashed(p,deadline)!={k:binding[k] for k in ("sha256","bytes")}:
  raise ValueError("RECORD_IDENTITY")
 raw=p.read_bytes();remaining(deadline)
 if len(raw)!=binding["bytes"] or hashlib.sha256(raw).hexdigest()!=binding["sha256"]:
  raise ValueError("CONSUMED_RECORD_IDENTITY")
 return raw

def save(path,data):
 with path.open("x") as f:json.dump(data,f,sort_keys=True,indent=2,allow_nan=False);f.write("\n")

def verify_material(receipt,observed,workspace,commit,tree):
 if receipt.get("terminal")!="MATERIALIZED" or receipt.get("source_custody")!="UNCHANGED" or receipt.get("commit")!=commit or receipt.get("tree")!=tree:
  raise ValueError("MATERIAL_IDENTITY")
 entries=receipt["entries"];actual={k:v for k,v in observed.items() if k!=".git" and not k.startswith(".git/")}
 if set(actual)!=set(entries):raise ValueError("SOURCE_MEMBERSHIP")
 for name,w in entries.items():
  v=actual[name];mode=w["mode"]
  if mode in ("40000","040000"):wanted={"type":"directory","mode":0o755}
  elif mode=="120000":
   target=w["target"];b=os.fsencode(target)
   if {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}!={k:w[k] for k in ("sha256","bytes")}:raise ValueError("SYMLINK_IDENTITY")
   wanted={"type":"symlink","target":target,"mode":0o777}
  elif mode in ("100644","100755"):wanted={"type":"file","mode":0o644 if mode=="100644" else 0o755,**{k:w[k] for k in ("sha256","bytes")}}
  else:raise ValueError("SOURCE_MODE")
  if v!=wanted:raise ValueError("SOURCE_IDENTITY")
 metadata={k[5:]:{x:v[x] for x in ("sha256","bytes")} for k,v in observed.items() if k.startswith(".git/") and v["type"]=="file"}
 if observed.get(".git",{}).get("type")!="directory" or metadata!=receipt["git_metadata"]:
  raise ValueError("GIT_METADATA_IDENTITY")
 if (workspace/".git/HEAD").read_bytes()!=(commit+"\n").encode():raise ValueError("DETACHED_HEAD")

def copy_workspace(source,dest,expected,deadline):
 dest.mkdir(parents=True)
 for name,v in sorted(expected.items(),key=lambda item:(len(Path(item[0]).parts),item[0])):
  remaining(deadline);p=source/name;q=dest/name
  if v["type"]=="directory":q.mkdir()
  elif v["type"]=="symlink":q.symlink_to(v["target"])
  else:
   with p.open("rb") as a,q.open("xb") as b:
    while True:
     remaining(deadline);block=a.read(1024**2)
     if not block:break
     b.write(block)
   q.chmod(v["mode"])
 for name,v in sorted(expected.items(),key=lambda item:len(Path(item[0]).parts),reverse=True):
  if v["type"]=="directory":(dest/name).chmod(v["mode"])
 if snapshot(dest,deadline)!=expected:raise ValueError("COPY_IDENTITY")

def _prepare(materials,lock_record,output,*,deadline_monotonic,lock_validator,authority_scope):
 start=time.monotonic();root=Path(output).absolute()
 if root.parent.resolve(strict=True)!=root.parent:raise ValueError("PATH_ALIAS")
 # Read only receipt metadata before any writes, to protect source/output overlap.
 paths=[lock_record["path"]]+[m["receipt"]["path"] for m in materials]
 for item in materials:
  raw=json.loads(read_record(item["receipt"],deadline_monotonic))
  if isinstance(raw,dict) and isinstance(raw.get("workspace"),str):paths.append(raw["workspace"])
 for value in paths:
  p=canonical(value)
  if p==root or p.is_relative_to(root) or root.is_relative_to(p):raise ValueError("OUTPUT_OVERLAP")
 root.mkdir(mode=0o700)
 result={"schema":"ocm.corpus-layout.v1","terminal":"LAYOUT_REFUSED","authority_scope":authority_scope,
  "input_materials":materials,"lock":lock_record,"workspaces":{},"source_before":{},"source_after":{},"added_directories":{},
  "cost_scope":"Cold copy/inventory/disk work before final receipt; excludes imports and final persistence, charged by outer caller. Acquisition is reused, not re-executed.",
  "scope":"Layout and byte custody only. No build dispatch, code audit, semantic result or no-neural closure qualification."}
 try:
  remaining(deadline_monotonic);lock=read_record(lock_record,deadline_monotonic);rows=lock_validator(lock)
  parsed=json.loads(lock)
  if parsed.get("packagesDir")!=".lake/packages" or any(r.get("subDir") is not None for r in parsed["packages"]):raise ValueError("LOCK_LAYOUT")
  names=["corpus"]+[r["name"] for r in rows]
  if len(set(names))!=len(names) or any(not re.fullmatch("[A-Za-z][A-Za-z0-9_-]*",n) for n in names) or [m["name"] for m in materials]!=names:
   raise ValueError("MATERIAL_IDENTITY")
  if any(set(m)!={"name","commit","tree","receipt"} or any(not re.fullmatch("[0-9a-f]{40}",m[k]) for k in ("commit","tree")) for m in materials):
   raise ValueError("MATERIAL_IDENTITY")
  if any(m["commit"]!=r["rev"] for m,r in zip(materials[1:],rows)):raise ValueError("MATERIAL_IDENTITY")
  if authority_scope=="PINNED_CORPUS_LAYOUT" and materials[0]["commit"]!="aa2d8b34692b16c70f699536de0d8e75b9a3e9ef":raise ValueError("MATERIAL_IDENTITY")
  result["deadline_monotonic"]=deadline_monotonic;result["disk_free_before_bytes"]=shutil.disk_usage(root).free
  sources={}
  for m in materials:
   name=m["name"];receipt=json.loads(read_record(m["receipt"],deadline_monotonic));ws=canonical(receipt["workspace"])
   if any(ws==p or ws.is_relative_to(p) or p.is_relative_to(ws) for p in sources.values()):raise ValueError("MATERIAL_ALIAS")
   sources[name]=ws;before=snapshot(ws,deadline_monotonic);verify_material(receipt,before,ws,m["commit"],m["tree"])
   if name=="corpus" and (ws/"lake-manifest.json").read_bytes()!=lock:raise ValueError("ROOT_LOCK_IDENTITY")
   if ".lake/package-overrides.json" in before:raise ValueError("PACKAGE_OVERRIDES")
   result["source_before"][name]=before
  mounts=[];writable=[];copies={};artifact=root/"artifacts";artifact.mkdir()
  for m in materials:
   name=m["name"];dest=root/"materials"/name/"workspace";before=result["source_before"][name]
   copy_workspace(sources[name],dest,before,deadline_monotonic);added=[]
   overlays=[".lake/config",".lake/build",".lake/cache",".lake/packages"] if name=="corpus" else [".lake/build"]
   for rel in overlays:
    p=dest/rel
    if p.exists() and (not p.is_dir() or p.is_symlink() or any(p.iterdir())):raise ValueError("NONEMPTY_OVERLAY")
   need=overlays+[f".lake/packages/{n}" for n in names[1:]] if name=="corpus" else overlays
   for rel in need:
    parts=Path(rel).parts
    for n in range(1,len(parts)+1):
     p=dest/Path(*parts[:n])
     if not p.exists():p.mkdir();added.append(p.relative_to(dest).as_posix())
     elif p.is_symlink() or not p.is_dir():raise ValueError("LAYOUT_PATH_ALIAS")
   after=snapshot(dest,deadline_monotonic)
   if {k:v for k,v in after.items() if k not in added}!=before:raise ValueError("LAYOUT_SOURCE_DRIFT")
   copies[name]=after
   inv={k:{a:b for a,b in v.items() if a!="mode"} for k,v in after.items()}
   invpath=root/(name+"-inventory.json");save(invpath,inv)
   guest="/workspace" if name=="corpus" else "/workspace/.lake/packages/"+name
   mounts.append({"path":str(dest),"guest":guest_path(guest),"inventory":{"path":str(invpath),**hashed(invpath,deadline_monotonic)}})
   result["workspaces"][name]=str(dest);result["added_directories"][name]=added
   host=artifact/(name+"-build");host.mkdir();writable.append({"path":str(host),"guest":guest+"/.lake/build"})
  for name,guest in [("scratch","/work"),("config","/workspace/.lake/config"),("cache","/workspace/.lake/cache")]:
   p=artifact/name;p.mkdir();writable.append({"path":str(p),"guest":guest})
   if name=="scratch":(p/"home").mkdir()
  writable.sort(key=lambda x:x["guest"]!="/work")
  for name,ws in sources.items():
   result["source_after"][name]=snapshot(ws,deadline_monotonic)
   if result["source_after"][name]!=result["source_before"][name]:raise ValueError("SOURCE_POST_DRIFT")
  for m in materials:read_record(m["receipt"],deadline_monotonic)
  if read_record(lock_record,deadline_monotonic)!=lock:raise ValueError("LOCK_POST_DRIFT")
  result["output_inventory_before_result"]=snapshot(root,deadline_monotonic)
  final=result["output_inventory_before_result"];expected={"materials","artifacts","artifacts/scratch/home"}
  for m in mounts:
   name=Path(m["path"]).parent.name;prefix="materials/"+name+"/workspace/"
   if {k[len(prefix):]:v for k,v in final.items() if k.startswith(prefix)}!=copies[name]:raise ValueError("FINAL_LAYOUT_DRIFT")
   inv=name+"-inventory.json"
   if {k:final[inv][k] for k in ("sha256","bytes")}!={k:m["inventory"][k] for k in ("sha256","bytes")}:raise ValueError("FINAL_LAYOUT_DRIFT")
   expected.update({"materials/"+name,prefix[:-1],inv});expected.update(prefix+k for k in copies[name])
  expected.update("artifacts/"+Path(w["path"]).name for w in writable)
  if set(final)!=expected or any(v["type"]!="directory" for k,v in final.items() if k.startswith("artifacts/")):
   raise ValueError("FINAL_LAYOUT_DRIFT")
  result["owned_logical_bytes_before_result"]=sum(v.get("bytes",0) for v in result["output_inventory_before_result"].values())
  result["disk_free_after_bytes"]=shutil.disk_usage(root).free;remaining(deadline_monotonic)
  result.update(terminal="LAYOUT_READY",material_mounts=mounts,writable=writable)
 except BaseException as e:result["error"]=type(e).__name__+":"+str(e)
 result["wall_before_result_s"]=time.monotonic()-start;save(root/"RESULT.json",result);return result

def prepare_layout(materials,lock_record,output,*,deadline_monotonic):
 return _prepare(materials,lock_record,output,deadline_monotonic=deadline_monotonic,
                 lock_validator=validate_lock,authority_scope="PINNED_CORPUS_LAYOUT")
