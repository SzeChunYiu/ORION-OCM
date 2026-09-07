"""Faithful offline Git-tree materialization; no archive, checkout, filter or hook execution."""
import hashlib,json,math,os,re,stat,time
from pathlib import Path,PurePosixPath
from materialize_objects import Git,Objects,file_map,remaining,save,stamp

CONFIG="""[core]
 repositoryformatversion = 0
 bare = false
 filemode = true
 autocrlf = false
 hooksPath = /dev/null
 fsmonitor = false
 logAllRefUpdates = false
[protocol]
 allow = never
[gc]
 auto = 0
"""

def entries(raw):
 """Binary framing follows proof-corpus-v1/corpus_tree.binary_entries, with full modes."""
 rows=[];offset=0;seen=set()
 while offset<len(raw):
  space=raw.find(b" ",offset);zero=raw.find(b"\0",offset)
  if space<offset or zero<space or zero+21>len(raw):raise ValueError("TREE_FRAMING")
  mode=raw[offset:space].decode("ascii");name=raw[space+1:zero].decode("utf-8")
  if not name or name in (".","..") or name.casefold()==".git" or any(c in name for c in "/\\") or any(ord(c)<32 for c in name):
   raise ValueError("TREE_PATH")
  if name in seen:raise ValueError("TREE_DUPLICATE")
  if mode not in ("40000","040000","100644","100755","120000"):raise ValueError("TREE_MODE")
  seen.add(name);rows.append((name,mode,raw[zero+1:zero+21].hex()));offset=zero+21
 return rows

def safe_link(path,target,workspace):
 if not target or "\0" in target or "\\" in target or PurePosixPath(target).is_absolute():raise ValueError("SYMLINK_TARGET")
 parts=list(path.parent.relative_to(workspace).parts)
 for part in target.split("/"):
  if part in ("","."):continue
  if part=="..":
   if not parts:raise ValueError("SYMLINK_ESCAPE")
   parts.pop()
  else:
   if part.casefold()==".git":raise ValueError("SYMLINK_METADATA")
   parts.append(part)

def materialize(bare_path,commit,expected_tree,expected_bare_inventory,output,*,deadline_monotonic,acquisition_reference):
 """Caller binds authority/deadline and supplies aggregate supervision. Failures retain partial data."""
 start=time.monotonic();bare=Path(bare_path).resolve(strict=True);root=Path(output).resolve()
 if root==bare or root.is_relative_to(bare) or bare.is_relative_to(root):raise ValueError("OUTPUT_OVERLAP")
 root.mkdir(mode=0o700);records=root/"records";records.mkdir()
 ws=root/"workspace";ws.mkdir();ws.chmod(0o755);meta=ws/".git";commands=[]
 result={"schema":"ocm.git-materialization.v1","terminal":"MATERIALIZE_REFUSED","workspace":str(ws),
  "source":str(bare),"commit":commit,"tree":expected_tree,"commands":commands,"entries":{},
  "acquisition_reference":acquisition_reference,"deadline_monotonic":deadline_monotonic if type(deadline_monotonic) in (int,float) and math.isfinite(deadline_monotonic) else None}
 try:
  remaining(deadline_monotonic)
  if any(type(x) is not str or not re.fullmatch("[0-9a-f]{40}",x) for x in (commit,expected_tree)):raise ValueError("PIN_ID")
  if file_map(bare,deadline_monotonic)!=expected_bare_inventory:raise ValueError("SOURCE_IDENTITY")
  save(records/"SOURCE.json",expected_bare_inventory)
  forbidden=("objects/info/alternates","objects/info/http-alternates")
  if any(p in expected_bare_inventory or any(k.startswith(p+"/") for k in expected_bare_inventory) for p in forbidden) or any(p.endswith(".promisor") for p in expected_bare_inventory):
   raise ValueError("EXTERNAL_OBJECT_DEPENDENCY")
  meta.mkdir();(meta/"objects").mkdir();(meta/"refs").mkdir()
  for name,value in sorted(expected_bare_inventory.items()):
   if not (name.startswith("objects/") or name=="shallow"):continue
   remaining(deadline_monotonic);src=bare/name;dest=meta/name;dest.parent.mkdir(parents=True,exist_ok=True)
   h=hashlib.sha256();size=0
   with src.open("rb") as source,dest.open("xb") as target:
    while True:
     remaining(deadline_monotonic);b=source.read(1024**2)
     if not b:break
     target.write(b);h.update(b);size+=len(b)
   if {"sha256":h.hexdigest(),"bytes":size}!=value:raise ValueError("COPIED_OBJECT_DRIFT")
  (meta/"HEAD").write_text(commit+"\n");(meta/"config").write_text(CONFIG)
  git=Git(meta,records,deadline_monotonic,commands)
  result["git_executable"]={"path":"/usr/bin/git",**stamp("/usr/bin/git")}
  if git.run("--version").read_bytes()!=b"git version 2.25.1\n":raise ValueError("GIT_VERSION")
  git.run("fsck","--full","--strict","--no-reflogs","--no-dangling",commit)
  cache={};links=[];objects=records/"objects";objects.mkdir()
  with Objects(git) as reader:
   result["objects"]=reader.objects
   c=objects/(commit+".commit");reader.read(commit,"commit",c,64*1024**2)
   if not c.read_bytes().startswith(("tree "+expected_tree+"\n").encode()):raise ValueError("REGISTERED_TREE_MISMATCH")
   stack=[("",expected_tree)]
   while stack:
    prefix,oid=stack.pop();remaining(deadline_monotonic)
    if oid not in cache:
     p=objects/(oid+".tree");reader.read(oid,"tree",p,64*1024**2);cache[oid]=entries(p.read_bytes())
    for name,mode,child in cache[oid]:
     relative=prefix+"/"+name if prefix else name;dest=ws/relative
     if relative in result["entries"]:raise ValueError("PATH_COLLISION")
     if mode in ("40000","040000"):
      dest.mkdir(mode=0o755);dest.chmod(0o755);result["entries"][relative]={"mode":mode,"oid":child};stack.append((relative,child))
     elif mode=="120000":
      p=objects/(str(len(reader.objects))+".link");r=reader.read(child,"blob",p,4096);target=p.read_bytes().decode("utf-8")
      safe_link(dest,target,ws);os.symlink(target,dest);links.append(dest)
      result["entries"][relative]={"mode":mode,"oid":child,"sha256":r["sha256"],"bytes":r["bytes"],"target":target}
     else:
      r=reader.read(child,"blob",dest);os.chmod(dest,0o755 if mode=="100755" else 0o644)
      result["entries"][relative]={k:r[k] for k in ("sha256","bytes")}|{"mode":mode,"oid":child}
  for link in links:
   if not link.resolve(strict=False).is_relative_to(ws) or (ws/".git") in link.resolve(strict=False).parents:raise ValueError("SYMLINK_RESOLUTION_ESCAPE")
  git.run("read-tree",commit)
  if git.run("write-tree").read_bytes()!=(expected_tree+"\n").encode():raise ValueError("INDEX_TREE_IDENTITY")
  if git.run("rev-parse","--verify","HEAD").read_bytes()!=(commit+"\n").encode():raise ValueError("DETACHED_HEAD")
  for relative,value in result["entries"].items():
   remaining(deadline_monotonic);p=ws/relative;mode=value["mode"]
   if mode=="120000":
    b=os.fsencode(os.readlink(p))
    if hashlib.sha256(b).hexdigest()!=value["sha256"] or len(b)!=value["bytes"]:raise ValueError("OUTPUT_SYMLINK_DRIFT")
   elif mode in ("40000","040000"):
    if not p.is_dir() or p.is_symlink() or stat.S_IMODE(p.stat().st_mode)!=0o755:raise ValueError("OUTPUT_DIRECTORY_DRIFT")
   elif p.is_symlink() or stamp(p)!={k:value[k] for k in ("sha256","bytes")} or stat.S_IMODE(p.stat().st_mode)!=(0o755 if mode=="100755" else 0o644):
    raise ValueError("OUTPUT_BLOB_DRIFT")
  observed=set()
  for base,dirs,files in os.walk(ws,followlinks=False):
   if Path(base)==ws:dirs.remove(".git")
   observed.update(str((Path(base)/n).relative_to(ws)) for n in dirs+files)
  if observed!=set(result["entries"]):raise ValueError("OUTPUT_MEMBERSHIP")
  if file_map(bare,deadline_monotonic)!=expected_bare_inventory:raise ValueError("SOURCE_POST_DRIFT")
  for p in meta.rglob("*"):
   if p.is_file():os.chmod(p,0o444)
  for p in sorted([meta,*[p for p in meta.rglob("*") if p.is_dir()]],key=lambda p:len(p.parts),reverse=True):os.chmod(p,0o555)
  result["git_metadata"]=file_map(meta,deadline_monotonic)
  remaining(deadline_monotonic)
  if ws.is_symlink() or stat.S_IMODE(ws.stat().st_mode)!=0o755:raise ValueError("OUTPUT_DIRECTORY_DRIFT")
  result["source_custody"]="UNCHANGED";result["terminal"]="MATERIALIZED"
 except BaseException as e:result["error"]=type(e).__name__+":"+str(e)
 result["wall_s"]=time.monotonic()-start
 result["cost_scope"]="Inner cold work through verification; excludes imports, final receipt persistence and caller acquisition. Outer supervision must charge those costs."
 result["source_files"]={n:stamp(Path(__file__).with_name(n)) for n in ("materialize_git.py","materialize_objects.py")}
 save(root/"RESULT.json",result);return result
